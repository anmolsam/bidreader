# Changelog

All notable changes to BidReader. Format: [Keep a Changelog](https://keepachangelog.com/);
versioning: [SemVer](https://semver.org/).

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
