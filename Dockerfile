# ========================================================
# GLITCHGUARD Unified Production Multi-Stage Dockerfile
# Serves React 19 Dashboard + FastAPI Telemetry Backend
# ========================================================

# Stage 1: Build React 19 Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim
WORKDIR /app

# Install curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    fastapi>=0.100 \
    "uvicorn[standard]>=0.23" \
    pydantic>=2.0 \
    pydantic-settings>=2.0 \
    pyserial>=3.5 \
    httpx>=0.24 \
    python-multipart>=0.0.6

# Copy application backend & experiment assets
COPY host-tools/ ./host-tools/
COPY experiments/ ./experiments/
COPY research/ ./research/
COPY docs/ ./docs/

# Copy compiled React frontend into dashboard/dist
COPY --from=frontend-builder /app/dashboard/dist ./dashboard/dist

# Configure environment
ENV PYTHONPATH=/app/host-tools
ENV FRONTEND_DIST_DIR=/app/dashboard/dist

# Expose default port
EXPOSE 8000

# Launch uvicorn bound to Railway dynamic $PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
