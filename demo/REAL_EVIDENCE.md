# BidReader — Real-document evaluation

BidReader run on **20 real, publicly-published** construction bid/estimate PDFs (estimating-firm samples, government bid docs). The PDFs are **not redistributed** (copyright) — each row cites its source URL; re-download to verify.

**Objective check:** does BidReader's extracted grand total reconcile (±2%) with the total the document itself prints? That ground truth lives in each doc, so no manual labeling is needed. (Full line-item/exclusion ground truth would need an estimator; this measures real-world total-reconciliation + ingestion robustness.)

## Aggregate

| metric | result |
|---|---|
| Real documents | 20 (7 parsed, 13 failed) |
| Total reconciles with printed total (±2%) | **1/7** |
| Scanned docs OCR'd & parsed | 0 |
| Total line items extracted | 268 |

## Per document

| source | pages | input | line items | excl | extracted total | printed total | match |
|---|---|---|---|---|---|---|---|
| https://www.buckleypc.com/wp-content/uploads/Sampl | — | — | — | — | — | — | ❌ JSONDecodeError: Unterminated  |
| https://constructiontakeoffservices.com/wp-content | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting pro |
| https://federalestimating.com/wp-content/uploads/2 | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting val |
| https://veracityestimating.com/wp-content/uploads/ | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting ',' |
| https://constructiontakeoffservices.com/wp-content | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting pro |
| https://bidsestimating.com/wp-content/uploads/2025 | — | — | — | — | — | — | ❌ JSONDecodeError: Unterminated  |
| https://wsdot.wa.gov/sites/default/files/2026-05/C | 9 | text | 60 | 0 | $9,743,128 | $11,208,632 | ⚠ |
| https://transportation.ky.gov/Construction-Procure | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting ',' |
| https://dgs.dc.gov/sites/default/files/dc/sites/dg | 1 | text | 12 | 0 | — | $605,000 | ⚠ |
| https://biddingestimating.com/storage/2022/05/6.-M | — | — | — | — | — | — | ❌ JSONDecodeError: Unterminated  |
| https://biddingestimating.com/storage/2022/05/7.-P | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting ',' |
| https://theaceservices.com/wp-content/uploads/2025 | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting ',' |
| https://www.ganarpro.com/wp-content/uploads/2024/0 | 3 | text | 52 | 1 | $85,000 | $85,000 | ✅ |
| https://www.wolgast.com/hubfs/Bid%20Tab%20for%20Pu | 3 | text | 84 | 0 | $4,013,405 | $969,992 | ⚠ |
| https://www.etsu.edu/facilities/documents/01_29_73 | 1 | text | 0 | 0 | — | — | ⚠ |
| https://resources.finalsite.net/images/v1704212336 | — | — | — | — | — | — | ❌ JSONDecodeError: Expecting val |
| https://www.nj.gov/transportation/contribute/busin | — | — | — | — | — | — | ❌ JSONDecodeError: Unterminated  |
| https://www.cuanschutz.edu/docs/librariesprovider2 | 1 | text | 4 | 0 | — | $196,500 | ⚠ |
| https://estimations.us/wp-content/uploads/2026/01/ | — | — | — | — | — | — | ❌ JSONDecodeError: Unterminated  |
| https://theaceservices.com/wp-content/uploads/2025 | 5 | text | 56 | 0 | $51,513 | $19,221 | ⚠ |

_Real third-party documents (cited, not redistributed). Printed-total reconciliation is an objective real-world signal; it is not a substitute for estimator-labeled line-item ground truth. Outputs are proposals to verify._
