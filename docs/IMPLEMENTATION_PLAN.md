# CodeSage AI — Implementation Plan

_Last updated: Phase 0 (2026-10-30)_

---

## Overview

The project is built in 7 phases. Each phase produces working, tested, committed code. No phase leaves the repository in a broken state. Phases are ordered by dependency: later phases build on earlier ones.

```
Phase 0  → Architecture & planning (this document)
Phase 1  → Backend skeleton + config + health endpoints
Phase 2  → Static analysis service (Ruff + Bandit)
Phase 3  → LLM provider + review orchestrator (no RAG yet)
Phase 4  → RAG: ChromaDB ingestion + retrieval service
Phase 5  → MongoDB persistence + history endpoints
Phase 6  → Frontend: full React application
Phase 7  → Docker Compose, README, final integration tests
```

---

## Phase 0 — Architecture & Planning

**Goal:** Establish all design documents; no code written.

**Deliverables:**
- `docs/ARCHITECTURE.md`
- `docs/API_CONTRACTS.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/DECISIONS.md`
- `docs/PROGRESS.md`

**Acceptance Criteria:**
- [x] Repository structure defined.
- [x] Finding model defined with all fields, enums, and constraints.
- [x] All 6 API endpoints documented with request/response schemas and error codes.
- [x] All environment variables listed with defaults.
- [x] Security boundaries articulated.
- [x] MongoDB and ChromaDB schemas defined.
- [x] Test strategy defined per layer.
- [x] Phase dependencies identified.
- [x] No contradictions between docs.

**Owner:** Architect
**Dependencies:** None

---

## Phase 1 — Backend Skeleton

**Goal:** Working FastAPI app with config, CORS, lifespan startup, health and readiness endpoints, project structure, and CI-ready test setup. No business logic yet.

