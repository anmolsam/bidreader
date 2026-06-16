# Running BidReader on free models

BidReader is a **text** task (it reads extracted PDF text, not images), so free /
small LLMs handle it well. Pick any one — no paid plan required.

## Option A — Google AI Studio (free tier, recommended)

1. Get a free key at https://aistudio.google.com → "Get API key".
2. ```bash
   export GEMINI_API_KEY=AIza...
   export BID_MODEL=gemini-2.5-flash      # free tier; image input not needed
   bidreader your_quote.pdf
   ```
Free tier has generous daily limits and includes the Flash models. Note: on the
free tier Google may use data to improve products.

## Option B — OpenRouter free models

1. Key at https://openrouter.ai/keys
2. Pick any model with a `:free` suffix, e.g.:
   ```bash
   export OPENROUTER_API_KEY=sk-or-v1-...
   export BID_MODEL="google/gemini-2.0-flash-exp:free"
   # other free options vary over time — see https://openrouter.ai/models?max_price=0
   bidreader your_quote.pdf
   ```
Free models are rate-limited (good for a handful of documents at a time).

## Option C — Requesty

```bash
export REQUESTY_API_KEY=...
export BID_MODEL="google/gemini-2.5-flash"
```
Requesty routes to many providers behind one key (some free routes available).

## Choosing a model

| Use | Suggestion |
|---|---|
| Free, quick checks | `gemini-2.5-flash` (AI Studio) or an OpenRouter `:free` model |
| Dense 25-page estimates | a clear/large model improves table recall |
| Cost-sensitive at scale | Flash-class models are fractions of a cent per page |

`BID_MODEL` accepts any model id your chosen gateway supports. Set it and go.
