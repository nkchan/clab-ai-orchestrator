# Sample 03: Config Change

Use Jinja2 templates to generate configs, push to FRR/vJunos, and verify propagation.

## Scenario

Add a new loopback network to FRR1's BGP advertisements.

```
Before: FRR1 advertises 10.0.0.1/32 only
After:  FRR1 advertises 10.0.0.1/32 + 10.1.0.0/24
```

## Steps

### Step 1: Check Current Routes

```json
{
  "tool": "junos_show",
  "arguments": {
    "container_name": "clab-basic-bgp-vjunos1",
    "command": "show route receive-protocol bgp 192.0.2.1"
  }
}
```

**Expected:** Only 10.0.0.1/32

### Step 2: Generate Config from Template

```python
# Example using vendors/frr/templates
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("vendors/frr/templates"))

config_lines = [
    "router bgp 65001",
    "address-family ipv4 unicast",
    "network 10.1.0.0/24",
    "exit-address-family",
]
```

### Step 3: Push Config to FRR

**MCP Tool:**
```json
{
  "tool": "frr_config",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "config_commands": [
      "interface lo",
      "ip address 10.1.0.1/24",
      "exit",
      "router bgp 65001",
      "address-family ipv4 unicast",
      "network 10.1.0.0/24",
      "exit-address-family"
    ]
  }
}
```

### Step 4: Verify Advertisement

```json
{
  "tool": "frr_show",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "command": "show ip bgp"
  }
}
```

### Step 5: Verify Reception on vJunos

```json
{
  "tool": "junos_show",
  "arguments": {
    "container_name": "clab-basic-bgp-vjunos1",
    "command": "show route receive-protocol bgp 192.0.2.1"
  }
}
```

**Expected:** 10.0.0.1/32 + 10.1.0.0/24

### Step 6: Rollback

```json
{
  "tool": "frr_config",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "config_commands": [
      "interface lo",
      "no ip address 10.1.0.1/24",
      "exit",
      "router bgp 65001",
      "address-family ipv4 unicast",
      "no network 10.1.0.0/24",
      "exit-address-family"
    ]
  }
}
```

## What You Learn

- Using Jinja2 templates for config generation
- Network advertisement workflow
- Cross-vendor route propagation verification (FRR ↔ Junos)
- Configuration rollback
