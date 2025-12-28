"""
Main CLI application for the console-based todo application.
Implements the menu-driven interface for interacting with the todo service.
"""
import sys
from typing import List
from datetime import datetime

from ..services.todo_service import TodoService
from ..models.task import Priority
from ..lib.logger import log_info, log_error, log_debug
from ..lib.errors import TodoError, ValidationError, TaskNotFoundError
from ..lib.config import config


class TodoCLI:
    """
    Command-line interface for the todo application.
    Provides a menu-driven interface for all todo operations.
    """

    def __init__(self):
        """Initialize the CLI with a todo service instance."""
        self.todo_service = TodoService()

    def run(self):
        """Main application loop."""
        print("Welcome to the Console-Based Todo Application!")
        print("=" * 50)
        log_info("Todo application started")

        while True:
            self.display_menu()
            choice = input("Select an option (1-10): ").strip()

            if choice == "1":
                log_debug("User selected 'Add Task'")
                self.add_task()
            elif choice == "2":
                log_debug("User selected 'View Tasks'")
                self.view_tasks()
            elif choice == "3":
                log_debug("User selected 'Update Task'")
                self.update_task()
            elif choice == "4":
                log_debug("User selected 'Delete Task'")
                self.delete_task()
            elif choice == "5":
                log_debug("User selected 'Toggle Task Status'")
                self.toggle_task_status()
            elif choice == "6":
                log_debug("User selected 'Search Tasks'")
                self.search_tasks()
            elif choice == "7":
                log_debug("User selected 'Filter Tasks'")
                self.filter_tasks()
            elif choice == "8":
                log_debug("User selected 'Sort Tasks'")
                self.sort_tasks()
            elif choice == "9":
                log_debug("User selected 'View Statistics'")
                self.view_statistics()
            elif choice == "10":
                log_info("Todo application exiting")
                print("Thank you for using the Todo Application. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please select a number between 1-10.")
                log_error(f"Invalid menu selection: {choice}")

            print()  # Add spacing between operations

    def display_menu(self):
        """Display the main menu options."""
        print("\nMain Menu:")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Toggle Task Status")
        print("6. Search Tasks")
        print("7. Filter Tasks")
        print("8. Sort Tasks")
        print("9. View Statistics")
        print("10. Exit")

    def add_task(self):
        """Add a new task."""
        print("\n--- Add New Task ---")

        try:
            title = input("Enter task title (1-255 characters): ").strip()
            if not title:
                print("Error: Title cannot be empty.")
                log_error("Empty title provided when adding task")
                return

            description = input("Enter task description (optional, 0-1000 characters): ").strip()

            print("Select priority (High/Medium/Low): ", end="")
            priority = input().strip()
            if not priority:
                priority = "Medium"  # Default priority

            tags_input = input("Enter tags separated by commas (optional): ").strip()
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []

            task_id = self.todo_service.add_task(title, description, priority, tags)
            print(f"Task added successfully with ID: {task_id}")
            log_info(f"Task added via CLI: ID {task_id}, Title '{title}'")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Add task operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def view_tasks(self):
        """View all tasks."""
        print("\n--- All Tasks ---")
        log_debug("Retrieving all tasks")

        tasks = self.todo_service.get_all_tasks()

        if not tasks:
            print("No tasks found.")
            log_info("View tasks completed - no tasks found")
            return

        for task in tasks:
            status = "✓" if task.completed else "○"
            priority_symbol = {
                Priority.HIGH: "!",
                Priority.MEDIUM: "~",
                Priority.LOW: "."
            }[task.priority]

            print(f"{status} [{task.id}] {priority_symbol} {task.title}")
            if task.description:
                print(f"    Description: {task.description}")
            if task.tags:
                print(f"    Tags: {', '.join(task.tags)}")
            print(f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        log_info(f"View tasks completed - displayed {len(tasks)} tasks")

    def update_task(self):
        """Update an existing task."""
        print("\n--- Update Task ---")

        try:
            task_id_str = input("Enter task ID to update: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number.")
                log_error(f"Invalid task ID format: {task_id_str}")
                return

            task_id = int(task_id_str)
            task = self.todo_service.get_task(task_id)
            if not task:
                print(f"Error: Task with ID {task_id} not found.")
                log_error(f"Task with ID {task_id} not found for update")
                return

            print(f"Current task: {task.title}")
            print("Leave fields empty to keep current values.")

            new_title = input(f"Enter new title (current: '{task.title}'): ").strip()
            new_description = input(f"Enter new description (current: '{task.description}'): ").strip()
            new_priority = input(f"Enter new priority (current: '{task.priority.value}'): ").strip()
            new_tags = input(f"Enter new tags (current: {', '.join(task.tags)}): ").strip()

            # Prepare update parameters
            update_params = {}
            if new_title:
                update_params["title"] = new_title
            if new_description:
                update_params["description"] = new_description
            if new_priority:
                update_params["priority"] = new_priority
            if new_tags:
                tags = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
                update_params["tags"] = tags

            success = self.todo_service.update_task(task_id, **update_params)
            if success:
                print("Task updated successfully.")
                log_info(f"Task with ID {task_id} updated successfully via CLI")
            else:
                print("Failed to update task.")
                log_error(f"Failed to update task with ID {task_id}")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Update task operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def delete_task(self):
        """Delete a task."""
        print("\n--- Delete Task ---")

        try:
            task_id_str = input("Enter task ID to delete: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number.")
                log_error(f"Invalid task ID format: {task_id_str}")
                return

            task_id = int(task_id_str)
            success = self.todo_service.delete_task(task_id)
            if success:
                print(f"Task with ID {task_id} deleted successfully.")
                log_info(f"Task with ID {task_id} deleted successfully via CLI")
            else:
                print(f"Error: Task with ID {task_id} not found.")
                log_error(f"Task with ID {task_id} not found for deletion")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Delete task operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def toggle_task_status(self):
        """Toggle task completion status."""
        print("\n--- Toggle Task Status ---")

        try:
            task_id_str = input("Enter task ID to toggle: ").strip()
            if not task_id_str.isdigit():
                print("Error: Task ID must be a number.")
                log_error(f"Invalid task ID format: {task_id_str}")
                return

            task_id = int(task_id_str)
            task = self.todo_service.get_task(task_id)
            if not task:
                print(f"Error: Task with ID {task_id} not found.")
                log_error(f"Task with ID {task_id} not found for status toggle")
                return

            success = self.todo_service.toggle_task_status(task_id)
            if success:
                new_status = "completed" if task.completed else "pending"
                print(f"Task status updated to: {new_status}")
                log_info(f"Task with ID {task_id} status updated to {new_status} via CLI")
            else:
                print("Failed to update task status.")
                log_error(f"Failed to update status for task with ID {task_id}")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Toggle task status operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def search_tasks(self):
        """Search tasks by query."""
        print("\n--- Search Tasks ---")

        try:
            query = input("Enter search query: ").strip()
            if not query:
                print("Error: Search query cannot be empty.")
                log_error("Empty search query provided")
                return

            tasks = self.todo_service.search_tasks(query)

            if not tasks:
                print("No tasks match your search query.")
                log_info(f"Search with query '{query}' returned no results")
                return

            print(f"Found {len(tasks)} task(s) matching '{query}':")
            for task in tasks:
                status = "✓" if task.completed else "○"
                print(f"{status} [{task.id}] {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                if task.tags:
                    print(f"    Tags: {', '.join(task.tags)}")
                print()

            log_info(f"Search completed with {len(tasks)} results for query '{query}'")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Search tasks operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def filter_tasks(self):
        """Filter tasks by criteria."""
        print("\n--- Filter Tasks ---")

        try:
            print("Filter options (press Enter to skip):")
            status = input("Status (completed/pending): ").strip()
            priority = input("Priority (High/Medium/Low): ").strip()
            tag = input("Tag: ").strip()

            # Only pass non-empty filters
            filters = {}
            if status:
                filters["status"] = status
            if priority:
                filters["priority"] = priority
            if tag:
                filters["tag"] = tag

            log_debug(f"Applying filters: {filters}")
            tasks = self.todo_service.filter_tasks(**filters)

            if not tasks:
                print("No tasks match your filter criteria.")
                log_info(f"Filter with criteria {filters} returned no results")
                return

            print(f"Found {len(tasks)} task(s) matching your filters:")
            for task in tasks:
                status = "✓" if task.completed else "○"
                print(f"{status} [{task.id}] {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                if task.tags:
                    print(f"    Tags: {', '.join(task.tags)}")
                print()

            log_info(f"Filter completed with {len(tasks)} results for criteria {filters}")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Filter tasks operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def sort_tasks(self):
        """Sort tasks by criteria."""
        print("\n--- Sort Tasks ---")

        try:
            print("Sort by options:")
            print("1. Title")
            print("2. Priority")
            print("3. Creation Date")

            sort_choice = input("Select sort option (1-3): ").strip()

            if sort_choice == "1":
                sort_by = "title"
            elif sort_choice == "2":
                sort_by = "priority"
            elif sort_choice == "3":
                sort_by = "created_at"
            else:
                print("Invalid sort option.")
                log_error(f"Invalid sort option selected: {sort_choice}")
                return

            order = input("Order (asc/desc, default asc): ").strip().lower()
            if order not in ["asc", "desc"]:
                order = "asc"

            log_debug(f"Sorting tasks by {sort_by} in {order} order")
            tasks = self.todo_service.sort_tasks(sort_by, order)

            if not tasks:
                print("No tasks to sort.")
                log_info("Sort operation completed but no tasks found to sort")
                return

            print(f"Tasks sorted by {sort_by} ({order}):")
            for task in tasks:
                status = "✓" if task.completed else "○"
                print(f"{status} [{task.id}] {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                if task.tags:
                    print(f"    Tags: {', '.join(task.tags)}")
                print()

            log_info(f"Sort completed with {len(tasks)} tasks sorted by {sort_by} in {order} order")

        except ValueError as e:
            error_msg = f"Validation error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except TodoError as e:
            error_msg = f"Todo application error: {e}"
            print(f"Error: {error_msg}")
            log_error(error_msg)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            log_debug("Sort tasks operation cancelled by user")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            log_error(error_msg)

    def view_statistics(self):
        """View application statistics."""
        print("\n--- Statistics ---")

        total_tasks = self.todo_service.get_task_count()
        completed_tasks = self.todo_service.get_completed_task_count()
        pending_tasks = self.todo_service.get_pending_task_count()

        print(f"Total Tasks: {total_tasks}")
        print(f"Completed Tasks: {completed_tasks}")
        print(f"Pending Tasks: {pending_tasks}")

        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            print(f"Completion Rate: {completion_rate:.1f}%")

        log_info(f"Statistics viewed - Total: {total_tasks}, Completed: {completed_tasks}, Pending: {pending_tasks}")


def main():
    """Entry point for the application."""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()