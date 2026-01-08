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
        return """<style>*{margin:0;padding:0;box-sizing:border-box}html,body{overflow:hidden}</style>
<article class="mcp-ui-container" style="min-height:150px;display:flex;align-items:center;justify-content:center;padding:20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#666;background:#f5f5f5">
  <div style="text-align:center">
    <div style="font-size:48px;margin-bottom:12px;opacity:0.5">🔍</div>
    <div style="font-size:16px">Žádné výsledky</div>
  </div>
</article>
<script>
const c=document.querySelector('.mcp-ui-container');
function p(){window.parent.postMessage({type:"ui-size-change",payload:{height:c.scrollHeight,width:c.scrollWidth}},"*")}
new ResizeObserver(p).observe(c);p();
</script>"""

    html_results = []

    for i, item in enumerate(results, 1):
        title = _escape_html(item.get("title", "Bez názvu"))
        link = item.get("link", "#")
        link_escaped = _escape_html(link)
        snippet = _escape_html(item.get("snippet", ""))
        position = item.get("position", i)
        favicon_url = _get_favicon_url(link)
        domain = _escape_html(_get_domain(link))

        html_results.append(f"""<div style="flex:0 0 224px;height:250px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px;display:flex;flex-direction:column;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
<img src="{favicon_url}" alt="" style="width:16px;height:16px;border-radius:4px" onerror="this.style.visibility='hidden'">
<span style="font-size:12px;color:#64748b;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{domain}</span>
<span style="font-size:11px;font-weight:600;color:#3b82f6;background:#eff6ff;padding:2px 8px;border-radius:12px">#{position}</span>
</div>
<a href="{link_escaped}" target="_blank" style="font-size:14px;font-weight:600;color:#1e293b;text-decoration:none;margin-bottom:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.4">{title}</a>
<p style="font-size:13px;color:#64748b;flex:1;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;margin:0;line-height:1.5">{snippet}</p>
<div style="display:flex;gap:8px;margin-top:12px">
<button onclick="extractContent('{link_escaped}')" class="btn-primary" style="flex:1;padding:6px 10px;border-radius:6px;font-size:11px;font-weight:500;cursor:pointer;border:none;background:#3b82f6;color:#fff">Získat</button>
<a href="{link_escaped}" target="_blank" class="btn-secondary" style="flex:1;padding:6px 10px;border-radius:6px;font-size:11px;font-weight:500;cursor:pointer;text-decoration:none;text-align:center;border:1px solid #e2e8f0;background:#fff;color:#64748b">Otevřít</a>
</div>
</div>""")

    results_html = "".join(html_results)

    return f"""<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{overflow:hidden}}#carousel::-webkit-scrollbar{{display:none}}.nav-btn:hover{{background:#e2e8f0}}.btn-primary:hover{{background:#2563eb!important}}.btn-secondary:hover{{background:#f8fafc!important}}</style>
<article class="mcp-ui-container" style="min-height:270px;padding:4px 12px;display:flex;align-items:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#fff">
  <div style="display:flex;gap:8px;align-items:center;width:100%">
    <button class="nav-btn" onclick="scrollCarousel(-1)" style="width:32px;height:32px;min-width:32px;border-radius:50%;border:none;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 4px rgba(0,0,0,0.08)"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></button>
    <div id="carousel" style="display:flex;gap:12px;overflow-x:auto;flex:1;scroll-behavior:smooth;scrollbar-width:none;align-items:center;padding:4px 0">{results_html}</div>
    <button class="nav-btn" onclick="scrollCarousel(1)" style="width:32px;height:32px;min-width:32px;border-radius:50%;border:none;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 4px rgba(0,0,0,0.08)"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg></button>
  </div>
</article>
<script>
const c=document.querySelector('.mcp-ui-container'),r=document.getElementById('carousel');
function scrollCarousel(d){{r.scrollBy({{left:d*240,behavior:'smooth'}})}}
function extractContent(u){{window.parent.postMessage({{type:'tool',payload:{{toolName:'extract_webpage',params:{{url:u}}}}}}, '*')}}
function p(){{window.parent.postMessage({{type:"ui-size-change",payload:{{height:c.scrollHeight,width:c.scrollWidth}}}},"*")}}
new ResizeObserver(p).observe(c);p();
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

