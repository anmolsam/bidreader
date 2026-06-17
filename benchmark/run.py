"""Run BidReader on every benchmark doc and score against committed ground truth.

Writes benchmark/scorecard.json and benchmark/SCORECARD.md.

    GEMINI_API_KEY=...  python benchmark/run.py        # any supported key
"""
import os, sys, json, re, glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from bidreader import read

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS, EXP = os.path.join(HERE, "docs"), os.path.join(HERE, "expected")


def toks(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def match_line_items(pred, truth):
    """Greedy: each truth item matched to a predicted item with amount within 2%
    (or $1) AND description token overlap >= 0.3."""
    used, found = set(), 0
    for ti in truth:
        ta, tt = ti["amount"], toks(ti["description"])
        best, bestscore = None, 0.0
        for j, pi in enumerate(pred):
            if j in used:
                continue
            pa = pi.get("amount")
            if not isinstance(pa, (int, float)):
                continue
            if abs(pa - ta) > max(1.0, abs(ta) * 0.02):
                continue
            ov = len(tt & toks(pi.get("description"))) / (len(tt) or 1)
            if ov > bestscore:
                best, bestscore = j, ov
        if best is not None and bestscore >= 0.3:
            used.add(best); found += 1
    return found


def score_case(exp, doc):
    pred_items = doc.get("line_items", [])
    truth = exp["line_items"]
    li_found = match_line_items(pred_items, truth)
    li_recall = li_found / len(truth) if truth else 1.0

    # exclusions caught (verbatim substring in any predicted exclusion quote)
    quotes = " || ".join((e.get("quote") or "") for e in doc.get("exclusions", [])).lower()
    keys = exp["exclusion_keys"]
    excl_found = sum(1 for k in keys if k.lower() in quotes)
    excl_recall = excl_found / len(keys) if keys else 1.0
    # no-hallucination: clean docs must not invent exclusions
    emax = exp.get("expect_exclusions_max")
    no_halluc = (len(doc.get("exclusions", [])) <= emax) if emax is not None else True

    # arithmetic-error detection
    err_idx = set(exp["math_error_idx"])
    math_metrics = None
    if err_idx or True:
        # map predicted mismatches back to truth lines by amount
        truth_err_amounts = {round(truth[i]["amount"], 2) for i in err_idx}
        truth_ok_amounts = {round(truth[i]["amount"], 2) for i in range(len(truth)) if i not in err_idx}
        pred_mismatch_amts = {round(p["amount"], 2) for p in pred_items
                              if p.get("math_check") == "mismatch" and isinstance(p.get("amount"), (int, float))}
        caught = len(truth_err_amounts & pred_mismatch_amts)
        false_pos = len(pred_mismatch_amts & truth_ok_amounts)
        math_metrics = {"planted": len(err_idx), "caught": caught, "false_positive": false_pos}

    total_ok = isinstance(doc.get("bid_total"), (int, float)) and \
        abs(doc["bid_total"] - exp["bid_total"]) <= max(1.0, exp["bid_total"] * 0.02)

    return {
        "line_item_recall": round(li_recall, 3), "line_items_found": li_found,
        "line_items_expected": len(truth),
        "exclusion_recall": round(excl_recall, 3), "exclusions_found": excl_found,
        "exclusions_expected": len(keys), "no_hallucination": no_halluc,
        "bid_total_ok": total_ok, "math": math_metrics,
    }


def main():
    expected = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(EXP, "*.json"))}
    rows = []
    for cid, exp in sorted(expected.items()):
        pdf = os.path.join(DOCS, f"{cid}.pdf")
        if not os.path.exists(pdf):
            print(f"!! missing {pdf} — run generate.py first"); continue
        print(f"scoring {cid} ...", file=sys.stderr)
        doc = read(pdf)
        rows.append((cid, score_case(exp, doc)))

    # aggregate
    li = sum(r["line_item_recall"] for _, r in rows) / len(rows)
    ex = sum(r["exclusion_recall"] for _, r in rows) / len(rows)
    halluc_ok = sum(1 for _, r in rows if r["no_hallucination"]) / len(rows)
    tot_ok = sum(1 for _, r in rows if r["bid_total_ok"]) / len(rows)
    planted = sum(r["math"]["planted"] for _, r in rows if r["math"])
    caught = sum(r["math"]["caught"] for _, r in rows if r["math"])
    fp = sum(r["math"]["false_positive"] for _, r in rows if r["math"])

    agg = {"cases": len(rows), "line_item_recall": round(li, 3), "exclusion_recall": round(ex, 3),
           "no_hallucination_rate": round(halluc_ok, 3), "bid_total_accuracy": round(tot_ok, 3),
           "math_errors_planted": planted, "math_errors_caught": caught, "math_false_positives": fp}
    json.dump({"aggregate": agg, "per_case": dict(rows)}, open(os.path.join(HERE, "scorecard.json"), "w"), indent=2)

    # markdown
    md = ["# Benchmark scorecard", "",
          f"BidReader scored against {len(rows)} synthetic ground-truth documents "
          "(authored here, so truth is exact and PDFs are freely redistributable).",
          "Reproduce: `python benchmark/generate.py && python benchmark/run.py`.", "",
          "## Aggregate", "",
          f"| metric | score |", "|---|---|",
          f"| Line-item recall | **{li:.0%}** |",
          f"| Exclusion-catch recall | **{ex:.0%}** |",
          f"| No-hallucination rate (clean docs) | **{halluc_ok:.0%}** |",
          f"| Bid-total accuracy (±2%) | **{tot_ok:.0%}** |",
          f"| Arithmetic errors planted / caught | **{caught}/{planted}** (false positives: {fp}) |",
          "", "## Per case", "",
          "| case | line items | exclusions | no-halluc | total ✓ | math caught |",
          "|---|---|---|---|---|---|"]
    for cid, r in rows:
        m = r["math"]; mc = f'{m["caught"]}/{m["planted"]}' if m and m["planted"] else "—"
        md.append(f'| `{cid}` | {r["line_items_found"]}/{r["line_items_expected"]} '
                  f'({r["line_item_recall"]:.0%}) | {r["exclusions_found"]}/{r["exclusions_expected"]} | '
                  f'{"✅" if r["no_hallucination"] else "❌"} | {"✅" if r["bid_total_ok"] else "❌"} | {mc} |')
    md += ["", "_Synthetic benchmark; results vary slightly by model. Run with `BID_MODEL` of your choice._"]
    open(os.path.join(HERE, "SCORECARD.md"), "w").write("\n".join(md) + "\n")

    print("\n=== AGGREGATE ===")
    for k, v in agg.items():
        print(f"  {k}: {v}")
    print("\nwrote benchmark/scorecard.json + benchmark/SCORECARD.md")


if __name__ == "__main__":
    main()
