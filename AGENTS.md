# AGENTS.md

## Purpose
- This repo is an MCP server exposing web search tools backed by Serper.dev.
- Entry point is `main.py`, which wires FastMCP tools, middleware, and lifecycle cleanup.

## Architecture At A Glance
- `main.py`: defines MCP tools (`search_web`, `search_web_ui`, `extract_webpage`) and `/health` route.
- `search/serper.py`: Serper API integration and shared async HTTP client (`SerperClient`).
- `search/ui.py`: builds raw HTML carousel UI and wraps it as `UIResource`.
- `middleware.py`: request logging + optional bearer auth (skips auth for MCP `initialize`).
- `config.py`: env-driven settings, cached via `get_config()`.

## Core Data Flows
- Text search flow: `search_web_tool` -> `google_search()` -> POST `https://google.serper.dev/search` -> formatted text.
- UI search flow: `search_web_ui_tool` -> `google_search_raw()` -> `create_search_results_ui()` -> `UIResource` list.
- Extraction flow: `extract_webpage_tool` -> `extract_page_content()` -> POST `https://scrape.serper.dev/`.

## UI/Tool Patterns To Follow
- Tool functions use `@mcp.tool(...)` and `Annotated[..., Field(...)]` for parameter schemas.
- `search_web_ui` returns `list[UIResource]`, not plain strings.
- UI HTML in `search/ui.py` posts:
  - `ui-size-change` for dynamic iframe sizing.
  - `tool` message calling `extract_webpage` when user clicks Extract.
- `create_search_results_ui()` uses timestamped `ui://mcp-search/...` URIs to avoid UI caching.

## Integration Boundaries
- External services:
  - Serper Search API (`google.serper.dev/search`)
  - Serper Scrape API (`scrape.serper.dev`)
  - Google favicon endpoint used in UI cards.
- Internal boundary: keep transport/middleware/tool registration in `main.py`; keep external API calling logic in `search/serper.py`.

## Practical Guardrails For Agents
- Reuse `SerperClient.get_client()`; do not create per-request `httpx.AsyncClient` instances.
- Surface API failures via `SerperAPIError` style used in `search/serper.py`.
- Keep auth semantics intact (do not require auth for MCP `initialize`).
- If adding UI tools, match existing postMessage contract and return `UIResource` objects.

