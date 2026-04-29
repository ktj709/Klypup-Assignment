# Interview Extreme Deep Dive - Klypup Assignment

This document is a high-density prep guide for tomorrow's interview. It is designed to help you explain the project end-to-end with confidence, including architecture, design decisions, security, multi-tenancy, AI orchestration, trade-offs, and likely interviewer questions.

## 1) 2-Minute Project Pitch

Klypup Assignment implements Option A: an Investment Research Dashboard.

Core value proposition:
- A user can run an AI-assisted research query (for example, company earnings comparison),
- The backend orchestrates tools (market data, news, filing retrieval),
- The response is structured into sections with citations,
- The result can be persisted as a tenant-scoped report,
- Teams can manage watchlists and org memberships with RBAC.

What makes it interview-strong:
- Real full-stack integration (Next.js + FastAPI + relational DB + Auth0 + LLM + external APIs).
- Explicit multi-tenant isolation strategy (not only UI-level filtering).
- AI orchestration with deterministic fallback logic.
- Practical product features (reports, tags/search, watchlist, admin invites).

## 2) Architecture in One View

Layers:
1. Frontend (apps/web): Next.js pages and components.
2. API (apps/api): FastAPI routes, auth, tenant context, orchestration.
3. Data: PostgreSQL tables (SQLAlchemy model) or Supabase REST mode.
4. AI + tools: Gemini planning/synthesis + yfinance + News API + FAISS retrieval.

Primary request path:
1. User signs in via Auth0.
2. Frontend sends Bearer token to API route.
3. API validates JWT (JWKS), resolves tenant context (org_id, role, user_id).
4. Route executes business logic with tenant filters.
5. For research: orchestrator decides tools, fetches data, builds sections/citations, synthesizes summary.
6. run-and-save persists report + sections + citations.
7. Frontend renders report detail and charts.

## 3) Monorepo Mental Model

Top-level:
- apps/api: backend service.
- apps/web: frontend app.
- docs: architecture, decisions, case study, interview docs.

Backend mental model (apps/api/app):
- api/routes: transport layer (HTTP contract).
- core: config, security, tenant context.
- db: session and ORM base.
- models: relational entities.
- schemas: pydantic request/response models.
- services: orchestration, tool adapters, external integrations.

Frontend mental model (apps/web):
- app: route-based pages.
- components: feature UI units.
- lib/api.ts: typed API client wrappers.
- lib/auth0.ts: session/auth wiring.

## 4) Backend Deep Dive

### 4.1 Bootstrapping and middleware

main.py highlights:
- Creates FastAPI app with configurable CORS origins.
- Registers route groups: health, orgs, reports, research, watchlist.
- Adds request logging middleware that:
  - attaches x-request-id,
  - logs method/path/status/duration,
  - helps observability and debugging.
- Startup behavior:
  - If data_backend != supabase_rest, creates SQLAlchemy tables automatically.

### 4.2 Configuration strategy

core/config.py uses BaseSettings with env loading.
Important fields:
- data_backend: sqlalchemy or supabase_rest.
- Auth0 settings: domain, audience, algorithm.
- External resilience knobs: external_request_timeout_seconds, external_request_retries.
- request_logging_enabled toggle.

Interview angle: this shows environment-driven behavior and deploy flexibility without code branching everywhere.

### 4.3 Auth and tenant resolution

core/security.py:
- Uses HTTP Bearer.
- Fetches Auth0 JWKS with cache + retry logic.
- Validates token issuer, audience, algorithm.
- Returns CurrentUser from JWT claims.

core/tenant.py:
- Converts CurrentUser into TenantContext(org_id, role, user_id).
- In supabase_rest mode:
  - Auto-provisions first-time users,
  - Creates a Personal Workspace org,
  - Assigns admin membership.
- In sqlalchemy mode:
  - Expects pre-provisioned user/membership,
  - Enforces 401/403 when missing.

Interview angle: clean separation of identity verification and authorization context.

### 4.4 Data model

Key entities in models/entities.py:
- Organization
- User
- OrganizationMembership (role enum: admin, analyst)
- ResearchReport
- ReportSection
- ReportCitation
- ReportTag
- CompanyWatchlist
- OrganizationInvite

