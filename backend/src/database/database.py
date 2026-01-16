from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from src.models.user import User
from src.models.task import Task
from src.models.password_reset import PasswordResetToken
from src.models.conversation import Conversation
from src.models.message import Message

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL - defaults to SQLite for development, can be overridden with DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# For SQLite, we need to use the correct URL format
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, disable the check_same_thread for development purposes
    engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
else:
    # For PostgreSQL and other databases, use connection pooling settings
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,    # Verify connections before use
        pool_recycle=300,      # Recycle connections every 5 minutes
        pool_size=5,           # Reduced pool size for Neon
        max_overflow=10,       # Reduced overflow for Neon
        pool_timeout=20,       # Shorter timeout
        pool_reset_on_return='commit',  # Reset connection on return
        max_identifier_length=30,  # For compatibility with some databases
        connect_args={
            "connect_timeout": 10,
            "application_name": "TodoApp"
        }
    )

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session