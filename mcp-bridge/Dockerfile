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
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r mcp && useradd -r -g mcp -d /app mcp

WORKDIR /app

# Install Python deps (cached layer)
COPY pyproject.toml ./
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# Copy source
COPY src/ ./src/

# Install package
RUN pip install --no-cache-dir -e .

USER mcp

ENTRYPOINT ["mcp-bridge"]
