"""Review request and response schemas.

These are the primary API-level types for code-review submission and results.
They are the single source of truth for the review contract; the TypeScript
mirrors in frontend/src/types/review.ts must stay in sync.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import FindingCounts
from app.schemas.finding import SEVERITY_ORDER, Finding, Severity


class ReviewRequest(BaseModel):
    """Request body for POST /api/v1/reviews."""

    code: Annotated[
        str,
        Field(
            min_length=1,
            description="Source code to review. Max size enforced at API layer.",
        ),
    ]
    language: str = Field(
        description="Programming language. Supported: python, java, javascript, typescript, c, cpp, html, css, sql.",
    )
    context: str | None = Field(
        default=None,
        max_length=500,
        description="Optional user-provided description passed to the LLM prompt.",
    )

    @field_validator("language")
    @classmethod
    def language_must_be_supported(cls, v: str) -> str:
        from app.core.languages import ALL_SUPPORTED_LANGUAGE_IDS, normalize_language

        normalized = normalize_language(v)
        if normalized is None:
            supported_str = ", ".join(ALL_SUPPORTED_LANGUAGE_IDS)
            raise ValueError(f"Unsupported language '{v}'. Supported languages: {supported_str}")
        return normalized.value

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "def greet(name):\n    print('Hello ' + name)\n",
                "language": "python",
                "context": "Simple greeting function for a CLI tool.",
            }
        }
    }


class ReviewSummary(BaseModel):
    """Compact review record used in GET /api/v1/history responses."""

    id: str
    submitted_at: datetime
    code_snippet: str = Field(
        description="First 500 characters of the submitted code (not the full code).",
    )
    finding_counts: FindingCounts
    language: str


class ReviewResponse(BaseModel):
    """Full review result — returned by POST /api/v1/reviews and GET /api/v1/reviews/{id}."""

    id: str = Field(description="UUID of this review.")
    submitted_at: datetime = Field(description="UTC timestamp of submission.")
    code_hash: str = Field(description="SHA-256 hex digest of the submitted code.")
    language: str
    summary: str = Field(
        default="",
        description="One-paragraph LLM summary. Empty if LLM was unavailable.",
    )
    findings: list[Finding] = Field(default_factory=list)
    static_analysis_ran: bool = Field(
        default=False,
        description="True if Ruff and Bandit were executed successfully.",
    )
    rag_context_retrieved: bool = Field(
        default=False,
        description="True if at least one RAG chunk was retrieved from ChromaDB.",
    )
    finding_counts: FindingCounts = Field(default_factory=FindingCounts)

    @model_validator(mode="after")
    def compute_finding_counts(self) -> ReviewResponse:
        """Recompute finding_counts from the findings list if not already set."""
        counts = FindingCounts()
        for f in self.findings:
            sev = f.severity
            if sev == Severity.critical:
                counts.critical += 1
            elif sev == Severity.high:
                counts.high += 1
            elif sev == Severity.medium:
                counts.medium += 1
            elif sev == Severity.low:
                counts.low += 1
            elif sev == Severity.info:
                counts.info += 1
        self.finding_counts = counts
        return self

    def sorted_findings(self) -> list[Finding]:
        """Return findings sorted by severity (critical → info)."""
        return sorted(self.findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    def to_summary(self, code_snippet: str) -> ReviewSummary:
        """Build a ReviewSummary from this response (for history listing)."""
        return ReviewSummary(
            id=self.id,
            submitted_at=self.submitted_at,
            code_snippet=code_snippet[:500],
            finding_counts=self.finding_counts,
            language=self.language,
        )

    @staticmethod
    def hash_code(code: str) -> str:
        """Return the SHA-256 hex digest of the submitted code."""
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def utcnow() -> datetime:
        """Return the current UTC datetime (timezone-aware)."""
        return datetime.now(tz=UTC)
