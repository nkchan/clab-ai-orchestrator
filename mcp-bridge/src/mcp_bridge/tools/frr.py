"""FRR (FRRouting) operation tools."""

import logging
import shlex

from mcp_bridge.utils.docker import docker_exec

logger = logging.getLogger(__name__)


class FrrTools:
    """FRR management tools via vtysh."""

    async def show(self, container_name: str, command: str) -> str:
        """Execute a show command on an FRR node.

        Args:
            container_name: Docker container name.
            command: Show command (e.g., 'show ip bgp summary').

        Returns:
            Command output.
        """
        # Ensure command starts with 'show' for safety
        if not command.strip().startswith("show"):
            return "Error: Only 'show' commands are allowed via frr_show. Use frr_config for configuration."

        vtysh_cmd = f"vtysh -c {shlex.quote(command)}"
        logger.info(f"FRR show on {container_name}: {command}")
        return await docker_exec(container_name, vtysh_cmd)

    async def configure(self, container_name: str, config_commands: list[str]) -> str:
        """Push configuration to an FRR node.

        Wraps commands in 'configure terminal' context.

        Args:
            container_name: Docker container name.
            config_commands: List of configuration commands.

        Returns:
            Configuration output.
        """
        # Build vtysh command with config terminal wrapper
        all_commands = ["configure terminal"] + config_commands + ["end", "write memory"]
        vtysh_args = " ".join(f"-c {shlex.quote(cmd)}" for cmd in all_commands)
        vtysh_cmd = f"vtysh {vtysh_args}"

        logger.info(f"FRR config on {container_name}: {len(config_commands)} commands")
        result = await docker_exec(container_name, vtysh_cmd)

        # Verify config was saved
        verify = await docker_exec(container_name, "vtysh -c 'show running-config'")
        return f"Configuration applied:\n{result}\n\n--- Running config (excerpt) ---\n{verify[:2000]}"
