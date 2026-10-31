"""Capabilities endpoint.

GET /api/v1/capabilities — returns safe, static information about backend features.
No secrets are exposed.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.core.languages import ALL_SUPPORTED_LANGUAGE_IDS
from app.schemas.common import CapabilitiesResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["capabilities"])


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    summary="Service capabilities",
    description=(
        "Returns safe information about supported languages, tools, and feature availability. "
        "No secrets are included in the response."
    ),
)
async def capabilities(request: Request) -> CapabilitiesResponse:
    settings = request.app.state.settings
    rag_enabled: bool = getattr(request.app.state, "rag_enabled", False)
    rag_document_count: int = getattr(request.app.state, "rag_document_count", 0)

    return CapabilitiesResponse(
        supported_languages=ALL_SUPPORTED_LANGUAGE_IDS,
        llm_model=settings.gemini_model,
        static_analysis_tools=["ruff", "bandit"],
        rag_enabled=rag_enabled,
        rag_document_count=rag_document_count,
        max_code_size_bytes=settings.max_code_size_bytes,
    )
