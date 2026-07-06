# Frontend Module Architecture

## Shell

`src/app` owns top-level providers, routing, theme setup, and application layout composition.

## Shared UI

`src/components/ui` is reserved for ShadCN UI primitives and local variants.
`src/components/layout` contains navigation, page chrome, sidebars, and cross-module layout.

## Feature Modules

Each feature folder should own its pages, components, hooks, types, API calls, and local tests.

| Feature | Responsibility | Future services |
| --- | --- | --- |
| dashboard | operational overview | risk KPIs, ingestion status, alert summary |
| documents | document upload and registry | upload queue, parser status, metadata review |
| graph | knowledge graph exploration | React Flow canvas, entity detail panel, path explorer |
| digital-twin | asset-centered intelligence | equipment profile, relationships, operating context |
| copilot | conversational AI | streaming chat, citations, feedback, source drawer |
| risk | risk intelligence center | risk matrix, trend analysis, mitigations |
| compliance | compliance center | controls, evidence, audit readiness |
| alerts | alerts center | alert triage, severity filters, subscriptions |

## State

Zustand stores belong in `src/stores` for cross-feature client state. Server state should later be isolated through a query client or generated API client.

