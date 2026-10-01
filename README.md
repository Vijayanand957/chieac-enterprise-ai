# Enterprise AI Operations Assistant

An end-to-end, cloud-deployable AI platform that lets business users ask natural-language
questions about their organization's data and get back grounded answers, executive
summaries, interactive visualizations, and predictive insights (churn, operational risk,
incident forecasting).

Built as a professional portfolio project demonstrating production patterns for
Generative AI + MLOps: RAG, multi-agent orchestration, predictive ML, and a
cloud-native deployment pipeline.

## Architecture

```
                        ┌─────────────────────────┐
                        │        Frontend          │
                        │   Next.js / React (TS)   │
                        │  Chat · Dashboards ·      │
                        │  Forecast charts          │
                        └────────────┬─────────────┘
                                     │ REST / SSE
                        ┌────────────▼─────────────┐
                        │         FastAPI           │
                        │   /chat  /documents        │
                        │   /analytics /forecast      │
                        └────────────┬─────────────┘
                                     │
                     ┌───────────────▼────────────────┐
                     │         Orchestrator Agent       │
                     │  routes a user query to one or   │
                     │  more specialist agents, then     │
                     │  synthesizes the final answer     │
                     └──┬───────┬───────┬───────┬──────┘
                        │       │       │       │
             ┌──────────▼┐ ┌────▼────┐ ┌▼───────────┐ ┌▼─────────────┐
             │ Retrieval  │ │  SQL /  │ │ Forecasting │ │  Reporting /  │
             │ (RAG) Agent│ │Analytics│ │   Agent     │ │ Recommendation│
             │            │ │  Agent  │ │  (XGBoost)  │ │     Agent     │
             └─────┬──────┘ └────┬────┘ └──────┬──────┘ └───────┬───────┘
                   │             │             │                │
          ┌────────▼───┐  ┌──────▼──────┐ ┌────▼─────┐   ┌──────▼──────┐
          │ Vector DB   │  │ PostgreSQL  │ │ Model     │   │  LLM        │
          │ (Chroma /   │  │ (structured │ │ Registry  │   │ (Claude API)│
          │  pgvector)  │  │   data)     │ │ (joblib)  │   │             │
          └─────────────┘  └─────────────┘ └───────────┘   └─────────────┘
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js (TypeScript), Tailwind, Recharts |
| API | Python, FastAPI, Pydantic v2 |
| Orchestration | LangChain-style agent graph (custom lightweight orchestrator) |
| LLM | Anthropic Claude API (swap-in ready for Azure OpenAI) |
| RAG | sentence-transformers embeddings + Chroma (local) / pgvector (prod) |
| Structured data | PostgreSQL + SQLAlchemy 2.0 |
| Predictive ML | XGBoost, scikit-learn, joblib model registry |
| Infra | Docker, docker-compose, GitHub Actions CI/CD, Azure Container Apps (Bicep) |
| Observability | structlog + /health, /metrics endpoints |

## Repository layout

```
backend/         FastAPI service, agents, RAG pipeline, ML models
frontend/        Next.js app (chat UI, dashboards, forecasting charts)
infra/azure/     Bicep templates + deploy script for Azure Container Apps
.github/workflows/  CI (lint+test+build) and CD (deploy) pipelines
docs/            Architecture notes and roadmap
```

## Local development

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY, DB creds
docker-compose up --build     # starts postgres, backend (:8000), frontend (:3000)
```

Backend docs: http://localhost:8000/docs
Frontend: http://localhost:3000

## Training the forecasting model

```bash
cd backend
python -m app.ml.train --dataset data/churn_sample.csv --target churn --out models/churn_xgb.json
```

## Deploying to Azure

```bash
cd infra/azure
az login
./deploy.sh <resource-group> <location>
```

This provisions: Azure Container Apps (backend + frontend), Azure Database for
PostgreSQL Flexible Server, Azure Container Registry, and Log Analytics — wired
together via `main.bicep`. The GitHub Actions workflow in
`.github/workflows/ci-cd.yml` builds images, pushes to ACR, and triggers a
revision update on every merge to `main`.

## Roadmap

See `docs/ROADMAP.md`.
