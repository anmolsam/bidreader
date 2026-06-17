"""
BidReader — read messy construction documents (sub-quotes, bid packages, spec
sections, schedules) into clean structured data, and CATCH the scope gaps /
exclusions vendors bury. Every value cites its page + the exact source text.

The valued, repeated estimator pain (r/Construction, 498 upvotes): not the
takeoff — it's wrangling "crime-scene formatting" PDFs into clean tables and
finding the one line where a sub quietly excluded something in size-8 font.

LLM-native (works today). Provider-agnostic key from env: REQUESTY / OPENROUTER
/ GEMINI. MIT.
"""
from __future__ import annotations
import os, re, json, ssl, urllib.request, certifi
import fitz

SSLCTX = ssl.create_default_context(cafile=certifi.where())
MODEL = os.environ.get("BID_MODEL", "google/gemini-2.5-flash")

SCHEMA_PROMPT = """You are a construction estimating assistant reading a vendor/subcontractor document
(quote, bid, proposal, spec section, or schedule). Read the TEXT (page-tagged) and return STRICT JSON only:
{
 "doc_type": "<sub-quote|bid package|spec section|schedule|invoice|other>",
 "vendor": "<company or null>", "project": "<project/title or null>",
 "trade": "<trade e.g. Drywall, Electrical or null>", "currency": "<e.g. USD or null>",
 "bid_total": <number or null>,
 "line_items": [{"section":"<csi/section or null>","description":"<text>","qty":<num|null>,"unit":"<EA/SF/LF/LS|null>","unit_price":<num|null>,"amount":<num|null>,"page":<int>,"source_text":"<the EXACT line as printed in the document>"}],
 "exclusions": [{"item":"<short label>","quote":"<EXACT text as written>","page":<int>,"risk":"<one line: why this matters / who eats the cost>"}],
 "assumptions": [{"text":"<exact>","page":<int>}],
 "alternates": [{"text":"<exact>","amount":<num|null>,"page":<int>}],
 "scope_gaps": [{"missing":"<scope likely NOT covered>","why":"<why an estimator should confirm>"}],
 "notes": "<one line on confidence/legibility>"
}
Rules: exclusions are CRITICAL — hunt everywhere, including fine print, footnotes, "by others", "not included",
"excludes", "assumes", "clarifications". Quote them verbatim with the page. Do not invent values; use null if unsure.
For scope_gaps, infer trade-standard scope a vendor commonly omits that is NOT mentioned in this doc."""


def _page_blocks(doc):
    out = []
    for i, p in enumerate(doc):
        t = p.get_text().strip()
        if t:
            out.append(f"[PAGE {i+1}]\n{t}")
    return out


def _chunk(blocks, budget=24000):
    """Group page-blocks into chunks under a char budget so the model's JSON
    output never overflows on large multi-page estimates."""
    chunks, cur, n = [], [], 0
    for b in blocks:
        if cur and n + len(b) > budget:
            chunks.append("\n\n".join(cur)); cur, n = [], 0
        cur.append(b); n += len(b)
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


def _select_backend():
    """Pick the LLM backend from the environment (testable, no network).

    Priority: explicit Ollama (local, no key, bids never leave the machine) >
    Requesty > OpenRouter > Google AI Studio. Returns a dict describing the call.
    """
    model = MODEL
    ollama_host = os.environ.get("OLLAMA_HOST")
    want_ollama = (os.environ.get("BID_BACKEND") == "ollama" or bool(ollama_host)
                   or model.startswith("ollama/"))
    if want_ollama:
        host = (ollama_host or "http://localhost:11434").rstrip("/")
        if model.startswith("ollama/"):
            m = model.split("/", 1)[1]
        elif model and "/" not in model:
            m = model
        else:
            m = os.environ.get("OLLAMA_MODEL", "llama3.1")
        return {"name": "ollama", "url": host + "/v1/chat/completions",
                "headers": {"Content-Type": "application/json"}, "model": m,
                "style": "openai", "local": True}
    rq = os.environ.get("REQUESTY_API_KEY"); ork = os.environ.get("OPENROUTER_API_KEY")
    gk = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if rq:
        return {"name": "requesty", "url": "https://router.requesty.ai/v1/chat/completions",
                "headers": {"Authorization": f"Bearer {rq}", "Content-Type": "application/json"},
                "model": model, "style": "openai", "local": False}
    if ork:
        return {"name": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions",
                "headers": {"Authorization": f"Bearer {ork}", "Content-Type": "application/json"},
                "model": model, "style": "openai", "local": False}
    if gk:
        m = model.split("/")[-1]
        return {"name": "aistudio", "model": m, "style": "gemini", "local": False,
                "url": f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gk}",
                "headers": {"Content-Type": "application/json"}}
    raise RuntimeError("No LLM backend: run Ollama locally (BID_BACKEND=ollama or "
                       "BID_MODEL=ollama/llama3.1) or set REQUESTY_API_KEY / "
                       "OPENROUTER_API_KEY / GEMINI_API_KEY.")


