# TITLE (paste ke field judul)

Agents for Humans: I built a release agent that refuses to ship without evidence — and a human

---

# BODY (paste ke editor)

Every team I know ships releases on vibes. A tired reviewer squints at a green CI badge, approves the deploy, and moves on. The badge says *build passed* — but nobody can answer: what exactly was verified, against what evidence, for which commit, and who approved it? When a release breaks at 2am, that answer can't be reconstructed, because the review happened in someone's head.

That's the repetitive, judgment-heavy task I went after for the **Agents for Humans Hackathon**: release verification. So I built **evidenza** — an evidence-led autonomous release verification agent on the **Strands Agents SDK**.

## What it does

Given a release task, the agent runs the whole verification flow end to end:

1. **Capture** the exact git commit being released (`git_sha`)
2. **Run** the release candidate's real test suite (`shell`)
3. **Inspect** manifests, configs, and source (`read_file`)
4. **Check** deployed endpoints when applicable (`verify_url`)
5. **Record** every acceptance criterion with its raw evidence in a proof artifact (JSON)
6. **Compute a verdict** — SHIP / BLOCKED / NEEDS_HUMAN_REVIEW — from the evidence, never from the model's assertion
7. **Pause for a human** at exactly one moment: should we ship?
8. **Deploy** only after explicit human approval

Seven lean tools total, each a small Strands `@tool` function. The interesting part isn't the tools — it's the gate.

## The pattern that makes it "agents for humans"

The deploy tool is the only one with real-world impact, so it's the only one that's gated. A Strands `BeforeToolCallEvent` hook intercepts the call and raises an `InterruptException` if no human has approved the proof:

```python
async def approval_hook(event: BeforeToolCallEvent) -> None:
    tool_use = event.tool_use
    if tool_use.get("name") != "deploy":
        return

    proof_id = (tool_use.get("input") or {}).get("proof_id")
    proof = proofs.get(proof_id)

    if proof is None or proof.verdict != "SHIP" or not proof.approval:
        raise InterruptException(Interrupt(
            id="v1:before_tool_call:deploy:approve_ship",
            name="approve_ship",
            reason=(
                "Agent wants to DEPLOY. Human approval required. "
                "Reply 'yes' to approve, 'no' to reject."
            ),
        ))
```

No auto-ship, ever. The agent is autonomous up to the point of impact, and human-in-the-loop at exactly the moment that matters. Everything before that — running tests, collecting evidence, computing the verdict — is exactly the kind of routine work an agent should take off a human's plate.

## The evidence IS the artifact

My favorite part: every run is saved as a proof artifact — a JSON file with each criterion, its status, its raw evidence, the verdict, and the human approval. Anyone can replay it later with **zero API keys**:

```
evidenza --proof-replay examples/demo/proof-run.json
```

That renders a Release Card: the criteria, the evidence, the verdict, and who approved it. Judges, auditors, and teammates can verify a release decision *after the fact* — which is the whole thing I was trying to fix.

## What I learned building it

- **Verdicts from evidence, not from the model.** The agent doesn't decide SHIP by "feeling confident" — `compute_verdict` is plain code over recorded evidence. LLMs orchestrate; deterministic code decides. That split made the agent trustworthy enough to gate a deploy.
- **Strands interrupts are the human-in-the-loop primitive.** One hook, one exception, and the agent cleanly parks until a human responds. No polling, no side-channel state hacks.
- **Deterministic demos are a feature.** For the demo video I didn't want a flaky model call deciding what the recording looks like, so the demo runner uses the real components with a deterministic flow. It records the same way every single time.

## Stack

- **Strands Agents SDK** (open source, production-ready, built by teams at AWS) as the agent orchestrator
- 7 lean `@tool` functions: `git_sha`, `git_commit`, `shell`, `read_file`, `write_file`, `verify_url`, `deploy` (gated)
- Human-in-the-loop approval via `BeforeToolCallEvent` + `InterruptException`
- Provider-agnostic runtime: local Anthropic-compatible proxy for dev/demo, **Amazon Bedrock** and **Amazon Bedrock AgentCore** supported for real deployments

## Try it

- Code: https://github.com/autokeren/evidenza (MIT)
- Demo video: https://youtu.be/7rXDJE-V8eQ
- Replay the proof yourself, no API key: `evidenza --proof-replay examples/demo/proof-run.json`

The thesis of this hackathon, made concrete: the agent does the work, the human keeps the judgment call that matters.

---

# HASHTAGS (paste di field tags bawah post)

#strands #agentic-ai #agents-for-humans #amazon-bedrock-agentcore #ai-agents #devops
