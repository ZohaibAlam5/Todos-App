# Research: Embedded AI Chatbot for Todo Management

**Feature Branch**: `002-embedded-ai-chatbot`
**Date**: 2026-01-15
**Status**: Complete

## Research Topics

### 1. AI Agent Framework Selection

**Decision**: OpenAI Agents SDK (openai-agents-python)

**Rationale**:
- First-party SDK from OpenAI with native support for tool calling
- Lightweight primitives: Agents, Handoffs, Guardrails, Sessions
- Built-in tracing for debugging and visualization
- Native MCP (Model Context Protocol) integration
- Async-first design compatible with FastAPI

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain | Heavier dependency, more complex abstractions |
| Raw OpenAI API | Manual tool call handling, no agent orchestration |
| AutoGen | Over-engineered for single-agent use case |

**Integration Pattern**:
```python
from agents import Agent, Runner, function_tool

@function_tool
def task_operation(params: dict) -> dict:
    """Execute task operation."""
    return {"result": "success"}

agent = Agent(
    name="Todo Assistant",
    instructions="Help users manage tasks via natural language.",
    tools=[task_operation],
)

result = await Runner.run(agent, user_message)
```

### 2. MCP Tool Server Architecture

**Decision**: FastMCP with Streamable HTTP transport

**Rationale**:
- FastMCP provides decorator-based tool definition (similar to FastAPI routes)
- Streamable HTTP transport allows integration within existing FastAPI app
- Tools are stateless and deterministic as required by spec
- Built-in input/output schema validation
- High benchmark score (89.2) and official Anthropic SDK

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| MCP Stdio transport | Requires separate process, complicates deployment |
| Custom tool implementation | No standardization, harder maintenance |
| LangChain Tools | Different protocol, not MCP-compatible |

**Tool Definition Pattern**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Todo MCP Server")

@mcp.tool()
def add_task(title: str, priority: str = "Medium") -> dict:
    """Create a new task."""
    return {"id": 1, "title": title, "priority": priority}
```

### 3. MCP-Agent Integration Strategy

**Decision**: MCPServerStreamableHttp for in-process communication

**Rationale**:
- OpenAI Agents SDK has native MCPServerStreamableHttp class
- Allows HTTP-based communication with MCP server
- Supports async context managers for proper lifecycle
- Can run MCP server on same FastAPI application
- Tool filtering and caching supported

**Architecture**:
```
Frontend → Chat API → Agent Runner → MCP Server → Task Service → Database
                                  ↘ Response ↙
```

**Integration Pattern**:
```python
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="Todo MCP Server",
    params={"url": "http://localhost:8000/mcp"},
) as server:
    agent = Agent(
        name="Todo Assistant",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, message)
```

### 4. Conversation Persistence Strategy

**Decision**: Database-backed conversation storage with lazy loading

**Rationale**:
- Spec requires: "No in-memory session state for conversations"
- Database storage enables cross-session persistence
- Lazy loading prevents loading entire history on each request
- Conversation context window can be limited to recent N messages

**Schema Design**:
- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, role, content, tool_calls (JSON), created_at

**Context Loading Strategy**:
1. Load last N messages (default: 20) for agent context
2. Summarize older messages if needed
3. Store full history for UI display

### 5. Chat UI Component Architecture

**Decision**: Custom embedded chat panel with existing auth context

**Rationale**:
- Must integrate with existing AuthContext from Phase 2
- Collapsible panel preserves existing task UI (FR-004)
- React state manages local message display
- API calls to /api/chat endpoint

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Third-party chat widget | Doesn't integrate with existing auth |
| Full-page chat | Violates FR-004 (must not replace task UI) |
| WebSocket-based | Adds complexity, HTTP sufficient for MVP |

**Component Structure**:
```
ChatPanel (collapsible container)
├── ChatHeader (title, new conversation button)
├── MessageList (scrollable message history)
│   └── Message (user or assistant message)
└── ChatInput (text input + send button)
```

### 6. Authentication & Authorization Flow

**Decision**: Reuse existing JWT authentication for chat endpoint

**Rationale**:
- Spec requires: "User identity from JWT token, never from request body"
- Existing `get_current_user()` middleware works unchanged
- MCP tools receive user context from authenticated request
- No additional auth infrastructure needed

**Flow**:
1. Frontend sends chat message with Bearer token
2. Chat endpoint validates JWT via existing middleware
3. User ID extracted from token, passed to MCP tools
4. Tools filter operations by user_id

### 7. Error Handling & Edge Cases

**Decision**: Graceful degradation with user-friendly messages

**Strategies**:
| Scenario | Handling |
|----------|----------|
| AI service unavailable | Return friendly error, suggest traditional UI |
| Empty message | Client-side validation, reject submission |
| Long message (>2000 chars) | Truncate with notification |
| Rapid-fire messages | Queue with typing indicator |
| Ambiguous intent | Agent asks for clarification |
| Destructive action | Agent confirms before execution |

### 8. Performance Considerations

**Decision**: Streaming responses with timeout handling

**Strategies**:
- Stream agent responses to show progress
- 30-second timeout on AI operations
- Cache MCP tool list (tools don't change during session)
- Limit conversation context to 20 messages
- Paginate task lists in responses

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| AI Agent Framework | OpenAI Agents SDK | Latest |
| MCP SDK | mcp (Python) | Latest |
| LLM Provider | OpenAI GPT-4 | gpt-4o |
| Transport | Streamable HTTP | - |
| Frontend | React (existing) | 18.3.1 |
| Backend | FastAPI (existing) | Latest |
| Database | PostgreSQL (existing) | - |

## Dependencies to Add

**Backend (requirements.txt)**:
```
openai-agents>=0.2.0
mcp>=1.0.0
```

**Frontend (package.json)**:
```json
{
  "dependencies": {
    // No new dependencies - using existing React/fetch
  }
}
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI latency affects UX | Medium | Medium | Streaming responses, typing indicators |
| Tool hallucination | Low | High | Strict tool schemas, validation |
| Token cost overruns | Medium | Medium | Context window limits, caching |
| MCP integration complexity | Medium | Medium | Start with function_tool, add MCP later |

## Open Questions Resolved

1. **Q: Function tools vs MCP tools?**
   A: Start with `@function_tool` decorator for simplicity; MCP server optional for future extensibility.

2. **Q: Conversation history in agent context?**
   A: Load last 20 messages, full history in DB for UI.

3. **Q: Real-time updates?**
   A: HTTP polling for MVP; WebSocket/SSE for future enhancement.

## Conclusion

The research validates the technical approach outlined in the specification. The OpenAI Agents SDK with function tools provides the simplest path to implementation while maintaining MCP compatibility for future expansion. No clarifications needed - proceed to Phase 1 design.