def _post(url, headers, body, local):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    # local Ollama is plain http; cloud is https → verify with certifi
    ctx = None if local or url.startswith("http://") else SSLCTX
    timeout = 600 if local else 180   # local CPU inference can be slow
    return json.load(urllib.request.urlopen(req, timeout=timeout, context=ctx))


def _llm(text):
    user = SCHEMA_PROMPT + "\n\n=== DOCUMENT TEXT ===\n" + text[:120000]
    be = _select_backend()
    if be["style"] == "gemini":
        body = {"contents": [{"parts": [{"text": user}]}],
                "generationConfig": {"response_mime_type": "application/json", "temperature": 0}}
        r = _post(be["url"], be["headers"], body, be["local"])
        return _clean(r["candidates"][0]["content"]["parts"][0]["text"])
    body = {"model": be["model"], "temperature": 0,
            "messages": [{"role": "user", "content": user}],
            "response_format": {"type": "json_object"}}
    if not be["local"]:
        body["max_tokens"] = 32000          # cloud honors this; Ollama uses num_predict
    r = _post(be["url"], be["headers"], body, be["local"])
    return _clean(r["choices"][0]["message"]["content"])


def _balance_close(s):
    """Best-effort repair of a TRUNCATED JSON object: close an open string, drop a
    trailing incomplete token, and append the closers for any still-open brackets.
    Recovers the complete items from a chunk whose JSON got cut mid-array."""
    stack, in_str, esc = [], False, False
    for ch in s:
        if esc:
            esc = False; continue
        if ch == "\\" and in_str:
            esc = True; continue
        if ch == '"':
            in_str = not in_str; continue
        if in_str:
            continue
        if ch in "{[":
            stack.append(ch)
        elif ch in "}]" and stack:
            stack.pop()
    res = s + ('"' if in_str else "")
    # strip a dangling partial token:  trailing comma / "key": / "key"
    res = re.sub(r'(,\s*"[^"]*"\s*:?\s*[^,}\]]*)$', "", res)
    res = re.sub(r'[,:]\s*$', "", res)
    for ch in reversed(stack):
        res += "}" if ch == "{" else "]"
    return res


def _clean(s):
    """Tolerant JSON parse: strip fences, isolate the object, repair trailing commas
    and truncation. Raises ValueError only if nothing parseable can be recovered."""
    s = s.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    i, j = s.find("{"), s.rfind("}")
    if i != -1 and j != -1 and j > i:
        s = s[i:j + 1]
    for cand in (s,
                 re.sub(r",(\s*[}\]])", r"\1", s),       # trailing commas
                 _balance_close(s)):                      # truncated → close & drop partial
        try:
            return json.loads(cand)
        except Exception:
            continue
    raise ValueError("unparseable JSON from model")


