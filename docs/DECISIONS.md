# DECISIONS.md

## 1. Option Choice
### Chosen Option
Option A (Investment Research Dashboard)

### Why
1. Best balance of business relevance and delivery confidence in a constrained timeline.
2. Strong alignment with rubric priorities: full-stack delivery, AI integration quality, multi-tenancy, and product UX.
3. Easier to demonstrate source-attributed AI reasoning with real data tools than a large multi-agent pricing control system in the same timeframe.

## 2. Stack Decisions and Alternatives
### Backend: FastAPI
Why selected:
1. Rapid API development with typed contracts and strong developer ergonomics.
2. Clean dependency-injection model for tenant/RBAC enforcement.

Alternatives considered:
1. Express/NestJS
2. Django/DRF

Trade-off:
- Python dependency footprint can be heavy, but implementation velocity and AI/data tooling compatibility were better.

### Frontend: Next.js
Why selected:
1. Product-ready React framework with good routing and server/client composition.
2. Straightforward Auth0 integration.

Alternatives considered:
1. Vite + React

Trade-off:
- Slightly more framework overhead than plain React, accepted for faster feature assembly.

### Auth: Auth0
Why selected:
1. Production-grade OIDC/JWT and user lifecycle primitives.
2. Clear role for interview discussion: token verification, JWKS, and middleware enforcement.

Trade-off:
- Third-party dependency and environment setup complexity.

### Database: PostgreSQL (Supabase-compatible)
Why selected:
1. Strong fit for tenant-aware relational modeling and filtering.
2. Easy expansion toward indexing and audit requirements.

Trade-off:
- Requires careful schema and query discipline to prevent tenant data leakage.

### Retrieval: FAISS local
Why selected:
1. Zero external infra required for vector retrieval prototype.
2. Low-cost and deterministic local behavior for assessment setting.

Trade-off:
- Less operationally scalable than managed vector stores.

### LLM: Gemini
Why selected:
1. Used both for tool planning and summary synthesis.
2. Works well with constrained prompt output and lightweight planning JSON.

Trade-off:
- Requires robust fallback when model output is malformed or unavailable.

## 3. Multi-Tenant Strategy
Pattern selected: shared-schema with strict query-level tenant filtering.

Implementation details:
1. Resolve tenant context from authenticated user membership.
2. Enforce `org_id` predicates across tenant-owned resources.
3. Maintain role checks (`admin`, `analyst`) for privileged endpoints.
4. Provide invite-code flow for organization onboarding.

Reasoning:
1. Fastest path to correctness for assessment timeline.
2. Clear and explainable implementation in interview.

## 4. AI Integration Design Decisions
1. Use LLM as orchestrator helper, not direct UI chatbot wrapper.
2. Keep tool layer explicit and auditable:
- market data tool
- news/sentiment tool
- document retrieval tool
3. Require structured output sections and citations for traceability.
4. Add safe deterministic fallback if planner output is missing/invalid.

Prompting strategy:
1. Planning prompt asks for strict JSON shape.
2. Synthesis prompt emphasizes no hallucinated facts and explicit uncertainty.

## 5. Timeline Trade-Offs Made
Given limited timeline, prioritized:
1. End-to-end correctness and demonstrable tenant isolation.
2. Structured source-attributed output over advanced quantitative modeling.
3. API and UI completeness over heavy infrastructure automation.

Deferred:
1. Full function-calling tool execution framework.
2. Streaming responses and advanced observability.
3. Broader test matrix and performance benchmarking suite.

## 6. Hardest Problems and How They Were Solved
1. Ensuring tenant isolation across all CRUD paths
- Solved by central tenant context dependency and query-level org filters.
2. Getting AI to make tool decisions reliably
- Solved by combining LLM plan with deterministic fallback.
3. Preserving source attribution in persisted reports
- Solved by explicit section/citation model and run-and-save persistence endpoint.

## 7. Cost and Operational Considerations
1. Chosen low-infrastructure architecture (no mandatory Docker/cluster complexity).
2. FAISS local avoids managed vector database cost for prototype.
3. LLM usage constrained to planning and concise summary generation.
4. API-first design supports later addition of caching/rate-limits for cost control.

## 8. What I Would Improve With Two More Weeks
1. Convert planner to strict schema/function-call execution path.
2. Add robust retries/timeouts/circuit breakers for external tools.
3. Add richer watchlist automations and scheduled refresh pipelines.
4. Add complete integration test suite for tags, watchlist, and invite join flow.
5. Add observability dashboards and request tracing.
6. Add cloud deployment artifacts and CI/CD pipeline.
