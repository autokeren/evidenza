"""Tests for M3: ProofManager lifecycle, replay rendering, and the
human-in-the-loop approval hook.

These are deterministic (no network / no live model) and cover the two safety
properties that make evidenza defensible:
  1. A SHIP verdict is never auto-deployed — it must pass the approval hook.
  2. Approving a non-SHIP verdict is rejected.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from evidenza.proof.manager import ProofManager
from evidenza.proof.replay import render_proof_card
from evidenza.approval import make_approval_hook
from strands.hooks import BeforeToolCallEvent
from strands.interrupt import InterruptException


# --- helpers ------------------------------------------------------------

def _make_event(proof_id, tool_use_id="tool_1"):
    class FakeAgent:
        pass
    return BeforeToolCallEvent(
        agent=FakeAgent(),
        selected_tool=None,
        tool_use={"name": "deploy", "toolUseId": tool_use_id,
                  "input": {"proof_id": proof_id, "app_path": "/app"}},
        invocation_state={},
    )


def _run_hook(hook, event):
    """Run an async hook callback synchronously and return its behavior."""
    async def _go():
        await hook(event)
    return asyncio.new_event_loop().run_until_complete(_go())


# --- ProofManager ------------------------------------------------------

def test_plan_record_ship(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["tests pass", "lint clean"], git_sha="abc123")
    pm.record(pid, 1, "passed", "pytest: 7 passed")
    pm.record(pid, 2, "passed", "ruff: clean")
    report = pm.report(pid)
    assert report["verdict"] == "SHIP"
    assert report["git_sha"] == "abc123"
    assert len(report["criteria"]) == 2


def test_record_failed_blocks(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a", "b"])
    pm.record(pid, 1, "passed", "ok")
    pm.record(pid, 2, "failed", "segfault")
    assert pm.report(pid)["verdict"] == "BLOCKED"


def test_record_manual_review(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    pm.record(pid, 1, "manual_review", "can't verify offline")
    assert pm.report(pid)["verdict"] == "NEEDS_HUMAN_REVIEW"


def test_approve_only_ship(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    pm.record(pid, 1, "failed", "boom")
    # BLOCKED verdict cannot be approved.
    import pytest
    with pytest.raises(PermissionError):
        pm.approve(pid)
    # Now make it SHIP and approve.
    pm.record(pid, 1, "passed", "fixed")
    pm.approve(pid, "tester")
    assert pm.is_approved(pid) is True


def test_invalid_status_rejected(tmp_path):
    import pytest
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    with pytest.raises(ValueError):
        pm.record(pid, 1, "bogus", "x")


def test_list_proofs(tmp_path):
    pm = ProofManager(tmp_path)
    pm.create_plan("a", ["x"])
    pm.create_plan("b", ["y"])
    assert len(pm.list_proofs()) == 2


# --- replay -------------------------------------------------------------

def test_replay_returns_data(capsys):
    # Use the committed demo proof artifact.
    demo = Path(__file__).resolve().parent.parent / "examples" / "demo" / "proof-run.json"
    data = render_proof_card(str(demo))
    assert data is not None
    assert data["verdict"] == "SHIP"
    captured = capsys.readouterr()
    assert "SHIP" in captured.out


def test_replay_missing_file(capsys):
    data = render_proof_card("/nonexistent/proof.json")
    assert data is None
    captured = capsys.readouterr()
    assert "not found" in captured.err


# --- approval hook ------------------------------------------------------

def test_hook_interrupts_unapproved_ship(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    pm.record(pid, 1, "passed", "ok")
    assert pm.report(pid)["verdict"] == "SHIP"
    assert not pm.is_approved(pid)

    hook = make_approval_hook(pm)
    event = _make_event(pid)
    import pytest
    with pytest.raises(InterruptException) as exc_info:
        _run_hook(hook, event)
    assert exc_info.value.interrupt.name == "approve_ship"


def test_hook_passes_after_approval(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    pm.record(pid, 1, "passed", "ok")
    pm.approve(pid)
    hook = make_approval_hook(pm)
    event = _make_event(pid)
    _run_hook(hook, event)  # should NOT raise


def test_hook_blocks_non_ship_verdict(tmp_path):
    pm = ProofManager(tmp_path)
    pid = pm.create_plan("v1.0", ["a"])
    pm.record(pid, 1, "failed", "boom")
    hook = make_approval_hook(pm)
    event = _make_event(pid)
    _run_hook(hook, event)
    # cancel_tool should be set because verdict is BLOCKED.
    assert event.cancel_tool
    assert "BLOCKED" in event.cancel_tool or "only SHIP" in event.cancel_tool


def test_hook_blocks_missing_proof_id(tmp_path):
    pm = ProofManager(tmp_path)
    hook = make_approval_hook(pm)
    class FakeAgent:
        pass
    event = BeforeToolCallEvent(
        agent=FakeAgent(), selected_tool=None,
        tool_use={"name": "deploy", "toolUseId": "t1", "input": {"app_path": "/app"}},
        invocation_state={},
    )
    _run_hook(hook, event)
    assert event.cancel_tool
    assert "proof_id" in event.cancel_tool


def test_hook_ignores_non_deploy_tool(tmp_path):
    pm = ProofManager(tmp_path)
    hook = make_approval_hook(pm)
    class FakeAgent:
        pass
    event = BeforeToolCallEvent(
        agent=FakeAgent(), selected_tool=None,
        tool_use={"name": "read_file", "toolUseId": "t1", "input": {"path": "x"}},
        invocation_state={},
    )
    _run_hook(hook, event)
    # read_file is not gated — cancel_tool stays False.
    assert event.cancel_tool is False
