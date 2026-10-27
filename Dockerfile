# syntax=docker/dockerfile:1
#
# Pathfinder - multi-stage build (Checkpoint 4, Deliverable 17)
#
#   Stage 1 "builder": installs dependencies into a venv, downloads the
#                      embedding model, and BUILDS THE CHROMA INDEX from
#                      data/processed/. Needs internet; no API key needed.
#   Stage 2 "runtime": copies only the venv, model cache, code and finished
#                      index into a clean slim image. Runs as a non-root user,
#                      works offline for the embedding model, and receives
#                      GEMINI_API_KEY only at `docker run` time.
#
# Build:  docker build -t pathfinder .
# Run:    docker run --rm -p 7860:7860 -e GEMINI_API_KEY=<your-key> pathfinder
# Open:   http://localhost:7860

############################ Stage 1: builder ############################
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/opt/hf-cache \
    ANONYMIZED_TELEMETRY=False

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# CPU-only PyTorch first: the default PyPI wheel drags in ~GBs of CUDA
# libraries that a CPU-only MiniLM embedder never uses.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements-app.txt .
RUN pip install -r requirements-app.txt

# Build the vector index at image-build time so the container starts ready
# (no first-request delay, no network needed for the embedding model).
COPY src/ ./src/
COPY data/processed/ ./data/processed/
RUN python src/04_setup_vector_db.py

############################ Stage 2: runtime ############################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/opt/hf-cache \
    HF_HUB_OFFLINE=1 \
    ANONYMIZED_TELEMETRY=False \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PORT=7860

# UID 1000 also matches what Hugging Face Spaces runs containers as.
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/hf-cache /opt/hf-cache
COPY --from=builder --chown=appuser:appuser /build/data ./data
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser tests/ ./tests/

USER appuser
EXPOSE 7860

# GEMINI_API_KEY is deliberately NOT set here - inject it at runtime
# (-e / --env-file / platform secret). See docs/Deployment_Guide.md.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/_stcore/health' % os.environ.get('PORT', '7860'), timeout=3)"]

CMD ["sh", "-c", "exec streamlit run app/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
