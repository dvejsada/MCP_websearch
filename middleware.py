"""Custom middleware for MCP Search server."""

import logging
import time
from typing import Optional

from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp import McpError
from mcp.types import ErrorData


logger = logging.getLogger("mcp_search")


class BearerAuthMiddleware(Middleware):
    """
    Middleware that authenticates requests using Bearer token (API key).

    The API key should be passed in the Authorization header as:
    Authorization: Bearer <api_key>
    """

    def __init__(self, api_key: str):
        """
        Initialize the authentication middleware.

        Args:
            api_key: The expected API key for authentication.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key

    async def on_request(self, context: MiddlewareContext, call_next):
        """Authenticate all incoming requests."""
        # Skip authentication for initialization (handshake)
        if context.method == "initialize":
            return await call_next(context)

        # Get authorization header
        auth_header = self._get_auth_header()

        if not auth_header:
            logger.warning(f"✗ Authentication failed for {context.method}: Missing Authorization header")
            raise McpError(
                ErrorData(
                    code=-32001,
                    message="Authentication required: Missing Authorization header"
                )
            )

        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            logger.warning(f"✗ Authentication failed for {context.method}: Invalid Authorization header format")
            raise McpError(
                ErrorData(
                    code=-32001,
                    message="Authentication required: Invalid Authorization header format. Expected 'Bearer <token>'"
                )
            )

        # Extract and validate token
        token = auth_header[7:]  # Remove "Bearer " prefix
        if token != self.api_key:
            logger.warning(f"✗ Authentication failed for {context.method}: Invalid API key")
            raise McpError(
                ErrorData(
                    code=-32001,
                    message="Authentication failed: Invalid API key"
                )
            )

        logger.debug(f"✓ Authentication successful for {context.method}")
        return await call_next(context)

    def _get_auth_header(self) -> Optional[str]:
        """Extract Authorization header from HTTP request."""
        try:
            headers = get_http_headers()
            if headers:
                return headers.get("authorization") or headers.get("Authorization")
        except Exception:
            # Not in HTTP context or headers not available
            pass
        return None


class RequestLoggingMiddleware(Middleware):
    """
    Middleware that logs all MCP requests and responses.

    Logs request method, timing, and success/failure status in a clean format.
    """

    async def on_message(self, context: MiddlewareContext, call_next):
        """Log all MCP messages with timing information."""
        start_time = time.perf_counter()
        method = context.method

        try:
            result = await call_next(context)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(f"✓ {method} [{duration_ms:.1f}ms]")
            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.error(f"✗ {method} [{duration_ms:.1f}ms] - {type(e).__name__}: {e}")
            raise

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Log tool calls with tool name."""
        start_time = time.perf_counter()
        tool_name = context.message.name

        try:
            result = await call_next(context)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(f"✓ tool/{tool_name} [{duration_ms:.1f}ms]")
            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.error(f"✗ tool/{tool_name} [{duration_ms:.1f}ms] - {type(e).__name__}: {e}")
            raise

