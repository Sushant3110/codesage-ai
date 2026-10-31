"""Retrieval service for CodeSage AI.

Provides semantic similarity search over indexed Python coding and security
guidelines using ChromaDB and SentenceTransformer embeddings.
Returns structured Citation objects with cosine similarity scores.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, cast

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from app.config import Settings, get_settings
from app.rag.ingest import get_chroma_client, get_embedding_function
from app.schemas.finding import Citation

if TYPE_CHECKING:
    import chromadb

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving guideline citations grounded in ChromaDB."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: chromadb.ClientAPI | None = None
        self._collection: chromadb.Collection | None = None

    def _get_collection(self) -> chromadb.Collection | None:
        """Lazily initialize and return the ChromaDB collection.

        Returns None if RAG is disabled or collection cannot be accessed.
        """
        if not self._settings.rag_enabled:
            return None

        if self._collection is not None:
            return self._collection

        try:
            self._client = get_chroma_client(self._settings.chroma_persist_dir)
            emb_fn = get_embedding_function(self._settings.embedding_model)
            self._collection = self._client.get_or_create_collection(
                name=self._settings.chroma_collection_name,
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"},
            )
            return self._collection
        except Exception as exc:
            logger.warning("Failed to initialize ChromaDB collection: %s", exc)
            return None

    def count(self) -> int:
        """Return the total number of indexed guideline chunks."""
        if not self._settings.rag_enabled:
            return 0
        try:
            col = self._get_collection()
            return col.count() if col is not None else 0
        except Exception as exc:
            logger.warning("Failed to count ChromaDB items: %s", exc)
            return 0

    def query(
        self,
        query_text: str,
        n_results: int | None = None,
        language: str | None = None,
    ) -> list[Citation]:
        """Query ChromaDB for relevant coding guidelines matching the query text.

        Args:
            query_text: Natural language or source code text to search against.
            n_results: Maximum number of citations to retrieve.
            language: Optional programming language to filter or prioritize guidelines.

        Returns:
            list[Citation]: Ranked list of grounded citations with relevance scores [0.0, 1.0].
            Returns an empty list if RAG is disabled, query is empty, or collection is empty.
        """
        if not self._settings.rag_enabled:
            return []

        clean_query = query_text.strip()
        if not clean_query:
            return []

        col = self._get_collection()
        if col is None:
            return []

        try:
            total_items = col.count()
            if total_items == 0:
                logger.debug("ChromaDB collection is empty; returning no citations.")
                return []

            k = min(n_results or self._settings.rag_n_results, total_items)
            results = None

            # Attempt language-specific retrieval if language is provided
            if language:
                lang_clean = language.strip().lower()
                try:
                    where_filter: dict[str, Any] = {
                        "$or": [
                            {"language": lang_clean},
                            {"language": "general"},
                        ]
                    }
                    filtered_res = col.query(
                        query_texts=[clean_query],
                        n_results=k,
                        where=where_filter,
                        include=cast(Any, ["documents", "metadatas", "distances"]),
                    )
                    raw_docs = filtered_res.get("documents")
                    if raw_docs and len(raw_docs) > 0 and len(raw_docs[0]) > 0:
                        results = filtered_res
                except Exception as filter_err:
                    logger.debug("Language-filtered ChromaDB query fallback: %s", filter_err)

            # Fallback to standard unfiltered query if language-specific returned no results
            if results is None:
                results = col.query(
                    query_texts=[clean_query],
                    n_results=k,
                    include=cast(Any, ["documents", "metadatas", "distances"]),
                )

            citations: list[Citation] = []
            raw_docs = results.get("documents")
            raw_metas = results.get("metadatas")
            raw_dists = results.get("distances")

            documents = raw_docs[0] if raw_docs and len(raw_docs) > 0 else []
            metadatas = raw_metas[0] if raw_metas and len(raw_metas) > 0 else []
            distances = raw_dists[0] if raw_dists and len(raw_dists) > 0 else []

            for doc_text, meta, distance in zip(documents, metadatas, distances, strict=False):
                # ChromaDB cosine distance: d in [0, 2], where 0 is exact match.
                # Convert to cosine similarity score in [0.0, 1.0]
                similarity = max(0.0, min(1.0, 1.0 - float(distance)))
                score = round(similarity, 4)

                meta_dict = meta if isinstance(meta, dict) else {}
                fallback_title = f"{language.capitalize() if language else 'Coding'} Guideline"
                citations.append(
                    Citation(
                        document_title=str(meta_dict.get("document_title", fallback_title)),
                        chunk_text=doc_text,
                        source_file=str(meta_dict.get("source_file", "guideline.md")),
                        source_url=str(meta_dict.get("source_url")) if meta_dict.get("source_url") else None,
                        section=str(meta_dict.get("section")) if meta_dict.get("section") else None,
                        relevance_score=score,
                    )
                )

            return citations
        except Exception as exc:
            logger.warning("RAG retrieval query failed gracefully: %s", exc)
            return []


_retrieval_service_instance: RetrievalService | None = None


def get_retrieval_service() -> RetrievalService:
    """Return the cached RetrievalService singleton."""
    global _retrieval_service_instance
    if _retrieval_service_instance is None:
        _retrieval_service_instance = RetrievalService()
    return _retrieval_service_instance
