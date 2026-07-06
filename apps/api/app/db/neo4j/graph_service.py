import logging

from app.core.config import settings
from app.db.neo4j.client import neo4j_database
from app.domain.documents.schemas import EntityExtractionResult, GraphBuildResult

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    async def build_document_graph(
        self,
        document_id: str,
        filename: str,
        entities: EntityExtractionResult,
    ) -> GraphBuildResult:
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            result = await session.execute_write(self._write_graph, document_id, filename, entities)

        logger.info(
            "knowledge_graph_built",
            extra={
                "document_id": document_id,
                "nodes": result.nodes_created,
                "edges": result.edges_created,
            },
        )
        return result

    @staticmethod
    async def _write_graph(tx, document_id: str, filename: str, entities: EntityExtractionResult) -> GraphBuildResult:
        nodes_created = 0
        edges_created = 0

        result = await tx.run(
            """
            MERGE (d:Document {document_id: $document_id})
            SET d.filename = $filename,
                d.updated_at = datetime()
            """,
            document_id=document_id,
            filename=filename,
        )
        summary = await result.consume()
        nodes_created += summary.counters.nodes_created
        edges_created += summary.counters.relationships_created

        for equipment in entities.equipment:
            result = await tx.run(
                """
                MERGE (e:Equipment {equipment_id: $id})
                SET e.name = coalesce($name, $id),
                    e.type = $type,
                    e.updated_at = datetime()
                WITH e
                MATCH (d:Document {document_id: $document_id})
                MERGE (e)-[:MENTIONED_IN]->(d)
                """,
                id=equipment.id,
                name=equipment.name,
                type=equipment.type,
                document_id=document_id,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created
            edges_created += summary.counters.relationships_created

        for person in entities.personnel:
            result = await tx.run(
                """
                MERGE (p:Person {person_id: $id})
                SET p.name = coalesce($name, $id),
                    p.role = $type,
                    p.updated_at = datetime()
                WITH p
                MATCH (d:Document {document_id: $document_id})
                MERGE (p)-[:MENTIONED_IN]->(d)
                """,
                id=person.id,
                name=person.name,
                type=person.type,
                document_id=document_id,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created
            edges_created += summary.counters.relationships_created

        for procedure in entities.procedures:
            result = await tx.run(
                """
                MERGE (pr:Procedure {procedure_id: $id})
                SET pr.name = coalesce($name, $id),
                    pr.type = $type,
                    pr.updated_at = datetime()
                WITH pr
                MATCH (d:Document {document_id: $document_id})
                MERGE (pr)-[:MENTIONED_IN]->(d)
                MERGE (d)-[:REFERENCES]->(pr)
                """,
                id=procedure.id,
                name=procedure.name,
                type=procedure.type,
                document_id=document_id,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created
            edges_created += summary.counters.relationships_created

        for incident in entities.incidents:
            result = await tx.run(
                """
                MERGE (i:Incident {incident_id: $id})
                SET i.name = coalesce($name, $id),
                    i.type = $type,
                    i.updated_at = datetime()
                WITH i
                MATCH (d:Document {document_id: $document_id})
                MERGE (i)-[:MENTIONED_IN]->(d)
                MERGE (d)-[:REFERENCES]->(i)
                """,
                id=incident.id,
                name=incident.name,
                type=incident.type,
                document_id=document_id,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created
            edges_created += summary.counters.relationships_created

        for failure_mode in entities.failure_modes:
            result = await tx.run(
                """
                MERGE (fm:FailureMode {failure_mode_id: $id})
                SET fm.name = coalesce($name, $id),
                    fm.type = $type,
                    fm.updated_at = datetime()
                WITH fm
                MATCH (d:Document {document_id: $document_id})
                MERGE (fm)-[:MENTIONED_IN]->(d)
                """,
                id=failure_mode.id,
                name=failure_mode.name,
                type=failure_mode.type,
                document_id=document_id,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created
            edges_created += summary.counters.relationships_created

        result = await tx.run(
            """
            MATCH (e:Equipment)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MATCH (pr:Procedure)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MERGE (e)-[:RELATED_TO {document_id: $document_id}]->(pr)
            """,
            document_id=document_id,
        )
        summary = await result.consume()
        nodes_created += summary.counters.nodes_created
        edges_created += summary.counters.relationships_created

        result = await tx.run(
            """
            MATCH (p:Person)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MATCH (e:Equipment)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MERGE (p)-[:ASSIGNED_TO {document_id: $document_id}]->(e)
            """,
            document_id=document_id,
        )
        summary = await result.consume()
        nodes_created += summary.counters.nodes_created
        edges_created += summary.counters.relationships_created

        result = await tx.run(
            """
            MATCH (fm:FailureMode)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MATCH (e:Equipment)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MERGE (fm)-[:RELATED_TO {document_id: $document_id}]->(e)
            """,
            document_id=document_id,
        )
        summary = await result.consume()
        nodes_created += summary.counters.nodes_created
        edges_created += summary.counters.relationships_created

        result = await tx.run(
            """
            MATCH (i:Incident)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MATCH (e:Equipment)-[:MENTIONED_IN]->(:Document {document_id: $document_id})
            MERGE (i)-[:CAUSED_BY {document_id: $document_id}]->(e)
            """,
            document_id=document_id,
        )
        summary = await result.consume()
        nodes_created += summary.counters.nodes_created
        edges_created += summary.counters.relationships_created

        return GraphBuildResult(nodes_created=nodes_created, edges_created=edges_created)
