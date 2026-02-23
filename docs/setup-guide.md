# Setup Guide

Environment setup on Ubuntu 24.04.

## Prerequisites

- Ubuntu 24.04 LTS
- sudo privileges
- Internet connection
- vJunos-router QCOW2 image

## Automated Setup

```bash
sudo bash setup/install.sh
```

This script installs:
1. **Docker** — Container runtime
2. **containerlab** — Network lab orchestrator
3. **FRR image** — `quay.io/frrouting/frr:10.3.1`
4. **vrnetlab** — Converts vJunos QCOW2 → Docker image
5. **Python 3** — Runtime for mcp-bridge

## Preparing the vJunos-router Image

### 1. Download
Download `vJunos-router-*.qcow2` from [Juniper Support](https://support.juniper.net/).

### 2. Place
```bash
cp vJunos-router-25.4R1.12.qcow2 images/
```

### 3. Build Docker Image
Running `setup/install.sh` will automatically build via vrnetlab.  
To build manually:

```bash
cp images/vJunos-router-25.4R1.12.qcow2 /opt/vrnetlab/vjunos-router/
cd /opt/vrnetlab/vjunos-router
sudo make
```

### 4. Verify
```bash
docker images | grep vjunos
# vrnetlab/juniper_vjunos-router   25.4R1.12   ...
```

## Setting Up mcp-bridge

```bash
cd mcp-bridge
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv if missing
source $HOME/.local/bin/env  # Update PATH
uv venv
uv pip install -e ".[dev]"
```

## Smoke Test

```bash
# Deploy lab
sudo clab deploy -t labs/basic-bgp/topology.clab.yml

# Inspect nodes
sudo clab inspect -t labs/basic-bgp/topology.clab.yml

# Check BGP
docker exec clab-basic-bgp-frr1 vtysh -c "show ip bgp summary"
docker exec clab-basic-bgp-vjunos1 cli show bgp summary
```
