"""Review endpoints.

POST /api/v1/reviews          — submit code for review
GET  /api/v1/reviews/{id}     — retrieve a completed review by ID
"""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import OrchestratorDep
from app.schemas.common import ErrorResponse
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.llm_provider import (
    LLMConfigurationError,
    LLMProviderError,
    LLMQuotaExceededError,
    LLMResponseValidationError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["reviews"])


@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    responses={
        413: {"model": ErrorResponse, "description": "Code exceeds size limit"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        503: {"model": ErrorResponse, "description": "Review engine not available"},
        500: {"model": ErrorResponse, "description": "Unexpected server error"},
    },
    summary="Submit code for review",
    description=(
        "Accepts Python source code and returns a structured code review. "
        "This endpoint is synchronous and may take 5-30 seconds."
    ),
)
async def create_review(
    request: Request,
    body: ReviewRequest,
    orchestrator: OrchestratorDep,
) -> ReviewResponse:
    """Validate input, invoke review orchestrator, and return validated findings."""
    settings = request.app.state.settings

    # 1. Enforce input size limit
    code_bytes = len(body.code.encode("utf-8"))
    if code_bytes > settings.max_code_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "detail": (
                    f"Submitted code is {code_bytes} bytes, which exceeds the "
                    f"{settings.max_code_size_bytes}-byte limit."
                ),
                "code": "CODE_TOO_LARGE",
            },
        )

    # 2. Execute review via orchestrator
    try:
        response = orchestrator.run_review(body)
        return response
    except LLMConfigurationError as exc:
        logger.warning("Review requested but LLM is not configured or authentication failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "LLM review service is not configured or authentication failed. Please check GEMINI_API_KEY.",
                "code": "SERVICE_UNAVAILABLE",
            },
        ) from exc
    except LLMQuotaExceededError as exc:
        logger.warning("LLM quota exceeded during review: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Gemini API quota or rate limit exceeded (HTTP 429). Please retry later.",
                "code": "SERVICE_UNAVAILABLE",
            },
        ) from exc
    except LLMTimeoutError as exc:
        logger.warning("LLM timeout during review: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Gemini API review request timed out after 30 seconds. Please retry with smaller input or later.",
                "code": "SERVICE_UNAVAILABLE",
            },
        ) from exc
    except LLMResponseValidationError as exc:
        logger.error("LLM produced invalid response during review: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "The review engine produced an unparseable response. Please retry.",
                "code": "SERVICE_UNAVAILABLE",
            },
        ) from exc
    except LLMProviderError as exc:
        logger.error("LLM provider error during review: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Gemini review service temporarily unavailable. Please retry later.",
                "code": "SERVICE_UNAVAILABLE",
            },
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in review creation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An internal error occurred while processing the review.",
                "code": "INTERNAL_ERROR",
            },
        ) from exc


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Review not found"},
        422: {"model": ErrorResponse, "description": "Invalid review ID format"},
        503: {"model": ErrorResponse, "description": "Persistence not yet implemented"},
    },
    summary="Get a review by ID",
    description="Returns the full review result for a previously submitted review.",
)
async def get_review(
    review_id: str,
    request: Request,
) -> ReviewResponse:
    """Retrieve review by ID (stub until Phase 5 persistence)."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    if not uuid_pattern.match(review_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": f"'{review_id}' is not a valid UUID.",
                "code": "VALIDATION_ERROR",
            },
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "detail": "Review persistence is not yet implemented (Phase 5).",
            "code": "SERVICE_UNAVAILABLE",
        },
    )
