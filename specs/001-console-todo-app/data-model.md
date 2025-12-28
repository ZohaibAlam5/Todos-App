# Data Model: Console-Based Todo Application

## Core Entity: Task

### Fields
- **id**: integer (unique, auto-incrementing)
  - Primary identifier for the task
  - Generated automatically when task is created
  - Range: positive integers starting from 1

- **title**: string (required, max 255 characters)
  - The main description of the task
  - Required field for all tasks
  - Validation: 1-255 characters, non-empty

- **description**: string (optional, max 1000 characters)
  - Additional details about the task
  - Optional field that can be empty
  - Validation: 0-1000 characters

- **completed**: boolean
  - Indicates whether the task is completed
  - Default value: false
  - Can be toggled between true/false

- **priority**: enum (High | Medium | Low)
  - Importance level of the task
  - Default value: Medium
  - Used for sorting and filtering operations

- **tags**: list of strings
  - Collection of tags assigned to the task
  - Used for categorization and filtering
  - Validation: duplicate tags are automatically removed

- **created_at**: timestamp (datetime)
  - Time when the task was created
  - Used for creation order sorting
  - Automatically set when task is created

### Relationships
- No relationships needed since this is a single-entity model for a single-user application

### Validation Rules
1. **Title**: Required, 1-255 characters, cannot be empty or just whitespace
2. **Description**: Optional, 0-1000 characters
3. **Priority**: Must be one of "High", "Medium", or "Low" (case-insensitive)
4. **Tags**: List of strings with duplicates automatically removed
5. **ID**: Must be unique within the application session
6. **Completed**: Must be boolean value (true/false)

### State Transitions
- **Creation**: New task with completed=false (default)
- **Update**: Any field except ID can be modified
- **Completion**: Toggle completed field between false and true
- **Deletion**: Task is removed from the collection

### Indexes
- Primary: ID (unique)
- Secondary: Priority (for sorting/filtering)
- Secondary: Tags (for filtering)
- Secondary: Completed status (for filtering)