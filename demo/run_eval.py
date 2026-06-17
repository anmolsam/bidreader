"""Run BidReader across the demo corpus, score honestly (including failures),
level the electrical & drywall sets to Excel, and write demo/EVIDENCE.md.

    GEMINI_API_KEY=... python demo/run_eval.py     # any supported key
"""
import os, sys, json, re, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bidreader import read
from bidreader.leveling import level, to_xlsx, summary_text

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS, EXPECT = os.path.join(HERE, "corpus"), os.path.join(HERE, "expected")


def toks(s): return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def match_items(pred, truth):
    used, found = set(), 0
    for ti in truth:
        ta, tt = ti["amount"], toks(ti["description"])
        best, bs = None, 0.0
        for j, pi in enumerate(pred):
            if j in used or not isinstance(pi.get("amount"), (int, float)):
                continue
            if abs(pi["amount"] - ta) > max(1.0, abs(ta) * 0.03):
                continue
            ov = len(tt & toks(pi.get("description"))) / (len(tt) or 1)
            if ov > bs:
                best, bs = j, ov
        if best is not None and bs >= 0.3:
            used.add(best); found += 1
    return found


def score(exp, doc):
    truth = exp["line_items"]
    li_found = match_items(doc.get("line_items", []), truth)
    quotes = " || ".join((e.get("quote") or "") for e in doc.get("exclusions", [])).lower()
    keys = exp["exclusion_keys"]
    ex_found = sum(1 for k in keys if k.lower() in quotes)
    err_amts = {round(truth[i]["amount"], 2) for i in exp["math_error_idx"]}
    pred_mis = {round(p["amount"], 2) for p in doc.get("line_items", [])
                if p.get("math_check") == "mismatch" and isinstance(p.get("amount"), (int, float))}
    total_ok = isinstance(doc.get("bid_total"), (int, float)) and \
        abs(doc["bid_total"] - exp["bid_total"]) <= max(1.0, exp["bid_total"] * 0.03)
    return {
        "li_found": li_found, "li_total": len(truth),
        "li_recall": li_found / len(truth) if truth else 1.0,
        "ex_found": ex_found, "ex_total": len(keys),
        "ex_recall": ex_found / len(keys) if keys else None,
        "no_halluc": (len(doc.get("exclusions", [])) == 0) if exp.get("no_excl") else None,
        "math_planted": len(err_amts), "math_caught": len(err_amts & pred_mis),
        "total_ok": total_ok, "text_source": doc.get("_text_source"),
    }


