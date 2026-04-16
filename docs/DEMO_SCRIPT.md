# Demo Script (15 Minutes)

## 0-2 min: Context and Problem
1. Introduce Option A and business pain: analysts spend days manually assembling fragmented data.
2. Explain objective: reduce time-to-insight to minutes with structured, source-attributed AI outputs.

## 2-5 min: Architecture Walkthrough
1. Show frontend and backend responsibilities.
2. Explain Auth0 + tenant middleware + RBAC path.
3. Explain orchestration flow: planner -> tools -> synthesis -> structured persistence.

## 5-11 min: Live Product Demo
### Workflow 1: Core AI Feature
1. Sign in.
2. Run a multi-company research query.
3. Show structured sections, charts, and citation attribution.
4. Save report and open detail view.

### Workflow 2: Multi-Tenant Isolation
1. Show Org A report list.
2. Switch user/org context.
3. Show Org B cannot access Org A reports.

### Workflow 3: RBAC Differences
1. In admin context, generate org invite code.
2. In non-admin context, show restricted behavior.

## 11-13 min: Engineering Choices
1. Why FastAPI + Next.js + Postgres + Gemini + FAISS.
2. Why shared-schema tenancy with strict org_id filtering.
3. Why fallback orchestration logic for reliability.

## 13-15 min: Trade-offs and Next Steps
1. Mention current limitations and hardening path.
2. Mention what would be improved in 2 weeks.
