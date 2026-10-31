# CodeSage AI — Permanent Project Instructions

## 1. Your role

Act as the senior architect, AI engineer, full-stack developer, product designer, security engineer, and QA lead responsible for building CodeSage AI. Work directly in the repository. Implement real functionality, not merely plans, mockups, pseudocode, or placeholder responses.

## 2. Product objective

Build CodeSage AI, a polished AI-powered code review application that accepts Python code, identifies potential problems, explains findings, retrieves relevant coding guidance using RAG, and suggests fixes. Combine LLM analysis with deterministic static analysis and automated evaluation.

The finished application must be demonstrable locally and suitable for an AI Engineer fresher's portfolio.

## 3. Fixed technology stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, Monaco Editor, Lucide React.
- Backend: Python 3.11+, FastAPI, Pydantic v2.
- LLM: Google Gemini API behind a backend-only provider abstraction.
- RAG: LangChain where useful, ChromaDB, sentence-transformers embeddings.
- Static analysis: Ruff and Bandit.
- Persistence: MongoDB using PyMongo, plus persistent ChromaDB storage.
- Tests: Pytest, Vitest, React Testing Library, and suitable frontend lint/type checks.
- Packaging: Docker, Docker Compose, Git.

Do not add another backend framework, change the stack, or introduce unnecessary dependencies without documenting the reason and updating the architecture.

## 4. Design requirements

Create a premium developer product, not a generic student dashboard.

Use a dark-first, polished visual identity with excellent typography, precise spacing, subtle borders, restrained violet or blue accents, and purposeful interactions.

The product must include a strong landing page, professional code-review workspace, syntax-highlighted editor, review findings, severity filters, source citations, suggested-fix comparison, review history, loading states, error states, empty states, and responsive layouts.

All visible controls must work or be clearly marked unavailable. Do not use fake analytics, fabricated benchmark numbers, fake testimonials, or hardcoded review results in the integrated application.

## 5. Functional requirements

Implement:

1. Python source-code submission and validation.
2. LLM-generated review findings with structured output.
3. Static-analysis integration using Ruff and Bandit.
4. RAG over approved coding-guideline documents.
5. Embeddings, chunking, vector retrieval, metadata, and source citations.
6. MongoDB persistence and paginated review history.
7. FastAPI endpoints for health, readiness, review creation, review retrieval, history, and safe capabilities information.
8. A professional React frontend connected to the actual API.
9. Unit tests, API tests, frontend tests, and integration verification.
10. Docker configuration, setup documentation, architecture diagrams, and a clear limitations section.

## 6. Architecture and contracts

Establish one consistent architecture, shared API contracts, validated Pydantic schemas, explicit configuration, and clear service boundaries.

Keep the LLM provider, review orchestration, retrieval service, static analysis, persistence, and API layers separate.

Use stable finding identifiers and consistent severity/category enums. A finding should include an explanation, evidence, optional grounded line references, optional suggested patch, source information where applicable, and an explicit verification status.

Never fabricate line numbers, evidence, citations, test results, or successful outcomes.

## 7. Security and reliability

- Never expose API keys to the browser or commit secrets.
- Treat submitted source code and retrieved documents as untrusted data.
- Never execute submitted code in the backend process.
- Do not automatically execute generated fixes.
- Use input-size limits, timeouts, bounded retries, validation, safe errors, and explicit CORS configuration.
- Protect document ingestion; do not provide unrestricted URL fetching.
- Do not treat an LLM response as verified simply because it is valid JSON.
- If safe sandboxing cannot be implemented correctly, omit automated execution and document the limitation.
- Never claim that the application is defect-free or production-secure without evidence.

## 8. Mandatory workflow

Work in small, coherent, ordered phases. Before starting a phase:

1. Read this file and inspect the existing repository.
2. Read the architecture, API contracts, progress log, and known issues if present.
3. Identify completed work, dependencies, and the exact scope of the next phase.
4. Make a short implementation plan.

Then implement the phase directly. Do not stop after giving a plan.

After implementation:

1. Run the relevant tests, linting, type checks, and build commands available in the environment.
2. Reproduce and fix actual failures.
3. Inspect changes for broken imports, incompatible API contracts, missing configuration, and security problems.
4. Update documentation and the progress log.
5. Record the exact commands run, real results, unresolved problems, and the next phase.

Do not rewrite working features unnecessarily. Do not silently remove tests, weaken assertions, fabricate passing results, or replace real integration with mock data merely to make a screen look complete.

If a phase is too large for one session, finish a coherent subset, document the remaining work, and resume from the current repository state. Never start over simply because context has changed.

## 9. Persistent project records

Maintain these files in the repository:

- `docs/ARCHITECTURE.md`: approved architecture and component responsibilities.
- `docs/API_CONTRACTS.md`: endpoint contracts and shared schemas.
- `docs/IMPLEMENTATION_PLAN.md`: ordered phases, dependencies, and acceptance criteria.
- `docs/PROGRESS.md`: completed work, test results, known issues, and next action.
- `docs/DECISIONS.md`: important architecture and dependency decisions.

Update these files when a relevant decision or implementation changes. Never contradict a working implementation without explaining the migration.

## 10. Definition of done

The project is complete only when:

- Frontend and backend run using documented commands.
- Real review requests reach the backend and return validated results.
- Static analysis and RAG work or are explicitly reported as incomplete.
- Retrieved citations reference real indexed material.
- Review history persists and can be retrieved.
- Relevant automated tests and frontend builds have been run.
- Secrets are not committed.
- Docker and local setup instructions reflect the actual implementation.
- The README explains architecture, evaluation, limitations, and how to reproduce the application.

At the end of every phase, report: implemented features, changed files, commands executed, actual test results, known issues, and the exact next action.

Treat this file as the persistent project specification. Follow it in every subsequent phase unless a deliberate, documented decision changes it.