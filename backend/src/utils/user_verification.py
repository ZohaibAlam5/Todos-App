from fastapi import HTTPException, status
from src.models.user import User

def verify_user_owns_resource(current_user: User, resource_user_id: str) -> bool:
    """
    Verify that the current user owns the resource they're trying to access.
    This is used to ensure multi-user isolation.
    """
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
    return True

def verify_user_id_match(current_user: User, path_user_id: str) -> bool:
    """
    Verify that the user ID in the JWT token matches the user ID in the path parameter.
    This ensures users can only access their own data.
    """
    if current_user.id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch"
        )
    return True