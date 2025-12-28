"""
Unit tests for the TodoService.
"""
import pytest
from datetime import datetime
from src.services.todo_service import TodoService
from src.models.task import Task, Priority


class TestTodoService:
    """Test cases for the TodoService."""

    def test_add_task(self):
        """Test adding a new task."""
        service = TodoService()
        task_id = service.add_task("Test Task", "Test Description", "High", ["test", "python"])

        assert task_id == 1
        assert service.get_task(1) is not None
        assert service.get_task(1).title == "Test Task"
        assert service.get_task(1).description == "Test Description"
        assert service.get_task(1).priority == Priority.HIGH
        assert "test" in service.get_task(1).tags

    def test_add_task_with_defaults(self):
        """Test adding a task with default values."""
        service = TodoService()
        task_id = service.add_task("Test Task")

        assert task_id == 1
        task = service.get_task(1)
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.priority == Priority.MEDIUM
        assert task.tags == []

    def test_get_task(self):
        """Test retrieving a task by ID."""
        service = TodoService()
        task_id = service.add_task("Test Task")

        task = service.get_task(task_id)
        assert task is not None
        assert task.id == task_id
        assert task.title == "Test Task"

        # Test getting non-existent task
        assert service.get_task(999) is None

    def test_get_all_tasks(self):
        """Test retrieving all tasks."""
        service = TodoService()
        service.add_task("Task 1")
        service.add_task("Task 2")

        all_tasks = service.get_all_tasks()
        assert len(all_tasks) == 2
        # Tasks should be sorted by creation date (oldest first)
        assert all_tasks[0].title == "Task 1"
        assert all_tasks[1].title == "Task 2"

        # Test with empty service
        empty_service = TodoService()
        assert len(empty_service.get_all_tasks()) == 0

    def test_update_task(self):
        """Test updating an existing task."""
        service = TodoService()
        task_id = service.add_task("Original Title", "Original Description", "Low", ["original"])

        # Update the task
        success = service.update_task(
            task_id=task_id,
            title="Updated Title",
            description="Updated Description",
            priority="High",
            tags=["updated", "tags"]
        )

        assert success is True
        updated_task = service.get_task(task_id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == Priority.HIGH
        assert "updated" in updated_task.tags
        assert "tags" in updated_task.tags

        # Test updating non-existent task
        result = service.update_task(999, title="New Title")
        assert result is False

    def test_update_task_partial(self):
        """Test updating only some fields of a task."""
        service = TodoService()
        task_id = service.add_task("Original Title", "Original Description", "Low", ["original"])

        # Update only the title
        service.update_task(task_id=task_id, title="Updated Title")

        updated_task = service.get_task(task_id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"  # Should remain unchanged
        assert updated_task.priority == Priority.LOW  # Should remain unchanged
        assert updated_task.tags == ["original"]  # Should remain unchanged

    def test_delete_task(self):
        """Test deleting a task."""
        service = TodoService()
        task_id = service.add_task("Test Task")

        # Verify task exists
        assert service.get_task(task_id) is not None

        # Delete the task
        success = service.delete_task(task_id)
        assert success is True
        assert service.get_task(task_id) is None

        # Test deleting non-existent task
        result = service.delete_task(999)
        assert result is False

    def test_toggle_task_status(self):
        """Test toggling task completion status."""
        service = TodoService()
        task_id = service.add_task("Test Task")  # Default completed=False

        # Verify initial state (should be False by default)
        task = service.get_task(task_id)
        assert task.completed is False

        # Toggle status
        success = service.toggle_task_status(task_id)
        assert success is True

        # Verify updated state
        task = service.get_task(task_id)
        assert task.completed is True

        # Toggle again
        service.toggle_task_status(task_id)
        task = service.get_task(task_id)
        assert task.completed is False

        # Test toggling non-existent task
        result = service.toggle_task_status(999)
        assert result is False

    def test_search_tasks(self):
        """Test searching tasks."""
        service = TodoService()
        service.add_task("Python Project", "Learn Python", "High", ["python", "learning"])
        service.add_task("JavaScript Project", "Learn JavaScript", "Medium", ["javascript", "learning"])
        service.add_task("Other Task", "Something else", "Low", ["other"])

        # Search by title
        results = service.search_tasks("Python")
        assert len(results) == 1
        assert results[0].title == "Python Project"

        # Search by description
        results = service.search_tasks("JavaScript")
        assert len(results) == 1
        assert results[0].title == "JavaScript Project"

        # Search by tag
        results = service.search_tasks("learning")
        assert len(results) == 2
        titles = [task.title for task in results]
        assert "Python Project" in titles
        assert "JavaScript Project" in titles

        # Search with no matches
        results = service.search_tasks("nonexistent")
        assert len(results) == 0

        # Search with empty query
        results = service.search_tasks("")
        assert len(results) == 0

        # Search is case-insensitive
        results = service.search_tasks("python")
        assert len(results) == 1
        assert results[0].title == "Python Project"

    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status."""
        service = TodoService()
        # Add tasks (default is pending/completed=False)
        task1_id = service.add_task("Pending Task 1")
        task2_id = service.add_task("Pending Task 2")

        # Mark one task as completed
        service.add_task("Another Pending Task")  # task3_id
        service.toggle_task_status(task2_id)  # Mark task2 as completed

        # Filter by completed
        completed_tasks = service.filter_tasks(status="completed")
        assert len(completed_tasks) == 1
        assert completed_tasks[0].completed is True

        # Filter by pending
        pending_tasks = service.filter_tasks(status="pending")
        assert len(pending_tasks) == 2
        assert all(task.completed is False for task in pending_tasks)

        # Test invalid status
        with pytest.raises(ValueError, match="Status must be 'completed' or 'pending'"):
            service.filter_tasks(status="invalid")

    def test_filter_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        service = TodoService()
        service.add_task("High Priority", priority="High")
        service.add_task("Medium Priority", priority="Medium")
        service.add_task("Low Priority", priority="Low")

        # Filter by high priority
        high_tasks = service.filter_tasks(priority="High")
        assert len(high_tasks) == 1
        assert high_tasks[0].priority == Priority.HIGH

        # Filter by medium priority
        medium_tasks = service.filter_tasks(priority="Medium")
        assert len(medium_tasks) == 1
        assert medium_tasks[0].priority == Priority.MEDIUM

    def test_filter_tasks_by_tag(self):
        """Test filtering tasks by tag."""
        service = TodoService()
        service.add_task("Task 1", tags=["work", "urgent"])
        service.add_task("Task 2", tags=["personal", "fun"])
        service.add_task("Task 3", tags=["work", "meeting"])

        # Filter by tag
        work_tasks = service.filter_tasks(tag="work")
        assert len(work_tasks) == 2
        titles = [task.title for task in work_tasks]
        assert "Task 1" in titles
        assert "Task 3" in titles

    def test_filter_tasks_combined(self):
        """Test filtering tasks with multiple criteria."""
        service = TodoService()

        # Add tasks with different properties
        task1_id = service.add_task("Work Task", priority="High", tags=["work"])
        task2_id = service.add_task("Another Work Task", priority="High", tags=["work"])
        task3_id = service.add_task("Personal Task", priority="Low", tags=["personal"])

        # Mark some tasks as completed
        service.toggle_task_status(task1_id)  # Completed Work Task
        # task2_id remains pending
        service.toggle_task_status(task3_id)  # Completed Personal Task

        # Filter by status and priority
        results = service.filter_tasks(status="completed", priority="High")
        assert len(results) == 1
        assert results[0].title == "Work Task"

        # Filter by status and tag
        results = service.filter_tasks(status="completed", tag="personal")
        assert len(results) == 1
        assert results[0].title == "Personal Task"

    def test_sort_tasks_by_title(self):
        """Test sorting tasks by title."""
        service = TodoService()
        service.add_task("Zebra Task")
        service.add_task("Apple Task")
        service.add_task("Mango Task")

        # Sort by title ascending
        sorted_tasks = service.sort_tasks("title", "asc")
        titles = [task.title for task in sorted_tasks]
        assert titles == ["Apple Task", "Mango Task", "Zebra Task"]

        # Sort by title descending
        sorted_tasks = service.sort_tasks("title", "desc")
        titles = [task.title for task in sorted_tasks]
        assert titles == ["Zebra Task", "Mango Task", "Apple Task"]

    def test_sort_tasks_by_priority(self):
        """Test sorting tasks by priority."""
        service = TodoService()
        service.add_task("Low Priority Task", priority="Low")
        service.add_task("High Priority Task", priority="High")
        service.add_task("Medium Priority Task", priority="Medium")

        # Sort by priority ascending (High, Medium, Low in that order)
        sorted_tasks = service.sort_tasks("priority", "asc")
        priorities = [task.priority for task in sorted_tasks]
        # Ascending means High (0) first, then Medium (1), then Low (2)
        assert priorities == [Priority.HIGH, Priority.MEDIUM, Priority.LOW]

        # Sort by priority descending
        sorted_tasks = service.sort_tasks("priority", "desc")
        priorities = [task.priority for task in sorted_tasks]
        # Descending means Low (2) first, then Medium (1), then High (0)
        assert priorities == [Priority.LOW, Priority.MEDIUM, Priority.HIGH]

    def test_sort_tasks_by_created_at(self):
        """Test sorting tasks by creation date."""
        service = TodoService()
        task1_id = service.add_task("First Task")
        task2_id = service.add_task("Second Task")
        task3_id = service.add_task("Third Task")

        # Sort by creation date ascending (oldest first)
        sorted_tasks = service.sort_tasks("created_at", "asc")
        ids = [task.id for task in sorted_tasks]
        assert ids == [task1_id, task2_id, task3_id]

        # Sort by creation date descending (newest first)
        sorted_tasks = service.sort_tasks("created_at", "desc")
        ids = [task.id for task in sorted_tasks]
        assert ids == [task3_id, task2_id, task1_id]

    def test_sort_tasks_invalid_params(self):
        """Test sorting with invalid parameters."""
        service = TodoService()
        service.add_task("Test Task")

        # Invalid sort field
        with pytest.raises(ValueError, match="sort_by must be 'title', 'priority', or 'created_at'"):
            service.sort_tasks("invalid_field")

        # Invalid sort order
        with pytest.raises(ValueError, match="order must be 'asc' or 'desc'"):
            service.sort_tasks("title", "invalid_order")

    def test_get_task_count(self):
        """Test getting total task count."""
        service = TodoService()
        assert service.get_task_count() == 0

        service.add_task("Task 1")
        assert service.get_task_count() == 1

        service.add_task("Task 2")
        assert service.get_task_count() == 2

    def test_get_completed_task_count(self):
        """Test getting completed task count."""
        service = TodoService()
        task1_id = service.add_task("Task 1")  # Default pending
        task2_id = service.add_task("Task 2")  # Default pending
        task3_id = service.add_task("Task 3")  # Default pending

        # Mark tasks as completed
        service.toggle_task_status(task1_id)  # Mark as completed
        service.toggle_task_status(task3_id)  # Mark as completed
        # task2 remains pending

        assert service.get_completed_task_count() == 2

    def test_get_pending_task_count(self):
        """Test getting pending task count."""
        service = TodoService()
        task1_id = service.add_task("Task 1")  # Default pending
        task2_id = service.add_task("Task 2")  # Default pending
        task3_id = service.add_task("Task 3")  # Default pending

        # Mark one task as completed
        service.toggle_task_status(task1_id)  # Mark as completed
        # task2 and task3 remain pending

        assert service.get_pending_task_count() == 2

    def test_task_counts_consistency(self):
        """Test that task counts are consistent."""
        service = TodoService()
        task1_id = service.add_task("Task 1")  # Default pending
        task2_id = service.add_task("Task 2")  # Default pending
        task3_id = service.add_task("Task 3")  # Default pending
        task4_id = service.add_task("Task 4")  # Default pending

        # Mark some tasks as completed
        service.toggle_task_status(task1_id)  # Mark as completed
        service.toggle_task_status(task3_id)  # Mark as completed
        # task2 and task4 remain pending

        total = service.get_task_count()
        completed = service.get_completed_task_count()
        pending = service.get_pending_task_count()

        assert total == 4
        assert completed == 2
        assert pending == 2
        assert total == completed + pending