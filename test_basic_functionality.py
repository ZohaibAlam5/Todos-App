"""
Basic functionality test for the Console-Based Todo Application.
This script tests the core functionality without requiring user input.
"""
from src.services.todo_service import TodoService
from src.models.task import Priority


def test_basic_functionality():
    """Test basic todo functionality."""
    print("Testing basic todo functionality...")

    # Create a todo service instance
    service = TodoService()

    # Test adding a task
    print("1. Adding a task...")
    task_id = service.add_task("Test task", "This is a test task", "High", ["test", "important"])
    print(f"   Task added with ID: {task_id}")

    # Test getting the task
    print("2. Retrieving the task...")
    task = service.get_task(task_id)
    if task:
        print(f"   Task retrieved: {task.title}")
        print(f"   Description: {task.description}")
        print(f"   Priority: {task.priority.value}")
        print(f"   Tags: {task.tags}")
    else:
        print("   ERROR: Task not found")

    # Test getting all tasks
    print("3. Getting all tasks...")
    all_tasks = service.get_all_tasks()
    print(f"   Total tasks: {len(all_tasks)}")

    # Test updating a task
    print("4. Updating the task...")
    update_result = service.update_task(task_id, title="Updated test task", description="Updated description")
    if update_result:
        print("   Task updated successfully")
        updated_task = service.get_task(task_id)
        print(f"   Updated title: {updated_task.title}")
        print(f"   Updated description: {updated_task.description}")
    else:
        print("   ERROR: Failed to update task")

    # Test toggling task status
    print("5. Toggling task status...")
    toggle_result = service.toggle_task_status(task_id)
    if toggle_result:
        toggled_task = service.get_task(task_id)
        print(f"   Task status toggled. Completed: {toggled_task.completed}")
    else:
        print("   ERROR: Failed to toggle task status")

    # Test searching tasks
    print("6. Searching for tasks...")
    search_results = service.search_tasks("test")
    print(f"   Search results: {len(search_results)} tasks found")

    # Test filtering tasks
    print("7. Filtering tasks by priority...")
    filtered_results = service.filter_tasks(priority="High")
    print(f"   Filtered results: {len(filtered_results)} tasks found")

    # Test sorting tasks
    print("8. Sorting tasks by title...")
    sorted_results = service.sort_tasks("title")
    print(f"   Sorted results: {len(sorted_results)} tasks")

    # Test statistics
    print("9. Getting statistics...")
    total = service.get_task_count()
    completed = service.get_completed_task_count()
    pending = service.get_pending_task_count()
    print(f"   Total: {total}, Completed: {completed}, Pending: {pending}")

    # Test deleting the task
    print("10. Deleting the task...")
    delete_result = service.delete_task(task_id)
    if delete_result:
        print("   Task deleted successfully")
    else:
        print("   ERROR: Failed to delete task")

    # Verify task is deleted
    deleted_task = service.get_task(task_id)
    if deleted_task is None:
        print("   Verification: Task is properly deleted")
    else:
        print("   ERROR: Task still exists after deletion")

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_basic_functionality()