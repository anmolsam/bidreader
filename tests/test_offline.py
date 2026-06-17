"""Offline regression tests (no network / no LLM). Run: pytest -q"""
import os
import bidreader.extract as ex
from bidreader.extract import _chunk, _merge, validate


def _backend(monkeyenv):
    """Helper: set env (clearing LLM vars first) and return the selected backend."""
    for k in ("BID_BACKEND", "OLLAMA_HOST", "OLLAMA_MODEL", "REQUESTY_API_KEY",
              "OPENROUTER_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        os.environ.pop(k, None)
    os.environ.update(monkeyenv)
    return ex._select_backend()


def test_ollama_backend_needs_no_key_and_is_local():
    orig_model = ex.MODEL
    try:
        ex.MODEL = "ollama/llama3.1"
        be = _backend({})
        assert be["name"] == "ollama" and be["local"] is True
        assert be["url"] == "http://localhost:11434/v1/chat/completions"
        assert be["model"] == "llama3.1"
        assert "Authorization" not in be["headers"]   # no key, bids stay local
    finally:
        ex.MODEL = orig_model


def test_ollama_via_env_flag_and_custom_host():
    orig_model = ex.MODEL
    try:
        ex.MODEL = "google/gemini-2.5-flash"   # default cloud model present
        be = _backend({"BID_BACKEND": "ollama", "OLLAMA_HOST": "http://box:11434",
                       "OLLAMA_MODEL": "qwen2.5"})
        assert be["url"] == "http://box:11434/v1/chat/completions"
        assert be["model"] == "qwen2.5" and be["local"] is True
    finally:
        ex.MODEL = orig_model


def test_cloud_backend_selection_priority():
    be = _backend({"REQUESTY_API_KEY": "x", "OPENROUTER_API_KEY": "y"})
    assert be["name"] == "requesty" and be["local"] is False
    assert be["headers"]["Authorization"].startswith("Bearer ")


def test_chunk_respects_budget_and_keeps_all_pages():
    blocks = [f"[PAGE {i}]\n" + "x" * 20000 for i in range(1, 6)]
    chunks = _chunk(blocks, budget=42000)
    assert len(chunks) >= 2
    joined = "\n\n".join(chunks)
    for i in range(1, 6):
        assert f"[PAGE {i}]" in joined  # no page dropped


def test_merge_concats_and_picks_grand_total():
    a = {"line_items": [{"description": "a"}], "bid_total": 100,
         "scope_gaps": [{"missing": "X", "why": "1"}], "vendor": "Acme"}
    b = {"line_items": [{"description": "b"}], "bid_total": 250,
         "scope_gaps": [{"missing": "x", "why": "dup"}, {"missing": "Y", "why": "2"}]}
    m = _merge([a, b])
    assert len(m["line_items"]) == 2
    assert m["bid_total"] == 250                 # grand total = max
    assert len(m["scope_gaps"]) == 2             # 'X' and 'x' dedupe
    assert m["vendor"] == "Acme"


def test_leveling_clusters_synonymous_exclusions():
    from bidreader.leveling import _cluster
    recs = [
        {"bidder": 0, "item": "Fire alarm system and devices excluded"},
        {"bidder": 2, "item": "Fire alarm EXCLUDED"},
        {"bidder": 1, "item": "Equipment and housekeeping pads excluded"},
    ]
    clusters = _cluster(recs, "item")
    # the two fire-alarm phrasings collapse into one row covering bidders 0 and 2
    fa = [c for c in clusters if "alarm" in c["label"].lower()]
    assert len(fa) == 1
    assert set(fa[0]["members"].keys()) == {0, 2}
    # the pads exclusion stays its own row
    assert any("pads" in c["label"].lower() for c in clusters)


def test_validate_flags_bad_arithmetic():
    data = {"line_items": [
        {"qty": 10, "unit_price": 2.0, "amount": 20.0},   # ok
        {"qty": 10, "unit_price": 2.0, "amount": 25.0},   # mismatch
        {"qty": None, "unit_price": 2.0, "amount": 20.0}, # n/a
    ]}
    out = validate(data)
    checks = [li["math_check"] for li in out["line_items"]]
    assert checks == ["ok", "mismatch", "n/a"]
    assert out["math_flagged"] == 1
    assert out["line_items"][1]["math_expected"] == 20.0
