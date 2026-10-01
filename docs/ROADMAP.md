# Roadmap

## Phase 1 — Foundation (weeks 1-3)
- [x] FastAPI backend skeleton with health checks
- [x] Multi-agent orchestrator (retrieval, SQL, forecasting, reporting)
- [x] RAG pipeline (chunking, embeddings, Chroma vector store)
- [x] XGBoost forecasting model + training CLI
- [x] Next.js chat UI + forecast charts
- [x] Docker Compose local environment
- [x] CI pipeline (lint + test)

## Phase 2 — Production hardening (weeks 4-6)
- [ ] Swap shared API key for Azure AD / OAuth2 authentication
- [ ] Move vector store to pgvector or Azure AI Search for horizontal scaling
- [ ] Add Alembic migrations instead of `create_all` on startup
- [ ] Add per-agent latency/error metrics (OpenTelemetry → Azure Monitor)
- [ ] Rate limiting and request quotas per user/org
- [ ] Add automated evals: a golden set of Q&A pairs to catch retrieval/agent regressions

## Phase 3 — Feature depth (weeks 7-10)
- [ ] Streaming chat responses (SSE) instead of blocking request/response
- [ ] Multi-turn conversation memory summarization for long chats
- [ ] Scheduled executive summary emails (weekly digest)
- [ ] Additional predictive models: operational risk scoring, incident time-to-resolution
- [ ] Role-based dashboards (exec view vs. analyst view)
- [ ] Support for connecting a live data warehouse (Snowflake/BigQuery) instead of the demo `operational_metrics` table

## Phase 4 — Polish & showcase (weeks 11-12)
- [ ] Public demo mode with synthetic sample data pre-loaded
- [ ] Architecture diagram + case-study write-up for portfolio
- [ ] Load testing report (Locust) and cost-per-query analysis
- [ ] Recorded walkthrough video for recruiters
