# Evidence / demo pack

A larger, **messy**, fully-reproducible corpus to show what BidReader actually
does — and where it fails. All docs are authored here (exact ground truth,
freely redistributable; no third-party copyright).

- `make_corpus.py` — generates 14 varied bids → `corpus/*.pdf` + `expected/*.json`.
  Includes prose-buried exclusions, fine-print footnotes, two-column layouts,
  planted arithmetic errors, a multi-page bid, and 2 **scanned** image-only PDFs.
- `run_eval.py` — runs BidReader on all of them, scores vs ground truth (honestly,
  including misses), levels the electrical (4-sub) and drywall (3-sub) sets to
  Excel, and writes **`EVIDENCE.md`** + `leveling_*.xlsx` + sample input PNGs.

```bash
pip install -e ".[xlsx,ocr]"      # + tesseract binary for the scanned docs
export GEMINI_API_KEY=...          # any supported key (or BID_MODEL=ollama/...)
python demo/make_corpus.py
python demo/run_eval.py
```

See **[EVIDENCE.md](EVIDENCE.md)** for the latest committed results. Outputs are
proposals to verify, never final numbers; synthetic docs are an upper bound on
clean structure (real scans/handwriting will score lower).
