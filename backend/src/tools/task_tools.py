# Task tools for AI chatbot agent
# Tools use @function_tool decorator from openai-agents SDK

from typing import Optional, List
from agents import function_tool
from pydantic import BaseModel, Field


class TaskCreatedResult(BaseModel):
    """Result of creating a task."""
    success: bool
    task_id: Optional[int] = None
    title: str
    message: str


class TaskListResult(BaseModel):
    """Result of listing tasks."""
    success: bool
    tasks: List[dict]
    count: int
    message: str


class TaskUpdateResult(BaseModel):
    """Result of updating a task."""
    success: bool
    task_id: Optional[int] = None
    message: str


class TaskDeleteResult(BaseModel):
    """Result of deleting a task."""
    success: bool
    message: str


# Note: These tools are called by the AI agent during conversation processing.
# The actual service calls are made in chat_service.py where we have access
# to the database session and user context.

# Tool definitions - these define the schema for the agent to use.
# The actual implementation is in chat_service.py which wraps these with DB access.

@function_tool
def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "Medium",
    tags: Optional[List[str]] = None,
) -> TaskCreatedResult:
    """
    Create a new task for the user.

    Args:
        title: The title of the task (required)
        description: Optional detailed description of the task
        priority: Task priority - must be "High", "Medium", or "Low" (default: Medium)
        tags: Optional list of tags to categorize the task

    Returns:
        TaskCreatedResult with success status and task details
    """
    # This is a placeholder - actual implementation is in chat_service.py
    # where we have access to user_id and database session
    return TaskCreatedResult(
        success=True,
        task_id=0,
        title=title,
        message=f"Task '{title}' created successfully"
    )


@function_tool
def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> TaskListResult:
    """
    List all tasks for the user with optional filters.

    Args:
        completed: Filter by completion status (True for completed, False for incomplete)
        priority: Filter by priority level ("High", "Medium", or "Low")
        tags: Filter by tags (tasks must have all specified tags)

    Returns:
        TaskListResult with list of tasks and count
    """
    # Placeholder - actual implementation in chat_service.py
    return TaskListResult(
        success=True,
        tasks=[],
        count=0,
        message="Tasks retrieved successfully"
    )


@function_tool
def complete_task(
    task_identifier: str,
) -> TaskUpdateResult:
    """
    Mark a task as complete.

    Args:
        task_identifier: The task ID (number) or partial title to match

    Returns:
        TaskUpdateResult with success status
    """
    # Placeholder - actual implementation in chat_service.py
    return TaskUpdateResult(
        success=True,
        task_id=0,
        message="Task marked as complete"
    )


@function_tool
def update_task(
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> TaskUpdateResult:
    """
    Update an existing task.

    Args:
        task_identifier: The task ID (number) or partial title to match
        title: New title for the task
        description: New description for the task
        priority: New priority ("High", "Medium", or "Low")
        tags: New list of tags (replaces existing tags)

    Returns:
        TaskUpdateResult with success status
    """
    # Placeholder - actual implementation in chat_service.py
    return TaskUpdateResult(
        success=True,
        task_id=0,
        message="Task updated successfully"
    )


@function_tool
def delete_task(
    task_identifier: str,
    confirmed: bool = False,
) -> TaskDeleteResult:
    """
    Delete a task. Requires confirmation.

    IMPORTANT: Always ask the user to confirm deletion before calling this tool.
    Only call this tool with confirmed=True after the user explicitly confirms.

    Args:
        task_identifier: The task ID (number) or partial title to match
        confirmed: Must be True to actually delete. If False, just returns a confirmation request.

    Returns:
        TaskDeleteResult with success status
    """
    # Placeholder - actual implementation in chat_service.py
    if not confirmed:
        return TaskDeleteResult(
            success=False,
            message="Please confirm you want to delete this task by saying 'yes' or 'confirm'"
        )
    return TaskDeleteResult(
        success=True,
        message="Task deleted successfully"
    )


# Export all tools for use in chat_service.py
__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "update_task",
    "delete_task",
    "TaskCreatedResult",
    "TaskListResult",
    "TaskUpdateResult",
    "TaskDeleteResult",
]
