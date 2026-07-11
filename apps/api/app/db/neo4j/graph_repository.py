from typing import Any

from app.core.config import settings
from app.db.neo4j.client import neo4j_database


SEARCH_LABELS = ["Equipment", "Person", "Procedure", "Incident", "Document", "FailureMode"]


class GraphRepository:
    async def ensure_indexes(self) -> None:
        statements = [
            "CREATE INDEX equipment_id_index IF NOT EXISTS FOR (n:Equipment) ON (n.equipment_id)",
            "CREATE INDEX equipment_name_index IF NOT EXISTS FOR (n:Equipment) ON (n.name)",
            "CREATE INDEX person_id_index IF NOT EXISTS FOR (n:Person) ON (n.person_id)",
            "CREATE INDEX person_name_index IF NOT EXISTS FOR (n:Person) ON (n.name)",
            "CREATE INDEX procedure_id_index IF NOT EXISTS FOR (n:Procedure) ON (n.procedure_id)",
            "CREATE INDEX procedure_name_index IF NOT EXISTS FOR (n:Procedure) ON (n.name)",
            "CREATE INDEX incident_id_index IF NOT EXISTS FOR (n:Incident) ON (n.incident_id)",
            "CREATE INDEX incident_name_index IF NOT EXISTS FOR (n:Incident) ON (n.name)",
            "CREATE INDEX document_id_index IF NOT EXISTS FOR (n:Document) ON (n.document_id)",
            "CREATE INDEX document_filename_index IF NOT EXISTS FOR (n:Document) ON (n.filename)",
            "CREATE INDEX failure_mode_id_index IF NOT EXISTS FOR (n:FailureMode) ON (n.failure_mode_id)",
            "CREATE INDEX failure_mode_name_index IF NOT EXISTS FOR (n:FailureMode) ON (n.name)",
        ]
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            for statement in statements:
                await session.run(statement)

    async def get_overview(self) -> dict[str, Any]:
        await self.ensure_indexes()
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            total_nodes = await (await session.run("MATCH (n) RETURN count(n) AS total")).single()
            total_relationships = await (await session.run("MATCH ()-[r]->() RETURN count(r) AS total")).single()
            node_types_result = await session.run(
                """
                MATCH (n)
                UNWIND labels(n) AS label
                RETURN label AS type, count(*) AS count
                ORDER BY count DESC, type ASC
                """
            )
            relationship_types_result = await session.run(
                """
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(*) AS count
                ORDER BY count DESC, type ASC
                """
            )
            return {
                "total_nodes": total_nodes["total"] if total_nodes else 0,
                "total_relationships": total_relationships["total"] if total_relationships else 0,
                "node_types": [record.data() async for record in node_types_result],
                "relationship_types": [record.data() async for record in relationship_types_result],
            }

    async def search_nodes(self, query: str, limit: int, offset: int) -> dict[str, Any]:
        await self.ensure_indexes()
        parameters = {"query": query.lower(), "labels": SEARCH_LABELS, "limit": limit, "offset": offset}
        match_query = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $labels)
          AND any(value IN [
            n.name,
            n.filename,
            n.equipment_id,
            n.person_id,
            n.procedure_id,
            n.incident_id,
            n.failure_mode_id,
            n.document_id
          ] WHERE value IS NOT NULL AND toLower(toString(value)) CONTAINS $query)
        WITH n
        ORDER BY coalesce(
          n.name,
          n.filename,
          n.equipment_id,
          n.person_id,
          n.procedure_id,
          n.incident_id,
          n.failure_mode_id,
          n.document_id
        )
        SKIP $offset
        LIMIT $limit
        RETURN collect(n {.*, id: elementId(n), labels: labels(n)}) AS nodes
        """
        count_query = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $labels)
          AND any(value IN [
            n.name,
            n.filename,
            n.equipment_id,
            n.person_id,
            n.procedure_id,
            n.incident_id,
            n.failure_mode_id,
            n.document_id
          ] WHERE value IS NOT NULL AND toLower(toString(value)) CONTAINS $query)
        RETURN count(n) AS total
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            records = await (await session.run(match_query, parameters)).single()
            total = await (await session.run(count_query, parameters)).single()
            return {
                "nodes": records["nodes"] if records else [],
                "total": total["total"] if total else 0,
                "limit": limit,
                "offset": offset,
            }

    async def get_subgraph(self, node_id: str, depth: int, limit: int) -> dict[str, Any]:
        await self.ensure_indexes()
        depth_range = "1..1" if depth == 1 else "1..2"
        query = f"""
        MATCH (center)
        WHERE elementId(center) = $node_id
           OR center.document_id = $node_id
           OR center.equipment_id = $node_id
           OR center.person_id = $node_id
           OR center.procedure_id = $node_id
           OR center.incident_id = $node_id
           OR center.failure_mode_id = $node_id
        OPTIONAL MATCH path = (center)-[*{depth_range}]-(neighbor)
        WITH center, [p IN collect(path) WHERE p IS NOT NULL][..$limit] AS paths
        UNWIND CASE WHEN paths = [] THEN [null] ELSE paths END AS node_path
        WITH center, paths, CASE WHEN node_path IS NULL THEN [center] ELSE nodes(node_path) END AS path_nodes
        UNWIND path_nodes AS n
        WITH center, paths, collect(DISTINCT n) AS nodes
        UNWIND CASE WHEN paths = [] THEN [null] ELSE paths END AS relationship_path
        WITH center,
             nodes,
             CASE WHEN relationship_path IS NULL THEN [] ELSE relationships(relationship_path) END AS path_relationships
        UNWIND CASE WHEN path_relationships = [] THEN [null] ELSE path_relationships END AS r
        WITH center, nodes, collect(DISTINCT r) AS relationships
        RETURN center {{.*, id: elementId(center), labels: labels(center)}} AS center_node,
               [n IN nodes | n {{.*, id: elementId(n), labels: labels(n)}}] AS nodes,
               [r IN relationships WHERE r IS NOT NULL | r {{.*, id: elementId(r), type: type(r), source: elementId(startNode(r)), target: elementId(endNode(r))}}] AS relationships
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            record = await (await session.run(query, node_id=node_id, limit=limit)).single()
            if record is None:
                center = await self._get_node_by_id(session, node_id)
                return {"center_node": center, "nodes": [center] if center else [], "relationships": []}
            return record.data()

    async def get_asset_context(self, equipment_id: str, limit: int, offset: int) -> dict[str, Any] | None:
        await self.ensure_indexes()
        query = """
        MATCH (e:Equipment {equipment_id: $equipment_id})
        OPTIONAL MATCH (e)-[document_rel:MENTIONED_IN]->(d:Document)
        OPTIONAL MATCH (p:Person)-[person_rel:ASSIGNED_TO]->(e)
        OPTIONAL MATCH (i:Incident)-[incident_rel:CAUSED_BY]->(e)
        OPTIONAL MATCH (e)-[procedure_rel:RELATED_TO]-(pr:Procedure)
        OPTIONAL MATCH (fm:FailureMode)-[failure_rel:RELATED_TO]->(e)
        WITH e,
             collect(DISTINCT d)[..$limit] AS documents,
             collect(DISTINCT p)[..$limit] AS personnel,
             collect(DISTINCT i)[..$limit] AS incidents,
             collect(DISTINCT pr)[..$limit] AS procedures,
             collect(DISTINCT fm)[..$limit] AS failure_modes,
             collect(DISTINCT document_rel)
             + collect(DISTINCT person_rel)
             + collect(DISTINCT incident_rel)
             + collect(DISTINCT procedure_rel)
             + collect(DISTINCT failure_rel) AS rels
        RETURN e {.*, id: elementId(e), labels: labels(e)} AS equipment,
               [n IN incidents[$offset..$end] WHERE n IS NOT NULL | n {.*, id: elementId(n), labels: labels(n)}] AS connected_incidents,
               [n IN documents[$offset..$end] WHERE n IS NOT NULL | n {.*, id: elementId(n), labels: labels(n)}] AS connected_documents,
               [n IN personnel[$offset..$end] WHERE n IS NOT NULL | n {.*, id: elementId(n), labels: labels(n)}] AS connected_personnel,
               [n IN failure_modes[$offset..$end] WHERE n IS NOT NULL | n {.*, id: elementId(n), labels: labels(n)}] AS failure_modes,
               [n IN procedures[$offset..$end] WHERE n IS NOT NULL | n {.*, id: elementId(n), labels: labels(n)}] AS related_procedures,
               [r IN rels WHERE r IS NOT NULL | r {.*, id: elementId(r), type: type(r), source: elementId(startNode(r)), target: elementId(endNode(r))}] AS relationships
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            record = await (
                await session.run(query, equipment_id=equipment_id, limit=limit, offset=offset, end=offset + limit)
            ).single()
            return record.data() if record else None

    async def most_connected_assets(self, limit: int) -> list[dict[str, Any]]:
        await self.ensure_indexes()
        query = """
        MATCH (e:Equipment)
        OPTIONAL MATCH (e)-[r]-()
        RETURN e.equipment_id AS equipment_id,
               coalesce(e.name, e.equipment_id) AS name,
               count(r) AS degree
        ORDER BY degree DESC, equipment_id ASC
        LIMIT $limit
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            result = await session.run(query, limit=limit)
            return [record.data() async for record in result]

    async def critical_equipment(self, limit: int) -> list[dict[str, Any]]:
        await self.ensure_indexes()
        query = """
        MATCH (e:Equipment)
        OPTIONAL MATCH (i:Incident)-[:CAUSED_BY]->(e)
        WITH e, count(DISTINCT i) AS incident_count
        OPTIONAL MATCH (fm:FailureMode)-[:RELATED_TO]->(e)
        WITH e, incident_count, count(DISTINCT fm) AS failure_mode_count
        OPTIONAL MATCH (e)-[r]-()
        WITH e, incident_count, failure_mode_count, count(r) AS degree
        RETURN e.equipment_id AS equipment_id,
               coalesce(e.name, e.equipment_id) AS name,
               incident_count,
               failure_mode_count,
               degree,
               incident_count * 5 + failure_mode_count * 3 + degree AS criticality_score
        ORDER BY criticality_score DESC, equipment_id ASC
        LIMIT $limit
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            result = await session.run(query, limit=limit)
            return [record.data() async for record in result]

    async def frequent_failure_modes(self, limit: int) -> list[dict[str, Any]]:
        await self.ensure_indexes()
        query = """
        MATCH (fm:FailureMode)
        OPTIONAL MATCH (fm)-[r]-()
        RETURN coalesce(fm.name, fm.failure_mode_id) AS failure_mode,
               count(r) AS mentions
        ORDER BY mentions DESC, failure_mode ASC
        LIMIT $limit
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            result = await session.run(query, limit=limit)
            return [record.data() async for record in result]

    @staticmethod
    async def _get_node_by_id(session, node_id: str) -> dict[str, Any] | None:
        record = await (
            await session.run(
                """
                MATCH (n)
                WHERE elementId(n) = $node_id
                   OR n.document_id = $node_id
                   OR n.equipment_id = $node_id
                   OR n.person_id = $node_id
                   OR n.procedure_id = $node_id
                   OR n.incident_id = $node_id
                   OR n.failure_mode_id = $node_id
                RETURN n {.*, id: elementId(n), labels: labels(n)} AS node
                """,
                node_id=node_id,
            )
        ).single()
        return record["node"] if record else None
