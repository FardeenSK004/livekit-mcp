# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# --- Build stage ---
FROM base AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies with locked uv state
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Copy source code and install project wheel
COPY . .
RUN uv sync --locked --no-dev

# --- Production stage ---
FROM base AS production

ENV UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    HOST="0.0.0.0" \
    PORT=8000 \
    ENVIRONMENT="production"

# Create non-root system user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install runtime utilities (curl for healthcheck, ca-certificates for HTTPS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy built application and virtualenv from build stage
COPY --from=build --chown=appuser:appuser /app /app
WORKDIR /app

USER appuser

# Expose default FastMCP HTTP/SSE port
EXPOSE 8000

# Health check against Starlette health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start LiveKit FastMCP server
CMD ["livekit-mcp"]
