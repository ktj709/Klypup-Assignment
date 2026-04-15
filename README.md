# Klypup Assignment - Option A (Investment Research Dashboard)

This repository contains a full-stack implementation scaffold for Option A using:
- Frontend: Next.js
- Backend: FastAPI
- Database: Supabase Postgres
- Auth: Auth0
- AI: Gemini (orchestration layer to be expanded)
- Market Data: yfinance
- News: NewsAPI (+ RSS fallback planned)

## Monorepo Structure
- apps/web: Next.js app
- apps/api: FastAPI app
- docs: Architecture and decision documents

## Why Option A
Option A was selected because it provides a strong balance of product impact and implementation depth for the 5-day timeline while clearly demonstrating AI orchestration, multi-tenant data isolation, and end-to-end full-stack engineering.

## Tech Stack Rationale
- Frontend: Next.js for fast product UI iteration and integrated Auth0 flow.
- Backend: FastAPI for typed APIs, dependency-based auth/tenant enforcement, and rapid integration work.
- Database: PostgreSQL (Supabase-compatible) for tenant-safe relational modeling.
- AI: Gemini for planner + synthesis workflows.
- Retrieval: FAISS local index for filing/earnings document context.

## Quick Start
### Backend
1. Copy `apps/api/.env.example` to `apps/api/.env`
2. Install dependencies:
   - `cd apps/api`
   - `pip install -r requirements.txt`
3. Run API:
   - `uvicorn app.main:app --reload --port 8000`

### Frontend
1. Copy `apps/web/.env.local.example` to `apps/web/.env.local`
2. Install dependencies:
   - `cd apps/web`
   - `npm install`
3. Run app:
   - `npm run dev`

## Setup Note
- Docker is intentionally not included in this submission scope.
- The evaluator can run the app locally using the steps above.

## Demo Seed Data
- Run `python scripts/seed_demo.py` from `apps/api` to create two sample organizations and memberships.

## Environment Variables
### Backend (`apps/api/.env`)
- `APP_NAME`: API service display name.
- `API_V1_PREFIX`: API route prefix.
- `ENVIRONMENT`: runtime mode.
- `DATABASE_URL`: PostgreSQL connection string.
- `AUTH0_DOMAIN`: Auth0 tenant domain.
- `AUTH0_AUDIENCE`: expected API audience in JWT.
- `AUTH0_ALGORITHMS`: JWT algorithm (RS256).
- `GEMINI_API_KEY`: Gemini API key.
- `GEMINI_MODEL`: Gemini model identifier.
- `NEWS_API_KEY`: News API key.
- `FAISS_INDEX_PATH`: FAISS index file path.
- `FAISS_META_PATH`: FAISS metadata file path.
- `CORS_ORIGINS`: allowed frontend origins.

### Frontend (`apps/web/.env.local`)
- `NEXT_PUBLIC_API_BASE_URL`: backend base URL.
- `AUTH0_SECRET`: session encryption secret.
- `APP_BASE_URL`: frontend base URL.
- `AUTH0_DOMAIN`: Auth0 tenant domain.
- `AUTH0_CLIENT_ID`: Auth0 app client id.
- `AUTH0_CLIENT_SECRET`: Auth0 app client secret.
- `AUTH0_AUDIENCE`: API audience requested from Auth0.

## Demo Workflows (Interview)
1. Core AI feature
   - Sign in, submit a research query, show structured sections/charts/citations, and save report.
2. Multi-tenant isolation
   - Use two org memberships, show one org cannot access the other org's report IDs.
3. RBAC behavior
   - Show admin invite-code creation and non-admin restriction.

## Screenshots (Add Before Submission)
Please add 4-6 screenshots in `docs/screenshots/` and reference them here.

Suggested captures:
1. Home dashboard (recent research + quick actions + bookmarks)
2. Research query result with charts and citations
3. Reports page with search/tag filters and report detail
4. Watchlist page
5. Admin page with invite code generation
6. Tenant isolation demonstration (two org contexts)

## Known Limitations
1. Advanced retry/circuit-breaker policy for all external tool calls is not fully implemented.
2. Additional integration tests beyond tenant/RBAC baseline are still recommended.
3. Live deployment URL is not included yet.

## Current Status
- Baseline monorepo scaffold complete
- Auth0-aware tenant middleware implemented on backend
- Tenant-scoped report CRUD endpoints implemented
- Research orchestration includes Gemini-assisted planning with safe fallback
- FAISS local ingestion and retrieval pipeline added for sample filings
- Run-and-save endpoint persists structured sections and citations
- Organization invite-code endpoints added for admin-managed onboarding
- Watchlist CRUD is implemented with dedicated UI page
- Report search and tag management are implemented in backend and frontend
- Admin page supports member view and invite-code creation

## Next Milestones
- Add deployment and final demo assets
- Expand integration tests for watchlist and tag management

## Useful API Calls
- POST /api/v1/research/ingest-documents
   - Builds the FAISS index from sample files under apps/api/data/documents
- POST /api/v1/research/run
   - Runs dynamic tool selection and returns structured response
- POST /api/v1/research/run-and-save
   - Runs research and persists report, sections, and citations
- GET /api/v1/reports?search=<query>&tag=<tag>
   - Retrieves tenant-scoped reports with optional search and tag filtering
- POST /api/v1/reports/{report_id}/tags?name=<tag>
   - Adds a tag to a report
- DELETE /api/v1/reports/{report_id}/tags/{tag_name}
   - Removes a tag from a report
- GET /api/v1/watchlist
   - Lists organization watchlist items
- POST /api/v1/watchlist
   - Adds ticker to watchlist
- DELETE /api/v1/watchlist/{watchlist_id}
   - Removes watchlist item
- GET /api/v1/orgs/members
   - Lists organization memberships
- POST /api/v1/orgs/invites
   - Creates invite code (admin only)
