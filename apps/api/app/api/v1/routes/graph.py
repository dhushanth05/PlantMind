from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domain.graph.schemas import AssetContext, GraphAnalytics, GraphOverview, GraphSearchResult, GraphSubgraph
from app.services.graph_explorer_service import GraphExplorerService

router = APIRouter()


@router.get("/health")
async def graph_health() -> dict[str, str]:
    return {"module": "graph", "status": "ready"}


def get_graph_explorer_service() -> GraphExplorerService:
    return GraphExplorerService()


@router.get("/overview", response_model=GraphOverview)
async def graph_overview(
    service: Annotated[GraphExplorerService, Depends(get_graph_explorer_service)],
) -> GraphOverview:
    return await service.get_overview()


@router.get("/subgraph/{node_id}", response_model=GraphSubgraph)
async def graph_subgraph(
    node_id: str,
    service: Annotated[GraphExplorerService, Depends(get_graph_explorer_service)],
    depth: Annotated[int, Query(ge=1, le=2)] = 1,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> GraphSubgraph:
    try:
        return await service.get_subgraph(node_id=node_id, depth=depth, limit=limit)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/search", response_model=GraphSearchResult)
async def graph_search(
    service: Annotated[GraphExplorerService, Depends(get_graph_explorer_service)],
    q: Annotated[str, Query(min_length=1, max_length=200)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> GraphSearchResult:
    return await service.search_nodes(query=q, limit=limit, offset=offset)


@router.get("/equipment/{equipment_id}", response_model=AssetContext)
async def equipment_context(
    equipment_id: str,
    service: Annotated[GraphExplorerService, Depends(get_graph_explorer_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AssetContext:
    try:
        return await service.get_asset_context(equipment_id=equipment_id, limit=limit, offset=offset)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/analytics", response_model=GraphAnalytics)
async def graph_analytics(
    service: Annotated[GraphExplorerService, Depends(get_graph_explorer_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GraphAnalytics:
    return await service.get_analytics(limit=limit)
