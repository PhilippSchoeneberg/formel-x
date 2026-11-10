# syntax=docker/dockerfile:1
#
# FormelX web app (FastAPI + static frontend). Multi-stage build:
#   1. "builder" installs the locked Python dependencies with uv into /app/.venv
#   2. the final image copies only that environment and the source code (no uv, no caches)
# Both base images are multi-arch, so this builds natively on arm64 (Oracle Ampere) and amd64.

ARG PYTHON_IMAGE=python:3.13-slim

FROM ${PYTHON_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Unprivileged user: the app never needs root inside the container.
RUN useradd --create-home --uid 10001 formelx

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY src ./src

USER formelx

# Plain HTTP inside the Docker network; the Caddy proxy in front terminates TLS (HTTPS).
EXPOSE 8000

# Migrations run on every start; they're a no-op when the schema is current.
# --proxy-headers: take the client address and the original scheme (https) from the
# X-Forwarded-For / X-Forwarded-Proto headers of the proxies listed in FORWARDED_ALLOW_IPS.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --proxy-headers --no-server-header"]
