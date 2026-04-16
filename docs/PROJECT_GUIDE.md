# Project Guide: Klypup Assignment (Option A)

This document explains how the project works end-to-end so you can quickly understand, run, debug, and present it.

## 1. What This Project Is

This is a full-stack Investment Research Dashboard built for Klypup Option A.

Primary goals:
- Accept natural-language research queries from analysts.
- Use an AI-assisted orchestration flow to choose and run data tools.
- Return structured, source-attributed output (not plain chatbot text).
- Persist reports in a multi-tenant, role-based workspace.

Business value:
- Reduce analysis turnaround from days to minutes for first-draft research.
- Improve analyst productivity with reusable reports and watchlists.
- Keep evidence traceable through section-level citations.

## 2. Stack and Why It Was Chosen

- Frontend: Next.js (React)
- Backend: FastAPI (Python)
- Database: PostgreSQL (Supabase-compatible)
- Auth: Auth0 (JWT + JWKS verification)
- LLM: Gemini
- Market data: yfinance
- News: NewsAPI
- Document retrieval: FAISS local index

This stack balances speed of delivery and architecture clarity for interview discussion.

## 3. Monorepo Layout

- apps/api
  - FastAPI backend, models, routes, services, tests, seed script
- apps/web
  - Next.js app, pages, components, auth middleware, API client
- docs
  - Architecture, decisions, compliance checklist, demo script, Q&A prep

## 4. High-Level Architecture

Request path (typical):
1. User signs in via Auth0 on web app.
2. Web app calls FastAPI with bearer token.
3. FastAPI verifies token with Auth0 JWKS.
4. FastAPI resolves tenant context (org + role).
5. API route executes tenant-scoped business logic.
6. For research flow, orchestrator calls tools and LLM synthesis.
7. Structured output is returned and optionally saved.

Key boundaries:
- Browser never calls LLM provider directly.
- Browser never calls external market/news tools directly.
- All secrets remain server-side in env files.

## 5. Backend Deep Dive

### 5.1 Entry Point and Middleware

Main file:
- apps/api/app/main.py

Responsibilities:
- Create FastAPI app.
- Enable CORS.
- Register all routes.
- Create DB tables at startup.
- Add request logging middleware with:
  - generated or propagated request ID
  - response status
  - latency in ms
  - x-request-id response header

### 5.2 Configuration

Config file:
- apps/api/app/core/config.py

Includes:
- App config (name, prefix, environment)
- DB URL
- Auth0 settings
- Gemini and News API keys
- FAISS paths
- External retry/timeout settings
- Request logging flag

### 5.3 Authentication and Tenant Isolation

Auth verification:
- apps/api/app/core/security.py

Tenant resolution:
- apps/api/app/core/tenant.py

How it works:
1. Decode JWT and validate against Auth0 issuer/audience.
2. Cache JWKS for a short period and retry JWKS fetch when needed.
3. Find or create local user by auth0_sub.
4. Resolve user membership to current organization.
5. Build TenantContext { org_id, role, user_id }.

Isolation rule:
- Every tenant-owned query filters by org_id from TenantContext.

### 5.4 Database and Models

DB session:
- apps/api/app/db/session.py

Core models:
- apps/api/app/models/entities.py

Implemented entities:
- organizations
- users
- organization_memberships (role per org)
- organization_invites
- research_reports
- report_sections
- report_citations
- report_tags
- company_watchlists

### 5.5 API Routes

Health:
- apps/api/app/api/routes/health.py
  - GET /api/v1/health

Research:
- apps/api/app/api/routes/research.py
  - POST /api/v1/research/run
  - POST /api/v1/research/run-and-save
  - POST /api/v1/research/ingest-documents

Reports:
- apps/api/app/api/routes/reports.py
  - GET /api/v1/reports (search + tag filters)
  - GET /api/v1/reports/{report_id}
  - POST /api/v1/reports
  - PATCH /api/v1/reports/{report_id}
  - DELETE /api/v1/reports/{report_id}
  - POST /api/v1/reports/{report_id}/tags
  - DELETE /api/v1/reports/{report_id}/tags/{tag_name}

Organizations:
- apps/api/app/api/routes/orgs.py
  - GET /api/v1/orgs/members
  - POST /api/v1/orgs/invites (admin-only)
  - POST /api/v1/orgs/join

Watchlist:
- apps/api/app/api/routes/watchlist.py
  - GET /api/v1/watchlist
  - POST /api/v1/watchlist
  - DELETE /api/v1/watchlist/{watchlist_id}

## 6. AI and Orchestration Flow

Orchestrator:
- apps/api/app/services/orchestrator.py

Supporting services:
- apps/api/app/services/gemini_service.py
- apps/api/app/services/market_data.py
- apps/api/app/services/news_data.py
- apps/api/app/services/document_retrieval.py

Execution sequence:
1. Parse user query.
2. Ask Gemini planner for tool plan in strict JSON shape:
   - tickers
   - use_market_data
   - use_news
   - use_documents
3. If planner fails or returns invalid output, fallback logic is used.
4. Selected tools run and produce structured data.
5. Build report sections with citations.
6. Optionally ask Gemini to synthesize executive summary.
7. Return ResearchResponse.
8. In run-and-save path, persist report + sections + citations and return report_id.

