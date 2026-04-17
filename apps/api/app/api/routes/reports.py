from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import ReportSection, ReportTag, ResearchReport, Role
from app.schemas.auth import TenantContext
from app.schemas.report import ReportCreate, ReportDetailOut, ReportOut, ReportUpdate
from app.services.supabase_rest import get_supabase_rest_client

router = APIRouter(prefix="/reports", tags=["reports"])


def _in_filter(ids: list[int]) -> str:
    return f"in.({','.join(str(item) for item in ids)})"


def _attach_tags(reports: list[dict]) -> None:
    if not reports:
        return

    supabase = get_supabase_rest_client()
    report_ids = [int(report["id"]) for report in reports]
    tags = supabase.select(
        "report_tags",
        {
            "select": "report_id,name",
            "report_id": _in_filter(report_ids),
        },
    )
    tags_by_report: dict[int, list[dict[str, str]]] = {report_id: [] for report_id in report_ids}
    for tag in tags:
        tags_by_report.setdefault(int(tag["report_id"]), []).append({"name": tag["name"]})

    for report in reports:
        report["tags"] = tags_by_report.get(int(report["id"]), [])


@router.get("", response_model=list[ReportOut])
def list_reports(
    search: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[ResearchReport]:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        params = {
            "select": "id,org_id,title,query_text,status,summary,created_at",
            "org_id": f"eq.{tenant.org_id}",
            "order": "created_at.desc",
            "limit": "100",
        }
        if search:
            term = search.strip().replace(",", "")
            params["or"] = f"(title.ilike.*{term}*,query_text.ilike.*{term}*)"

        reports = supabase.select("research_reports", params)

        if tag:
            normalized = tag.strip().lower()
            if not reports:
                return []
            report_ids = [int(item["id"]) for item in reports]
            matching_tags = supabase.select(
                "report_tags",
                {
                    "select": "report_id",
                    "name": f"eq.{normalized}",
                    "report_id": _in_filter(report_ids),
                },
            )
            allowed_ids = {int(item["report_id"]) for item in matching_tags}
            reports = [item for item in reports if int(item["id"]) in allowed_ids]

        _attach_tags(reports)
        return reports

    query = (
        db.query(ResearchReport)
        .options(selectinload(ResearchReport.tags))
        .filter(ResearchReport.org_id == tenant.org_id)
    )

    if search:
        like = f"%{search.strip()}%"
        query = query.filter((ResearchReport.title.ilike(like)) | (ResearchReport.query_text.ilike(like)))

    if tag:
        query = query.join(ReportTag).filter(ReportTag.name == tag.strip().lower())

    reports = query.order_by(ResearchReport.created_at.desc()).limit(100).all()
    return reports


@router.get("/{report_id}", response_model=ReportDetailOut)
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchReport:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        report_rows = supabase.select(
            "research_reports",
            {
                "select": "id,org_id,title,query_text,status,summary,created_at",
                "id": f"eq.{report_id}",
                "org_id": f"eq.{tenant.org_id}",
                "limit": "1",
            },
        )
        if not report_rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        report = report_rows[0]
        _attach_tags([report])

        sections = supabase.select(
            "report_sections",
            {
                "select": "id,title,body,order_index",
                "report_id": f"eq.{report_id}",
                "order": "order_index.asc",
            },
        )
        if sections:
            section_ids = [int(section["id"]) for section in sections]
            citations = supabase.select(
                "report_citations",
                {
                    "select": "id,section_id,source_type,source_name,reference",
                    "section_id": _in_filter(section_ids),
                },
            )
            by_section: dict[int, list[dict]] = {section_id: [] for section_id in section_ids}
            for citation in citations:
                by_section.setdefault(int(citation["section_id"]), []).append(
                    {
                        "id": citation["id"],
                        "source_type": citation["source_type"],
                        "source_name": citation["source_name"],
                        "reference": citation["reference"],
                    }
                )
            for section in sections:
                section["citations"] = by_section.get(int(section["id"]), [])
        report["sections"] = sections
        return report

    report = (
        db.query(ResearchReport)
        .options(
            selectinload(ResearchReport.sections).selectinload(ReportSection.citations),
            selectinload(ResearchReport.tags),
        )
        .filter(ResearchReport.id == report_id, ResearchReport.org_id == tenant.org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchReport:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        inserted = supabase.insert(
            "research_reports",
            {
                "org_id": tenant.org_id,
                "created_by_user_id": tenant.user_id,
                "title": payload.title,
                "query_text": payload.query_text,
                "summary": payload.summary,
                "status": "completed",
            },
            select="id,org_id,title,query_text,status,summary,created_at",
        )
        report = inserted[0]
        report["tags"] = []
        return report

    report = ResearchReport(
        org_id=tenant.org_id,
        created_by_user_id=tenant.user_id,
        title=payload.title,
        query_text=payload.query_text,
        summary=payload.summary,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.patch("/{report_id}", response_model=ReportOut)
def update_report(
    report_id: int,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchReport:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        existing = supabase.select(
            "research_reports",
            {
                "select": "id",
                "id": f"eq.{report_id}",
                "org_id": f"eq.{tenant.org_id}",
                "limit": "1",
            },
        )
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        update_payload: dict[str, str | None] = {}
        if payload.title is not None:
            update_payload["title"] = payload.title
        if payload.summary is not None:
            update_payload["summary"] = payload.summary

        if update_payload:
            updated = supabase.update(
                "research_reports",
                update_payload,
                {"id": f"eq.{report_id}", "org_id": f"eq.{tenant.org_id}"},
                select="id,org_id,title,query_text,status,summary,created_at",
            )
            report = updated[0]
        else:
            report = supabase.select(
                "research_reports",
                {
                    "select": "id,org_id,title,query_text,status,summary,created_at",
                    "id": f"eq.{report_id}",
                    "org_id": f"eq.{tenant.org_id}",
                    "limit": "1",
                },
            )[0]

        _attach_tags([report])
        return report

    report = (
        db.query(ResearchReport)
        .filter(ResearchReport.id == report_id, ResearchReport.org_id == tenant.org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if payload.title is not None:
        report.title = payload.title
    if payload.summary is not None:
        report.summary = payload.summary

    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> None:
    settings = get_settings()
    if tenant.role not in (Role.ADMIN, Role.ANALYST):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        report = supabase.select(
            "research_reports",
            {
                "select": "id",
                "id": f"eq.{report_id}",
                "org_id": f"eq.{tenant.org_id}",
                "limit": "1",
            },
        )
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        supabase.delete(
            "research_reports",
            {"id": f"eq.{report_id}", "org_id": f"eq.{tenant.org_id}"},
        )
        return None

    report = (
        db.query(ResearchReport)
        .filter(ResearchReport.id == report_id, ResearchReport.org_id == tenant.org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    db.delete(report)
    db.commit()
    return None


@router.post("/{report_id}/tags", response_model=ReportOut)
def add_report_tag(
    report_id: int,
    name: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchReport:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        report_rows = supabase.select(
            "research_reports",
            {
                "select": "id,org_id,title,query_text,status,summary,created_at",
                "id": f"eq.{report_id}",
                "org_id": f"eq.{tenant.org_id}",
                "limit": "1",
            },
        )
        if not report_rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        normalized = name.strip().lower()
        existing = supabase.select(
            "report_tags",
            {
                "select": "id",
                "report_id": f"eq.{report_id}",
                "name": f"eq.{normalized}",
                "limit": "1",
            },
        )
        if not existing:
            supabase.insert("report_tags", {"report_id": report_id, "name": normalized}, select="id")

        report = report_rows[0]
        _attach_tags([report])
        return report

    report = (
        db.query(ResearchReport)
        .options(selectinload(ResearchReport.tags))
        .filter(ResearchReport.id == report_id, ResearchReport.org_id == tenant.org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    normalized = name.strip().lower()
    exists = any(tag.name == normalized for tag in report.tags)
    if not exists:
        db.add(ReportTag(report_id=report.id, name=normalized))
        db.commit()
        db.refresh(report)
    return report


@router.delete("/{report_id}/tags/{tag_name}", response_model=ReportOut)
def delete_report_tag(
    report_id: int,
    tag_name: str,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchReport:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        report_rows = supabase.select(
            "research_reports",
            {
                "select": "id,org_id,title,query_text,status,summary,created_at",
                "id": f"eq.{report_id}",
                "org_id": f"eq.{tenant.org_id}",
                "limit": "1",
            },
        )
        if not report_rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        supabase.delete(
            "report_tags",
            {"report_id": f"eq.{report_id}", "name": f"eq.{tag_name.lower()}"},
        )
        report = report_rows[0]
        _attach_tags([report])
        return report

    report = (
        db.query(ResearchReport)
        .options(selectinload(ResearchReport.tags))
        .filter(ResearchReport.id == report_id, ResearchReport.org_id == tenant.org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    candidate = next((item for item in report.tags if item.name == tag_name.lower()), None)
    if candidate:
        db.delete(candidate)
        db.commit()
        db.refresh(report)

    return report
