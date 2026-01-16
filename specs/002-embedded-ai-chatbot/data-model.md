# Data Model: Embedded AI Chatbot

**Feature Branch**: `002-embedded-ai-chatbot`
**Date**: 2026-01-15
**Status**: Complete

## Overview

This document defines the data entities required for the embedded AI chatbot feature. These entities extend the existing Phase 2 data model without modifying existing tables.

## Existing Entities (Reference)

### User (existing)
```
- id: str (UUID, primary key)
- email: str (unique, indexed)
- password_hash: str
- created_at: datetime
- updated_at: datetime
```

### Task (existing)
```
- id: int (auto-increment, primary key)
- user_id: str (foreign key → user.id, indexed)
- title: str (required)
- description: Optional[str]
- completed: bool (default=False)
- priority: str (High|Medium|Low, default=Medium)
- tags: str (JSON string)
- created_at: datetime
- updated_at: datetime
```

## New Entities

### Conversation

Represents a chat session belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK, UUID | Unique conversation identifier |
| user_id | str | FK → user.id, indexed, NOT NULL | Owner of the conversation |
| title | str | Optional, max 100 chars | Auto-generated from first message |
| created_at | datetime | NOT NULL, default=now() | When conversation started |
| updated_at | datetime | NOT NULL, default=now() | Last activity timestamp |

**Indexes**:
- `idx_conversation_user_id` on `user_id` for efficient user lookup
- `idx_conversation_updated_at` on `updated_at` for sorting by recent activity

**Relationships**:
- Conversation belongs to User (many-to-one)
- Conversation has many Messages (one-to-many)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message

Represents a single message within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PK, auto-increment | Unique message identifier |
| conversation_id | str | FK → conversation.id, indexed, NOT NULL | Parent conversation |
| role | str | NOT NULL, enum: user\|assistant | Message author role |
| content | str | NOT NULL, max 10000 chars | Message text content |
| tool_calls | str | Optional, JSON | Tool invocations made (for assistant messages) |
| created_at | datetime | NOT NULL, default=now() | When message was created |

**Indexes**:
- `idx_message_conversation_id` on `conversation_id` for conversation message lookup
- `idx_message_created_at` on `created_at` for chronological ordering

**Relationships**:
- Message belongs to Conversation (many-to-one)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: MessageRole = Field(...)
    content: str = Field(max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

## API Schemas

### Request Schemas

**ChatRequest**:
```python
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
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
```

### Response Schemas

**ToolCallInfo**:
```python
class ToolCallInfo(BaseModel):
    tool_name: str
    arguments: dict
    result: dict
```

**ChatResponse**:
```python
from pydantic import BaseModel
from typing import List, Optional

class ChatResponse(BaseModel):
    conversation_id: str = Field(description="Conversation ID (new or existing)")
    message: str = Field(description="Assistant response text")
    tool_calls: Optional[List[ToolCallInfo]] = Field(
        default=None,
        description="Tool invocations made during processing"
    )
```

**ConversationRead**:
```python
class ConversationRead(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**MessageRead**:
```python
class MessageRead(BaseModel):
    id: int
    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCallInfo]]
    created_at: datetime

    class Config:
        from_attributes = True
```

## State Transitions

### Conversation Lifecycle

```
[New Request without conversation_id]
        │
        ▼
    ┌─────────┐
    │ Created │ ──── conversation created with first user message
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Active  │ ──── messages being exchanged
    └────┬────┘
         │
         ▼ (user starts new conversation)
    ┌──────────┐
    │ Archived │ ──── no longer the active conversation
    └──────────┘
```

Note: Conversations are never deleted; they remain in history.

### Message Flow

```
[User sends message]
        │
        ▼
    ┌──────────────┐
    │ User Message │ ──── role=user, stored immediately
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Agent Runs   │ ──── tool calls executed
    └──────┬───────┘
           │
           ▼
    ┌───────────────────┐
    │ Assistant Message │ ──── role=assistant, includes tool_calls
    └───────────────────┘
```

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| Conversation | user_id | Must reference existing user |
| Conversation | title | Max 100 characters |
| Message | conversation_id | Must reference existing conversation |
| Message | role | Must be "user" or "assistant" |
| Message | content | Non-empty, max 10000 characters |
| ChatRequest | message | Non-empty, max 2000 characters |

## Data Integrity

1. **Cascade Delete**: When a user is deleted, all their conversations and messages are deleted (handled by database cascade).

2. **Foreign Key Enforcement**: All foreign keys must reference existing records.

3. **Timestamps**: `created_at` is immutable; `updated_at` is modified on any change.

4. **Tool Calls JSON**: Stored as validated JSON string, parsed to `List[ToolCallInfo]` in API responses.

## Migration Notes

- New tables: `conversation`, `message`
- No changes to existing `user` or `task` tables
- SQLModel's `SQLModel.metadata.create_all()` handles table creation
- Alembic migration recommended for production deployments
