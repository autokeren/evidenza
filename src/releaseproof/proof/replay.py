"""Proof replay: render a visual Release Card from a pre-recorded proof run.

This allows judges to evaluate the proof system without any API key —
they replay a pre-recorded, verified proof artifact.

TODO(M3): implement visual rendering.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_proof_card(proof_file: str) -> None:
    """Render a visual Release Card from a pre-recorded proof run JSON.

    Args:
        proof_file: path to proof-run.json

    TODO(M3): implement rich terminal rendering.
    """
    path = Path(proof_file)
    if not path.exists():
        print(f"Error: proof file not found: {proof_file}")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    # TODO(M3): pretty-print with rich
    print(json.dumps(data, indent=2))
