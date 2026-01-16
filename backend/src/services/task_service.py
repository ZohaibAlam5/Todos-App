from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.models.user import User
import json


class TaskService:
    """Service for task operations, used by both REST API and AI agent tools."""

    def __init__(self, db: Session):
        self.db = db

    def get_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TaskRead]:
        """Get all tasks for a user with optional filters."""
        statement = select(Task).where(Task.user_id == user_id)

        tasks = self.db.exec(statement).all()

        # Apply filters in-memory (could optimize with SQL for large datasets)
        result = []
        for task in tasks:
            # Filter by completed status
            if completed is not None and task.completed != completed:
                continue

            # Filter by priority
            if priority is not None and task.priority != priority:
                continue

            # Filter by tags (must contain all specified tags)
            if tags is not None:
                task_tags = task.tags_list
                if not all(tag in task_tags for tag in tags):
                    continue

            # Convert to TaskRead format
            task_dict = task.model_dump()
            task_dict["tags"] = task.tags_list
            task_dict["priority"] = task.priority
            result.append(TaskRead(**task_dict))

        return result

    def get_task_by_id(self, user_id: str, task_id: int) -> Optional[TaskRead]:
        """Get a specific task by ID for a user."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(statement).first()

        if not task:
            return None

        task_dict = task.model_dump()
        task_dict["tags"] = task.tags_list
        task_dict["priority"] = task.priority
        return TaskRead(**task_dict)

    def find_task_by_title(self, user_id: str, title_query: str) -> Optional[Task]:
        """Find a task by partial title match for a user."""
        statement = select(Task).where(Task.user_id == user_id)
        tasks = self.db.exec(statement).all()

        # Case-insensitive partial match
        title_lower = title_query.lower()
        for task in tasks:
            if title_lower in task.title.lower():
                return task

        return None

    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "Medium",
        tags: Optional[List[str]] = None,
    ) -> TaskRead:
        """Create a new task for a user."""
        # Validate priority
        if priority not in ["High", "Medium", "Low"]:
            raise ValueError(f"Invalid priority: {priority}. Must be High, Medium, or Low.")

        # Create the task
        db_task = Task(
            title=title,
            description=description,
            completed=False,
            priority=priority,
            tags=json.dumps(tags) if tags else "[]",
            user_id=user_id,
        )

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        # Convert to TaskRead format
        task_dict = db_task.model_dump()
        task_dict["tags"] = db_task.tags_list
        task_dict["priority"] = db_task.priority
        return TaskRead(**task_dict)

    def update_task(
        self,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        completed: Optional[bool] = None,
    ) -> Optional[TaskRead]:
        """Update a task for a user."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = self.db.exec(statement).first()

        if not db_task:
            return None

        # Update fields if provided
        if title is not None:
            db_task.title = title
        if description is not None:
            db_task.description = description
        if priority is not None:
            if priority not in ["High", "Medium", "Low"]:
                raise ValueError(f"Invalid priority: {priority}. Must be High, Medium, or Low.")
            db_task.priority = priority
        if tags is not None:
            db_task.tags = json.dumps(tags)
        if completed is not None:
            db_task.completed = completed

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        # Convert to TaskRead format
        task_dict = db_task.model_dump()
        task_dict["tags"] = db_task.tags_list
        task_dict["priority"] = db_task.priority
        return TaskRead(**task_dict)

    def toggle_completion(self, user_id: str, task_id: int) -> Optional[TaskRead]:
        """Toggle the completion status of a task."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = self.db.exec(statement).first()

        if not db_task:
            return None

        db_task.completed = not db_task.completed

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        # Convert to TaskRead format
        task_dict = db_task.model_dump()
        task_dict["tags"] = db_task.tags_list
        task_dict["priority"] = db_task.priority
        return TaskRead(**task_dict)

    def delete_task(self, user_id: str, task_id: int) -> bool:
        """Delete a task for a user. Returns True if deleted, False if not found."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = self.db.exec(statement).first()

        if not db_task:
            return False

        self.db.delete(db_task)
        self.db.commit()
        return True
