"""
MCP (Model Context Protocol) Client for Todo Application

This module provides a client interface to interact with MCP tools
for enhanced task management capabilities.
"""

import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import httpx

logger = logging.getLogger(__name__)


class MCPCallResult(BaseModel):
    """Result of an MCP call"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPClient:
    """
    Client for interacting with Model Context Protocol (MCP) tools.

    This client provides methods to:
    - Call MCP tools for task management
    - Handle context exchange with external tools
    """

    def __init__(self, base_url: str = "http://localhost:3000/mcp"):
        """
        Initialize the MCP client.

        Args:
            base_url: Base URL of the MCP service
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)  # 30-second timeout for API calls

    async def close(self):
        """Close the HTTP client connection pool."""
        await self.client.aclose()

    async def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        user_id: str
    ) -> MCPCallResult:
        """
        Call an MCP tool with the specified parameters.

        Args:
            tool_name: Name of the MCP tool to call
            params: Parameters for the tool
            user_id: User ID for context and isolation

        Returns:
            MCPCallResult: Result of the tool call
        """
        url = f"{self.base_url}/call"
        payload = {
            "tool": tool_name,
            "params": params,
            "context": {
                "user_id": user_id
            }
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            return MCPCallResult(success=True, data=data)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while calling MCP tool {tool_name}: {e.response.status_code} - {e.response.text}")
            return MCPCallResult(success=False, error=str(e))
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while calling MCP tool {tool_name}: {str(e)}")
            return MCPCallResult(success=False, error=str(e))
        except Exception as e:
            logger.error(f"Unexpected error occurred while calling MCP tool {tool_name}: {str(e)}")
            return MCPCallResult(success=False, error=str(e))

    async def get_available_tools(self) -> MCPCallResult:
        """
        Get list of available MCP tools.

        Returns:
            MCPCallResult: Result containing available tools
        """
        url = f"{self.base_url}/tools"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return MCPCallResult(success=True, data=data)
        except Exception as e:
            logger.error(f"Error getting available MCP tools: {str(e)}")
            return MCPCallResult(success=False, error=str(e))

    async def health_check(self) -> bool:
        """
        Check if the MCP service is healthy.

        Returns:
            True if the service is healthy, False otherwise
        """
        url = f"{self.base_url}/health"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return data.get("status") == "healthy"
        except:
            return False


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """
    Get the global MCP client instance.

    Returns:
        MCPClient instance
    """
    global _mcp_client
    if _mcp_client is None:
        # Get base URL from environment or use default
        import os
        mcp_base_url = os.getenv("MCP_BASE_URL", "http://localhost:3000/mcp")
        _mcp_client = MCPClient(base_url=mcp_base_url)
    return _mcp_client