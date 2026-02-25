"""Junos (vJunos-router) operation tools."""

import logging
import shlex
import paramiko

from mcp_bridge.utils.docker import run_command

logger = logging.getLogger(__name__)


class JunosTools:
    """Junos management tools via SSH."""

    async def _run_ssh_command(self, container_name: str, command: str) -> str:
        """Helper to run command over paramiko SSH."""
        # Get container IP
        ip_cmd = f"docker inspect -f '{{{{range.NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {shlex.quote(container_name)}"
        ip = (await run_command(ip_cmd)).strip()
        if not ip:
            return f"Error: Could not find IP for container {container_name}"

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=ip, username="admin", password="admin@123", timeout=10)
            stdin, stdout, stderr = client.exec_command(command)
            err = stderr.read().decode()
            out = stdout.read().decode()
            if err:
                logger.warning(f"SSH stderr: {err}")
            return out if out else err
        except Exception as e:
            return f"SSH connection failed: {str(e)}"
        finally:
            client.close()

    async def show(self, container_name: str, command: str, fmt: str = "text") -> str:
        """Execute a show command on a vJunos node."""
        if not command.strip().startswith("show"):
            return "Error: Only 'show' commands are allowed via junos_show. Use junos_config for configuration."

        if fmt == "json" and "| display json" not in command:
            command = f"{command} | display json"

        logger.info(f"Junos show on {container_name}: {command}")
        return await self._run_ssh_command(container_name, command)

    async def configure(self, container_name: str, config_commands: list[str]) -> str:
        """Push set-style configuration to a vJunos node."""
        # Note: junos requires commands to be fed into 'cli' session or netconf.
        # paramiko exec_command does not start an interactive cli shell by default for commands, 
        # so we pipe them into 'cli' just like before.
        commands = ["configure"] + config_commands + ["commit and-quit"]
        combined_cmds = "\n".join(commands)
        
        logger.info(f"Junos config on {container_name}: {len(config_commands)} commands")
        cmd_wrapper = f"echo {shlex.quote(combined_cmds)} | cli"
        result = await self._run_ssh_command(container_name, cmd_wrapper)
        return f"Configuration committed:\n{result}"
