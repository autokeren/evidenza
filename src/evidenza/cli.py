"""evidenza CLI entry point.

Usage:
    evidenza "<prompt>"                  # run agent with prompt
    evidenza --proof-replay <file.json>   # replay pre-recorded proof (no API key)
    evidenza --provider <p> "<prompt>"    # override model provider
"""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="evidenza",
        description="Evidence-led autonomous release verification agent (Strands Agents SDK).",
    )
    parser.add_argument("prompt", nargs="?", help="Task prompt for the agent")
    parser.add_argument("--proof-replay", metavar="FILE", help="Replay a pre-recorded proof run (no API key needed)")
    parser.add_argument("--provider", choices=["proxy", "anthropic", "bedrock"], default="proxy",
                        help="Model provider (default: proxy = local Anthropic-compatible proxy)")
    parser.add_argument("--model", help="Override model id")
    parser.add_argument("--proxy-url", help="Override proxy base URL (provider=proxy)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full agent output")
    args = parser.parse_args()

    if args.proof_replay:
        from evidenza.proof.replay import render_proof_card
        render_proof_card(args.proof_replay)
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    from evidenza.runtime import load_config
    from evidenza import agent

    config = load_config()
    if args.provider:
        config.model_provider = args.provider
    if args.model:
        config.model_id = args.model
    if args.proxy_url:
        config.proxy_base_url = args.proxy_url

    print(f"[evidenza] provider={config.model_provider} model={config.model_id}")
    print(f"[evidenza] prompt: {args.prompt!r}")
    print("[evidenza] running agent ...\n")

    out = agent.run(args.prompt, config)

    print("\n" + "=" * 60)
    print(f"VERDICT: {out['verdict']}")
    print(f"stop_reason: {out['stop_reason']}")
    if out["tool_metrics"]:
        print("tools:")
        for name, m in out["tool_metrics"].items():
            print(f"  {name}: {m['success']}/{m['calls']} ok, {m['errors']} err")
    if args.verbose and out["content"]:
        print("\n--- agent output ---")
        print(out["content"])
    print("=" * 60)


if __name__ == "__main__":
    main()
