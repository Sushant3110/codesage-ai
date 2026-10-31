# CodeSage AI — API Contracts

_Last updated: Phase 0 (2026-10-30)_

---

## 1. Conventions

- All endpoints are prefixed `/api/v1/`.
- Request and response bodies are JSON (`Content-Type: application/json`).
- Timestamps are ISO 8601 UTC strings (`"2026-10-30T06:21:00Z"`).
- UUIDs are lowercase hyphenated strings (`"3fa85f64-5717-4562-b3fc-2c963f66afa6"`).
- HTTP error responses always follow the `ErrorResponse` schema (see §3.5).
- Pagination uses `page` (1-indexed) and `page_size` query parameters.

---

## 2. Base URL

```
Local dev:  http://localhost:8000
Docker:     http://backend:8000   (internal service name)
```

Frontend uses `VITE_API_BASE_URL` env var to resolve this.

---

## 3. Shared Schemas

### 3.1 `Severity`
```
"critical" | "high" | "medium" | "low" | "info"
```

### 3.2 `Category`
```
"security" | "correctness" | "performance" | "maintainability" | "style" | "documentation"
```

### 3.3 `FindingSource`
```
"llm" | "ruff" | "bandit"
```

### 3.4 `VerificationStatus`
```
"deterministic" | "unverified"
```

### 3.5 `LineRange`
```json
{
  "start": 1,
  "end": 5
}
```
Both values are 1-indexed, inclusive. `end >= start`.

### 3.6 `Patch`
```json
{
  "original": "x = 1+1\n",
  "suggested": "x = 1 + 1\n"
}
```
`original` must be an exact substring of the submitted code. Presence does not imply automated application.

### 3.7 `Citation`
```json
{
  "document_title": "PEP 8 Style Guide for Python Code",
  "chunk_text": "Surround binary operators with a single space on each side...",
  "source_file": "pep8_style_guide.md",
  "relevance_score": 0.87,
  "source_url": "https://peps.python.org/pep-0008/",
  "section": "Whitespace in Expressions and Statements"
}
```
`source_url` (optional string or null) points to the approved guideline source. `section` (optional string or null) indicates the section heading from which the chunk was extracted. `relevance_score` is a float in `[0.0, 1.0]` representing cosine similarity.