Notable constraints and indexing:
- users.auth0_sub unique.
- org-scoped ownership across report/watchlist objects.
- Composite index ix_reports_org_created on (org_id, created_at).

### 4.5 Route behavior by feature

Research routes:
- POST /api/v1/research/run:
  - Resolves tenant context,
  - Executes orchestration,
  - Returns structured response (not persisted).
- POST /api/v1/research/run-and-save:
  - Runs orchestration,
  - Persists report + sections + citations,
  - Returns response with report_id.
- POST /api/v1/research/ingest-documents:
  - Builds/refreshes FAISS index from local sample docs.

Reports routes:
- GET /reports with optional search and tag filtering.
- GET /reports/{id} returns sections and citations.
- POST /reports creates manual report.
- PATCH /reports/{id} updates title/summary.
- DELETE /reports/{id} enforces role check and tenant ownership.
- POST /reports/{id}/tags and DELETE /reports/{id}/tags/{tag} normalize tags to lowercase.

Watchlist routes:
- GET /watchlist is tenant-scoped.
- POST /watchlist upserts behavior by org+ticker (returns existing if duplicate).
- DELETE /watchlist/{id} requires tenant ownership.

Org routes:
- GET /orgs/members lists current org memberships.
- POST /orgs/invites admin-only invite generation.
- POST /orgs/join validates invite existence/expiry/used state and adds analyst membership.

## 5) AI Orchestration Deep Dive

orchestrator.py execution flow:
1. Parse query and infer potential tickers by regex fallback.
2. Infer needs for news/documents via keyword heuristics.
3. Ask Gemini planner (plan_tools) for structured tool usage decision.
4. Merge planner output over heuristics if planner is valid.
5. Execute selected tools:
   - market_data: yfinance snapshot per ticker,
   - news_data: company news + sentiment lines,
   - document_retrieval: FAISS chunk hits.
6. Build normalized sections and citations.
7. Synthesize final executive summary using Gemini.
8. If no tools selected, return a meaningful fallback interpretation section.

Why this is good architecture for interview:
- LLM is advisory and synthesis-focused, not blindly authoritative.
- Pipeline still works if planner fails (deterministic fallback).
- Output shape is structured and persistent-friendly.

## 6) Frontend Deep Dive

Home page (app/page.tsx):
- Uses server-side session check via Auth0.
- Pulls recent reports + watchlist on signed-in sessions.
- Renders quick actions and research console.
- Graceful fallback if API fails (dashboard remains functional).

Research Console (components/ResearchConsole.tsx):
- Handles query state, run/save actions, loading and status messages.
- Displays summary, tools_used, sections, citations, and charts.

Reports view:
- Table shows title, tags, status, created timestamp, query, and deep-link.
- Search/tag filtering is backed by API query params.

Watchlist panel:
- Add/remove items with optimistic local list update patterns.
- Normalizes ticker format to uppercase before send.

Admin page:
- Requires authenticated session.
- Attempts member retrieval; if unavailable, communicates likely non-admin state.

API client strategy (lib/api.ts):
- Centralized typed wrappers for all backend calls.
- Consistent Authorization header usage.
- Better error messages for research endpoints by parsing response detail.

## 7) Multi-Tenancy and RBAC Story

How to explain it in interview:
1. Every protected route depends on get_tenant_context.
2. TenantContext carries org_id + role + user_id.
3. All tenant-owned queries include org_id filters.
4. Admin-only operations explicitly check tenant.role.
5. Tests verify cross-tenant denial behavior.

This is stronger than frontend isolation because enforcement lives server-side.

## 8) Test Coverage and What It Proves

Current integration-style tests focus on critical risks:
- test_tenant_isolation.py:
  - report created in org1 cannot be listed/read by org2.
  - org invite creation denied for non-admin.
- test_reports_tags_search.py:
  - tag add/remove works.
  - tag and text search filtering works.
- test_watchlist.py:
  - org1 watchlist CRUD succeeds.
  - org2 cannot see or delete org1 records.

Testing approach details:
- Uses TestClient.
- Overrides dependencies for DB and tenant context.
- Uses isolated sqlite test DB lifecycle per test.

