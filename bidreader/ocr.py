"""OCR for scanned / image-only PDFs.

Many real bids are scans with no text layer. This module rasterizes each page
with PyMuPDF and runs local Tesseract OCR to recover page-tagged text, which then
feeds the normal extraction pipeline. Fully local — keeps the privacy story
intact (no page images leave the machine).

Requires the `tesseract` binary (brew/apt install tesseract) and `pytesseract`
(`pip install "bidreader[ocr]"`).
"""
from __future__ import annotations
import fitz


def has_text_layer(doc, min_chars=40):
    return sum(len(p.get_text().strip()) for p in doc) >= min_chars


def ocr_pages(doc, dpi=300, lang="eng"):
    """Return page-tagged OCR text for an image-only PDF: '[PAGE n]\\n<text>'."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            "OCR needs extras: pip install \"bidreader[ocr]\"  (and the tesseract "
            "binary: `brew install tesseract` / `apt install tesseract-ocr`)."
        ) from e
    import io
    blocks = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang).strip()
        if text:
            blocks.append(f"[PAGE {i+1}]\n{text}")
    return blocks


def tesseract_available():
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
