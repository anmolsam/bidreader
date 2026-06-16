"""Run BidReader on a PDF and print an estimator-facing report."""
import sys
from bidreader import read

path = sys.argv[1] if len(sys.argv) > 1 else "/Users/anmol/bidreader/sample_quote.pdf"
d = read(path)

print("=" * 74)
print(f"BIDREADER  |  {d['_source']}  ({d['_pages']}p)")
print("=" * 74)
print(f"{d.get('doc_type','?')}  |  {d.get('vendor','?')}  |  trade: {d.get('trade','?')}  |  {d.get('currency','')}")
print(f"Project: {d.get('project','?')}")
print(f"\nLINE ITEMS ({len(d.line_items)}):")
print(f"  {'CSI':10s}{'Description':40s}{'Qty':>8s}{'Unit':>5s}{'Amount':>12s}  pg")
for li in d.line_items:
    print(f"  {str(li.get('section') or '-'):10s}{str(li.get('description',''))[:39]:40s}"
          f"{str(li.get('qty') or ''):>8s}{str(li.get('unit') or ''):>5s}"
          f"{('$'+format(li['amount'],',.2f')) if li.get('amount') is not None else '':>12s}  {li.get('page','?')}")
print(f"  {'BID TOTAL':55s}{('$'+format(d['bid_total'],',.2f')) if d.get('bid_total') else '?':>12s}")

print(f"\n⚠  EXCLUSIONS CAUGHT ({len(d.exclusions)})  — the stuff buried in fine print:")
for e in d.exclusions:
    print(f"   • {e.get('item','?')}   (page {e.get('page','?')})")
    print(f"       \"{e.get('quote','')[:110]}\"")
    print(f"       risk: {e.get('risk','')}")

if d.get("alternates"):
    print(f"\nALTERNATES ({len(d['alternates'])}):")
    for a in d["alternates"]:
        amt = ('$'+format(a['amount'],',.2f')) if a.get('amount') is not None else ''
        print(f"   • {a.get('text','')[:80]}  {amt}  (pg {a.get('page','?')})")

print(f"\nSCOPE GAPS TO CONFIRM ({len(d.scope_gaps)}):")
for g in d.scope_gaps:
    print(f"   • {g.get('missing','')} — {g.get('why','')}")
print(f"\nnotes: {d.get('notes','')}")
