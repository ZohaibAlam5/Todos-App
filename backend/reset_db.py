import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import engine
from src.models.task import Task
from src.models.user import User
from sqlmodel import SQLModel

def reset_database():
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")

    print("Creating all tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("All tables created successfully!")

    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()