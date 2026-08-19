# releaseproof — Demo Guide & Narration Script

> Evidence-led autonomous release verification agent, built on the Strands Agents SDK.
> Track: **Professional Agents** — Agents for Humans hackathon.

This guide walks through recording the demo video for the submission. The demo
runs entirely on local, deterministic components — no live model calls, no
API keys, so it records reliably.

## Prerequisites

```bash
cd /home/ubuntu/releaseproof
source .venv/bin/activate
```

## The Demo (two commands)

### Part A — SHIP path (the happy path, ~60s)

```bash
python examples/demo/run_demo.py
```

What it shows, in order:
1. **Capture git SHA** — the exact commit being released is recorded.
2. **Run the real test suite** — `pytest` against the demo checkout API; live
   evidence is captured per test.
3. **Record acceptance criteria** — each test becomes a criterion with status +
   evidence, stored as a proof JSON.
4. **Compute the evidence-led verdict** — `SHIP` because all criteria passed.
5. **Attempt deploy WITHOUT human approval** — the `BeforeToolCallEvent` hook
   raises `InterruptException`; deploy is blocked. *This is the safety
   property: autonomous up to the point of impact.*
6. **Human approves** — `ProofManager.approve()` records a human approval.
7. **Attempt deploy AFTER approval** — the gate passes; deploy proceeds.
8. **Render the Release Card** — the replayable artifact, no API key needed.

### Part B — BLOCKED path (the safety story, ~15s)

```bash
python examples/demo/run_demo.py --block
```

Shows a failing test → `BLOCKED` verdict → releaseproof stops **before** any
human is bothered. The evidence itself says the release isn't ready; no
approval is needed because nothing is deployed.

### Part C — Judge replay (the self-contained artifact, ~10s)

```bash
python -m releaseproof.cli --proof-replay examples/demo/proof-run.json
```

Judges can replay the exact proof artifact with **zero API keys** — the
evidence *is* the artifact. This is the offline-evidence angle that makes the
submission self-contained for evaluation.

## Narration (for the ~90s video)

> This is **releaseproof** — an evidence-led autonomous release agent built on
> the Strands Agents SDK. It verifies a release by gathering concrete evidence
> *before* declaring it ready to ship.
>
> *[Part A runs]*
>
> First it captures the git commit being released. Then it runs the release
> candidate's real test suite and records each test as an acceptance criterion
> with its evidence. From that evidence it computes a verdict — here, SHIP.
>
> Now the key part: when the agent tries to deploy, a Strands
> `BeforeToolCallEvent` hook raises an interrupt. The agent **cannot** deploy
> until a human approves. Autonomous up to the point of impact — that's the
> "Agents for Humans" angle.
>
> Once a human approves, the gate passes and deploy proceeds. The whole run is
> saved as a proof artifact — a JSON file — that judges can replay with zero
> API keys, because the evidence *is* the artifact.
>
> *[Part B runs]*
>
> And if a test fails, the verdict is BLOCKED — releaseproof stops before any
> human is even asked. The evidence decides; the human only decides when the
> evidence says ship.
>
> releaseproof: evidence-led, human-gated, replayable.

## Why this is defensible (for judges)

- **Evidence-led**: the verdict is computed from recorded criteria, never from
  the model's assertion. A SHIP requires every criterion `passed`.
- **Human-in-the-loop at impact**: the `deploy` tool is gated by a Strands hook
  that raises `InterruptException`. No auto-ship, ever.
- **Replayable**: proofs are JSON artifacts, replayable without any model or
  API key — the evidence is self-contained.
- **Two safety properties**: (1) `approve()` rejects non-SHIP verdicts with
  `PermissionError`; (2) `_extract_verdict` defaults to `NEEDS_HUMAN_REVIEW`,
  never auto-ship.
