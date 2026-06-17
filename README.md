<div align="center">

# 📄 BidReader

### Read messy construction sub-quotes, bid packages & spec PDFs into clean structured data — and catch the scope gaps and exclusions vendors bury in the fine print.

Every line item carries its **page**, the **exact source text** it came from, and an **arithmetic check** (`qty × unit_price == amount`) — verification on top of extraction, not just an LLM guess.

[![PyPI](https://img.shields.io/pypi/v/bidreader?color=2ea043&label=pip%20install%20bidreader)](https://pypi.org/project/bidreader/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![MCP](https://img.shields.io/badge/MCP-server-8b5cf6)](docs/MCP.md)
[![Runs on free models](https://img.shields.io/badge/runs%20on-free%20LLMs-success)](docs/FREE_MODELS.md)

</div>

---

> *"Manually typing numbers from a PDF into Excel because the formatting is a crime scene… hunting for the one line where a sub quietly excluded 'trash removal' in size-8 font."*
> — r/Construction, **498 upvotes** ([source](https://www.reddit.com/r/Construction/comments/1pq34ur/))

The construction-AI gold rush is all chasing the same crowded, resisted thing — autonomous *takeoff*. The **loudest unmet pain** of estimators is upstream and downstream of it: wrangling crime-scene PDFs into clean data, and **catching what subcontractors quietly excluded** before it costs six figures on the job.

No permissively-licensed library did this. **BidReader is that primitive** — MIT, `pip install`, runs on free LLMs, and callable from any AI agent over MCP.

## Quickstart (copy-paste, ~30 seconds)

```bash
pip install bidreader

# Use any one — a FREE key works (see docs/FREE_MODELS.md):
export GEMINI_API_KEY=...        # free at aistudio.google.com
# or  export OPENROUTER_API_KEY=...   (has :free models)
# or  export REQUESTY_API_KEY=...

bidreader your_sub_quote.pdf
```

```python
from bidreader import read

doc = read("sub_quote.pdf")
doc.line_items     # [{section, description, qty, unit, amount, page}, ...]
doc.exclusions     # [{item, quote, page, risk}, ...]   <- the buried stuff
doc.scope_gaps     # trade-standard scope NOT in the doc — confirm before bidding
doc.to_json()
```

## Real output

On a real **$324,240.61 drywall estimate** (72 line items, scanned in seconds), BidReader's scope engine caught a genuinely expensive hole:

```
!!  SCOPE GAPS TO CONFIRM:
  - Finishing (taping, mudding, sanding) -- the gypsum line items price the BOARD
    only, not the finishing labor to reach a paint-ready surface.
  - Door hardware -- "Door W/ Frame" lines don't include hinges/locks/closers.
  - Firestopping at rated assemblies -- life-safety scope, commonly omitted.
```

On a real **25-page multi-trade GC estimate**, it parsed **959 line items across 16 CSI divisions** (demolition → concrete → steel → finishes → plumbing → fire suppression), each page-cited. See [docs/RESULTS.md](docs/RESULTS.md) and a full worked example in [`examples/`](examples/).

## Bid leveling — compare subs side-by-side → Excel

The bid-day workflow: read every sub's quote and level them apples-to-apples.

```bash
pip install "bidreader[xlsx]"
bidreader level voltage_bros.pdf current_co.pdf sparky.pdf -o leveling.xlsx
```

It builds an Excel workbook (bidders as columns) with a **scope/exclusion matrix** that exposes the catch every estimator dreads — the *apparent* low bid that quietly carved out scope:

```
                  Voltage Bros   Current Co   Sparky
Bid total            $64,300      $108,890    $77,520
                     ◀ LOW
EXCLUSION MATRIX (filled = this bidder EXCLUDED it):
Fire alarm system    EXCL p1         —        EXCL p1
Temporary power      EXCL p1         —        EXCL p1
Permits                 —            —        EXCL p1
```

The "$64,300 low bid" excluded the fire alarm the $108,890 bid *includes* — not actually the cheapest. Plus per-bidder detail sheets with line items + arithmetic flags. (Try it: `python examples/make_leveling_sample.py` → `examples/leveling_demo.xlsx`.)

## Use it from an AI agent (MCP)

```bash
pip install "bidreader[mcp]"
```
```json
{ "mcpServers": { "bidreader": {
    "command": "bidreader-mcp",
    "env": { "GEMINI_API_KEY": "..." }
}}}
```
Tools: `read_document`, `catch_exclusions`, `extract_line_items`. Now your agent can answer *"which subs excluded fire-stopping across this bid folder?"* Full guide: [docs/MCP.md](docs/MCP.md).

## How it works

```
PDF (sub-quote / bid package / spec / schedule)
  → page-tagged text extraction (PyMuPDF)
  → chunk by page  (scales to 25+ page, 900+ line-item estimates)
  → LLM structured extraction  (line items · exclusions · assumptions · alternates · scope gaps)
  → merge + page-cited output (JSON / CLI / MCP)
```

Text-based, so it runs great on **free** models — see [docs/FREE_MODELS.md](docs/FREE_MODELS.md).

## Benchmark

Reproducible ground-truth benchmark ([`benchmark/`](benchmark/)) — synthetic docs we author, so truth is exact and the PDFs ship in-repo:

| metric | score |
|---|---|
| Line-item recall | **100%** |
| Exclusion-catch recall (incl. prose-buried) | **100%** |
| No-hallucination rate (clean docs) | **100%** |
| Bid-total accuracy (±2%) | **100%** |
| Arithmetic errors caught | **2/2**, 0 false positives |

Honest caveat: synthetic docs are cleaner than real scans — these are an **upper bound** on well-structured input, not a claim about messy real bids. Uncontrolled real-document results are in [docs/RESULTS.md](docs/RESULTS.md). Reproduce: `python benchmark/generate.py && python benchmark/run.py`.

## Why this, and why now — the evidence

A full write-up (problem, market data, prior-art gap, method, results) is in **[PAPER.md](PAPER.md)**. The short version:

- **Loudest, most-shared pain** in construction-estimating communities (the 498-upvote thread above; more cited in the paper).
- **It works *today*** — document extraction is LLM-native, unlike floor-plan symbol detection (academic SOTA tops out ~83% mAP).
- **Empty slot** — `bidreader`, `blueprint-parser`, `pytakeoff` were all unclaimed on PyPI; the only adjacent tools are AGPL/non-commercial or abandoned toys.
- **Broadest base** — every estimator *and* every construction-AI builder needs document extraction. The library is the dependency; the MCP server is the agent-era surface.

## Roadmap

- [ ] Scanned-PDF vision OCR path
- [ ] Revision/addendum **diff** ("what changed between Addendum 3 and 4")
- [ ] Excel/CSV BOQ export + multi-quote **leveling** (compare subs side-by-side)
- [ ] Region/trade notation packs (AISC, BS/IS, AUS)

## Contributing

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Good first issues: add a notation parser, a new export format, or a test fixture.

## License

[MIT](LICENSE) © 2026. Cite via [CITATION.cff](CITATION.cff).
