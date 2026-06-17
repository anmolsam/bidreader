# Contributing to BidReader

Thanks for helping build the open primitive for construction document intelligence.

## Dev setup

```bash
git clone https://github.com/anmolsam/bidreader && cd bidreader
python -m venv .venv && source .venv/bin/activate
pip install -e ".[mcp,tables]"
export GEMINI_API_KEY=...          # any supported key (see docs/FREE_MODELS.md)
python make_sample.py
bidreader examples/sample_quote.pdf
```

## Good first issues

- **Notation packs** — region/trade parsers (AISC `W12x65`, BS/IS `UC305x305x158`, AUS `310UB40.4`).
- **Export formats** — Excel/CSV writers in `bidreader/` (mirror the `Doc` shape).
- **Test fixtures** — add a small, **synthetic** (self-authored) document + expected JSON. Do **not** commit third-party/copyrighted PDFs.
- **Scanned-PDF OCR path** — vision fallback when `read()` finds no text layer.

## Guidelines

- Keep the core dependency-light (PyMuPDF + stdlib). Heavy/optional deps go behind extras.
- Every extracted value should keep its **page citation** — that's the product's trust contract.
- Outputs are *proposals to be verified* — don't add logic that hides uncertainty.
- Match the existing code style; no large unrelated refactors in a feature PR.

## PRs

Small, focused PRs with a one-line CHANGELOG entry. Run the sample end-to-end before submitting.

## Releasing (maintainers)

1. Bump the version in `pyproject.toml`, `bidreader/__init__.py`, and `CITATION.cff` (must match), add a `CHANGELOG.md` entry.
2. Create a **project-scoped** PyPI token (pypi.org → tokens) and export it — never paste it inline:
   ```bash
   export PYPI_TOKEN=pypi-...
   ./release.sh --dry-run     # build + tests + checks, no upload
   ./release.sh               # publishes the current version
   git tag v$(grep -E '^version' pyproject.toml | sed -E 's/.*"(.*)".*/\1/') && git push --tags
   ```
`release.sh` verifies version consistency, refuses to re-publish an existing version, runs tests, and reads the token from `$PYPI_TOKEN` only.
