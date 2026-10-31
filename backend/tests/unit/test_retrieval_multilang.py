"""Unit tests for multi-language RAG retrieval in CodeSage AI."""

from pathlib import Path
import pytest
from app.config import Settings
from app.services.retrieval import RetrievalService


@pytest.fixture
def retrieval_service():
    target_dir = Path("chroma_data")
    if not target_dir.exists():
        target_dir = Path("backend/chroma_data")
    settings = Settings(
        rag_enabled=True,
        chroma_persist_dir=str(target_dir),
        chroma_collection_name="coding_guidelines",
    )
    return RetrievalService(settings=settings)


def test_retrieval_service_has_indexed_multilang_chunks(retrieval_service):
    count = retrieval_service.count()
    assert count >= 70, f"Expected at least 70 chunks across 11 documents, got {count}"


def test_retrieval_for_java_prefers_java_guidelines(retrieval_service):
    citations = retrieval_service.query(
        query_text="PreparedStatement SQL injection and NullPointerException",
        n_results=3,
        language="java",
    )
    assert len(citations) > 0
    # At least one citation should be from Java guidelines
    java_citations = [c for c in citations if "java" in c.source_file.lower() or "java" in c.document_title.lower()]
    assert len(java_citations) > 0, f"Expected Java citations, got {[c.source_file for c in citations]}"


def test_retrieval_for_c_prefers_c_guidelines(retrieval_service):
    citations = retrieval_service.query(
        query_text="strcpy buffer overflow bounds checking snprintf malloc free",
        n_results=3,
        language="c",
    )
    assert len(citations) > 0
    c_citations = [c for c in citations if "c_" in c.source_file.lower() or "iso c" in c.document_title.lower()]
    assert len(c_citations) > 0, f"Expected C citations, got {[c.source_file for c in citations]}"


def test_retrieval_for_sql_prefers_sql_guidelines(retrieval_service):
    citations = retrieval_service.query(
        query_text="SQL injection parameterized queries prepared statements transaction ACID",
        n_results=3,
        language="sql",
    )
    assert len(citations) > 0
    sql_citations = [c for c in citations if "sql" in c.source_file.lower() or "sql" in c.document_title.lower()]
    assert len(sql_citations) > 0, f"Expected SQL citations, got {[c.source_file for c in citations]}"


def test_retrieval_for_python_prefers_python_guidelines(retrieval_service):
    citations = retrieval_service.query(
        query_text="PEP 8 naming convention mutable default arguments subprocess shell injection",
        n_results=3,
        language="python",
    )
    assert len(citations) > 0
    py_citations = [c for c in citations if "python" in c.source_file.lower() or "pep8" in c.source_file.lower()]
    assert len(py_citations) > 0, f"Expected Python citations, got {[c.source_file for c in citations]}"
