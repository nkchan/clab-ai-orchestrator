# Vendors

Vendor-specific parsers and configuration templates.

## Structure

```
vendors/
├── frr/
│   ├── parser.py          # FRR show command output parser
│   └── templates/
│       └── bgp.conf.j2    # BGP config template
└── junos/
    ├── parser.py          # Junos show command output parser
    └── templates/
        └── bgp.conf.j2    # BGP config template
```

## Parsers

### FRR (`frr/parser.py`)
- `parse_bgp_summary()` — Parses `show ip bgp summary` into structured data
- `parse_ip_route()` — Parses `show ip route` into structured data

### Junos (`junos/parser.py`)
- `parse_bgp_summary()` — Parses `show bgp summary` (text/JSON) into structured data
- `parse_route_table()` — Parses `show route` into structured data

## Templates

Jinja2-format configuration templates for generating new lab configs.

### Usage Example
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("vendors/frr/templates"))
template = env.get_template("bgp.conf.j2")
config = template.render(
    hostname="frr1",
    router_id="10.0.0.1",
    local_as=65001,
    neighbor_ip="192.0.2.2",
    remote_as=65002,
    loopback_ip="10.0.0.1/32",
    p2p_ip="192.0.2.1/30",
    p2p_interface="eth1",
)
```

## Adding a New Vendor

1. Create `vendors/<vendor_name>/` directory
2. Implement `parser.py` with show command parsers
3. Add Jinja2 templates in `templates/`
4. Add corresponding tools in `mcp-bridge/src/mcp_bridge/tools/`
