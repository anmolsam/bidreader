"""Real-document evaluation — runs BidReader on REAL public bid/estimate PDFs and
validates against each document's OWN printed total (objective ground truth that
lives in the doc; no manual labeling needed).

We do NOT redistribute the third-party PDFs (copyright) — the manifest cites
source URLs, and only the extraction summary is committed (demo/REAL_EVIDENCE.md).

    GEMINI_API_KEY=... python demo/real_eval.py /path/to/manifest.json
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fitz
from bidreader import read

HERE = os.path.dirname(os.path.abspath(__file__))

# match "...total... $1,234,567.89" — grand/bid/contract total preferred
_TOTAL = re.compile(r"(grand\s+total|bid\s+total|total\s+bid|contract\s+(?:sum|amount)|"
                    r"total\s+(?:amount|price|cost)?)\s*[:\-]?\s*\$?\s*([\d,]+(?:\.\d{2})?)",
                    re.I)
_MONEY = re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)")


def printed_total(doc):
    """Best-effort: the document's own stated total (independent of extraction)."""
    text = "\n".join(p.get_text() for p in doc)
    cands = []
    for m in _TOTAL.finditer(text):
        try:
            cands.append(float(m.group(2).replace(",", "")))
        except ValueError:
            pass
    if cands:
        return max(cands)               # grand total is the largest "total" line
    money = [float(m.group(1).replace(",", "")) for m in _MONEY.finditer(text)]
    return max(money) if money else None


def close(a, b, tol=0.02):
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and b and \
        abs(a - b) <= max(1.0, abs(b) * tol)


def main():
    manifest = sys.argv[1] if len(sys.argv) > 1 else "/Users/anmol/realbids/manifest.json"
    items = json.load(open(manifest))
    rows = []
    for it in items:
        path = it["path"]
        try:
            doc = fitz.open(path)
            stated = it.get("printed_total") or printed_total(doc)
            res = read(path)
            extracted = res.get("bid_total")
            math_flags = res.get("math_flagged", 0)
            rows.append({
                "url": it.get("url", ""), "pages": res.get("_pages"),
                "src": res.get("_text_source"), "scanned": it.get("scanned", False),
                "line_items": len(res.get("line_items", [])),
                "exclusions": len(res.get("exclusions", [])),
                "extracted_total": extracted, "stated_total": stated,
                "total_match": close(extracted, stated), "math_flags": math_flags,
                "note": it.get("note", ""),
            })
            print(f"OK  {os.path.basename(path)}  items={rows[-1]['line_items']} "
                  f"extracted={extracted} stated={stated} match={rows[-1]['total_match']}", file=sys.stderr)
        except Exception as e:
            rows.append({"url": it.get("url", ""), "error": f"{type(e).__name__}: {e}",
                         "note": it.get("note", "")})
            print(f"ERR {os.path.basename(path)}: {e}", file=sys.stderr)

    ok = [r for r in rows if "error" not in r]
    matched = [r for r in ok if r["total_match"]]
    scanned_ok = [r for r in ok if r["src"] == "ocr"]
    tot_items = sum(r["line_items"] for r in ok)

    M = ["# BidReader — Real-document evaluation", "",
         f"BidReader run on **{len(items)} real, publicly-published** construction "
         "bid/estimate PDFs (estimating-firm samples, government bid docs). The PDFs are "
         "**not redistributed** (copyright) — each row cites its source URL; re-download to verify.", "",
         "**Objective check:** does BidReader's extracted grand total reconcile (±2%) with "
         "the total the document itself prints? That ground truth lives in each doc, so no "
         "manual labeling is needed. (Full line-item/exclusion ground truth would need an "
         "estimator; this measures real-world total-reconciliation + ingestion robustness.)", "",
         "## Aggregate", "",
         "| metric | result |", "|---|---|",
         f"| Real documents | {len(items)} ({len(ok)} parsed, {len(rows)-len(ok)} failed) |",
         f"| Total reconciles with printed total (±2%) | **{len(matched)}/{len(ok)}** |",
         f"| Scanned docs OCR'd & parsed | {len(scanned_ok)} |",
         f"| Total line items extracted | {tot_items} |",
         "", "## Per document", "",
         "| source | pages | input | line items | excl | extracted total | printed total | match |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "error" in r:
            M.append(f"| {r['url'][:50]} | — | — | — | — | — | — | ❌ {r['error'][:30]} |")
            continue
        et = f"${r['extracted_total']:,.0f}" if isinstance(r['extracted_total'], (int, float)) else "—"
        st = f"${r['stated_total']:,.0f}" if isinstance(r['stated_total'], (int, float)) else "—"
        src = "scan→OCR" if r["src"] == "ocr" else "text"
        M.append(f"| {r['url'][:50]} | {r['pages']} | {src} | {r['line_items']} | "
                 f"{r['exclusions']} | {et} | {st} | {'✅' if r['total_match'] else '⚠'} |")
    M += ["", "_Real third-party documents (cited, not redistributed). Printed-total reconciliation "
          "is an objective real-world signal; it is not a substitute for estimator-labeled line-item "
          "ground truth. Outputs are proposals to verify._"]
    open(os.path.join(HERE, "REAL_EVIDENCE.md"), "w").write("\n".join(M) + "\n")
    json.dump(rows, open(os.path.join(HERE, "real_eval.json"), "w"), indent=2)
    print(f"\n=== REAL DOCS: {len(matched)}/{len(ok)} totals reconcile, {len(scanned_ok)} scanned OK, "
          f"{tot_items} line items, {len(rows)-len(ok)} failed ===")
    print("wrote demo/REAL_EVIDENCE.md + real_eval.json")


if __name__ == "__main__":
    main()
