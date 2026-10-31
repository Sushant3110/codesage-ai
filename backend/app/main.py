"""CodeSage AI — FastAPI application entry point.

This module creates the FastAPI app, registers middleware, mounts the API router,
and manages the lifespan (startup/shutdown) of external dependencies.

It contains no business logic. All logic lives in app/services/.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import capabilities, health, history, reviews
from app.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup and shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise dependencies on startup; clean up on shutdown."""
    settings = get_settings()
    app.state.settings = settings
    app.state.app_version = settings.app_version

    # ── MongoDB ──────────────────────────────────────────────────────────
    mongo_client: Any = None
    try:
        import pymongo

        mongo_client = pymongo.MongoClient(  # type: ignore[attr-defined]
            settings.mongodb_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
        )
        # Force a connection attempt to catch bad URIs early.
        mongo_client.admin.command("ping")
        app.state.mongo_client = mongo_client
        app.state.mongo_db = mongo_client[settings.mongodb_db_name]
        app.state.mongo_status = "ok"
        logger.info("MongoDB connected: %s / %s", settings.mongodb_uri, settings.mongodb_db_name)
    except Exception as exc:
        # Non-fatal: app still starts; ready endpoint reflects this.
        logger.warning("MongoDB unavailable at startup: %s", exc)
        app.state.mongo_client = None
        app.state.mongo_db = None
        app.state.mongo_status = f"error: {exc}"

    # ── ChromaDB ─────────────────────────────────────────────────────────
    try:
        import importlib

        chromadb = importlib.import_module("chromadb")  # lazy — allows mock injection in tests
        chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=chromadb.config.Settings(anonymized_telemetry=False, is_persistent=True),
        )
        # Verify the collection is accessible (creates it if it doesn't exist).
        collection = chroma_client.get_or_create_collection(settings.chroma_collection_name)
        doc_count = collection.count()
        app.state.chroma_client = chroma_client
        app.state.chroma_collection = collection
        app.state.chroma_status = "ok"
        app.state.rag_enabled = settings.rag_enabled and (doc_count > 0)
        app.state.rag_document_count = doc_count
        logger.info(
            "ChromaDB ready: collection='%s', chunks=%d, rag_enabled=%s",
            settings.chroma_collection_name,
            doc_count,
            app.state.rag_enabled,
        )
    except Exception as exc:
        logger.warning("ChromaDB unavailable at startup: %s", exc)
        app.state.chroma_client = None
        app.state.chroma_collection = None
        app.state.chroma_status = f"error: {exc}"
        app.state.rag_enabled = False
        app.state.rag_document_count = 0

    # ── Gemini key presence check ─────────────────────────────────────────
    if not settings.has_gemini_key():
        logger.warning(
            "GEMINI_API_KEY is not configured or is a placeholder. "
            "LLM review features will be unavailable."
        )

    logger.info("CodeSage AI v%s started.", settings.app_version)
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────
    if mongo_client is not None:
        mongo_client.close()
        logger.info("MongoDB connection closed.")
    logger.info("CodeSage AI shut down.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Construct and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="CodeSage AI",
        description=(
            "AI-powered Python code review: static analysis (Ruff + Bandit), "
            "LLM findings (Gemini), and RAG-grounded citations."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Initialize default state attributes immediately
    app.state.settings = settings
    app.state.app_version = settings.app_version
    app.state.mongo_client = None
    app.state.mongo_db = None
    app.state.mongo_status = "not_checked"
    app.state.chroma_client = None
    app.state.chroma_collection = None
    app.state.chroma_status = "not_checked"
    app.state.rag_enabled = False
    app.state.rag_document_count = 0

    # ── CORS ─────────────────────────────────────────────────────────────
    origins = settings.cors_origins_list()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Accept"],
    )

    # ── Custom exception handlers ────────────────────────────────────────
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTPExceptions, unpacking structured dict details directly into the error envelope."""
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail), "code": "ERROR"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Convert Pydantic validation errors to the standard ErrorResponse shape."""
        first_error = exc.errors()[0] if exc.errors() else {}
        msg = first_error.get("msg", "Validation error")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": msg, "code": "VALIDATION_ERROR"},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all handler — returns 500 without leaking internal details."""
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred.", "code": "INTERNAL_ERROR"},
        )

    # ── Routers ──────────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(health.router, prefix=prefix)
    app.include_router(capabilities.router, prefix=prefix)
    app.include_router(reviews.router, prefix=prefix)
    app.include_router(history.router, prefix=prefix)

    return app


# Module-level app instance used by uvicorn / tests.
app = create_app()
