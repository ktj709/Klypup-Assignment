from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import ReportSection, ReportTag, ResearchReport, Role
from app.schemas.auth import TenantContext
from app.schemas.report import ReportCreate, ReportDetailOut, ReportOut, ReportUpdate

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
def list_reports(
    search: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[ResearchReport]:
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
    if tenant.role not in (Role.ADMIN, Role.ANALYST):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

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
