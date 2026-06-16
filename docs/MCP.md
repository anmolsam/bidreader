# BidReader MCP server

Expose BidReader to any MCP client (Claude Desktop, Cursor, Continue, etc.) so an
AI agent can read construction documents and reason over the results.

## Install

```bash
pip install "bidreader[mcp]"
```

## Configure

Add to your client's MCP config (Claude Desktop: `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bidreader": {
      "command": "bidreader-mcp",
      "env": { "GEMINI_API_KEY": "AIza..." }
    }
  }
}
```
Any supported key works (`GEMINI_API_KEY` / `OPENROUTER_API_KEY` / `REQUESTY_API_KEY`);
see [FREE_MODELS.md](FREE_MODELS.md). Optionally set `BID_MODEL`.

## Tools

| Tool | Args | Returns |
|---|---|---|
| `read_document` | `path` | full structured object: line_items, exclusions, assumptions, alternates, scope_gaps — page-cited |
| `catch_exclusions` | `path` | `{vendor, trade, exclusions[], scope_gaps[]}` — what to confirm before bidding |
| `extract_line_items` | `path` | `{bid_total, currency, line_items[]}` |

`path` is an absolute path to a local PDF the client can read.

## Example agent prompts

- *"Run catch_exclusions on every PDF in ~/bids/maple-st and tell me which subs excluded firestopping."*
- *"Read this sub-quote and compare its line items to the architect's spec."*

## Run standalone (debug)

```bash
GEMINI_API_KEY=... bidreader-mcp     # stdio transport
```
