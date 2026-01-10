from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select
from src.models.user import User
from src.database.database import get_db
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None  # Store user ID from JWT 'sub' field

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72-byte password length limit, so truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def validate_password(password: str) -> bool:
    """Validate password according to requirements: 8+ chars, mixed case, numbers, symbols."""
    import re

    # Check minimum length
    if len(password) < 8:
        return False

    # Check maximum length (bcrypt limit is 72 bytes)
    if len(password.encode('utf-8')) > 72:
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify a JWT token and return the token data."""
    try:
        print(f"Verifying token: {token[:20]}...")  # Debug log - print first 20 chars
        print(f"Using SECRET_KEY: {SECRET_KEY[:10]}...")  # Debug log - print first 10 chars of key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debug log
        user_id: str = payload.get("sub")  # This should be the user ID
        if user_id is None:
            print("No 'sub' field found in token payload")  # Debug log
            return None
        token_data = TokenData(id=user_id)  # Store user ID in id field
        print(f"Returning token data for user_id: {user_id}")  # Debug log
        return token_data
    except JWTError as e:
        print(f"JWT Error during verification: {e}")  # Debug log
        return None
    except Exception as e:
        print(f"Unexpected error during token verification: {e}")  # Debug log
        return None

def get_current_user_from_token(token: str) -> Optional[User]:
    """Get the current user from a JWT token."""
    token_data = verify_token(token)
    if token_data is None:
        return None

    # In a real implementation, you would query the database for the user
    # This is a simplified version for now
    return User(id=token_data.username, email="temp@example.com", password_hash="temp")  # This is just a placeholder