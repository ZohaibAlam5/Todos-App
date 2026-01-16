# Tasks: Embedded AI Chatbot for Todo Management

**Input**: Design documents from `/specs/002-embedded-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Based on plan.md structure from Phase 2 web application

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup for AI chatbot feature

- [ ] T001 Add openai-agents dependency to backend/requirements.txt
- [ ] T002 [P] Add OPENAI_API_KEY to backend/src/config.py configuration
- [ ] T003 [P] Create backend/src/tools/ directory with __init__.py
- [ ] T004 [P] Extend frontend/src/types/index.ts with Chat types (ChatRequest, ChatResponse, Message, Conversation, ToolCallInfo)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [ ] T005 Create Conversation model in backend/src/models/conversation.py per data-model.md
- [ ] T006 [P] Create Message model with MessageRole enum in backend/src/models/message.py per data-model.md
- [ ] T007 Export new models from backend/src/models/__init__.py
- [ ] T008 Update backend/src/database/init_db.py to import new models for table creation

### Task Service Extraction

- [ ] T009 Create TaskService class in backend/src/services/task_service.py extracting logic from tasks_routes.py (get_tasks, create_task, update_task, delete_task, toggle_completion methods accepting user_id parameter)

### Chat Infrastructure

- [ ] T010 Create ChatService class in backend/src/services/chat_service.py with conversation management methods (create_conversation, get_conversation, get_or_create_conversation, add_message, get_messages, get_user_conversations)
- [ ] T011 Create chat API router in backend/src/api/chat_routes.py with placeholder POST /api/chat endpoint (auth required, returns 501 Not Implemented)
- [ ] T012 Register chat_router in backend/src/main.py

### Frontend Chat Infrastructure

- [ ] T013 Create chat service in frontend/src/services/chat.ts with sendMessage, getConversations, getConversation methods
- [ ] T014 [P] Create ChatInput component in frontend/src/components/ChatInput.tsx (text input with send button, disabled while processing)
- [ ] T015 [P] Create ChatMessage component in frontend/src/components/ChatMessage.tsx (displays user/assistant messages with role styling)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Task via Chat (Priority: P1) MVP

**Goal**: Enable authenticated users to create tasks through natural language chat

**Independent Test**: Send "Create a task called buy milk" via chat and verify task appears in both chat response and traditional task list

### Implementation for User Story 1

- [ ] T016 [US1] Implement add_task function tool in backend/src/tools/task_tools.py using @function_tool decorator (calls TaskService.create_task, accepts title, description, priority, tags parameters)
- [ ] T017 [US1] Create AI agent configuration in backend/src/services/chat_service.py with Agent class (name="Todo Assistant", instructions for task management, tools=[add_task])
- [ ] T018 [US1] Implement process_message method in ChatService that runs Agent with user message and returns response with tool_calls
- [ ] T019 [US1] Update POST /api/chat endpoint in backend/src/api/chat_routes.py to call ChatService.process_message, persist user/assistant messages, return ChatResponse
- [ ] T020 [US1] Create ChatPanel component in frontend/src/components/ChatPanel.tsx (collapsible panel, message list, input field, sends messages via chat service)
- [ ] T021 [US1] Integrate ChatPanel into frontend/src/app/dashboard/page.tsx (show only for authenticated users, position as floating button/panel)
- [ ] T022 [US1] Add conversation state management to ChatPanel (tracks current conversation_id, message history)
- [ ] T023 [US1] Handle ambiguous requests in agent instructions (ask for clarification when task title is unclear)

**Checkpoint**: User Story 1 complete - users can create tasks via chat

---

## Phase 4: User Story 2 - List and Search Tasks via Chat (Priority: P1)

**Goal**: Enable authenticated users to query and search their tasks through natural language

**Independent Test**: Send "Show me all my tasks" and verify response lists all user's tasks accurately

### Implementation for User Story 2

- [ ] T024 [US2] Implement list_tasks function tool in backend/src/tools/task_tools.py (calls TaskService.get_tasks with optional filters: completed, priority, tags)
- [ ] T025 [US2] Add list_tasks tool to Agent tools list in backend/src/services/chat_service.py
- [ ] T026 [US2] Update agent instructions to handle task listing queries (show title, priority, completion status)
- [ ] T027 [US2] Handle empty task list case in agent instructions (suggest creating a task)
- [ ] T028 [US2] Format task list display in ChatMessage component to handle multi-line responses

**Checkpoint**: User Stories 1 AND 2 complete - users can create and list tasks via chat

---

## Phase 5: User Story 3 - Complete Tasks via Chat (Priority: P2)

**Goal**: Enable authenticated users to mark tasks as complete through natural language

**Independent Test**: Create a task, then send "Mark [task] as complete" and verify task completion in both chat response and traditional UI

### Implementation for User Story 3

- [ ] T029 [US3] Implement complete_task function tool in backend/src/tools/task_tools.py (calls TaskService.toggle_completion, accepts task identifier - id or title match)
- [ ] T030 [US3] Add complete_task tool to Agent tools list in backend/src/services/chat_service.py
- [ ] T031 [US3] Update agent instructions to handle completion requests (find task by partial match, confirm action)
- [ ] T032 [US3] Handle ambiguous task match in agent (ask user to clarify when multiple tasks match)
- [ ] T033 [US3] Handle non-existent task case in agent instructions (inform user task not found)

**Checkpoint**: Users can create, list, and complete tasks via chat

---

## Phase 6: User Story 4 - Update Tasks via Chat (Priority: P2)

**Goal**: Enable authenticated users to update task attributes through natural language

**Independent Test**: Create a task with medium priority, send "Set [task] priority to high" and verify update in both chat response and traditional UI

### Implementation for User Story 4

- [ ] T034 [US4] Implement update_task function tool in backend/src/tools/task_tools.py (calls TaskService.update_task, accepts task identifier and update fields: title, description, priority, tags)
- [ ] T035 [US4] Add update_task tool to Agent tools list in backend/src/services/chat_service.py
- [ ] T036 [US4] Update agent instructions to handle update requests (priority changes, tag additions, title renames)
- [ ] T037 [US4] Handle partial updates in update_task tool (only modify provided fields)

**Checkpoint**: Users can create, list, complete, and update tasks via chat

---

## Phase 7: User Story 5 - Delete Tasks via Chat (Priority: P3)

**Goal**: Enable authenticated users to delete tasks through natural language with confirmation

**Independent Test**: Create a task, send "Delete [task]", confirm deletion, and verify task removed from traditional UI

### Implementation for User Story 5

- [ ] T038 [US5] Implement delete_task function tool in backend/src/tools/task_tools.py (calls TaskService.delete_task, requires task identifier)
- [ ] T039 [US5] Add delete_task tool to Agent tools list in backend/src/services/chat_service.py
- [ ] T040 [US5] Update agent instructions to ALWAYS ask for confirmation before delete (FR-007)
- [ ] T041 [US5] Implement confirmation flow in agent (track pending deletion state, wait for user yes/no)
- [ ] T042 [US5] Handle cancelled deletion in agent (acknowledge cancellation, task preserved)

**Checkpoint**: All task operations available via chat (CRUD + complete)

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P2)

**Goal**: Enable conversation history to persist across browser sessions

**Independent Test**: Start conversation, create task via chat, close browser, reopen, verify previous messages visible and context preserved

### Implementation for User Story 6

- [ ] T043 [US6] Implement GET /api/chat/conversations endpoint in backend/src/api/chat_routes.py (list user conversations with pagination)
- [ ] T044 [US6] Implement GET /api/chat/conversations/{id} endpoint in backend/src/api/chat_routes.py (get conversation with messages)
- [ ] T045 [US6] Update ChatPanel to load existing conversations on mount via chat service
- [ ] T046 [US6] Add conversation selector/list to ChatPanel (show recent conversations, switch between them)
- [ ] T047 [US6] Implement "New Conversation" button in ChatPanel (creates fresh conversation, preserves history)
- [ ] T048 [US6] Load conversation context into agent (last 20 messages per AD-003 decision)
- [ ] T049 [US6] Auto-generate conversation title from first user message in ChatService

**Checkpoint**: Full conversation persistence - users can continue chats across sessions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Edge case handling, error handling, and UX improvements

### Error Handling

- [ ] T050 Handle AI service unavailable (503) in backend/src/api/chat_routes.py with friendly error message
- [ ] T051 [P] Handle AI service errors gracefully in ChatPanel (show error message, suggest traditional UI)
- [ ] T052 [P] Add message length validation in ChatInput (max 2000 chars, show warning)
- [ ] T053 Add empty message validation in ChatInput (prevent submission, show prompt)

### UX Improvements

- [ ] T054 [P] Add typing indicator to ChatPanel while waiting for AI response
- [ ] T055 [P] Add message queue handling for rapid submissions (process sequentially)
- [ ] T056 [P] Style ChatPanel with collapsible toggle button (floating icon when collapsed)
- [ ] T057 [P] Add scroll-to-bottom on new messages in ChatPanel
- [ ] T058 Ensure ChatPanel does not block TodoList interactions (z-index, positioning per FR-004)

### Security Hardening

- [ ] T059 Verify all tool invocations filter by authenticated user_id (audit task_tools.py)
- [ ] T060 Add rate limiting consideration for chat endpoint (document in chat_routes.py)

### Validation

- [ ] T061 Run quickstart.md validation - verify setup instructions work end-to-end
- [ ] T062 Verify Phase 2 functionality unaffected (existing task routes, auth, UI all work)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Foundation
  - US3-US6 (P2-P3) can proceed after Foundation (parallel if staffed)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation required - No dependencies on other stories
- **User Story 2 (P1)**: Foundation required - Independent of US1
- **User Story 3 (P2)**: Foundation required - Independent (uses same tools pattern)
- **User Story 4 (P2)**: Foundation required - Independent (uses same tools pattern)
- **User Story 5 (P3)**: Foundation required - Independent (uses same tools pattern)
- **User Story 6 (P2)**: Foundation required - Independent (conversation management)

### Within Each User Story

- Models before services
- Services before endpoints
- Backend before frontend integration
- Core implementation before edge cases

### Parallel Opportunities

- T002, T003, T004 can run in parallel (different files)
- T005, T006 can run in parallel (separate model files)
- T014, T015 can run in parallel (different frontend components)
- US1 and US2 can run in parallel after Foundation
- All [P] tasks within same phase can run in parallel
- All tool implementations (T016, T024, T029, T034, T038) follow same pattern

---

## Parallel Example: Foundation Phase

```bash
# Launch model creation in parallel:
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/message.py"

