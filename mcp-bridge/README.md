# MCP Bridge

MCP (Model Context Protocol) server for operating containerlab / FRR / vJunos-router.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
# STDIO mode
mcp-bridge
```

## Available Tools

| Tool | Description |
|------|-------------|
| `clab_deploy` | Deploy a containerlab topology |
| `clab_destroy` | Destroy a topology |
| `clab_inspect` | Inspect node status |
| `frr_show` | Execute show commands on FRR |
| `frr_config` | Push configuration to FRR |
| `junos_show` | Execute show commands on vJunos |
| `junos_config` | Push configuration to vJunos |

## Development

```bash
# Lint
ruff check src/

# Test
pytest
```
