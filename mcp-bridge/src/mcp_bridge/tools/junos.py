"""Junos (vJunos-router) operation tools."""

import logging
import shlex
import paramiko

from mcp_bridge.utils.docker import run_command

logger = logging.getLogger(__name__)


class JunosTools:
    """Junos management tools via SSH."""

    async def _run_ssh_command(self, container_name: str, command: str) -> str:
        """Helper to run command over docker exec telnet to bypass SSH failure."""
        cmd_wrapper = f"(echo 'cli'; sleep 1; echo {shlex.quote(command)}; sleep 1) | telnet 127.0.0.1 5000"
        
        docker_cmd = f"docker exec -i {shlex.quote(container_name)} sh -c {shlex.quote(cmd_wrapper)}"
        
        try:
            out = await run_command(docker_cmd)
            # Remove the telnet connection messages and CLI prompt noise
            lines = out.split("\n")
            filtered_lines = []
            capture = False
            for line in lines:
                if line.strip() == command.strip():
                    capture = True
                    continue
                if line.strip() == "cli" or line.strip() == "Password:Connection closed by foreign host." or line.strip().startswith("Trying 127.0.0.1") or line.strip().startswith("Connected to") or line.strip().startswith("Escape character is"):
                    continue
                if capture:
                    # stop capturing if we hit another prompt
                    if line.strip().startswith("root>") or line.strip().startswith("root@"):
                        capture = False
                        break
                    filtered_lines.append(line)
            
            # If nothing was captured via exact match, fallback to just returning all but prompt
            if not filtered_lines:
                return "\n".join([l for l in lines if not any(p in l for p in ["Trying 127.0.0.1", "Connected to", "Escape character", "login:", "Password:", "Connection closed by foreign host"])])
            
            return "\n".join(filtered_lines).strip()
        except Exception as e:
            return f"Telnet connection failed: {str(e)}"

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
