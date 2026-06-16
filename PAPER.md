# BidReader: An Open Primitive for Structured Extraction and Scope-Gap Detection from Construction Bid Documents

**Abstract.** Construction estimators lose hours moving numbers out of inconsistently-formatted PDFs and, more dangerously, miss exclusions and scope gaps buried in vendor fine print — omissions that surface later as six-figure change orders. The current wave of construction AI concentrates on autonomous *takeoff* (measuring quantities from drawings), a space that is both commercially saturated and actively resisted by estimators. We argue the higher-leverage, under-served problem is **document intelligence**: turning messy bid documents into clean, page-cited structured data and surfacing what a vendor did *not* include. We present **BidReader**, an MIT-licensed Python library, CLI, and MCP server that performs this task with a page-chunked LLM extraction pipeline. On real third-party estimates it extracts line items at scale (72 items from a $324K drywall bid; 959 items across 16 CSI divisions from a 25-page GC estimate) and flags materially important scope gaps (e.g., gypsum board priced without finishing labor; door openings without hardware; missing firestopping). BidReader fills a verified gap: no permissively-licensed, installable library previously provided this capability.

## 1. Problem

Two needs recur across estimator and developer communities:

1. **"Crime-scene formatting."** Sub-quotes, bid packages, schedules, and spec sections arrive as PDFs whose layout resists copy/paste. Re-keying into a spreadsheet is slow and error-prone.
2. **Buried exclusions.** Vendors place scope limitations ("by others", "not included", "excludes…") in footnotes and fine print. Missing one shifts cost to the GC or a change order.

Representative evidence (estimators):

- *"Manually typing numbers from a PDF into Excel because the formatting is a crime scene… hunting for the one line where a sub quietly excluded 'trash removal' in size-8 font."* — r/Construction, 498 upvotes. https://www.reddit.com/r/Construction/comments/1pq34ur/
- *"Trying to scrape a messy sub quote into a clean table usually takes me longer than just re-typing it manually."* — ibid.
- *"I just want a junior who never sleeps… don't write anything new — just find the existing text (like a specific exclusion hidden in the notes) and point to it."* — ibid.

Representative evidence (builders of construction AI):

- *"Trust is the real bottleneck. Estimators don't adopt tools they can't audit. Every output has to trace back to something verifiable, or it's a liability."* — r/ConstructTech. https://www.reddit.com/r/ConstructTech/comments/1sehfy4/
- Frontier vision models "struggle to locate symbols on a crowded plan sheet… the best published results top out around 83% mAP." — bedrock.cv. https://bedrock.cv/blog/why-construction-symbol-detection-is-hard

## 2. Why not autonomous takeoff?

The visible gold rush targets PDF→auto-takeoff. Two findings argue against it as an open-source wedge:

1. **Saturation.** 15+ closed SaaS products and dozens of sub-15-star solo repositories already chase it.
2. **Resistance.** Estimators decline to delegate the measurement step: *"The takeoff is the thinking part. That's where I catch the weird stuff… AI as the first set of eyes is an idea only morons could think up."*

Document intelligence sits adjacent: estimators *want* a tireless assistant that reads and points, and it is technically tractable today.

## 3. Prior art and the gap

| Tool | Scope | License | Installable lib? |
|---|---|---|---|
| IfcOpenShell | IFC/BIM geometry & QTO | LGPL-3.0 | yes (needs an IFC model, not PDFs) |
| CubiCasa5K | floor-plan segmentation | **CC-BY-NC** | no (research code) |
| OpenConstructionERP | BOQ + takeoff app | **AGPL-3.0** | yes (copyleft blocks SaaS) |
| DeepFloorplan | floor-plan recognition | GPL-3.0 | no (stale) |
| **bid-document → structured data + exclusions** | — | — | **none (verified empty on PyPI)** |

PyPI names `bidreader`, `blueprint-parser`, `pytakeoff`, `floortrans` were unclaimed/unrelated. No permissive library performed bid-document extraction with scope-gap detection.

## 4. Method

```
PDF → per-page text (PyMuPDF) → page-chunking (≤~42k chars/chunk)
    → per-chunk LLM structured extraction (strict JSON schema)
    → merge (concat line items/exclusions; dedupe scope gaps; grand-total = max)
    → page-cited Doc { line_items, exclusions, assumptions, alternates, scope_gaps }
```

Design choices:

- **Page-tagged input** so every extracted value carries a verifiable page citation — directly addressing the trust/audit bottleneck.
- **Chunking by page** so large estimates (25+ pages, 900+ items) never truncate the model's JSON output. (This was a real failure mode fixed in v0.2.1.)
- **Exclusion-hunting prompt** that treats fine print, footnotes, and "by others" as first-class targets, quoted verbatim with page and a plain-language risk note.
- **Scope-gap inference**: the model reasons about trade-standard scope *absent* from the document (e.g., drywall finishing labor) and flags it for human confirmation.
- **Provider-agnostic, free-capable**: any OpenAI-compatible or Google AI Studio endpoint; text task → free models suffice.

BidReader is human-in-the-loop by design: it proposes and cites; the estimator verifies. Accuracy over automation.

## 5. Results

Tested on real, publicly-published third-party estimates (documents not redistributed here; source URLs and reproduction steps in [docs/RESULTS.md](docs/RESULTS.md)).

- **Drywall estimate (appleestimating.com), 2 pp.** Extracted **72 line items**, bid total **$324,240.61**, with correct CSI grouping. Zero hallucinated exclusions (the document states none). Inferred **7 scope gaps**, including the materially significant *gypsum board priced without finishing labor (taping/mudding/sanding)*, missing *door hardware*, and *firestopping at rated assemblies*.
- **General-contractor estimate (federalestimating.com), 25 pp.** Extracted **959 line items across 16 CSI divisions** (Div 01 General Requirements through Div 22 Plumbing), each page-cited, via 7-chunk page splitting.
- **Synthetic drywall quote** (provided in `examples/`): 5 line items + correctly caught all 4 buried exclusions (fire-stopping, scaffolding >10', final cleaning, debris haul-off) hidden in size-7 footnote text.

## 6. Limitations

- Scanned (image-only) PDFs are not yet supported (vision-OCR path is on the roadmap).
- Scope-gap inference is advisory and may over- or under-suggest; it is meant to prompt human confirmation, not to be authoritative.
- Numeric accuracy depends on the underlying model; free/small models trade some recall for cost. Outputs are proposals to be verified, never final.

## 7. Future work

Revision/addendum diffing; Excel/CSV BOQ export and multi-quote leveling; region/trade notation packs; a permissively-licensed annotated benchmark corpus for bid-document extraction.

## 8. Reproducibility

`pip install bidreader`; set any LLM key; run `bidreader <pdf> --json`. The synthetic example and its output ship in `examples/`. Real-document tests are reproducible from the public URLs in [docs/RESULTS.md](docs/RESULTS.md).

## References

1. r/Construction, "estimator grunt work" thread (498 upvotes). https://www.reddit.com/r/Construction/comments/1pq34ur/
2. r/ConstructTech, builder discussion on trust/scope. https://www.reddit.com/r/ConstructTech/comments/1sehfy4/
3. Bedrock, "Why construction symbol detection is hard." https://bedrock.cv/blog/why-construction-symbol-detection-is-hard
4. IfcOpenShell. https://github.com/IfcOpenShell/IfcOpenShell
5. CubiCasa5K. https://github.com/CubiCasa/CubiCasa5k
