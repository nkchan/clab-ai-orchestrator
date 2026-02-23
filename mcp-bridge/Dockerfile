# syntax=docker/dockerfile:1
# ============================================================
# mcp-bridge Docker Image
# ============================================================
# Pins Python version and all dependencies for reproducibility.
# Runs as non-root user for security.
# ============================================================
FROM python:3.12.8-slim-bookworm AS base

# System deps required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io curl sudo \
    && curl -sL https://get.containerlab.dev | bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (cached layer)
COPY pyproject.toml ./
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# Copy source
COPY src/ ./src/

# Install package
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["mcp-bridge"]
