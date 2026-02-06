"""
AI Agent for Todo Application with MCP Integration

This module implements the AI chatbot functionality that integrates with both
the RAG engine for knowledge retrieval and MCP (Model Context Protocol) tools
for enhanced task management capabilities.
"""

import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from openai import AsyncOpenAI
import logging
from app.services.rag_client import get_rag_client, RAGQueryResponse

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Represents a chat message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str


class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    user_id: str
    messages: List[ChatMessage]
    use_rag: bool = True  # Whether to use RAG for knowledge retrieval
    rag_threshold: float = 0.5  # Threshold for RAG relevance


class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    response: str
    sources: List[Dict[str, Any]] = []
    context_used: bool = False  # Whether RAG context was used


class TodoAIChatbot:
    """
    AI Chatbot for the Todo application with RAG and MCP integration.

    The chatbot can:
    - Answer general questions using RAG for knowledge retrieval
    - Interact with task management features through MCP tools
    - Leverage MCP tools for enhanced functionality
    """

    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the AI Chatbot.

        Args:
            openai_api_key: OpenAI API key for language model access
            model: The OpenAI model to use for responses
        """
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model
        self.rag_client = get_rag_client()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request and return a response.

        Args:
            request: ChatRequest containing user input and context

        Returns:
            ChatResponse with the AI's response and any sources used
        """
        # Determine if we should use RAG for this query
        should_use_rag = request.use_rag and await self._should_query_rag(request.messages[-1].content)

        rag_response: Optional[RAGQueryResponse] = None
        sources: List[Dict[str, Any]] = []

        if should_use_rag:
            try:
                # Use the user ID directly as project ID for RAG isolation
                project_id = request.user_id

                # Query the RAG system
                rag_response = await self.rag_client.query_project(
                    project_id=project_id,
                    query=request.messages[-1].content,
                    threshold=request.rag_threshold
                )

                if rag_response.success:
                    sources = rag_response.sources
                else:
                    logger.warning(f"RAG query failed: {rag_response}")
            except Exception as e:
                logger.error(f"Error querying RAG system: {str(e)}")
                # Continue without RAG if it fails

        # Prepare context for the language model
        context_messages = self._prepare_context_messages(
            request.messages,
            rag_response.response if rag_response and rag_response.success else None
        )

        # Generate response using the language model
        response = await self._generate_response(context_messages)

        return ChatResponse(
            response=response,
            sources=sources,
            context_used=bool(rag_response and rag_response.success)
        )

    async def _should_query_rag(self, user_message: str) -> bool:
        """
        Determine if the user's message should trigger a RAG query.

        Args:
            user_message: The user's message

        Returns:
            True if RAG should be queried, False otherwise
        """
        # Simple heuristic: if the message contains certain keywords or seems knowledge-seeking
        knowledge_keywords = [
            'what is', 'how do', 'explain', 'tell me about', 'define',
            'information about', 'details on', 'can you help', 'where can i',
            'when', 'why', 'how to', 'guide', 'tutorial', 'instructions'
        ]

        lower_msg = user_message.lower()
        return any(keyword in lower_msg for keyword in knowledge_keywords)

    def _prepare_context_messages(
        self,
        original_messages: List[ChatMessage],
        rag_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for the language model, incorporating RAG context if available.

        Args:
            original_messages: Original conversation messages
            rag_context: Context retrieved from RAG system

        Returns:
            List of messages formatted for the language model
        """
        prepared_messages = []

        # Add system message with context about the todo application
        system_message = {
            "role": "system",
            "content": (
                "You are an AI assistant for a Todo application. "
                "You can help users manage their tasks, answer questions about features, "
                "and provide general assistance. If you have specific knowledge context provided, "
                "use it to answer the user's question. Otherwise, provide general assistance "
                "related to task management and productivity."
            )
        }
        prepared_messages.append(system_message)

        # Add RAG context if available
        if rag_context:
            context_message = {
                "role": "system",
                "content": f"Knowledge context: {rag_context}"
            }
            prepared_messages.append(context_message)

        # Add original conversation history
        for msg in original_messages:
            prepared_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return prepared_messages

    async def _generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response using the language model.

        Args:
            messages: Formatted messages for the language model

        Returns:
            Generated response string
        """
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

    async def add_task_via_chat(self, user_id: str, task_description: str) -> Dict[str, Any]:
        """
        Helper method to create a task based on natural language description.

        Args:
            user_id: The user's ID
            task_description: Natural language description of the task

        Returns:
            Result of the task creation
        """
        # This would typically call an MCP tool or API to create a task
        # For now, returning a placeholder - in real implementation,
        # this would interface with MCP tools
        return {
            "success": True,
            "message": f"Task '{task_description}' would be created for user {user_id} via MCP tools",
            "task_description": task_description
        }

    async def query_tasks_via_chat(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Helper method to query user's tasks based on natural language.

        Args:
            user_id: The user's ID
            query: Natural language query about tasks

        Returns:
            Result of the task query
        """
        # This would typically call an MCP tool or API to query tasks
        # For now, returning a placeholder - in real implementation,
        # this would interface with MCP tools
        return {
            "success": True,
            "message": f"Query '{query}' about tasks for user {user_id} would be processed via MCP tools",
            "query": query
        }


# Global AI chatbot instance
_ai_chatbot: Optional[TodoAIChatbot] = None


def get_ai_chatbot() -> Optional[TodoAIChatbot]:
    """
    Get the global AI chatbot instance.

    Returns:
        TodoAIChatbot instance or None if not configured
    """
    global _ai_chatbot
    if _ai_chatbot is None:
        import os
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            _ai_chatbot = TodoAIChatbot(openai_api_key=openai_api_key, model=model)
        else:
            logger.warning("OpenAI API key not found. AI chatbot will not be available.")
    return _ai_chatbot