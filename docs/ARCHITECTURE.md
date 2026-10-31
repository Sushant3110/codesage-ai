# CodeSage AI — Architecture

_Last updated: Phase 0 (2026-10-30)_

---

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser (React + TypeScript + Vite)                                │
│  Landing Page │ Review Workspace │ Review History │ Review Detail   │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTP/JSON  (CORS-restricted)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI Application  (Python 3.11+)                                │
│                                                                     │
│  ┌──────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ API Layer│  │ Review           │  │ Config / Env             │  │
│  │ (routers)│→ │ Orchestrator     │  │ (pydantic-settings)      │  │
│  └──────────┘  └────────┬─────────┘  └──────────────────────────┘  │
│                         │                                           │
│          ┌──────────────┼──────────────────┐                       │
│          ▼              ▼                  ▼                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ LLM Provider │ │ Static Anal. │ │ Retrieval    │               │
│  │ (Gemini)     │ │ (Ruff+Bandit)│ │ Service      │               │
│  └──────────────┘ └──────────────┘ └──────┬───────┘               │
│                                           │                        │
│                                    ┌──────▼───────┐               │
│                                    │  ChromaDB    │               │
│                                    │  (persistent)│               │
│                                    └──────────────┘               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Persistence Layer (PyMongo → MongoDB)                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                         │
             ┌───────────┴────────────┐
             ▼                        ▼
     ┌───────────────┐      ┌──────────────────┐
     │  MongoDB       │      │  Google Gemini   │
     │  (local/Atlas) │      │  API (external)  │
     └───────────────┘      └──────────────────┘
```

---

## 2. Repository Structure

```
Ai_Code_Review/
├── AGENTS.md                        # Permanent project specification
├── README.md                        # Setup, architecture, limitations
├── .env.example                     # Environment variable template (no secrets)
├── .gitignore
├── docker-compose.yml               # Full stack (backend + mongo + frontend)
├── docker-compose.dev.yml           # Dev override (hot-reload volumes)
│
├── docs/
│   ├── ARCHITECTURE.md              # This file
│   ├── API_CONTRACTS.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── DECISIONS.md
│   └── PROGRESS.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml               # Project metadata, tool config (Ruff, Pytest)
│   ├── requirements.txt             # Pinned production deps
│   ├── requirements-dev.txt         # Dev-only deps (pytest, httpx, etc.)
│   ├── .env.example                 # Backend-specific env template
│   │
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory, CORS, lifespan
│   │   ├── config.py                # pydantic-settings Settings class
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py              # Shared FastAPI dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── health.py        # GET /api/v1/health, /api/v1/ready
│   │   │       ├── reviews.py       # POST /api/v1/reviews, GET /api/v1/reviews/{id}
│   │   │       ├── history.py       # GET /api/v1/history
│   │   │       └── capabilities.py  # GET /api/v1/capabilities
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── review.py            # ReviewRequest, ReviewResponse, FindingModel
│   │   │   ├── finding.py           # Finding, Severity, Category, VerificationStatus
│   │   │   └── common.py            # PaginatedResponse, ErrorResponse
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py      # ReviewOrchestrator — coordinates all services
│   │   │   ├── llm_provider.py      # GeminiProvider — LLM calls, prompt building
│   │   │   ├── static_analysis.py   # run_ruff(), run_bandit() → List[Finding]
│   │   │   ├── retrieval.py         # RetrievalService — ChromaDB query → citations
│   │   │   └── persistence.py       # ReviewRepository — MongoDB CRUD
│   │   │
│   │   └── rag/
│   │       ├── __init__.py
│   │       ├── ingest.py            # CLI script: chunk, embed, upsert into ChromaDB
│   │       └── documents/           # Approved coding-guideline source documents
│   │           └── .gitkeep
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_static_analysis.py
│       │   ├── test_llm_provider.py
│       │   ├── test_retrieval.py
│       │   └── test_schemas.py
│       ├── api/
│       │   ├── test_health.py
│       │   ├── test_reviews.py
│       │   └── test_history.py
│       └── integration/
│           └── test_review_flow.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── .env.example                 # VITE_API_BASE_URL only
    │
    ├── public/
    │   └── favicon.svg
    │
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx                  # Router setup
    │   ├── index.css                # Tailwind base + custom tokens
    │   │
    │   ├── pages/
    │   │   ├── LandingPage.tsx
    │   │   ├── ReviewPage.tsx       # Editor + submit + live findings panel
    │   │   ├── HistoryPage.tsx      # Paginated review list
    │   │   └── ReviewDetailPage.tsx # Full detail for a past review
    │   │
    │   ├── components/
    │   │   ├── layout/
    │   │   │   ├── Navbar.tsx
    │   │   │   └── Footer.tsx
    │   │   ├── editor/
    │   │   │   └── CodeEditor.tsx   # Monaco wrapper
    │   │   ├── findings/
    │   │   │   ├── FindingsPanel.tsx
    │   │   │   ├── FindingCard.tsx
    │   │   │   ├── SeverityBadge.tsx
    │   │   │   ├── SeverityFilter.tsx
    │   │   │   └── DiffViewer.tsx   # Suggested-fix comparison
    │   │   ├── citations/
    │   │   │   └── CitationList.tsx
    │   │   └── ui/
    │   │       ├── Button.tsx
    │   │       ├── Spinner.tsx
    │   │       ├── EmptyState.tsx
    │   │       └── ErrorBanner.tsx
    │   │
    │   ├── hooks/
    │   │   ├── useReview.ts         # Submit code, poll/receive result
    │   │   └── useHistory.ts        # Paginated history fetch
    │   │
    │   ├── api/
    │   │   └── client.ts            # Typed fetch wrapper, base URL from env
    │   │
    │   ├── types/
    │   │   └── review.ts            # TypeScript mirrors of backend schemas
    │   │
    │   └── utils/
    │       └── severity.ts          # Severity → color / label helpers
    │
    └── tests/
        ├── setup.ts
        ├── components/
        │   ├── FindingCard.test.tsx
        │   └── SeverityFilter.test.tsx
        └── pages/
            └── ReviewPage.test.tsx
