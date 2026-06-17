"""Generate a larger, MESSY, realistic synthetic bid corpus (+ ground truth).

Authored docs -> exact ground truth, freely redistributable. Deliberately varied
and messy: prose-buried exclusions, fine-print footnotes, two-column layouts,
alternates, planted arithmetic errors, multi-page, and scanned (image-only)
variants — so the evidence pack includes honest FAILURE cases, not just wins.
"""
import os, json, fitz

HERE = os.path.dirname(__file__)
CORPUS, EXPECT = os.path.join(HERE, "corpus"), os.path.join(HERE, "expected")
os.makedirs(CORPUS, exist_ok=True); os.makedirs(EXPECT, exist_ok=True)

# li = (section, description, qty, unit, unit_price, amount_override_or_None)
CASES = [
    # ---- electrical leveling set (4 subs, same scope, differing exclusions/price) ----
    {"id": "elec_sub_a", "trade": "Electrical", "vendor": "Voltage Bros Electric", "set": "electrical",
     "li": [("26 05 19", "Branch wiring THHN", 8400, "LF", 1.20, None),
            ("26 51 00", "LED 2x4 troffers", 220, "EA", 145.00, None),
            ("26 27 26", "Wiring devices + plates", 540, "EA", 18.00, None),
            ("26 24 16", "Panelboards 42-ckt", 6, "EA", 2100.00, None)],
     "err": [], "excl": ["Fire alarm system and devices EXCLUDED (by others).",
                         "Low voltage / data cabling not included.",
                         "Excludes temporary power and temporary lighting."],
     "keys": ["fire alarm", "low voltage", "temporary power"], "style": "tidy"},
    {"id": "elec_sub_b", "trade": "Electrical", "vendor": "Current Co", "set": "electrical",
     "li": [("26 05 19", "Branch circuit wiring", 8400, "LF", 1.35, None),
            ("26 51 00", "LED troffer fixtures 2x4", 220, "EA", 158.00, None),
            ("26 27 26", "Devices and coverplates", 540, "EA", 16.50, None),
            ("26 24 16", "Distribution panelboards", 6, "EA", 1980.00, None),
            ("28 31 00", "Fire alarm system complete", 1, "LS", 42000.00, None)],
     "err": [], "excl": ["Low voltage / data cabling by others.",
                         "Excludes equipment pads and housekeeping pads."],
     "keys": ["low voltage", "pads"], "style": "footnote"},
    {"id": "elec_sub_c", "trade": "Electrical", "vendor": "Sparky Solutions LLC", "set": "electrical",
     "li": [("26 05 19", "Power branch wiring", 8400, "LF", 1.10, None),
            ("26 51 00", "2x4 LED troffers", 220, "EA", 139.00, None),
            ("26 27 26", "Wiring devices", 540, "EA", 15.00, None),
            ("26 24 16", "Panelboards", 6, "EA", 1850.00, None),
            ("26 56 00", "Site / exterior lighting", 1, "LS", 18500.00, None)],
     "err": [], "excl": ["Fire alarm EXCLUDED.", "Temporary power EXCLUDED.",
                         "Low voltage and data EXCLUDED.", "Permits by GC."],
     "keys": ["fire alarm", "temporary power", "low voltage", "permits"], "style": "tidy"},
    {"id": "elec_sub_d", "trade": "Electrical", "vendor": "Ohm Town Electrical", "set": "electrical",
     "li": [("26 05 19", "Branch wiring (copper THHN)", 8400, "LF", 1.28, None),
            ("26 51 00", "2x4 LED fixtures", 220, "EA", 150.00, 30000.00),   # planted error (=33000)
            ("26 27 26", "Devices/plates", 540, "EA", 17.00, None),
            ("26 24 16", "Panelboards", 6, "EA", 2050.00, None),
            ("28 31 00", "Fire alarm", 1, "LS", 38000.00, None)],
     "err": [1], "excl": ["Low voltage/data by others.", "Excludes generator and ATS."],
     "keys": ["low voltage", "generator"], "style": "twocol"},
    # ---- drywall leveling set (3 subs) ----
    {"id": "dw_sub_a", "trade": "Drywall", "vendor": "Acme Drywall & Framing", "set": "drywall",
     "li": [("09 22 16", "Metal stud framing 3-5/8in 25ga", 12400, "SF", 2.85, None),
            ("09 29 00", "5/8in Type X gypsum board both faces", 24800, "SF", 1.65, None),
            ("09 29 00", "Tape and finish Level 4", 24800, "SF", 0.95, None),
            ("09 81 00", "Acoustic insulation R-13", 12400, "SF", 0.72, None)],
     "err": [], "excl": ["Excludes fire-stopping at rated assemblies.",
                         "Scaffolding over 10ft by others.", "Final cleaning excluded."],
     "keys": ["fire-stopping", "scaffolding", "final cleaning"], "style": "footnote"},
    {"id": "dw_sub_b", "trade": "Drywall", "vendor": "Premier Wall Systems", "set": "drywall",
     "li": [("09 22 16", "3-5/8in metal studs 25ga", 12400, "SF", 3.05, None),
            ("09 29 00", "Gypsum board 5/8 Type X 2 sides", 24800, "SF", 1.72, None),
            ("09 29 00", "Level 4 finish", 24800, "SF", 1.05, None),
            ("09 81 00", "R-13 batt insulation", 12400, "SF", 0.78, None),
            ("07 84 00", "Fire-stopping at rated walls", 1, "LS", 7800.00, None)],
     "err": [], "excl": ["Excludes scaffolding/lifts.", "Final cleaning by others."],
     "keys": ["scaffolding", "final cleaning"], "style": "tidy"},
    {"id": "dw_sub_c", "trade": "Drywall", "vendor": "BudgetBoard Co", "set": "drywall",
     "li": [("09 22 16", "Metal framing", 12400, "SF", 2.60, None),
            ("09 29 00", "Gyp board both faces", 24800, "SF", 1.55, None),
            ("09 29 00", "Tape/finish", 24800, "SF", 0.88, 20000.00)],   # planted error (=21824)
     "err": [2], "excl": ["Fire-stopping EXCLUDED.", "Insulation EXCLUDED.",
                          "Scaffolding EXCLUDED.", "Final cleaning EXCLUDED."],
     "keys": ["fire-stopping", "insulation", "scaffolding", "final cleaning"], "style": "twocol"},
    # ---- singles, varied trades + messiness ----
    {"id": "plumbing_quote", "trade": "Plumbing", "vendor": "FlowRight Mechanical", "set": None,
     "li": [("22 11 00", "Domestic water piping copper", 2400, "LF", 12.50, None),
            ("22 13 00", "Sanitary waste & vent PVC", 1800, "LF", 9.80, None),
            ("22 40 00", "Plumbing fixtures (WC/lav/sink)", 42, "EA", 650.00, None),
            ("22 34 00", "Gas-fired water heaters", 3, "EA", 4200.00, None)],
     "err": [], "excl": ["Excludes trenching, backfill, and site utilities (by others).",
                         "Medical gas systems not included.", "Excludes fire sprinkler."],
     "keys": ["trenching", "medical gas", "fire sprinkler"], "style": "prose"},
    {"id": "roofing_spec", "trade": "Roofing", "vendor": "Apex Roofing Co", "set": None,
     "li": [("07 54 23", "TPO membrane fully adhered 60mil", 22000, "SF", 6.10, None),
            ("07 22 00", "Polyiso roof insulation R-30", 22000, "SF", 2.30, None),
            ("07 62 00", "Sheet metal flashing and trim", 1450, "LF", 14.00, None)],
     "err": [], "excl": ["Wood blocking and nailers by others.",
                         "Structural deck repair excluded.", "Interior finishes not in scope."],
     "keys": ["wood blocking", "deck repair", "interior finishes"], "style": "prose"},
    {"id": "concrete_multipage", "trade": "Concrete", "vendor": "SolidForm Concrete", "set": None,
     "li": [("03 30 00", "Slab on grade 6in", 28000, "SF", 7.20, None),
            ("03 30 00", "Continuous footings", 320, "CY", 165.00, None),
            ("03 30 00", "Foundation walls 12in", 180, "CY", 285.00, None),
            ("03 21 00", "Reinforcing steel #5", 42000, "LBS", 1.10, None),
            ("03 35 00", "Polished concrete finish", 22000, "SF", 3.40, None),
            ("03 15 00", "Expansion joint + sealant", 2300, "LF", 4.20, None)],
     "err": [], "excl": ["Excludes excavation, over-ex, and engineered fill.",
                         "Concrete testing by Owner.", "Excludes site retaining walls."],
     "keys": ["excavation", "testing", "retaining"], "style": "multipage"},
    {"id": "steel_errors", "trade": "Structural Steel", "vendor": "IronClad Steel", "set": None,
     "li": [("05 12 00", "W-shape beams and columns", 86, "TON", 2850.00, None),
            ("05 21 00", "Steel joists", 42, "TON", 2400.00, 110000.00),   # planted error (=100800)
            ("05 31 00", "Metal deck 1.5in", 30000, "SF", 3.10, None),
            ("05 50 00", "Misc metals / embeds", 1, "LS", 28000.00, None)],
     "err": [1], "excl": ["Excludes fireproofing (SFRM).", "Anchor bolts/embeds set by others.",
                          "Excludes stairs and railings."],
     "keys": ["fireproofing", "anchor bolts", "stairs"], "style": "footnote"},
    {"id": "painting_clean", "trade": "Painting", "vendor": "Straight Shooter Painting", "set": None,
     "li": [("09 91 00", "Prime + paint gypsum walls 2 coats", 31000, "SF", 0.78, None),
            ("09 91 00", "Paint doors and frames", 36, "EA", 65.00, None),
            ("09 91 23", "Paint exposed ceilings", 14200, "SF", 1.10, None)],
     "err": [], "excl": [], "keys": [], "no_excl": True, "style": "tidy"},
    # ---- scanned (image-only) variants ----
    {"id": "hvac_scanned", "trade": "HVAC", "vendor": "Climate Control Inc", "set": None, "scanned": True,
     "li": [("23 74 00", "Rooftop units 20-ton", 4, "EA", 38000.00, None),
            ("23 31 00", "Ductwork galvanized", 18000, "LBS", 6.40, None),
            ("23 37 00", "Diffusers/grilles/registers", 180, "EA", 145.00, None),
            ("23 09 00", "Controls and BAS", 1, "LS", 62000.00, None)],
     "err": [], "excl": ["Excludes electrical power wiring to units (by others).",
                         "Test and balance by others.", "Excludes roof curbs."],
     "keys": ["electrical power", "test and balance", "roof curbs"], "style": "tidy"},
    {"id": "demo_scanned_messy", "trade": "Demolition", "vendor": "Wrecking Crew LLC", "set": None, "scanned": True,
     "li": [("02 41 00", "Interior selective demolition", 34000, "SF", 2.80, None),
            ("02 41 00", "Remove existing roofing", 22000, "SF", 1.40, None),
            ("02 41 00", "Haul-off and disposal", 1, "LS", 24000.00, None)],
     "err": [], "excl": ["Excludes abatement of hazardous materials (asbestos/lead).",
                         "Excludes structural demolition.", "Permits by GC."],
     "keys": ["hazardous", "structural", "permits"], "style": "footnote"},
]


