"""History endpoint.

GET /api/v1/history — paginated review history (most recent first)

Phase 1 stub: returns an empty paginated response because MongoDB persistence
is not yet implemented. The response shape matches the contract exactly.
Phase 5 will wire this to the real ReviewRepository.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.review import ReviewSummary

logger = logging.getLogger(__name__)
router = APIRouter(tags=["history"])


@router.get(
    "/history",
    response_model=PaginatedResponse[ReviewSummary],
    status_code=status.HTTP_200_OK,
    summary="List review history",
    description=(
        "Returns a paginated list of past reviews, most recent first. "
        "Persistence is not yet implemented (Phase 5); returns empty list."
    ),
)
async def list_history(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed).")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Results per page.")] = 20,
) -> PaginatedResponse[ReviewSummary]:
    """Phase 1 stub: returns empty paginated response."""
    logger.debug("History requested (page=%d, page_size=%d) — stub returning empty.", page, page_size)
    return PaginatedResponse[ReviewSummary](
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )
