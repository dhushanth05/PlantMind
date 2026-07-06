# Docker Architecture

## Services

| Service | Image | Responsibility |
| --- | --- | --- |
| `web` | Node 22 Alpine | Vite React frontend |
| `api` | Python 3.12 slim | FastAPI backend, LangGraph orchestration, AI service interfaces |
| `mongodb` | MongoDB 7 | document metadata, chunks, vector metadata, conversations |
| `neo4j` | Neo4j 5 community | knowledge graph and relationship traversal |
| `redis` | Redis 7 Alpine | cache, sessions, workflow state, rate limits |

## Development Network

The compose file creates an internal service network. The frontend calls the API through `VITE_API_BASE_URL`, the API reaches databases by service name, and local ports expose web, API, MongoDB, Neo4j Browser, Bolt, and Redis.

