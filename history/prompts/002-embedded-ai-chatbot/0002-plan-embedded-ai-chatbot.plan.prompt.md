---
id: 0002
title: Implementation Plan for Embedded AI Chatbot
stage: plan
date: 2026-01-15
surface: agent
model: claude-opus-4-5-20251101
feature: 002-embedded-ai-chatbot
branch: 002-embedded-ai-chatbot
user: system
command: /sp.plan
labels: ["phase-3", "ai-chatbot", "architecture", "openai-agents", "mcp"]
links:
  spec: specs/002-embedded-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-embedded-ai-chatbot/plan.md
  - specs/002-embedded-ai-chatbot/research.md
  - specs/002-embedded-ai-chatbot/data-model.md
  - specs/002-embedded-ai-chatbot/contracts/chat-api.yaml
  - specs/002-embedded-ai-chatbot/quickstart.md
  - CLAUDE.md
tests:
  - null
---

## Prompt

/sp.plan

Execute implementation planning workflow for Phase 3: Embedded AI Chatbot feature based on the specification in specs/002-embedded-ai-chatbot/spec.md.

## Response snapshot

Created comprehensive implementation plan for Phase 3 Embedded AI Chatbot:

**Phase 0: Research (Complete)**
- Selected OpenAI Agents SDK for AI agent framework
- Decided on @function_tool over separate MCP server for simplicity
- Chose HTTP polling over WebSockets for MVP
- Defined conversation context limit of 20 messages

**Phase 1: Design (Complete)**

Artifacts generated:
1. `plan.md` - Full implementation plan with:
   - Technical context (Python 3.11, TypeScript 5.x, FastAPI, Next.js)
   - Constitution check (all gates PASS)
   - AI Agent Governance check (all requirements PASS)
   - Project structure (backend + frontend changes)
   - 3 Architecture Decisions documented

2. `research.md` - Technology research including:
   - AI framework selection (OpenAI Agents SDK)
   - MCP vs function_tool decision
   - Integration patterns and code examples
   - Risk assessment

3. `data-model.md` - Database schema for:
   - Conversation entity (id, user_id, title, timestamps)
   - Message entity (id, conversation_id, role, content, tool_calls)
   - API schemas (ChatRequest, ChatResponse, ToolCallInfo)

4. `contracts/chat-api.yaml` - OpenAPI 3.1 specification:
   - POST /api/chat - Main chat endpoint
   - GET /api/chat/conversations - List user conversations
   - GET /api/chat/conversations/{id} - Get conversation with messages
   - Full request/response schemas with examples

5. `quickstart.md` - Development setup guide:
   - Environment variables (OPENAI_API_KEY)
   - Backend/frontend commands
   - Testing instructions
   - Architecture diagram

**Agent Context Updated**
- CLAUDE.md updated with new technologies for 002-embedded-ai-chatbot

**Ready for**: `/sp.tasks` to generate implementation tasks

## Outcome

- Impact: Created complete architectural plan enabling AI chatbot implementation
- Tests: N/A (planning phase)
- Files: 5 planning artifacts created, 1 agent context updated
- Next prompts: /sp.tasks (to generate implementation tasks)
- Reflection: Plan is comprehensive; all constitution gates passed; research resolved all unknowns

## Evaluation notes (flywheel)

- Failure modes observed: None - all research resolved, no clarifications needed
- Graders run and results (PASS/FAIL): Constitution Check PASS, AI Governance PASS, Security Check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - proceed to task generation
