"""
API Endpoints for AI Chatbot

This module defines the API endpoints for the AI chatbot functionality,
including chat interactions and RAG integration.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..ai_agents.chatbot import ChatRequest, ChatResponse, get_ai_chatbot
from ..auth.jwt_handler import get_current_user

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
) -> ChatResponse:
    """
    Chat endpoint for interacting with the AI assistant.

    Args:
        request: ChatRequest containing user input and context
        current_user: Authenticated user making the request (as dict from JWT)

    Returns:
        ChatResponse with the AI's response
    """
    # Extract user ID from JWT payload and convert to string for RAG compatibility
    user_id = str(current_user.get("id", ""))
    request.user_id = user_id

    ai_chatbot = get_ai_chatbot()
    if not ai_chatbot:
        raise HTTPException(status_code=503, detail="AI chatbot service is not configured")

    try:
        response = await ai_chatbot.chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@router.get("/health")
async def chatbot_health() -> Dict[str, Any]:
    """
    Health check for the AI chatbot service.

    Returns:
        Health status information
    """
    ai_chatbot = get_ai_chatbot()

    status = {
        "chatbot_configured": ai_chatbot is not None,
        "rag_available": True  # We assume RAG is available if the client exists
    }

    if ai_chatbot:
        try:
            # Check if RAG service is reachable
            rag_healthy = await ai_chatbot.rag_client.health_check()
            status["rag_healthy"] = rag_healthy
        except Exception:
            status["rag_healthy"] = False

    return {"status": "healthy", "details": status}


@router.post("/query-tasks")
async def query_tasks_naturally(
    query: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Natural language query for user's tasks.

    Args:
        query: Natural language query about tasks
        current_user: Authenticated user making the request (as dict from JWT)

    Returns:
        Results of the task query
    """
    ai_chatbot = get_ai_chatbot()
    if not ai_chatbot:
        raise HTTPException(status_code=503, detail="AI chatbot service is not configured")

    try:
        user_id = str(current_user.get("id", ""))
        result = await ai_chatbot.query_tasks_via_chat(user_id, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing task query: {str(e)}")


@router.post("/create-task-via-chat")
async def create_task_via_chat(
    task_description: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a task using natural language description.

    Args:
        task_description: Natural language description of the task to create
        current_user: Authenticated user making the request (as dict from JWT)

    Returns:
        Result of the task creation
    """
    ai_chatbot = get_ai_chatbot()
    if not ai_chatbot:
        raise HTTPException(status_code=503, detail="AI chatbot service is not configured")

    try:
        user_id = str(current_user.get("id", ""))
        result = await ai_chatbot.add_task_via_chat(user_id, task_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")