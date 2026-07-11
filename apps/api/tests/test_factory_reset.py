from pathlib import Path
import shutil
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes import admin as admin_route
from app.domain.admin.schemas import FactoryResetDeletedCounts, FactoryResetResponse
from app.main import app
from app.services.factory_reset_service import FactoryResetService


class FakeDeleteResult:
    def __init__(self, deleted_count: int) -> None:
        self.deleted_count = deleted_count


class FakeCollection:
    def __init__(self, count: int) -> None:
        self.count = count

    async def count_documents(self, _query: dict) -> int:
        return self.count

    async def delete_many(self, _query: dict) -> FakeDeleteResult:
        deleted = self.count
        self.count = 0
        return FakeDeleteResult(deleted)


class FakeMongoDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, FakeCollection] = {
            "documents": FakeCollection(2),
            "chunks": FakeCollection(5),
            "embeddings": FakeCollection(5),
            "document_entities": FakeCollection(2),
            "incidents": FakeCollection(1),
            "asset_events": FakeCollection(3),
        }

    def __getitem__(self, collection: str) -> FakeCollection:
        if collection not in self.collections:
            self.collections[collection] = FakeCollection(0)
        return self.collections[collection]


class FakeCache:
    def __init__(self) -> None:
        self.patterns: list[str] = []
        self.remaining = {
            "search:*": 2,
            "chat:*": 1,
            "graph:*": 3,
            "digital_twin:*": 1,
        }

    async def delete_pattern(self, pattern: str) -> int:
        self.patterns.append(pattern)
        return self.remaining.pop(pattern, 0)


@pytest.mark.asyncio
async def test_factory_reset_clears_runtime_data_idempotently(monkeypatch: pytest.MonkeyPatch) -> None:
    test_root = Path.cwd() / f"pytest-factory-reset-{uuid4()}"
    storage_root = test_root / "runtime-documents"
    storage_root.mkdir(parents=True)
    try:
        (storage_root / "uploaded.pdf").write_bytes(b"%PDF-1.7")
        (storage_root / "processing").mkdir()
        (storage_root / "processing" / "artifact.txt").write_text("temporary", encoding="utf-8")

        monkeypatch.setattr("app.services.factory_reset_service.ROOT_DIR", test_root / "source-root")
        monkeypatch.setattr("app.services.factory_reset_service.settings.document_storage_root", str(storage_root))

        service = FactoryResetService(cache=FakeCache())  # type: ignore[arg-type]
        service.db = FakeMongoDatabase()  # type: ignore[assignment]

        graph_calls = 0

        async def fake_clear_neo4j() -> dict[str, int]:
            nonlocal graph_calls
            graph_calls += 1
            return {"nodes": 4 if graph_calls == 1 else 0, "relationships": 6 if graph_calls == 1 else 0}

        monkeypatch.setattr(service, "_clear_neo4j", fake_clear_neo4j)

        first = await service.reset()
        second = await service.reset()

        assert first.success is True
        assert first.deleted.documents == 2
        assert first.deleted.chunks == 5
        assert first.deleted.embeddings == 5
        assert first.deleted.graphNodes == 4
        assert first.deleted.graphRelationships == 6
        assert first.deleted.cacheKeys == 7
        assert first.deleted.uploadedFiles == 2
        assert second.deleted.documents == 0
        assert second.deleted.graphNodes == 0
        assert second.deleted.uploadedFiles == 0
        assert storage_root.exists()
        assert (storage_root / "tmp").is_dir()
        assert (storage_root / "processing").is_dir()
    finally:
        if test_root.exists():
            shutil.rmtree(test_root)


def test_factory_reset_rejects_source_tree_paths() -> None:
    with pytest.raises(RuntimeError):
        FactoryResetService._ensure_runtime_path(Path.cwd().resolve())


def test_factory_reset_route_returns_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    class StubFactoryResetService:
        async def reset(self) -> FactoryResetResponse:
            return FactoryResetResponse(
                deleted=FactoryResetDeletedCounts(
                    documents=0,
                    chunks=0,
                    embeddings=0,
                    graphNodes=0,
                    graphRelationships=0,
                    cacheKeys=0,
                    uploadedFiles=0,
                )
            )

    monkeypatch.setattr(admin_route, "FactoryResetService", StubFactoryResetService)

    client = TestClient(app)
    response = client.delete("/api/v1/admin/factory-reset")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "deleted": {
            "documents": 0,
            "chunks": 0,
            "embeddings": 0,
            "graphNodes": 0,
            "graphRelationships": 0,
            "cacheKeys": 0,
            "uploadedFiles": 0,
        },
    }