Interview angle: you intentionally tested isolation paths first because data leakage is a high-severity risk in multi-tenant SaaS.

## 9) Design Trade-Offs You Can Defend

1. Shared-schema multi-tenancy instead of database-per-tenant:
- Faster delivery and simpler operations for assessment scope.
- Requires disciplined query filters and tests.

2. FAISS local vector store instead of managed vector DB:
- Lower setup and deterministic local demo.
- Not ideal for large-scale production corpora.

3. Gemini as planner+synthesizer with fallback:
- Better control and reliability than a fully freeform LLM response.
- Still dependent on prompt quality and output correctness checks.

4. Dual backend support (SQLAlchemy and Supabase REST):
- Increases portability and integration options.
- Adds branching complexity that needs good test coverage.

## 10) Security and Reliability Notes

Security controls already present:
- JWT verification via Auth0 JWKS.
- Audience and issuer checks.
- Tenant and role-based route guards.
- Backend-only secrets usage for external APIs.

Reliability controls already present:
- External request timeout and retry settings.
- Request-id logging for correlation.
- UI resilience patterns when backend calls fail.

Current gaps to acknowledge honestly:
- No dedicated audit event table.
- Limited observability dashboards/tracing.
- More robust circuit breaker policies can be added.

## 11) Interview Demo Script (8-10 minutes)

1. Start at Home:
- Show signed-in dashboard, recent reports, watchlist snapshot.

2. Run research query:
- Use a query with multiple companies and recent news.
- Explain tool selection and resulting sections.

3. Save report:
- Show saved report id and open report detail.
- Highlight citations and tags.

4. Reports filtering:
- Filter by search term and tag.

5. Watchlist:
- Add and remove ticker.

6. Admin:
- Show member list and invite creation.

7. Isolation proof:
- Explain or demonstrate that org2 cannot read org1 report IDs.

Narration tip:
- Keep saying where enforcement happens (backend dependencies + org_id filters).

## 12) Tough Interview Questions and Strong Answers

Q1: How do you prevent cross-tenant data leakage?
A:
- TenantContext is resolved for each request,
- org_id is applied at query level for every tenant-owned resource,
- tests explicitly verify cross-org denial for read/list/delete paths.

Q2: Why not let the LLM do everything directly?
A:
- Full autonomy increases hallucination and unpredictability,
- explicit tool adapters keep sources traceable,
- fallback logic keeps system useful even with planner failure.

Q3: Why include both SQLAlchemy and Supabase REST paths?
A:
- Gives deployment flexibility,
- supports local relational flow and hosted Supabase integration,
- demonstrates abstraction around persistence while keeping route contracts stable.

Q4: What would you improve first for production?
A:
- centralized audit events,
- stronger observability and tracing,
- broader failure-mode tests,
- stricter planner output validation with schema/function-calling.

Q5: How did you choose what to build under time constraints?
A:
- prioritized end-to-end product correctness,
- prioritized security/isolation and source attribution,
- deferred lower-value infra polish that can be layered later.

## 13) 30-Minute Final Revision Plan (Before Interview)

1. Read sections 2, 4, 5, 7, 9, and 12 of this file.
2. Open architecture and decision docs and rehearse your own wording.
3. Rehearse the 8-10 minute demo once without interruptions.
4. Prepare one concrete "mistake and fix" story from implementation.

## 14) File Reading Order for Fast Code Refresh

If you have limited time, review in this order:
1. apps/api/app/main.py
2. apps/api/app/core/security.py
3. apps/api/app/core/tenant.py
4. apps/api/app/api/routes/research.py
5. apps/api/app/services/orchestrator.py
6. apps/api/app/api/routes/reports.py
7. apps/api/app/models/entities.py
8. apps/api/tests/test_tenant_isolation.py
9. apps/api/tests/test_reports_tags_search.py
10. apps/web/app/page.tsx
11. apps/web/components/ResearchConsole.tsx
12. apps/web/lib/api.ts

## 15) One-Sentence Summary To End Interview

"I built a tenant-safe, source-attributed AI research platform with explicit orchestration, robust backend enforcement, and a practical full-stack UX, and I can clearly show how each design choice balanced reliability, delivery speed, and extensibility."