Resilience built in:
- Graceful fallback on LLM exceptions.
- News API retries with timeout and backoff.
- Market data defensive failure handling.
- Orchestration continues with partial outputs where possible.

## 7. Document Retrieval Pipeline (FAISS)

File:
- apps/api/app/services/document_retrieval.py

Data source:
- apps/api/data/documents/*.txt

Pipeline:
1. Read documents.
2. Chunk text with overlap.
3. Create deterministic local embeddings (prototype-friendly).
4. Build FAISS index and metadata.
5. Query top-k relevant chunks for research questions.

Ingestion endpoint:
- POST /api/v1/research/ingest-documents

## 8. Frontend Deep Dive

### 8.1 App Shell and Auth

- apps/web/app/layout.tsx
  - Global layout and top navigation
- apps/web/middleware.ts
  - Auth0 middleware hook
- apps/web/app/api/auth/[auth0]/route.ts
  - Auth0 route handlers
- apps/web/lib/auth0.ts
  - Auth0 client setup

### 8.2 Pages

Home dashboard:
- apps/web/app/page.tsx
- Shows:
  - recent reports
  - bookmarked companies (watchlist)
  - quick actions
  - research console when signed in

Reports:
- apps/web/app/reports/page.tsx
- Supports:
  - search and tag filters
  - report table listing
  - interactive detail view (tag add/remove)
  - error-state message on load failure

Watchlist:
- apps/web/app/watchlist/page.tsx
- Supports create/list/remove flow
- Includes load error handling

Admin:
- apps/web/app/admin/page.tsx
- Supports:
  - member list
  - invite code generation for admin users

Global resilience:
- apps/web/app/loading.tsx
- apps/web/app/error.tsx

### 8.3 Components

- ResearchConsole: query submission + save flow
- ResearchCharts: sentiment and citation chart widgets
- ReportTable: report listing
- ReportDetailInteractive: section display + tag operations
- WatchlistPanel: watchlist operations
- AdminPanel: invite and member management

### 8.4 Frontend API Client

File:
- apps/web/lib/api.ts

Contains typed API calls for:
- reports, report details, tags
- research run and run-and-save
- watchlist CRUD
- org members and invite creation

## 9. Multi-Tenant and RBAC Rules

Roles:
- admin
- analyst

Rules in practice:
- Reports and watchlist are always org-scoped.
- Admin-only action currently enforced:
  - create org invite code
- Cross-org access is blocked by query-level filtering and route checks.

## 10. Running the Project Locally

### Backend
1. cd apps/api
2. Copy .env.example to .env and fill values
3. Install deps
4. Start API:
   - uvicorn app.main:app --reload --port 8000

Optional seed:
- python scripts/seed_demo.py

### Frontend
1. cd apps/web
2. Copy .env.local.example to .env.local and fill values
3. Install deps
4. Start app:
   - npm run dev

## 11. Testing

Test files:
- apps/api/tests/test_tenant_isolation.py
- apps/api/tests/test_reports_tags_search.py
- apps/api/tests/test_watchlist.py

Coverage includes:
- tenant isolation
- RBAC gate check on invite creation
- report tags and filtered search
- watchlist CRUD and cross-tenant access restrictions

## 12. Logging and Observability

Current:
- request-level logging in middleware
- request ID propagation via x-request-id
- per-request latency logging

Planned future:
- richer structured logging sink
- metrics dashboard
- circuit breaker and cache telemetry

## 13. Security Posture

Implemented safeguards:
- JWT verification against Auth0 issuer/audience
- backend-only secret use
- query-level tenant isolation
- role checks for privileged actions
- env template files committed, real env files excluded

## 14. Demo and Interview Assets

Available docs:
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/ASSESSMENT_COMPLIANCE.md
- docs/DEMO_SCRIPT.md
- docs/INTERVIEW_QA.md

Screenshot placeholders:
- docs/screenshots/README.md

## 15. What Is Still Manual

Before final submission, manually add:
1. Real screenshots under docs/screenshots.
2. Optional deployment URL if you choose to include a live demo bonus.

## 16. Quick Troubleshooting

If login works but APIs fail:
- verify AUTH0_AUDIENCE and backend audience match
- verify token is sent to backend

If research returns sparse output:
- check GEMINI_API_KEY and NEWS_API_KEY
- run /research/ingest-documents once

If tenant data looks missing:
- verify membership records for that user and org
- run seed script and re-check org context

If frontend cannot reach backend:
- verify NEXT_PUBLIC_API_BASE_URL
- verify backend CORS includes frontend origin

## 17. Code Navigation Shortcuts

Start here for architecture understanding:
1. apps/api/app/main.py
2. apps/api/app/core/security.py
3. apps/api/app/core/tenant.py
4. apps/api/app/services/orchestrator.py
5. apps/api/app/models/entities.py
6. apps/web/app/page.tsx
7. apps/web/app/reports/page.tsx
8. apps/web/lib/api.ts

This guide should be enough for end-to-end comprehension and confident interview walkthrough.