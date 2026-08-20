"""Tests for the M2 agent runtime: verdict extraction and config.

These avoid network calls (which depend on a live proxy) and instead test
the deterministic pieces: verdict extraction logic, config loading, and the
safety property that we never auto-ship without an explicit VERDICT line.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from evidenza.agent import _extract_verdict
from evidenza.runtime import RuntimeConfig, load_config


# --- verdict extraction -------------------------------------------------

def test_verdict_ship():
    assert _extract_verdict("all good\nVERDICT: SHIP") == "SHIP"


def test_verdict_blocked():
    assert _extract_verdict("tests failed\nVERDICT: BLOCKED") == "BLOCKED"


def test_verdict_needs_human():
    assert _extract_verdict("unsure\nVERDICT: NEEDS_HUMAN_REVIEW") == "NEEDS_HUMAN_REVIEW"


def test_verdict_missing_defaults_to_human_review():
    # Safety property: no explicit verdict -> never auto-ship.
    assert _extract_verdict("everything looks fine, shipping now") == "NEEDS_HUMAN_REVIEW"


def test_verdict_case_insensitive():
    assert _extract_verdict("VERDICT: ship") == "SHIP"
    assert _extract_verdict("verdict: blocked") == "BLOCKED"


def test_verdict_partial_match():
    assert _extract_verdict("VERDICT: SHIP IT") == "SHIP"
    assert _extract_verdict("VERDICT: BLOCKED by failing tests") == "BLOCKED"


# --- config loading -----------------------------------------------------

def test_config_defaults():
    # load_config with no file and no env should yield the documented defaults.
    # Clear env to avoid leaking real settings into the test.
    env_keys = ["EVIDENZA_PROVIDER", "EVIDENZA_MODEL_ID",
                "EVIDENZA_PROXY_URL", "EVIDENZA_PROXY_KEY", "EVIDENZA_MAX_ITER"]
    saved = {k: os.environ.pop(k, None) for k in env_keys}
    try:
        # Point at a path that does not exist so only defaults apply.
        cfg = load_config("/nonexistent/config.yaml")
        assert cfg.model_provider == "proxy"
        assert cfg.conversation_manager == "sliding"
        assert cfg.max_iterations == 20
        assert cfg.is_proxy is True
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_config_env_override(monkeypatch=None):
    # Env vars win over defaults.
    os.environ["EVIDENZA_PROVIDER"] = "bedrock"
    os.environ["EVIDENZA_MODEL_ID"] = "anthropic.claude-sonnet-4-20250514-v1:0"
    os.environ["EVIDENZA_MAX_ITER"] = "5"
    try:
        cfg = load_config("/nonexistent/config.yaml")
        assert cfg.model_provider == "bedrock"
        assert cfg.model_id == "anthropic.claude-sonnet-4-20250514-v1:0"
        assert cfg.max_iterations == 5
        assert cfg.is_proxy is False
    finally:
        del os.environ["EVIDENZA_PROVIDER"]
        del os.environ["EVIDENZA_MODEL_ID"]
        del os.environ["EVIDENZA_MAX_ITER"]
