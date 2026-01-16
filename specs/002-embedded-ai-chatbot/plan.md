# Implementation Plan: Embedded AI Chatbot for Todo Management

**Branch**: `002-embedded-ai-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-embedded-ai-chatbot/spec.md`

## Summary

Embed an AI-powered chatbot into the existing Phase 2 web application, enabling authenticated users to manage Todo items through natural language conversation. The chatbot uses OpenAI Agents SDK with function tools to interpret user intent and execute task operations via existing backend services. Conversation history persists to PostgreSQL, and all operations enforce user isolation through JWT authentication.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, openai-agents, mcp (Python SDK)
- Frontend: Next.js 16.1.1, React 18.3.1, Tailwind CSS 4.1
**Storage**: PostgreSQL (Neon Serverless) - existing + new Conversation/Message tables
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web (desktop/mobile browsers)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Task creation via chat: <5 seconds
- Task query response: <3 seconds
- Chatbot load time: <1 second
**Constraints**:
- No breaking changes to Phase 2 APIs
- Single chat endpoint only
- User identity from JWT only
**Scale/Scope**: Multi-user, existing Phase 2 user base

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-Driven Authority | PASS | All features traced to spec.md FR-001 through FR-019 |
| Spec-First Development | PASS | Specification created before implementation plan |
| Determinism & Reproducibility | PASS | Explicit tool definitions, no hidden assumptions |
| Progressive Evolution | PASS | Phase 2 remains functional, additive changes only |
| AI-Native Architecture | PASS | AI agents use defined tools, no direct DB access |
| Constitutional Compliance | PASS | All implementation follows constitution |

### AI Agent Governance Check

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Tool-Based Control | PASS | All operations via @function_tool decorators |
| Stateless Tools | PASS | Tools call existing services, store no state |
| Direct DB Access Forbidden | PASS | Tools use TaskService, not Session directly |
| Deterministic Decision Rules | PASS | Tools have explicit input/output schemas |
| Explainable Actions | PASS | Tool calls logged in Message.tool_calls |
| Input Validation | PASS | Pydantic schemas on all tool inputs |
| Clarification on Ambiguity | PASS | Agent instructions require clarification |
| Destructive Action Confirmation | PASS | Delete tool requires explicit confirmation |

### Security & Isolation Check

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| User Data Isolation | PASS | All queries filter by current_user.id |
| Auth at Every Layer | PASS | JWT required for /api/chat, tools receive user context |
| No Endpoint Bypasses | PASS | MCP tools enforce ownership via user_id parameter |

**Gate Result**: PASS - Proceed to Phase 1 Design

## Project Structure

### Documentation (this feature)

```text
specs/002-embedded-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── auth_routes.py      # Existing
│   │   ├── tasks_routes.py     # Existing
│   │   └── chat_routes.py      # NEW: Chat endpoint
│   ├── models/
│   │   ├── user.py             # Existing
│   │   ├── task.py             # Existing
│   │   ├── conversation.py     # NEW: Conversation model
│   │   └── message.py          # NEW: Message model
│   ├── services/
│   │   ├── auth_service.py     # Existing
│   │   ├── task_service.py     # NEW: Extract from routes
│   │   └── chat_service.py     # NEW: Agent orchestration
│   ├── tools/
│   │   ├── __init__.py         # NEW: Tool exports
│   │   └── task_tools.py       # NEW: MCP tool definitions
│   ├── middleware/
│   │   └── auth_middleware.py  # Existing (reused)
│   ├── database/
│   │   ├── database.py         # Existing
│   │   └── init_db.py          # Existing (update for new models)
│   ├── config.py               # Existing (add OPENAI_API_KEY)
│   └── main.py                 # Existing (add chat_router)
└── tests/
    ├── unit/
    │   └── test_task_tools.py  # NEW
    ├── integration/
    │   └── test_chat_api.py    # NEW
    └── contract/
        └── test_chat_contract.py # NEW

frontend/
├── src/
│   ├── components/
│   │   ├── AuthContext.tsx     # Existing
│   │   ├── TodoList.tsx        # Existing
│   │   ├── ChatPanel.tsx       # NEW: Main chat component
│   │   ├── ChatMessage.tsx     # NEW: Message display
│   │   └── ChatInput.tsx       # NEW: Input component
│   ├── services/
│   │   ├── auth.ts             # Existing
│   │   ├── task.ts             # Existing
│   │   └── chat.ts             # NEW: Chat API calls
│   ├── types/
│   │   └── index.ts            # Existing (extend with Chat types)
│   └── app/
│       └── dashboard/
│           └── page.tsx        # Existing (add ChatPanel)
└── tests/
    └── components/
        └── ChatPanel.test.tsx  # NEW
```

**Structure Decision**: Extends existing Phase 2 web application structure. New files added to existing directories following established patterns. No new top-level directories required.

## Complexity Tracking

> No violations requiring justification. Implementation follows constitution.

## Architecture Decisions

### AD-001: Function Tools over MCP Server

**Decision**: Use `@function_tool` decorator from openai-agents instead of separate MCP server.

**Rationale**:
- Simpler deployment (no separate process)
- Same tool semantics as MCP
- Can migrate to MCP server later if needed
- Reduces operational complexity

**Trade-offs**:
- Less portable tools (tied to OpenAI Agents SDK)
- Acceptable for MVP; revisit for multi-agent scenarios

### AD-002: HTTP Polling over WebSockets

**Decision**: Use standard HTTP POST for chat, polling for updates.

**Rationale**:
- Simpler implementation aligns with existing API patterns
- Sufficient for conversational (not real-time) use case
- WebSockets add deployment complexity

**Trade-offs**:
- Slightly higher latency for long responses
- Acceptable; can add streaming/WebSockets later

### AD-003: Conversation Context Limit

**Decision**: Load last 20 messages into agent context.

**Rationale**:
- Balances context quality vs. token costs
- Full history stored in DB for UI display
- Agent can reference recent context accurately

**Trade-offs**:
- Very old messages not in agent's memory
- Acceptable; users can start new conversations

## Phase 1 Artifacts

The following artifacts will be generated:
1. `data-model.md` - Conversation and Message entity definitions
2. `contracts/chat-api.yaml` - OpenAPI specification for POST /api/chat
3. `quickstart.md` - Development setup instructions

## Next Steps

1. Generate data-model.md with Conversation and Message schemas
2. Generate contracts/chat-api.yaml with request/response schemas
3. Generate quickstart.md with setup instructions
4. Run `/sp.tasks` to generate implementation tasks
