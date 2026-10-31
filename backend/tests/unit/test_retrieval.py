"""Unit tests for CodeSage AI RAG pipeline and RetrievalService.

Verifies document parsing, chunking, deterministic IDs, duplicate ingestion prevention,
similarity score normalization, graceful error handling, RAG disabling, and citation grounding.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.rag.ingest import (
    DOCUMENTS_DIR,
    ingest_documents,
    parse_markdown_metadata,
)
from app.schemas.finding import (
    Category,
    Citation,
    Finding,
    FindingSource,
    Severity,
    VerificationStatus,
)
from app.schemas.review import ReviewRequest
from app.services.orchestrator import ReviewOrchestrator
from app.services.retrieval import RetrievalService

# ---------------------------------------------------------------------------
# 1. Document Parsing and Chunking Tests
# ---------------------------------------------------------------------------


def test_parse_markdown_metadata_extracts_headers():
    raw_md = (
        "# Sample Document Title\n"
        "Source URL: https://example.com/guidelines\n"
        "Document Title: Canonical Title\n\n"
        "## Section 1\n"
        "Content in section 1.\n\n"
        "### Section 1.1\n"
        "Deeper content.\n\n"
        "## Section 2\n"
        "Content in section 2.\n"
    )
    meta, sections = parse_markdown_metadata(raw_md, "sample.md")

    assert meta.title == "Canonical Title"
    assert meta.source_url == "https://example.com/guidelines"
    assert meta.source_file == "sample.md"
    assert len(meta.content_hash) == 64  # SHA-256

    assert len(sections) == 3
    sec_names = [s[0] for s in sections]
    assert "Section 1" in sec_names
    assert "Section 1.1" in sec_names
    assert "Section 2" in sec_names


def test_parse_markdown_fallback_title():
    raw_md = "# First Heading\nSome general text without front metadata."
    meta, sections = parse_markdown_metadata(raw_md, "test.md")
    assert meta.title == "First Heading"
    assert meta.source_url == ""
    assert len(sections) == 1
    assert sections[0][0] == "General"


def test_curated_guideline_documents_exist():
    """Verify all 3 required guideline documents exist in app/rag/documents/."""
    assert DOCUMENTS_DIR.exists(), f"Missing documents dir: {DOCUMENTS_DIR}"
    md_files = list(DOCUMENTS_DIR.glob("*.md"))
    filenames = [f.name for f in md_files]

    assert "pep8_style_guide.md" in filenames
    assert "owasp_python_security.md" in filenames
    assert "python_defensive_programming.md" in filenames


# ---------------------------------------------------------------------------
# 2. Citation Schema & Normalization Tests
# ---------------------------------------------------------------------------


def test_citation_model_validates_relevance_score():
    """Relevance score must be within [0.0, 1.0]."""
    cit = Citation(
        document_title="PEP 8",
        chunk_text="Use 4 spaces",
        source_file="pep8.md",
        relevance_score=0.85,
        source_url="https://peps.python.org/pep-0008/",
        section="Indentation",
    )
    assert cit.relevance_score == 0.85
    assert cit.source_url == "https://peps.python.org/pep-0008/"

    # Invalid score > 1.0
    with pytest.raises(ValidationError):
        Citation(
            document_title="PEP 8",
            chunk_text="Text",
            source_file="pep8.md",
            relevance_score=1.5,
        )

    # Invalid score < 0.0
    with pytest.raises(ValidationError):
        Citation(
            document_title="PEP 8",
            chunk_text="Text",
            source_file="pep8.md",
            relevance_score=-0.1,
        )


# ---------------------------------------------------------------------------
# 3. RetrievalService Unit Tests (Mocked ChromaDB)
# ---------------------------------------------------------------------------


def test_retrieval_service_disabled_rag():
    settings = Settings(rag_enabled=False)
    service = RetrievalService(settings=settings)

    assert service.count() == 0
    citations = service.query("def insecure(): pass")
    assert citations == []


def test_retrieval_service_empty_query():
    settings = Settings(rag_enabled=True)
    service = RetrievalService(settings=settings)

    assert service.query("") == []
    assert service.query("   ") == []


def test_retrieval_service_empty_collection():
    settings = Settings(rag_enabled=True)
    service = RetrievalService(settings=settings)

    mock_collection = MagicMock()
    mock_collection.count.return_value = 0
    service._collection = mock_collection

    citations = service.query("find something")
    assert citations == []
    mock_collection.query.assert_not_called()


def test_retrieval_service_query_success_and_score_conversion():
    settings = Settings(rag_enabled=True, rag_n_results=2)
    service = RetrievalService(settings=settings)

    mock_collection = MagicMock()
    mock_collection.count.return_value = 10
    # Chroma returns cosine distance d in [0, 2]
    mock_collection.query.return_value = {
        "documents": [["Chunk 1 text", "Chunk 2 text"]],
        "metadatas": [[
            {
                "document_title": "OWASP Security",
                "source_file": "owasp.md",
                "source_url": "https://owasp.org",
                "section": "Command Injection",
            },
            {
                "document_title": "PEP 8",
                "source_file": "pep8.md",
                "source_url": "https://peps.python.org",
                "section": "Whitespace",
            },
        ]],
        "distances": [[0.25, 0.70]],  # cosine distances -> similarities 0.75, 0.30
    }
    service._collection = mock_collection

    results = service.query("os.system(cmd)")
    assert len(results) == 2

    assert results[0].document_title == "OWASP Security"
    assert results[0].chunk_text == "Chunk 1 text"
    assert results[0].relevance_score == 0.75
    assert results[0].section == "Command Injection"

    assert results[1].document_title == "PEP 8"
    assert results[1].relevance_score == 0.30


def test_retrieval_service_graceful_error_handling():
    settings = Settings(rag_enabled=True)
    service = RetrievalService(settings=settings)

    mock_collection = MagicMock()
    mock_collection.count.side_effect = RuntimeError("Chroma connection dropped")
    service._collection = mock_collection

    # Must not raise exception
    assert service.count() == 0
    assert service.query("some code") == []


# ---------------------------------------------------------------------------
# 4. Ingestion Idempotency & Duplicate Prevention Tests
# ---------------------------------------------------------------------------


def test_ingest_documents_mocked():
    """Verify ingest_documents parses files, splits text, and calls upsert with deterministic IDs."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 5
    mock_client.get_or_create_collection.return_value = mock_collection

    with (
        patch("app.rag.ingest.get_chroma_client", return_value=mock_client),
        patch("app.rag.ingest.get_embedding_function", return_value=MagicMock()),
    ):
        stats = ingest_documents(docs_dir=DOCUMENTS_DIR)

        assert stats.documents_scanned >= 3
        assert stats.chunks_created > 0
        assert stats.chunks_indexed == stats.chunks_created
        assert mock_collection.upsert.called

        call_kwargs = mock_collection.upsert.call_args.kwargs
        ids = call_kwargs["ids"]
        docs = call_kwargs["documents"]
        metas = call_kwargs["metadatas"]

        # All IDs must be unique within batch and deterministic SHA-256 strings
        assert len(ids) == len(set(ids))
        assert len(ids) == len(docs) == len(metas)
        assert all(len(cid) == 64 for cid in ids)


