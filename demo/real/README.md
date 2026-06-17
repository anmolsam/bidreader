# Real / anonymized bid benchmark (drop-in)

The synthetic corpus proves the workflow is replayable; **real, estimator-labeled
quotes** are what prove it survives real bidder formatting, omissions, and bad scans.

To contribute a real benchmark case (even 5 quotes matters more than 50 synthetic):

1. Anonymize a real subcontractor quote PDF (redact names/prices if needed) → `demo/real/<id>.pdf`
2. Have an estimator label the truth → `demo/real/expected/<id>.json` (same shape as `demo/expected/*.json`).
3. Run `python demo/run_eval_real.py` (mirrors run_eval.py over this folder) and commit BidReader's raw output next to the expected labels.

PRs with real anonymized cases are the highest-value contribution — see ../../CONTRIBUTING.md.
Do NOT commit confidential/un-anonymized bids.
