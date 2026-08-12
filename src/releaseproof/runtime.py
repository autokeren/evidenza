"""Runtime config loader for releaseproof.

Loads config.yaml (or falls back to config.example.yaml defaults),
resolves model provider, and returns a typed config object.

TODO(M1): implement full config loading.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """Runtime configuration for releaseproof."""
    model_provider: str = "bedrock"
    model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    conversation_manager: str = "sliding"
    max_iterations: int = 20
    deploy_agentcore: bool = False


def load_config(path: str | None = None) -> RuntimeConfig:
    """Load runtime config from YAML file or return defaults.

    TODO(M1): implement YAML loading.
    """
    return RuntimeConfig()
