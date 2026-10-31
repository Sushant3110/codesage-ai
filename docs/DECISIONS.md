# CodeSage AI — Architecture & Design Decisions

_Last updated: Phase 0 (2026-10-30)_

---

## DEC-001 — Single LLM Provider: Google Gemini Only

**Decision:** The backend supports only the Google Gemini API as its LLM provider.

**Rationale:** AGENTS.md §3 mandates Gemini. Adding a provider abstraction layer beyond a single class (`GeminiProvider`) would add complexity without benefit in scope. The class is named `GeminiProvider` (not an abstract `LLMProvider`) to avoid over-engineering a feature not required.

**Consequence:** If a future phase adds a second provider, a `BaseLLMProvider` abstract class should be introduced and `GeminiProvider` should inherit from it. Document in this file when that happens.

**Date:** 2026-10-30

---

## DEC-002 — Full Submitted Code Not Persisted to MongoDB

**Decision:** MongoDB stores only the first 500 characters of submitted code (`code_snippet`) plus a SHA-256 hash (`code_hash`). The full code is not stored.

**Rationale:** Storing full user code raises privacy and storage concerns disproportionate to the portfolio use case. The code is processed in memory during a review and is not needed for history retrieval. The hash allows deduplication detection if needed later.

**Consequence:** `GET /api/v1/reviews/{id}` returns the full `ReviewResponse` with all findings but without the original code. The frontend does not display the original code in the detail view. If full-code retrieval is added in future, this decision must be revisited and the schema updated.

**Date:** 2026-10-30

---

## DEC-003 — Synchronous Review Endpoint (No Background Tasks)

**Decision:** `POST /api/v1/reviews` is a synchronous FastAPI endpoint. The review runs end-to-end within the HTTP request lifetime (up to 60 s LLM timeout + static analysis time).

**Rationale:** Background task queues (Celery, ARQ, etc.) add significant operational complexity. For a portfolio demo with low concurrency, synchronous execution with a clear loading state in the UI is sufficient. FastAPI's `async def` + `asyncio.gather` for parallelising static analysis and RAG retrieval mitigates latency.

**Consequence:** Under concurrent load, requests queue inside the event loop. This is a known limitation documented in README. If the project moves to production with real users, a task queue should be added.

**Date:** 2026-10-30

---

## DEC-004 — sentence-transformers Embedding (Local, No External Call)

**Decision:** RAG embeddings use `all-MiniLM-L6-v2` via the `sentence-transformers` library running locally in the backend process.

**Rationale:** Avoids a second external API dependency, reduces latency, has no per-call cost, and the model is small enough (~90 MB) for a development machine. LangChain's `HuggingFaceEmbeddings` wrapper is used so the embedding backend can be swapped later.

**Consequence:** First-run model download (~90 MB) must be documented. In Docker, the model should be downloaded during image build (`RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`) to avoid cold-start delay.

**Date:** 2026-10-30

---

## DEC-005 — Pydantic v2 Throughout

**Decision:** Backend uses Pydantic v2 exclusively. `model_validator`, `field_validator`, and `model_config` use the v2 API.

**Rationale:** AGENTS.md §3 mandates Pydantic v2. FastAPI ≥0.100 supports Pydantic v2 natively.

**Consequence:** Pydantic v1 compatibility shims are not used. Any LangChain dependency version that requires Pydantic v1 compatibility must be pinned carefully (LangChain ≥0.1 supports Pydantic v2).

**Date:** 2026-10-30

---

## DEC-006 — No Authentication in Scope

**Decision:** No user authentication or session management is implemented. The API is open.

**Rationale:** AGENTS.md §5 does not list authentication as a requirement. Adding auth (JWT, OAuth) would consume significant time and is not required for a portfolio demo.

**Consequence:** The application is not suitable for public deployment without auth. This is documented as a limitation in README. CORS origins are restricted as a partial mitigation.

**Date:** 2026-10-30

---

## DEC-007 — Static Analysis via Subprocess (Not Python Library API)

**Decision:** Ruff and Bandit are invoked as subprocesses (`subprocess.run(["ruff", "check", "--output-format", "json", tmpfile])`), not via their Python library APIs.

**Rationale:** Both tools expose a stable, well-documented JSON CLI output format. Using the CLI avoids coupling to internal library APIs that may change across versions. The subprocess approach also clearly enforces that submitted code is never `import`ed or `exec`-ed.

**Consequence:** Ruff and Bandit must be installed in the same Python environment as the backend. They are listed in `requirements.txt` (not `requirements-dev.txt`) because they are needed at runtime. The temp file must be cleaned up in a `finally` block.

**Date:** 2026-10-30

---

## DEC-008 — ChromaDB Persistence Directory (Not Client-Server Mode)

