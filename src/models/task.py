"""
Task model for the console-based todo application.
Implements the Task entity with all required fields and validation as per the specification.
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Priority(Enum):
    """Priority levels for tasks."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Task:
    """
    Represents a single task in the todo application.

    Attributes:
        id: Unique identifier for the task
        title: Title of the task (1-255 characters)
        description: Optional description of the task (0-1000 characters)
        completed: Boolean indicating if the task is completed
        priority: Priority level (High, Medium, Low)
        tags: List of tags associated with the task
        created_at: Timestamp when the task was created
    """

    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False,
                 priority: Priority = Priority.MEDIUM, tags: List[str] = None, created_at: datetime = None):
        """
        Initialize a Task instance with validation.

        Args:
            task_id: Unique identifier for the task
            title: Title of the task (1-255 characters)
            description: Optional description (0-1000 characters)
            completed: Boolean indicating completion status
            priority: Priority level (High, Medium, Low)
            tags: List of tags (duplicates will be removed)
            created_at: Timestamp of creation (defaults to now if not provided)

        Raises:
            ValueError: If any validation fails
        """
        self.id = task_id
        self.title = self._validate_title(title)
        self.description = self._validate_description(description)
        self.completed = completed
        self.priority = self._validate_priority(priority)
        self.tags = self._validate_tags(tags or [])
        self.created_at = created_at or datetime.now()

    def _validate_title(self, title: str) -> str:
        """Validate the title according to specification (1-255 characters)."""
        if not isinstance(title, str):
            raise ValueError("Title must be a string")
        if len(title) < 1 or len(title) > 255:
            raise ValueError("Title must be between 1 and 255 characters")
        return title

    def _validate_description(self, description: str) -> str:
        """Validate the description according to specification (0-1000 characters)."""
        if not isinstance(description, str):
            raise ValueError("Description must be a string")
        if len(description) > 1000:
            raise ValueError("Description must be 1000 characters or less")
        return description

    def _validate_priority(self, priority: Priority) -> Priority:
        """Validate the priority is one of the allowed values."""
        if isinstance(priority, str):
            try:
                priority = Priority[priority.upper()]
            except KeyError:
                raise ValueError(f"Priority must be one of {list(Priority)}")
        elif not isinstance(priority, Priority):
            raise ValueError(f"Priority must be a Priority enum value")
        return priority

    def _validate_tags(self, tags: List[str]) -> List[str]:
        """Validate and clean tags (remove duplicates)."""
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list of strings")

        validated_tags = []
        seen = set()

        for tag in tags:
            if not isinstance(tag, str):
                raise ValueError("Each tag must be a string")
            # Remove duplicates by converting to lowercase for comparison
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                validated_tags.append(tag)

        return validated_tags

    def update_title(self, title: str):
        """Update the title with validation."""
        self.title = self._validate_title(title)

    def update_description(self, description: str):
        """Update the description with validation."""
        self.description = self._validate_description(description)

    def update_priority(self, priority: Priority):
        """Update the priority with validation."""
        self.priority = self._validate_priority(priority)

    def update_tags(self, tags: List[str]):
        """Update the tags with validation and duplicate removal."""
        self.tags = self._validate_tags(tags)

    def toggle_completion(self):
        """Toggle the completion status of the task."""
        self.completed = not self.completed

    def to_dict(self) -> dict:
        """Convert the task to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        """String representation of the task."""
        status = "✓" if self.completed else "○"
        return f"Task({status} {self.id}: {self.title} [{self.priority.value}] - {len(self.tags)} tags)"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Task):
            return False
        return self.id == other.id