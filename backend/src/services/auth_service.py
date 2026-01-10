from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from src.models.user import User, UserCreate
from src.models.password_reset import PasswordResetToken
from src.database.database import get_db
from src.utils.jwt import verify_password, get_password_hash
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        statement = select(User).where(User.email == email)
        user = self.db.exec(statement).first()

        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()  # This preserves the original data including 'sub'
        print(f"Creating token with data: {to_encode}")  # Debug log
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})  # Add expiration while keeping original data
        print(f"Final payload for encoding: {to_encode}")  # Debug log
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"Encoded JWT: {encoded_jwt[:50]}...")  # Debug log - first 50 chars
        return encoded_jwt

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Check if user already exists
        existing_user = self.db.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash the password
        hashed_password = get_password_hash(user_create.password)

        # Create the user
        user = User(
            email=user_create.email,
            password_hash=hashed_password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        user = self.db.exec(statement).first()
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        statement = select(User).where(User.id == user_id)
        user = self.db.exec(statement).first()
        return user

    def request_password_reset(self, email: str) -> bool:
        """Request a password reset for a user."""
        import secrets
        from datetime import datetime, timedelta
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from src.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM

        # Find the user
        user = self.get_user_by_email(email)
        if not user:
            # Don't reveal if the email exists to prevent enumeration attacks
            return True  # Still return True to not disclose if email exists

        # Generate a secure reset code (6 digits)
        reset_code = f"{secrets.randbelow(1000000):06d}"

        # Store the reset code and expiry time (15 minutes from now)
        expiry_time = datetime.utcnow() + timedelta(minutes=15)

        # Remove any existing reset tokens for this email
        existing_token = self.db.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.email == email
            )
        ).first()

        if existing_token:
            self.db.delete(existing_token)
            self.db.commit()

        # Create a new reset token
        reset_token = PasswordResetToken(
            email=email,
            token=reset_code,
            expires_at=expiry_time
        )

        self.db.add(reset_token)
        self.db.commit()
        self.db.refresh(reset_token)

        # Send the reset code via email
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = email
            msg['Subject'] = "Password Reset Code - TaskFlow"

            body = f"""
            Hello,

            You have requested to reset your password for TaskFlow.

            Your password reset code is: {reset_code}

            This code will expire in 15 minutes. If you did not request this reset, please ignore this email.

            Thank you,
            TaskFlow Team
            """

            msg.attach(MIMEText(body, 'plain'))

            # Connect to server and send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Enable encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_FROM, email, text)
            server.quit()

            print(f"Password reset code sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            # Still return True to not reveal if email exists, but log the error
            return True

        return True

    def verify_reset_code(self, email: str, code: str) -> bool:
        """Verify if the reset code is valid for the email."""
        from datetime import datetime

        # Check if code is properly formatted
        if len(code) != 6 or not code.isdigit():
            return False

        # Find the reset token for this email
        reset_token = self.db.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.email == email,
                PasswordResetToken.token == code,
                PasswordResetToken.used == False
            )
        ).first()

        if not reset_token:
            print(f"No valid reset code found for email: {email}")
            return False

        # Check if code has expired
        current_time = datetime.utcnow()
        if current_time > reset_token.expires_at:
            print(f"Reset code for {email} has expired")
            # Mark the token as used to prevent reuse
            reset_token.used = True
            self.db.add(reset_token)
            self.db.commit()
            return False

        # Mark the token as used to prevent reuse
        reset_token.used = True
        self.db.add(reset_token)
        self.db.commit()

        print(f"Reset code verified successfully for {email}")
        return True

    def reset_user_password(self, email: str, new_password: str) -> bool:
        """Reset the user's password."""
        user = self.get_user_by_email(email)
        if not user:
            return False

        # Validate the new password
        from src.utils.jwt import validate_password
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements"
            )

        # Hash the new password
        hashed_password = get_password_hash(new_password)
        user.password_hash = hashed_password

        # Update the user in the database
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return True