**Decision:** ChromaDB runs in embedded persistent mode (`chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)`), not in client-server mode.

**Rationale:** Running ChromaDB as a separate service (its HTTP server) adds Docker complexity for no benefit at this scale. The embedded persistent client stores data to disk and is fully functional for a single-backend-process setup.

**Consequence:** ChromaDB storage is co-located with the backend process. In Docker, the `CHROMA_PERSIST_DIR` must be a mounted volume so data persists across container restarts. Multiple backend replicas cannot share the same ChromaDB instance in this mode — a known limitation for scale-out.

**Date:** 2026-10-30

---

## DEC-009 — Finding IDs Are UUIDs Generated at Review Time

**Decision:** Each finding in a review gets a UUID generated at the time the review is created. These IDs are stable within a review but are not globally unique across reviews (the same Ruff rule firing on the same line in two reviews produces two different finding IDs).

**Rationale:** Finding IDs are needed for React `key` props and future deep-linking. Global deduplication is not a current requirement.

**Consequence:** No deduplication logic is needed. Finding IDs should not be used for cross-review comparisons.

**Date:** 2026-10-30

---

## DEC-010 — Gemini Model Default: `gemini-1.5-flash`

**Decision:** The default Gemini model is `gemini-1.5-flash`.

**Rationale:** `flash` has a lower per-token cost and sufficient capability for structured code review output. `gemini-1.5-pro` could produce higher-quality explanations but would increase API cost and latency. The model is configurable via `GEMINI_MODEL` env var to allow easy switching.

**Consequence:** Review quality may be lower than with `pro`. Document as a configurable trade-off in README.

**Date:** 2026-10-30

---

## DEC-011 — React Router v6 with `createBrowserRouter`

**Decision:** Frontend routing uses React Router v6 with `createBrowserRouter` (data router API), not the legacy `<BrowserRouter>` component.

**Rationale:** `createBrowserRouter` is the recommended API in React Router v6.4+ and enables future use of loaders/actions if needed.

**Consequence:** The Vite dev server and Nginx config must serve `index.html` for all routes (SPA fallback). This is documented in the Nginx config and Vite config.

**Date:** 2026-10-30

---

## DEC-012 — No Automated Fix Execution

**Decision:** Suggested patches (the `patch` field) are displayed to the user in a diff viewer but are never automatically applied or executed.

**Rationale:** AGENTS.md §7 explicitly requires this. Automatically applying LLM-generated patches without user review is unsafe.

**Consequence:** The DiffViewer component is read-only. A "Copy patch" button may be added as a convenience. No "Apply fix" button exists.

**Date:** 2026-10-30

---

## DEC-013 — Multi-Language Support & Registry Architecture

**Decision:** CodeSage AI supports 9 programming and markup languages (`python`, `java`, `javascript`, `typescript`, `c`, `cpp`, `html`, `css`, `sql`) using a centralized Python backend registry (`app.core.languages`), dynamic language-tailored Gemini prompts, language-indexed ChromaDB RAG guidelines, and Monaco Editor syntax integration.

**Rationale:** Broadening review capabilities beyond Python makes CodeSage AI significantly more versatile and portfolio-ready, while maintaining Python-only backend implementation constraints and preserving existing Python endpoints and test coverage.

**Consequence:** All 9 languages are fully validated, prompt-isolated, and supported in the frontend workspace with syntax highlighting and auto-detection. Static analysis (Ruff, Bandit) continues to target Python code, while LLM + RAG semantic retrieval supports all languages.

**Date:** 2026-10-31

---

## Assumptions

1. The development machine has Python 3.11+, Node.js 20+, Docker, and internet access.
2. A valid Gemini API key is available to the developer.
3. MongoDB is available either via Docker or Atlas.
4. RAG guideline documents are curated locally; no unauthenticated external web scraping is performed.
5. The application runs as a single backend instance (no horizontal scaling).
6. Multi-language support covers Python, Java, JavaScript, TypeScript, C, C++, HTML, CSS, and SQL. Unsupported languages return a 422 VALIDATION_ERROR.

## Unresolved Issues

- **UI-001:** Whether to lazy-load Monaco Editor only when the ReviewPage is active (vs. eager load). Decision deferred to Phase 6 implementation.
- **UI-002:** Whether the history page should support search/filter by severity. Not in scope for MVP; deferred.
- **BE-001:** Whether to stream Gemini responses (Server-Sent Events) to reduce perceived latency. Not in scope for MVP given synchronous architecture (DEC-003). Deferred.
- **DOC-001:** Which specific documents to include in `app/rag/documents/`. Minimum 3 decided: PEP 8 excerpts, OWASP Top 10 Python notes, Python Anti-Patterns. Final selection happens in Phase 4.