# ---------------------------------------------------------------------------
# 5. Citation Grounding & Review Orchestrator Tests
# ---------------------------------------------------------------------------


def test_ground_findings_with_matching_citations():
    """Orchestrator attaches matching retrieved citations to findings without fabricating data."""
    citations = [
        Citation(
            document_title="OWASP Python Security Cheat Sheet",
            chunk_text="Never pass unsanitized user input to os.system or subprocess.",
            source_file="owasp_python_security.md",
            source_url="https://cheatsheetseries.owasp.org",
            section="Command Injection",
            relevance_score=0.88,
        ),
        Citation(
            document_title="PEP 8 Style Guide for Python Code",
            chunk_text="Use 4 spaces per indentation level. Limit lines to 79 chars.",
            source_file="pep8_style_guide.md",
            source_url="https://peps.python.org/pep-0008/",
            section="Indentation",
            relevance_score=0.72,
        ),
    ]

    findings = [
        Finding(
            id="f-sec-1",
            source=FindingSource.llm,
            severity=Severity.high,
            category=Category.security,
            title="Command injection via os.system",
            explanation="Untrusted user input passed into os.system ping command.",
            evidence="os.system(user_ip)",
            verification_status=VerificationStatus.unverified,
        ),
        Finding(
            id="f-style-1",
            source=FindingSource.llm,
            severity=Severity.low,
            category=Category.style,
            title="Line exceeds 79 characters",
            explanation="Code formatting style violation on line 10.",
            evidence=None,
            verification_status=VerificationStatus.unverified,
        ),
    ]

    orchestrator = ReviewOrchestrator(settings=Settings())
    orchestrator._ground_findings_with_citations(findings, citations)

    # Security finding should match the OWASP citation
    assert len(findings[0].citations) >= 1
    assert findings[0].citations[0].document_title == "OWASP Python Security Cheat Sheet"
    assert findings[0].citations[0].section == "Command Injection"

    # Style finding should match the PEP 8 citation
    assert len(findings[1].citations) >= 1
    assert findings[1].citations[0].document_title == "PEP 8 Style Guide for Python Code"


