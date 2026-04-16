# Interview Q&A Prep

## Architecture
### Q: Why shared-schema tenancy instead of schema-per-tenant?
A: Shared-schema was chosen for speed and clarity in a 5-day scope while still enforcing strict query-level isolation through tenant middleware and org filters.

### Q: How do you prevent cross-tenant data leaks?
A: Every tenant-owned resource query includes org_id filtering resolved from authenticated membership context. UI-level filtering is not trusted.

## AI and Orchestration
### Q: Is this just a chatbot wrapper?
A: No. The backend orchestrates tool decisions and retrieval pipelines, returns structured sections, and persists citation-attributed outputs.

### Q: What happens when LLM/tool calls fail?
A: Planner and synthesis have graceful fallback behavior; external request retries/timeouts are configured; tool failures return partial but usable output instead of crashing.

## Data and Persistence
### Q: How are reports stored?
A: Reports are normalized across reports, sections, citations, and tags for structured retrieval and filtering.

### Q: Why FAISS local?
A: Low-cost, dependency-light retrieval for prototype constraints with deterministic ingestion and search behavior.

## Product and Delivery
### Q: What did you prioritize under time pressure?
A: End-to-end correctness, tenant safety, structured AI output, and demo reliability over advanced streaming/deployment features.

### Q: What would you improve with two more weeks?
A: Deeper integration tests, stronger observability, cache/rate-limit controls, and full deployment + CI pipeline.
