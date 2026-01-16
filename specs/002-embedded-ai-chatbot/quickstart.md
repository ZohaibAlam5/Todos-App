# Quickstart: Embedded AI Chatbot

**Feature Branch**: `002-embedded-ai-chatbot`
**Date**: 2026-01-15

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use existing Neon database)
- OpenAI API key

## Environment Setup

### 1. Backend Environment Variables

Add to `backend/.env`:

```bash
# Existing variables (keep these)
DATABASE_URL=postgresql://...
SECRET_KEY=your-jwt-secret
FRONTEND_URL=http://localhost:3000

# NEW: Add OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt

# New dependencies will include:
# openai-agents>=0.2.0
```

### 3. Frontend Setup

No new frontend dependencies required. Existing React/Next.js setup is sufficient.

```bash
cd frontend
npm install  # If not already done
```

## Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Verify Setup

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "healthy"}
   ```

2. **Chat API (after implementation)**:
   ```bash
   # Get JWT token first
   TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Password123!"}' \
     | jq -r '.access_token')

   # Test chat endpoint
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"message": "List my tasks"}'
   ```

3. **Frontend**:
   - Navigate to http://localhost:3000
   - Log in with test credentials
   - Look for chat icon in dashboard (after implementation)

## Database Migration

The new `conversation` and `message` tables will be created automatically by SQLModel on application startup.

For production deployments, use Alembic:

```bash
cd backend
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

## Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v

# Run specific test categories:
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

## Troubleshooting

### OpenAI API Errors

**Error**: `openai.AuthenticationError`
**Solution**: Verify `OPENAI_API_KEY` is set correctly in `.env`

**Error**: `openai.RateLimitError`
**Solution**: Check OpenAI usage limits; implement retry logic

### Database Errors

**Error**: `relation "conversation" does not exist`
**Solution**: Ensure database initialization runs on startup; check `init_db.py`

### CORS Errors

**Error**: `Access-Control-Allow-Origin` mismatch
**Solution**: Verify `FRONTEND_URL` in backend `.env` matches frontend origin

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   TodoList   │   │  ChatPanel   │   │  AuthContext │    │
│  └──────────────┘   └──────┬───────┘   └──────────────┘    │
└────────────────────────────┼────────────────────────────────┘
                             │ POST /api/chat
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ chat_routes  │──▶│ chat_service │──▶│  task_tools  │    │
│  └──────────────┘   └──────────────┘   └──────┬───────┘    │
│         │                                      │            │
│         │           ┌──────────────┐           │            │
│         └──────────▶│  task_routes │◀──────────┘            │
│                     │  (existing)  │                        │
│                     └──────┬───────┘                        │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  (user,task, │
                     │  conversation,│
                     │  message)    │
                     └──────────────┘
```

## Next Steps

After environment setup:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement in priority order:
   - P1: Task tools (add_task, list_tasks)
   - P1: Chat service and endpoint
   - P1: ChatPanel component
   - P2: Complete/update/delete tools
   - P2: Conversation persistence
   - P3: Edge case handling

## Resources

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contract](./contracts/chat-api.yaml)
