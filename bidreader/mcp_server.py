"""BidReader MCP server — lets any agent (Claude Desktop, Cursor, etc.) read a
construction document and get structured data + caught exclusions.

Run:  bidreader-mcp           (stdio transport)
Needs an LLM key in env: REQUESTY_API_KEY / OPENROUTER_API_KEY / GEMINI_API_KEY.

Claude Desktop / Cursor config:
  {"mcpServers": {"bidreader": {"command": "bidreader-mcp",
     "env": {"REQUESTY_API_KEY": "rqsty-..."}}}}
"""
from __future__ import annotations
import os
from mcp.server.fastmcp import FastMCP
from .extract import read

mcp = FastMCP("bidreader")


def _check_key():
    if not (os.environ.get("REQUESTY_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        raise RuntimeError("No LLM key in env (REQUESTY_API_KEY / OPENROUTER_API_KEY / GEMINI_API_KEY).")


@mcp.tool()
def read_document(path: str) -> dict:
    """Read a construction PDF (sub-quote, bid package, spec section, schedule) into
    clean structured data: line_items, exclusions, assumptions, alternates, scope_gaps —
    every value cited to its page. `path` is an absolute path to a local PDF.
    Returns the full structured object."""
    _check_key()
    return dict(read(path))


@mcp.tool()
def catch_exclusions(path: str) -> dict:
    """Scan a construction quote/spec PDF for scope EXCLUSIONS and gaps a vendor buried
    (fine print, 'by others', 'not included'). Returns {exclusions:[{item,quote,page,risk}],
    scope_gaps:[{missing,why}]} — what an estimator must confirm before bidding."""
    _check_key()
    d = read(path)
    return {"vendor": d.get("vendor"), "trade": d.get("trade"),
            "exclusions": d.get("exclusions", []), "scope_gaps": d.get("scope_gaps", [])}


@mcp.tool()
def extract_line_items(path: str) -> dict:
    """Extract priced line items (section, description, qty, unit, amount, page) and the
    bid total from a construction quote/bid PDF. Returns {bid_total, currency, line_items}."""
    _check_key()
    d = read(path)
    return {"bid_total": d.get("bid_total"), "currency": d.get("currency"),
            "line_items": d.get("line_items", [])}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
