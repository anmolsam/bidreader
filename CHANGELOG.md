# Changelog

All notable changes to BidReader. Format: [Keep a Changelog](https://keepachangelog.com/);
versioning: [SemVer](https://semver.org/).

## [0.9.1] - 2026-06-17
### Changed
- Grand-total sum now extends `qty x unit_price` per line when an explicit `amount`
  is absent (unit-price schedules). NOTE: a real-doc test (`15_plumbing`) surfaced a
  separate limitation — on some layouts the LLM extracts line-item descriptions but
  not their dollar columns (unit_price/amount null), so there is nothing to sum; the
  total honestly stays null rather than being fabricated. Price-column extraction on
  varied layouts is the next real gap.

## [0.9.0] - 2026-06-17
### Added
- **Grand-total resolution + document cross-check.** When a doc prints no single
  grand total (line-item-only estimates), `bid_total` is now derived by summing the
  line items (`total_source="sum-of-line-items"`). When a printed total IS present,
  it's cross-checked against the sum (`total_reconciles`, `total_delta_pct`) — a
  document-level trust signal that catches missing/duplicate items. CLI surfaces both.
  Fixes the main real-world gap from the real-doc eval (4 docs returned null totals).

## [0.8.2] - 2026-06-17
### Fixed
- **Per-chunk JSON resilience** (found via a real-document eval where ~5/20 bids
  hard-failed): a truncated/malformed chunk no longer sinks the whole document.
  `read()` isolates each chunk (records `_chunks_failed`); `_clean()` is now a
  tolerant parser (strip fences → isolate object → repair trailing commas →
  `_balance_close` recovers complete items from a truncated chunk, dropping the
  partial one). Smaller chunks (24k) + higher output budget (32k) reduce
  truncation up front. Unit test covers truncated-JSON recovery.
### Added
- `demo/real_eval.py` + `demo/real/`: evaluate BidReader on REAL public bids,
  validating extracted total against each doc's own printed total (objective,
  no manual labeling). PDFs are cited by URL, not redistributed.

## [0.8.1] - 2026-06-17
### Fixed
- **MCP private mode**: MCP tools no longer require a cloud key — they accept any
  configured backend, including local Ollama (bids stay local over MCP too).
  Previously `_check_key()` rejected Ollama-only configs.
- README roadmap updated to reflect shipped features (leveling, local mode, OCR)
  instead of listing them as unchecked.

## [0.8.0] - 2026-06-17
### Added
- **Scanned-PDF OCR** (`bidreader/ocr.py`): scanned / image-only PDFs are
  auto-detected and OCR'd with local **Tesseract** (rasterize → OCR → existing
  pipeline), so scans no longer hard-fail. Fully local (page images never leave
  the machine). `read(path, ocr="auto"|"always"|"never")`; CLI `--ocr`; `[ocr]`
  extra (pytesseract + pillow; needs the `tesseract` binary). Result carries
  `_text_source` ("text-layer" | "ocr"). Verified end-to-end on an image-only quote.

## [0.7.0] - 2026-06-17
### Added
- **Local / private mode via Ollama** — run fully offline, no API key, bids never
  leave the machine. Enable with `BID_MODEL=ollama/<model>`, `BID_BACKEND=ollama`,
  or `OLLAMA_HOST=...` (incl. shared on-prem hosts). Closes the bid-confidentiality
  adoption blocker. Docs: `docs/LOCAL_MODELS.md`.
- Backend selection refactored into a testable `_select_backend()` (priority:
  Ollama > Requesty > OpenRouter > Google AI Studio) with offline tests proving
  the local path needs no key and targets `localhost:11434`.
### Changed
- HTTP calls go through `_post()` (plain http for local Ollama, certifi-verified
  https for cloud; 10-min timeout for slower local inference).

## [0.6.0] - 2026-06-17
### Added
- **Bid leveling → Excel** (`bidreader level q1.pdf q2.pdf … -o leveling.xlsx`):
  reads multiple subs and builds an apples-to-apples workbook — bidders as
  columns, a normalized **exclusion matrix** (which bidder excluded which scope,
  exposing the "low bid that carved out scope"), scope-gap matrix, lowest-bid
  marker, and per-bidder detail sheets with arithmetic flags. New `[xlsx]` extra
  (openpyxl) and `bidreader.leveling` module.
- **MCP tool `level_bids`** — agents can level competing bids and get the
  exclusion matrix as JSON.
- Offline test for the exclusion-clustering (synonymous phrasings collapse).
- `examples/make_leveling_sample.py` → 3 competing electrical subs + `leveling_demo.xlsx`.
### Addresses
- The #1 estimator-workflow gap from external review: output lands in Excel and
  supports side-by-side sub leveling (the bid-day workflow), not just one quote.

## [0.5.0] - 2026-06-17
### Added
- **Reproducible ground-truth benchmark** (`benchmark/`): 5 synthetic, freely-
  redistributable documents with committed expected outputs + a scorer
  (`generate.py`, `run.py`, `SCORECARD.md`). Measures line-item recall,
  exclusion-catch recall, no-hallucination rate, bid-total accuracy, and
  arithmetic-error detection. Current: 100% on all extraction metrics, 2/2
  planted arithmetic errors caught with 0 false positives (synthetic = upper bound).

## [0.4.0] - 2026-06-17
### Added
- **Verified evidence per line item**: `source_text` (exact printed line) so the
  page citation is real, not an LLM guess.
- **Arithmetic validation**: each line item gets `math_check` (`ok`/`mismatch`/`n/a`);
  `qty × unit_price` is checked against `amount` (2% / $1 tolerance) and mismatches
  are surfaced in the CLI. Non-LLM trust layer on top of extraction.
- Offline regression tests (`tests/test_offline.py`) wired into CI.
### Changed
- README citation claim corrected to match what the code actually returns
  (page + source_text + arithmetic check), after an external code review.

## [0.3.0] - 2026-06-17
### Added
- Documentation suite: `PAPER.md` (whitepaper), `docs/RESULTS.md`,
  `docs/FREE_MODELS.md`, `docs/MCP.md`, `CITATION.cff`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, GitHub CI workflow and issue templates.
- Worked `examples/` (synthetic sub-quote PDF + committed JSON/text output).
### Notes
- Verified on real third-party estimates: 72-item drywall bid ($324,240.61);
  959-item, 16-division, 25-page GC estimate.

## [0.2.1] - 2026-06-17
### Fixed
- **Large-document truncation.** Multi-page estimates (25+ pages / 900+ line
  items) overflowed the model's JSON output. Documents are now chunked by page
  and merged, scaling to arbitrarily large bids.

## [0.2.0] - 2026-06-17
### Added
- `bidreader-mcp` MCP server (`read_document`, `catch_exclusions`,
  `extract_line_items`) and `[mcp]` extra.

## [0.1.0] - 2026-06-17
### Added
- Initial release: `read()` → page-cited line items, exclusions, assumptions,
  alternates, scope gaps. CLI `bidreader <pdf>`. Provider-agnostic LLM backend
  (Requesty / OpenRouter / Google AI Studio). MIT.
