# MCP Search Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing web search and content extraction tools powered by [Serper.dev](https://serper.dev/) Google Search API.

Built with [FastMCP](https://github.com/jlowin/fastmcp) for high performance and ease of use.

## Features

- 🔍 **Google Web Search** - Search the web with localization and time filters
- 📄 **Webpage Content Extraction** - Extract main text content from any URL
- 🎨 **Visual UI Search Results** - Rich visual presentation of search results
- 🔐 **Bearer Token Authentication** - Secure API access
- 🐳 **Docker Ready** - Easy deployment with Docker and Docker Compose
- ⚡ **HTTP/2 Support** - Fast, multiplexed connections

## Tools

### `search_web`

Search the web using Google.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | The search query string (required) |
| `country` | string | Country code for localized results (e.g., `us`, `cz`, `de`) |
| `language` | string | Language code for results (e.g., `en`, `cs`, `de`) |
| `location` | string | Geographic location (e.g., `Prague, Czech Republic`) |
| `time_period` | string | Time filter: `qdr:h` (hour), `qdr:d` (day), `qdr:w` (week), `qdr:m` (month), `qdr:y` (year) |
| `page` | int | Page number for pagination (starts at 1) |

### `search_web_ui`

Search the web using Google and display results with a visual UI. Same parameters as `search_web`. Show interactive buttons to extraxt of open the webpage.

### `extract_webpage`

Extract the main text content from a webpage URL.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | The URL of the webpage to extract content from (required) |


## Setup

### Prerequisites

- [Serper.dev API Key](https://serper.dev/) (free tier available)

### Docker

#### Using Docker Compose (Recommended)

1. Copy `docker-compose.yaml` to your target directory.

2. Create `.env` file with your configuration, see `.env.example` for reference.

3. Run:
   ```bash
   docker-compose up -d
   ```

#### Using Docker directly (pre-built image)

```bash
# Pull the pre-built image from Docker Hub
docker pull georgx22/websearch_mcp:latest

# Run the container (exposes port 8000)
docker run -d -p 8000:8000 --env-file .env georgx22/websearch_mcp:latest
```

## Health Check

The server exposes a health check endpoint:

```
GET /health
```

Returns `OK` with status 200 when the server is healthy.

## Authentication

When `MCP_API_KEY` is set, all requests must include the Bearer token:

```
Authorization: Bearer your_api_key
```

