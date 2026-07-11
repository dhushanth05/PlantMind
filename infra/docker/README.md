# Docker Infrastructure

Purpose: container build definitions for PlantMind services.

Responsibilities: local development Dockerfiles and future production image hardening.

Future services: multi-stage production builds, health checks, vulnerability scanning, and runtime user policies.

API image notes:

- `requirements.prod.txt` contains the FastAPI, MongoDB, Neo4j, Redis, PDF, and Gemini runtime dependencies.
- `requirements.dev.txt` adds test and lint tooling for local development.
- `requirements.ml.txt` contains heavy optional ML packages (`sentence-transformers`, spaCy) and is intentionally not installed during Docker build.
- The API Dockerfile copies requirement files before source files so dependency layers are cached between source-only changes.
- Optional ML dependencies are installed lazily at runtime on the first embedding/entity-extraction path that needs them.
