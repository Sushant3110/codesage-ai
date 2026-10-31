"""Application configuration — single Settings class backed by pydantic-settings.

All environment variables are read here. No other module should read os.environ
or access .env files directly. Secrets (GEMINI_API_KEY) are never logged.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Required secrets ────────────────────────────────────────────────────
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key. Required for LLM features.",
    )
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection string.",
    )

    # ── MongoDB ─────────────────────────────────────────────────────────────
    mongodb_db_name: str = Field(default="codesage")

    # ── Gemini / LLM ────────────────────────────────────────────────────────
    gemini_model: str = Field(default="gemini-1.5-flash")
    gemini_timeout_seconds: Annotated[int, Field(ge=5, le=300)] = 30
    gemini_max_retries: Annotated[int, Field(ge=0, le=5)] = 1

    # ── Input validation ────────────────────────────────────────────────────
    max_code_size_bytes: Annotated[int, Field(ge=1024, le=524288)] = 32768

    # ── ChromaDB & RAG ──────────────────────────────────────────────────────
    chroma_persist_dir: str = Field(default="./chroma_data")
    chroma_collection_name: str = Field(default="coding_guidelines")
    rag_enabled: bool = Field(default=True, description="Enable or disable RAG retrieval.")
    rag_n_results: Annotated[int, Field(ge=1, le=20)] = 5
    rag_chunk_size: Annotated[int, Field(ge=100, le=2000)] = 500
    rag_chunk_overlap: Annotated[int, Field(ge=0, le=500)] = 50
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="SentenceTransformers model name.")

    # ── CORS ───────────────────────────────────────────────────────────────
    cors_origins: str = Field(default="http://localhost:5173")

    # ── Logging ─────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    # ── App metadata ────────────────────────────────────────────────────────
    app_version: str = Field(default="0.1.0")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        level = v.upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"Invalid log level: {v}")
        return level

    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list (split on comma)."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def has_gemini_key(self) -> bool:
        """Return True if a non-placeholder Gemini key is configured."""
        return bool(self.gemini_api_key) and self.gemini_api_key != "your-gemini-api-key-here"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    settings = Settings()
    # Configure root logger immediately when settings are first loaded.
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    return settings
