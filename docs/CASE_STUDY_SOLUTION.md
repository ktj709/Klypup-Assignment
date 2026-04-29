# Case Study Solution Document

## 1. Problem Statement
Investment teams and advisors lose significant time producing research updates because data is fragmented across market feeds, news sources, internal notes, and filing documents. This causes three business problems:

1. Slow decision cycles and missed market opportunities.
2. Inconsistent research quality across analysts.
3. High operating cost for repeated manual analysis tasks.

For organizations operating multiple client entities or business units, there is an additional risk: data leakage across tenants if isolation is not enforced correctly.

## 2. Customer Problem and Business Context
### Primary users
1. Investment analysts who need fast, evidence-backed company research.
2. Portfolio managers who need concise recommendations and risk signals.
3. Operations/admin teams who manage user access and organizational controls.

### Current pain points
1. 3-6 tools are used per research task, with manual copy-paste and low traceability.
2. Reports are difficult to reproduce because source references are not consistently captured.
3. Research turnaround is often measured in hours, not minutes.
4. Multi-tenant environments require strict separation by organization and role.

## 3. Proposed Solution (Business View)
### Solution name
AI-Powered Investment Research Dashboard (Agentic Research Assistant)

### What it does
1. Accepts a natural-language research query from a user.
2. Uses an orchestrated AI flow to decide which tools to run (market data, news, document retrieval).
3. Produces a structured, source-attributed research report with sections, citations, and summary.
4. Saves reports for search, tagging, and reuse.
5. Supports watchlists and admin invite workflows.
6. Enforces multi-tenant and role-based access control end-to-end.

### Why this solves the problem
1. Reduces research cycle time through automated evidence gathering and synthesis.
2. Improves consistency with structured report templates.
3. Increases trust with explicit citations and stored research history.
4. Protects enterprise data boundaries with tenant-scoped access.

## 4. Business Impact (Working Backward from Customer Outcomes)
### Target outcomes
1. 50-70% reduction in time to first research draft.
2. 20-30% increase in analyst throughput per week.
3. Faster decision support for portfolio actions.
4. Lower compliance and operational risk through access controls and traceability.

### KPI framework
1. Time-to-report: query submission to first usable report.
2. Reuse rate: percentage of decisions using saved tagged reports.
3. Citation coverage: percentage of report sections with sources.
4. Tenant isolation incidents: target zero.
5. Cost per research run: blended cost of LLM + external API + infrastructure.

## 5. Technology Solution (Robust, Secure, Scalable)
### Architecture summary
1. Frontend: Next.js application for dashboard, reports, watchlist, and admin workflows.
2. Backend: FastAPI API layer for auth, tenant context resolution, orchestration, and persistence.
3. Data: PostgreSQL (Supabase-compatible) for reports, tags, memberships, watchlist, and invites.
4. AI and retrieval: Gemini for planning/synthesis and FAISS for local document retrieval.
5. External integrations: Yahoo Finance and News APIs.

### Agentic orchestration design
1. Planner step determines tool usage and ticker hints in strict JSON form.
2. Tool execution step runs selected tools and normalizes outputs.
3. Synthesis step returns structured report sections and executive summary.
4. Fallback logic handles malformed or unavailable planner output.

### Security controls
1. Auth0 JWT validation through JWKS in backend middleware.
2. Tenant context resolved from membership, not client-side claims alone.
3. Query-level org filtering for all tenant-owned resources.
4. RBAC checks for privileged endpoints (admin workflows).
5. Secret keys stored server-side only.

### Scalability approach
1. Stateless API layer enables horizontal scaling.
2. Postgres indexing strategy supports tenant-scoped query patterns.
3. Tool timeouts and retry policy reduce cascading failures.
4. Caching layer can be added for repeated market/news fetches.
5. Managed vector store can replace FAISS when corpus and concurrency increase.

### Reliability approach
1. Typed API schemas and validation reduce runtime failures.
2. Graceful degradation when external data/LLM is unavailable.
3. Integration tests cover tenant isolation and RBAC boundaries.

## 6. Cost Model and Efficiency Strategy
### Cost drivers
1. LLM inference (planning + synthesis).
2. External market/news API usage.
3. Application hosting and managed database.
4. Observability and logging.

### Cost optimization levers
1. Constrain LLM calls to high-value stages only.
2. Cache deterministic or slowly changing external data.
3. Apply token budgeting and response-size limits.
4. Route simple queries to deterministic templates without LLM when possible.
5. Use tiered retention for report artifacts.

### Expected cost profile
1. Prototype/MVP: low fixed cost, variable per-run LLM/API cost.
2. Growth stage: moderate increase from usage volume; offset by caching and batching.
3. Enterprise stage: higher infrastructure spend justified by productivity gains and reduced manual effort.

## 7. Implementation Plan
### Phase 1 (Weeks 1-2): Foundation
1. Confirm user journeys, KPI baseline, and compliance boundaries.
2. Finalize auth, tenant schema, and core report workflow.

### Phase 2 (Weeks 3-4): Agentic Intelligence
1. Add planner and synthesis orchestration with strict output contracts.
2. Integrate market/news/document tools and citation pipeline.

### Phase 3 (Weeks 5-6): Hardening
1. Add retries, timeout controls, and observability dashboards.
2. Expand tests for failure modes and tenant boundary checks.
3. Tune cost controls, caching, and request budgets.

## 8. Risks and Mitigations
1. Hallucinated AI output.
- Mitigation: require citations, confidence/uncertainty messaging, deterministic fallback.

2. Tenant data leakage.
- Mitigation: enforce org_id filtering in backend query paths and test isolation routinely.

3. External API instability.
- Mitigation: retries, backoff, graceful partial responses, and provider abstraction.

4. Cost overrun with scale.
- Mitigation: query classification, caching, and LLM usage policies.

## 9. Why This Is a Strong Business + Technology Solution
1. Solves a clear customer pain (slow, fragmented, inconsistent investment research).
2. Uses AI where it creates measurable value, not as a superficial add-on.
3. Prioritizes enterprise needs: security, tenant isolation, traceability, and operational control.
4. Maintains a practical cost strategy with clear optimization paths.