```

---

## 3. Component Responsibilities

### 3.1 FastAPI Application (`app/main.py`)
- Constructs the FastAPI app instance.
- Registers CORS middleware (allowed origins from config).
- Mounts API v1 router.
- Lifespan context: initialises MongoDB connection, ChromaDB client, and verifies Gemini API key on startup. Tears down cleanly on shutdown.
- Does **not** contain business logic.

### 3.2 Config (`app/config.py`)
- Single `Settings` class via `pydantic-settings`.
- Reads `.env` file + environment variables; never has defaults for secrets.
- Exposed as a module-level singleton via `get_settings()` (cached with `@lru_cache`).

### 3.3 API Layer (`app/api/v1/`)
- Pure FastAPI routers: validation, dependency injection, delegation to services.
- Returns Pydantic response models. Never calls MongoDB, ChromaDB, or Gemini directly.
- Error handling: re-raises `HTTPException` for client errors; converts service errors to 500.

### 3.4 Schemas (`app/schemas/`)
- Pydantic v2 models. Single source of truth for request/response shapes.
- Shared between API layer and services; services accept and return these models.
- Finding model is defined once in `finding.py` and imported everywhere.

### 3.5 Review Orchestrator (`app/services/orchestrator.py`)
- Entry point for all review logic. Called by the API layer.
- Runs static analysis synchronously in a thread pool executor (blocking subprocesses).
- Calls `RetrievalService` to build the RAG context.
- Calls `GeminiProvider` with code + static-analysis summary + RAG context.
- Merges LLM findings and static-analysis findings into a single list.
- Persists the completed review via `ReviewRepository`.
- Returns the full `ReviewResponse`.

### 3.6 LLM Provider (`app/services/llm_provider.py`)
- Wraps the Google Gemini API. Contains a `GeminiProvider` class.
- Builds prompts from templates; requests structured JSON output.
- Validates the JSON response against `List[Finding]` before returning it.
- Marks all returned findings with `source="llm"` and `verification_status="unverified"`.
- Applies timeout (configurable, default 60 s) and bounded retries (max 2).
- **Never** exposes the API key outside this module.

### 3.7 Static Analysis (`app/services/static_analysis.py`)
- Runs `ruff check --output-format json` and `bandit -f json` as subprocesses.
- **Never executes submitted code**; tools operate on the source text written to a temp file.
- Temp file is deleted after analysis regardless of success or failure.
- Normalises tool output into `List[Finding]` with `source="ruff"` or `source="bandit"`.
- Marks findings with `verification_status="deterministic"` (tool output is authoritative for syntax/AST issues).
- Returns empty list on tool failure; logs the error.

### 3.8 Retrieval Service (`app/services/retrieval.py`)
- Wraps ChromaDB; exposes `query(text: str, n_results: int) -> List[Citation]`.
- Embedding model: `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no external call).
- Returns citations with `document_title`, `chunk_text`, `source_file`, and `relevance_score`.
- Returns empty list if ChromaDB collection is empty (RAG is gracefully degraded).

