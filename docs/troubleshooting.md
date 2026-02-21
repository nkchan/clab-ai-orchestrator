# Troubleshooting

## containerlab

### `clab deploy` fails

**Symptom**: Permission denied error

```bash
# Run with sudo
sudo clab deploy -t labs/basic-bgp/topology.clab.yml
```

### vJunos node doesn't start

**Symptom**: Node not showing `running` in `clab inspect`

1. Check Docker image:
```bash
docker images | grep vjunos
```

2. If image is missing, build with vrnetlab:
```bash
cp images/vJunos-router-25.4R1.12.qcow2 /opt/vrnetlab/vjunos-router/
cd /opt/vrnetlab/vjunos-router && sudo make
```

3. vJunos may take **3–5 minutes** to boot. Wait and re-check.

### Stale lab remains

```bash
# Check all labs
sudo clab inspect --all

# Destroy specific lab
sudo clab destroy -t labs/basic-bgp/topology.clab.yml

# Destroy with cleanup
sudo clab destroy -t labs/basic-bgp/topology.clab.yml --cleanup
```

## BGP

### BGP neighbor not establishing

1. **Check IP addresses**:
```bash
# FRR
docker exec clab-basic-bgp-frr1 vtysh -c "show interface brief"

# vJunos
docker exec clab-basic-bgp-vjunos1 cli show interfaces terse
```

2. **Check reachability**:
```bash
docker exec clab-basic-bgp-frr1 ping -c 3 192.0.2.2
```

3. **Check BGP details**:
```bash
# FRR
docker exec clab-basic-bgp-frr1 vtysh -c "show ip bgp neighbor 192.0.2.2"

# vJunos
docker exec clab-basic-bgp-vjunos1 cli show bgp neighbor 192.0.2.1
```

## mcp-bridge

### Installation error

```bash
cd mcp-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### MCP server won't start

- Requires Python 3.10+
- Verify `mcp` package is installed:
```bash
pip show mcp
```
