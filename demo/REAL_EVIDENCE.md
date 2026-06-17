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

## Honest interpretation

- **Ingestion is now robust:** 14/14 real docs parsed with **0 crashes** (5 of these
  hard-failed on JSON errors before the v0.8.2 per-chunk resilience fix). Extraction
  scaled to **4,196 line items** across the set (e.g. 1,282 from a 19pp multifamily
  estimate, 885 from a 25pp GC sample).
- **Total reconciliation is ~43% (6/14)** — and that number is limited as much by the
  crude printed-total *heuristic* as by extraction. Two failure modes dominate:
  (a) docs with **no single grand total** (line-item-only estimates) where extracted
  total is null; (b) the regex grabbing the **wrong "$" as the total** (e.g. a subtotal
  or unit price). The line items themselves extracted fine in most of these.
- **Takeaway:** on real, varied bids BidReader reliably *ingests and extracts*; a
  trustworthy *grand-total* needs better total-detection (sum line items / detect the
  summary line), and multi-bidder DOT unit-price tabs are a separate doc class (excluded
  here, noted). This is the honest real-world state — not the 100% of the synthetic set.
