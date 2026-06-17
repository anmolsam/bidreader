# Changelog

All notable changes to BidReader. Format: [Keep a Changelog](https://keepachangelog.com/);
versioning: [SemVer](https://semver.org/).

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
