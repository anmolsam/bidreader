---
name: Bug report
about: Something extracted wrong, or a document failed
title: "[bug] "
labels: bug
---

**What happened**
A clear description. If extraction was wrong, paste the relevant `bidreader <pdf> --json` snippet.

**Document**
Type (sub-quote / bid package / spec / schedule), page count, vector or scanned.
Do NOT attach copyrighted third-party PDFs — a synthetic/redacted repro is ideal.

**Model used**
`BID_MODEL` value and gateway (AI Studio / OpenRouter / Requesty).

**Expected vs actual**

**Environment**
`bidreader --version` (or `pip show bidreader`), Python version, OS.
