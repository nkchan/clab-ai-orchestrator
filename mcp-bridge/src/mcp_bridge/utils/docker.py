"""Docker helper utilities for executing commands in containers."""

import asyncio
import logging
import shlex

logger = logging.getLogger(__name__)


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
    cmd = f"docker exec {shlex.quote(container_name)} {command}"
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