def _render(case):
    doc = fitz.open(); pg = doc.new_page(width=612, height=792)
    def t(x, y, s, sz=9): pg.insert_text((x, y), s, fontsize=sz)
    t(40, 48, case["vendor"], 13)
    t(40, 63, f'{case["trade"]} — Riverside Commercial Build-Out', 8)
    style = case.get("style", "tidy")
    items = case["li"]; total = 0.0
    if style == "twocol":
        # messy two-column layout (harder to parse)
        t(40, 90, "SCOPE & PRICING", 9)
        half = (len(items) + 1) // 2
        for col, group in enumerate((items[:half], items[half:])):
            x = 40 + col * 290; y = 108
            for sec, d, q, u, up, ov in group:
                amt = ov if ov is not None else q * up; total += amt
                t(x, y, f"{sec} {d[:26]}", 6); y += 11
                t(x + 8, y, f"{q:,} {u} @ {up:,.2f} = {amt:,.2f}", 6); y += 16
        y = 108 + half * 27 + 20
    else:
        y = 96
        t(40, y, "CSI"); t(95, y, "Description"); t(360, y, "Qty"); t(400, y, "Unit"); t(440, y, "Unit$"); t(515, y, "Amount")
        y += 6; pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 13
        for sec, d, q, u, up, ov in items:
            amt = ov if ov is not None else q * up; total += amt
            t(40, y, sec, 7); t(95, y, d[:46], 7); t(360, y, f"{q:,}", 7); t(400, y, u, 7)
            t(440, y, f"{up:,.2f}", 7); t(515, y, f"{amt:,.2f}", 7); y += 14
        pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 13
    t(400, y, f"BID TOTAL:  ${total:,.2f}", 10); y += 24

    excl = case.get("excl", [])
    if style == "prose" and excl:
        t(40, y, "GENERAL CONDITIONS", 9); y += 13
        prose = ("The subcontractor shall furnish all labor and material for the scope above. "
                 + " ".join(excl) + " Pricing valid 30 days from date hereof.")
        # wrap prose
        words = prose.split(); line = ""
        for w in words:
            if len(line) + len(w) > 95:
                t(40, y, line, 7); y += 11; line = ""
            line += w + " "
        if line: t(40, y, line, 7); y += 11
    elif style == "footnote" and excl:
        t(40, y, "Clarifications:", 8); y += 11
        for i, e in enumerate(excl, 1):
            t(40, y, f"{i}. {e}", 6); y += 9        # tiny fine print
    elif excl:
        t(40, y, "Clarifications & Exclusions:", 9); y += 13
        for i, e in enumerate(excl, 1):
            t(40, y, f"{i}. {e}", 7); y += 12
    elif case.get("no_excl"):
        t(40, y, "Notes: Full prep included. Pricing valid 30 days.", 8)

    if style == "multipage":
        pg2 = doc.new_page(width=612, height=792)
        pg2.insert_text((40, 60), "Page 2 — Clarifications (cont.)", fontsize=9)
        yy = 90
        for i, e in enumerate(excl, 1):
            pg2.insert_text((40, yy), f"{i}. {e}", fontsize=7); yy += 12

    path = os.path.join(CORPUS, f'{case["id"]}.pdf'); doc.save(path)

    if case.get("scanned"):
        src = fitz.open(path); out = fitz.open()
        dpi = 150 if case["id"] != "demo_scanned_messy" else 110   # messier scan = lower dpi
        for p in src:
            pix = p.get_pixmap(dpi=dpi)
            npg = out.new_page(width=p.rect.width, height=p.rect.height)
            npg.insert_image(npg.rect, stream=pix.tobytes("png"))
        out.save(path)   # overwrite with image-only version
    return path, round(total, 2)