# Launch frontend components in parallel:
Task: "Create ChatInput component in frontend/src/components/ChatInput.tsx"
Task: "Create ChatMessage component in frontend/src/components/ChatMessage.tsx"
```

## Parallel Example: User Story 1 + 2

```bash
# After Foundation complete, launch both P1 stories:
# Developer A: User Story 1 (Create Task)
Task: "Implement add_task function tool in backend/src/tools/task_tools.py"
Task: "Create ChatPanel component in frontend/src/components/ChatPanel.tsx"

# Developer B: User Story 2 (List Tasks)
Task: "Implement list_tasks function tool in backend/src/tools/task_tools.py"
Task: "Format task list display in ChatMessage component"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Task)
4. Complete Phase 4: User Story 2 (List Tasks)
5. **STOP and VALIDATE**: Test creating and listing tasks via chat
6. Deploy/demo if ready - users have functional chatbot for basic task management

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test → Deploy (MVP with create/list)
3. Add User Story 3 + 4 → Test → Deploy (complete/update)
4. Add User Story 5 → Test → Deploy (delete with confirmation)
5. Add User Story 6 → Test → Deploy (conversation persistence)
6. Polish phase → Final release

### Suggested MVP Scope

**Minimum Viable Product**: User Stories 1 + 2 only
- Users can create tasks via natural language
- Users can list/query their tasks via natural language
- Basic chat UI embedded in dashboard
- Validates entire AI agent pipeline end-to-end

---

## Summary

| Phase | Tasks | Parallel Tasks | Description |
|-------|-------|----------------|-------------|
| Phase 1: Setup | 4 | 3 | Dependencies and config |
| Phase 2: Foundational | 11 | 3 | Models, services, routes |
| Phase 3: US1 Create | 8 | 0 | Create task via chat (P1) |
| Phase 4: US2 List | 5 | 0 | List tasks via chat (P1) |
| Phase 5: US3 Complete | 5 | 0 | Complete tasks via chat (P2) |
| Phase 6: US4 Update | 4 | 0 | Update tasks via chat (P2) |
| Phase 7: US5 Delete | 5 | 0 | Delete tasks via chat (P3) |
| Phase 8: US6 Persist | 7 | 0 | Conversation persistence (P2) |
| Phase 9: Polish | 13 | 6 | Edge cases, UX, security |
| **Total** | **62** | **12** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tools must enforce user_id filtering (security requirement)
- Agent instructions critical for proper NLP behavior
