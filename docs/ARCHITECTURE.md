# Architecture (Working Draft)

## High-Level Components
- Next.js web app for authenticated UX and report views.
- FastAPI backend for auth verification, tenant isolation, RBAC, orchestration, and persistence.
- Supabase Postgres for transactional multi-tenant data.
- FAISS local index for document retrieval (planned expansion).
- External data tools: Yahoo Finance, NewsAPI.
- LLM layer: Gemini for structured synthesis (planned expansion over current scaffold).

## Data Flow (Current)
1. User logs in through Auth0 on frontend.
2. Frontend calls backend endpoints with bearer token.
3. Backend verifies JWT against Auth0 JWKS.
4. Tenant context resolves org membership and role.
5. Endpoint executes tenant-scoped queries and returns response.

## Data Flow (Target Research)
1. User submits natural-language research query.
2. Backend parses intent and decides required tools.
3. Tool layer fetches market/news/document data.
4. Orchestration composes structured sections with citations.
5. Response returned to frontend and persisted as report.

## Multi-Tenant Enforcement
- Tenant is resolved from authenticated user membership.
- All report queries enforce `org_id` scoping.
- RBAC checks on write actions.
- Organization invite-code onboarding is supported via admin-created invite tokens.

## Core Tables (Implemented Baseline)
- organizations
- users
- organization_memberships
- research_reports
- report_sections
- report_citations
- report_tags
- company_watchlists
- organization_invites

## Pending Expansion
- activity_logs