### 3.8 `Finding`
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "source": "llm",
  "severity": "high",
  "category": "security",
  "rule_id": null,
  "title": "Hardcoded password detected",
  "explanation": "The variable `password` is assigned a string literal. Hardcoded credentials are a significant security risk.",
  "evidence": "password = \"hunter2\"",
  "line_range": { "start": 12, "end": 12 },
  "patch": {
    "original": "password = \"hunter2\"\n",
    "suggested": "password = os.getenv(\"APP_PASSWORD\")\n"
  },
  "citations": [
    {
      "document_title": "OWASP Secure Coding",
      "chunk_text": "Never hardcode credentials in source code...",
      "source_file": "owasp_secure_coding.md",
      "relevance_score": 0.91
    }
  ],
  "verification_status": "unverified"
}
```

For a static-analysis finding:
```json
{
  "id": "7d9e2b1a-...",
  "source": "ruff",
  "severity": "low",
  "category": "style",
  "rule_id": "E501",
  "title": "Line too long (92 > 79 characters)",
  "explanation": "PEP 8 recommends lines no longer than 79 characters.",
  "evidence": "    very_long_variable_name = some_function(argument_one, argument_two, argument_three)",
  "line_range": { "start": 34, "end": 34 },
  "patch": null,
  "citations": [],
  "verification_status": "deterministic"
}
```

### 3.9 `ErrorResponse`
```json
{
  "detail": "Human-readable error message",
  "code": "VALIDATION_ERROR"
}
```
`code` is a machine-readable uppercase string. Standard codes:

| Code                    | HTTP Status | Meaning                                   |
|-------------------------|-------------|-------------------------------------------|
| `VALIDATION_ERROR`      | 422         | Request body failed Pydantic validation   |
| `CODE_TOO_LARGE`        | 413         | Submitted code exceeds size limit         |
| `UNSUPPORTED_LANGUAGE`  | 422         | Language is not "python"                  |
| `REVIEW_NOT_FOUND`      | 404         | Review ID does not exist                  |
| `SERVICE_UNAVAILABLE`   | 503         | Backend dependency (LLM, DB) unreachable  |
| `INTERNAL_ERROR`        | 500         | Unexpected server error                   |

### 3.10 `PaginatedResponse<T>`
```json
{
  "items": [ /* array of T */ ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### 3.11 `ReviewSummary` (used in history list)
```json
{
  "id": "3fa85f64-...",
  "submitted_at": "2026-10-30T06:21:00Z",
  "code_snippet": "def hello():\n    print('hello')",
  "finding_counts": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 0,
    "info": 1
  },
  "language": "python"
}
```

---

## 4. Endpoints

### 4.1 `GET /api/v1/health`
Liveness probe. Always returns 200 if the process is alive.

**Response 200:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```
No auth, no body. Used by Docker health checks and monitoring.

---

### 4.2 `GET /api/v1/ready`
Readiness probe. Returns 200 only if MongoDB and ChromaDB are reachable.

**Response 200:**
```json
{
  "status": "ready",
  "checks": {
    "mongodb": "ok",
    "chromadb": "ok"
  }
}
```

**Response 503:**
```json
{
  "status": "not_ready",
  "checks": {
    "mongodb": "ok",
    "chromadb": "error: collection not found"
  }
}
```

---

### 4.3 `POST /api/v1/reviews`
Submit Python code for review. This is the primary endpoint.

**Request body:**
```json
{
  "code": "def greet(name):\n    print('Hello ' + name)\n",
  "language": "python",
  "context": "Optional user-provided description of the code (max 500 chars)"
}
```

| Field      | Type   | Required | Constraints                                                                                          |
|------------|--------|----------|------------------------------------------------------------------------------------------------------|
| `code`     | string | ✅       | 1–32 768 bytes, UTF-8                                                                                |
| `language` | string | ✅       | Must be one of: `"python"`, `"java"`, `"javascript"`, `"typescript"`, `"c"`, `"cpp"`, `"html"`, `"css"`, `"sql"` |
| `context`  | string | no       | Max 500 characters; passed to LLM prompt                                                             |

**Response 200:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "submitted_at": "2026-10-30T06:21:00Z",
  "code_hash": "e3b0c44298fc1c149afb...",
  "language": "python",
  "summary": "The code has one high-severity security issue and two style issues.",
  "findings": [ /* List[Finding] sorted critical→info */ ],
  "static_analysis_ran": true,
  "rag_context_retrieved": true,
  "finding_counts": {
    "critical": 0,
    "high": 1,
    "medium": 0,
    "low": 0,
    "info": 2
  }
}
```

**Error responses:**
- `413` — code exceeds size limit (`CODE_TOO_LARGE`)
- `422` — validation failure (`VALIDATION_ERROR` or `UNSUPPORTED_LANGUAGE`)
- `503` — LLM or DB unavailable (`SERVICE_UNAVAILABLE`)
- `500` — unexpected error (`INTERNAL_ERROR`)

> **Performance note:** This endpoint is synchronous and may take 5–30 seconds depending on LLM latency. The frontend must show a loading state for the full duration.

---

### 4.4 `GET /api/v1/reviews/{review_id}`
Retrieve a previously completed review by ID.

**Path parameter:** `review_id` — UUID string.

**Response 200:** Full `ReviewResponse` object (same schema as POST response).

**Error responses:**
- `404` — review not found (`REVIEW_NOT_FOUND`)
- `422` — `review_id` is not a valid UUID

---

### 4.5 `GET /api/v1/history`
Retrieve paginated review history (most recent first).

**Query parameters:**

| Parameter   | Type | Default | Constraints        |
|-------------|------|---------|--------------------|
| `page`      | int  | `1`     | ≥ 1                |
| `page_size` | int  | `20`    | 1–100              |

**Response 200:** `PaginatedResponse<ReviewSummary>`

```json
{
  "items": [
    {
      "id": "3fa85f64-...",
      "submitted_at": "2026-10-30T06:21:00Z",
      "code_snippet": "def hello():\n    ...",
      "finding_counts": { "critical": 0, "high": 1, "medium": 2, "low": 0, "info": 1 },
      "language": "python"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

### 4.6 `GET /api/v1/capabilities`
Returns safe, static information about what the backend supports. No secrets exposed.

**Response 200:**
```json
{
  "supported_languages": ["python"],
  "llm_model": "gemini-1.5-flash",
  "static_analysis_tools": ["ruff", "bandit"],
  "rag_enabled": true,
  "rag_document_count": 5,
  "max_code_size_bytes": 32768
}
```

`rag_enabled` is `true` only if the ChromaDB collection has at least one document. `rag_document_count` is the count of source documents (not chunks).

---

## 5. Frontend API Client Contract

The TypeScript client in `frontend/src/api/client.ts` must:

1. Read `VITE_API_BASE_URL` from `import.meta.env`.
2. Set `Content-Type: application/json` on POST requests.
3. Throw a typed `ApiError` (containing `detail` and `code`) for any non-2xx response.
4. Export typed functions:
   - `submitReview(request: ReviewRequest): Promise<ReviewResponse>`
   - `getReview(id: string): Promise<ReviewResponse>`
   - `getHistory(page: number, pageSize: number): Promise<PaginatedResponse<ReviewSummary>>`
   - `getCapabilities(): Promise<CapabilitiesResponse>`
   - `getHealth(): Promise<HealthResponse>`

---

## 6. TypeScript Type Mirrors

File: `frontend/src/types/review.ts`

All TypeScript types must exactly mirror the backend Pydantic schemas. They are hand-maintained (no code generation in Phase 0). Key types:

```typescript
export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type Category = 'security' | 'correctness' | 'performance' | 'maintainability' | 'style' | 'documentation';
export type FindingSource = 'llm' | 'ruff' | 'bandit';
export type VerificationStatus = 'deterministic' | 'unverified';

export interface LineRange { start: number; end: number; }
export interface Patch { original: string; suggested: string; }
export interface Citation { document_title: string; chunk_text: string; source_file: string; relevance_score: number; }

export interface Finding {
  id: string;
  source: FindingSource;
  severity: Severity;
  category: Category;
  rule_id: string | null;
  title: string;
  explanation: string;
  evidence: string | null;
  line_range: LineRange | null;
  patch: Patch | null;
  citations: Citation[];
  verification_status: VerificationStatus;
}

export interface ReviewRequest { code: string; language: 'python'; context?: string; }
export interface FindingCounts { critical: number; high: number; medium: number; low: number; info: number; }

export interface ReviewResponse {
  id: string;
  submitted_at: string;
  code_hash: string;
  language: string;
  summary: string;
  findings: Finding[];
  static_analysis_ran: boolean;
  rag_context_retrieved: boolean;
  finding_counts: FindingCounts;
}

export interface ReviewSummary {
  id: string;
  submitted_at: string;
  code_snippet: string;
  finding_counts: FindingCounts;
  language: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

---

_This contract is authoritative. Any endpoint or schema change must be reflected here before implementation._
