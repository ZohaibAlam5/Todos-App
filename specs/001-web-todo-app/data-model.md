# Data Model: Web-Based Multi-User Todo Application

## User Entity

**Fields:**
- `id` (string) - Unique identifier for the user
- `email` (string) - User's email address (unique, required)
- `password_hash` (string) - Hashed password for authentication
- `created_at` (timestamp) - Account creation timestamp
- `updated_at` (timestamp) - Last account update timestamp

**Relationships:**
- One-to-many with Task entity (via user_id foreign key)

**Validation:**
- Email must be valid email format
- Password must meet complexity requirements (minimum 8 characters with mixed case, numbers, symbols)
- Email must be unique across all users

## Task Entity

**Fields:**
- `id` (integer) - Primary key, auto-incrementing
- `user_id` (string) - Foreign key referencing User.id
- `title` (string) - Task title (required, max 255 characters)
- `description` (string) - Task description (optional, max 1000 characters)
- `completed` (boolean) - Task completion status (default: false)
- `priority` (enum) - Task priority level (values: "High", "Medium", "Low", default: "Medium")
- `tags` (array of strings) - Array of tags for categorization (optional)
- `created_at` (timestamp) - Task creation timestamp
- `updated_at` (timestamp) - Last task update timestamp

**Relationships:**
- Many-to-one with User entity (via user_id foreign key)

**Validation:**
- Title must not be empty
- Priority must be one of the allowed values
- Tags array elements must be valid strings
- User_id must reference an existing user

## State Transitions

**Task States:**
- Active → Completed: When user marks task as complete
- Completed → Active: When user marks task as incomplete

**User States:**
- Unauthenticated → Authenticated: After successful login
- Authenticated → Unauthenticated: After logout or session expiration

## Indexes

**Required Indexes:**
- User.email (unique index for authentication)
- Task.user_id (index for user-specific queries)
- Task.completed (index for filtering by completion status)
- Task.priority (index for sorting by priority)
- Task.created_at (index for sorting by creation date)