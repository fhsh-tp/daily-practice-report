FROM python:3.13-slim-trixie

# Update system dependencies
RUN apt-get update \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .

# Install the application dependencies.
RUN uv sync --frozen --no-cache

COPY ./src ./src

# Reduce system loading
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ASGI settings
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

## Uvicorn parameter `--forwarded-allow-ips` default value is point to $FORWARDED_ALLOW_IPS
## Default is empty (no trusted proxies). Override at runtime: docker run -e FORWARDED_ALLOW_IPS=127.0.0.1
ENV FORWARDED_ALLOW_IPS=""

# Use entrypoint script to handle environment-based startup
COPY ./scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE ${UVICORN_PORT:-8000}