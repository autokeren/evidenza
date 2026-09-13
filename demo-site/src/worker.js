const SHIP_PROOF = {
  proof_id: "proof-20260819T051812Z-1740",
  title: "Demo checkout API release",
  git_sha: "7036650",
  created_at: "2026-08-19T05:18:12Z",
  criteria: [
    {
      num: 1,
      description: "Valid Checkout Returns 200",
      status: "passed",
      evidence:
        "examples/demo/test_app.py::test_valid_checkout_returns_200 PASSED        [ 33%]",
    },
    {
      num: 2,
      description: "Missing Items Returns 400",
      status: "passed",
      evidence:
        "examples/demo/test_app.py::test_missing_items_returns_400 PASSED         [ 66%]",
    },
    {
      num: 3,
      description: "Missing Card Returns 400",
      status: "passed",
      evidence:
        "examples/demo/test_app.py::test_missing_card_returns_400 PASSED          [100%]",
    },
  ],
  verdict: "SHIP",
  approved: true,
  approved_at: "2026-08-19T05:18:12Z",
  approved_by: "human@example.com",
};

const BLOCKED_PROOF = {
  proof_id: "proof-20260913T091158Z-6980",
  title: "Demo checkout API release",
  git_sha: "9b52c46",
  created_at: "2026-09-13T09:11:58Z",
  criteria: [
    {
      num: 1,
      description: "Valid checkout returns 200 with correct total",
      status: "passed",
      evidence: "test_valid_checkout_returns_200: PASSED.",
    },
    {
      num: 2,
      description: "Missing items returns 400 error",
      status: "passed",
      evidence: "test_missing_items_returns_400: PASSED.",
    },
    {
      num: 3,
      description: "Invalid card is rejected",
      status: "failed",
      evidence:
        "test_invalid_card: FAILED. AssertionError: assert response.status_code == 400",
    },
  ],
  verdict: "BLOCKED",
  approved: false,
  approved_at: null,
  approved_by: null,
};

const HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>evidenza — Evidence-Led Release Agent</title>
<meta name="description" content="evidenza: an evidence-led autonomous release verification agent built on the Strands Agents SDK. Replay proof artifacts in your browser — zero API keys.">
<style>
  :root {
    --bg: #0b0f14; --panel: #11161d; --line: #1e2630; --text: #d7e0ea;
    --dim: #7b8794; --green: #3ddc84; --red: #ff5f6d; --amber: #ffc857;
    --cyan: #56c8f8; --mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: var(--mono); min-height: 100vh; padding: 24px 16px 48px; }
  .wrap { max-width: 880px; margin: 0 auto; }
  header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 12px; margin-bottom: 8px; }
  h1 { font-size: 26px; letter-spacing: 1px; color: #fff; }
  h1 span { color: var(--cyan); }
  .tagline { color: var(--dim); font-size: 13px; }
  .badges { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0 22px; }
  .badge { font-size: 11px; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; color: var(--dim); background: var(--panel); }
  .badge b { color: var(--text); font-weight: 600; }
  .controls { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
  button { font-family: var(--mono); font-size: 13px; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--line); background: var(--panel); color: var(--text); cursor: pointer; }
  button:hover { border-color: var(--cyan); }
  button.active { border-color: var(--cyan); color: var(--cyan); }
  .hint { color: var(--dim); font-size: 12px; margin-left: 4px; }
  .paste { display: none; margin-bottom: 16px; width: 100%; }
  .paste.open { display: block; }
  textarea { width: 100%; height: 140px; background: var(--panel); color: var(--text); border: 1px solid var(--line); border-radius: 8px; padding: 10px; font-family: var(--mono); font-size: 12px; resize: vertical; }
  textarea:focus { outline: none; border-color: var(--cyan); }
  .card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
  .card-head { padding: 14px 18px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
  .card-title { font-size: 15px; font-weight: 600; color: #fff; }
  .verdict { font-weight: 700; font-size: 15px; }
  .v-SHIP { color: var(--green); }
  .v-BLOCKED { color: var(--red); }
  .v-NEEDS_HUMAN_REVIEW { color: var(--amber); }
  .meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px 18px; padding: 14px 18px; border-bottom: 1px solid var(--line); font-size: 12px; }
  .meta .k { color: var(--dim); display: block; margin-bottom: 2px; }
  .approval-yes { color: var(--green); }
  .approval-no { color: var(--red); }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { text-align: left; color: var(--dim); font-weight: 600; padding: 10px 18px; border-bottom: 1px solid var(--line); font-size: 11px; text-transform: uppercase; letter-spacing: .5px; }
  td { padding: 10px 18px; border-bottom: 1px solid var(--line); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  .st-passed { color: var(--green); }
  .st-failed { color: var(--red); }
  .st-blocked { color: var(--amber); }
  .st-manual_review { color: #d38bff; }
  .st-pending { color: var(--cyan); }
  .desc { color: var(--text); }
  .ev { color: var(--dim); font-size: 11px; word-break: break-word; }
  .card-foot { padding: 12px 18px; font-size: 13px; border-top: 1px dashed var(--line); }
  .f-ship { color: var(--green); }
  .f-blocked { color: var(--red); }
  .err { color: var(--red); font-size: 13px; margin: 12px 0; display: none; }
  section.try { margin-top: 28px; border: 1px dashed var(--line); border-radius: 10px; padding: 16px 18px; }
  section.try h2 { font-size: 14px; margin-bottom: 10px; color: #fff; }
  pre { background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 12px; font-size: 12px; overflow-x: auto; color: var(--text); }
  .links { margin-top: 12px; font-size: 13px; display: flex; gap: 18px; flex-wrap: wrap; }
  a { color: var(--cyan); text-decoration: none; }
  a:hover { text-decoration: underline; }
  footer { margin-top: 32px; color: var(--dim); font-size: 12px; text-align: center; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>evidenza<span>()</span></h1>
    <div class="tagline">Evidence-Led Release Agent — built on the Strands Agents SDK</div>
  </header>
  <div class="badges">
    <div class="badge"><b>Agents for Humans</b> Hackathon · Professional Agents</div>
    <div class="badge">verdict from <b>evidence</b>, never from the model's assertion</div>
    <div class="badge">replay with <b>zero API keys</b></div>
  </div>

  <div class="controls">
    <button id="btn-ship" class="active" onclick="loadExample('ship')">SHIP example</button>
    <button id="btn-blocked" onclick="loadExample('blocked')">BLOCKED example</button>
    <button id="btn-paste" onclick="togglePaste()">Paste your own proof JSON</button>
    <span class="hint">proof artifacts are the replayable evidence of a release decision</span>
  </div>

  <div class="paste" id="paste-box">
    <textarea id="paste-area" placeholder='Paste a proof artifact JSON produced by evidenza (see examples/demo/proof-run.json in the repo)...'></textarea>
    <div style="margin-top:8px">
      <button onclick="renderPasted()">Render proof</button>
    </div>
  </div>

  <div class="err" id="err"></div>
  <div id="card-slot"></div>

  <section class="try">
    <h2>Run the agent yourself</h2>
<pre>git clone https://github.com/autokeren/evidenza
cd evidenza &amp;&amp; pip install -e .

evidenza --proof-replay examples/demo/proof-run.json   # render a proof, zero API keys
python examples/demo/run_demo.py                      # full SHIP flow, live
python examples/demo/run_demo.py --block              # BLOCKED flow: evidence stops the release</pre>
    <div class="links">
      <a href="https://github.com/autokeren/evidenza">GitHub — autokeren/evidenza (MIT)</a>
      <a href="https://youtu.be/7rXDJE-V8eQ">Demo video (1:20)</a>
    </div>
  </section>

  <footer>evidenza — the agent does the work, the human keeps the judgment call that matters.</footer>
</div>

<script>
const SYM = { passed: "&#10003;", failed: "&#10007;", blocked: "&#9940;", manual_review: "?", pending: "&middot;" };
let shipProof, blockedProof;

async function loadExamples() {
  const [s, b] = await Promise.all([
    fetch("/api/proof/ship.json").then(r => r.json()),
    fetch("/api/proof/blocked.json").then(r => r.json()),
  ]);
  shipProof = s; blockedProof = b;
  loadExample("ship");
}

function setActiveBtn(id) {
  for (const b of ["btn-ship", "btn-blocked", "btn-paste"])
    document.getElementById(b).classList.toggle("active", b === id);
}

function loadExample(kind) {
  setActiveBtn(kind === "ship" ? "btn-ship" : "btn-blocked");
  hideErr();
  renderProof(kind === "ship" ? shipProof : blockedProof);
}

function togglePaste() {
  const box = document.getElementById("paste-box");
  const open = box.classList.toggle("open");
  setActiveBtn(open ? "btn-paste" : "");
  if (open) document.getElementById("paste-area").focus();
}

function renderPasted() {
  const raw = document.getElementById("paste-area").value;
  try {
    const p = JSON.parse(raw);
    if (!Array.isArray(p.criteria) || !p.verdict) throw new Error("missing 'criteria' or 'verdict'");
    hideErr();
    renderProof(p);
    setActiveBtn("");
  } catch (e) {
    showErr("Could not parse proof artifact: " + e.message);
  }
}

function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

function renderProof(p) {
  const st = (s) => '<span class="st-' + esc(s) + '">' + (SYM[s] || "&middot;") + " " + esc(s) + "</span>";
  const rows = p.criteria.map(c =>
    "<tr><td>" + esc(c.num ?? "-") + "</td><td><div class='desc'>" + esc(c.description ?? "") +
    "</div><div class='ev'>" + esc(c.evidence ?? "") + "</div></td><td>" + st(c.status) + "</td></tr>"
  ).join("");
  const approved = p.approved
    ? '<span class="approval-yes">APPROVED' + (p.approved_by ? " by " + esc(p.approved_by) : "") + "</span>"
    : '<span class="approval-no">NOT APPROVED</span>';
  const foot =
    p.verdict === "SHIP" && p.approved
      ? '<span class="f-ship">Evidence-led SHIP, approved by human — safe to deploy.</span>'
      : p.verdict === "SHIP"
        ? '<span class="f-blocked">SHIP verdict, but no human approval yet — the deploy gate stays closed.</span>'
        : '<span class="f-blocked">' + esc(p.verdict) + " — the evidence itself stops the release. No human is bothered.</span>";
  const html =
    '<div class="card">' +
    '<div class="card-head"><div class="card-title">' + esc(p.title || p.proof_id || "proof artifact") + '</div><div class="verdict v-' + esc(p.verdict) + '">' + esc(p.verdict) + "</div></div>" +
    '<div class="meta">' +
      '<div><span class="k">Proof ID</span>' + esc(p.proof_id ?? "-") + "</div>" +
      '<div><span class="k">Git SHA</span>' + esc(p.git_sha ?? "-") + "</div>" +
      '<div><span class="k">Created</span>' + esc(p.created_at ?? "-") + "</div>" +
      '<div><span class="k">Approval</span>' + approved + "</div>" +
    "</div>" +
    '<table><thead><tr><th style="width:36px">#</th><th>Criterion &amp; evidence</th><th style="width:120px">Status</th></tr></thead><tbody>' + rows + "</tbody></table>" +
    '<div class="card-foot">' + foot + "</div>" +
    "</div>";
  document.getElementById("card-slot").innerHTML = html;
}

function showErr(m) { const e = document.getElementById("err"); e.textContent = m; e.style.display = "block"; }
function hideErr() { document.getElementById("err").style.display = "none"; }
loadExamples();
</script>
</body>
</html>`;

const json = (data) =>
  new Response(JSON.stringify(data, null, 2), {
    headers: { "content-type": "application/json;charset=utf-8" },
  });

export default {
  async fetch(request) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/proof/ship.json") return json(SHIP_PROOF);
    if (pathname === "/api/proof/blocked.json") return json(BLOCKED_PROOF);
    if (pathname === "/health") return json({ ok: true, service: "evidenza-demo" });
    return new Response(HTML, {
      headers: { "content-type": "text/html;charset=utf-8" },
    });
  },
};