def main():
    index = []
    for case in CASES:
        path, total = _render(case)
        exp = {"id": case["id"], "trade": case["trade"], "vendor": case["vendor"],
               "bid_total": total, "scanned": case.get("scanned", False),
               "set": case.get("set"), "style": case["style"],
               "line_items": [{"section": s, "description": d, "qty": q, "unit": u,
                               "unit_price": up, "amount": (ov if ov is not None else q * up)}
                              for (s, d, q, u, up, ov) in case["li"]],
               "math_error_idx": case["err"], "exclusion_keys": case["keys"],
               "no_excl": case.get("no_excl", False)}
        json.dump(exp, open(os.path.join(EXPECT, f'{case["id"]}.json'), "w"), indent=2)
        index.append({"id": case["id"], "trade": case["trade"], "scanned": case.get("scanned", False),
                      "style": case["style"], "total": total, "set": case.get("set")})
        print(f'{case["id"]:24s} {case["trade"]:16s} {case["style"]:9s} '
              f'{"SCANNED" if case.get("scanned") else "text":8s} ${total:,.0f}')
    json.dump(index, open(os.path.join(HERE, "corpus_index.json"), "w"), indent=2)
    print(f"\n{len(CASES)} docs generated in demo/corpus/  (+ expected/)")


if __name__ == "__main__":
    main()
