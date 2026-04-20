# Architecture

## 1. System Architecture
The project follows a decoupled architecture where the frontend serves as a thin client for the FastAPI backend, which acts as the central controller for authentication, database persistence, and AI orchestration.

Primary components:
1. Client layer (`apps/web`): Next.js frontend for dashboard, reports, watchlist, and admin workflows.
2. API layer (`apps/api`): FastAPI app with Auth0 JWT validation, tenant/RBAC resolution, business routes, and orchestration control.
3. Data layer: PostgreSQL (Supabase-compatible) for tenant-scoped persistence plus FAISS index for document context retrieval.
4. AI layer: Gemini for planning and summary synthesis.
5. External APIs: Yahoo Finance (market data) and NewsAPI (news/sentiment).

## 2. System Architecture Diagram (Logical)
```mermaid
flowchart TB
    subgraph Client
        FE[Next.js Frontend]
    end

    FE -->|REST + JWT| SEC[Auth0 Security Middleware]

    subgraph API
        SEC -->|Validated Context| APP[FastAPI Application]
        APP -->|Execute Research| ORCH[Research Orchestrator]
    end

    subgraph Services
        DB[(PostgreSQL DB)]
        VEC[(FAISS Vector Index)]
        LLM[Gemini LLM - Planner and Synthesizer]
        EXT[Market and News APIs]
    end

    APP -->|CRUD org_id scoped| DB
    ORCH -->|Context Retrieval| VEC
    ORCH -->|Planning and Summary| LLM
    ORCH -->|External Data| EXT
```

## 3. High-Level Data Flow
1. Authentication: Users authenticate via Auth0; the frontend includes the Bearer token in API requests.
2. Context resolution: Backend validates JWT and resolves tenant context (`org_id`, `role`, `user_id`) via membership lookup.
3. Research orchestration: `run_research` triggers Gemini-assisted planning, external data fetches (yfinance, NewsAPI), FAISS retrieval, and structured synthesis.
4. Persistence: Reports, sections, tags, and citations are written to PostgreSQL with explicit organization scoping.

## 4. Data Flow Diagram (UI Input to Rendered Output)
```mermaid
sequenceDiagram
		participant U as User
		participant W as Next.js UI
		participant A as FastAPI
		participant T as Auth/Tenant Middleware
		participant O as Research Orchestrator
		participant G as Gemini
		participant E as External APIs
		participant F as FAISS
		participant D as PostgreSQL

		U->>W: Submit research query
		W->>A: POST /api/v1/research/run-and-save (Bearer JWT)
		A->>T: Validate JWT + resolve org_id/role
		T-->>A: TenantContext(org_id, role, user_id)
		A->>O: Execute query with tenant context
		O->>G: Plan tools + synthesize summary
		O->>E: Fetch market/news data
		O->>F: Retrieve document chunks
		O-->>A: Structured sections + citations + summary
		A->>D: Write report/sections/citations (org_id scoped)
		D-->>A: Persisted record IDs
		A-->>W: Structured response JSON
		W-->>U: Render cards/charts/citations
```

## 5. Database Schema / ER Diagram
```mermaid
erDiagram
    ORGANIZATIONS ||--o{ ORGANIZATION_MEMBERSHIPS : has
    USERS ||--o{ ORGANIZATION_MEMBERSHIPS : belongs_to
    ORGANIZATIONS ||--o{ ORGANIZATION_INVITES : has
    ORGANIZATIONS ||--o{ RESEARCH_REPORTS : owns
    USERS ||--o{ RESEARCH_REPORTS : creates
    RESEARCH_REPORTS ||--o{ REPORT_SECTIONS : contains
    REPORT_SECTIONS ||--o{ REPORT_CITATIONS : cites
    RESEARCH_REPORTS ||--o{ REPORT_TAGS : tagged_with
    ORGANIZATIONS ||--o{ COMPANY_WATCHLISTS : tracks

    ORGANIZATIONS {
        int id
        string name
        string created_at
    }

    USERS {
        int id
        string auth0_sub
        string email
        string full_name
        string created_at
    }

    ORGANIZATION_MEMBERSHIPS {
        int id
        int org_id
        int user_id
        string role
    }

    RESEARCH_REPORTS {
        int id
        int org_id
        int created_by_user_id
        string title
        string query_text
        string status
        string summary
        string created_at
        string updated_at
    }

    REPORT_SECTIONS {
        int id
        int report_id
        string title
        string body
        int order_index
    }

    REPORT_CITATIONS {
        int id
        int section_id
        string source_type
        string source_name
        string reference
    }

    REPORT_TAGS {
        int id
        int report_id
        string name
    }

    COMPANY_WATCHLISTS {
        int id
        int org_id
        string ticker
        string company_name
        string created_at
    }

    ORGANIZATION_INVITES {
        int id
        int org_id
        string code
        string expires_at
        string used_at
        string created_at
    }
```

Key indexes currently implemented:
1. `users.auth0_sub` unique index for auth lookup.
2. `research_reports.org_id` + composite index `ix_reports_org_created(org_id, created_at)` for tenant queries.
3. `report_tags.report_id` and `report_tags.name` for report filtering.
4. `company_watchlists.org_id` and `company_watchlists.ticker` for tenant watchlist operations.

Audit logs:
1. Dedicated audit-event table is not yet implemented.
2. Current traceability is through timestamps, ownership fields, and request logging.

