"""releaseproof CLI entry point.

Usage:
    releaseproof "<prompt>"                  # run agent with prompt
    releaseproof --proof-replay <file.json>   # replay pre-recorded proof (no API key)
    releaseproof --provider <p> "<prompt>"    # override model provider
"""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="releaseproof",
        description="Evidence-led autonomous release verification agent (Strands Agents SDK).",
    )
    parser.add_argument("prompt", nargs="?", help="Task prompt for the agent")
    parser.add_argument("--proof-replay", metavar="FILE", help="Replay a pre-recorded proof run (no API key needed)")
    parser.add_argument("--provider", choices=["bedrock", "anthropic", "openai"], help="Override model provider")
    args = parser.parse_args()

    if args.proof_replay:
        from releaseproof.proof.replay import render_proof_card
        render_proof_card(args.proof_replay)
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    # TODO(M1): wire to Strands agent runtime
    print(f"[releaseproof] prompt: {args.prompt!r}")
    print("[releaseproof] agent runtime not yet wired — see EXECUTION-PLAN.md")


if __name__ == "__main__":
    main()
