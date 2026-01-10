from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from src.api.auth_routes import router as auth_router
from src.api.tasks_routes import router as tasks_router
from src.database.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    print("Starting up...")
    try:
        # Initialize database tables with retry logic
        for attempt in range(3):
            try:
                create_db_and_tables()
                print("Database tables created successfully")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} to create tables failed: {e}")
                if attempt == 2:  # Last attempt
                    raise e
                asyncio.sleep(1)  # Wait before retry
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise e

    # Shutdown
    yield

    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")  # Default to localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Allow only the frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers that frontend might need
    expose_headers=["Access-Control-Allow-Origin"]
)

# Include authentication routes
app.include_router(auth_router)
# Include tasks routes
app.include_router(tasks_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))