# 🏗️ Architecture — releaseproof

> Evidence-led autonomous release verification agent built on the Strands Agents SDK.

## 🧭 Design Principles

1. **Lean** — only 7 tools the demo needs (not 28)
2. **Strands = orchestrator core**, not a thin wrapper
3. **Human-in-the-loop** — agent pauses for SHIP approval via Strands `event.interrupt()`
4. **Evidence-led** — every verdict backed by real test output
5. **Safety** — stale proofs block deploy; code changes require re-verification
6. **Judge-friendly** — `--proof-replay` works without any API key

## 📐 Architecture Diagram

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
                                │ (optional)
                   ┌────────────▼─────────────┐
                   │  Amazon Bedrock AgentCore  │
                   │  Runtime deployment        │
                   └───────────────────────────┘
```

## 📁 Project Structure

```
releaseproof/
├── src/releaseproof/
│   ├── cli.py              CLI entry (argparse, --proof-replay)
│   ├── agent.py            Strands Agent setup + run loop
│   ├── runtime.py          Config loader
│   ├── tools/              7 lean Strands @tool functions
│   ├── hooks/              Safety hooks (secret scan, loop detect)
│   └── proof/              Proof manager + verdict + replay
├── examples/demo/          Demo app + test suite + proof-run.json
├── tests/                 Unit tests
└── docs/                  Architecture diagram (PNG)
```

## 🔄 Release Verification Workflow

```
User prompt: "/safe-deploy build X with tests"
         │
         ▼
   ┌──────────┐
   │  PLAN    │  agent creates proof plan with acceptance criteria
   └────┬─────┘
        ▼
   ┌──────────┐
   │  BUILD   │  agent writes code (write_file, shell)
   └────┬─────┘
        ▼
   ┌──────────┐
   │ RECORD   │  agent runs tests, records real output as evidence
   └────┬─────┘
        ▼
   ┌──────────┐
   │ VERDICT  │  compute_verdict() → SHIP / BLOCKED / NEEDS_HUMAN_REVIEW
   └────┬─────┘
        ▼
   ┌──────────────────┐
   │ If SHIP:         │  agent pauses via event.interrupt()
   │ HUMAN APPROVAL   │  human types y/n
   └────┬─────────────┘
        ▼ (approved)
   ┌──────────┐
   │ PUBLISH  │  deploy, bound to verified git commit
   └──────────┘
        │
        ▼ (if code changes after approval)
   ┌──────────┐
   │ STALE    │  proof no longer matches commit → deploy BLOCKED
   │ CHECK    │  re-verification required
   └──────────┘
```

## 🛠️ Tools (7 Lean)

| Tool | Purpose | Lines (est) |
|---|---|---|
| `read_file` | Read file contents | ~50 |
| `write_file` | Write file contents | ~50 |
| `shell` | Run shell command, capture output | ~80 |
| `git_commit` | Git commit + get current SHA | ~60 |
| `proof` | ⭐ plan/record/verdict (THE STAR) | ~200 |
| `deploy` | Publish (simplified) | ~80 |
| `verify_url` | Check deployed URL is alive | ~40 |

## 🪝 Hooks

| Hook | Event | Action |
|---|---|---|
| Secret scan | BeforeToolCall (write_file) | Cancel if secret/API key detected |
| Loop detect | AfterToolCall | Track tool+args hash, cancel if repeating |

## 📦 Dependencies

- `strands-agents` — agent SDK (required)
- `httpx` — HTTP client for deploy/verify (required)
- `bedrock-agentcore` — AgentCore deploy (optional)

## 🚀 Deployment (Optional)

releaseproof can deploy to Amazon Bedrock AgentCore Runtime for
production-scale operation. See `agentcore.yaml` (to be added in M4).

## ⚠️ Research Questions (to answer in M1)

1. Does Strands support tools from JSON schema directly (avoid manual wrap)?
2. Is `event.interrupt()` available in the Python SDK? What's the signature?
3. What does AgentCore Runtime deployment require (entrypoint, config, image)?
4. Does Bedrock model access need provisioning in AWS console? Which region?
