"""FRR output parser.

Parses common FRR show command outputs into structured data.
"""

import re


def parse_bgp_summary(output: str) -> dict:
    """Parse 'show ip bgp summary' output.

    Args:
        output: Raw vtysh output of 'show ip bgp summary'.

    Returns:
        Dictionary with router_id, local_as, and list of neighbors.

    Example output parsed:
        IPv4 Unicast Summary:
        BGP router identifier 10.0.0.1, local AS number 65001 vrf-id 0
        ...
        Neighbor        V  AS   MsgRcvd  MsgSent  TblVer  InQ OutQ  Up/Down State/PfxRcd
        192.0.2.2       4 65002      10       12       0    0    0 00:05:30            1
    """
    result = {
        "router_id": None,
        "local_as": None,
        "neighbors": [],
    }

    # Extract router ID and local AS
    id_match = re.search(r"BGP router identifier ([\d.]+), local AS number (\d+)", output)
    if id_match:
        result["router_id"] = id_match.group(1)
        result["local_as"] = int(id_match.group(2))

    # Parse neighbor lines
    # Format: IP  V  AS  MsgRcvd  MsgSent  TblVer  InQ  OutQ  Up/Down  State/PfxRcd
    neighbor_pattern = re.compile(
        r"([\d.]+)\s+"       # Neighbor IP
        r"(\d)\s+"           # Version
        r"(\d+)\s+"          # AS
        r"(\d+)\s+"          # MsgRcvd
        r"(\d+)\s+"          # MsgSent
        r"(\d+)\s+"          # TblVer
        r"(\d+)\s+"          # InQ
        r"(\d+)\s+"          # OutQ
        r"([\d:dhm]+)\s+"   # Up/Down
        r"(\S+)"             # State/PfxRcd
    )

    for match in neighbor_pattern.finditer(output):
        state_pfx = match.group(10)
        try:
            pfx_count = int(state_pfx)
            state = "Established"
        except ValueError:
            pfx_count = 0
            state = state_pfx

        result["neighbors"].append({
            "neighbor": match.group(1),
            "version": int(match.group(2)),
            "remote_as": int(match.group(3)),
            "msg_rcvd": int(match.group(4)),
            "msg_sent": int(match.group(5)),
            "up_down": match.group(9),
            "state": state,
            "pfx_rcvd": pfx_count,
        })

    return result


def parse_ip_route(output: str) -> list[dict]:
    """Parse 'show ip route' output.

    Args:
        output: Raw vtysh output of 'show ip route'.

    Returns:
        List of route dictionaries.
    """
    routes = []
    # Match lines like: B>* 10.0.0.2/32 [20/0] via 192.0.2.2, eth1, ...
    route_pattern = re.compile(
        r"([A-Z>*]+)\s+"     # Protocol/status flags
        r"([\d./]+)\s+"      # Prefix
        r"\[(\d+)/(\d+)\]\s+"  # AD/metric
        r"via\s+([\d.]+)"    # Next hop
    )

    for match in route_pattern.finditer(output):
        routes.append({
            "flags": match.group(1),
            "prefix": match.group(2),
            "admin_distance": int(match.group(3)),
            "metric": int(match.group(4)),
            "next_hop": match.group(5),
        })

    return routes
