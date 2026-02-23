# MCP Bridge

MCP (Model Context Protocol) server for operating containerlab / FRR / FRR.

## Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv if missing
source $HOME/.local/bin/env  # Update PATH
uv venv
uv pip install -e ".[dev]"
```

## Run

```bash
# STDIO mode
uv run mcp-bridge
```

## Available Tools

| Tool | Description |
|------|-------------|
| `clab_deploy` | Deploy a containerlab topology |
| `clab_destroy` | Destroy a topology |
| `clab_inspect` | Inspect node status |
| `frr_show` | Execute show commands on FRR |
| `frr_config` | Push configuration to FRR |
| `junos_show` | Execute show commands on Junos (Disabled) |
| `junos_config` | Push configuration to Junos (Disabled) |

## Development

```bash
# Lint
ruff check src/

# Test
pytest
```
