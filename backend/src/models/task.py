from sqlmodel import SQLModel, Field
from sqlalchemy import String
from typing import Optional, List
from datetime import datetime
from enum import Enum
import json

class PriorityEnum(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(sa_type=String, default="Medium")

class TaskCreateBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(sa_type=String, default="Medium")

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    priority: str = Field(sa_type=String, default="Medium")  # Override to ensure string type
    tags: Optional[str] = Field(default=None)  # Store as JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def tags_list(self) -> List[str]:
        """Convert stored JSON string to list of tags"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except json.JSONDecodeError:
                return []
        return []

    @tags_list.setter
    def tags_list(self, tags: List[str]):
        """Convert list of tags to JSON string for storage"""
        self.tags = json.dumps(tags) if tags else "[]"

class TaskCreate(TaskCreateBase):
    tags: Optional[List[str]] = None

class TaskRead(TaskBase):
    id: int
    user_id: str
    tags: List[str]  # Return as list, not string
    created_at: datetime
    updated_at: datetime

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None