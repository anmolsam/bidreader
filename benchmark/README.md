# BidReader benchmark

A reproducible, ground-truth benchmark for bid-document extraction.

## What it measures

| Metric | Definition |
|---|---|
| **Line-item recall** | fraction of ground-truth line items matched (amount within ±2% **and** description token-overlap ≥ 0.3) |
| **Exclusion-catch recall** | fraction of planted exclusions caught verbatim (incl. ones buried in prose) |
| **No-hallucination rate** | clean docs (zero real exclusions) must yield ≈zero invented exclusions |
| **Bid-total accuracy** | extracted grand total within ±2% of truth |
| **Arithmetic-error detection** | of intentionally-wrong line amounts, how many `math_check` flags as `mismatch` (and false positives on correct lines) |

## Why synthetic

The cases in [`cases.py`](cases.py) are **authored here**, so:
- ground truth is exact (we know every quantity, price, exclusion, and planted error);
- the PDFs are freely redistributable (no third-party copyright), so the benchmark is fully committed and reproducible by anyone.

**Caveat (honest):** synthetic documents are *cleaner* than real-world scans and crime-scene layouts. High scores here mean the engine is correct on well-structured input; they are an upper bound, not a claim about messy real bids. Real third-party document results (uncontrolled) are reported separately in [../docs/RESULTS.md](../docs/RESULTS.md).

## Cases

| id | tests |
|---|---|
| `drywall_quote` | line items + 3 fine-print exclusions |
| `gc_multitrade` | 8 divisions, multi-trade line items + qualifications |
| `quote_with_errors` | 2 **intentionally wrong** line amounts → arithmetic detection |
| `clean_no_exclusions` | zero exclusions → no-hallucination |
| `spec_prose_exclusions` | exclusions embedded in narrative prose ("by others") |

## Reproduce

```bash
pip install -e ".[dev]"
export GEMINI_API_KEY=...           # any supported key (see ../docs/FREE_MODELS.md)
python benchmark/generate.py        # writes docs/*.pdf + expected/*.json
python benchmark/run.py             # writes scorecard.json + SCORECARD.md
```

Latest committed results: [SCORECARD.md](SCORECARD.md).
