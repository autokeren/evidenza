"""Shell tool: run a command and capture output (lean, ~80 lines).

Fresh implementation for releaseproof. No code copied from any prior project.
"""
from __future__ import annotations

import subprocess

from strands import tool


@tool
def shell(command: str, timeout: int = 60) -> str:
    """Run a shell command and return its output (stdout + stderr).

    Args:
        command: The shell command to execute.
        timeout: Max execution time in seconds (default 60).

    Returns:
        Combined stdout and stderr output, or error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        if not output:
            output = "(no output)"
        if len(output) > 20000:
            output = output[:20000] + "\n... truncated"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"
