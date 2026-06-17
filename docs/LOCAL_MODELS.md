# Run fully local — your bids never leave your machine

Subcontractor bids are confidential. BidReader can run entirely offline against a
local [Ollama](https://ollama.com) model, so **no document text is sent to any
cloud LLM**.

## Setup

```bash
# 1. install Ollama (https://ollama.com/download), then pull a capable text model
ollama pull llama3.1          # or qwen2.5, mistral-small, etc.

# 2. point BidReader at it (any one of these)
export BID_MODEL=ollama/llama3.1            # explicit
#   or
export BID_BACKEND=ollama                  # uses OLLAMA_MODEL (default llama3.1)
#   or
export OLLAMA_HOST=http://localhost:11434  # also enables Ollama

pip install bidreader
bidreader your_sub_quote.pdf
```

That's it — extraction, exclusion-catching, arithmetic checks, and leveling all
run against the local model. No API key required.

## Notes

- **Privacy**: with Ollama selected, the only network call is to your local
  `OLLAMA_HOST` (default `http://localhost:11434`). Nothing goes to Requesty /
  OpenRouter / Google.
- **Model choice**: bigger models extract dense multi-page estimates more
  reliably. `llama3.1`/`qwen2.5` (8B) handle typical quotes; use a larger model
  for 25-page bid packages. Output is always *proposals to verify*.
- **Speed**: local CPU inference is slower than cloud; BidReader uses a 10-minute
  per-call timeout for local backends.
- **Custom host**: set `OLLAMA_HOST=http://your-server:11434` to use a shared
  on-prem Ollama (e.g., a GC's internal box) — bids stay inside your network.
- **Remote/cloud option**: omit the Ollama vars and set a cloud key instead
  (see [FREE_MODELS.md](FREE_MODELS.md)).

## Verify it's local

```bash
BID_MODEL=ollama/llama3.1 bidreader your_quote.pdf
# while it runs, `ollama ps` shows the model loaded; no outbound cloud traffic.
```