### 3.9 Persistence (`app/services/persistence.py`)
- `ReviewRepository` wraps a PyMongo collection.
- Stores and retrieves `ReviewResponse` documents as BSON.
- Provides `save()`, `get_by_id()`, `list_paginated()`.
- MongoDB `_id` is stored as the review's stable UUID string (not ObjectId).

### 3.10 RAG Ingestion (`app/rag/ingest.py`)
- CLI script (`python -m app.rag.ingest`): reads markdown/text files from `app/rag/documents/`.
- Chunks with LangChain's `RecursiveCharacterTextSplitter` (chunk size 512, overlap 64 tokens).
- Embeds with `all-MiniLM-L6-v2` and upserts into ChromaDB collection `coding_guidelines`.
- Idempotent: re-running with the same files does not create duplicate chunks (uses content hash as chunk ID).
- Metadata stored per chunk: `source_file`, `chunk_index`, `document_title`.

### 3.11 Frontend (`frontend/src/`)
- Single-page application; React Router v6 with four routes (see Section 6).
- All API calls go through `api/client.ts` using `VITE_API_BASE_URL`.
- No API keys or secrets in any frontend file.
- Monaco Editor component is lazy-loaded.
- Dark-first Tailwind theme with violet/blue accent palette.

---

## 4. Finding Model

A **finding** is the atomic unit of review output. Both LLM and static analysis produce findings conforming to the same model.

```python
class Severity(str, Enum):
    critical = "critical"
    high     = "high"
    medium   = "medium"
    low      = "low"
    info     = "info"

class Category(str, Enum):
    security        = "security"
    correctness     = "correctness"
    performance     = "performance"
    maintainability = "maintainability"
    style           = "style"
    documentation   = "documentation"

class VerificationStatus(str, Enum):
    deterministic = "deterministic"   # static analysis tool output; rule-based
    unverified    = "unverified"      # LLM output; may be wrong

class FindingSource(str, Enum):
    llm    = "llm"
    ruff   = "ruff"
    bandit = "bandit"

class LineRange(BaseModel):
    start: int               # 1-indexed
    end:   int               # 1-indexed, inclusive

class Patch(BaseModel):
    original: str            # exact lines from submitted code
    suggested: str           # replacement lines

class Citation(BaseModel):
    document_title:    str
    chunk_text:        str
    source_file:       str
    relevance_score:   float  # 0.0–1.0 (ChromaDB cosine similarity)

class Finding(BaseModel):
    id:                  str               # UUID, stable within a review
    source:              FindingSource
    severity:            Severity
    category:            Category
    rule_id:             Optional[str]     # e.g. "E501", "B105" — from static tools
    title:               str               # short human label
    explanation:         str               # full explanation
    evidence:            Optional[str]     # quoted code snippet or tool message
    line_range:          Optional[LineRange]
    patch:               Optional[Patch]
    citations:           List[Citation]    # grounding from RAG; may be empty
    verification_status: VerificationStatus
```

### Distinguishing LLM vs Static-Analysis Findings

| Attribute           | LLM Finding               | Static-Analysis Finding        |
|---------------------|---------------------------|--------------------------------|
| `source`            | `"llm"`                   | `"ruff"` or `"bandit"`         |
| `verification_status` | `"unverified"`          | `"deterministic"`              |
| `rule_id`           | `null`                    | Tool rule code (e.g. `"E501"`) |
| `line_range`        | LLM-provided (may be wrong)| Exact from tool output         |
| `citations`         | Populated from RAG results | Empty (tools are self-contained)|
| `evidence`          | LLM-quoted snippet        | Tool output message            |
| `patch`             | LLM-generated diff        | Not provided by tools          |

