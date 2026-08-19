"""Verify URL tool: check if a deployed URL is alive (lean, ~40 lines).

Fresh implementation for evidenza. No code copied from any prior project.
"""
from __future__ import annotations

import httpx

from strands import tool


@tool
def verify_url(url: str, timeout: int = 15) -> str:
    """Check if a URL is reachable and return its HTTP status code.

    Args:
        url: The URL to check (must include http:// or https://).
        timeout: Request timeout in seconds (default 15).

    Returns:
        The HTTP status code and a brief description, or error message.
    """
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True)
        status_desc = {
            200: "OK", 201: "Created", 204: "No Content",
            301: "Moved Permanently", 302: "Found",
            400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
            404: "Not Found", 500: "Internal Server Error",
        }.get(resp.status_code, "Unknown")
        return f"HTTP {resp.status_code} ({status_desc}) — {url}"
    except httpx.TimeoutException:
        return f"Error: timeout after {timeout}s — {url}"
    except httpx.ConnectError:
        return f"Error: connection failed — {url}"
    except Exception as e:
        return f"Error: {e}"
