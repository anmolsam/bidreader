"""Render each benchmark case to a PDF and write the committed expected JSON."""
import os, json
import fitz
from cases import CASES

HERE = os.path.dirname(__file__)
DOCS = os.path.join(HERE, "docs"); EXP = os.path.join(HERE, "expected")
os.makedirs(DOCS, exist_ok=True); os.makedirs(EXP, exist_ok=True)

NOTES = {
    "drywall_quote": [
        "Clarifications & Exclusions:",
        "1. Pricing assumes building dried-in prior to board installation.",
        "2. This proposal EXCLUDES fire-stopping at rated assemblies, scaffolding over 10',",
        "   and removal/haul-off of construction debris (by others).",
    ],
    "gc_multitrade": [
        "Qualifications:",
        "1. Excludes abatement or handling of any hazardous material (asbestos, lead).",
        "2. Building permit and plan-check fees by Owner; not included in this bid.",
    ],
    "quote_with_errors": [
        "Notes:",
        "1. Fire alarm system and devices are EXCLUDED (by others).",
        "2. Low voltage / data cabling not included in this proposal.",
    ],
    "clean_no_exclusions": [
        "Notes: All surfaces prepped per manufacturer spec. Pricing valid 30 days.",
    ],
    "spec_prose_exclusions": [
        "General: The roofing subcontractor shall furnish and install the membrane",
        "assembly described above. Wood blocking and nailers at perimeters are to be",
        "provided by others under the carpentry scope. Any structural deck repair",
        "discovered during tear-off is excluded and will be handled by change order.",
        "Interior finishes affected by leaks are not part of this scope.",
    ],
}


def render(case):
    doc = fitz.open(); pg = doc.new_page(width=612, height=792)
    def t(x, y, s, sz=9, c=(0, 0, 0)): pg.insert_text((x, y), s, fontsize=sz, color=c)
    t(40, 50, case["vendor"], 14)
    t(40, 66, f'{case["doc_type"].upper()}  —  Trade: {case["trade"]}', 9)
    t(40, 80, "Project: Riverside Commercial Build-Out", 8)
    y = 110
    t(40, y, "CSI"); t(95, y, "Description"); t(360, y, "Qty"); t(405, y, "Unit"); t(440, y, "Unit$"); t(515, y, "Amount")
    y += 6; pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 14
    total = 0.0
    for sec, desc, qty, unit, up, amt in case["line_items"]:
        t(40, y, sec, 7); t(95, y, desc[:48], 7); t(360, y, f"{qty:,}", 7)
        t(405, y, unit, 7); t(440, y, f"{up:,.2f}", 7); t(515, y, f"{amt:,.2f}", 7)
        total += amt; y += 15
    pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 14
    t(400, y, f"BID TOTAL:  ${total:,.2f}", 10); y += 26
    for line in NOTES.get(case["id"], []):
        t(40, y, line, 7); y += 12
    path = os.path.join(DOCS, f'{case["id"]}.pdf'); doc.save(path)
    return path, round(total, 2)


def expected(case, total):
    return {
        "id": case["id"], "doc_type": case["doc_type"], "vendor": case["vendor"],
        "trade": case["trade"], "bid_total": total,
        "line_items": [
            {"section": s, "description": d, "qty": q, "unit": u, "unit_price": up, "amount": a}
            for (s, d, q, u, up, a) in case["line_items"]
        ],
        "math_error_idx": case["math_error_idx"],
        "exclusion_keys": case["exclusion_keys"],
        "expect_exclusions_min": case["expect_exclusions_min"],
        "expect_exclusions_max": case.get("expect_exclusions_max"),
    }


if __name__ == "__main__":
    for case in CASES:
        path, total = render(case)
        json.dump(expected(case, total), open(os.path.join(EXP, f'{case["id"]}.json'), "w"), indent=2)
        print(f'generated {case["id"]}.pdf  (total ${total:,.2f})  + expected/{case["id"]}.json')
