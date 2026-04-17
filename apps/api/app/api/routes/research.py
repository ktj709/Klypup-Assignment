from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import ReportCitation, ReportSection, ResearchReport
from app.schemas.auth import TenantContext
from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.document_retrieval import ingest_documents
from app.services.orchestrator import run_research
from app.services.supabase_rest import get_supabase_rest_client

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/run", response_model=ResearchResponse)
def run_research_query(
    payload: ResearchRequest,
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchResponse:
    # Tenant context is resolved for all research requests; downstream persistence is scoped to tenant.
    _ = tenant
    return run_research(payload)


@router.post("/run-and-save", response_model=ResearchResponse)
def run_research_and_save(
    payload: ResearchRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchResponse:
    result = run_research(payload)

    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        report_rows = supabase.insert(
            "research_reports",
            {
                "org_id": tenant.org_id,
                "created_by_user_id": tenant.user_id,
                "title": result.title,
                "query_text": payload.query,
                "summary": result.executive_summary,
                "status": "completed",
            },
            select="id",
        )
        report_id = int(report_rows[0]["id"])

        for index, section in enumerate(result.sections):
            section_rows = supabase.insert(
                "report_sections",
                {
                    "report_id": report_id,
                    "title": section.title,
                    "body": section.body,
                    "order_index": index,
                },
                select="id",
            )
            section_id = int(section_rows[0]["id"])

            if section.citations:
                citations_payload = [
                    {
                        "section_id": section_id,
                        "source_type": citation.source_type,
                        "source_name": citation.source_name,
                        "reference": citation.reference,
                    }
                    for citation in section.citations
                ]
                supabase.insert("report_citations", citations_payload, select="id")

        result.report_id = report_id
        return result

    report = ResearchReport(
        org_id=tenant.org_id,
        created_by_user_id=tenant.user_id,
        title=result.title,
        query_text=payload.query,
        summary=result.executive_summary,
    )
    db.add(report)
    db.flush()

    for index, section in enumerate(result.sections):
        report_section = ReportSection(
            report_id=report.id,
            title=section.title,
            body=section.body,
            order_index=index,
        )
        db.add(report_section)
        db.flush()

        for citation in section.citations:
            db.add(
                ReportCitation(
                    section_id=report_section.id,
                    source_type=citation.source_type,
                    source_name=citation.source_name,
                    reference=citation.reference,
                )
            )

    db.commit()
    result.report_id = report.id
    return result


@router.post("/ingest-documents")
def ingest_document_corpus(
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, int | str]:
    _ = tenant
    count = ingest_documents()
    return {"status": "ok", "ingested_chunks": count}
