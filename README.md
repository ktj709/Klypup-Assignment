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
- Expand test coverage beyond core tenant/RBAC checks

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
