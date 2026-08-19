"""Runtime config loader for releaseproof.

Loads config.yaml (or falls back to config.example.yaml defaults), resolves
model provider, and returns a typed config object. Supports a `proxy`
provider that talks to a local Anthropic-Messages-compatible proxy
(e.g. claude-cf on :8787, claude-do on :8788) — this is the default for
local dev and the hackathon demo since it needs no cloud credentials.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RuntimeConfig:
    """Runtime configuration for releaseproof."""

    model_provider: str = "proxy"
    model_id: str = "claude-sonnet-4-20250514"
    proxy_base_url: str = "http://127.0.0.1:8787"
    proxy_api_key: str = "dummy"
    conversation_manager: str = "sliding"
    max_iterations: int = 20
    max_tokens: int = 1024
    deploy_agentcore: bool = False

    @property
    def is_proxy(self) -> bool:
        return self.model_provider == "proxy"


def _coalesce(*vals: str | None) -> str | None:
    """Return the first non-empty value, else None."""
    for v in vals:
        if v and v.strip():
            return v
    return None


def load_config(path: str | None = None) -> RuntimeConfig:
    """Load runtime config from YAML (if present) + env overrides + defaults.

    Resolution order (later wins): defaults → config.yaml → env vars.
    """
    cfg = RuntimeConfig()

    # Try to load YAML. PyYAML is optional; degrade gracefully if absent.
    yaml_path = Path(path) if path else Path("config.yaml")
    if yaml_path.exists():
        try:
            import yaml  # type: ignore[import-untyped]
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
        m = data.get("model", {}) or {}
        a = data.get("agent", {}) or {}
        d = data.get("deploy", {}) or {}
        p = data.get("proxy", {}) or {}
        if m.get("provider"):
            cfg.model_provider = str(m["provider"])
        if m.get("id"):
            cfg.model_id = str(m["id"])
        if p.get("base_url"):
            cfg.proxy_base_url = str(p["base_url"])
        if p.get("api_key"):
            cfg.proxy_api_key = str(p["api_key"])
        if a.get("conversation_manager"):
            cfg.conversation_manager = str(a["conversation_manager"])
        if a.get("max_iterations") is not None:
            cfg.max_iterations = int(a["max_iterations"])
        if d.get("agentcore"):
            cfg.deploy_agentcore = bool(d["agentcore"])

    # Environment overrides (highest precedence).
    if v := _coalesce(os.environ.get("RELEASEPROOF_PROVIDER")):
        cfg.model_provider = v
    if v := _coalesce(os.environ.get("RELEASEPROOF_MODEL_ID")):
        cfg.model_id = v
    if v := _coalesce(os.environ.get("RELEASEPROOF_PROXY_URL")):
        cfg.proxy_base_url = v
    if v := _coalesce(os.environ.get("RELEASEPROOF_PROXY_KEY")):
        cfg.proxy_api_key = v
    if v := _coalesce(os.environ.get("RELEASEPROOF_MAX_ITER")):
        try:
            cfg.max_iterations = int(v)
        except ValueError:
            pass

    return cfg
