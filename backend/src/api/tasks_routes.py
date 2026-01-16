from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import json
from src.database.database import get_db
from src.models.user import User
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskRead])
def get_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for the current user."""
    statement = select(Task).where(Task.user_id == current_user.id)
    tasks = db.exec(statement).all()

    # Convert tasks to TaskRead format
    result = []
    for task in tasks:
        task_dict = task.model_dump()
        # Convert the tags string to a list for the response
        task_dict["tags"] = task.tags_list
        # Priority is already a string
        task_dict["priority"] = task.priority
        result.append(TaskRead(**task_dict))

    return result

@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task for the current user."""
    try:
        print(f"Creating task: {task.title} for user: {current_user.id}")  # Debug log
        print(f"Task data: title={task.title}, description={task.description}, priority={task.priority}")  # Debug log
        print(f"Task tags: {task.tags}")  # Debug log
        print(f"Current user exists: {current_user.email}")  # Debug log
        print(f"Current user ID type: {type(current_user.id)}, value: {current_user.id}")  # Debug log

        # Verify that the user actually exists in the database (within the same session)
        # This ensures that the user_id is valid within the current transaction
        user_verification_query = select(User).where(User.id == current_user.id)
        verified_user = db.exec(user_verification_query).first()
        print(f"Verified user exists in session: {verified_user is not None}")  # Debug log

        if not verified_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {current_user.id} not found in database"
            )

        # Validate priority is one of the allowed values
        if task.priority not in ["High", "Medium", "Low"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority value: {task.priority}. Must be 'High', 'Medium', or 'Low'"
            )

        # Create task directly from validated input
        db_task = Task(
            title=task.title,
            description=task.description,
            completed=task.completed or False,
            priority=task.priority,  # Already validated
            tags=json.dumps(task.tags) if task.tags else "[]",  # Store tags as JSON string
            user_id=current_user.id
        )
        print(f"DB Task created: {db_task.title}")  # Debug log

        db.add(db_task)
        print("Task added to session")  # Debug log

        try:
            # Flush to trigger any constraint violations before commit
            db.flush()
            print("Flush completed successfully")  # Debug log
        except Exception as flush_error:
            print(f"Flush error: {flush_error}")  # Debug log
            db.rollback()
            raise flush_error

        db.commit()
        print("Transaction committed")  # Debug log
        db.refresh(db_task)
        print("Task refreshed from DB")  # Debug log

        # Convert to TaskRead format for response
        task_dict = db_task.model_dump()
        task_dict["tags"] = db_task.tags_list
        # Priority is already a string
        task_dict["priority"] = db_task.priority
        return TaskRead(**task_dict)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error in create_task: {e}")  # Debug log
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Could not create task: {str(e)}")

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = db.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Convert to TaskRead format for response
    task_dict = db_task.model_dump()
    task_dict["tags"] = db_task.tags_list
    # Priority is already a string
    task_dict["priority"] = db_task.priority
    return TaskRead(**task_dict)

@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = db.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task with provided values
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tags" and value is not None:
            # Handle tags conversion to JSON string for storage
            setattr(db_task, "tags", json.dumps(value) if value else "[]")
        elif field == "priority" and value is not None:
            # Validate priority is one of the allowed values
            if value not in ["High", "Medium", "Low"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority value: {value}. Must be 'High', 'Medium', or 'Low'"
                )
            setattr(db_task, field, value)
        elif value is not None:
            setattr(db_task, field, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Convert to TaskRead format for response
    task_dict = db_task.model_dump()
    task_dict["tags"] = db_task.tags_list
    # Priority is already a string
    task_dict["priority"] = db_task.priority
    return TaskRead(**task_dict)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = db.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}