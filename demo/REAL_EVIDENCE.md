# BidReader — Real-document evaluation

BidReader run on **14 real, publicly-published, estimate-class** construction PDFs
(estimating-firm samples, GC estimates, schedules of values). The PDFs are **not
redistributed** (copyright) — each row cites its source URL; re-download to verify.

> Scope note: this covers **estimate-class** docs. 6 large multi-bidder government
> DOT unit-price *bid-tabulation* PDFs (110–121 pp) are a **separate document class**
> and were excluded — a full-20 live run is LLM-throughput-bound and did not complete.
> Claims here are about estimate-class bids, not all construction bid documents.

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

## Failure audit (machine-derived from real_eval.json)

Categories below are computed deterministically by `demo/audit.py` from the committed `real_eval.json` — not hand-asserted. Reproduce: `python demo/audit.py`.

| category | count |
|---|---|
| reconciled | 6 |
| no grand-total emitted (items extracted, no total line) | 4 |
| evaluator: printed-total heuristic likely wrong | 2 |
| TRUE product total mismatch | 1 |
| N/A (no pricing extracted) | 1 |

| doc | extracted total | printed total | category |
|---|---|---|---|
| Sample-General-Construction-Estima | $17,494,401 | $17,494,401 | reconciled |
| residential-estimate-sample-additi | $305,374 | $305,374 | reconciled |
| general-contractor-sample.pdf | $0 | $961 | no grand-total emitted (items extracted, no total line) |
| Sixth-Story-Multi-Family-Building- | $6,502,553 | $6,502,553 | reconciled |
| Sitework-estimate-sample-veracity- | $453,765 | $453,765 | reconciled |
| Bids-Estimating-Special-Contructio | $426,166 | $477,050 | TRUE product total mismatch |
| 6.-MEP-Format.pdf | $0 | $26,000 | no grand-total emitted (items extracted, no total line) |
| 7.-Plumbing-Format.pdf | $0 | $22,000 | no grand-total emitted (items extracted, no total line) |
| Estimate-For-901-RENALDI-PLAN1.pdf | $102,576 | $29,219 | evaluator: printed-total heuristic likely wrong |
| schedule-of-values-sample-sov-on-a | $85,000 | $85,000 | reconciled |
| 01_29_73_schedule_of_values_2018-0 | — | — | N/A (no pricing extracted) |
| BID-ARCON-Phase-2-BID_Tabulations_ | — | — | no grand-total emitted (items extracted, no total line) |
| Residential-Sample-01.pdf | $2,118,924 | $2,118,924 | reconciled |
| 1022-03.pdf | $51,513 | $19,221 | evaluator: printed-total heuristic likely wrong |
