from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    token: str = Field(index=True, unique=True)
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PasswordResetTokenCreate(SQLModel):
    email: str
    token: str
    expires_at: datetime


class PasswordResetTokenRead(SQLModel):
    id: int
    email: str
    token: str
    expires_at: datetime
    used: bool
    created_at: datetime