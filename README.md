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

## Current Status
- Baseline monorepo scaffold complete
- Auth0-aware tenant middleware implemented on backend
- Tenant-scoped report CRUD endpoints implemented
- Research endpoint scaffolded with dynamic tool selection

## Next Milestones
- Replace research synthesis stub with Gemini function-calling orchestration
- Add FAISS ingestion pipeline for filings and earnings docs
- Build structured UI components for report sections and citations
- Add deployment and demo assets
