"""Generate a realistic, messy drywall subcontractor quote PDF with line items
and a nasty exclusion buried in fine print — to test BidReader honestly."""
import fitz

doc = fitz.open(); pg = doc.new_page(width=612, height=792)
def t(x, y, s, size=10, color=(0,0,0)):
    pg.insert_text((x, y), s, fontsize=size, color=color)

t(40, 50, "ACME DRYWALL & METAL FRAMING, LLC", 14)
t(40, 66, "1420 Industrial Pkwy, Columbus OH  |  bids@acmedrywall.com", 8)
t(40, 90, "SUBCONTRACTOR QUOTE  —  Quote #DW-2026-0417", 11)
t(40, 106, "Project: Maple Street Medical Office Building (3 storey)", 9)
t(40, 118, "To: Buckeye General Contractors   Date: June 12, 2026", 9)

t(40, 150, "SCOPE OF WORK — Light gauge framing, gypsum board, taping & finishing", 9)
rows = [
 ("09 22 16", "Metal stud framing, 3-5/8\" 25ga walls", "12,400", "SF", "2.85", "35,340.00"),
 ("09 29 00", "5/8\" Type X gypsum board, both faces", "24,800", "SF", "1.65", "40,920.00"),
 ("09 29 00", "Tape & finish, Level 4", "24,800", "SF", "0.95", "23,560.00"),
 ("09 81 00", "Acoustic insulation, R-13 batts", "12,400", "SF", "0.72", "8,928.00"),
 ("09 22 16", "Ceiling suspension grid framing", "9,200", "SF", "1.40", "12,880.00"),
]
y = 168
t(40, y, "CSI"); t(95, y, "Description"); t(340, y, "Qty"); t(395, y, "Unit"); t(435, y, "Unit$"); t(500, y, "Amount"); y += 6
pg.draw_line(fitz.Point(40, y), fitz.Point(560, y)); y += 14
for csi, d, q, u, up, amt in rows:
    t(40, y, csi, 8); t(95, y, d, 8); t(340, y, q, 8); t(395, y, u, 8); t(435, y, up, 8); t(500, y, amt, 8); y += 16
pg.draw_line(fitz.Point(40, y), fitz.Point(560, y)); y += 14
t(420, y, "BASE BID TOTAL:  $121,628.00", 10); y += 26

t(40, y, "CLARIFICATIONS & ASSUMPTIONS", 9); y += 14
notes = [
 "1. Pricing assumes building dried-in and conditioned prior to board installation.",
 "2. One mobilization included; additional mobilizations billed at $850 each.",
 "3. Pricing valid for 30 days from date above. Material escalation may apply thereafter.",
 # the buried nasty exclusion, small font, mid-paragraph:
 "4. Work is based on Architectural drawings dated 05/2026. Quantities by others; this",
 "   proposal EXCLUDES fire-stopping/firecaulking at rated assemblies, scaffolding over",
 "   10', final cleaning, and removal/haul-off of construction debris (by others).",
 "5. Add alternate ADD-1: Level 5 finish at lobby walls .......... ADD $6,200.00",
]
for n in notes:
    t(40, y, n, 7); y += 12

t(40, y + 10, "Submitted by: J. Alvarez, Estimator", 8)
doc.save("/Users/anmol/bidreader/sample_quote.pdf")
print("wrote /Users/anmol/bidreader/sample_quote.pdf")
