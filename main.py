"""FastMCP Server with tools for MCP Search."""

import logging
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from config import get_config
from middleware import BearerAuthMiddleware, RequestLoggingMiddleware
from search import google_search, extract_page_content

# Load configuration
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

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


if __name__ == "__main__":
    # Run the server with streamable HTTP transport
    mcp.run(
        transport=config.TRANSPORT,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL,
    )

