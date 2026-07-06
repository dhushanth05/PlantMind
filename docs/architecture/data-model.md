# Data Architecture

## MongoDB Collections

| Collection | Purpose | Example fields |
| --- | --- | --- |
| `documents` | source document registry | `_id`, `tenant_id`, `title`, `type`, `asset_ids`, `status`, `storage_uri`, `created_at` |
| `document_chunks` | chunked text and vector metadata | `_id`, `document_id`, `chunk_index`, `text`, `embedding`, `page`, `section`, `source_span` |
| `conversations` | copilot sessions | `_id`, `tenant_id`, `user_id`, `title`, `created_at`, `updated_at` |
| `messages` | chat turns | `_id`, `conversation_id`, `role`, `content`, `citations`, `created_at` |
| `incidents` | historical incidents and lessons learned | `_id`, `asset_id`, `summary`, `causes`, `consequences`, `lesson_ids` |
| `risk_assessments` | risk scoring outputs | `_id`, `asset_id`, `scenario`, `likelihood`, `severity`, `score`, `evidence` |
| `compliance_evidence` | requirement-to-source mappings | `_id`, `standard`, `control_id`, `document_id`, `citations`, `status` |
| `alerts` | user-facing alert feed | `_id`, `severity`, `type`, `entity_ref`, `status`, `created_at` |
| `audit_events` | security and change audit trail | `_id`, `actor_id`, `action`, `resource`, `metadata`, `created_at` |

## Neo4j Nodes

| Node | Purpose | Key properties |
| --- | --- | --- |
| `Asset` | physical asset or equipment | `asset_id`, `name`, `site`, `criticality` |
| `System` | industrial system boundary | `system_id`, `name`, `site` |
| `Document` | source document reference | `document_id`, `title`, `type` |
| `Chunk` | cited document segment | `chunk_id`, `page`, `section` |
| `Entity` | extracted technical entity | `entity_id`, `name`, `entity_type` |
| `Incident` | historical incident | `incident_id`, `date`, `severity` |
| `Hazard` | identified hazard | `hazard_id`, `name`, `category` |
| `Control` | mitigation or safeguard | `control_id`, `name`, `effectiveness` |
| `Requirement` | compliance obligation | `requirement_id`, `standard`, `clause` |
| `LessonLearned` | reusable lesson | `lesson_id`, `summary`, `confidence` |

## Neo4j Relationships

| Relationship | From | To | Purpose |
| --- | --- | --- | --- |
| `PART_OF` | `Asset` | `System` | asset hierarchy |
| `MENTIONED_IN` | `Entity` | `Chunk` | source traceability |
| `HAS_CHUNK` | `Document` | `Chunk` | document structure |
| `RELATED_TO` | `Entity` | `Entity` | extracted semantic link |
| `FAILED_IN` | `Asset` | `Incident` | incident association |
| `CAUSED_BY` | `Incident` | `Hazard` | causal modeling |
| `MITIGATED_BY` | `Hazard` | `Control` | safeguard mapping |
| `SATISFIES` | `Control` | `Requirement` | compliance evidence |
| `PRODUCED_LESSON` | `Incident` | `LessonLearned` | lessons learned |
| `APPLIES_TO` | `LessonLearned` | `Asset` | reusable operational knowledge |

