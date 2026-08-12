"""Strands Agent setup + run loop.

This module creates the Strands Agent instance with tools, hooks, and
conversation manager, then exposes a single `run(prompt)` entrypoint.

TODO(M2): implement after Strands SDK research (M1).
"""
from __future__ import annotations


def create_agent(config):
    """Create a Strands Agent with tools, hooks, and conversation manager.

    TODO(M2): implement.
    """
    raise NotImplementedError("create_agent not yet implemented — see EXECUTION-PLAN.md M2")


def run(prompt: str, config=None) -> str:
    """Run the releaseproof agent with a user prompt.

    TODO(M2): wire to Strands Agent + tools + hooks.
    """
    raise NotImplementedError("run not yet implemented — see EXECUTION-PLAN.md M2")
