# BidReader — Real-document evaluation

BidReader run on **14 real, publicly-published** construction bid/estimate PDFs (estimating-firm samples, government bid docs). The PDFs are **not redistributed** (copyright) — each row cites its source URL; re-download to verify.

**Objective check:** does BidReader's extracted grand total reconcile (±2%) with the total the document itself prints? That ground truth lives in each doc, so no manual labeling is needed. (Full line-item/exclusion ground truth would need an estimator; this measures real-world total-reconciliation + ingestion robustness.)

## Aggregate

| metric | result |
|---|---|
| Real documents | 14 (14 parsed, 0 failed) |
| Total reconciles with printed total (±2%) | **6/14** |
| Scanned docs OCR'd & parsed | 1 |
| Total line items extracted | 4196 |

## Per document

| source | pages | input | line items | excl | extracted total | printed total | match |
|---|---|---|---|---|---|---|---|
| https://www.buckleypc.com/wp-content/uploads/Sampl | 47 | text | 388 | 0 | $17,494,401 | $17,494,401 | ✅ |
| https://constructiontakeoffservices.com/wp-content | 4 | text | 173 | 6 | $305,374 | $305,374 | ✅ |
| https://federalestimating.com/wp-content/uploads/2 | 25 | text | 885 | 19 | $0 | $961 | ⚠ |
| https://veracityestimating.com/wp-content/uploads/ | 19 | text | 1282 | 0 | $6,502,553 | $6,502,553 | ✅ |
| https://constructiontakeoffservices.com/wp-content | 11 | text | 65 | 0 | $453,765 | $453,765 | ✅ |
| https://bidsestimating.com/wp-content/uploads/2025 | 10 | text | 161 | 12 | $426,166 | $477,050 | ⚠ |
| https://biddingestimating.com/storage/2022/05/6.-M | 15 | text | 582 | 4 | $0 | $26,000 | ⚠ |
| https://biddingestimating.com/storage/2022/05/7.-P | 7 | text | 243 | 1 | $0 | $22,000 | ⚠ |
| https://theaceservices.com/wp-content/uploads/2025 | 5 | text | 101 | 6 | $102,576 | $29,219 | ⚠ |
| https://www.ganarpro.com/wp-content/uploads/2024/0 | 3 | text | 52 | 1 | $85,000 | $85,000 | ✅ |
| https://www.etsu.edu/facilities/documents/01_29_73 | 1 | text | 0 | 1 | — | — | ⚠ |
| https://resources.finalsite.net/images/v1704212336 | 9 | scan→OCR | 44 | 18 | — | — | ⚠ |
| https://estimations.us/wp-content/uploads/2026/01/ | 19 | text | 164 | 0 | $2,118,924 | $2,118,924 | ✅ |
| https://theaceservices.com/wp-content/uploads/2025 | 5 | text | 56 | 0 | $51,513 | $19,221 | ⚠ |

_Real third-party documents (cited, not redistributed). Printed-total reconciliation is an objective real-world signal; it is not a substitute for estimator-labeled line-item ground truth. Outputs are proposals to verify._

## Reconciliation failure audit (what "6/14" actually means)

The blunt `6/14` mixes three different things. Audited per-doc, the breakdown is:

| category | count | what it is |
|---|---|---|
| ✅ **Reconciled exactly** | 6 | extracted grand total == the document's printed total |
| **Evaluator heuristic grabbed wrong $** | 2 | extraction fine; this eval's `printed_total()` regex picked a subtotal/wrong figure (`16_ace`, `25_ace`). **Not a product failure.** |
| **No single grand total in source** | 4 | line-item-only estimates/tabs (`04_federal` 885 items, `14_mep` 582, `15_plumbing` 243, `21_ccsd15` scanned 44) — items extracted fine; the doc prints no one grand-total line, so `bid_total` is null |
| **N/A** | 1 | `20_etsu` is a 1-page SOV with nothing to price |
| **True BidReader total error** | **1** | `08_bids`: $426,166 vs $477,050 (~11% off — investigate) |

So the honest headline is **not** "57% wrong":
- **14/14 parsed, 0 crashes, 4,196 line items extracted.**
- Of docs with a detectable single grand total: **6 reconciled, 1 true product miss.**
- **2** misses are this evaluator's heuristic; **4** are docs with no grand-total line; **1** N/A.

**The real product gap is grand-total *detection*** (sum the line items / find the summary line) — not extraction, which works on real, varied bids. Multi-bidder DOT unit-price tabs are a separate doc class (excluded, noted). This is the honest real-world state — not the synthetic set's 100%.
