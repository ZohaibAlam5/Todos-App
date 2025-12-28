"""
Integration tests for the CLI application flow.
"""
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from src.cli.main import TodoCLI
from src.models.task import Priority


class TestCLIIntegration:
    """Integration tests for the CLI application."""

    def setup_method(self):
        """Set up a fresh CLI instance for each test."""
        self.cli = TodoCLI()

    def test_add_and_view_task_flow(self):
        """Test the flow of adding a task and then viewing it."""
        # Add a task
        task_title = "Integration Test Task"
        task_description = "This is a test task for integration testing"
        task_priority = "High"
        task_tags = ["integration", "test"]

        # Mock user inputs for adding a task
        with patch('builtins.input', side_effect=[
            task_title,  # title
            task_description,  # description
            task_priority,  # priority
            ",".join(task_tags)  # tags
        ]):
            # Capture printed output
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.add_task()
                output = mock_stdout.getvalue()

        # Verify the task was added successfully
        assert "Task added successfully" in output

        # Now view all tasks to ensure the task appears
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_tasks()
                output = mock_stdout.getvalue()

        # Verify the task appears in the view
        assert task_title in output
        assert task_description in output
        for tag in task_tags:
            assert tag in output

    def test_add_update_delete_flow(self):
        """Test the flow of adding, updating, and deleting a task."""
        # Add a task
        original_title = "Original Title"
        with patch('builtins.input', side_effect=[original_title, "", "Medium", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.add_task()
                output = mock_stdout.getvalue()

        # Verify the task was added
        assert "Task added successfully" in output
        task_id = 1  # The first task should have ID 1

        # Update the task
        updated_title = "Updated Title"
        with patch('builtins.input', side_effect=[
            str(task_id),  # task ID to update
            updated_title,  # new title
            "",  # keep description empty
            "",  # keep priority unchanged
            ""   # keep tags unchanged
        ]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.update_task()
                output = mock_stdout.getvalue()

        assert "Task updated successfully" in output

        # Verify the task was updated by viewing it
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_tasks()
                output = mock_stdout.getvalue()

        assert updated_title in output
        assert original_title not in output  # Original title should not appear

        # Delete the task
        with patch('builtins.input', side_effect=[str(task_id)]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.delete_task()
                output = mock_stdout.getvalue()

        assert "deleted successfully" in output

        # Verify the task is gone by viewing all tasks
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_tasks()
                output = mock_stdout.getvalue()

        assert updated_title not in output

    def test_toggle_task_status_flow(self):
        """Test toggling task completion status."""
        # Add a task (initially not completed)
        task_title = "Toggle Test Task"
        with patch('builtins.input', side_effect=[task_title, "", "Medium", ""]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        # View tasks to confirm it's pending
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_tasks()
                output = mock_stdout.getvalue()

        # Task should be pending (○ symbol)
        assert "○" in output
        assert task_title in output

        # Toggle the task status to completed
        with patch('builtins.input', side_effect=["1"]):  # task ID 1
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.toggle_task_status()
                output = mock_stdout.getvalue()

        assert "updated to: completed" in output

        # View tasks again to confirm it's completed
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_tasks()
                output = mock_stdout.getvalue()

        # Task should now be completed (✓ symbol)
        assert "✓" in output
        assert task_title in output

        # Toggle back to pending
        with patch('builtins.input', side_effect=["1"]):  # task ID 1
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.toggle_task_status()
                output = mock_stdout.getvalue()

        assert "updated to: pending" in output

    def test_search_functionality(self):
        """Test the search functionality."""
        # Add multiple tasks with different characteristics
        with patch('builtins.input', side_effect=["Task 1", "Description with python keyword", "High", "python,work"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        with patch('builtins.input', side_effect=["Python Task", "Another description", "Low", "learning"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        with patch('builtins.input', side_effect=["Other Task", "Unrelated description", "Medium", "unrelated"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        # Search for tasks containing "python"
        with patch('builtins.input', side_effect=["python"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.search_tasks()
                output = mock_stdout.getvalue()

        # Should find at least one task with "python"
        assert "Found" in output
        assert "python" in output.lower() or "Python" in output

        # Search for tasks containing "learning"
        with patch('builtins.input', side_effect=["learning"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.search_tasks()
                output = mock_stdout.getvalue()

        assert "Found" in output
        assert "Python Task" in output

    def test_filter_functionality(self):
        """Test the filter functionality."""
        # Add tasks with different priorities and statuses
        with patch('builtins.input', side_effect=["High Priority Task", "", "High", "important"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        with patch('builtins.input', side_effect=["Low Priority Task", "", "Low", "later"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        # Mark the first task as completed
        with patch('builtins.input', side_effect=["1"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.toggle_task_status()

        # Filter by completed status
        with patch('builtins.input', side_effect=["completed", "", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.filter_tasks()
                output = mock_stdout.getvalue()

        assert "Found" in output
        assert "High Priority Task" in output

        # Filter by priority
        with patch('builtins.input', side_effect=["", "High", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.filter_tasks()
                output = mock_stdout.getvalue()

        assert "Found" in output
        assert "High Priority Task" in output

    def test_statistics_functionality(self):
        """Test the statistics functionality."""
        # Add some tasks
        with patch('builtins.input', side_effect=["Task 1", "", "High", "test"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        with patch('builtins.input', side_effect=["Task 2", "", "Low", "test"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.add_task()

        # Mark one task as completed
        with patch('builtins.input', side_effect=["1"]):
            with patch('sys.stdout', new_callable=StringIO):
                self.cli.toggle_task_status()

        # View statistics
        with patch('builtins.input', side_effect=[]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.view_statistics()
                output = mock_stdout.getvalue()

        # Verify statistics are displayed
        assert "Total Tasks:" in output
        assert "Completed Tasks:" in output
        assert "Pending Tasks:" in output
        assert "Completion Rate:" in output

        # Verify correct counts
        assert "Total Tasks: 2" in output
        assert "Completed Tasks: 1" in output
        assert "Pending Tasks: 1" in output

    def test_invalid_task_operations(self):
        """Test handling of invalid task operations."""
        # Try to update a non-existent task
        with patch('builtins.input', side_effect=["999", "New Title", "", "", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.update_task()
                output = mock_stdout.getvalue()

        assert "not found" in output.lower()

        # Try to delete a non-existent task
        with patch('builtins.input', side_effect=["999"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.delete_task()
                output = mock_stdout.getvalue()

        assert "not found" in output.lower()

        # Try to toggle status of a non-existent task
        with patch('builtins.input', side_effect=["999"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.toggle_task_status()
                output = mock_stdout.getvalue()

        assert "not found" in output.lower()

    def test_validation_errors_in_cli(self):
        """Test CLI handling of validation errors."""
        # Try to add a task with empty title (should fail validation)
        with patch('builtins.input', side_effect=["", "Description", "Medium", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.add_task()
                output = mock_stdout.getvalue()

        assert "Error:" in output
        assert "cannot be empty" in output.lower()

        # Try to add a task with invalid priority
        with patch('builtins.input', side_effect=["Valid Title", "Description", "InvalidPriority", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.add_task()
                output = mock_stdout.getvalue()

        assert "Error:" in output
        assert "priority" in output.lower()