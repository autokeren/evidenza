"""Human-in-the-loop SHIP approval via Strands hooks.

The core safety mechanism of releaseproof: the agent may gather evidence and
compute a verdict autonomously, but it CANNOT deploy without a human
explicitly approving the SHIP decision. We enforce this by registering a
``BeforeToolCallEvent`` hook that intercepts the ``deploy`` tool call: if the
referenced proof has not been approved by a human, the hook raises an
``InterruptException``, pausing the agent until the human responds.

This is the "Agents for Humans" angle made concrete: autonomous up to the
point of impact, human-in-the-loop at the moment that matters.

Fresh implementation for releaseproof. No code copied from any prior project.
"""
from __future__ import annotations

from typing import Any

from strands.hooks import BeforeToolCallEvent, HookCallback
from strands.interrupt import Interrupt, InterruptException

from .proof.manager import ProofManager

# The tool name we intercept. Only the deploy tool is gated by human approval.
DEPLOY_TOOL_NAME = "deploy"


def make_approval_hook(proofs: ProofManager) -> HookCallback:
    """Create a hook callback that gates `deploy` behind human approval.

    Args:
        proofs: The ProofManager used to check approval status.

    Returns:
        A hook callback for ``BeforeToolCallEvent``.
    """

    async def approval_hook(event: BeforeToolCallEvent) -> None:
        # Only act on the deploy tool.
        tool_use: dict[str, Any] = event.tool_use
        if tool_use.get("name") != DEPLOY_TOOL_NAME:
            return

        # The deploy tool takes a proof_id argument; if missing, block.
        tool_input = tool_use.get("input") or {}
        proof_id = tool_input.get("proof_id")
        if not proof_id:
            event.cancel_tool = "deploy requires an approved proof_id; none provided."
            return

        try:
            report = proofs.report(proof_id)
        except FileNotFoundError:
            event.cancel_tool = f"proof {proof_id!r} not found; cannot deploy."
            return

        verdict = report.get("verdict")
        if verdict != "SHIP":
            event.cancel_tool = (
                f"proof {proof_id} verdict is {verdict}; only SHIP proofs may deploy."
            )
            return

        if proofs.is_approved(proof_id):
            # Already approved by a human — let the deploy proceed.
            return

        # Not yet approved → pause for human-in-the-loop approval.
        raise InterruptException(Interrupt(
            id=f"v1:before_tool_call:{tool_use.get('toolUseId','deploy')}:approve_ship",
            name="approve_ship",
            reason=(
                f"Agent wants to DEPLOY (proof {proof_id}, verdict SHIP). "
                f"Human approval required. Reply 'yes' to approve, 'no' to reject."
            ),
        ))

    return approval_hook
