# Results & reproduction

All tests run with `BID_MODEL=google/gemini-2.5-flash` via an OpenAI-compatible
gateway. The third-party PDFs below are **publicly published** by their authors;
we do **not** redistribute them (copyright) — reproduce from the source URLs.

## Synthetic example (shipped in `examples/`)

A generated drywall sub-quote with four exclusions buried in size-7 footnote text.

| Metric | Result |
|---|---|
| Line items | 5 (CSI, qty, unit, amount, page) |
| Bid total | $121,628.00 |
| Exclusions caught | **4/4** (fire-stopping, scaffolding >10', final cleaning, debris haul-off) |
| Scope gaps inferred | 5 |

Reproduce:
```bash
python make_sample.py            # writes examples/sample_quote.pdf
bidreader examples/sample_quote.pdf
```
Output is committed at [`examples/sample_output.txt`](../examples/sample_output.txt) / [`.json`](../examples/sample_output.json).

## Real document #1 — drywall estimate (2 pp.)

Source: `https://appleestimating.com/wp-content/uploads/2024/03/Estimate-Drywall.pdf`

| Metric | Result |
|---|---|
| Line items | **72** |
| Bid total | **$324,240.61** |
| Project | 600 Bushwick Ave, Brooklyn |
| Exclusions caught | 0 (document states none — no hallucination) |
| Scope gaps inferred | 7 |

Most significant catch: *gypsum board priced without finishing labor (taping/mudding/sanding)*; also missing *door hardware* and *firestopping at rated assemblies*.

## Real document #2 — general-contractor estimate (25 pp.)

Source: `https://federalestimating.com/wp-content/uploads/2025/12/general-contractor-sample.pdf`

| Metric | Result |
|---|---|
| Pages | 25 (≈274k chars) |
| Page-chunks | 7 |
| Line items | **959** across **16 CSI divisions** (Div 01 → Div 22) |
| Page citations | every line |

Demonstrates the page-chunking pipeline scaling to large multi-trade estimates
without JSON truncation.

## Notes

- Outputs are **proposals to be verified**, never final numbers.
- Free models work for these text tasks (see [FREE_MODELS.md](FREE_MODELS.md)); large/clear models improve recall on dense tables.
