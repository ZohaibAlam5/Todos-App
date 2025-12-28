# Console-Based Todo Application

A simple, efficient todo application with a command-line interface built in Python.

## Features

- Add, view, update, and delete tasks
- Mark tasks as complete/incomplete
- Search tasks by title, description, or tags
- Filter tasks by status, priority, or tags
- Sort tasks by title, priority, or creation date
- View statistics about your tasks

## Requirements

- Python 3.11 or higher

## Installation

No external dependencies required - uses only Python standard library.

## Usage

To run the application:

```bash
python main.py
```

The application will start in interactive mode with a menu-driven interface.

## Architecture

The application follows a layered architecture:

- `src/cli/` - Command-line interface layer
- `src/services/` - Business logic layer
- `src/models/` - Data models
- `src/lib/` - Utilities (logging, validation, configuration)

## Configuration

The application can be configured using environment variables:

- `TODO_DEBUG` - Enable debug mode (true/false)
- `TODO_LOG_LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)
- `TODO_DATA_DIR` - Directory for data storage (not used in in-memory version)
- `TODO_MAX_TASKS` - Maximum number of tasks allowed (default: 1000)

## Data Model

Each task has the following properties:
- `id`: Unique identifier
- `title`: Task title (1-255 characters)
- `description`: Task description (up to 1000 characters)
- `completed`: Boolean indicating completion status
- `priority`: Priority level (High, Medium, Low)
- `tags`: List of tags associated with the task
- `created_at`: Timestamp when the task was created