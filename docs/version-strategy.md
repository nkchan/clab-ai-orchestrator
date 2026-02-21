# Version Strategy

Version pinning policy for tools and libraries used in this project.

## Policy

| Layer | Method | Rationale |
|-------|--------|-----------|
| **Python runtime** | Pinned in Dockerfile (`3.12.8`) | Independent of host Python |
| **Python packages** | Fully pinned in `requirements.lock` | Reproducible builds |
| **containerlab** | Latest stable via setup script | Rarely has breaking changes |
| **FRR image** | Tag pinned in `.env.example` (`10.3.1`) | Use verified NOS versions |
| **vJunos image** | Pinned at vrnetlab build time (`25.4R1.12`) | Managed per-image |

## mcp-bridge: Native vs Container

### Container Execution (Recommended)

```bash
docker compose up -d
```

**Advantages:**
- Python version and dependencies are fully isolated
- Does not pollute the host environment
- Docker socket mount enables containerlab operations
- Same image for production and test environments

**Notes:**
- Docker socket is mounted read-only for security
- STDIO communication is preserved via `stdin_open: true` + `tty: true`

### Native Execution (Development)

```bash
cd mcp-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
pip install -e ".[dev]"
mcp-bridge
```

Native execution is convenient for rapid iteration during development.

## Updating Versions

### Python Packages

```bash
cd mcp-bridge
# 1. Edit dependencies in pyproject.toml
# 2. Regenerate lock file
pip install pip-tools
pip-compile pyproject.toml -o requirements.lock
# 3. Test
pip install -r requirements.lock
pytest
# 4. Rebuild Docker image
docker compose build
```

### FRR / vJunos Images

1. Update version tags in `.env.example`
2. Update topology definitions in `labs/` for the new version
3. Verify with `samples/`
