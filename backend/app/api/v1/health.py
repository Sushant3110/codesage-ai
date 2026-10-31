"""Health and readiness endpoints.

GET /api/v1/health  — liveness probe (always 200 if process is alive)
GET /api/v1/ready   — readiness probe (200 only if dependencies are reachable)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.common import (
    HealthResponse,
    ReadinessCheck,
    ReadinessResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Always returns 200 if the process is running.",
)
async def health(request: Request) -> HealthResponse:
    version: str = getattr(request.app.state, "app_version", "0.1.0")
    return HealthResponse(status="ok", version=version)


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns 200 when all dependencies are reachable; 503 otherwise.",
)
async def ready(request: Request) -> JSONResponse:
    """Check MongoDB and ChromaDB reachability stored in app.state."""
    mongo_status: str = getattr(request.app.state, "mongo_status", "not_checked")
    chroma_status: str = getattr(request.app.state, "chroma_status", "not_checked")

    checks = ReadinessCheck(mongodb=mongo_status, chromadb=chroma_status)
    all_ok = mongo_status == "ok" and chroma_status == "ok"

    response = ReadinessResponse(
        status="ready" if all_ok else "not_ready",
        checks=checks,
    )
    return JSONResponse(
        content=response.model_dump(),
        status_code=200 if all_ok else 503,
    )
