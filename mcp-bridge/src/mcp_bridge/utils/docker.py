"""Docker helper utilities for executing commands in containers."""

import asyncio
import logging
import shlex

logger = logging.getLogger(__name__)


async def resolve_container_name(name: str) -> str:
    """Attempt to resolve a short name to a full clab container name."""
    # If the name already starts with 'clab-', assume it's full (or try as is)
    if name.startswith("clab-"):
        return name

    # Try to find a clab container where the node name matches
    try:
        # List all clab containers and their node names
        out = await run_command("docker ps --format '{{.Names}}\t{{.Label \"clab-node-name\"}}' --filter 'label=clab-node-name'")
        for line in out.strip().split('\n'):
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                container, node = parts[0], parts[1]
                if node == name:
                    logger.info(f"Resolved short name {name} to container {container}")
                    return container
                if container.endswith(f"-{name}"):
                    logger.info(f"Resolved suffix {name} to container {container}")
                    return container
    except Exception as e:
        logger.warning(f"Failed to resolve container name {name}: {e}")

    return name


async def docker_exec(container_name: str, command: str, timeout: int = 30) -> str:
    """Execute a command inside a Docker container.

    Args:
        container_name: Name of the Docker container.
        command: Command to execute.
        timeout: Timeout in seconds.

    Returns:
        Command output as string.

    Raises:
        RuntimeError: If command execution fails.
    """
    # Resolve name before execution
    resolved_name = await resolve_container_name(container_name)
    
    cmd = f"docker exec {shlex.quote(resolved_name)} {command}"
    logger.info(f"Executing: {cmd}")

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"Command timed out after {timeout}s: {cmd}")

    output = stdout.decode("utf-8", errors="replace")
    errors = stderr.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={proc.returncode}): {cmd}\n"
            f"stdout: {output}\n"
            f"stderr: {errors}"
        )

    return output


async def run_command(command: str, timeout: int = 120) -> str:
    """Execute a shell command.

    Args:
        command: Command to execute.
        timeout: Timeout in seconds.

    Returns:
        Command output as string.

    Raises:
        RuntimeError: If command execution fails.
    """
    logger.info(f"Executing: {command}")

    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"Command timed out after {timeout}s: {command}")

    output = stdout.decode("utf-8", errors="replace")
    errors = stderr.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={proc.returncode}): {command}\n"
            f"stdout: {output}\n"
            f"stderr: {errors}"
        )

    return output
