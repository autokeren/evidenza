#!/usr/bin/env python3
"""End-to-end smoke test: Strands Agent via claude-cf proxy (localhost:8787).

Runs the evidenza agent with a trivial prompt that exercises a tool,
proving the Strands + tool + proxy stack works together.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ensure src on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from strands import Agent
from strands.models.anthropic import AnthropicModel

from evidenza.tools.file import read_file, write_file
from evidenza.tools.git import git_sha, git_commit
from evidenza.tools.verify import verify_url
from evidenza.tools.shell import shell

PROXY_URL = "http://127.0.0.1:8787"
MODEL_ID = "claude-sonnet-4-20250514"  # proxy ignores model name, uses glm-5.2


def main() -> int:
    model = AnthropicModel(
        client_args={"base_url": PROXY_URL, "api_key": "dummy"},
        model_id=MODEL_ID,
        max_tokens=1024,
    )
    agent = Agent(
        model=model,
        tools=[read_file, write_file, git_sha, git_commit, verify_url, shell],
        system_prompt=(
            "You are evidenza, an evidence-led release verification agent. "
            "Use the provided tools when asked to inspect files or run commands. "
            "Be concise."
        ),
    )

    # Trivial task: write a file, read it back, confirm its content.
    test_file = "/tmp/evidenza_e2e_test.txt"
    test_content = "evidenza e2e smoke test ok"

    prompt = (
        f"Use the write_file tool to write this exact content to {test_file}: "
        f'"{test_content}". '
        "Then use the read_file tool to read it back. "
        "Finally reply with just: SMOKE_OK"
    )

    print("=== Running agent (this may take 10-30s) ===")
    try:
        result = agent(prompt)
    except Exception as e:
        print(f"ERROR: agent raised: {e}")
        return 1

    # Strands Agent __call__ returns a Result; .message is the Anthropic message.
    text = str(result)
    print("=== Agent output ===")
    print(text)

    # Verify the file was actually written
    p = Path(test_file)
    if p.exists() and test_content in p.read_text():
        print("=== File verified: tool actually ran ===")
    else:
        print(f"WARNING: file {test_file} not written as expected")
        if p.exists():
            print(f"  content: {p.read_text()!r}")

    if "SMOKE_OK" in text or "smoke_ok" in text.lower():
        print("=== E2E SMOKE TEST PASSED ===")
        return 0
    print("=== E2E SMOKE TEST: agent finished but SMOKE_OK not found in output ===")
    return 2


if __name__ == "__main__":
    sys.exit(main())
