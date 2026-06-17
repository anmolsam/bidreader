"""Offline regression tests (no network / no LLM). Run: pytest -q"""
from bidreader.extract import _chunk, _merge, validate


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
