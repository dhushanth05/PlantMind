# 🌿 PlantMind

> **AI-Powered Industrial Knowledge Intelligence Platform**

Transform industrial documents into searchable operational intelligence using AI, hybrid retrieval, knowledge graphs, and a grounded AI copilot.

---

<p align="center">
  <img src="docs/screenshots/dashboard.png" width="90%">
</p>
> Industrial knowledge intelligence for plant teams: upload technical PDFs, extract evidence, explore equipment relationships, ask a grounded copilot, review operational analytics, and reset demo data safely.

PlantMind is a hackathon-ready full-stack application for turning industrial documents into searchable operational knowledge. It combines a FastAPI ingestion and intelligence backend with a React workspace for document upload, hybrid search, graph exploration, asset context, copilot Q&A, dashboards, and demo-safe factory reset.

## Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [How to Run](#how-to-run)
- [API Overview](#api-overview)
- [Screenshots](#screenshots)
- [Demo Workflow](#demo-workflow)
- [Factory Reset](#factory-reset)
- [Future Improvements](#future-improvements)
- [Team / Author](#team--author)
- [License](#license)

## Overview

Industrial teams often need to reason across maintenance reports, inspection records, procedures, incident narratives, equipment history, and lessons learned. PlantMind gives those documents a working interface:

1. PDF files are uploaded into a backend ingestion pipeline.
2. Text is extracted, chunked, embedded, and converted into graph context.
3. Operators can search evidence, inspect relationships, and ask a copilot grounded in retrieved document chunks.
4. Dashboards summarize risk, compliance, alerts, executive analytics, and asset health views.
5. A guarded Factory Reset clears runtime demo data so the same environment can be reused for judging or demos.

The codebase is organized as a monorepo with a Python API, TypeScript frontend, Docker Compose infrastructure, and architecture notes under `docs/`.

## Problem Statement

Plant knowledge is usually scattered across static PDFs, work orders, inspection reports, and incident documents. During operational reviews or abnormal events, teams need fast answers with traceable evidence, not just keyword matches. PlantMind addresses this by combining document ingestion, hybrid retrieval, graph context, and citation-aware chat into one plant intelligence workspace.

## Key Features

Only features implemented in this repository are listed here.

| Area | Implemented capability |
| --- | --- |
| Document ingestion | Multi-PDF upload UI, PDF validation, size limit enforcement, persistent file storage, document records, text/chunk/entity/graph/embedding pipeline hooks, upload history, retry/cancel UI states |
| Hybrid search | `/api/v1/search/query` endpoint using a `HybridRetriever`, evidence ranking, graph context, confidence score, and Redis response caching |
| AI copilot | Chat endpoint with conversation memory, retrieval-grounded prompt construction, Gemini client integration, citation resolution, fallback evidence answers, follow-up questions, and related assets |
| Knowledge graph explorer | Graph overview, node search, subgraph loading, equipment context, graph analytics, React Flow canvas, filters, search, node drawer, neighbor highlighting, and analytics sidebar |
| Asset digital twin | Asset-specific digital twin route and frontend page for `/assets/:assetId`, backed by asset services and tests |
| Dashboards | Main dashboard, risk dashboard, compliance dashboard, alerts dashboard, and executive analytics frontend routes backed by API services |
| Factory Reset | Settings UI danger zone and `DELETE /api/v1/admin/factory-reset` endpoint that clears runtime MongoDB collections, Neo4j graph data, Redis cache keys, uploaded files, and temporary processing folders |
| App shell | React Router workspace, lazy-loaded feature pages, TanStack Query caching, Zustand app store, dark mode support, offline banner, toast notifications, and error boundaries |
| Infrastructure | Docker Compose services for API, web, MongoDB, Neo4j with APOC, and Redis |
| Tests | Backend tests for chat copilot, document pipeline, hybrid search, graph explorer, dashboard, risk dashboard, asset digital twin, and factory reset |

## Architecture

```text
                    +-----------------------------+
                    | React + Vite web workspace  |
                    | http://localhost:5173       |
                    +--------------+--------------+
                                   |
                                   | REST /api/v1
                                   v
                    +-----------------------------+
                    | FastAPI backend             |
                    | http://localhost:8000       |
                    +---+-------------+-------+---+
                        |             |       |
        document files  |             |       | cache / memory
                        v             v       v
              +---------+--+    +-----+--+  +-+------+
              | MongoDB    |    | Neo4j  |  | Redis  |
              | metadata,  |    | graph  |  | cache  |
              | chunks     |    | data   |  |        |
              +------------+    +--------+  +--------+
                        |
                        v
              +-----------------------------+
              | AI services                 |
              | embeddings, extraction,     |
              | citations, Gemini chat      |
              +-----------------------------+
```

### Backend Flow

- `apps/api/app/api/v1/routes/` exposes versioned FastAPI routes.
- `apps/api/app/domain/` defines Pydantic request and response schemas.
- `apps/api/app/services/` contains application services for search, chat, dashboards, graph explorer, assets, ingestion support, and reset logic.
- `apps/api/app/db/` contains MongoDB, Neo4j, and Redis adapters.
- `apps/api/app/agents/` and `apps/api/app/workflows/` contain ingestion and workflow orchestration.

### Frontend Flow

- `apps/web/src/app/App.tsx` defines the main route tree.
- Feature modules live under `apps/web/src/features/`.
- Shared layout and reusable UI helpers live under `apps/web/src/components/`.
- API base URL configuration lives in `apps/web/src/lib/api-client.ts`.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, TypeScript, Vite 6, React Router 7, TanStack Query 5, Zustand, Tailwind CSS, Framer Motion |
| UI / Visualization | Radix UI primitives, Lucide icons, React Flow (`@xyflow/react`), React Markdown, Highlight.js |
| Backend | Python, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings |
| AI / Retrieval | Google Generative AI client, LangGraph, LangChain Core, embedding/entity/citation service modules |
| Data | MongoDB, Neo4j 5 Community with APOC, Redis |
| Document Processing | `pdfplumber`, `PyPDF2`, `python-multipart` |
| Testing / Quality | Pytest, pytest-asyncio, Ruff, MyPy, ESLint, TypeScript compiler |
| DevOps | Docker Compose, custom API and web Dockerfiles |

## Project Structure

```text
PlantMind/
+-- apps/
|   +-- api/
|   |   +-- app/
|   |   |   +-- api/v1/routes/       # FastAPI route modules
|   |   |   +-- agents/              # ingestion and intelligence agents
|   |   |   +-- core/                # config and logging
|   |   |   +-- db/                  # MongoDB, Neo4j, Redis adapters
|   |   |   +-- domain/              # Pydantic schemas and domain types
|   |   |   +-- services/            # business and AI services
|   |   |   +-- workflows/           # ingestion workflow orchestration
|   |   +-- data/documents/          # local sample/runtime document files
|   |   +-- tests/                   # backend test suite
|   |   +-- requirements*.txt
|   +-- web/
|       +-- src/
|       |   +-- app/                 # React app shell and routes
|       |   +-- components/          # layout, shared, dashboard, UI components
|       |   +-- features/            # documents, graph, copilot, dashboards, settings
|       |   +-- lib/                 # API client and query helpers
|       |   +-- stores/              # Zustand app store
|       +-- package.json
+-- docs/architecture/               # architecture documentation
+-- infra/
|   +-- docker/                      # API and web Dockerfiles
|   +-- mongo/                       # MongoDB initialization notes
|   +-- neo4j/                       # Neo4j import area and notes
|   +-- redis/                       # Redis notes
+-- scripts/                         # developer automation notes
+-- docker-compose.yml
+-- pytest.ini
+-- README.md
```

## Installation and Setup

### Prerequisites

| Tool | Purpose |
| --- | --- |
| Docker + Docker Compose | Run the complete local stack |
| Node.js + npm | Run the frontend outside Docker |
| Python 3.12 recommended | Run the backend outside Docker |

### Option 1: Docker Compose

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Services started by Compose:

| Service | URL / Port |
| --- | --- |
| Web app | `http://localhost:5173` |
| API | `http://localhost:8000` |
| API docs | `http://localhost:8000/docs` |
| MongoDB | `localhost:27017` |
| Neo4j Browser | `http://localhost:7474` |
| Neo4j Bolt | `localhost:7687` |
| Redis | `localhost:6379` |

### Option 2: Local Backend + Frontend

Start MongoDB, Neo4j, and Redis first. The easiest local path is to use Docker Compose for dependencies:

```bash
docker compose up -d mongodb neo4j redis
```

Then run the backend:

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In a second terminal, run the frontend:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:5173`.

> Note: `apps/api/requirements.txt` delegates to `requirements.dev.txt`, which includes production requirements plus test and lint tooling.

## Environment Variables

The backend loads `.env` from the repository root through `apps/api/app/core/config.py`. Docker Compose also passes several service URLs automatically.

| Variable | Default | Used by | Purpose |
| --- | --- | --- | --- |
| `ENVIRONMENT` | `local` | API | Runtime environment label |
| `LOG_LEVEL` | `INFO` | API | Logging verbosity |
| `CORS_ORIGINS` | `http://localhost:5173` | API | Allowed frontend origins |
| `MONGODB_URI` | `mongodb://mongodb:27017/plantmind` | API | MongoDB connection string |
| `MONGODB_DATABASE` | `plantmind` | API | MongoDB database name |
| `MONGODB_VECTOR_INDEX` | `plantmind_vector_index` | API | MongoDB vector index name |
| `NEO4J_URI` | `bolt://neo4j:7687` | API | Neo4j Bolt URI |
| `NEO4J_USERNAME` | `neo4j` | API | Neo4j username |
| `NEO4J_PASSWORD` | `plantmind-local-password` | API | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | API | Neo4j database |
| `REDIS_URL` | `redis://redis:6379/0` | API | Redis connection URL |
| `GEMINI_API_KEY` | empty | API | Optional Gemini API key for model-backed copilot responses |
| `GEMINI_MODEL` | `gemini-2.5-pro` | API | Gemini model name |
| `SENTENCE_TRANSFORMER_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | API | Embedding model setting |
| `SPACY_MODEL` | `en_core_web_sm` | API | Entity extraction model setting |
| `DOCUMENT_STORAGE_ROOT` | `/data/documents` | API | Uploaded document storage path |
| `MAX_UPLOAD_MB` | `100` | API | PDF upload size limit |
| `SCANNED_TEXT_THRESHOLD` | `250` | API | Threshold for scanned-text handling |
| `GRAPH_CACHE_TTL_SECONDS` | `60` | API | Graph cache TTL |
| `SEARCH_CACHE_TTL_SECONDS` | `60` | API | Search cache TTL |
| `HYBRID_SEARCH_TOP_K` | `8` | API | Default search result count |
| `DIGITAL_TWIN_CACHE_TTL_SECONDS` | `300` | API | Asset digital twin cache TTL |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Web | Frontend API base URL |

Example `.env` for Docker Compose:

```bash
ENVIRONMENT=local
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
GEMINI_API_KEY=
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

For local non-Docker backend development, point service URLs at localhost:

```bash
MONGODB_URI=mongodb://localhost:27017/plantmind
NEO4J_URI=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0
DOCUMENT_STORAGE_ROOT=./data/documents
```

## How to Run

### Full Stack

```bash
docker compose up --build
```

### Backend Only

```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Only

```bash
cd apps/web
npm run dev
```

### Backend Tests

```bash
cd apps/api
pytest
```

### Frontend Build

```bash
cd apps/web
npm run build
```

### Frontend Lint

```bash
cd apps/web
npm run lint
```

## API Overview

Base URL:

```text
http://localhost:8000/api/v1
```

Interactive docs:

```text
http://localhost:8000/docs
```

### Major Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/auth/health` | Authentication module health check |
| `GET` | `/documents/health` | Document module health check |
| `GET` | `/documents` | List uploaded/processed documents |
| `POST` | `/documents/upload` | Upload one or more PDF files |
| `POST` | `/search/query` | Run hybrid evidence search with graph context |
| `GET` | `/chat/health` | Chat module health check |
| `POST` | `/chat` | Ask the retrieval-grounded copilot |
| `GET` | `/graph/health` | Graph module health check |
| `GET` | `/graph/overview` | Get graph node and relationship counts |
| `GET` | `/graph/search` | Search graph nodes |
| `GET` | `/graph/subgraph/{node_id}` | Load a bounded graph neighborhood |
| `GET` | `/graph/equipment/{equipment_id}` | Load graph context for equipment |
| `GET` | `/graph/analytics` | Load graph analytics summaries |
| `GET` | `/assets/{asset_id}/digital-twin` | Load asset digital twin data |
| `GET` | `/dashboard` | Load main dashboard data |
| `GET` | `/risk/health` | Risk module health check |
| `GET` | `/risk/dashboard` | Load risk dashboard data |
| `GET` | `/compliance/health` | Compliance module health check |
| `GET` | `/compliance/dashboard` | Load compliance dashboard data |
| `GET` | `/alerts/health` | Alerts module health check |
| `GET` | `/alerts/dashboard` | Load alerts dashboard data |
| `GET` | `/analytics/dashboard` | Load executive analytics data |
| `DELETE` | `/admin/factory-reset` | Clear runtime demo data |

### Example Requests

Upload PDFs:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "files=@./sample-inspection.pdf"
```

Run hybrid search:

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"pressure anomaly on P204\",\"top_k\":5}"
```

Ask the copilot:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"demo-session\",\"message\":\"What evidence explains the pressure anomaly?\"}"
```

Factory reset:

```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/factory-reset"
```

## Screenshots

Add screenshots to `docs/screenshots/` and update the paths below.

| Screen | Placeholder | Caption |
| --- | --- | --- |
| Dashboard | `docs/screenshots/dashboard.png` | PlantMind operational landing dashboard |
| Document Upload | `docs/screenshots/document-upload.png` | Multi-PDF upload queue with ingestion stages |
| Hybrid Search | `docs/screenshots/search-results.png` | Evidence retrieval with confidence and graph context |
| Knowledge Graph | `docs/screenshots/knowledge-graph.png` | React Flow graph explorer with node drawer and analytics |
| AI Copilot | `docs/screenshots/copilot.png` | Retrieval-grounded copilot answer with citations |
| Analytics | `docs/screenshots/analytics.png` | Executive analytics workspace |
| Factory Reset | `docs/screenshots/factory-reset.png` | Guarded reset dialog in Settings |

## Demo Workflow

Use this path for a hackathon judging demo:

1. **Upload**: Open `/documents`, drag in one or more PDF files, and watch the queue move through upload, extraction, chunking, entity extraction, graph, embeddings, risk, and digital twin stages.
2. **Search**: Call `/api/v1/search/query` or use app flows that depend on search to retrieve evidence and graph context.
3. **Graph**: Open `/graph`, search for an equipment or document node, inspect the generated relationship map, expand nodes, and review graph analytics.
4. **Copilot**: Open `/copilot`, ask a plant question, and review the grounded answer, confidence, citations, related assets, and follow-up prompts.
5. **Analytics**: Open `/analytics`, `/risk`, `/compliance`, and `/alerts` to review operational dashboard views.
6. **Factory Reset**: Open `/settings`, choose **Factory Reset**, type `FACTORY RESET`, and clear runtime data for the next demo run.

## Factory Reset

PlantMind includes a demo-friendly reset workflow implemented in both the frontend Settings page and backend admin route.

```text
DELETE /api/v1/admin/factory-reset
```

The reset service clears:

- Runtime MongoDB collections such as documents, chunks, embeddings, incidents, asset events, analytics, risk outputs, compliance evidence, and alerts.
- Neo4j graph nodes and relationships.
- Redis cache keys matching search, chat, conversation, dashboard, graph, embedding, and digital twin cache patterns.
- Uploaded files and temporary processing artifacts under `DOCUMENT_STORAGE_ROOT`.

The reset service refuses to run against protected source-tree paths such as the repository root, `apps`, `infra`, `scripts`, `docs`, `.git`, or `.github`.

## Future Improvements

These items are future work, not current capabilities:

- User authentication and role-based authorization beyond the current health route scaffold.
- Background job queue for long-running ingestion instead of request-bound processing.
- Production-grade OCR workflow for scanned PDFs.
- Richer vector database/index management and operational observability.
- Human review workflows for extracted entities and graph relationships.
- CI pipeline, deployment manifests, and cloud environment templates.
- Persisted screenshot assets and a polished public demo video.
- Expanded model provider configuration and evaluation harnesses for copilot answers.

## Team / Author

| Role | Name |
| --- | --- |
| Creator / Developer | Dhushanth S |

## License

No license file is currently included in this repository. Add a `LICENSE` file before distributing, publishing, or reusing the project outside the current workspace.
