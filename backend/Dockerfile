# ==============================================================================
# CodeSage AI — Backend Dockerfile
# Multi-stage production build for Python 3.11+ FastAPI service
# ==============================================================================

# ── Stage 1: Dependency builder & model pre-fetch ────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers embedding model during build
# This avoids runtime latency and prevents network dependency on startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ── Stage 2: Minimal runtime image ───────────────────────────────────────────
FROM python:3.11-slim AS runner

WORKDIR /app

# Install curl for Docker health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment and model cache from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /root/.cache /root/.cache

# Runtime environment configuration
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ANONYMIZED_TELEMETRY=False \
    HF_HUB_OFFLINE=1 \
    CHROMA_PERSIST_DIR=/app/chroma_data

# Create persistent storage directory for ChromaDB
RUN mkdir -p /app/chroma_data

# Copy backend application code
COPY app /app/app
COPY pyproject.toml /app/

# Expose FastAPI port
EXPOSE 8000

# Docker healthcheck querying the liveness endpoint
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Launch uvicorn web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
