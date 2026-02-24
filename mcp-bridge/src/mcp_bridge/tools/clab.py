"""Containerlab operation tools."""

import logging
import shlex

from mcp_bridge.utils.docker import run_command

logger = logging.getLogger(__name__)


class ClabTools:
    """Containerlab management tools."""

    async def deploy(self, topology_file: str, reconfigure: bool = False) -> str:
        """Deploy a containerlab topology.

        Args:
            topology_file: Path to the topology YAML file.
            reconfigure: If True, reconfigure existing lab.

        Returns:
            Deployment output.
        """
        cmd = f"sudo clab deploy -t {shlex.quote(topology_file)}"
        if reconfigure:
            cmd += " --reconfigure"

        logger.info(f"Deploying topology: {topology_file}")
        return await run_command(cmd, timeout=300)

    async def destroy(self, topology_file: str, cleanup: bool = False) -> str:
        """Destroy a running containerlab topology.

        Args:
            topology_file: Path to the topology YAML file.
            cleanup: If True, remove lab directory.

        Returns:
            Destroy output.
        """
        cmd = f"sudo clab destroy -t {shlex.quote(topology_file)}"
        if cleanup:
            cmd += " --cleanup"

        logger.info(f"Destroying topology: {topology_file}")
        return await run_command(cmd, timeout=120)

    async def inspect(self, topology_file: str | None = None, name: str | None = None) -> str:
        """Inspect running containerlab nodes.

        Uses 'docker ps' to discover running clab containers since
        containerlab state lives on the host, not inside the mcp-bridge
        container.

        Args:
            topology_file: Unused (kept for API compat). Ignored.
            name: Lab name filter (e.g., 'vjunos-test' matches 'clab-vjunos-test-*').

        Returns:
            Table of running containerlab containers.
        """
        cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' --filter 'label=clab-node-name'"
        if name:
            cmd += f" --filter 'name=clab-{shlex.quote(name)}'"

        logger.info(f"Inspecting clab containers (filter: {name or 'all'})")
        return await run_command(cmd)
