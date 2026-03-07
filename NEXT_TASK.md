# Next Steps: BGP Troubleshooting & Verification

The environment is set up with a functional `mcp-bridge` that can interact with vJunos via telnet and resolve short container names.

## Current State
- **vJunos**: Booted in "Amnesiac" state (SSH disabled). Accessed via `docker exec ... telnet 127.0.0.1 5000`.
- **Tools**: `junos_show`, `frr_show`, and `clab_inspect` are updated and ready.
- **MCP Bridge**: Running on `nkchan-desktop-1` at port `9005`.

## Tasks to be performed by the next session

### 1. Initial Verification
Run the following commands via the AI agent (e.g., using Open WebUI) to confirm connectivity:
- `clab_inspect(name="vjunos-test")`
- `junos_show(container_name="vjunos1", command="show interfaces terse")`
- `frr_show(container_name="frr1", command="show ip interface brief")`

### 2. BGP Investigation
Analyze the BGP neighbor status:
- `junos_show(container_name="vjunos1", command="show bgp summary")`
- `frr_show(container_name="frr1", command="show ip bgp summary")`

Expected issue: BGP session might be `Idle` or `Active` instead of `Established` due to interface configuration or AS mismatch.

### 3. Detailed Config Analysis
If BGP is down, inspect the protocols:
- `junos_show(container_name="vjunos1", command="show configuration protocols bgp")`
- `frr_show(container_name="frr1", command="show running-config")`

### 4. Apply Fixes
Apply configuration changes if needed using:
- `junos_config` (to be tested via telnet bridge)
- `frr_config`

### 5. Final Report
Generate a summary report:
- Use `save_report(filename="bgp_verification.md", content="# ...")` to document the final state and Mermaid diagrams.
