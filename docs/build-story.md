# TITLE (paste ke field judul)

Agents for Humans: I built a release agent that refuses to ship without evidence — and a human

---

# BODY (paste ke editor — udah di bawah 3000 karakter)

Every team ships releases on vibes. A tired reviewer squints at a green CI badge, approves, and moves on. The badge says *build passed* — but nobody can answer: what exactly was verified, against what evidence, for which commit, and who approved it? When a release breaks at 2am, that answer can't be reconstructed. The review happened in someone's head.

For the Agents for Humans Hackathon I went after that repetitive, judgment-heavy task: release verification. I built **evidenza** — an evidence-led autonomous release verification agent on the **Strands Agents SDK**.

Given a release task, the agent runs the whole flow end to end: capture the exact git commit (`git_sha`), run the real test suite (`shell`), inspect manifests and configs (`read_file`), check endpoints (`verify_url`), record every acceptance criterion with its raw evidence into a proof artifact (JSON), and compute a verdict — SHIP / BLOCKED / NEEDS_HUMAN_REVIEW — from evidence, never from the model's assertion.

Seven lean `@tool` functions. The interesting part is the gate. Deploy is the only tool with real-world impact, so it's the only one gated. A Strands `BeforeToolCallEvent` hook intercepts the call and raises `InterruptException` until a human approves:

```python
async def approval_hook(event: BeforeToolCallEvent) -> None:
    if event.tool_use.get("name") != "deploy":
        return
    proof = proofs.get(event.tool_use["input"].get("proof_id"))
    if proof is None or proof.verdict != "SHIP" or not proof.approval:
        raise InterruptException(Interrupt(
            name="approve_ship",
            reason="Human approval required. Reply 'yes' to approve.",
        ))
```

No auto-ship, ever. The agent is autonomous up to the point of impact, human-in-the-loop at the moment that matters. Running tests and collecting evidence is exactly the routine work an agent should take off a human's plate.

The evidence IS the artifact: every run saves a proof JSON (criteria, status, raw evidence, verdict, approval) that anyone can replay later with **zero API keys**:

`evidenza --proof-replay examples/demo/proof-run.json`

Two lessons worth sharing:

- Verdicts from evidence, not from the model. The LLM orchestrates; deterministic code decides. That split makes an agent trustworthy enough to gate a deploy.
- Strands interrupts are THE human-in-the-loop primitive. One hook, one exception — the agent parks until a human responds. No polling, no state hacks.

Try it:
- Code: https://github.com/autokeren/evidenza (MIT)
- Demo video: https://youtu.be/7rXDJE-V8eQ
- Replay the proof yourself, no API key: `evidenza --proof-replay examples/demo/proof-run.json`

The hackathon thesis, made concrete: the agent does the work, the human keeps the judgment call that matters.

---

# HASHTAGS (paste di field tags bawah post)

#strands #agentic-ai #agents-for-humans #amazon-bedrock-agentcore
