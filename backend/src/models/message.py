from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel
import json

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class MessageRole(str, Enum):
    """Role of the message author."""
    user = "user"
    assistant = "assistant"


class Message(SQLModel, table=True):
    """Represents a single message within a conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: MessageRole = Field(...)
    content: str = Field(max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    @property
    def tool_calls_list(self) -> List[dict]:
        """Parse tool_calls JSON string to list of dicts."""
        if self.tool_calls:
            try:
                return json.loads(self.tool_calls)
            except json.JSONDecodeError:
                return []
        return []

    @tool_calls_list.setter
    def tool_calls_list(self, value: List[dict]):
        """Convert list of tool calls to JSON string."""
        self.tool_calls = json.dumps(value) if value else None


class ToolCallInfo(BaseModel):
    """Information about a tool invocation."""
    tool_name: str
    arguments: dict
    result: Optional[dict] = None


class MessageRead(SQLModel):
    """Read schema for Message API responses."""
    id: int
    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCallInfo]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