def validate(data):
    """Attach an objective arithmetic check to each line item:
    'ok' if qty*unit_price ≈ amount, 'mismatch' if not, 'n/a' if missing inputs.
    This is non-LLM verification — the trust layer on top of extraction."""
    flagged = 0
    for li in data.get("line_items", []):
        q, up, amt = li.get("qty"), li.get("unit_price"), li.get("amount")
        if isinstance(q, (int, float)) and isinstance(up, (int, float)) and isinstance(amt, (int, float)):
            expect = q * up
            tol = max(1.0, abs(amt) * 0.02)  # 2% or $1
            if abs(expect - amt) <= tol:
                li["math_check"] = "ok"
            else:
                li["math_check"] = "mismatch"; li["math_expected"] = round(expect, 2); flagged += 1
        else:
            li["math_check"] = "n/a"
    data["math_flagged"] = flagged

    # ── grand-total resolution + document-level cross-check ──────────────────
    amts = [li["amount"] for li in data.get("line_items", []) if isinstance(li.get("amount"), (int, float))]
    computed = round(sum(amts), 2) if amts else None
    data["computed_total"] = computed          # sum of extracted line items
    printed = data.get("bid_total")
    if isinstance(printed, (int, float)) and printed:
        data["total_source"] = "printed"
        if computed:
            delta = abs(printed - computed) / abs(printed)
            data["total_reconciles"] = delta <= 0.03
            data["total_delta_pct"] = round(delta * 100, 1)
    elif computed:
        data["bid_total"] = computed           # no printed grand total → sum the items
        data["total_source"] = "sum-of-line-items"
        data["total_reconciles"] = None
    else:
        data["total_source"] = None
    return data


class Doc(dict):
    """Result with convenience accessors."""
    @property
    def line_items(self): return self.get("line_items", [])
    @property
    def exclusions(self): return self.get("exclusions", [])
    @property
    def scope_gaps(self): return self.get("scope_gaps", [])
    def to_json(self, **kw): return json.dumps(self, indent=2, **kw)


def _merge(parts):
    out = {"doc_type": None, "vendor": None, "project": None, "trade": None,
           "currency": None, "bid_total": None, "line_items": [], "exclusions": [],
           "assumptions": [], "alternates": [], "scope_gaps": [], "notes": None}
    seen_gap = set()
    totals = []
    for d in parts:
        for k in ("doc_type", "vendor", "project", "trade", "currency", "notes"):
            if not out[k] and d.get(k):
                out[k] = d[k]
        if isinstance(d.get("bid_total"), (int, float)):
            totals.append(d["bid_total"])
        for k in ("line_items", "exclusions", "assumptions", "alternates"):
            out[k].extend(d.get(k) or [])
        for g in d.get("scope_gaps") or []:
            key = (g.get("missing") or "").strip().lower()
            if key and key not in seen_gap:
                seen_gap.add(key); out["scope_gaps"].append(g)
    out["bid_total"] = max(totals) if totals else None   # grand total > subtotals
    return out


def read(path: str, ocr: str = "auto") -> Doc:
    """Read a construction PDF into structured, page-cited data.

    Large multi-page estimates are chunked by page and merged, so the model's
    JSON output never truncates.

    ocr: "auto" (default) runs local Tesseract OCR when the PDF has no text layer
    (scanned); "always" forces OCR; "never" disables it (raises on scanned input).
    """
    from . import ocr as _ocr
    doc = fitz.open(path)
    blocks = _page_blocks(doc)
    source = "text-layer"
    scanned = sum(len(b) for b in blocks) < 40
    if (ocr == "always") or (scanned and ocr == "auto"):
        if ocr != "always" and not _ocr.tesseract_available():
            raise RuntimeError(
                "Scanned PDF (no text layer) and OCR is unavailable. Install OCR: "
                "pip install \"bidreader[ocr]\" + the tesseract binary "
                "(`brew install tesseract` / `apt install tesseract-ocr`), or pass ocr='never'.")
        blocks = _ocr.ocr_pages(doc)
        source = "ocr"
    if sum(len(b) for b in blocks) < 40:
        raise RuntimeError("No extractable text (even after OCR). Is the PDF blank or unreadable?")
    chunks = _chunk(blocks)
    parts, failed = [], 0
    for c in chunks:
        try:
            parts.append(_llm(c))          # tolerant JSON parse inside _clean
        except Exception:
            failed += 1                    # one bad chunk must not sink the whole doc
    if not parts:
        raise RuntimeError(f"All {len(chunks)} chunk(s) failed to parse — model output unusable.")
    data = validate(_merge(parts))
    data["_source"] = path.split("/")[-1]
    data["_pages"] = doc.page_count
    data["_chunks"] = len(chunks)
    data["_chunks_failed"] = failed
    data["_text_source"] = source
    return Doc(data)
