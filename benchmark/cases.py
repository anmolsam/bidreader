"""Ground-truth benchmark cases.

These are SYNTHETIC documents we author, so the ground truth is exact and the
PDFs are freely redistributable (no third-party copyright). `generate.py` renders
each case to a PDF; `expected/<id>.json` is the committed ground truth; `run.py`
scores BidReader's output against it.

Each line item: (section, description, qty, unit, unit_price, printed_amount).
For correct lines printed_amount == qty*unit_price. For lines listed in
`math_error_idx`, printed_amount is intentionally WRONG (tests arithmetic check).
`exclusion_keys`: substrings that MUST appear in a caught exclusion (verbatim in doc).
"""

CASES = [
    {
        "id": "drywall_quote",
        "doc_type": "sub-quote",
        "vendor": "Acme Drywall & Framing LLC",
        "trade": "Drywall",
        "line_items": [
            ("09 22 16", "Metal stud framing 3-5/8in 25ga", 12400, "SF", 2.85, 35340.00),
            ("09 29 00", "5/8in Type X gypsum board both faces", 24800, "SF", 1.65, 40920.00),
            ("09 29 00", "Tape and finish Level 4", 24800, "SF", 0.95, 23560.00),
            ("09 81 00", "Acoustic insulation R-13 batts", 12400, "SF", 0.72, 8928.00),
            ("09 22 16", "Ceiling suspension grid framing", 9200, "SF", 1.40, 12880.00),
        ],
        "math_error_idx": [],
        "exclusion_keys": ["fire-stopping", "scaffolding", "debris"],
        "expect_exclusions_min": 3,
    },
    {
        "id": "gc_multitrade",
        "doc_type": "bid package",
        "vendor": "Bedrock General Contractors",
        "trade": "General",
        "line_items": [
            ("01 00 00", "General conditions and supervision", 1, "LS", 48000.00, 48000.00),
            ("02 41 00", "Selective demolition interior", 6200, "SF", 3.10, 19220.00),
            ("03 30 00", "Cast-in-place concrete slab on grade", 310, "CY", 165.00, 51150.00),
            ("05 12 00", "Structural steel columns and beams", 42, "TON", 2850.00, 119700.00),
            ("07 54 00", "TPO roofing 60 mil", 18500, "SF", 6.40, 118400.00),
            ("08 11 00", "Hollow metal doors and frames", 36, "EA", 900.00, 32400.00),
            ("09 51 00", "Acoustical ceiling 2x4 grid and tile", 14200, "SF", 4.20, 59640.00),
            ("22 00 00", "Plumbing rough-in and fixtures", 1, "LS", 88000.00, 88000.00),
        ],
        "math_error_idx": [],
        "exclusion_keys": ["hazardous material", "permit"],
        "expect_exclusions_min": 2,
    },
    {
        "id": "quote_with_errors",
        "doc_type": "sub-quote",
        "vendor": "Lowball Electric Inc",
        "trade": "Electrical",
        "line_items": [
            ("26 05 19", "Branch circuit wiring THHN", 8400, "LF", 1.20, 10080.00),   # correct
            ("26 51 00", "LED 2x4 troffer fixtures", 220, "EA", 145.00, 25900.00),    # WRONG (=31900)
            ("26 27 26", "Wiring devices and plates", 540, "EA", 18.00, 9720.00),     # correct
            ("26 24 16", "Panelboards 42-circuit", 6, "EA", 2100.00, 14700.00),       # WRONG (=12600)
        ],
        "math_error_idx": [1, 3],
        "exclusion_keys": ["fire alarm", "low voltage"],
        "expect_exclusions_min": 2,
    },
    {
        "id": "clean_no_exclusions",
        "doc_type": "sub-quote",
        "vendor": "Straight Shooter Painting",
        "trade": "Painting",
        "line_items": [
            ("09 91 00", "Prime and paint gypsum walls 2 coats", 31000, "SF", 0.78, 24180.00),
            ("09 91 00", "Paint hollow metal doors and frames", 36, "EA", 65.00, 2340.00),
            ("09 91 23", "Paint exposed structure ceilings", 14200, "SF", 1.10, 15620.00),
        ],
        "math_error_idx": [],
        "exclusion_keys": [],          # NONE — tests no-hallucination
        "expect_exclusions_min": 0,
        "expect_exclusions_max": 0,
    },
    {
        "id": "spec_prose_exclusions",
        "doc_type": "spec section",
        "vendor": "Apex Roofing Co",
        "trade": "Roofing",
        "line_items": [
            ("07 54 23", "TPO membrane fully adhered 60 mil", 22000, "SF", 6.10, 134200.00),
            ("07 22 00", "Polyiso roof insulation R-30", 22000, "SF", 2.30, 50600.00),
            ("07 62 00", "Sheet metal flashing and trim", 1450, "LF", 14.00, 20300.00),
        ],
        "math_error_idx": [],
        # exclusions written into prose notes, not a tidy list:
        "exclusion_keys": ["wood blocking", "structural deck repair", "interior finishes"],
        "expect_exclusions_min": 3,
    },
]
