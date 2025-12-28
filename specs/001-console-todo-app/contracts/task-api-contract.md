# Task API Contract: Console-Based Todo Application

## Overview
This document defines the functional contracts for the console-based todo application. These contracts map directly to the functional requirements specified in the feature specification.

## Core Operations

### 1. Add Task
**Endpoint**: CLI Command - `add_task(title, description=None, priority="Medium", tags=[])`
**Input**:
- title (string, required, 1-255 characters)
- description (string, optional, 0-1000 characters)
- priority (enum, optional, values: "High", "Medium", "Low", default: "Medium")
- tags (list of strings, optional)

**Output**:
- task_id (integer) - unique identifier for the created task
- success (boolean) - indicates if the operation was successful

**Validation**:
- Title must be 1-255 characters
- Description must be 0-1000 characters
- Priority must be one of "High", "Medium", "Low" (case-insensitive)
- Duplicate tags are automatically removed

**Error Cases**:
- Invalid input parameters return appropriate error message
- Returns to main menu after error

### 2. View Tasks
**Endpoint**: CLI Command - `view_tasks(filter=None, sort_by=None)`
**Input**:
- filter (object, optional) - filter criteria
- sort_by (string, optional) - sort criteria

**Output**:
- tasks (list of task objects) - list of tasks with all properties
- count (integer) - number of tasks returned

**Response Format**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Sample task",
      "description": "Sample description",
      "completed": false,
      "priority": "Medium",
      "tags": ["tag1", "tag2"],
      "created_at": "2025-12-27T10:00:00Z"
    }
  ],
  "count": 1
}
```

### 3. Update Task
**Endpoint**: CLI Command - `update_task(task_id, title=None, description=None, priority=None, tags=None)`
**Input**:
- task_id (integer) - unique identifier of the task to update
- title (string, optional) - new title for the task
- description (string, optional) - new description for the task
- priority (string, optional) - new priority for the task
- tags (list of strings, optional) - new tags for the task

**Output**:
- success (boolean) - indicates if the operation was successful
- message (string) - success or error message

**Validation**:
- Task with given ID must exist
- All field validations as per Add Task operation

**Error Cases**:
- Task ID not found returns error message
- Invalid parameters return appropriate error message

### 4. Delete Task
**Endpoint**: CLI Command - `delete_task(task_id)`
**Input**:
- task_id (integer) - unique identifier of the task to delete

**Output**:
- success (boolean) - indicates if the operation was successful
- message (string) - success or error message

**Validation**:
- Task with given ID must exist

**Error Cases**:
- Task ID not found displays error message and returns to main menu

### 5. Mark Task Complete/Incomplete
**Endpoint**: CLI Command - `toggle_task_status(task_id, completed)`
**Input**:
- task_id (integer) - unique identifier of the task to update
- completed (boolean) - new completion status

**Output**:
- success (boolean) - indicates if the operation was successful
- message (string) - success or error message

**Validation**:
- Task with given ID must exist

**Error Cases**:
- Task ID not found returns error message

### 6. Search Tasks
**Endpoint**: CLI Command - `search_tasks(query)`
**Input**:
- query (string) - search term to match against title, description, and tags

**Output**:
- tasks (list of task objects) - list of matching tasks
- count (integer) - number of matching tasks

**Behavior**:
- Search is case-insensitive
- Matches against title, description, and tags
- Returns all tasks that match the query

### 7. Filter Tasks
**Endpoint**: CLI Command - `filter_tasks(criteria)`
**Input**:
- criteria (object) - filter parameters
  - status (string, optional) - "completed" or "pending"
  - priority (string, optional) - "High", "Medium", or "Low"
  - tag (string, optional) - specific tag to filter by

**Output**:
- tasks (list of task objects) - list of filtered tasks
- count (integer) - number of filtered tasks

**Behavior**:
- Multiple criteria can be combined (AND operation)
- If no criteria match, returns empty list

### 8. Sort Tasks
**Endpoint**: CLI Command - `sort_tasks(sort_by, order="asc")`
**Input**:
- sort_by (string) - field to sort by ("title", "priority", "created_at")
- order (string, optional) - sort order ("asc", "desc", default: "asc")

**Output**:
- tasks (list of task objects) - sorted list of tasks
- count (integer) - number of tasks

**Behavior**:
- Sorts all available tasks by specified field
- Priority sorting follows High → Medium → Low order
- Creation order sorting follows chronological order

## Validation Contract
All inputs are validated according to the data model specifications:
- String length limits enforced
- Enum values validated
- Duplicate handling as specified
- Error messages provided for invalid inputs