**Deliverables:**
- `backend/pyproject.toml` (with Ruff + Pytest config)
- `backend/requirements.txt` and `requirements-dev.txt`
- `backend/.env.example`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/api/v1/health.py` — `/api/v1/health`, `/api/v1/ready`
- `backend/app/api/v1/capabilities.py` — `/api/v1/capabilities`
- `backend/app/schemas/common.py`, `finding.py`, `review.py`
- `backend/tests/api/test_health.py`

**Acceptance Criteria:**
- [x] `uvicorn app.main:app` starts without errors.
- [x] `GET /api/v1/health` → `200 {"status": "ok", "version": "0.1.0"}`.
- [x] `GET /api/v1/ready` → `200` when MongoDB is reachable, `503` when not.
- [x] `GET /api/v1/capabilities` → correct static response.
- [x] All Pydantic schemas (`Finding`, `ReviewRequest`, `ReviewResponse`, etc.) parse without error.
- [x] `pytest tests/api/test_health.py` passes (uses TestClient; no real DB needed).
- [x] `ruff check app/` reports zero issues.
- [x] `mypy app/` (or `pyright`) passes (strict optional checks).
- [x] `.env.example` present; no actual secrets in any committed file.

**Owner:** Backend
**Dependencies:** Phase 0

---

## Phase 2 — Static Analysis Service

**Goal:** Implement the static analysis service (Ruff + Bandit). The `/api/v1/reviews` endpoint becomes callable but returns only static-analysis findings (no LLM yet).

**Deliverables:**
- `backend/app/services/static_analysis.py`
- `backend/app/api/v1/reviews.py` (POST only; calls static analysis + returns stub ReviewResponse)
- `backend/app/services/orchestrator.py` (partial: wires static analysis only)
- `backend/tests/unit/test_static_analysis.py`
- `backend/tests/api/test_reviews.py` (static analysis path only)

**Acceptance Criteria:**
- [ ] `POST /api/v1/reviews` with valid Python code returns `200` with findings from Ruff and Bandit.
- [ ] `POST /api/v1/reviews` with code > 32 KB returns `413`.
- [ ] `POST /api/v1/reviews` with `language != "python"` returns `422`.
- [ ] Finding `source` is `"ruff"` or `"bandit"`; `verification_status` is `"deterministic"`.
- [ ] `rule_id` is non-null for all static-analysis findings.
- [ ] Submitted code is never persisted in full (only first 500 chars in snippet).
- [ ] Temp file for static analysis is deleted after each run.
- [ ] Unit tests cover: clean code (zero findings), code with style issues (Ruff), code with security issues (Bandit), tool subprocess failure (empty list returned, no crash).
- [ ] `pytest tests/unit/test_static_analysis.py tests/api/test_reviews.py` all pass.

**Owner:** Backend
**Dependencies:** Phase 1

---

## Phase 3 — LLM Provider + Full Orchestrator

**Goal:** Integrate Gemini. The review endpoint now returns LLM findings merged with static-analysis findings, plus a summary. RAG context is empty at this stage.

**Deliverables:**
- `backend/app/services/llm_provider.py`
- `backend/app/services/orchestrator.py` (full: LLM + static analysis; RAG stub returns empty)
- `backend/tests/unit/test_llm_provider.py`
- `backend/tests/integration/test_review_flow.py` (LLM mocked; Ruff/Bandit real)

**Acceptance Criteria:**
- [ ] `POST /api/v1/reviews` returns both LLM findings (`source="llm"`) and static findings.
- [ ] LLM findings have `verification_status="unverified"`.
- [ ] Static findings have `verification_status="deterministic"`.
- [ ] `summary` field is populated from LLM output.
- [ ] If Gemini returns invalid JSON, endpoint still returns `200` with static findings only; no 500.
- [ ] If Gemini times out (after configured timeout), endpoint returns `200` with static findings only.
- [ ] `rag_context_retrieved` is `false` in this phase.
- [ ] LLM unit tests mock the Gemini SDK; no real API calls in unit/API tests.
- [ ] `pytest tests/unit/test_llm_provider.py tests/integration/test_review_flow.py` all pass.
- [ ] `GEMINI_API_KEY` is never logged or included in any response.

**Owner:** Backend
**Dependencies:** Phase 2

---

## Phase 4 — RAG: Ingestion + Retrieval

**Goal:** Implement ChromaDB ingestion and retrieval. At least 3 real coding-guideline documents are chunked, embedded, and indexed. The review endpoint returns citations.

**Deliverables:**
- `backend/app/rag/ingest.py`
- `backend/app/rag/documents/` — minimum 3 Markdown guideline documents (e.g. PEP 8 excerpts, OWASP Top 10 Python notes, Python best practices)
- `backend/app/services/retrieval.py`
- `backend/app/services/orchestrator.py` (full: includes RAG)
- `backend/tests/unit/test_retrieval.py`

**Acceptance Criteria:**
- [ ] `python -m app.rag.ingest` completes without error and prints chunk count.
- [ ] Running ingest twice does not create duplicate chunks (idempotent via content-hash IDs).
- [ ] `POST /api/v1/reviews` with code related to a guideline document returns at least one citation.
- [ ] `rag_context_retrieved` is `true` when at least one chunk was retrieved.
- [ ] Citations include `document_title`, `chunk_text`, `source_file`, `relevance_score`.
- [ ] `relevance_score` is a float between 0 and 1.
- [ ] `GET /api/v1/capabilities` returns correct `rag_enabled: true` and `rag_document_count`.
- [ ] If ChromaDB collection is empty, retrieval returns `[]`; no crash.
- [ ] Unit tests for retrieval mock ChromaDB; test both populated and empty collection.
- [ ] `pytest tests/unit/test_retrieval.py` all pass.

**Owner:** Backend
**Dependencies:** Phase 3

---

## Phase 5 — MongoDB Persistence + History

**Goal:** All completed reviews are persisted to MongoDB. History and detail endpoints are fully functional.

**Deliverables:**
- `backend/app/services/persistence.py`
- `backend/app/api/v1/reviews.py` (GET /{id} endpoint added)
- `backend/app/api/v1/history.py`
- `backend/app/services/orchestrator.py` (saves review to MongoDB after completion)
- `backend/tests/unit/` — persistence tests (mock PyMongo)
- `backend/tests/api/test_history.py`

**Acceptance Criteria:**
- [ ] After `POST /api/v1/reviews`, the review is retrievable via `GET /api/v1/reviews/{id}`.
- [ ] `GET /api/v1/history` returns paginated list sorted by `submitted_at` descending.
- [ ] `page` and `page_size` query params work correctly; out-of-range page returns empty `items`.
- [ ] `GET /api/v1/reviews/{nonexistent-id}` returns `404` with `REVIEW_NOT_FOUND`.
- [ ] History items include `finding_counts` pre-computed correctly.
- [ ] `code_snippet` in history items is max 500 chars of the submitted code.
- [ ] Full submitted code is **not** stored in MongoDB.
- [ ] MongoDB connection failure at startup logs an error and health/ready reflect it.
- [ ] `pytest tests/api/test_history.py` and persistence unit tests all pass.

**Owner:** Backend
**Dependencies:** Phase 4

---

## Phase 6 — Frontend

**Goal:** Complete, polished React frontend connected to the real backend API.

**Deliverables:**
- `frontend/` — full Vite + React + TypeScript + Tailwind project.
- All 4 routes implemented: Landing, Review, History, ReviewDetail.
- All components from the architecture: CodeEditor, FindingsPanel, FindingCard, SeverityFilter, DiffViewer, CitationList, Navbar, Footer, UI primitives.
- `frontend/src/api/client.ts` — typed API client.
- `frontend/src/types/review.ts` — TypeScript mirrors.
- `frontend/tests/` — component and page tests.

**Acceptance Criteria:**
- [ ] `pnpm dev` starts without errors; app loads at `localhost:5173`.
- [ ] `pnpm build` succeeds with zero TypeScript errors.
- [ ] `pnpm test` (Vitest) passes; coverage includes `FindingCard`, `SeverityFilter`, `ReviewPage`.
- [ ] `tsc --noEmit` passes.
- [ ] Landing page has a working CTA linking to `/review`.
- [ ] Monaco Editor loads Python code with syntax highlighting.
- [ ] Submit button is disabled while a review is in-flight; spinner is shown.
- [ ] Findings render after response; severity filter correctly hides/shows findings.
- [ ] Static-analysis findings are visually distinguished from LLM findings (badge or label).
- [ ] `verification_status` is displayed on each finding card.
- [ ] Citations are shown with document title, chunk snippet, and relevance score.
- [ ] DiffViewer shows original vs. suggested patch side-by-side when `patch` is non-null.
- [ ] History page shows paginated list; clicking a row navigates to detail.
- [ ] ReviewDetailPage shows full findings, not just summary.
- [ ] Loading, error, and empty states are implemented for every data-fetching component.
- [ ] No API key or secret is present in any frontend file or build output.
- [ ] Design is dark-first with violet/blue accents; no placeholder copy or fake data.

**Owner:** Frontend
**Dependencies:** Phase 5 (for real API endpoints)

---

## Phase 7 — Docker, README, Final Integration

**Goal:** Docker Compose works end-to-end. README is complete. Final integration tests pass.

**Deliverables:**
- `docker-compose.yml` (production-mode)
- `docker-compose.dev.yml` (dev-mode override)
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `README.md` — full setup, architecture, limitations
- `backend/tests/integration/test_review_flow.py` — full integration (real DB, real tools, LLM mocked)

**Acceptance Criteria:**
- [ ] `docker compose up --build` starts all three services (frontend, backend, mongodb).
- [ ] Frontend container serves the built React app at port 80.
- [ ] Backend container starts, connects to MongoDB, and responds to health checks.
- [ ] `docker compose exec backend python -m app.rag.ingest` works after startup.
- [ ] End-to-end: submit code via browser → review appears in history.
- [ ] `docker compose down -v` cleans up without error.
- [ ] README covers: prerequisites, `.env` setup, local dev commands, Docker commands, architecture summary, known limitations.
- [ ] No `.env` or secret files are committed; `.gitignore` covers them.
- [ ] `pytest -m integration` (with real MongoDB) all pass.

**Owner:** DevOps / Full-stack
**Dependencies:** Phase 6

---

## Phase Dependency Graph

```
Phase 0 (Docs)
    └── Phase 1 (Backend Skeleton)
            └── Phase 2 (Static Analysis)
                    └── Phase 3 (LLM + Orchestrator)
                            └── Phase 4 (RAG)
                                    └── Phase 5 (Persistence)
                                            ├── Phase 6 (Frontend)
                                            └── Phase 7 (Docker + README)
                                                        ↑
                                                  Phase 6 also feeds here
```

---

## Risk Register

| Risk                                          | Likelihood | Impact | Mitigation                                                      |
|-----------------------------------------------|------------|--------|-----------------------------------------------------------------|
| Gemini API key quota / rate limit             | Medium     | High   | Use `gemini-1.5-flash` (cheaper); mock in all non-integration tests |
| ChromaDB cold-start model download            | Low        | Medium | Document in README; pre-download in Dockerfile                  |
| Ruff/Bandit subprocess failure on Windows     | Medium     | Medium | Wrap in try/except; return empty list; add Windows CI note      |
| MongoDB connection refused in dev             | Medium     | Medium | Clear error message; ready endpoint reflects state              |
| LLM hallucinated line numbers                 | High       | Low    | `verification_status="unverified"` displayed in UI; never block on it |
| Large code submissions degrading performance  | Low        | Medium | 32 KB input limit enforced at API layer                         |

---

_This plan is authoritative. Add new tasks to the appropriate phase or create a new phase, then update `PROGRESS.md`._
