# Backend Module Architecture

## Layers

1. `api/v1/routes`: HTTP endpoints only. No business logic belongs here.
2. `domain`: use cases, Pydantic contracts, repository interfaces, and domain errors.
3. `services/ai`: AI capabilities wrapped behind stable service interfaces.
4. `agents`: LangGraph agent nodes, prompt templates, and tool contracts.
5. `workflows`: LangGraph state machines that compose agent nodes.
6. `db`: MongoDB, Neo4j, and Redis adapters.
7. `core`: configuration, security, logging, lifecycle, dependency injection.

## API Domains

| API | Responsibility | Future endpoints |
| --- | --- | --- |
| Authentication | identity, roles, tenants, session policy | login, refresh, SSO, RBAC |
| Document APIs | upload, parse status, document catalog | multipart upload, chunk review, reprocess |
| Chat APIs | copilot conversations with citations | streaming chat, feedback, conversation history |
| Graph APIs | graph search and traversal | neighbors, path finding, graph snapshots |
| Risk APIs | risk scoring and scenario analysis | risk register, score explanations, mitigations |
| Compliance APIs | controls and evidence | obligation mapping, evidence packs, audit export |
| Alert APIs | alert feed and triage | acknowledgements, escalation, subscriptions |

