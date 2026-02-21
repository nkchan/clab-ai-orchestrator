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
        """Inspect a running containerlab topology.

        Args:
            topology_file: Path to the topology YAML file (optional).
            name: Lab name to inspect (optional).

        Returns:
            Inspection output with node status.
        """
        cmd = "sudo clab inspect"
        if topology_file:
            cmd += f" -t {shlex.quote(topology_file)}"
        elif name:
            cmd += f" --name {shlex.quote(name)}"
        else:
            cmd += " --all"

        logger.info("Inspecting topology")
        return await run_command(cmd)
