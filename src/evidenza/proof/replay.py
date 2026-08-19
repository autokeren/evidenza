"""Proof replay: render a visual Release Card from a pre-recorded proof run.

Judges can evaluate the proof system WITHOUT any API key — they replay a
pre-recorded, verified proof artifact. This is the offline-evidence angle
that makes the hackathon submission self-contained.

Fresh implementation for evidenza. No code copied from any prior project.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def render_proof_card(proof_file: str) -> dict[str, Any] | None:
    """Render a visual Release Card from a pre-recorded proof run JSON.

    Args:
        proof_file: path to proof-run.json.

    Prints a formatted card to stdout and returns the parsed data dict
    (or None if the file could not be read).
    """
    path = Path(proof_file)
    if not path.exists():
        print(f"Error: proof file not found: {proof_file}", file=sys.stderr)
        return None

    data = json.loads(path.read_text(encoding="utf-8"))

    # Try rich rendering; degrade to plain text if rich isn't installed.
    try:
        _render_rich(data)
    except ImportError:
        _render_plain(data)
    return data


# Status -> (symbol, color) for rich; plain uses the symbol.
_STATUS_SYM = {
    "passed": ("✓", "green"),
    "failed": ("✗", "red"),
    "blocked": ("⛔", "yellow"),
    "manual_review": ("?", "magenta"),
    "pending": ("·", "cyan"),
}
_VERDICT_STYLE = {
    "SHIP": ("green", "✅"),
    "BLOCKED": ("red", "🛑"),
    "NEEDS_HUMAN_REVIEW": ("yellow", "⏸"),
}


def _render_rich(data: dict[str, Any]) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console()
    verdict = data.get("verdict", "NEEDS_HUMAN_REVIEW")
    vstyle, vsym = _VERDICT_STYLE.get(verdict, ("white", "·"))
    approved = data.get("approved", False)
    approved_str = "✓ APPROVED" if approved else "✗ NOT APPROVED"

    title = f"{vsym}  {data.get('title', 'evidenza proof')}"
    header = Text.assemble(
        ("Verdict: ", "bold"), (f"{verdict}\n", f"bold {vstyle}"),
        ("Proof ID: ", "dim"), (f"{data.get('proof_id','')}\n", "white"),
        ("Git SHA: ", "dim"), (f"{data.get('git_sha','(none)')[:12]}\n", "white"),
        ("Created: ", "dim"), (f"{data.get('created_at','')}\n", "white"),
        ("Human approval: ", "dim"), (approved_str, "bold green" if approved else "bold red"),
    )

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Criterion", ratio=2)
    table.add_column("Status", width=14)
    table.add_column("Evidence", ratio=3)

    for c in data.get("criteria", []):
        sym, color = _STATUS_SYM.get(c.get("status", "pending"), ("·", "white"))
        table.add_row(
            str(c.get("num", "")),
            c.get("description", ""),
            Text(f"{sym} {c.get('status','')}", style=color),
            c.get("evidence", "") or "—",
        )

    body = Text.assemble(header, "\n\n")
    console.print(Panel(body, title=title, border_style=vstyle, expand=False))
    console.print(table)

    if verdict == "SHIP" and not approved:
        console.print("\n[yellow]⚠ Verdict is SHIP but no human approval recorded yet.[/]")
    if verdict == "SHIP" and approved:
        console.print("\n[green]✓ Evidence-led SHIP, approved by human — safe to deploy.[/]")


def _render_plain(data: dict[str, Any]) -> None:
    verdict = data.get("verdict", "NEEDS_HUMAN_REVIEW")
    vsym = _VERDICT_STYLE.get(verdict, ("", "·"))[1]
    approved = data.get("approved", False)

    print("=" * 64)
    print(f"{vsym}  {data.get('title', 'evidenza proof')}")
    print("=" * 64)
    print(f"  Verdict:     {verdict}")
    print(f"  Proof ID:    {data.get('proof_id','')}")
    print(f"  Git SHA:     {data.get('git_sha','(none)')[:12]}")
    print(f"  Created:     {data.get('created_at','')}")
    print(f"  Approval:    {'APPROVED' if approved else 'NOT APPROVED'}")
    print("-" * 64)
    print(f"  {'#':<4} {'Criterion':<38} {'Status':<14} Evidence")
    for c in data.get("criteria", []):
        sym = _STATUS_SYM.get(c.get("status", "pending"), ("·", ""))[0]
        ev = (c.get("evidence", "") or "—")[:40]
        desc = c.get("description", "")[:36]
        print(f"  {c.get('num',''):<4} {desc:<38} {sym} {c.get('status',''):<12} {ev}")
    print("-" * 64)
    if verdict == "SHIP" and approved:
        print("  Evidence-led SHIP, approved by human — safe to deploy.")
    elif verdict == "SHIP":
        print("  Verdict is SHIP but no human approval recorded yet.")
    print("=" * 64)
