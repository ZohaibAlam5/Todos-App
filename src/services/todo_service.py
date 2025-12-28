"""
Todo service for the console-based todo application.
Implements the business logic for managing tasks with in-memory storage.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.task import Task, Priority
from ..lib.logger import log_info, log_error, log_debug
from ..lib.errors import TaskNotFoundError, ValidationError, StorageError
from ..lib.config import config
import re


class TodoService:
    """
    Service class that handles all business logic for managing tasks.
    Uses in-memory storage for task persistence during application runtime.
    """

    def __init__(self):
        """Initialize the todo service with empty storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
        log_info("TodoService initialized")

    def _generate_id(self) -> int:
        """Generate a unique ID for a new task."""
        # Check if we've reached the maximum number of tasks
        if len(self._tasks) >= config.max_tasks:
            raise StorageError(f"Maximum number of tasks ({config.max_tasks}) reached")

        new_id = self._next_id
        self._next_id += 1
        # Ensure the ID is not already in use
        while new_id in self._tasks:
            new_id = self._next_id
            self._next_id += 1
        return new_id

    def add_task(self, title: str, description: str = "", priority: str = "Medium", tags: List[str] = None) -> int:
        """
        Add a new task to the storage.

        Args:
            title: Title of the task (1-255 characters)
            description: Optional description (0-1000 characters)
            priority: Priority level as string ("High", "Medium", "Low")
            tags: List of tags (duplicates will be removed)

        Returns:
            int: The ID of the newly created task

        Raises:
            ValueError: If validation fails
        """
        log_debug(f"Adding new task: title='{title}', priority='{priority}'")

        # Validate priority string and convert to Priority enum
        priority_enum = self._validate_priority_string(priority)

        # Create a new task with a unique ID
        task_id = self._generate_id()
        new_task = Task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority_enum,
            tags=tags or []
        )

        # Store the task
        self._tasks[task_id] = new_task
        log_info(f"Task added successfully with ID: {task_id}")
        return task_id

    def _validate_priority_string(self, priority: str) -> Priority:
        """Validate and convert priority string to Priority enum."""
        if not isinstance(priority, str):
            raise ValueError("Priority must be a string")

        priority_upper = priority.strip().upper()
        if priority_upper == "HIGH":
            return Priority.HIGH
        elif priority_upper == "MEDIUM":
            return Priority.MEDIUM
        elif priority_upper == "LOW":
            return Priority.LOW
        else:
            raise ValueError(f"Priority must be one of 'High', 'Medium', 'Low' (case-insensitive)")

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        log_debug(f"Retrieving task with ID: {task_id}")
        task = self._tasks.get(task_id)
        if task:
            log_debug(f"Task found: {task.title}")
        else:
            log_debug(f"Task with ID {task_id} not found")
        return task

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks sorted by creation date (oldest first)
        """
        return sorted(self._tasks.values(), key=lambda task: task.created_at)

    def update_task(self, task_id: int, title: str = None, description: str = None,
                    priority: str = None, tags: List[str] = None) -> bool:
        """
        Update an existing task.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority as string (optional)
            tags: New tags (optional)

        Returns:
            bool: True if update was successful, False if task not found
        """
        log_debug(f"Updating task with ID: {task_id}")

        task = self.get_task(task_id)
        if not task:
            log_error(f"Task with ID {task_id} not found for update")
            return False

        # Update fields if provided
        if title is not None:
            log_debug(f"Updating title from '{task.title}' to '{title}'")
            task.update_title(title)
        if description is not None:
            log_debug(f"Updating description")
            task.update_description(description)
        if priority is not None:
            log_debug(f"Updating priority from '{task.priority.value}' to '{priority}'")
            priority_enum = self._validate_priority_string(priority)
            task.update_priority(priority_enum)
        if tags is not None:
            log_debug(f"Updating tags from {task.tags} to {tags}")
            task.update_tags(tags)

        log_info(f"Task with ID {task_id} updated successfully")
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            bool: True if deletion was successful, False if task not found
        """
        log_debug(f"Deleting task with ID: {task_id}")

        if task_id in self._tasks:
            task_title = self._tasks[task_id].title
            del self._tasks[task_id]
            log_info(f"Task '{task_title}' with ID {task_id} deleted successfully")
            return True
        else:
            log_error(f"Task with ID {task_id} not found for deletion")
            return False

    def toggle_task_status(self, task_id: int) -> bool:
        """
        Toggle the completion status of a task.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            bool: True if toggle was successful, False if task not found
        """
        log_debug(f"Toggling status for task with ID: {task_id}")

        task = self.get_task(task_id)
        if task:
            old_status = task.completed
            task.toggle_completion()
            new_status = task.completed
            status_text = "completed" if new_status else "pending"
            log_info(f"Task '{task.title}' status changed from {not new_status} to {new_status} ({status_text})")
            return True
        else:
            log_error(f"Task with ID {task_id} not found for status toggle")
            return False

    def search_tasks(self, query: str) -> List[Task]:
        """
        Search tasks by query string matching title, description, and tags.

        Args:
            query: The search query string

        Returns:
            List of tasks that match the query (case-insensitive)
        """
        log_debug(f"Searching tasks with query: '{query}'")

        if not query:
            log_debug("Empty query provided, returning empty list")
            return []

        query_lower = query.lower()
        matching_tasks = []

        for task in self._tasks.values():
            # Check title
            if query_lower in task.title.lower():
                matching_tasks.append(task)
                continue

            # Check description
            if query_lower in task.description.lower():
                matching_tasks.append(task)
                continue

            # Check tags
            for tag in task.tags:
                if query_lower in tag.lower():
                    matching_tasks.append(task)
                    break

        log_info(f"Search with query '{query}' returned {len(matching_tasks)} matching tasks")
        return matching_tasks

    def filter_tasks(self, status: str = None, priority: str = None, tag: str = None) -> List[Task]:
        """
        Filter tasks by specified criteria.

        Args:
            status: Filter by status ("completed", "pending")
            priority: Filter by priority ("High", "Medium", "Low")
            tag: Filter by specific tag

        Returns:
            List of tasks that match all specified criteria

        Raises:
            ValueError: If status is not 'completed' or 'pending'
        """
        log_debug(f"Filtering tasks - status: {status}, priority: {priority}, tag: {tag}")

        # Start with all tasks
        filtered_tasks = list(self._tasks.values())

        # Filter by status
        if status:
            status_lower = status.lower()
            if status_lower == "completed":
                filtered_tasks = [task for task in filtered_tasks if task.completed]
            elif status_lower == "pending":
                filtered_tasks = [task for task in filtered_tasks if not task.completed]
            else:
                error_msg = "Status must be 'completed' or 'pending'"
                log_error(error_msg)
                raise ValueError(error_msg)

        # Filter by priority
        if priority:
            priority_enum = self._validate_priority_string(priority)
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority_enum]

        # Filter by tag
        if tag:
            tag_lower = tag.lower()
            filtered_tasks = [
                task for task in filtered_tasks
                if any(tag_lower == t.lower() for t in task.tags)
            ]

        log_info(f"Filtering returned {len(filtered_tasks)} tasks")
        return filtered_tasks

    def sort_tasks(self, sort_by: str, order: str = "asc") -> List[Task]:
        """
        Sort tasks by specified field and order.

        Args:
            sort_by: Field to sort by ("title", "priority", "created_at")
            order: Sort order ("asc", "desc")

        Returns:
            List of tasks sorted according to criteria
        """
        log_debug(f"Sorting tasks by '{sort_by}' in {order} order")

        if sort_by not in ["title", "priority", "created_at"]:
            error_msg = "sort_by must be 'title', 'priority', or 'created_at'"
            log_error(error_msg)
            raise ValueError(error_msg)

        if order.lower() not in ["asc", "desc"]:
            error_msg = "order must be 'asc' or 'desc'"
            log_error(error_msg)
            raise ValueError(error_msg)

        # Get all tasks to sort
        filtered_tasks = list(self._tasks.values())

        # Define sort key function based on sort_by parameter
        if sort_by == "title":
            key_func = lambda task: task.title.lower()
        elif sort_by == "priority":
            # Sort by priority with High > Medium > Low
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            key_func = lambda task: priority_order[task.priority]
        elif sort_by == "created_at":
            key_func = lambda task: task.created_at

        reverse = order.lower() == "desc"
        sorted_tasks = sorted(filtered_tasks, key=key_func, reverse=reverse)

        log_info(f"Sorted {len(sorted_tasks)} tasks by '{sort_by}' in {order} order")
        return sorted_tasks

    def get_task_count(self) -> int:
        """
        Get the total number of tasks.

        Returns:
            int: Total number of tasks
        """
        return len(self._tasks)

    def get_completed_task_count(self) -> int:
        """
        Get the number of completed tasks.

        Returns:
            int: Number of completed tasks
        """
        return sum(1 for task in self._tasks.values() if task.completed)

    def get_pending_task_count(self) -> int:
        """
        Get the number of pending tasks.

        Returns:
            int: Number of pending tasks
        """
        return sum(1 for task in self._tasks.values() if not task.completed)