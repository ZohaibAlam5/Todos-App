# Quickstart Guide: Web-Based Multi-User Todo Application

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 12+
- Git

## Setup Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and secret keys
   ```

5. Start the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```

## Setup Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend API URL
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

The backend serves API endpoints at `http://localhost:8000/api/{user_id}/tasks`

## Authentication

1. Register a new user at `/register`
2. Login at `/login` to get a JWT token
3. Include the token in the `Authorization` header as `Bearer {token}` for API requests

## Database Setup

1. Set up PostgreSQL database
2. Update the database URL in your backend `.env` file
3. Run the application to automatically create tables via SQLModel

## Running Tests

Backend tests:
```bash
cd backend
python -m pytest
```

Frontend tests:
```bash
cd frontend
npm test
```