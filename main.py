"""FastMCP Server with tools for MCP Search."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastmcp import FastMCP
from mcp_ui_server.core import UIResource
from pydantic import Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from config import get_config
from middleware import BearerAuthMiddleware, RequestLoggingMiddleware
from search import google_search, google_search_raw, extract_page_content, SerperClient, create_search_results_ui
from mcp_ui_server import create_ui_resource

# Load configuration
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mcp_search")


@asynccontextmanager
async def lifespan(app):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    yield
    # Shutdown - close the shared HTTP client with timeout
    try:
        await asyncio.wait_for(SerperClient.close(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Timeout while closing HTTP client")
    except asyncio.CancelledError:
        # Gracefully handle cancellation during shutdown
        pass
    except Exception as e:
        logger.warning(f"Error closing HTTP client: {e}")


# Initialize FastMCP server with optimized settings
mcp = FastMCP(
    name="mcp-search",
    version="0.1.0",
    instructions="MCP Search Server providing search tools.",
    # Performance and behavior settings
    on_duplicate_tools=config.ON_DUPLICATE_TOOLS,
    on_duplicate_resources=config.ON_DUPLICATE_RESOURCES,
    on_duplicate_prompts=config.ON_DUPLICATE_PROMPTS,
    # Disable FastMCP metadata for cleaner responses
    include_fastmcp_meta=config.INCLUDE_FASTMCP_META,
    # Lifespan handler for proper cleanup
    lifespan=lifespan,
)

# Add middleware (order matters: auth first, then logging)
if config.API_KEY:
    mcp.add_middleware(BearerAuthMiddleware(api_key=config.API_KEY))

mcp.add_middleware(RequestLoggingMiddleware())


# Health check endpoint for container orchestration
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint for load balancers and container orchestration."""
    return PlainTextResponse("OK")


@mcp.tool(
    name="search_web",
    description="Search the web using Google.",
    annotations={
        "title": "Web Search",
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def search_web_tool(
    query: Annotated[str, Field(description="The search query string")],
    country: Annotated[str | None, Field(description="Country code for localized results (e.g., 'us', 'cz', 'de')")] = None,
    language: Annotated[str | None, Field(description="Language code for results (e.g., 'en', 'cs', 'de')")] = None,
    location: Annotated[str | None, Field(description="Geographic location for results (e.g., 'Prague, Czech Republic', 'New York, United States')")] = None,
    time_period: Annotated[str | None, Field(description="Time filter: 'qdr:h' (past hour), 'qdr:d' (past day), 'qdr:w' (past week), 'qdr:m' (past month), 'qdr:y' (past year)")] = None,
    page: Annotated[int | None, Field(description="Page number for pagination (starts at 1)", ge=1)] = 1,
) -> str:
    """Search the web using Google. Returns results as text."""
    return await google_search(
        query=query,
        country=country,
        language=language,
        location=location,
        time_period=time_period,
        page=page,
    )



@mcp.tool(
    name="extract_webpage",
    description="Extract the main text content from a webpage URL.",
    annotations={
        "title": "Extract Webpage Content",
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def extract_webpage_tool(
    url: Annotated[str, Field(description="The URL of the webpage to extract content from")],
) -> str:
    """Extract the main text content from a webpage."""
    return await extract_page_content(url=url)


@mcp.tool(
    name="search_web_ui",
    description="Search the web using Google and display results with a visual UI. Use this for a rich visual presentation of search results.",
    annotations={
        "title": "Web Search (Visual UI)",
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def search_web_ui_tool(
    query: Annotated[str, Field(description="The search query string")],
    country: Annotated[str | None, Field(description="Country code for localized results (e.g., 'us', 'cz', 'de')")] = None,
    language: Annotated[str | None, Field(description="Language code for results (e.g., 'en', 'cs', 'de')")] = None,
    location: Annotated[str | None, Field(description="Geographic location for results (e.g., 'Prague, Czech Republic', 'New York, United States')")] = None,
    time_period: Annotated[str | None, Field(description="Time filter: 'qdr:h' (past hour), 'qdr:d' (past day), 'qdr:w' (past week), 'qdr:m' (past month), 'qdr:y' (past year)")] = None,
    page: Annotated[int | None, Field(description="Page number for pagination (starts at 1)", ge=1)] = 1,
) -> list[UIResource]:
    """Search the web using Google and return results with visual UI."""
    # Get raw search results
    data = await google_search_raw(
        query=query,
        country=country,
        language=language,
        location=location,
        time_period=time_period,
        page=page,
    )

    results = data.get("organic", [])

    # Create UI resource using helper from search package
    ui_resource = create_search_results_ui(query, results)

    return [ui_resource]


# ============================================================================
# Example: UI Tool Implementation
# ============================================================================
# This is a commented-out example showing how to create a tool that returns
# a visual UI component. Use this as a template for creating your own UI tools.
#
# @mcp.tool(
#     name="test_ui_simple",
#     description="Test tool displaying a simple placeholder UI with 600px height.",
#     annotations={
#         "title": "Test UI (Simple)",
#         "readOnlyHint": True,
#         "openWorldHint": True,
#     },
# )
# async def test_ui_simple_tool() -> list[UIResource]:
#     """Display a simple placeholder UI for testing purposes."""
#     html_content = """
# <style>
#   * { box-sizing: border-box; margin: 0; padding: 0; }
#   html, body { overflow: hidden; }
#   body {
#     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
#     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#     min-height: 100vh;
#   }
#   .mcp-ui-container {
#     min-height: 600px;
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     padding: 20px;
#   }
#   .card {
#     text-align: center;
#     padding: 40px;
#     background: rgba(255,255,255,0.1);
#     border-radius: 16px;
#     backdrop-filter: blur(10px);
#     color: #fff;
#   }
#   .icon { font-size: 64px; margin-bottom: 20px; }
#   h1 { font-size: 28px; margin-bottom: 12px; }
#   p { font-size: 16px; opacity: 0.9; }
# </style>
#
# <article class="mcp-ui-container">
#   <div class="card">
#     <div class="icon">🎨</div>
#     <h1>MCP UI Test</h1>
#     <p>Simple placeholder UI (600px height)</p>
#   </div>
# </article>
#
# <script>
# const container = document.querySelector('.mcp-ui-container');
# function postSize() {
#   window.parent.postMessage({
#     type: "ui-size-change",
#     payload: { height: container.scrollHeight, width: container.scrollWidth }
#   }, "*");
# }
# new ResizeObserver(() => postSize()).observe(container);
# postSize();
# </script>
# """
#
#     ui_resource = create_ui_resource({
#         "uri": "ui://mcp-search/test-simple",
#         "content": {
#             "type": "rawHtml",
#             "htmlString": html_content
#         },
#         "encoding": "text"
#     })
#
#     return [ui_resource]

if __name__ == "__main__":
    # Run the server with streamable HTTP transport
    mcp.run(
        transport=config.TRANSPORT,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL,
    )

