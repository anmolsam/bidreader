"""`bidreader <file.pdf>` — print an estimator report, or `--json` for piping."""
import sys, json
from .extract import read


def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    paths = [a for a in args if not a.startswith("-")]
    if not paths:
        print("usage: bidreader <document.pdf> [--json]"); sys.exit(1)
    d = read(paths[0])
    if as_json:
        print(d.to_json()); return
    print("=" * 74)
    print(f"BIDREADER  |  {d['_source']}  ({d['_pages']}p)")
    print("=" * 74)
    print(f"{d.get('doc_type','?')}  |  {d.get('vendor','?')}  |  trade: {d.get('trade','?')}  |  {d.get('currency','')}")
    print(f"Project: {d.get('project','?')}")
    print(f"\nLINE ITEMS ({len(d.line_items)}):")
    for li in d.line_items:
        amt = ('$' + format(li['amount'], ',.2f')) if li.get('amount') is not None else ''
        print(f"  {str(li.get('section') or '-'):10s}{str(li.get('description',''))[:40]:41s}"
              f"{str(li.get('qty') or ''):>8s}{str(li.get('unit') or ''):>5s}{amt:>13s}  p{li.get('page','?')}")
    if d.get('bid_total'):
        print(f"  {'BID TOTAL':56s}{'$' + format(d['bid_total'], ',.2f'):>13s}")
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
        for g in d.scope_gaps:
            print(f"   - {g.get('missing','')} -- {g.get('why','')}")


if __name__ == "__main__":
    main()
