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
import os, json, ssl, urllib.request, certifi
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
 "line_items": [{"section":"<csi/section or null>","description":"<text>","qty":<num|null>,"unit":"<EA/SF/LF/LS|null>","unit_price":<num|null>,"amount":<num|null>,"page":<int>}],
 "exclusions": [{"item":"<short label>","quote":"<EXACT text as written>","page":<int>,"risk":"<one line: why this matters / who eats the cost>"}],
 "assumptions": [{"text":"<exact>","page":<int>}],
 "alternates": [{"text":"<exact>","amount":<num|null>,"page":<int>}],
 "scope_gaps": [{"missing":"<scope likely NOT covered>","why":"<why an estimator should confirm>"}],
 "notes": "<one line on confidence/legibility>"
}
Rules: exclusions are CRITICAL — hunt everywhere, including fine print, footnotes, "by others", "not included",
"excludes", "assumes", "clarifications". Quote them verbatim with the page. Do not invent values; use null if unsure.
For scope_gaps, infer trade-standard scope a vendor commonly omits that is NOT mentioned in this doc."""


def _page_text(doc):
    parts = []
    for i, p in enumerate(doc):
        t = p.get_text().strip()
        if t:
            parts.append(f"[PAGE {i+1}]\n{t}")
    return "\n\n".join(parts)


def _llm(text):
    rq = os.environ.get("REQUESTY_API_KEY"); ork = os.environ.get("OPENROUTER_API_KEY")
    gk = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    user = SCHEMA_PROMPT + "\n\n=== DOCUMENT TEXT ===\n" + text[:120000]
    if rq: base, key = "https://router.requesty.ai/v1/chat/completions", rq
    elif ork: base, key = "https://openrouter.ai/api/v1/chat/completions", ork
    elif gk:
        m = MODEL.split("/")[-1]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gk}"
        body = {"contents":[{"parts":[{"text":user}]}],
                "generationConfig":{"response_mime_type":"application/json","temperature":0}}
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=180, context=SSLCTX))
        return _clean(r["candidates"][0]["content"]["parts"][0]["text"])
    else:
        raise RuntimeError("Set REQUESTY_API_KEY / OPENROUTER_API_KEY / GEMINI_API_KEY")
    body = {"model": MODEL, "temperature": 0, "max_tokens": 16000, "reasoning_effort": "low",
            "messages": [{"role": "user", "content": user}]}
    req = urllib.request.Request(base, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=180, context=SSLCTX))
    return _clean(r["choices"][0]["message"]["content"])


def _clean(s):
    s = s.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(s)


class Doc(dict):
    """Result with convenience accessors."""
    @property
    def line_items(self): return self.get("line_items", [])
    @property
    def exclusions(self): return self.get("exclusions", [])
    @property
    def scope_gaps(self): return self.get("scope_gaps", [])
    def to_json(self, **kw): return json.dumps(self, indent=2, **kw)


def read(path: str) -> Doc:
    """Read a construction PDF into structured, page-cited data."""
    doc = fitz.open(path)
    text = _page_text(doc)
    if len(text) < 40:
        raise RuntimeError("No extractable text (scanned PDF) — vision OCR path TODO.")
    data = _llm(text)
    data["_source"] = path.split("/")[-1]
    data["_pages"] = doc.page_count
    return Doc(data)
