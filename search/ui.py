"""UI generation utilities for MCP Search using mcp-ui-server."""

import time
from urllib.parse import urlparse
from html import escape

from mcp_ui_server import create_ui_resource, UIMetadataKey
from mcp_ui_server.core import UIResource


def _get_favicon_url(url: str) -> str:
    """Get favicon URL using Google's favicon service."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
    except Exception:
        return "https://www.google.com/s2/favicons?domain=example.com&sz=32"


def _escape_html(text: str) -> str:
    """Safely escape HTML characters."""
    return escape(str(text)) if text else ""


def _get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return url


def generate_search_results_html(query: str, results: list[dict]) -> str:
    """Generate HTML for search results display.

    Args:
        query: The search query string.
        results: List of search result dictionaries with title, link, snippet, and position.

    Returns:
        Complete HTML document string for displaying search results.
    """
    if not results:
        return """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #666;
        }
        .empty { text-align: center; }
        .empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }
        .empty-text { font-size: 16px; }
    </style>
</head>
<body>
    <div class="empty">
        <div class="empty-icon">🔍</div>
        <div class="empty-text">Žádné výsledky</div>
    </div>
</body>
</html>
"""

    html_results = []

    for i, item in enumerate(results, 1):
        title = _escape_html(item.get("title", "Bez názvu"))
        link = item.get("link", "#")
        link_escaped = _escape_html(link)
        snippet = _escape_html(item.get("snippet", ""))
        position = item.get("position", i)
        favicon_url = _get_favicon_url(link)
        domain = _escape_html(_get_domain(link))

        html_results.append(f"""<div style="flex: 0 0 200px; height: 100px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; box-sizing: border-box;">
<div style="display: flex; align-items: center; gap: 4px; margin-bottom: 3px;">
<img src="{favicon_url}" alt="" style="width: 12px; height: 12px;" onerror="this.style.visibility='hidden'">
<span style="font-size: 9px; color: #6c757d; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{domain}</span>
<span style="font-size: 8px; font-weight: 600; color: #0d6efd; background: #e7f1ff; padding: 1px 4px; border-radius: 8px;">#{position}</span>
</div>
<a href="{link_escaped}" target="_blank" style="font-size: 10px; font-weight: 600; color: #212529; text-decoration: none; margin-bottom: 2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.2;">{title}</a>
<p style="font-size: 9px; color: #6c757d; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0; line-height: 1.2;">{snippet}</p>
<div style="display: flex; gap: 4px; margin-top: 2px;">
<button onclick="extractContent('{link_escaped}')" style="flex: 1; padding: 2px 4px; border-radius: 3px; font-size: 8px; font-weight: 500; cursor: pointer; border: none; background: #0d6efd; color: #fff;">Získat</button>
<a href="{link_escaped}" target="_blank" style="flex: 1; padding: 2px 4px; border-radius: 3px; font-size: 8px; font-weight: 500; cursor: pointer; text-decoration: none; text-align: center; background: #e9ecef; color: #495057;">Otevřít</a>
</div>
</div>""")

    results_html = "".join(html_results)

    return f"""<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{height:100%;overflow:hidden}}</style>
<div style="padding: 6px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; height: 150px; box-sizing: border-box; overflow: hidden;">
<div style="display: flex; gap: 6px; align-items: center; height: 100%;">
<button onclick="scrollCarousel(-1)" style="width: 20px; height: 20px; min-width: 20px; border-radius: 50%; border: 1px solid #ddd; background: #f5f5f5; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">◀</button>
<div id="carousel" style="display: flex; gap: 8px; overflow-x: auto; flex: 1; scroll-behavior: smooth; scrollbar-width: none; align-items: center;">{results_html}</div>
<button onclick="scrollCarousel(1)" style="width: 20px; height: 20px; min-width: 20px; border-radius: 50%; border: 1px solid #ddd; background: #f5f5f5; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">▶</button>
</div>
</div>
<script>
const carousel = document.getElementById('carousel');
function scrollCarousel(dir) {{ carousel.scrollBy({{ left: dir * 210, behavior: 'smooth' }}); }}
function extractContent(url) {{ if (window.parent) {{ window.parent.postMessage({{ type: 'tool', payload: {{ toolName: 'extract_webpage', params: {{ url: url }} }} }}, '*'); }} }}
</script>"""


def create_search_results_ui(query: str, results: list[dict]) -> UIResource:
    """Create a UI resource for search results.

    Args:
        query: The search query string.
        results: List of search result dictionaries.

    Returns:
        UIResource with HTML content for displaying search results.
    """
    html_content = generate_search_results_html(query, results)

    # Use timestamp for unique URI to avoid caching issues
    timestamp = int(time.time() * 1000)
    query_hash = hash(query) & 0xFFFFFFFF

    return create_ui_resource({
        "uri": f"ui://mcp-search/results-{query_hash}-{timestamp}",
        "content": {
            "type": "rawHtml",
            "htmlString": html_content
        },
        "encoding": "text",
        "uiMetadata": {
            UIMetadataKey.PREFERRED_FRAME_SIZE: ["100%", "150px"]
        }
    })

