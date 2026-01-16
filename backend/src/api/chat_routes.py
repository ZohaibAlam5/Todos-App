from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from src.database.database import get_db
from src.models.user import User
from src.models.message import MessageRole, MessageRead, ToolCallInfo
from src.models.conversation import ConversationRead
from src.middleware.auth_middleware import get_current_active_user
from src.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Request/Response schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. If omitted, creates new conversation."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message text"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: str = Field(description="Conversation ID (new or existing)")
    message: MessageRead = Field(description="Assistant response message")
    tool_calls: Optional[List[ToolCallInfo]] = Field(
        default=None,
        description="Tool invocations made during processing"
    )


class ConversationWithMessages(ConversationRead):
    """Conversation with its messages."""
    messages: List[MessageRead] = []


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Send a chat message to the AI assistant.

    Creates a new conversation if conversation_id is not provided.
    Returns the assistant's response along with any tool invocations.
    """
    chat_service = ChatService(db)

    try:
        # Process the message through the AI agent
        result = await chat_service.process_message(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
        )

        # Get the assistant message from the database
        messages = chat_service.get_messages(
            conversation_id=result.conversation_id,
            user_id=current_user.id,
            limit=1,
            offset=0,
        )

        # Get the most recent message (assistant response)
        recent_messages = chat_service.get_recent_messages(
            conversation_id=result.conversation_id,
            user_id=current_user.id,
            count=1,
        )

        if not recent_messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve assistant response."
            )

        assistant_message = recent_messages[-1]

        return ChatResponse(
            conversation_id=result.conversation_id,
            message=assistant_message,
            tool_calls=result.tool_calls if result.tool_calls else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service is temporarily unavailable. Please try again later or use the traditional task interface. Error: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationRead])
def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all conversations for the current user."""
    chat_service = ChatService(db)
    return chat_service.get_user_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific conversation with its messages."""
    chat_service = ChatService(db)

    conversation = chat_service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = chat_service.get_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=100,  # Get up to 100 messages per conversation
    )

    return ConversationWithMessages(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages,
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific conversation and all its messages."""
    chat_service = ChatService(db)

    deleted = chat_service.delete_conversation(conversation_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {"message": "Conversation deleted successfully"}
