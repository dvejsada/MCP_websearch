"""Centralized configuration for MCP Search server."""

import os
from functools import lru_cache
from typing import Literal


def _is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def _load_env() -> None:
    """Load environment variables from .env file in non-production."""
    if not _is_production():
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not installed, skip loading


# Load environment variables at module import (only in non-production)
_load_env()


class Config:
    """Application configuration loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Transport settings
    TRANSPORT: Literal["stdio", "http", "sse"] = os.getenv("MCP_TRANSPORT", "http")  # type: ignore
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))

    # Authentication
    API_KEY: str = os.getenv("MCP_API_KEY", "")

    # FastMCP settings
    LOG_LEVEL: str = os.getenv("FASTMCP_LOG_LEVEL", "INFO")
    MASK_ERROR_DETAILS: bool = os.getenv("FASTMCP_MASK_ERROR_DETAILS", "false").lower() == "true"
    STRICT_INPUT_VALIDATION: bool = os.getenv("FASTMCP_STRICT_INPUT_VALIDATION", "false").lower() == "true"
    INCLUDE_FASTMCP_META: bool = os.getenv("FASTMCP_INCLUDE_FASTMCP_META", "false").lower() == "true"

    # Duplicate handling
    ON_DUPLICATE_TOOLS: Literal["error", "warn", "replace"] = os.getenv("ON_DUPLICATE_TOOLS", "error")  # type: ignore
    ON_DUPLICATE_RESOURCES: Literal["error", "warn", "replace"] = os.getenv("ON_DUPLICATE_RESOURCES", "warn")  # type: ignore
    ON_DUPLICATE_PROMPTS: Literal["error", "warn", "replace"] = os.getenv("ON_DUPLICATE_PROMPTS", "replace")  # type: ignore

    # Serper.dev API
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get cached configuration instance."""
    return Config()
