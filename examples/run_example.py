"""Minimal end-to-end example.

    GEMINI_API_KEY=... python examples/run_example.py

Reads the shipped synthetic sub-quote and prints the structured result.
See docs/FREE_MODELS.md for free key options.
"""
import os
from bidreader import read

HERE = os.path.dirname(__file__)
doc = read(os.path.join(HERE, "sample_quote.pdf"))

print(f"{doc.get('vendor')} — {doc.get('trade')} — total ${doc.get('bid_total'):,.2f}")
print(f"line items: {len(doc.line_items)}")
print(f"\nexclusions caught ({len(doc.exclusions)}):")
for e in doc.exclusions:
    print(f"  - {e['item']} (p{e['page']}): \"{e['quote'][:80]}\"")
print(f"\nscope gaps to confirm ({len(doc.scope_gaps)}):")
for g in doc.scope_gaps:
    print(f"  - {g['missing']}")
