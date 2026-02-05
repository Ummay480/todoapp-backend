"""
RAG Client Module for Todo AI Chatbot

This module provides a client interface to interact with the external
RAG Chatbot Engine via HTTP API calls.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class RAGQueryResponse(BaseModel):
    """Response model for RAG queries"""
    success: bool
    response: str
    sources: List[Dict[str, Any]]
    context_info: Dict[str, Any]


class RAGClient:
    """
    Client for interacting with the external RAG Chatbot Engine.

    This client provides methods to:
    - Query the RAG system for knowledge retrieval
    - Ingest documents into specific projects
    - Manage project-level data
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the RAG client.

        Args:
            base_url: Base URL of the RAG Chatbot Engine API
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)  # 30-second timeout for API calls

    async def close(self):
        """Close the HTTP client connection pool."""
        await self.client.aclose()

    async def query_project(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
        threshold: float = 0.3,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> RAGQueryResponse:
        """
        Query a specific project in the RAG system.

        Args:
            project_id: Unique identifier for the project/user
            query: The question/query to ask
            top_k: Number of top results to retrieve
            threshold: Similarity threshold for retrieval
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in the response

        Returns:
            RAGQueryResponse: The response from the RAG system
        """
        url = f"{self.base_url}/query"
        payload = {
            "project_id": project_id,
            "query": query,
            "top_k": top_k,
            "threshold": threshold,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            return RAGQueryResponse(**data)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while querying RAG: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while querying RAG: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred while querying RAG: {str(e)}")
            raise

    async def ingest_text(
        self,
        project_id: str,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest text content into a specific project.

        Args:
            project_id: Unique identifier for the project/user
            text_content: Text content to ingest
            metadata: Optional metadata to associate with the content

        Returns:
            Dict containing ingestion result
        """
        url = f"{self.base_url}/ingest"
        payload = {
            "project_id": project_id,
            "text_content": text_content,
            "metadata": metadata or {}
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while ingesting text: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while ingesting text: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred while ingesting text: {str(e)}")
            raise

    async def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific project.

        Args:
            project_id: Unique identifier for the project/user

        Returns:
            Dict containing project statistics
        """
        url = f"{self.base_url}/stats/{project_id}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while getting project stats: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while getting project stats: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting project stats: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the RAG service is healthy.

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


# Global RAG client instance
_rag_client: Optional[RAGClient] = None


def get_rag_client() -> RAGClient:
    """
    Get the global RAG client instance.

    Returns:
        RAGClient instance
    """
    global _rag_client
    if _rag_client is None:
        # Get base URL from environment or use default
        import os
        rag_base_url = os.getenv("RAG_ENGINE_URL", "http://localhost:8000")
        _rag_client = RAGClient(base_url=rag_base_url)
    return _rag_client