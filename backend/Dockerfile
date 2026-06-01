# ─────────────────────────────────────────────
# JurisFind API – Dockerfile
# Base: Python 3.11 slim (compatible with all requirements)
# ─────────────────────────────────────────────

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies needed by PyMuPDF, torch, faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source
COPY . .

# Create directory for temporary confidential uploads
RUN mkdir -p /tmp/confidential_uploads

# Expose the uvicorn port
EXPOSE 8000

# Health check – hits the /api/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run with uvicorn factory mode — matches how main.py calls uvicorn.run()
# 2 workers is fine for Standard_B2s (2 vCPU). Increase to 4 on larger VMs.
CMD ["uvicorn", "main:create_app", \
     "--factory", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--timeout-keep-alive", "5"]
