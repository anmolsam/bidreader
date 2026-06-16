# BidReader

**Read messy construction sub-quotes, bid packages & spec PDFs into clean structured data — and catch the scope gaps and exclusions vendors bury in the fine print.** Every value is cited to its page and exact source text.

MIT · `pip install bidreader` · works on the PDFs estimators actually get.

> *"Manually typing numbers from a PDF into Excel because the formatting is a crime scene… hunting for the one line where a sub quietly excluded 'trash removal' in size-8 font."* — r/Construction (498 upvotes)

BidReader is that junior who never sleeps: it doesn't write anything new — it finds what's already there and points to it.

---

## What it does

```bash
pip install bidreader
export REQUESTY_API_KEY=...        # or OPENROUTER_API_KEY / GEMINI_API_KEY (free tier works)
bidreader sub_quote.pdf
```

```python
from bidreader import read
doc = read("sub_quote.pdf")
doc.line_items     # [{section, description, qty, unit, amount, page}, ...]
doc.exclusions     # [{item, quote, page, risk}, ...]   <- the stuff they buried
doc.scope_gaps     # trade-standard scope NOT mentioned (confirm before you bid)
doc.to_json()
```

## Real output (drywall sub-quote, exclusion buried in size-7 font)

```
LINE ITEMS (5):
  09 22 16  Metal stud framing, 3-5/8" 25ga walls   12400 SF   $35,340.00  p1
  09 29 00  5/8" Type X gypsum board, both faces     24800 SF   $40,920.00  p1
  09 29 00  Tape & finish, Level 4                   24800 SF   $23,560.00  p1
  ...                                                 BID TOTAL  $121,628.00

!!  EXCLUSIONS CAUGHT (4):
  - Fire-stopping/firecaulking  (page 1)
      "this proposal EXCLUDES fire-stopping/firecaulking at rated assemblies"
      risk: life-safety scope; another trade or a change order eats this cost.
  - Debris removal/haul-off  (page 1)
      "removal/haul-off of construction debris (by others)"
  ...

SCOPE GAPS TO CONFIRM (5):
  - Acoustic ceiling tiles -- grid framing is included but the tiles within it are not.
  - Rough carpentry blocking/backing for fixtures -- not mentioned.
```

## Why

The construction-AI gold rush is all building the same crowded, resisted thing — autonomous *takeoff*. The loudest, most-repeated, **unmet** estimator pain is upstream and downstream of it: turning crime-scene PDFs into clean data and **catching what subs quietly excluded**. No permissive library does this. BidReader is that primitive.

- **MIT** — depend on it inside your commercial estimating/BIM product (no AGPL/NC contamination).
- **Provider-agnostic** — Requesty, OpenRouter, or Google AI Studio (free tier).
- **Cited** — every number traces to a page + the exact source text. Trust is the real adoption blocker; this is built for it.

## Use it from an AI agent (MCP)

Any MCP client — Claude Desktop, Cursor, etc. — can call BidReader:

```bash
pip install "bidreader[mcp]"
```
```json
{
  "mcpServers": {
    "bidreader": {
      "command": "bidreader-mcp",
      "env": { "REQUESTY_API_KEY": "rqsty-..." }
    }
  }
}
```
Tools exposed: `read_document(path)`, `catch_exclusions(path)`, `extract_line_items(path)`.
Now your agent can answer *"which subs excluded fire-stopping?"* across a bid folder.

## Roadmap
- Scanned-PDF vision OCR path · revision/addendum **diff** ("what changed between Addendum 3 and 4") · `bidreader-mcp` server (any agent can call it) · Excel/CSV export · multi-quote leveling (compare subs side-by-side).

## License
MIT.
