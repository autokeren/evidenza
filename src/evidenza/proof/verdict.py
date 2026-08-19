"""Verdict logic: SHIP / BLOCKED / NEEDS_HUMAN_REVIEW.

Given a list of acceptance criteria with statuses, compute the release verdict.

This is a fresh, lean reimplementation of the evidence-led verdict concept
(not copied from any prior project).
"""
from __future__ import annotations

from typing import Any


def compute_verdict(criteria: list[dict[str, Any]]) -> str:
    """Compute release verdict from acceptance criteria.

    Args:
        criteria: list of criterion dicts, each with a "status" key.
            Status values: "pending" | "passed" | "failed" | "blocked" | "manual_review"

    Returns:
        "SHIP" | "BLOCKED" | "NEEDS_HUMAN_REVIEW"

    Rules:
        - Any "failed" or "blocked" → BLOCKED
        - Any "manual_review" (and no failed/blocked) → NEEDS_HUMAN_REVIEW
        - All "passed" → SHIP
        - Otherwise (pending or mix) → NEEDS_HUMAN_REVIEW
    """
    statuses = [c.get("status", "pending") for c in criteria]

    if not statuses:
        return "NEEDS_HUMAN_REVIEW"

    if any(s in ("failed", "blocked") for s in statuses):
        return "BLOCKED"

    if any(s == "manual_review" for s in statuses):
        return "NEEDS_HUMAN_REVIEW"

    if all(s == "passed" for s in statuses):
        return "SHIP"

    return "NEEDS_HUMAN_REVIEW"
