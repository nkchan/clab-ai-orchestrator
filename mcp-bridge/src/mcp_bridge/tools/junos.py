"""Junos (vJunos-router) operation tools."""

import logging
import shlex

from mcp_bridge.utils.docker import docker_exec

logger = logging.getLogger(__name__)


class JunosTools:
    """Junos management tools via CLI."""

    async def show(self, container_name: str, command: str, fmt: str = "text") -> str:
        """Execute a show command on a vJunos node.

        Args:
            container_name: Docker container name.
            command: Show command (e.g., 'show bgp summary').
            fmt: Output format - 'text' or 'json'.

        Returns:
            Command output.
        """
        if not command.strip().startswith("show"):
            return "Error: Only 'show' commands are allowed via junos_show. Use junos_config for configuration."

        # Format the command for Junos CLI
        if fmt == "json" and "| display json" not in command:
            command = f"{command} | display json"

        cli_cmd = f"cli -c {shlex.quote(command)}"
        logger.info(f"Junos show on {container_name}: {command}")
        return await docker_exec(container_name, cli_cmd, timeout=60)

    async def configure(self, container_name: str, config_commands: list[str]) -> str:
        """Push set-style configuration to a vJunos node.

        Args:
            container_name: Docker container name.
            config_commands: List of set-style commands (e.g., ['set protocols bgp ...']).

        Returns:
            Configuration output.
        """
        # Build a single CLI session with configure/commit
        commands = (
            ["configure"]
            + config_commands
            + ["commit and-quit"]
        )

        # Join commands for a single cli invocation
        combined = " && ".join(f"cli -c {shlex.quote(cmd)}" for cmd in commands)

        logger.info(f"Junos config on {container_name}: {len(config_commands)} commands")
        result = await docker_exec(container_name, f"sh -c {shlex.quote(combined)}", timeout=120)

        return f"Configuration committed:\n{result}"
