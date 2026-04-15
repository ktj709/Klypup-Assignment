from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import ResearchReport, Role
from app.schemas.auth import TenantContext
from app.schemas.report import ReportCreate, ReportOut, ReportUpdate

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[ResearchReport]:
    reports = (
        db.query(ResearchReport)
        .filter(ResearchReport.org_id == tenant.org_id)
        .order_by(ResearchReport.created_at.desc())
        .limit(100)
        .all()
    )
    return reports


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
