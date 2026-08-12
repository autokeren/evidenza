# releaseproof

**Evidence-led autonomous release verification agent built on the [Strands Agents SDK](https://strandsagents.com/).**

releaseproof autonomously plans acceptance criteria, records real verification
evidence, and emits a **SHIP / BLOCKED / NEEDS_HUMAN_REVIEW** verdict. The agent
handles the routine verification work in the background — it only surfaces to a
human for the one decision that matters: *should we ship?*

Built for the **Agents for Humans** hackathon (AWS × Strands Agents SDK).

---

## 🚀 Quickstart for Judges (No API Key Required)

Judges can test the proof-rendering system without any external API keys:

```bash
git clone https://github.com/ajat/releaseproof
cd releaseproof
pip install -e .

# Replay a pre-recorded, verified proof run
releaseproof --proof-replay examples/demo/proof-run.json
```

This renders a visual Release Card from a pre-recorded proof artifact.
It does not run tests dynamically or require any model provider.

---

## 🔧 Full Demo (Requires Model Access)

```bash
# Option A: AWS Bedrock (default)
export AWS_PROFILE=default
releaseproof "/safe-deploy build a checkout API with tests"

# Option B: Anthropic
export ANTHROPIC_API_KEY=sk-...
releaseproof --provider anthropic "/safe-deploy build a checkout API with tests"
```

The agent will:
1. **Plan** acceptance criteria for the release
2. **Build** the app and **record** real test evidence
3. **Emit** a verdict (SHIP / BLOCKED / NEEDS_HUMAN_REVIEW)
4. **Pause** for human approval if SHIP (human-in-the-loop)
5. **Publish** only after approval, bound to the verified git commit

---

## 🏗️ Architecture

```
                   ┌──────────────────────────┐
                   │     releaseproof CLI      │
                   └────────────┬─────────────┘
                                │
                   ┌────────────▼─────────────┐
                   │  Strands Agent (orchestrator) │
                   │  agent loop + conv mgr + hooks │
                   └────────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
  ┌─────────▼─────┐   ┌────────▼────────┐  ┌──────▼───────┐
  │  7 Lean Tools  │   │  Safety Hooks     │  │ Proof       │
  │  (Strands      │   │  BeforeToolCall   │  │ Interrupt   │
  │   @tool)       │   │  AfterToolCall   │  │ (SHIP gate)  │
  │                │   │  - secret scan    │  │              │
  │  read_file     │   │  - loop detect    │  │              │
  │  write_file    │   │                   │  │              │
  │  shell         │   │                   │  │              │
  │  git_commit    │   │                   │  │              │
  │  proof         │   │                   │  │              │
  │  deploy        │   │                   │  │              │
  │  verify_url    │   │                   │  │              │
  └────────────────┘   └───────────────────┘  └──────────────┘
                                │
                   ┌────────────▼─────────────┐
                   │  Model Provider            │
                   │  (Bedrock / Anthropic /    │
                   │   OpenAI / custom)         │
                   └───────────────────────────┘
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full design.

---

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- AWS account with Bedrock model access (optional — Anthropic/OpenAI also supported)

### Install

```bash
git clone https://github.com/ajat/releaseproof
cd releaseproof
pip install -e .

# With AgentCore support (optional)
pip install -e ".[agentcore]"

# For development
pip install -e ".[dev]"
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📦 What It Does

| Phase | Action | Human? |
|---|---|---|
| **Plan** | Agent creates acceptance criteria from the task | No |
| **Build** | Agent writes code, runs tests | No |
| **Record** | Agent records real test output as evidence | No |
| **Verdict** | Agent emits SHIP / BLOCKED / NEEDS_HUMAN_REVIEW | No |
| **Approval** | If SHIP, agent pauses and asks human to approve | ✅ **Yes** |
| **Publish** | After approval, agent deploys (bound to verified commit) | No |
| **Safety** | If code changes after approval, proof becomes stale → deploy blocked | No |

---

## 🎯 Agents for Humans Hackathon

This project is submitted to the **Agents for Humans** hackathon (AWS × Strands Agents SDK):
- **Track:** Professional Agents
- **Build period:** August 10 – September 14, 2026
- **Demo video:** [YouTube link TBD]

---

## Acknowledgments & Prior Work

This project, **releaseproof**, is a fresh implementation built during the
Agents for Humans hackathon (Aug 10 – Sep 14, 2026). The release verification
concept (evidence-led SHIP/BLOCKED/NEEDS_HUMAN_REVIEW verdict system,
safe-deploy workflow) builds upon ideas explored in the author's prior
open-source project, [autokeren](https://github.com/autokeren/autokeren)
(MIT license).

releaseproof is a new, lean codebase written from scratch during the
submission period, using the Strands Agents SDK as the agent orchestrator.
No code was directly copied from autokeren; the concepts were reimplemented
in a minimal form tailored to demonstrate the release verification agent
pattern with Strands.

The author is the original creator of autokeren and owns its copyright.

---

## 📄 License

MIT — see [LICENSE](./LICENSE).
