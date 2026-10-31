"""Unit tests for Pydantic schemas — finding model, review schemas, common schemas."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.common import PaginatedResponse
from app.schemas.finding import (
    Citation,
    Finding,
    FindingSource,
    LineRange,
    Severity,
    VerificationStatus,
)
from app.schemas.review import ReviewRequest, ReviewResponse

# ---------------------------------------------------------------------------
# LineRange
# ---------------------------------------------------------------------------


class TestLineRange:
    def test_valid_range(self):
        lr = LineRange(start=1, end=5)
        assert lr.start == 1
        assert lr.end == 5

    def test_single_line(self):
        lr = LineRange(start=10, end=10)
        assert lr.start == lr.end

    def test_end_less_than_start_raises(self):
        with pytest.raises(ValidationError):
            LineRange(start=10, end=5)

    def test_zero_start_raises(self):
        with pytest.raises(ValidationError):
            LineRange(start=0, end=1)

    def test_negative_start_raises(self):
        with pytest.raises(ValidationError):
            LineRange(start=-1, end=1)


# ---------------------------------------------------------------------------
# Citation
# ---------------------------------------------------------------------------


class TestCitation:
    def test_valid_citation(self):
        c = Citation(
            document_title="PEP 8",
            chunk_text="Use spaces around operators.",
            source_file="pep8.md",
            relevance_score=0.92,
        )
        assert c.relevance_score == 0.92

    def test_relevance_score_above_1_raises(self):
        with pytest.raises(ValidationError):
            Citation(
                document_title="X",
                chunk_text="Y",
                source_file="z.md",
                relevance_score=1.1,
            )

    def test_relevance_score_below_0_raises(self):
        with pytest.raises(ValidationError):
            Citation(
                document_title="X",
                chunk_text="Y",
                source_file="z.md",
                relevance_score=-0.1,
            )


# ---------------------------------------------------------------------------
# Finding
# ---------------------------------------------------------------------------


class TestFinding:
    def _minimal_finding(self, **kwargs) -> dict:
        base = {
            "id": str(uuid.uuid4()),
            "source": "ruff",
            "severity": "low",
            "category": "style",
            "title": "Line too long",
            "explanation": "PEP 8 recommends 79 chars.",
            "verification_status": "deterministic",
            "citations": [],
        }
        base.update(kwargs)
        return base

    def test_valid_ruff_finding(self):
        f = Finding(**self._minimal_finding(rule_id="E501"))
        assert f.source == FindingSource.ruff
        assert f.verification_status == VerificationStatus.deterministic
        assert f.rule_id == "E501"

    def test_valid_llm_finding(self):
        f = Finding(
            **self._minimal_finding(
                source="llm",
                severity="high",
                category="security",
                rule_id=None,
                verification_status="unverified",
            )
        )
        assert f.source == FindingSource.llm
        assert f.verification_status == VerificationStatus.unverified
        assert f.rule_id is None

    def test_invalid_severity_raises(self):
        with pytest.raises(ValidationError):
            Finding(**self._minimal_finding(severity="catastrophic"))

    def test_invalid_source_raises(self):
        with pytest.raises(ValidationError):
            Finding(**self._minimal_finding(source="mypy"))

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            Finding(**self._minimal_finding(title=""))

    def test_finding_with_patch(self):
        f = Finding(
            **self._minimal_finding(
                patch={"original": "x=1\n", "suggested": "x = 1\n"},
            )
        )
        assert f.patch is not None
        assert f.patch.suggested == "x = 1\n"

    def test_finding_with_line_range(self):
        f = Finding(**self._minimal_finding(line_range={"start": 5, "end": 7}))
        assert f.line_range is not None
        assert f.line_range.start == 5

    def test_finding_with_citations(self):
        citation = {
            "document_title": "PEP 8",
            "chunk_text": "...",
            "source_file": "pep8.md",
            "relevance_score": 0.8,
        }
        f = Finding(**self._minimal_finding(citations=[citation]))
        assert len(f.citations) == 1

    def test_all_severities_valid(self):
        for sev in ["critical", "high", "medium", "low", "info"]:
            f = Finding(**self._minimal_finding(severity=sev))
            assert f.severity.value == sev

    def test_all_categories_valid(self):
        for cat in ["security", "correctness", "performance", "maintainability", "style", "documentation"]:
            f = Finding(**self._minimal_finding(category=cat))
            assert f.category.value == cat

    def test_all_sources_valid(self):
        for src in ["llm", "ruff", "bandit"]:
            f = Finding(**self._minimal_finding(source=src))
            assert f.source.value == src


# ---------------------------------------------------------------------------
# ReviewRequest
# ---------------------------------------------------------------------------


class TestReviewRequest:
    def test_valid_request(self):
        r = ReviewRequest(code="print('hi')", language="python")
        assert r.language == "python"

    def test_wrong_language_raises(self):
        with pytest.raises(ValidationError):
            ReviewRequest(code="console.log('hi')", language="unsupported_fortran")

    def test_multilang_requests_valid(self):
        for lang in ("python", "java", "javascript", "typescript", "c", "cpp", "html", "css", "sql"):
            r = ReviewRequest(code="let a = 1;", language=lang)
            assert r.language == lang

    def test_empty_code_raises(self):
        with pytest.raises(ValidationError):
            ReviewRequest(code="", language="python")

    def test_context_within_limit(self):
        r = ReviewRequest(code="x=1", language="python", context="a" * 500)
        assert len(r.context) == 500

    def test_context_too_long_raises(self):
        with pytest.raises(ValidationError):
            ReviewRequest(code="x=1", language="python", context="a" * 501)

    def test_context_optional(self):
        r = ReviewRequest(code="x=1", language="python")
        assert r.context is None


# ---------------------------------------------------------------------------
# ReviewResponse + FindingCounts
# ---------------------------------------------------------------------------


class TestReviewResponse:
    def _make_finding(self, severity: str) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "source": "ruff",
            "severity": severity,
            "category": "style",
            "title": "Test",
            "explanation": "Test finding.",
            "verification_status": "deterministic",
            "citations": [],
        }

    def test_finding_counts_computed(self):
        findings = [
            self._make_finding("critical"),
            self._make_finding("high"),
            self._make_finding("high"),
            self._make_finding("medium"),
            self._make_finding("info"),
        ]
        r = ReviewResponse(
            id=str(uuid.uuid4()),
            submitted_at=ReviewResponse.utcnow(),
            code_hash="abc123",
            language="python",
            findings=findings,
        )
        assert r.finding_counts.critical == 1
        assert r.finding_counts.high == 2
        assert r.finding_counts.medium == 1
        assert r.finding_counts.low == 0
        assert r.finding_counts.info == 1

    def test_empty_findings(self):
        r = ReviewResponse(
            id=str(uuid.uuid4()),
            submitted_at=ReviewResponse.utcnow(),
            code_hash="abc123",
            language="python",
        )
        assert r.finding_counts.critical == 0
        assert r.findings == []

    def test_hash_code(self):
        h = ReviewResponse.hash_code("print('hi')")
        assert len(h) == 64  # SHA-256 hex
        # Deterministic
        assert h == ReviewResponse.hash_code("print('hi')")

    def test_sorted_findings_order(self):
        findings = [
            self._make_finding("info"),
            self._make_finding("critical"),
            self._make_finding("medium"),
        ]
        r = ReviewResponse(
            id=str(uuid.uuid4()),
            submitted_at=ReviewResponse.utcnow(),
            code_hash="abc",
            language="python",
            findings=findings,
        )
        sorted_f = r.sorted_findings()
        assert sorted_f[0].severity == Severity.critical
        assert sorted_f[-1].severity == Severity.info

    def test_to_summary(self):
        r = ReviewResponse(
            id="test-id",
            submitted_at=ReviewResponse.utcnow(),
            code_hash="abc",
            language="python",
        )
        summary = r.to_summary("def hello(): pass")
        assert summary.id == "test-id"
        assert summary.code_snippet == "def hello(): pass"

    def test_to_summary_truncates_at_500(self):
        r = ReviewResponse(
            id="test-id",
            submitted_at=ReviewResponse.utcnow(),
            code_hash="abc",
            language="python",
        )
        long_code = "x" * 600
        summary = r.to_summary(long_code)
        assert len(summary.code_snippet) == 500


# ---------------------------------------------------------------------------
# PaginatedResponse
# ---------------------------------------------------------------------------


class TestPaginatedResponse:
    def test_total_pages_computed(self):
        p = PaginatedResponse[str](items=[], total=42, page=1, page_size=20)
        assert p.total_pages == 3  # ceil(42/20)

    def test_total_pages_exact_division(self):
        p = PaginatedResponse[str](items=[], total=40, page=1, page_size=20)
        assert p.total_pages == 2

    def test_total_pages_zero_when_empty(self):
        p = PaginatedResponse[str](items=[], total=0, page=1, page_size=20)
        assert p.total_pages == 0

    def test_items_are_preserved(self):
        p = PaginatedResponse[str](items=["a", "b"], total=2, page=1, page_size=20)
        assert p.items == ["a", "b"]
