"""Review orchestrator — coordinates all review services.

In this phase, it orchestrates RAG retrieval, invokes the LLM provider review workflow
with retrieved coding guidelines as untrusted reference material, grounds findings,
and compiles the structured ReviewResponse conforming to the API contract.
"""

from __future__ import annotations

import logging
import re
import uuid

from app.config import Settings, get_settings
from app.schemas.finding import SEVERITY_ORDER, Category, Citation, Finding
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.llm_provider import GeminiProvider
from app.services.retrieval import RetrievalService, get_retrieval_service

logger = logging.getLogger(__name__)


class ReviewOrchestrator:
    """Orchestrates code review execution across review components."""

    def __init__(
        self,
        settings: Settings | None = None,
        llm_provider: GeminiProvider | None = None,
        retrieval_service: RetrievalService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.llm_provider = llm_provider or GeminiProvider(settings=self.settings)
        self.retrieval_service = retrieval_service or get_retrieval_service()

    def run_review(self, request: ReviewRequest) -> ReviewResponse:
        """Execute a review run for submitted code.

        Returns a complete ReviewResponse conforming to the API contract.
        """
        logger.info(
            "Starting review run for %s code (length: %d chars)...",
            request.language,
            len(request.code),
        )

        # 1. Retrieve relevant guideline citations using RAG
        citations: list[Citation] = []
        if self.settings.rag_enabled:
            query_text = f"{request.code[:1000]}\n{request.context or ''}".strip()
            try:
                citations = self.retrieval_service.query(
                    query_text=query_text,
                    n_results=self.settings.rag_n_results,
                    language=request.language,
                )
                logger.info("RAG retrieved %d guideline citations for %s.", len(citations), request.language)
            except Exception as exc:
                logger.warning("RAG retrieval failed during review orchestration: %s", exc)
                citations = []

        # 2. Invoke LLM Provider with retrieved citations and language
        summary, findings = self.llm_provider.review_code(
            code=request.code,
            context=request.context,
            citations=citations,
            language=request.language,
        )

        # 3. Ground findings with genuine retrieved citations
        if citations and findings:
            self._ground_findings_with_citations(findings, citations)

        # 4. Sort findings by severity priority (critical -> info)
        sorted_findings = sorted(
            findings,
            key=lambda f: SEVERITY_ORDER.get(f.severity, 99),
        )

        # 5. Construct authoritative ReviewResponse
        review_id = str(uuid.uuid4())
        submitted_at = ReviewResponse.utcnow()
        code_hash = ReviewResponse.hash_code(request.code)

        response = ReviewResponse(
            id=review_id,
            submitted_at=submitted_at,
            code_hash=code_hash,
            language=request.language,
            summary=summary,
            findings=sorted_findings,
            static_analysis_ran=False,
            rag_context_retrieved=len(citations) > 0,
        )

        logger.info(
            "Completed review run %s: %d findings identified (rag_context=%s).",
            review_id,
            len(response.findings),
            response.rag_context_retrieved,
        )
        return response

    def _ground_findings_with_citations(
        self,
        findings: list[Finding],
        citations: list[Citation],
    ) -> None:
        """Ground findings with actual retrieved citations based on relevance.

        Never fabricates citations or URLs. Only attaches citations that were
        actually retrieved from the vector store.
        """
        for finding in findings:
            matched_citations: list[Citation] = []
            finding_text = f"{finding.title} {finding.explanation} {finding.evidence or ''}".lower()

            for cit in citations:
                cit_text = f"{cit.document_title} {cit.section or ''} {cit.chunk_text}".lower()

                # Check keyword or category alignment
                is_match = (
                    (
                        finding.category == Category.security
                        and any(
                            k in cit_text
                            for k in [
                                "security", "injection", "owasp", "sql", "command", "pickle", "secret",
                                "traversal", "xss", "buffer", "overflow", "memory", "leak", "pointer",
                                "sanitize", "sanitization", "parameterized", "deserialization", "cwe"
                            ]
                        )
                    )
                    or (
                        finding.category == Category.style
                        and any(
                            k in cit_text
                            for k in ["pep 8", "pep8", "style", "naming", "indent", "import", "line length", "convention", "formatting", "specificity"]
                        )
                    )
                    or (
                        finding.category in (Category.correctness, Category.maintainability)
                        and any(
                            k in cit_text
                            for k in [
                                "defensive", "mutable", "resource", "exception", "with statement", "lock",
                                "precondition", "null", "raii", "thread", "concurrency", "bounds", "cleanup"
                            ]
                        )
                    )
                )

                if not is_match:
                    # Token overlap check
                    words = set(re.findall(r"\b[a-z]{4,}\b", finding_text))
                    cit_words = set(re.findall(r"\b[a-z]{4,}\b", cit_text))
                    overlap = len(words & cit_words)
                    if overlap >= 3:
                        is_match = True

                if is_match and cit not in matched_citations:
                    matched_citations.append(cit)
                    if len(matched_citations) >= 2:
                        break

            # If no direct keyword match, but we have high-relevance citations,
            # attach the top citation if category generally matches
            if not matched_citations and citations:
                top_cit = citations[0]
                if top_cit.relevance_score >= 0.5:
                    matched_citations.append(top_cit)

            finding.citations = matched_citations
