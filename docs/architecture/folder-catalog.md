# Folder Catalog

This catalog explains every tracked folder in the initial PlantMind scaffold.

| Folder | Purpose | Responsibilities | Future services |
| --- | --- | --- | --- |
| `apps` | Product applications | Hold deployable services in one monorepo | additional workers, admin app |
| `apps/api` | Backend service root | FastAPI app, requirements, tests | API workers, background queues |
| `apps/api/app` | Python application package | Compose routes, domain, agents, workflows, services, data access | app lifecycle and dependency graph |
| `apps/api/app/api` | HTTP API package | Versioned API organization | API gateways, generated OpenAPI clients |
| `apps/api/app/api/v1` | API version boundary | Stable v1 router assembly | v2 migration path |
| `apps/api/app/api/v1/routes` | FastAPI route modules | HTTP request/response contracts | auth, documents, chat, graph, risk, compliance, alerts endpoints |
| `apps/api/app/core` | Shared backend foundation | settings, logging, security, dependency wiring | telemetry, feature flags, tenant context |
| `apps/api/app/db` | Database adapter root | Persistence abstractions and connection lifecycle | repositories, migrations, health checks |
| `apps/api/app/db/mongodb` | MongoDB adapter | document, chunk, vector metadata, conversation persistence | Atlas vector indexes, bulk ingestion repositories |
| `apps/api/app/db/neo4j` | Neo4j adapter | knowledge graph writes, reads, constraints, Cypher utilities | graph migrations, traversal services |
| `apps/api/app/db/redis` | Redis adapter | cache, sessions, workflow state, rate limits | queue locks, streaming buffers |
| `apps/api/app/domain` | Domain model root | Pydantic schemas, service contracts, business use-case boundaries | shared domain events |
| `apps/api/app/domain/auth` | Authentication domain | identity, RBAC, tenant membership contracts | SSO, API keys, policy engine |
| `apps/api/app/domain/documents` | Document domain | upload metadata, parsing states, chunk models | review queues, reprocessing policies |
| `apps/api/app/domain/chat` | Chat domain | conversations, messages, citations, feedback contracts | streaming chat, answer evaluation |
| `apps/api/app/domain/graph` | Graph domain | graph query contracts and DTOs | path search, graph snapshots |
| `apps/api/app/domain/risk` | Risk domain | risk scenario and scoring contracts | risk register, mitigations, bowtie analysis |
| `apps/api/app/domain/compliance` | Compliance domain | standards, controls, evidence contracts | audit packs, gap analysis |
| `apps/api/app/domain/alerts` | Alerts domain | alert lifecycle and triage contracts | escalation, subscriptions, alert routing |
| `apps/api/app/services` | Application service root | External capability wrappers | AI, storage, notifications |
| `apps/api/app/services/ai` | AI service boundary | Model-agnostic AI interfaces | model registry, prompt evaluation |
| `apps/api/app/services/ai/entity_extraction` | Entity extraction | spaCy and LLM extraction contracts | industrial NER, unit normalization |
| `apps/api/app/services/ai/embedding` | Embeddings | sentence transformer interface | vector batching, reranking |
| `apps/api/app/services/ai/citation` | Citations | source span and evidence contracts | citation verification, source rendering |
| `apps/api/app/services/ai/pattern_detection` | Pattern detection | recurring incident and signal analysis | clustering, trend discovery |
| `apps/api/app/services/ai/risk_scoring` | Risk scoring | risk score and explanation contracts | calibrated scoring, confidence models |
| `apps/api/app/agents` | Agent root | LangGraph node ownership | shared agent tools and policies |
| `apps/api/app/agents/ingestion` | Ingestion agent | document intake orchestration boundary | parser selection, OCR routing |
| `apps/api/app/agents/graph_builder` | Graph builder agent | entity-to-graph orchestration boundary | entity resolution, relationship confidence |
| `apps/api/app/agents/retriever` | Retriever agent | context retrieval boundary | hybrid vector and graph retrieval |
| `apps/api/app/agents/synthesis` | Synthesis agent | answer synthesis boundary | grounded response generation |
| `apps/api/app/agents/citation` | Citation agent | evidence validation boundary | citation filtering, source ranking |
| `apps/api/app/agents/pattern` | Pattern agent | operational pattern analysis boundary | incident similarity, anomaly surfacing |
| `apps/api/app/agents/risk` | Risk agent | risk reasoning boundary | mitigation proposals, score explanations |
| `apps/api/app/agents/compliance` | Compliance agent | requirement mapping boundary | control mapping, audit summaries |
| `apps/api/app/workflows` | Workflow root | LangGraph state machines | ingestion, copilot, risk workflows |
| `apps/api/tests` | Backend tests | unit, integration, contract, workflow tests | database fixtures and agent regression suites |
| `apps/web` | Frontend service root | Vite React app and frontend dependencies | generated API clients, frontend test harness |
| `apps/web/src` | Frontend source root | app shell, components, features, stores, utilities | route modules and shared design system |
| `apps/web/src/app` | App shell | root composition and providers | routing, authentication guards, theme |
| `apps/web/src/components` | Shared component root | cross-feature UI and layout building blocks | reusable visualization primitives |
| `apps/web/src/components/layout` | Layout components | page shell and navigation | workspace nav, sidebars, breadcrumbs |
| `apps/web/src/components/ui` | ShadCN UI primitives | accessible visual primitives | buttons, dialogs, tables, toasts |
| `apps/web/src/features` | Feature module root | independent UI modules | colocated hooks, types, API clients |
| `apps/web/src/features/dashboard` | Dashboard | system overview and KPIs | ingestion status, risk summary |
| `apps/web/src/features/documents` | Document Upload | upload and document registry UI | parser status, review queue |
| `apps/web/src/features/graph` | Knowledge Graph Explorer | graph visualization UI | React Flow canvas, entity panel |
| `apps/web/src/features/digital-twin` | Asset Digital Twin | asset-centric UI | equipment profiles, linked incidents |
| `apps/web/src/features/copilot` | AI Copilot Chat | chat and citation UI | streaming messages, source drawer |
| `apps/web/src/features/risk` | Risk Intelligence Center | risk analysis UI | matrix, scenarios, mitigations |
| `apps/web/src/features/compliance` | Compliance Center | compliance evidence UI | control mapping, audit readiness |
| `apps/web/src/features/alerts` | Alerts Center | alert feed and triage UI | routing, acknowledgement, escalation |
| `apps/web/src/lib` | Frontend utilities | API client, constants, shared helpers | generated SDK, telemetry client |
| `apps/web/src/stores` | Client state | Zustand stores for cross-feature state | session, graph viewport, chat state |
| `docs` | Documentation root | architecture and future ADRs | runbooks, threat models |
| `docs/architecture` | Architecture docs | module, data, workflow, Docker design | ADRs and diagrams |
| `infra` | Infrastructure root | container, database, and deployment support | Kubernetes, Terraform, CI infrastructure |
| `infra/docker` | Docker build assets | Dockerfiles and container build policy | production images, health checks |
| `infra/mongo` | MongoDB infra | indexes and seed scripts | Atlas vector index definitions |
| `infra/neo4j` | Neo4j infra | constraints, indexes, import assets | graph migrations and APOC scripts |
| `infra/redis` | Redis infra | Redis configuration | eviction, queue, lock settings |
| `scripts` | Automation root | developer and CI helper scripts | setup, lint, migration commands |

