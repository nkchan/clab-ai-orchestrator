# Samples — Usage Examples & Scenarios

This directory contains concrete usage scenarios for Clab AI Orchestrator.  
Each scenario is self-contained and can be followed sequentially to experience all features.

## Scenario Index

| # | Scenario | Description | Tools Used |
|---|----------|-------------|------------|
| 01 | [Deploy & Verify](01_deploy_and_verify/) | Lab deployment → BGP verification | `clab_deploy`, `clab_inspect`, `frr_show`, `junos_show` |
| 02 | [Troubleshoot BGP](02_troubleshoot_bgp/) | BGP fault investigation & repair | `frr_show`, `junos_show`, `frr_config`, `junos_config` |
| 03 | [Config Change](03_config_change/) | Configuration change & rollback | `frr_config`, `junos_config`, templates |

## Prerequisites

- Lab deployed: `sudo clab deploy -t labs/basic-bgp/topology.clab.yml`
- BGP in Established state

## How to Use

Each scenario has a `README.md` with step-by-step instructions.  
They can be executed via MCP tools (AI agent) or manual CLI commands.
