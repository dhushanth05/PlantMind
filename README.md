# PlantMind

PlantMind is an AI-powered Industrial Knowledge Intelligence Platform for ingesting industrial documents, constructing a knowledge graph, supporting a conversational copilot with citations, analyzing risk, and surfacing lessons learned from historical incidents.

This repository currently contains the initial architecture skeleton only. Business logic is intentionally not implemented yet.

## Architecture

PlantMind is organized as a production-oriented monorepo:

```text
apps/
  api/       FastAPI, Python 3.12, Pydantic, LangGraph, AI services
  web/       React, TypeScript, Vite, TailwindCSS, ShadCN UI, React Flow, Zustand
docs/        architecture docs and future ADRs
infra/       Docker and database infrastructure
scripts/     developer automation
```

## Backend

The backend separates HTTP routes, domain services, AI integrations, LangGraph agents, workflows, and persistence adapters.

Core API modules:

- Authentication
- Document APIs
- Chat APIs
- Graph APIs
- Risk APIs
- Compliance APIs
- Alert APIs

AI services:

- Entity Extraction Service
- Embedding Service
- Citation Service
- Pattern Detection Service
- Risk Scoring Service

Agent layer:

- Ingestion Agent
- Graph Builder Agent
- Retriever Agent
- Synthesis Agent
- Citation Agent
- Pattern Agent
- Risk Agent
- Compliance Agent

## Frontend

The frontend is divided into feature modules:

- Dashboard
- Document Upload
- Knowledge Graph Explorer
- Asset Digital Twin
- AI Copilot Chat
- Risk Intelligence Center
- Compliance Center
- Alerts Center

Shared shell code lives in `apps/web/src/app`, reusable ShadCN UI primitives live in `apps/web/src/components/ui`, layout components live in `apps/web/src/components/layout`, and cross-feature Zustand stores live in `apps/web/src/stores`.

## Data Stores

MongoDB stores document metadata, chunks, vector metadata, conversations, incidents, risk outputs, compliance evidence, alerts, and audit events.

Neo4j stores the industrial knowledge graph with assets, systems, documents, chunks, extracted entities, incidents, hazards, controls, requirements, and lessons learned.

Redis is reserved for caching, sessions, workflow state, rate limits, and future background coordination.

## Docker

The local Docker architecture includes:

- `web`: Vite development server
- `api`: FastAPI development server
- `mongodb`: document and vector metadata store
- `neo4j`: graph database
- `redis`: cache and workflow support

Start locally:

```bash
cp .env.example .env
docker compose up --build
```

## Architecture Docs

- `docs/architecture/folder-structure.md`
- `docs/architecture/backend.md`
- `docs/architecture/frontend.md`
- `docs/architecture/langgraph.md`
- `docs/architecture/data-model.md`
- `docs/architecture/docker.md`
- `docs/architecture/folder-catalog.md`
