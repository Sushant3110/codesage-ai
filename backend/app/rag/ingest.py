"""Document ingestion for CodeSage AI RAG pipeline.

Loads approved Python coding and security guidelines from the local curated
documents directory, chunks them with LangChain's RecursiveCharacterTextSplitter,
computes deterministic chunk hashes, and upserts them into persistent ChromaDB
with full provenance metadata.

Run from backend root:
    python -m app.rag.ingest
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from typing import Any, Mapping, cast

# Disable ChromaDB telemetry and default to offline hub if cached
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings

logger = logging.getLogger(__name__)

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"


@dataclass
class DocumentMetadata:
    title: str
    source_url: str
    source_file: str
    content_hash: str
    language: str = "general"


@dataclass
class IngestionStats:
    documents_scanned: int
    chunks_created: int
    chunks_indexed: int
    collection_total: int


def parse_markdown_metadata(content: str, filename: str) -> tuple[DocumentMetadata, list[tuple[str, str]]]:
    """Parse title, source URL, language, and section blocks from a guideline Markdown file.

    Returns:
        (DocumentMetadata, list of (section_name, section_text) tuples)
    """
    lines = content.splitlines()
    title = filename
    source_url = ""
    language = "general"
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # Heuristic inference from filename if not specified in headers
    lower_fn = filename.lower()
    if any(prefix in lower_fn for prefix in ("python", "pep8", "owasp_python")):
        language = "python"
    elif "java" in lower_fn and "javascript" not in lower_fn:
        language = "java"
    elif "javascript" in lower_fn:
        language = "javascript"
    elif "typescript" in lower_fn:
        language = "typescript"
    elif "cpp" in lower_fn or "cplusplus" in lower_fn:
        language = "cpp"
    elif lower_fn.startswith("c_") or "_c_" in lower_fn:
        language = "c"
    elif "html" in lower_fn:
        language = "html"
    elif "css" in lower_fn:
        language = "css"
    elif "sql" in lower_fn:
        language = "sql"

    # Extract title, source URL, and language from front lines
    remaining_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Source URL:"):
            source_url = stripped.removeprefix("Source URL:").strip()
        elif stripped.startswith("Document Title:"):
            title = stripped.removeprefix("Document Title:").strip()
        elif stripped.startswith("Language:"):
            language = stripped.removeprefix("Language:").strip().lower()
        elif stripped.startswith("# ") and title == filename:
            title = stripped.removeprefix("# ").strip()
        else:
            remaining_lines.append(line)

    # Split into sections based on ## or ### markdown headings
    sections: list[tuple[str, str]] = []
    current_section = "General"
    current_lines: list[str] = []

    for line in remaining_lines:
        if line.startswith("## ") or line.startswith("### "):
            if current_lines:
                sec_text = "\n".join(current_lines).strip()
                if sec_text:
                    sections.append((current_section, sec_text))
                current_lines = []
            current_section = line.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sec_text = "\n".join(current_lines).strip()
        if sec_text:
            sections.append((current_section, sec_text))

    doc_meta = DocumentMetadata(
        title=title,
        source_url=source_url,
        source_file=filename,
        content_hash=content_hash,
        language=language,
    )
    return doc_meta, sections


def get_chroma_client(persist_dir: Path | str | None = None) -> chromadb.ClientAPI:
    """Initialize a persistent ChromaDB client."""
    settings = get_settings()
    path_str = str(persist_dir or settings.chroma_persist_dir)
    Path(path_str).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=path_str,
        settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True),
    )


def get_embedding_function(model_name: str | None = None) -> Any:
    """Return the shared SentenceTransformer embedding function."""
    import chromadb.utils.embedding_functions as ef

    settings = get_settings()
    model = model_name or settings.embedding_model
    st_cls = getattr(ef, "SentenceTransformerEmbeddingFunction")
    return st_cls(model_name=model)


def ingest_documents(
    docs_dir: Path | None = None,
    persist_dir: Path | None = None,
    clean: bool = False,
) -> IngestionStats:
    """Ingest all approved guideline documents into ChromaDB.

    Uses deterministic chunk IDs and collection.upsert to guarantee idempotency.
    """
    settings = get_settings()
    target_dir = docs_dir or DOCUMENTS_DIR
    if not target_dir.exists():
        logger.warning("Documents directory not found: %s", target_dir)
        return IngestionStats(0, 0, 0, 0)

    client = get_chroma_client(persist_dir)
    emb_fn = get_embedding_function()

    if clean:
        try:
            client.delete_collection(name=settings.chroma_collection_name)
            logger.info("Deleted existing collection '%s'", settings.chroma_collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"},
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    doc_files = sorted(target_dir.glob("*.md"))
    if not doc_files:
        logger.warning("No markdown files found in %s", target_dir)
        return IngestionStats(0, 0, 0, collection.count())

    total_chunks = 0
    all_ids: list[str] = []
    all_texts: list[str] = []
    all_metadatas: list[Mapping[str, str | int | float | bool]] = []

    for file_path in doc_files:
        content = file_path.read_text(encoding="utf-8")
        meta, sections = parse_markdown_metadata(content, file_path.name)

        chunk_idx = 0
        for section_name, section_text in sections:
            chunks = splitter.split_text(section_text)
            for c in chunks:
                chunk_str = c.strip()
                if not chunk_str:
                    continue

                chunk_content_hash = hashlib.sha256(chunk_str.encode("utf-8")).hexdigest()
                # Deterministic ID combining source_file, chunk index, and content hash
                chunk_id = hashlib.sha256(
                    f"{meta.source_file}:{chunk_idx}:{chunk_content_hash}".encode()
                ).hexdigest()

                all_ids.append(chunk_id)
                all_texts.append(chunk_str)
                all_metadatas.append({
                    "document_title": meta.title,
                    "source_file": meta.source_file,
                    "source_url": meta.source_url,
                    "section": section_name,
                    "language": meta.language,
                    "chunk_index": chunk_idx,
                    "content_hash": chunk_content_hash,
                })
                chunk_idx += 1
                total_chunks += 1

    if all_ids:
        # ChromaDB supports upsert — updates existing IDs and adds new ones
        collection.upsert(
            ids=all_ids,
            documents=all_texts,
            metadatas=all_metadatas,
        )
        logger.info(
            "Indexed %d chunks across %d documents into '%s'",
            len(all_ids),
            len(doc_files),
            settings.chroma_collection_name,
        )

    final_count = collection.count()
    return IngestionStats(
        documents_scanned=len(doc_files),
        chunks_created=total_chunks,
        chunks_indexed=len(all_ids),
        collection_total=final_count,
    )


def main() -> None:
    """CLI entrypoint for guideline ingestion."""
    parser = argparse.ArgumentParser(description="Ingest coding guidelines into ChromaDB.")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=DOCUMENTS_DIR,
        help="Path to directory containing guideline markdown documents",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing collection before reindexing",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print(f"Ingesting guidelines from: {args.docs_dir.resolve()}")
    stats = ingest_documents(docs_dir=args.docs_dir, clean=args.clean)
    print("Ingestion complete:")
    print(f"  Documents scanned : {stats.documents_scanned}")
    print(f"  Chunks created    : {stats.chunks_created}")
    print(f"  Chunks indexed    : {stats.chunks_indexed}")
    print(f"  Collection total  : {stats.collection_total}")


if __name__ == "__main__":
    main()
