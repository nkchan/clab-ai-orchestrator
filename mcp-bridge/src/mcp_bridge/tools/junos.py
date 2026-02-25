"""Junos (vJunos-router) operation tools."""

import logging
import shlex
import paramiko

from mcp_bridge.utils.docker import run_command, resolve_container_name

logger = logging.getLogger(__name__)


class JunosTools:
    """Junos management tools via SSH."""

    async def _run_ssh_command(self, container_name: str, command: str) -> str:
        """Helper to run command over docker exec telnet to bypass SSH failure."""
        # Resolve name before execution
        resolved_name = await resolve_container_name(container_name)
        
        # Use a more robust sequence: extra newlines, clear pager, enter cli (if needed), execute
        # Sending 'q' helps if a previous session left a pager open
        cmd_wrapper = (
            f"(printf '\\r\\n'; sleep 0.5; "
            f"echo 'q'; sleep 0.5; "
            f"echo 'cli'; sleep 1; "
            f"echo 'set cli screen-length 0'; sleep 0.5; "
            f"echo {shlex.quote(command)}; sleep 2) | telnet 127.0.0.1 5000"
        )
        
        docker_cmd = f"docker exec -i {shlex.quote(resolved_name)} sh -c {shlex.quote(cmd_wrapper)}"
        
        try:
            out = await run_command(docker_cmd)
            # Remove the telnet connection messages and CLI prompt noise
            lines = out.split("\n")
            filtered_lines = []
            capture = False
            
            # Identify the command line to start capturing after it
            cmd_norm = command.strip()
            
            for line in lines:
                lstrip = line.strip()
                
                # Start capturing AFTER the command echo
                if not capture and cmd_norm in lstrip:
                    capture = True
                    continue
                
                if capture:
                    # stop capturing if we hit another prompt
                    if lstrip.startswith("root>") or lstrip.startswith("root@"):
                        # If it's a prompt but we've already captured some meaningful output, stop
                        if any(l.strip() for l in filtered_lines):
                             break
                        else:
                             # Just another prompt before the output, keep going
                             continue
                    
                    # Skip common noisy lines
                    if lstrip in ["cli", "q", "set cli screen-length 0", "Screen length set to 0", "unknown command."]:
                        continue
                    if "Connection closed by foreign host" in lstrip or "Trying 127.0.0.1" in lstrip:
                        continue
                        
                    filtered_lines.append(line)
            
            # Fallback if nothing was captured via logic
            if not filtered_lines:
                return "\n".join([l for l in lines if not any(p in l for p in ["Trying 127.0.0.1", "Connected to", "Escape character", "login:", "Password:", "Connection closed by foreign host", "root>", "root@"])])
            
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
