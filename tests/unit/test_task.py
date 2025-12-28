"""
Unit tests for the Task model.
"""
import pytest
from datetime import datetime
from src.models.task import Task, Priority


class TestTask:
    """Test cases for the Task model."""

    def test_task_creation_with_valid_data(self):
        """Test creating a task with valid data."""
        task = Task(
            task_id=1,
            title="Test Task",
            description="Test Description",
            completed=False,
            priority=Priority.MEDIUM,
            tags=["test", "python"]
        )

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert task.priority == Priority.MEDIUM
        assert task.tags == ["test", "python"]
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_defaults(self):
        """Test creating a task with default values."""
        task = Task(task_id=1, title="Test Task")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.completed is False
        assert task.priority == Priority.MEDIUM
        assert task.tags == []
        assert isinstance(task.created_at, datetime)

    def test_title_validation_min_length(self):
        """Test title validation for minimum length."""
        with pytest.raises(ValueError, match="Title must be between 1 and 255 characters"):
            Task(task_id=1, title="")

    def test_title_validation_max_length(self):
        """Test title validation for maximum length."""
        long_title = "t" * 256
        with pytest.raises(ValueError, match="Title must be between 1 and 255 characters"):
            Task(task_id=1, title=long_title)

    def test_description_validation_max_length(self):
        """Test description validation for maximum length."""
        long_description = "d" * 1001
        with pytest.raises(ValueError, match="Description must be 1000 characters or less"):
            Task(task_id=1, title="Test", description=long_description)

    def test_priority_validation(self):
        """Test priority validation."""
        # Test valid priorities
        for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            task = Task(task_id=1, title="Test", priority=priority)
            assert task.priority == priority

        # Test invalid priority type
        with pytest.raises(ValueError):
            Task(task_id=1, title="Test", priority="Invalid")

    def test_tags_validation_and_deduplication(self):
        """Test tags validation and duplicate removal."""
        task = Task(task_id=1, title="Test", tags=["test", "python", "test", "TEST"])
        # Should remove duplicates (case-insensitive)
        assert len(task.tags) == 2
        assert "test" in task.tags
        assert "python" in task.tags

    def test_update_title(self):
        """Test updating task title."""
        task = Task(task_id=1, title="Original Title")
        task.update_title("New Title")

        assert task.title == "New Title"

    def test_update_description(self):
        """Test updating task description."""
        task = Task(task_id=1, title="Test", description="Original Description")
        task.update_description("New Description")

        assert task.description == "New Description"

    def test_update_priority(self):
        """Test updating task priority."""
        task = Task(task_id=1, title="Test", priority=Priority.LOW)
        task.update_priority(Priority.HIGH)

        assert task.priority == Priority.HIGH

    def test_update_tags(self):
        """Test updating task tags."""
        task = Task(task_id=1, title="Test", tags=["original"])
        task.update_tags(["new", "tags", "new"])

        assert len(task.tags) == 2
        assert "new" in task.tags
        assert "tags" in task.tags

    def test_toggle_completion(self):
        """Test toggling task completion status."""
        task = Task(task_id=1, title="Test", completed=False)
        assert task.completed is False

        task.toggle_completion()
        assert task.completed is True

        task.toggle_completion()
        assert task.completed is False

    def test_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(task_id=1, title="Test", description="Desc", completed=True, priority=Priority.HIGH, tags=["tag"])
        task_dict = task.to_dict()

        assert task_dict["id"] == 1
        assert task_dict["title"] == "Test"
        assert task_dict["description"] == "Desc"
        assert task_dict["completed"] is True
        assert task_dict["priority"] == "High"
        assert task_dict["tags"] == ["tag"]
        assert "created_at" in task_dict

    def test_repr(self):
        """Test string representation of task."""
        task = Task(task_id=1, title="Test", completed=True)
        repr_str = repr(task)

        assert "✓" in repr_str  # Completed task
        assert "1" in repr_str   # Task ID
        assert "Test" in repr_str  # Task title

        task.completed = False
        repr_str = repr(task)
        assert "○" in repr_str  # Pending task

    def test_equality(self):
        """Test task equality comparison."""
        task1 = Task(task_id=1, title="Test")
        task2 = Task(task_id=1, title="Different")
        task3 = Task(task_id=2, title="Test")

        assert task1 == task2  # Same ID means equal
        assert task1 != task3  # Different ID means not equal
        assert task1 != "not a task"  # Different type means not equal