"""Strands Agent setup + run loop.

Creates the Strands Agent with all evidenza tools, a system prompt that
drives an evidence-led verification loop, and a conversation manager. Exposes
a single `run(prompt, config)` entrypoint that returns the agent's result and
the computed release verdict.
"""
from __future__ import annotations

import logging
from typing import Any

from strands import Agent
from strands.models.model import Model

from .proof.verdict import compute_verdict
from .runtime import RuntimeConfig, load_config
from .tools.deploy import deploy
from .tools.file import read_file, write_file
from .tools.git import git_commit, git_sha
from .tools.shell import shell
from .tools.verify import verify_url

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are evidenza, an evidence-led autonomous release verification agent.

Your job: given a release task, gather CONCRETE EVIDENCE before declaring a
release ready to ship. Never assert readiness without evidence.

Available evidence sources (tools):
- read_file: inspect source, configs, manifests, changelogs
- shell: run build/test/lint commands and capture output
- git_sha / git_commit: capture the exact commit being released
- verify_url: confirm a deployed URL is alive and returns 200
- write_file: write a verification report
- deploy: ship once a proof is approved

WORKFLOW for a verify task:
1. Capture the git SHA being released (git_sha).
2. Read relevant files (manifests, configs, tests) to understand the release.
3. Run the build/tests/lint via shell to confirm they pass.
4. If a URL is given, verify_url to confirm it is live.
5. Report evidence as a JSON list of acceptance criteria, each with a status:
   "passed" | "failed" | "blocked" | "manual_review" | "pending"
   Each criterion: {"name": "...", "status": "...", "evidence": "..."}
6. End your final message with a line: VERDICT: <SHIP|BLOCKED|NEEDS_HUMAN_REVIEW>

Rules:
- Be concise. Do not narrate at length.
- If a tool fails, record it as "blocked" with the error as evidence.
- If you cannot fully verify something, mark it "manual_review", never "passed".
- Never claim SHIP unless every criterion is "passed".
"""

# Tools the agent may use, in the order presented to the model.
ALL_TOOLS = [
    read_file,
    write_file,
    shell,
    git_sha,
    git_commit,
    verify_url,
    deploy,
]


def _build_model(config: RuntimeConfig) -> Model:
    """Construct the model provider from config."""
    if config.is_proxy:
        from .proxy_model import ProxyModel
        return ProxyModel(
            base_url=config.proxy_base_url,
            api_key=config.proxy_api_key,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
        )
    if config.model_provider == "anthropic":
        from strands.models.anthropic import AnthropicModel
        return AnthropicModel(
            client_args={"api_key": config.proxy_api_key},
            model_id=config.model_id,
            max_tokens=config.max_tokens,
        )
    if config.model_provider == "bedrock":
        from strands.models.bedrock import BedrockModel
        return BedrockModel(model_id=config.model_id)
    raise ValueError(f"unknown model provider: {config.model_provider!r}")


def create_agent(config: RuntimeConfig | None = None, proofs=None) -> Agent:
    """Create a configured Strands Agent with all evidenza tools.

    Args:
        config: Runtime config (loaded from defaults if None).
        proofs: Optional ProofManager. When provided, a human-in-the-loop
            approval hook is registered so the ``deploy`` tool is gated behind
            explicit human approval of a SHIP verdict.
    """
    config = config or load_config()
    model = _build_model(config)

    # Conversation manager: sliding window keeps recent turns. Optional — if
    # the import path varies across Strands versions we degrade gracefully.
    conversation_manager = None
    if config.conversation_manager == "sliding":
        try:
            from strands.agent.conversation_manager.sliding import SlidingWindowConversationManager
            conversation_manager = SlidingWindowConversationManager()
        except Exception:
            pass

    agent = Agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,  # quiet; we read results programmatically
    )

    # Register the human-in-the-loop SHIP approval hook when a ProofManager
    # is provided. This gates `deploy` behind human approval.
    if proofs is not None:
        from strands.hooks import BeforeToolCallEvent as _BTCE
        from .approval import make_approval_hook
        agent.hooks.add_callback(_BTCE, make_approval_hook(proofs))

    return agent


def run(prompt: str, config: RuntimeConfig | None = None, proofs=None) -> dict[str, Any]:
    """Run the evidenza agent with a user prompt.

    Args:
        prompt: The task prompt.
        config: Runtime config (loaded from defaults if None).
        proofs: Optional ProofManager enabling human-in-the-loop deploy gating.

    Returns a dict with: result (AgentResult), verdict (str), content (str),
    stop_reason (str|None), tool_metrics (dict), interrupts (list[dict]).
    """
    config = config or load_config()
    agent = create_agent(config, proofs=proofs)
    logger.debug("running agent prompt (%d chars)", len(prompt))

    result = agent(prompt)

    # Extract final assistant text.
    content_blocks = result.message.get("content", []) if hasattr(result, "message") else []
    texts = [b.get("text", "") for b in content_blocks if isinstance(b, dict) and "text" in b]
    content = "\n".join(t for t in texts if t)

    # Derive verdict from the explicit VERDICT: line the agent emits.
    verdict = _extract_verdict(content)

    tool_metrics: dict[str, Any] = {}
    if hasattr(result, "metrics") and getattr(result.metrics, "tool_metrics", None):
        tool_metrics = {
            k: {"calls": v.call_count, "success": v.success_count, "errors": v.error_count}
            for k, v in result.metrics.tool_metrics.items()
        }

    # Extract any interrupts that fired (human-in-the-loop pauses).
    interrupts: list[dict[str, Any]] = []
    if hasattr(result, "interrupts"):
        for it in (result.interrupts or []):
            interrupts.append({
                "id": getattr(it, "id", None),
                "name": getattr(it, "name", None),
                "reason": getattr(it, "reason", None),
            })

    return {
        "result": result,
        "verdict": verdict,
        "content": content,
        "stop_reason": getattr(result, "stop_reason", None),
        "tool_metrics": tool_metrics,
        "interrupts": interrupts,
    }


def _extract_verdict(content: str) -> str:
    """Pull the VERDICT: <X> line from agent output, normalize it.

    Falls back to NEEDS_HUMAN_REVIEW (never auto-ship without an explicit
    VERDICT: SHIP line — this is the safety property of the whole system).
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("VERDICT:"):
            val = stripped.split(":", 1)[1].strip().upper()
            if val in ("SHIP", "BLOCKED", "NEEDS_HUMAN_REVIEW"):
                return val
            if "SHIP" in val:
                return "SHIP"
            if "BLOCK" in val:
                return "BLOCKED"
            if "HUMAN" in val or "REVIEW" in val:
                return "NEEDS_HUMAN_REVIEW"
    return "NEEDS_HUMAN_REVIEW"
