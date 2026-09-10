# Devpost Submission Text — evidenza

> Copy-paste ke Devpost form. Bagian per bagian sesuai field form.

---

## Project Name

evidenza

## Elevator Pitch / Short Description

Evidence-led autonomous release verification agent. evidenza captures the
git commit, runs the release candidate's test suite, records every test as an
acceptance criterion with real evidence, computes a SHIP / BLOCKED /
NEEDS_HUMAN_REVIEW verdict — then pauses for a human at exactly one moment:
should we ship?

## Description (full)

### The problem

Every team ships releases on vibes. A tired reviewer squints at a green CI
badge, approves a deploy, and moves on. The badge says *build passed*, but
nobody can answer: **what exactly was verified, against what evidence, for
which commit, and who approved it?** When a release breaks, that answer can't
be reconstructed — the review happened in someone's head.

### Who it's for

Release engineers, senior developers, and solo maintainers of professional
projects — the people who bear the cost of a bad deploy. Especially small
teams without a release-engineering function: the person approving the deploy
is the same person who wrote the code at 2am.

### What it does

evidenza is an autonomous release verification agent built on the **Strands
Agents SDK**. Given a release task, it:

1. **Captures** the exact git commit being released (`git_sha` tool)
2. **Runs** the release candidate's real test suite and commands (`shell`)
3. **Inspects** manifests, configs, and source (`read_file`)
4. **Checks** deployed endpoints when applicable (`verify_url`)
5. **Records** each acceptance criterion with its raw evidence in a proof
   artifact (JSON)
6. **Computes** an evidence-led verdict — SHIP / BLOCKED / NEEDS_HUMAN_REVIEW
7. **Pauses** for human approval before deploy — a Strands
   `BeforeToolCallEvent` hook raises an interrupt that blocks the `deploy`
   tool until a human explicitly approves
8. **Replays**: the proof artifact renders a Release Card with zero API keys
   — judges, auditors, or teammates can verify the evidence later

### Why it matters

Verification work is routine and repetitive — perfect agent territory — but
the *decision to ship* is a judgment call with real consequences. evidenza
draws that line explicitly: **autonomous up to the point of impact,
human-in-the-loop at the moment that matters.** That's the "agents for
humans" thesis made concrete: the agent does the work, the human keeps the
authority.

Two safety properties are enforced in code, not by prompt:
- A `SHIP` verdict requires every criterion to be `passed`, computed from
  recorded evidence — never from the model's own assertion.
- `approve()` rejects any non-SHIP verdict, and the deploy hook raises an
  interrupt for unapproved SHIP proofs. No auto-ship, ever.

### How we built it

- **Strands Agents SDK** — the core: `Agent` loop, `@tool` decorated tools,
  conversation manager, hooks, and the interrupt system for human approval
- **7 lean tools** — read_file, write_file, shell, git_sha, git_commit,
  verify_url, deploy — each a thin, typed Strands tool
- **Approval hook** — a `BeforeToolCallEvent` hook gating `deploy` behind
  human approval via `InterruptException`
- **Proof system** — a plan/record/report/approve state machine serializing
  proofs to JSON, plus a replay renderer for the Release Card
- **Model-provider agnostic** — pluggable providers (local proxy default for
  dev/demo, Anthropic, Amazon Bedrock)

### What we learned

- The Strands hooks + interrupt design maps *exactly* to a
  human-approval gate — the whole safety property is ~80 lines of hook code,
  which is exactly the kind of non-obvious SDK usage this hackathon asks for.
- Non-streaming model responses needed a custom Strands model provider to be
  reliable across our proxy backends.
- "Evidence-led" beats "model says it's fine": forcing the verdict to be
  computed from recorded criteria — instead of trusting model narration —
  surfaced every assumption we'd otherwise have shipped on.

### Accomplishments we're proud of

- 28 deterministic tests covering both safety properties — verdicts and the
  human-approval gate — with zero network dependency
- A demo that runs end-to-end reliably on video: real pytest output becomes
  evidence, the deploy gets blocked, then approved, then proceeds
- Proof artifacts that judges can replay with **zero API keys**

## Built with

Python, Strands Agents SDK, pytest, httpx, AWS (planned: Bedrock AgentCore)

## Track

Professional Agents

## Links

- Code: https://github.com/autokeren/evidenza
- Demo video: [TBD — YouTube]
- Replay the proof yourself (no API key): `evidenza --proof-replay examples/demo/proof-run.json`
