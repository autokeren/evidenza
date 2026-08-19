"""Deploy tool: simplified publish (lean, ~80 lines).

Fresh implementation for releaseproof. No code copied from any prior project.

This is a SIMPLIFIED deploy for demo purposes. In a real scenario, this would
publish to a platform (e.g., Cloudflare Pages, AWS, etc.). For the hackathon
demo, we simulate a deploy and return a URL.
"""
from __future__ import annotations

import hashlib
import time

from strands import tool


@tool
def deploy(app_path: str, proof_id: str) -> str:
    """Deploy an app and return its public URL. Requires an approved proof.

    Args:
        app_path: Path to the app directory or entry file to deploy.
        proof_id: The approved proof ID (must be SHIP + approved).

    Returns:
        The deployed URL, or error if proof not approved.
    """
    # In a real implementation, this would:
    # 1. Check proof_id is approved (SHIP + human approval)
    # 2. Check git SHA matches the proof's recorded SHA
    # 3. Deploy to platform
    # 4. Return URL

    # For demo: simulate deploy with a hash-based URL
    deploy_hash = hashlib.sha256(f"{proof_id}{app_path}{time.time()}".encode()).hexdigest()[:8]
    url = f"https://app-{deploy_hash}.releaseproof.dev"

    # Simulate brief deploy time
    time.sleep(1)

    return f"Deployed {app_path} to {url}\nProof: {proof_id}\nStatus: LIVE"
