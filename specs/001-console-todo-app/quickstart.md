# Quickstart Guide: Console-Based Todo Application

## Prerequisites
- Python 3.11 or higher
- No additional dependencies required

## Running the Application

1. **Clone/Access the repository**
   ```bash
   # Navigate to the project directory
   cd /path/to/project
   ```

2. **Run the application**
   ```bash
   python src/cli/main.py
   ```

## Basic Usage

### Main Menu Options
When the application starts, you'll see a menu with the following options:
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Search Tasks
7. Filter Tasks
8. Sort Tasks
9. Exit

### Common Workflows

#### Adding a Task
1. Select "Add Task" from the main menu
2. Enter the task title (required, max 255 characters)
3. Optionally enter a description (max 1000 characters)
4. Optionally set priority (High/Medium/Low, defaults to Medium)
5. Optionally add tags (comma-separated)

#### Viewing Tasks
1. Select "View Tasks" from the main menu
2. All tasks will be displayed with ID, title, status, priority, and tags

#### Searching Tasks
1. Select "Search Tasks" from the main menu
2. Enter a keyword to search in titles, descriptions, and tags
3. Matching tasks will be displayed

#### Filtering Tasks
1. Select "Filter Tasks" from the main menu
2. Choose filter criteria (status, priority, or tags)
3. Filtered tasks will be displayed

#### Sorting Tasks
1. Select "Sort Tasks" from the main menu
2. Choose sort criteria (title, priority, or creation order)
3. Tasks will be displayed in sorted order

## Error Handling
- Invalid inputs will show clear error messages
- The application will not crash on invalid input
- You'll be returned to the main menu after error messages

## Data Persistence
- All data is stored in memory only
- Tasks will be lost when the application exits
- No file or database storage is used