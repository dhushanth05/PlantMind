from pydantic import BaseModel, Field


class FactoryResetDeletedCounts(BaseModel):
    documents: int = 0
    chunks: int = 0
    embeddings: int = 0
    graphNodes: int = Field(default=0, alias="graphNodes")
    graphRelationships: int = Field(default=0, alias="graphRelationships")
    cacheKeys: int = Field(default=0, alias="cacheKeys")
    uploadedFiles: int = Field(default=0, alias="uploadedFiles")


class FactoryResetResponse(BaseModel):
    success: bool = True
    deleted: FactoryResetDeletedCounts
