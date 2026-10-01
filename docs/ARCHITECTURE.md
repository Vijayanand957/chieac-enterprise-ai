# Architecture Deep Dive

## Multi-agent design

The system uses an **orchestrator + specialist agents** pattern rather than a
single monolithic prompt:

- **Orchestrator** (`app/agents/orchestrator.py`) — classifies each incoming
  message into one or more intents (`retrieval`, `sql`, `forecast`, `general`)
  with a cheap, low-token routing call, then dispatches to the relevant
  specialist(s) and synthesizes a single answer. Every step is recorded in an
  `agent_trace` returned to the frontend so users (and interviewers!) can see
  *which* agent contributed *what* — this transparency is a deliberate design
  choice for enterprise trust and debuggability.
- **Retrieval agent** — RAG over uploaded documents using a local vector
  store (Chroma + sentence-transformers embeddings). Grounded, cited answers;
  explicitly says "I don't know" when nothing relevant is indexed.
- **SQL/analytics agent** — answers questions about structured operational
  data. Deliberately does *not* let the LLM generate raw SQL against
  production tables (a common injection/hallucination risk); instead it pulls
  a bounded, filtered result set via the ORM and asks the LLM to reason over
  the JSON, which is a safer pattern for production systems.
- **Forecasting agent** — wraps an XGBoost/time-series layer and narrates the
  result in business language.
- **Reporting/Recommendation agent** — synthesizes multiple agents' findings
  into an executive summary and prioritized action items.

## Why this design scales into a real internship deliverable

1. **Swap points are explicit.** The LLM client, vector store, and forecasting
   model are each behind a thin module boundary so they can be swapped
   (Claude → Azure OpenAI, Chroma → pgvector/Azure AI Search, XGBoost →
   Prophet) without touching agent logic.
2. **Safety-conscious by default.** No free-form SQL generation from the LLM;
   file upload type/size limits; retries with backoff on the LLM client.
3. **Observable.** Every chat response carries a structured trace of which
   agents ran and why — this is the seed of a proper eval/observability
   pipeline (e.g. logging traces to a table and building a dashboard of which
   agents get invoked most, latency per agent, etc. — a great "phase 2" item).

## Data model

- `documents` — metadata for uploaded files (the actual chunks live in the
  vector store, keyed by `doc_id`).
- `conversations` / `messages` — chat history, including the serialized agent
  trace per assistant message.
- `operational_metrics` — a generic fact table (`metric_name`, `dimension`,
  `value`, `recorded_at`) the SQL agent queries. In a real deployment this
  would be replaced by (or federated with) the organization's actual
  warehouse tables.
- `forecast_runs` — audit log of model training runs and their metrics.

## Known simplifications (call these out explicitly to reviewers)

- The time-series forecaster uses Holt's linear trend method rather than a
  heavier dependency (Prophet/ARIMA) to keep the container lightweight; the
  interface (`time_series_forecast`) is designed so swapping the
  implementation doesn't touch calling code.
- Intent classification is a single LLM call rather than a trained classifier
  — reasonable for a portfolio project's traffic volume; a production system
  handling high QPS would cache/distill this into a small classifier.
- Auth is a single shared API key placeholder (`core/security.py` stub) —
  a real deployment should integrate Azure AD / OAuth2.