## 6. AI Orchestration Flow
```mermaid
flowchart LR
		Q[User Query] --> P[Planner Stage\nGemini JSON Plan]
		P --> V{Plan Valid?}
		V -->|Yes| M[Select Tools]
		V -->|No| Fallback[Deterministic Fallback Rules]
		Fallback --> M
		M --> MK[Market Data Tool]
		M --> NW[News Tool]
		M --> DR[Document Retrieval Tool]
		MK --> AGG[Aggregate Tool Results]
		NW --> AGG
		DR --> AGG
		AGG --> SYN[Gemini Summary Synthesis]
		SYN --> OUT[Structured Output\nsections + citations + summary]
```

Execution behavior:
1. Planner decides tool usage and ticker hints.
2. Tools execute sequentially per selected scope and produce normalized sections.
3. Aggregated sections are optionally summarized by Gemini.
4. Final response is returned in a typed schema (`title`, `executive_summary`, `sections`, `citations`).

## 7. Multi-Tenant Data Flow (Isolation)
```mermaid
flowchart TD
    REQ["Incoming API Request plus Bearer JWT"] --> AUTH["Auth0 JWT Verification via JWKS"]
    AUTH --> USER["Resolve Current User from sub"]
    USER --> TENANT["Resolve Membership and TenantContext<br>org_id, role, user_id"]

    TENANT --> GATE{"RBAC Check"}
    GATE -->|Allowed| HANDLER["Route Handler"]
    GATE -->|Denied| FORBID["403 Forbidden"]

    HANDLER --> FILTER["Apply org_id filter on tenant-owned query"]
    FILTER --> DATA[("PostgreSQL or Supabase")]
    DATA --> SCOPED["Tenant-scoped rows only"]
    SCOPED --> RESP["API Response"]

    subgraph IG["Isolation Guarantee"]
        A1["Org A token gives org_id A"]
        B1["Org B token gives org_id B"]
        A1 --> A2["Queries constrained to org_id A"]
        B1 --> B2["Queries constrained to org_id B"]
    end
```

Isolation enforcement points:
1. Authentication and token verification.
2. Tenant context resolution from membership.
3. Query-level `org_id` scoping on every tenant-owned resource.
4. Role checks (`admin`, `analyst`) for privileged actions.

Leak-prevention guarantee:
1. Org A and Org B requests resolve different `org_id` values.
2. Data access is constrained by `org_id` at backend query level, not just UI filtering.

## 8. API Design (Methods, Auth, Request/Response)
All endpoints are under `/api/v1`.

| Endpoint | Method | Auth | Request Shape | Response Shape |
|---|---|---|---|---|
| `/health` | GET | No | None | `{ status: "ok" }` |
| `/research/run` | POST | JWT required | `{ query: string }` | `ResearchResponse` |
| `/research/run-and-save` | POST | JWT required | `{ query: string }` | `ResearchResponse` + persisted `report_id` |
| `/research/ingest-documents` | POST | JWT required | None | `{ status, ingested_chunks }` |
| `/reports` | GET | JWT required | Query: `search?`, `tag?` | `ReportOut[]` (tenant scoped) |
| `/reports/{id}` | GET | JWT required | Path: `id` | `ReportDetailOut` |
| `/reports` | POST | JWT required | `ReportCreate` | `ReportOut` |
| `/reports/{id}` | PATCH | JWT required | `ReportUpdate` | `ReportOut` |
| `/reports/{id}` | DELETE | JWT required | Path: `id` | `204 No Content` |
| `/reports/{id}/tags` | POST | JWT required | Query: `name` | `ReportOut` |
| `/reports/{id}/tags/{tag}` | DELETE | JWT required | Path: `id`, `tag` | `ReportOut` |
| `/watchlist` | GET | JWT required | None | `WatchlistOut[]` |
| `/watchlist` | POST | JWT required | `WatchlistCreate` | `WatchlistOut` |
| `/watchlist/{id}` | DELETE | JWT required | Path: `id` | `204 No Content` |
| `/orgs/members` | GET | JWT required | None | `MembershipOut[]` |
| `/orgs/invites` | POST | JWT required (`admin`) | None | `InviteOut` |
| `/orgs/join` | POST | JWT required | `{ invite_code: string }` | `MembershipOut` |

## 9. Reliability and Security Notes
1. Auth0 JWT verification through JWKS.
2. Backend-only handling of secret API keys.
3. Tenant and RBAC guards on protected routes.
4. Structured response models with pydantic validation.
5. Integration tests cover tenant isolation and admin gate checks.

## 10. Known Gaps / Next Hardening
1. Add centralized retries/circuit-breakers per external tool.
2. Add richer observability dashboards and tracing.
3. Add dedicated audit-event persistence.
4. Expand integration tests for failure-path behavior.

## 11. System Entity Mapping
The following sequence view captures the system entity mapping for the research execution path, aligned with the architecture interaction flow.

```mermaid
sequenceDiagram
	participant RC as ResearchConsole (apps/web)
	participant RR as Research Router (apps/api)
	participant OR as Orchestrator (orchestrator.py)
	participant GS as GeminiService (gemini_service.py)
	participant TA as Tool Adapters (market/news/docs)

	RC->>RR: POST /research/run-and-save
	RR->>OR: run_research(query)
	OR->>GS: plan_tools(query)
	GS-->>OR: ToolPlan (JSON)
	OR->>TA: Execute selected tools
	TA-->>OR: Data Results
	OR->>GS: synthesize_summary(context)
	OR-->>RR: ResearchResponse
	RR->>RR: Persist ResearchReport & ReportSection
	RR-->>RC: report_id
```
