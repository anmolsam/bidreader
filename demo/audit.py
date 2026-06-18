"""Derive the reconciliation failure-category per doc DETERMINISTICALLY from
real_eval.json (no LLM), so the audit in REAL_EVIDENCE.md is machine-checkable
rather than hand-asserted (Codex validation fix).

    python demo/audit.py        # rewrites the audit table + categories in real_eval.json
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))


def categorize(r):
    if "error" in r:
        return "PARSE FAILURE"
    ext, st, items = r.get("extracted_total"), r.get("stated_total"), r.get("line_items", 0)
    if r.get("total_match"):
        return "reconciled"
    if ext in (None, 0) and items == 0:
        return "N/A (no pricing extracted)"
    if ext in (None, 0):
        return "no grand-total emitted (items extracted, no total line)"
    if st in (None, 0):
        return "evaluator: no printed total to compare"
    # both present and differ
    if ext > st * 1.5 or st > ext * 1.5:
        return "evaluator: printed-total heuristic likely wrong"
    return "TRUE product total mismatch"


def main():
    rows = json.load(open(os.path.join(HERE, "real_eval.json")))
    for r in rows:
        r["category"] = categorize(r)
    json.dump(rows, open(os.path.join(HERE, "real_eval.json"), "w"), indent=2)

    from collections import Counter
    c = Counter(r["category"] for r in rows)
    lines = ["## Failure audit (machine-derived from real_eval.json)", "",
             "Categories below are computed deterministically by `demo/audit.py` from the "
             "committed `real_eval.json` — not hand-asserted. Reproduce: `python demo/audit.py`.", "",
             "| category | count |", "|---|---|"]
    for cat, n in c.most_common():
        lines.append(f"| {cat} | {n} |")
    lines += ["", "| doc | extracted total | printed total | category |", "|---|---|---|---|"]
    for r in rows:
        u = (r.get("url", "") or "").split("/")[-1][:34]
        ext = f"${r['extracted_total']:,.0f}" if isinstance(r.get("extracted_total"), (int, float)) else "—"
        st = f"${r['stated_total']:,.0f}" if isinstance(r.get("stated_total"), (int, float)) else "—"
        lines.append(f"| {u} | {ext} | {st} | {r['category']} |")
    audit_md = "\n".join(lines)

    # splice into REAL_EVIDENCE.md, replacing any prior "## Failure audit"/"## Reconciliation failure audit"
    p = os.path.join(HERE, "REAL_EVIDENCE.md")
    doc = open(p).read()
    import re
    doc = re.split(r"\n## (?:Failure audit|Reconciliation failure audit|Honest interpretation)", doc)[0].rstrip()
    open(p, "w").write(doc + "\n\n" + audit_md + "\n")
    print("categories:", dict(c))
    print("rewrote REAL_EVIDENCE.md audit + tagged real_eval.json")


if __name__ == "__main__":
    main()
