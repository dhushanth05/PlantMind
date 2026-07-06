from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.mongodb.client import mongo_database
from app.db.neo4j.client import neo4j_database
from app.db.redis.client import redis_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    mongo_database.close()
    await neo4j_database.close()
    await redis_database.close()


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="PlantMind API",
        version="0.1.0",
        description="Industrial Knowledge Intelligence Platform API skeleton.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
