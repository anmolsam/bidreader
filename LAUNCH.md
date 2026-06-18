# Launch posts (draft)

Honest, estimate-class framing. Fire only after `pip install bidreader` serves the
latest version (publish 0.9.5 first). Replace `<version>` checks before posting.

---

## Show HN

**Title:**
`Show HN: BidReader – open-source tool that catches the "fake low bid" in construction quotes`

**URL:** https://github.com/anmolsam/bidreader

**Body:**

I kept reading the same complaint from construction estimators: the lowest sub-quote
often wins the job and then blows the budget, because it quietly *excluded* scope —
fire alarm, firestopping, temporary power, debris haul-off — buried in size-8 fine
print. Comparing 5 messy PDF quotes by hand to find those gaps is hours of grunt work.

BidReader reads construction sub-quotes / estimates / spec PDFs into clean,
**page-cited** structured data, flags the exclusions vendors bury, arithmetic-checks
every line (qty × unit price = amount), and **levels multiple bids into one Excel
workbook** — bidders as columns, with an exclusion matrix that exposes the apparent
low bid that carved out scope.

```
$ pip install "bidreader[xlsx]"
$ bidreader level voltage_bros.pdf current_co.pdf sparky.pdf -o leveling.xlsx

Bid total        $64,300      $108,890     $77,520
                 ◀ "low"
EXCLUSION MATRIX (filled = this bidder EXCLUDED it):
Fire alarm        EXCL p1        —          EXCL p1
Temporary power   EXCL p1        —          EXCL p1
```
The $64,300 "low" bid excluded the fire alarm the $108,890 bid includes — not
actually the cheapest.

- **MIT**, pip-installable, also an MCP server (use it from Claude/Cursor).
- **Runs on free models** (Google AI Studio free tier / OpenRouter `:free`) — or
  **fully local with Ollama**, so confidential bids never leave your machine.
- Scanned PDFs handled via local Tesseract OCR.

**What it is honestly:** an *assistant*, not an autopilot. On 14 real public
estimate-class PDFs it parsed 14/14 without crashing and extracted ~4,200 line items;
its extracted grand total reconciled exactly with the document's own printed total on
6 of them (the misses are documented — some docs print no single total, and line-item
extraction is sometimes incomplete; the tool flags that in its output). It is **not**
built for multi-bidder DOT unit-price bid-tabs. Every number cites its page + source
text so you can verify, never blindly trust.

Repo has a reproducible benchmark + a real-document evidence pack (numbers above).
Feedback welcome — especially from estimators on what would make it bid-day usable,
and the line-item-completeness gap is the main thing I'm improving next.

---

## r/AECtech  (and r/Construction with a softer, less "dev" framing)

**Title:** `I open-sourced a tool that catches the scope a sub quietly excluded — and levels bids side-by-side in Excel`

**Body:**

Built this after seeing the r/Construction thread about estimator grunt work
(re-typing crime-scene PDFs, hunting for the one line where a sub excluded "trash
removal" in tiny font).

**BidReader** reads sub-quotes / estimates (PDF) and gives you:
- clean line items, each cited to its page + the exact text it came from
- the **exclusions** vendors bury ("by others", "not included", fine print)
- an **Excel leveling sheet**: every sub as a column, with a matrix showing who
  excluded what — so the "low bid" that dropped fire alarm / firestopping is obvious
- arithmetic check on every line (catches fat-fingered extensions)

It's free and open-source (MIT), runs on free AI models, and can run **100% on your
own machine** (Ollama) so bids stay confidential. Scanned PDFs work too (OCR).

It's a second set of eyes, not a replacement for your judgment — it proposes, you
verify (everything's cited). Tested on real public estimates; honest about where it's
still rough (line-item capture isn't always complete — it tells you when).

Repo: https://github.com/anmolsam/bidreader — would love feedback from estimators on
what's missing for real bid-day use.

---

## X / Twitter thread

**1/**
Estimators: the "low bid" that wins the job and then blows the budget usually didn't
win — it just *excluded* scope (fire alarm, firestopping, temp power) in the fine print.

I open-sourced a tool that catches it. 🧵

**2/**
BidReader reads messy construction quote PDFs → clean, page-cited line items + the
buried exclusions + an arithmetic check on every line.

`pip install "bidreader[xlsx]"`  (MIT)

**3/**
The killer feature: level multiple subs into one Excel sheet.

Bidders as columns. An exclusion matrix shows WHO excluded WHAT.

The $64,300 "low" bid excluded the fire alarm the $108,890 bid includes. Now it's
obvious. [screenshot of the matrix]

**4/**
- Runs on free models, or 100% local with Ollama (bids never leave your machine)
- Scanned PDFs via OCR
- Works as an MCP server (call it from Claude / Cursor)
- Every number cites its page + source text

**5/**
Honest: it's an assistant, not autopilot. Tested on real public estimates — parses
them reliably, extracts thousands of line items, and tells you when its line-item
capture looks incomplete. Built to verify, not blindly trust.

Repo + benchmark + real-doc evidence: https://github.com/anmolsam/bidreader

---

## Posting notes
- Publish 0.9.5 to PyPI first (so `pip install bidreader` matches the claims).
- Capture a real screenshot/GIF of the leveling Excel workbook + the matrix for HN/X.
- Best windows: Show HN ~6–9am PT weekday; r/AECtech midweek.
- Reply fast to the first comments (HN/Reddit reward author engagement).
- Lead with the fake-low-bid example everywhere; do NOT claim "handles all bids" —
  say estimate-class.
