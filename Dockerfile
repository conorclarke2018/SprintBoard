# SprintBoard: one image for the whole app.
# Stage 1 builds the React frontend; stage 2 runs FastAPI, which serves both the API (/api)
# and the built frontend from a single port.

# ---------- Stage 1: build the frontend ----------
FROM node:22-alpine AS frontend

WORKDIR /app/frontend

# Install dependencies first so this layer is cached until package files change.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: run the backend ----------
FROM python:3.13-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.11.33 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/backend/.venv/bin:$PATH" \
    DATABASE_URL="sqlite:////data/sprintboard.db" \
    PORT=8000

WORKDIR /app/backend

# Install Python packages from the lock file (production only, no test tools).
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/app ./app
COPY backend/seed.py ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Run as a non-root user. /data holds the SQLite database; logs/ holds app.log.
RUN useradd --create-home --uid 1000 sprintboard \
    && mkdir -p /data /app/backend/logs \
    && chown -R sprintboard:sprintboard /data /app/backend/logs
USER sprintboard

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/health', timeout=4)"

# PORT can be overridden by the host (Render sets it automatically).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
