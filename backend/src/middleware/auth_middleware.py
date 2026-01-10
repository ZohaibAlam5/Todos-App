from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from src.utils.jwt import verify_token
from src.database.database import get_db
from src.models.user import User
from src.services.auth_service import AuthService
from typing import Generator

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user from the JWT token in the Authorization header.
    This serves as authentication middleware.
    """
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token data
    user_id = token_data.id  # This is from the token's 'sub' field which stores user id
    print(f"Looking up user with ID: {user_id}")  # Debug log

    try:
        # Get the user from the database by ID
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User not found with ID: {user_id}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        print(f"Error fetching user from database: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - database error",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    # In a real implementation, we would check if the user is active
    # For now, we'll assume all users are active
    return current_user