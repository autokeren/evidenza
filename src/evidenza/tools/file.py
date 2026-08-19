"""File tools: read_file and write_file (lean, ~100 lines total).

Fresh implementation for evidenza. No code copied from any prior project.
"""
from __future__ import annotations

from pathlib import Path

from strands import tool


@tool
def read_file(path: str) -> str:
    """Read the contents of a file at the given path.

    Args:
        path: Relative or absolute file path.

    Returns:
        The file contents as a string, or an error message.
    """
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: file not found: {path}"
        if not p.is_file():
            return f"Error: not a file: {path}"
        content = p.read_text(encoding="utf-8")
        if len(content) > 50000:
            content = content[:50000] + "\n... truncated"
        return content
    except Exception as e:
        return f"Error reading {path}: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path. Creates parent dirs if needed.

    Args:
        path: Relative or absolute file path.
        content: The text content to write.

    Returns:
        Success confirmation or error message.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"
