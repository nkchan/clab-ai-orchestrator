"""Junos output parser.

Parses common Junos show command outputs into structured data.
Junos supports native JSON output via '| display json', which is preferred.
This module handles both text and JSON parsing.
"""

import json
import re


def parse_bgp_summary(output: str, fmt: str = "text") -> dict:
    """Parse 'show bgp summary' output.

    Args:
        output: Raw CLI output of 'show bgp summary'.
        fmt: Output format - 'text' or 'json'.

    Returns:
        Dictionary with router_id, local_as, and list of peers.
    """
    if fmt == "json":
        return _parse_bgp_summary_json(output)
    return _parse_bgp_summary_text(output)


def _parse_bgp_summary_json(output: str) -> dict:
    """Parse JSON format BGP summary."""
    try:
        data = json.loads(output)
        # Navigate Junos JSON structure
        bgp_info = data.get("bgp-information", [{}])[0]
        result = {
            "router_id": None,
            "local_as": None,
            "peers": [],
        }

        for peer in bgp_info.get("bgp-peer", []):
            result["peers"].append({
                "peer_address": peer.get("peer-address", [{}])[0].get("data", ""),
                "peer_as": int(peer.get("peer-as", [{}])[0].get("data", 0)),
                "state": peer.get("peer-state", [{}])[0].get("data", ""),
                "elapsed_time": peer.get("elapsed-time", [{}])[0].get("data", ""),
            })

        return result
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"error": f"Failed to parse JSON: {e}", "raw": output}


def _parse_bgp_summary_text(output: str) -> dict:
    """Parse text format BGP summary.

    Example Junos output:
        Threading mode: BGP I/O
        ...
        Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
        192.0.2.1             65001         10         12       0       0        5:30 Establ
    """
    result = {
        "router_id": None,
        "local_as": None,
        "peers": [],
    }

    # Extract local AS
    as_match = re.search(r"AS:\s*(\d+)", output)
    if as_match:
        result["local_as"] = int(as_match.group(1))

    # Parse peer lines
    peer_pattern = re.compile(
        r"([\d.]+)\s+"      # Peer address
        r"(\d+)\s+"         # AS
        r"(\d+)\s+"         # InPkt
        r"(\d+)\s+"         # OutPkt
        r"(\d+)\s+"         # OutQ
        r"(\d+)\s+"         # Flaps
        r"([\d:]+)\s+"      # Last Up/Dwn
        r"(\S+)"            # State
    )

    for match in peer_pattern.finditer(output):
        state = match.group(8)
        result["peers"].append({
            "peer_address": match.group(1),
            "peer_as": int(match.group(2)),
            "in_packets": int(match.group(3)),
            "out_packets": int(match.group(4)),
            "flaps": int(match.group(6)),
            "elapsed_time": match.group(7),
            "state": state,
        })

    return result


def parse_route_table(output: str) -> list[dict]:
    """Parse 'show route' text output.

    Args:
        output: Raw CLI output of 'show route'.

    Returns:
        List of route dictionaries.
    """
    routes = []
    # Match lines like: * 10.0.0.1/32    BGP    170  100   ...  > 192.0.2.1
    route_pattern = re.compile(
        r"[*]\s+"              # Active flag
        r"([\d./]+)\s+"        # Prefix
        r"(\w+)\s+"            # Protocol
        r"(\d+)\s+"            # Preference
        r".*?>\s*([\d.]+)"     # Next hop
    )

    for match in route_pattern.finditer(output):
        routes.append({
            "prefix": match.group(1),
            "protocol": match.group(2),
            "preference": int(match.group(3)),
            "next_hop": match.group(4),
        })

    return routes
