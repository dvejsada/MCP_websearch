"""Search package for MCP Search server using Serper.dev API."""

from search.serper import google_search, google_search_raw, extract_page_content, SerperClient
from search.ui import generate_search_results_html, create_search_results_ui

__all__ = [
    "google_search",
    "google_search_raw",
    "extract_page_content",
    "SerperClient",
    "generate_search_results_html",
    "create_search_results_ui",
]
