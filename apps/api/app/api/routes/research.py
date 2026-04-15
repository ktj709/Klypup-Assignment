from fastapi import APIRouter, Depends

from app.core.tenant import get_tenant_context
from app.schemas.auth import TenantContext
from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.orchestrator import run_research

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/run", response_model=ResearchResponse)
def run_research_query(
    payload: ResearchRequest,
    tenant: TenantContext = Depends(get_tenant_context),
) -> ResearchResponse:
    # Tenant context is resolved for all research requests; downstream persistence is scoped to tenant.
    _ = tenant
    return run_research(payload)
