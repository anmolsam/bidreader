"""Generate 3 competing electrical subcontractor quotes (same project, differing
scope/exclusions/prices) so `bidreader level` has a realistic apples-to-apples demo."""
import os, fitz

HERE = os.path.dirname(__file__)

SUBS = [
    {"file": "elec_sub_a.pdf", "vendor": "Voltage Bros Electric", "total_note": None,
     "items": [("26 05 19", "Branch wiring THHN", 8400, "LF", 1.20),
               ("26 51 00", "LED 2x4 troffers", 220, "EA", 145.00),
               ("26 27 26", "Wiring devices + plates", 540, "EA", 18.00),
               ("26 24 16", "Panelboards 42-ckt", 6, "EA", 2100.00)],
     "excl": ["Fire alarm system and devices are EXCLUDED (by others).",
              "Low voltage / data cabling not included.",
              "Excludes temporary power and temporary lighting."]},
    {"file": "elec_sub_b.pdf", "vendor": "Current Co", "total_note": None,
     "items": [("26 05 19", "Branch circuit wiring", 8400, "LF", 1.35),
               ("26 51 00", "LED troffer fixtures 2x4", 220, "EA", 158.00),
               ("26 27 26", "Devices and coverplates", 540, "EA", 16.50),
               ("26 24 16", "Distribution panelboards", 6, "EA", 1980.00),
               ("28 31 00", "Fire alarm system complete", 1, "LS", 42000.00)],
     "excl": ["Low voltage / data cabling by others.",
              "Excludes equipment pads and housekeeping pads."]},
    {"file": "elec_sub_c.pdf", "vendor": "Sparky Solutions LLC", "total_note": None,
     "items": [("26 05 19", "Power branch wiring", 8400, "LF", 1.10),
               ("26 51 00", "2x4 LED troffers", 220, "EA", 139.00),
               ("26 27 26", "Wiring devices", 540, "EA", 15.00),
               ("26 24 16", "Panelboards", 6, "EA", 1850.00),
               ("26 56 00", "Site / exterior lighting", 1, "LS", 18500.00)],
     "excl": ["Fire alarm EXCLUDED.", "Temporary power EXCLUDED.",
              "Low voltage and data EXCLUDED.", "Permits by GC."]},
]


def render(sub):
    doc = fitz.open(); pg = doc.new_page(width=612, height=792)
    def t(x, y, s, sz=9): pg.insert_text((x, y), s, fontsize=sz)
    t(40, 50, sub["vendor"], 14)
    t(40, 66, "ELECTRICAL SUBCONTRACTOR QUOTE — Riverside Commercial Build-Out", 9)
    y = 96
    t(40, y, "CSI"); t(95, y, "Description"); t(360, y, "Qty"); t(400, y, "Unit"); t(440, y, "Unit$"); t(515, y, "Amount")
    y += 6; pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 14
    total = 0.0
    for sec, d, q, u, up in sub["items"]:
        amt = q * up; total += amt
        t(40, y, sec, 7); t(95, y, d[:46], 7); t(360, y, f"{q:,}", 7); t(400, y, u, 7)
        t(440, y, f"{up:,.2f}", 7); t(515, y, f"{amt:,.2f}", 7); y += 15
    pg.draw_line(fitz.Point(40, y), fitz.Point(565, y)); y += 14
    t(400, y, f"BID TOTAL:  ${total:,.2f}", 10); y += 26
    t(40, y, "Clarifications & Exclusions:", 9); y += 13
    for i, e in enumerate(sub["excl"], 1):
        t(40, y, f"{i}. {e}", 7); y += 12
    path = os.path.join(HERE, sub["file"]); doc.save(path)
    return path, total


if __name__ == "__main__":
    for s in SUBS:
        p, tot = render(s)
        print(f"wrote {s['file']}  ({s['vendor']}, ${tot:,.0f})")