---

## 5. Review Lifecycle

```
Client POST /api/v1/reviews
         │
         ▼
   ReviewRequest validated (Pydantic)
   • code ≤ 32 KB
   • language == "python" only
         │
         ▼
   ReviewOrchestrator.run(request)
         │
    ┌────┴──────────────────────────────────────────────────┐
    │  Run in parallel (asyncio.gather):                    │
    │  • static_analysis(code) → List[Finding]              │
    │  • retrieval.query(code[:500]) → List[Citation]       │
    └────┬──────────────────────────────────────────────────┘
         │
         ▼
   Build LLM prompt:
   • System role + instructions (structured JSON output)
   • User code (as fenced block)
   • Static analysis summary
   • RAG context chunks
         │
         ▼
   GeminiProvider.generate(prompt) → raw JSON string
         │
         ▼
   Validate JSON → List[Finding] (mark source="llm", status="unverified")
   On validation failure → log + return empty LLM findings (don't crash)
         │
         ▼
   Merge findings:
   • Static findings first (deterministic)
   • LLM findings appended
   • Sort by severity (critical → info)
         │
         ▼
   Build ReviewResponse:
   • id (UUID)
   • submitted_at (UTC timestamp)
   • code_hash (SHA-256 of submitted code)
   • language = "python"
   • findings (merged list)
   • summary (LLM-provided one-paragraph summary or empty string)
   • static_analysis_ran: bool
   • rag_context_retrieved: bool
         │
         ▼
   ReviewRepository.save(response) → MongoDB
         │
         ▼
   Return ReviewResponse to client
```

---

## 6. Frontend Routes

| Route                     | Component             | Description                                              |
|---------------------------|-----------------------|----------------------------------------------------------|
| `/`                       | `LandingPage`         | Hero, feature highlights, CTA → `/review`               |
| `/review`                 | `ReviewPage`          | Monaco editor, submit button, live findings panel        |
| `/history`                | `HistoryPage`         | Paginated list of past reviews; click → detail           |
| `/history/:reviewId`      | `ReviewDetailPage`    | Full findings, citations, diffs for a specific review    |

All routes wrapped in a shared `Navbar` and `Footer`.

---

## 7. Environment Variables

### Backend (`.env` at `backend/.env`, never committed)

| Variable                    | Required | Default         | Description                                |
|-----------------------------|----------|-----------------|--------------------------------------------|
| `GEMINI_API_KEY`            | ✅ yes   | —               | Google Gemini API key                      |
| `MONGODB_URI`               | ✅ yes   | —               | MongoDB connection string                  |
| `MONGODB_DB_NAME`           | no       | `codesage`      | Database name                              |
| `CHROMA_PERSIST_DIR`        | no       | `./chroma_data` | ChromaDB storage path                      |
| `CHROMA_COLLECTION_NAME`    | no       | `coding_guidelines` | ChromaDB collection                    |
| `GEMINI_MODEL`              | no       | `gemini-1.5-flash` | Gemini model name                       |
| `GEMINI_TIMEOUT_SECONDS`    | no       | `60`            | LLM call timeout                           |
| `GEMINI_MAX_RETRIES`        | no       | `2`             | Max retries on transient LLM errors        |
| `MAX_CODE_SIZE_BYTES`       | no       | `32768`         | Input size limit (32 KB)                   |
| `RAG_N_RESULTS`             | no       | `5`             | Number of RAG chunks to retrieve           |
| `CORS_ORIGINS`              | no       | `http://localhost:5173` | Comma-separated allowed origins  |
| `LOG_LEVEL`                 | no       | `INFO`          | Python log level                           |

### Frontend (`.env` at `frontend/.env`, or `frontend/.env.local`)

| Variable                | Required | Default                       | Description           |
|-------------------------|----------|-------------------------------|-----------------------|
| `VITE_API_BASE_URL`     | no       | `http://localhost:8000`       | Backend base URL      |

---

## 8. External Services

