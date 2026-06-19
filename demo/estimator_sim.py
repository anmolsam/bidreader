"""Run BidReader on 5 diverse REAL bid PDFs, then simulate 5 distinct skeptical
estimator personas reacting to the ACTUAL output (Codex's "would you use this on a
real bid this week?" test). SIMULATED — directional, not a substitute for real users.
"""
import os, sys, json, ssl, urllib.request, certifi
sys.path.insert(0, "/Users/anmol/bidreader")
from bidreader import read

SSLCTX = ssl.create_default_context(cafile=certifi.where())
DOCS = [
    ("residential GC addition (4pp)", "/Users/anmol/realbids/03_cts_residential_addition.pdf"),
    ("plumbing/MEP estimate (7pp)",   "/Users/anmol/realbids/15_plumbing_estimate.pdf"),
    ("sitework/concrete (11pp)",      "/Users/anmol/realbids/06_veracity_sitework.pdf"),
    ("AIA G703 schedule of values (3pp)", "/Users/anmol/realbids/17_sov_g703.pdf"),
    ("specialty contractor estimate (5pp)", "/Users/anmol/realbids/16_ace_renaldi.pdf"),
]

def summarize(label, path):
    try:
        d = read(path)
    except Exception as e:
        return f"### {label}\nFAILED: {type(e).__name__}: {e}\n"
    items = d.line_items
    sample = "\n".join(f"   - {str(li.get('section') or '-')} | {str(li.get('description',''))[:50]} | "
                       f"{li.get('qty')} {li.get('unit') or ''} | amount={li.get('amount')}" for li in items[:5])
    excl = "\n".join(f"   - {e.get('item','?')}: \"{(e.get('quote') or '')[:70]}\"" for e in d.exclusions[:4]) or "   (none)"
    gaps = "\n".join(f"   - {g.get('missing','')[:80]}" for g in d.scope_gaps[:4]) or "   (none)"
    rec = d.get("total_reconciles")
    rec_s = ("reconciles" if rec is True else f"items sum to {round((d.get('computed_total') or 0)/(d['bid_total'])*100) if d.get('bid_total') else '?'}% of printed (INCOMPLETE)" if rec is False else "—")
    return (f"### {label}  [{os.path.basename(path)}]\n"
            f"- {len(items)} line items ({sum(1 for li in items if isinstance(li.get('amount'),(int,float)))} priced) | "
            f"bid_total={d.get('bid_total')} ({d.get('total_source')}, {rec_s}) | "
            f"{len(d.exclusions)} exclusions | {len(d.scope_gaps)} scope-gaps | math_flags={d.get('math_flagged')}\n"
            f"  sample items:\n{sample}\n  exclusions caught:\n{excl}\n  scope-gaps inferred:\n{gaps}\n")

def llm(prompt):
    key = os.environ["REQUESTY_API_KEY"]
    body = {"model": "google/gemini-2.5-pro", "temperature": 0.5,
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("https://router.requesty.ai/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180, context=SSLCTX))["choices"][0]["message"]["content"]

def main():
    print("running BidReader on 5 real bids...", file=sys.stderr)
    summaries = "\n".join(summarize(l, p) for l, p in DOCS)
    prompt = f"""You are simulating FIVE DISTINCT, skeptical, realistic construction ESTIMATORS evaluating an
open-source tool called BidReader. It reads bid/estimate PDFs into page-cited line items, flags buried
exclusions, infers likely missing scope ("scope gaps"), arithmetic-checks lines, and levels multiple subs
into an Excel exclusion matrix. CLI: `pip install bidreader`; needs an LLM API key or local Ollama.

Below is BidReader's ACTUAL output on 5 real bid PDFs:

{summaries}

Simulate these 5 estimators reacting to the ACTUAL output above. Be CRITICAL and realistic — most estimators
are busy, skeptical of AI on numbers, and live in Excel/Bluebeam. Personas:
1. Frank — 25-yr chief estimator at a large commercial GC; Excel/Bluebeam power user; trusts nothing he can't verify.
2. Maria — preconstruction manager, mid-size GC; drowns in sub quotes on bid day; privacy-conscious (won't upload client bids to a cloud LLM).
3. Dave — owner of a small electrical sub; does his own estimating; NOT technical (won't run Python or Ollama).
4. Priya — construction-tech founder/engineer deciding whether to build ON bidreader as a dependency.
5. Tom — grizzled veteran; "AI as a second set of eyes only, never the first."

For EACH persona give: (a) gut reaction to the actual output, (b) what they'd TRUST vs DISTRUST citing specifics,
(c) the single dealbreaker or hook, (d) verdict: WOULD YOU USE THIS ON A REAL BID THIS WEEK? yes / maybe / no — and why.
Then a SYNTHESIS: how many of 5 would actually use it, the #1 adoption blocker, and the #1 thing to build next.
No flattery. Ground every point in the real output shown."""
    out = llm(prompt)
    open("/Users/anmol/bidreader/demo/ESTIMATOR_SIM.md", "w").write(
        "# Simulated estimator panel (5 personas) — DIRECTIONAL, not real users\n\n"
        "BidReader's real output on 5 real public bid PDFs, reacted to by 5 simulated estimator "
        "personas (LLM role-play). A substitute for *talking to 5 real estimators* this is NOT — "
        "it surfaces likely objections, not ground truth.\n\n"
        "## BidReader output on the 5 real bids\n\n" + summaries +
        "\n## The panel\n\n" + out + "\n")
    print(out)

if __name__ == "__main__":
    main()
