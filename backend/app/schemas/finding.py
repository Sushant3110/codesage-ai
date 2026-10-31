"""Finding model — the atomic unit of review output.

Both LLM and static-analysis tools produce Finding objects conforming to
this schema. The `source` and `verification_status` fields distinguish them.
See docs/ARCHITECTURE.md §4 and docs/API_CONTRACTS.md §3.8.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Severity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


# Severity ordering for sorting (lower number = higher priority)
SEVERITY_ORDER: dict[Severity, int] = {
    Severity.critical: 0,
    Severity.high: 1,
    Severity.medium: 2,
    Severity.low: 3,
    Severity.info: 4,
}


class Category(StrEnum):
    security = "security"
    correctness = "correctness"
    performance = "performance"
    maintainability = "maintainability"
    style = "style"
    documentation = "documentation"


class VerificationStatus(StrEnum):
    """How trustworthy the finding is.

    - ``deterministic``: produced by a rule-based static analysis tool; the
      finding accurately reflects what the tool found.
    - ``unverified``: produced by an LLM; the line references, evidence, and
      suggested patch may be inaccurate.
    """

    deterministic = "deterministic"
    unverified = "unverified"


class FindingSource(StrEnum):
    """Which tool or service produced this finding."""

    llm = "llm"
    ruff = "ruff"
    bandit = "bandit"


class LineRange(BaseModel):
    """Inclusive 1-indexed line range within submitted code."""

    start: int = Field(ge=1, description="First line of the finding (1-indexed).")
    end: int = Field(ge=1, description="Last line of the finding (1-indexed, inclusive).")

    @field_validator("end")
    @classmethod
    def end_ge_start(cls, v: int, info) -> int:  # type: ignore[override]
        start = info.data.get("start")
        if start is not None and v < start:
            raise ValueError(f"`end` ({v}) must be >= `start` ({start})")
        return v


class Patch(BaseModel):
    """A suggested code patch — display-only; never auto-applied."""

    original: str = Field(description="Exact text from submitted code to be replaced.")
    suggested: str = Field(description="Replacement text.")


class Citation(BaseModel):
    """A retrieved chunk from the RAG knowledge base that grounds the finding."""

    document_title: str
    chunk_text: str
    source_file: str
    relevance_score: float = Field(ge=0.0, le=1.0, description="Cosine similarity score from ChromaDB.")
    source_url: str | None = Field(default=None, description="Approved external URL for the reference document.")
    section: str | None = Field(default=None, description="Section heading within the reference document.")


class Finding(BaseModel):
    """A single code-review finding produced by LLM or static analysis."""

    id: str = Field(description="UUID — stable within a review; not globally deduplicated.")
    source: FindingSource
    severity: Severity
    category: Category
    rule_id: str | None = Field(
        default=None,
        description="Tool rule code (e.g. 'E501', 'B105'). Null for LLM findings.",
    )
    title: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1)
    evidence: str | None = Field(
        default=None,
        description="Quoted code snippet or tool message. May be None.",
    )
    line_range: LineRange | None = Field(
        default=None,
        description="Affected lines. From tool output for static; LLM-provided (may be wrong) for LLM findings.",
    )
    patch: Patch | None = Field(
        default=None,
        description="Display-only suggested fix. Never automatically applied.",
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="RAG citations grounding the finding. Empty for static-analysis findings.",
    )
    verification_status: VerificationStatus

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "source": "llm",
                "severity": "high",
                "category": "security",
                "rule_id": None,
                "title": "Hardcoded password detected",
                "explanation": "The variable `password` is assigned a string literal.",
                "evidence": 'password = "hunter2"',
                "line_range": {"start": 12, "end": 12},
                "patch": {
                    "original": 'password = "hunter2"\n',
                    "suggested": 'password = os.getenv("APP_PASSWORD")\n',
                },
                "citations": [],
                "verification_status": "unverified",
            }
        }
    }
