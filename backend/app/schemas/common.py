"""Shared Pydantic schemas: error responses, paginated responses, and finding counts."""

from __future__ import annotations

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error envelope returned for all non-2xx responses."""

    detail: str = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable uppercase error code.")

    model_config = {"json_schema_extra": {"example": {"detail": "Review not found.", "code": "REVIEW_NOT_FOUND"}}}


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(default_factory=list)
    total: int = Field(ge=0, description="Total number of matching records.")
    page: int = Field(ge=1, description="Current page number (1-indexed).")
    page_size: int = Field(ge=1, le=100, description="Number of items per page.")
    total_pages: int = Field(ge=0, description="Total number of pages.")

    @model_validator(mode="before")
    @classmethod
    def compute_total_pages(cls, data: dict) -> dict:  # type: ignore[override]
        if isinstance(data, dict):
            total = data.get("total", 0)
            page_size = data.get("page_size", 20)
            if page_size and "total_pages" not in data:
                data["total_pages"] = max(1, math.ceil(total / page_size)) if total > 0 else 0
        return data


class FindingCounts(BaseModel):
    """Pre-computed per-severity finding counts for a review."""

    critical: int = Field(default=0, ge=0)
    high: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    low: int = Field(default=0, ge=0)
    info: int = Field(default=0, ge=0)


class HealthResponse(BaseModel):
    """Response for GET /api/v1/health."""

    status: str
    version: str


class ReadinessCheck(BaseModel):
    """Individual dependency check result."""

    mongodb: str
    chromadb: str


class ReadinessResponse(BaseModel):
    """Response for GET /api/v1/ready."""

    status: str  # "ready" or "not_ready"
    checks: ReadinessCheck


class CapabilitiesResponse(BaseModel):
    """Response for GET /api/v1/capabilities."""

    supported_languages: list[str]
    llm_model: str
    static_analysis_tools: list[str]
    rag_enabled: bool
    rag_document_count: int
    max_code_size_bytes: int
