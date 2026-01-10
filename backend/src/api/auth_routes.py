from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.models.user import UserCreate
from src.database.database import get_db
from src.services.auth_service import AuthService
from src.middleware.auth_middleware import get_current_active_user
from src.models.user import User
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        auth_service = AuthService(db)

        # Check if user already exists
        existing_user = auth_service.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create the user
        user = auth_service.create_user(user_create)

        # Refresh the user object to ensure it's properly loaded from the database
        db.refresh(user)

        # Create access token
        print(f"Creating access token for user ID: {user.id}")  # Debug log
        access_token = auth_service.create_access_token(data={"sub": user.id})

        # Explicitly commit the transaction
        db.commit()

        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        print(f"Error in register: {e}")  # Debug log
        raise

@router.post("/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Login a user and return access token."""
    try:
        auth_service = AuthService(db)

        user = auth_service.authenticate_user(login_request.email, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Refresh the user object to ensure it's properly loaded from the database
        db.refresh(user)

        # Create access token
        print(f"Creating access token for user ID: {user.id}")  # Debug log
        access_token = auth_service.create_access_token(data={"sub": user.id})

        # Explicitly commit the transaction (though login shouldn't modify DB)
        db.commit()

        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        print(f"Error in login: {e}")  # Debug log
        raise

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    print(f"Auth /me endpoint reached for user: {current_user.email}")  # Debug log
    return current_user

# --- FORGOT PASSWORD ROUTES ---

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset."""
    try:
        auth_service = AuthService(db)
        success = auth_service.request_password_reset(request.email)
        if success:
            return {"message": "Password reset code sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send reset code"
            )
    except Exception as e:
        print(f"Error in forgot_password: {e}")  # Debug log
        raise

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset user password with the code."""
    try:
        auth_service = AuthService(db)

        # Verify the reset code
        if not auth_service.verify_reset_code(request.email, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )

        # Reset the password
        success = auth_service.reset_user_password(request.email, request.new_password)
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error in reset_password: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting the password"
        )