def test_orchestrator_sets_rag_context_retrieved():
    """Verify ReviewResponse reflects whether RAG context was retrieved."""
    mock_retrieval = MagicMock()
    mock_retrieval.query.return_value = [
        Citation(
            document_title="PEP 8",
            chunk_text="Indentation guideline",
            source_file="pep8.md",
            relevance_score=0.9,
        )
    ]

    mock_llm = MagicMock()
    mock_llm.review_code.return_value = ("Test summary", [])

    settings = Settings(rag_enabled=True)
    orchestrator = ReviewOrchestrator(
        settings=settings,
        llm_provider=mock_llm,
        retrieval_service=mock_retrieval,
    )

    req = ReviewRequest(code="def foo():\n    pass\n", language="python")
    resp = orchestrator.run_review(req)

    assert resp.rag_context_retrieved is True
    assert mock_retrieval.query.called


def test_orchestrator_rag_disabled_flag():
    """When rag_enabled is False, retrieval is bypassed and flag is False."""
    mock_retrieval = MagicMock()
    mock_llm = MagicMock()
    mock_llm.review_code.return_value = ("Clean code", [])

    settings = Settings(rag_enabled=False)
    orchestrator = ReviewOrchestrator(
        settings=settings,
        llm_provider=mock_llm,
        retrieval_service=mock_retrieval,
    )

    req = ReviewRequest(code="x = 1\n", language="python")
    resp = orchestrator.run_review(req)

    assert resp.rag_context_retrieved is False
    assert not mock_retrieval.query.called


# ---------------------------------------------------------------------------
# 6. Live ChromaDB Integration (Local Persistent Store)
# ---------------------------------------------------------------------------


def test_live_retrieval_against_indexed_chroma():
    """End-to-end test against the actual local ChromaDB index created during Phase 3."""
    settings = Settings(rag_enabled=True, chroma_persist_dir="./chroma_data")
    service = RetrievalService(settings=settings)

    if service.count() == 0:
        pytest.skip("ChromaDB local store not yet populated.")

    # 1. Query for security issue
    sec_citations = service.query("subprocess.Popen(cmd, shell=True) and os.system()")
    assert len(sec_citations) > 0
    top_sec = sec_citations[0]
    assert "Security" in top_sec.document_title or "OWASP" in top_sec.document_title
    assert 0.0 <= top_sec.relevance_score <= 1.0

    # 2. Query for mutable default argument
    defensive_citations = service.query("def add_item(item, list_arg=[]):")
    assert len(defensive_citations) > 0
    top_def = defensive_citations[0]
    assert "Defensive" in top_def.document_title or "Robustness" in top_def.document_title
    assert 0.0 <= top_def.relevance_score <= 1.0
