"""Git tool: commit and get current SHA (lean, ~60 lines).

Fresh implementation for releaseproof. No code copied from any prior project.
"""
from __future__ import annotations

import subprocess

from strands import tool


@tool
def git_commit(message: str) -> str:
    """Stage all changes and create a git commit. Returns the new commit SHA.

    Args:
        message: The commit message.

    Returns:
        The new commit SHA (short), or error message.
    """
    try:
        subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10)
        r = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
            return f"Error: git commit failed: {r.stderr}"
        sha_r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return f"Committed: {sha_r.stdout.strip()}"
    except Exception as e:
        return f"Error: {e}"


@tool
def git_sha() -> str:
    """Get the current git commit SHA (short).

    Returns:
        The short commit SHA, or error message.
    """
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
        return f"Error: {r.stderr}"
    except Exception as e:
        return f"Error: {e}"
