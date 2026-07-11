from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_root_dir() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".env").exists() or (parent / "docker-compose.yml").exists():
            return parent
    return current.parents[2]


ROOT_DIR = find_root_dir()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    log_level: str = "INFO"
    cors_origins_raw: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    mongodb_uri: str = "mongodb://mongodb:27017/plantmind"
    mongodb_database: str = "plantmind"
    mongodb_vector_index: str = Field(default="plantmind_vector_index", alias="MONGODB_VECTOR_INDEX")
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "plantmind-local-password"
    neo4j_database: str = "neo4j"
    redis_url: str = "redis://redis:6379/0"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"
    sentence_transformer_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    spacy_model: str = "en_core_web_sm"
    document_storage_root: str = "/data/documents"
    max_upload_mb: int = 100
    scanned_text_threshold: int = 250
    graph_cache_ttl_seconds: int = 60
    search_cache_ttl_seconds: int = 60
    hybrid_search_top_k: int = 8
    digital_twin_cache_ttl_seconds: int = 300

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
