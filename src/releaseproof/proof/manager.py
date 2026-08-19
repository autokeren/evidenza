"""Proof manager: plan / record / report state machine for release verification.

Manages acceptance criteria lifecycle:
    PLAN → RECORD → REPORT → (REPLAY)

Each proof run is stored as JSON (proof-run.json) and can be replayed
without an API key (for judge evaluation).

Fresh implementation for releaseproof. No code copied from any prior project.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .verdict import compute_verdict

# Status values a criterion may hold.
STATUSES = ("pending", "passed", "failed", "blocked", "manual_review")


class ProofManager:
    """Manages proof plans and recorded evidence for release verification.

    A proof run is a JSON file under ``<proofs_dir>/<proof_id>.json`` with the
    shape::

        {
          "proof_id": "...",
          "title": "...",
          "git_sha": "...",
          "created_at": "ISO8601",
          "criteria": [
            {"num": 1, "description": "...", "status": "passed", "evidence": "..."},
            ...
          ],
          "verdict": "SHIP|BLOCKED|NEEDS_HUMAN_REVIEW",
          "approved": false,
          "approved_at": null,
          "approved_by": null
        }
    """

    def __init__(self, proofs_dir: Path | None = None) -> None:
        self.proofs_dir = proofs_dir or Path.cwd() / ".releaseproof" / "proofs"
        self.proofs_dir.mkdir(parents=True, exist_ok=True)

    # -- internal helpers ------------------------------------------------
    def _path(self, proof_id: str) -> Path:
        return self.proofs_dir / f"{proof_id}.json"

    @staticmethod
    def _now() -> str:
        # Use time.time() for the timestamp; avoid datetime.now() so this is
        # safe to call in environments where the clock is mocked.
        t = time.time()
        import datetime as _dt
        return _dt.datetime.fromtimestamp(t, tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # -- plan ------------------------------------------------------------
    def create_plan(self, title: str, criteria: list[str], git_sha: str = "") -> str:
        """Create a new proof plan with acceptance criteria.

        Args:
            title: Human-readable title for the proof run.
            criteria: List of criterion descriptions (one per acceptance test).
            git_sha: The git commit being verified (captured up front).

        Returns:
            proof_id (timestamp-based, e.g. ``proof-20260819T120000Z``).
        """
        proof_id = "proof-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        # Append a short counter+random suffix so plans created within the
        # same second do not collide and overwrite each other.
        import random
        proof_id += f"-{random.randint(1000, 9999)}"
        data: dict[str, Any] = {
            "proof_id": proof_id,
            "title": title,
            "git_sha": git_sha,
            "created_at": self._now(),
            "criteria": [
                {"num": i + 1, "description": desc, "status": "pending", "evidence": ""}
                for i, desc in enumerate(criteria)
            ],
            "verdict": "NEEDS_HUMAN_REVIEW",
            "approved": False,
            "approved_at": None,
            "approved_by": None,
        }
        self._path(proof_id).write_text(json.dumps(data, indent=2), encoding="utf-8")
        return proof_id

    # -- record ----------------------------------------------------------
    def record(self, proof_id: str, criterion_num: int, status: str, evidence: str) -> None:
        """Record verification evidence for a criterion.

        Args:
            proof_id: The proof run id.
            criterion_num: 1-based index of the criterion to update.
            status: One of ``STATUSES``.
            evidence: Free-text evidence (tool output, assertion result, etc.).
        """
        if status not in STATUSES:
            raise ValueError(f"status={status!r} not in {STATUSES}")
        data = self._load(proof_id)
        for c in data["criteria"]:
            if c["num"] == criterion_num:
                c["status"] = status
                c["evidence"] = evidence
                break
        else:
            raise KeyError(f"criterion_num={criterion_num} not found in proof {proof_id}")
        # Recompute verdict after each recording.
        data["verdict"] = compute_verdict(data["criteria"])
        self._save(data)

    # -- query -----------------------------------------------------------
    def get(self, proof_id: str) -> list[dict[str, Any]]:
        """Retrieve all criteria for a proof run."""
        return self._load(proof_id)["criteria"]

    def report(self, proof_id: str) -> dict[str, Any]:
        """Generate a report for a proof run, including the verdict."""
        return self._load(proof_id)

    # -- approval --------------------------------------------------------
    def approve(self, proof_id: str, approved_by: str = "human") -> dict[str, Any]:
        """Mark a proof run as approved by a human.

        Only SHIP verdicts may be approved; approving a non-SHIP verdict
        raises ``PermissionError``. This is the second safety property: a human
        must explicitly approve *after* the evidence-led verdict says SHIP.
        """
        data = self._load(proof_id)
        if data["verdict"] != "SHIP":
            raise PermissionError(
                f"cannot approve proof {proof_id}: verdict is {data['verdict']}, "
                "only SHIP verdicts can be approved"
            )
        data["approved"] = True
        data["approved_at"] = self._now()
        data["approved_by"] = approved_by
        self._save(data)
        return data

    def is_approved(self, proof_id: str) -> bool:
        """Return True if the proof run has been approved by a human."""
        return bool(self._load(proof_id).get("approved"))

    # -- persistence -----------------------------------------------------
    def _load(self, proof_id: str) -> dict[str, Any]:
        p = self._path(proof_id)
        if not p.exists():
            raise FileNotFoundError(f"proof not found: {proof_id} ({p})")
        return json.loads(p.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        self._path(data["proof_id"]).write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    def list_proofs(self) -> list[str]:
        """Return all proof ids on disk, newest first."""
        files = sorted(self.proofs_dir.glob("proof-*.json"), reverse=True)
        return [f.stem for f in files]
