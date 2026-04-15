# DECISIONS.md (Working Draft)

## Why Option A
Selected Option A for best balance of delivery certainty and depth in a 5-day window while still demonstrating full-stack engineering, AI orchestration, and multi-tenant architecture.

## Tech Stack Rationale
- FastAPI: fast development speed, typed contracts, clean API layering.
- Next.js: strong DX for product UI and Auth0 integration.
- Supabase Postgres: managed relational DB with straightforward multi-tenant modeling.
- Auth0: robust auth provider with JWT/OIDC support.
- Gemini: flexible LLM choice for structured AI synthesis.
- FAISS local: low-cost local vector retrieval for ingesting sample filings.

## Multi-Tenant Pattern
Using a shared-schema approach with `org_id` in core entities and tenant middleware to enforce query-level isolation. Chosen for simplicity and speed within timeline.

## Trade-Offs
- Initial orchestration is scaffold-first to ensure end-to-end app stability early.
- Local FAISS chosen over hosted vector DB to control cost and setup complexity.
- Prioritized core rubric requirements over advanced analytics and streaming.

## What to Improve with 2 More Weeks
- Full Gemini function-calling with strict JSON schema enforcement.
- Rich report section modeling and citation graph.
- Integration and load testing.
- Better observability and cost dashboards.
