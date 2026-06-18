"""`bidreader <file.pdf>` — print an estimator report, or `--json` for piping."""
import sys, json
from .extract import read


def _level(argv):
    from .leveling import level, to_xlsx, summary_text
    out = "leveling.xlsx"
    if "-o" in argv:
        i = argv.index("-o"); out = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    pdfs = [a for a in argv if a.lower().endswith(".pdf")]
    if len(pdfs) < 2:
        print("usage: bidreader level <quote1.pdf> <quote2.pdf> [...] [-o leveling.xlsx]"); sys.exit(1)
    print(f"leveling {len(pdfs)} bids ...", file=sys.stderr)
    result = level(pdfs)
    print(summary_text(result))
    to_xlsx(result, out)
    print(f"\nwrote {out}")


def main():
    args = [a for a in sys.argv[1:]]
    if args and args[0] == "level":
        _level(args[1:]); return
    as_json = "--json" in args
    ocr = "auto"
    if "--ocr" in args:
        i = args.index("--ocr"); ocr = args[i + 1] if i + 1 < len(args) else "auto"
        args = args[:i] + args[i + 2:]
    paths = [a for a in args if not a.startswith("-")]
    if not paths:
        print("usage: bidreader <document.pdf> [--json] [--ocr auto|always|never]\n"
              "       bidreader level <q1.pdf> <q2.pdf> [...] [-o leveling.xlsx]"); sys.exit(1)
    d = read(paths[0], ocr=ocr)
    if as_json:
        print(d.to_json()); return
    g = lambda k, default="unknown": d.get(k) or default
    print("=" * 74)
    print(f"BIDREADER  |  {d['_source']}  ({d['_pages']}p)")
    print("=" * 74)
    meta = "  |  ".join(x for x in [g('doc_type', 'document'), g('vendor', ''),
                                    f"trade: {g('trade')}", g('currency', 'USD')] if x)
    print(meta)
    if d.get('project'):
        print(f"Project: {d['project']}")
    print(f"\nLINE ITEMS ({len(d.line_items)}):")
    for li in d.line_items:
        amt = ('$' + format(li['amount'], ',.2f')) if li.get('amount') is not None else ''
        sec = str(li.get('section') or '-')[:12]
        desc = str(li.get('description', ''))[:42]
        print(f"  {sec:12.12s}  {desc:42.42s} {str(li.get('qty') or ''):>8s}"
              f"{str(li.get('unit') or ''):>5s}{amt:>13s}  p{li.get('page','?')}")
    if d.get('bid_total'):
        src = d.get('total_source', '')
        tag = "(summed from line items)" if src == "sum-of-line-items" else ""
        print(f"  {'BID TOTAL ' + tag:56s}{'$' + format(d['bid_total'], ',.2f'):>13s}")
        if d.get('total_reconciles') is False:
            print(f"  !! printed total vs sum-of-items off by {d.get('total_delta_pct')}% — verify missing/duplicate items")
    mm = [li for li in d.line_items if li.get('math_check') == 'mismatch']
    if mm:
        print(f"\n!!  ARITHMETIC MISMATCHES ({len(mm)}) — qty x unit_price != amount:")
        for li in mm[:10]:
            print(f"   - p{li.get('page','?')} {str(li.get('description',''))[:46]}: "
                  f"stated {li.get('amount')}, computed {li.get('math_expected')}")
    print(f"\n!!  EXCLUSIONS CAUGHT ({len(d.exclusions)}):")
    for e in d.exclusions:
        print(f"   - {e.get('item','?')}  (page {e.get('page','?')})")
        print(f"       \"{e.get('quote','')[:120]}\"")
        print(f"       risk: {e.get('risk','')}")
    if d.scope_gaps:
        print(f"\nSCOPE GAPS TO CONFIRM ({len(d.scope_gaps)}):")
        for gp in d.scope_gaps:
            print(f"   - {gp.get('missing','')} -- {gp.get('why','')}")

    # trust-building footer
    n_priced = sum(1 for li in d.line_items if isinstance(li.get('amount'), (int, float)))
    tot = ('$' + format(d['bid_total'], ',.0f')) if d.get('bid_total') else "n/a"
    rec = {True: "reconciles", False: f"off {d.get('total_delta_pct')}%", None: "—"}.get(d.get('total_reconciles'))
    src = "scan→OCR" if d.get('_text_source') == 'ocr' else "text"
    print("\n" + "-" * 74)
    print(f"total {tot} ({d.get('total_source','?')}, {rec})  |  {len(d.line_items)} items "
          f"({n_priced} priced)  |  {len(mm)} math flags  |  {len(d.exclusions)} exclusions  |  {src}")
    print("every line cites its page + source_text. Next:  bidreader <pdf> --json"
          "   |   bidreader level q1.pdf q2.pdf -o leveling.xlsx")


if __name__ == "__main__":
    main()
