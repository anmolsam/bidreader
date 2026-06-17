# Benchmark scorecard

BidReader scored against 5 synthetic ground-truth documents (authored here, so truth is exact and PDFs are freely redistributable).
Reproduce: `python benchmark/generate.py && python benchmark/run.py`.

## Aggregate

| metric | score |
|---|---|
| Line-item recall | **100%** |
| Exclusion-catch recall | **100%** |
| No-hallucination rate (clean docs) | **100%** |
| Bid-total accuracy (±2%) | **100%** |
| Arithmetic errors planted / caught | **2/2** (false positives: 0) |

## Per case

| case | line items | exclusions | no-halluc | total ✓ | math caught |
|---|---|---|---|---|---|
| `clean_no_exclusions` | 3/3 (100%) | 0/0 | ✅ | ✅ | — |
| `drywall_quote` | 5/5 (100%) | 3/3 | ✅ | ✅ | — |
| `gc_multitrade` | 8/8 (100%) | 2/2 | ✅ | ✅ | — |
| `quote_with_errors` | 4/4 (100%) | 2/2 | ✅ | ✅ | 2/2 |
| `spec_prose_exclusions` | 3/3 (100%) | 3/3 | ✅ | ✅ | — |

_Synthetic benchmark; results vary slightly by model. Run with `BID_MODEL` of your choice._
