from src.database.database import create_db_and_tables

def init_db():
    """Initialize the database and create tables."""
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()