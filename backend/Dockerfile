# Production Dockerfile for SmartConsent AI Backend
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered streaming logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    CHROMA_DB_DIR=/app/data/chroma_db \
    RAG_DOCS_DIR=/app/rag/documents \
    DATABASE_URL=sqlite:////app/data/smartconsent.db

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for Docker build cache reuse
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code and legal RAG documents
COPY backend /app/backend
COPY rag /app/rag

# Create persistent storage folder and ensure entrypoint is executable
RUN mkdir -p /app/data && chmod +x /app/backend/entrypoint.sh

WORKDIR /app/backend
ENV PYTHONPATH=/app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/backend/entrypoint.sh"]