| Service              | Access        | Notes                                           |
|----------------------|---------------|-------------------------------------------------|
| Google Gemini API    | HTTPS outbound| Backend only; key in env var                    |
| MongoDB              | TCP           | Local Docker or Atlas; URI in env var           |
| ChromaDB             | In-process    | Persisted to local directory; no network call   |
| sentence-transformers| In-process    | Model downloaded on first run (~90 MB)          |

---

## 9. Security Boundaries

1. **No secrets in frontend.** `VITE_API_BASE_URL` is the only frontend env var.
2. **No code execution.** Submitted Python is written to a temp file for static tool invocation only; the process runs with `subprocess.run(...)` with a strict timeout, and the temp file is deleted immediately.
3. **CORS lockdown.** Only configured origins (`CORS_ORIGINS`) are allowed; wildcard `*` is never used in production config.
4. **Input limits.** Code submissions > 32 KB (configurable) are rejected with 422 before reaching services.
5. **LLM output treated as untrusted.** All LLM-returned findings are validated by Pydantic before use; validation failures are logged and return empty rather than crashing.
6. **No unrestricted URL fetching.** RAG ingestion reads only from `app/rag/documents/` on disk.
7. **MongoDB injection.** PyMongo with typed queries; submitted code stored as a string field, never interpolated into queries.

---

## 10. Persistence Schemas

### MongoDB Collection: `reviews`

```json
{
  "_id": "uuid-string",
  "submitted_at": "2026-10-30T06:21:00Z",
  "code_hash": "sha256hex",
  "language": "python",
  "code_snippet": "... first 500 chars ...",
  "findings": [ /* array of Finding objects */ ],
  "summary": "string",
  "static_analysis_ran": true,
  "rag_context_retrieved": true,
  "finding_counts": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 0,
    "info": 1
  }
}
```

> **Note:** Full submitted code is **not** persisted to MongoDB. Only a 500-character snippet is stored for display in history. This reduces storage and avoids retaining potentially sensitive user code.

### ChromaDB Collection: `coding_guidelines`

Each document embedding metadata:
```json
{
  "id": "sha256(source_file + chunk_index)",
  "document": "chunk text",
  "metadata": {
    "source_file": "pep8_style_guide.md",
    "document_title": "PEP 8 Style Guide",
    "chunk_index": 3
  }
}
```

---

## 11. Local Development

```bash
# 1. Start MongoDB (Docker)
docker run -d --name mongo -p 27017:27017 mongo:7

# 2. Backend
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # fill in GEMINI_API_KEY and MONGODB_URI
python -m app.rag.ingest          # ingest guideline documents
uvicorn app.main:app --reload     # starts on :8000

# 3. Frontend
cd frontend
pnpm install
cp .env.example .env.local        # set VITE_API_BASE_URL if needed
pnpm dev                          # starts on :5173
```

---

## 12. Docker Compose

`docker-compose.yml` services:
- `mongodb` — official `mongo:7` image, persistent volume `mongo_data`.
- `backend` — custom image from `backend/Dockerfile`; depends on `mongodb`.
- `frontend` — custom image from `frontend/Dockerfile` (Nginx serving built assets).

`docker-compose.dev.yml` (override for development):
- `backend` uses volume mount for hot-reload via `uvicorn --reload`.
- `frontend` uses Vite dev server with volume mount.

---

## 13. Test Strategy

| Layer               | Tool                        | What is tested                                      |
|---------------------|-----------------------------|-----------------------------------------------------|
| Backend unit        | Pytest + pytest-mock        | Each service in isolation; LLM and DB are mocked    |
| Backend API         | Pytest + httpx (TestClient) | Endpoint contracts, error codes, response shapes    |
| Backend integration | Pytest                      | Full review flow with real Ruff/Bandit; LLM mocked  |
| Frontend unit       | Vitest + RTL                | Component rendering, user interactions              |
| Frontend type check | `tsc --noEmit`              | TypeScript type correctness                         |
| Frontend lint       | ESLint                      | Code quality                                        |

Integration tests that require MongoDB or ChromaDB are marked `@pytest.mark.integration` and skipped in CI by default unless `INTEGRATION_TESTS=1` is set.

---

_This document is authoritative. Any implementation that deviates from it must update this document and log the decision in `DECISIONS.md`._
