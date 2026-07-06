# PlantMind Folder Structure

```text
PlantMind/
  apps/
    api/
      app/
        api/v1/routes/
        agents/
        core/
        db/
        domain/
        services/ai/
        workflows/
      tests/
      requirements.txt
    web/
      src/
        app/
        components/
        features/
        lib/
        stores/
      package.json
  docs/
    architecture/
  infra/
    docker/
    mongo/
    neo4j/
    redis/
  scripts/
  docker-compose.yml
  .env.example
  README.md
```

## Folder Responsibilities

| Folder | Purpose | Responsibilities | Future services |
| --- | --- | --- | --- |
| `apps/api/app/api/v1/routes` | FastAPI route layer | HTTP contracts, request validation, response shaping | REST endpoints, streaming chat, upload callbacks |
| `apps/api/app/domain` | Domain boundary | Pydantic schemas, domain services, repository interfaces | auth, documents, chat, graph, risk, compliance, alerts |
| `apps/api/app/services/ai` | AI service adapters | Model clients, extraction, embeddings, citations, scoring | Gemini, spaCy, sentence transformers, rerankers |
| `apps/api/app/agents` | LangGraph node ownership | Agent prompts, node functions, agent-specific policies | ingestion, graph builder, retriever, synthesis, citation, pattern, risk, compliance |
| `apps/api/app/workflows` | LangGraph orchestration | Workflow state, graph assembly, conditional routing | ingestion workflow, RAG workflow, incident analysis workflow |
| `apps/api/app/db` | Persistence adapters | Connection lifecycle, repositories, migrations | MongoDB, Neo4j, Redis, vector index integration |
| `apps/api/app/core` | Cross-cutting backend | settings, security, logging, dependency injection | auth middleware, telemetry, feature flags |
| `apps/api/tests` | Backend quality gate | unit, integration, contract, workflow tests | database fixtures, agent regression tests |
| `apps/web/src/app` | Frontend shell | root app composition, routing, providers | route guards, layouts, theme providers |
| `apps/web/src/components/layout` | Shared layout | navigation, header, sidebars, empty states | enterprise shell, breadcrumbs, command palette |
| `apps/web/src/components/ui` | ShadCN primitives | reusable UI components | buttons, dialogs, tables, forms, toasts |
| `apps/web/src/features/dashboard` | Dashboard module | KPIs, activity, operational summary | executive overview, risk heatmaps |
| `apps/web/src/features/documents` | Document upload module | upload flows, document registry | parser status, review queue |
| `apps/web/src/features/graph` | Knowledge graph explorer | React Flow graph canvas | entity search, graph filters, lineage view |
| `apps/web/src/features/digital-twin` | Asset digital twin | asset state, linked docs, linked incidents | equipment profile, sensor overlays |
| `apps/web/src/features/copilot` | AI copilot chat | chat UI, citations, conversation history | streaming answers, source drawer |
| `apps/web/src/features/risk` | Risk intelligence center | risk scenarios and scoring views | bowtie analysis, mitigations, risk trends |
| `apps/web/src/features/compliance` | Compliance center | controls, obligations, evidence | audit packs, gap analysis |
| `apps/web/src/features/alerts` | Alerts center | alert feed and triage | subscriptions, severity rules |
| `apps/web/src/lib` | Frontend utilities | API client, formatting, constants | generated API client, telemetry |
| `apps/web/src/stores` | Zustand state | client state stores | session, graph viewport, chat state |
| `infra/docker` | Container build files | API and web images | production Dockerfiles, health checks |
| `infra/mongo` | MongoDB infra | seed scripts, indexes | Atlas vector search indexes |
| `infra/neo4j` | Neo4j infra | constraints, indexes, imports | APOC scripts, graph migrations |
| `infra/redis` | Redis infra | cache config | queue config, eviction policies |
| `docs/architecture` | Architecture record | design docs and diagrams | ADRs, threat model, runbooks |
| `scripts` | Developer automation | setup, lint, migrations | CI helpers, local seed commands |

