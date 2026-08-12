"""Proof manager: plan/record/report state machine.

Manages acceptance criteria lifecycle:
    PLAN → RECORD → REPORT → (REPLAY)

Each proof run is stored as JSON (proof-run.json) and can be replayed
without an API key (for judge evaluation).

TODO(M2/M3): implement full state machine.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ProofManager:
    """Manages proof plans and recorded evidence for release verification.

    TODO(M3): implement plan/record/report/replay.
    """

    def __init__(self, proofs_dir: Path | None = None) -> None:
        self.proofs_dir = proofs_dir or Path.cwd() / ".releaseproof" / "proofs"
        self.proofs_dir.mkdir(parents=True, exist_ok=True)

    def create_plan(self, title: str, criteria: list[str]) -> str:
        """Create a new proof plan with acceptance criteria.

        Returns: proof_id (timestamp-based).
        TODO(M3): implement.
        """
        raise NotImplementedError("create_plan not yet implemented — see EXECUTION-PLAN.md M3")

    def record(self, proof_id: str, criterion_num: int, status: str, evidence: str) -> None:
        """Record verification evidence for a criterion.

        TODO(M3): implement.
        """
        raise NotImplementedError("record not yet implemented — see EXECUTION-PLAN.md M3")

    def get(self, proof_id: str) -> list[dict[str, Any]]:
        """Retrieve all criteria for a proof run.

        TODO(M3): implement.
        """
        raise NotImplementedError("get not yet implemented — see EXECUTION-PLAN.md M3")

    def report(self, proof_id: str) -> dict[str, Any]:
        """Generate a report for a proof run, including the verdict.

        TODO(M3): implement.
        """
        raise NotImplementedError("report not yet implemented — see EXECUTION-PLAN.md M3")


def _timestamp() -> str:
    """Generate a UTC timestamp for proof IDs (not using time-dependent APIs in scripts)."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