def main():
    idx = json.load(open(os.path.join(HERE, "corpus_index.json")))
    rows = []
    for c in idx:
        cid = c["id"]; exp = json.load(open(os.path.join(EXPECT, f"{cid}.json")))
        print(f"eval {cid} ({'scanned' if c['scanned'] else 'text'}) ...", file=sys.stderr)
        try:
            doc = read(os.path.join(CORPUS, f"{cid}.pdf"))
            rows.append((c, score(exp, doc), None))
        except Exception as e:
            rows.append((c, None, f"{type(e).__name__}: {e}"))

    ok = [r for r in rows if r[1]]
    li_rec = sum(r[1]["li_recall"] for r in ok) / len(ok)
    ex_rows = [r for r in ok if r[1]["ex_recall"] is not None]
    ex_rec = sum(r[1]["ex_recall"] for r in ex_rows) / len(ex_rows)
    mp = sum(r[1]["math_planted"] for r in ok); mc = sum(r[1]["math_caught"] for r in ok)
    tot_ok = sum(1 for r in ok if r[1]["total_ok"]) / len(ok)
    halluc = [r for r in ok if r[1]["no_halluc"] is not None]
    scanned_ok = [r for r in ok if r[1]["text_source"] == "ocr"]

    # leveling sets -> xlsx + markdown matrix
    lev_md = {}
    for setname in ("electrical", "drywall"):
        paths = [os.path.join(CORPUS, f"{c['id']}.pdf") for c in idx if c.get("set") == setname]
        res = level(paths)
        out = os.path.join(HERE, f"leveling_{setname}.xlsx"); to_xlsx(res, out)
        lev_md[setname] = summary_text(res)
        print(f"wrote leveling_{setname}.xlsx ({len(paths)} bids)", file=sys.stderr)

    # render two messy input pages to PNG (proof of messiness)
    import fitz
    shots = []
    for cid in ("elec_sub_d", "demo_scanned_messy"):
        d = fitz.open(os.path.join(CORPUS, f"{cid}.pdf"))
        pix = d[0].get_pixmap(dpi=110)
        p = os.path.join(HERE, f"sample_{cid}.png"); pix.save(p); shots.append(os.path.basename(p))

    # ---- write EVIDENCE.md ----
    M = ["# BidReader — Evidence Pack", "",
         f"BidReader run across **{len(idx)} synthetic but messy** construction bids "
         "(prose-buried exclusions, fine-print footnotes, two-column layouts, planted "
         "arithmetic errors, multi-page, and image-only **scanned** docs). Authored here → "
         "exact ground truth, freely redistributable. Reproduce: "
         "`python demo/make_corpus.py && python demo/run_eval.py`.", "",
         "## Aggregate (honest — includes failures)", "",
         "| metric | result |", "|---|---|",
         f"| Documents | {len(idx)} ({sum(1 for c in idx if c['scanned'])} scanned) |",
         f"| Line-item recall | **{li_rec:.0%}** |",
         f"| Exclusion-catch recall | **{ex_rec:.0%}** |",
         f"| Bid-total accuracy (±3%) | **{tot_ok:.0%}** |",
         f"| Arithmetic errors caught | **{mc}/{mp}** |",
         f"| No-hallucination (clean doc) | {'PASS' if all(r[1]['no_halluc'] for r in halluc) else 'CHECK'} |",
         f"| Scanned docs OCR'd & extracted | {len(scanned_ok)}/{sum(1 for c in idx if c['scanned'])} |",
         "", "## Per document", "",
         "| doc | trade | input | line items | exclusions | math | total | notes |",
         "|---|---|---|---|---|---|---|---|"]
    fails = []
    for c, s, err in rows:
        if err:
            M.append(f"| `{c['id']}` | {c['trade']} | {c['style']} | — | — | — | — | ❌ {err[:40]} |")
            fails.append((c["id"], err)); continue
        src = "scan→OCR" if s["text_source"] == "ocr" else "text"
        exr = f"{s['ex_found']}/{s['ex_total']}" if s["ex_total"] else "n/a"
        mathc = f"{s['math_caught']}/{s['math_planted']}" if s["math_planted"] else "—"
        note = []
        if s["li_recall"] < 1: note.append(f"missed {s['li_total']-s['li_found']} items")
        if s["ex_total"] and s["ex_found"] < s["ex_total"]: note.append("missed excl")
        if s["math_planted"] and s["math_caught"] < s["math_planted"]: note.append("missed math err")
        if not s["total_ok"]: note.append("total off")
        flag = "⚠ " + "; ".join(note) if note else "✓"
        M.append(f"| `{c['id']}` | {c['trade']} | {src} | {s['li_found']}/{s['li_total']} "
                 f"({s['li_recall']:.0%}) | {exr} | {mathc} | {'✓' if s['total_ok'] else '✗'} | {flag} |")

    M += ["", "## Honest failure / weakness notes", ""]
    weak = [f"`{c['id']}`: {'; '.join([n for n in [] ])}" for c, s, e in rows if s and (s['li_recall']<1 or (s['ex_total'] and s['ex_found']<s['ex_total']))]
    weak_lines = []
    for c, s, e in rows:
        if e:
            weak_lines.append(f"- **`{c['id']}` failed**: {e}")
        elif s and (s["li_recall"] < 1 or (s["ex_total"] and s["ex_found"] < s["ex_total"]) or (s["math_planted"] and s["math_caught"] < s["math_planted"])):
            issues = []
            if s["li_recall"] < 1: issues.append(f"{s['li_total']-s['li_found']} line item(s) missed ({c['style']} layout)")
            if s["ex_total"] and s["ex_found"] < s["ex_total"]: issues.append(f"{s['ex_total']-s['ex_found']} exclusion(s) missed")
            if s["math_planted"] and s["math_caught"] < s["math_planted"]: issues.append("planted math error missed")
            weak_lines.append(f"- `{c['id']}` ({c['style']}): " + "; ".join(issues))
    M += weak_lines or ["- No extraction failures in this run. (Two-column and scanned-low-DPI docs are the usual weak spots; see those rows.)"]

    M += ["", "## Bid leveling — Excel output (the bid-day workflow)", "",
          "Multiple subs → one workbook, bidders as columns, exclusion matrix exposing "
          "the *apparent low bid that carved out scope*. Workbooks: "
          "`leveling_electrical.xlsx`, `leveling_drywall.xlsx`.", "",
          "### Electrical (4 subs)", "```", lev_md["electrical"], "```",
          "### Drywall (3 subs)", "```", lev_md["drywall"], "```",
          "", "## Sample messy inputs", "",
          *[f"![{s}]({s})" for s in shots],
          "", "_Synthetic corpus; results vary by model. Outputs are proposals to verify, never final numbers._"]
    open(os.path.join(HERE, "EVIDENCE.md"), "w").write("\n".join(M) + "\n")

    print("\n=== AGGREGATE ===")
    print(f"docs={len(idx)} li_recall={li_rec:.0%} ex_recall={ex_rec:.0%} "
          f"total_ok={tot_ok:.0%} math={mc}/{mp} scanned_ok={len(scanned_ok)} fails={len(fails)}")
    print("wrote demo/EVIDENCE.md + leveling_*.xlsx + sample PNGs")


if __name__ == "__main__":
    main()
