"""Serper.dev API integration for Google Search and page extraction."""

import httpx

from config import get_config


class SerperAPIError(Exception):
    """Exception raised when Serper.dev API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def google_search(
    query: str,
    country: str | None = None,
    language: str | None = None,
    location: str | None = None,
    time_period: str | None = None,
    page: int | None = 1,
) -> str:
    """
    Perform a Google search using Serper.dev API.

    Args:
        query: The search query string.
        country: Optional country code for localized results (e.g., "us", "cz").
        language: Optional language code for results (e.g., "en", "cs").
        location: Optional geographic location (e.g., "Prague, Czech Republic").
        time_period: Optional time filter (e.g., "qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y").
        page: Page number for pagination (starts at 1).

    Returns:
        Formatted text with search results.

    Raises:
        SerperAPIError: If the API request fails.
    """
    config = get_config()

    if not config.SERPER_API_KEY:
        raise SerperAPIError("SERPER_API_KEY is not configured")

    # Apply defaults for None values
    page = page if page is not None else 1

    # Build request payload
    payload: dict = {
        "q": query,
    }

    if country:
        payload["gl"] = country.lower()

    if language:
        payload["hl"] = language.lower()

    if location:
        payload["location"] = location

    if time_period:
        payload["tbs"] = time_period

    if page > 1:
        payload["page"] = page


    headers = {
        "X-API-KEY": config.SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise SerperAPIError(
                f"Serper API request failed: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise SerperAPIError(f"Serper API connection error: {str(e)}")

    data = response.json()

    # Format results as human-readable text
    lines = []
    for item in data.get("organic", []):
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        lines.append(f"{title}\n{link}\n{snippet}")

    return "\n\n".join(lines)


async def extract_page_content(url: str) -> str:
    """
    Extract content from a webpage using Serper.dev Scrape API.

    Args:
        url: The URL of the page to extract content from.

    Returns:
        Formatted text with page title and content.

    Raises:
        SerperAPIError: If the API request fails.
    """
    config = get_config()

    if not config.SERPER_API_KEY:
        raise SerperAPIError("SERPER_API_KEY is not configured")

    payload: dict = {
        "url": url,
    }

    headers = {
        "X-API-KEY": config.SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://scrape.serper.dev/",
                json=payload,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise SerperAPIError(
                f"Serper Scrape API request failed: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise SerperAPIError(f"Serper Scrape API connection error: {str(e)}")

    data = response.json()

    # Get title and content
    title = data.get("metadata", {}).get("title", "")
    content = data.get("text", "")

    # Format as human-readable text
    if title:
        return f"{title}\n\n{content}"
    return content

