---
description: "Task list template for feature implementation"
---

# Tasks: Console-Based Todo Application

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/` or `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /sp.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python 3.11 project with built-in libraries dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Create Task model with validation in src/models/task.py
- [ ] T005 [P] Setup in-memory storage framework in src/services/todo_service.py
- [ ] T006 [P] Setup CLI routing and menu structure in src/cli/main.py
- [ ] T007 Create input validation utilities in src/lib/validators.py
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Core functionality to add tasks and view them in the system

**Independent Test**: Can be fully tested by adding a task and then listing all tasks to verify it appears in the list. This delivers the basic value of a todo list.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for add_task endpoint in tests/contract/test_add_task.py
- [ ] T011 [P] [US1] Contract test for view_tasks endpoint in tests/contract/test_view_tasks.py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create Task model with all required fields in src/models/task.py
- [ ] T013 [P] [US1] Implement task creation logic in src/services/todo_service.py
- [ ] T014 [US1] Implement add_task functionality in src/cli/main.py
- [ ] T015 [US1] Implement view_tasks functionality in src/cli/main.py
- [ ] T016 [US1] Add validation for task title and description length limits
- [ ] T017 [US1] Add logging for task creation and viewing operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update and Complete Tasks (Priority: P2)

**Goal**: Allow users to modify tasks and mark them as complete

**Independent Test**: Can be fully tested by adding a task, updating its details, and toggling its completion status. This delivers task management functionality.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for update_task endpoint in tests/contract/test_update_task.py
- [ ] T019 [P] [US2] Contract test for toggle_task_status endpoint in tests/contract/test_toggle_status.py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Add update_task logic in src/services/todo_service.py
- [ ] T021 [P] [US2] Add toggle_task_status logic in src/services/todo_service.py
- [ ] T022 [US2] Implement update_task CLI interface in src/cli/main.py
- [ ] T023 [US2] Implement toggle_task_status CLI interface in src/cli/main.py
- [ ] T024 [US2] Add validation for task updates
- [ ] T025 [US2] Integrate with User Story 1 components

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete and Search Tasks (Priority: P3)

**Goal**: Allow users to remove tasks and search through their tasks

**Independent Test**: Can be fully tested by adding multiple tasks, searching for specific ones by keywords, and deleting unwanted tasks. This delivers advanced management capabilities.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T026 [P] [US3] Contract test for delete_task endpoint in tests/contract/test_delete_task.py
- [ ] T027 [P] [US3] Contract test for search_tasks endpoint in tests/contract/test_search_tasks.py

### Implementation for User Story 3

- [ ] T028 [P] [US3] Add delete_task logic in src/services/todo_service.py
- [ ] T029 [P] [US3] Add search_tasks logic in src/services/todo_service.py
- [ ] T030 [US3] Implement delete_task CLI interface in src/cli/main.py
- [ ] T31 [US3] Implement search_tasks CLI interface in src/cli/main.py
- [ ] T032 [US3] Add case-insensitive search functionality
- [ ] T033 [US3] Integrate with User Story 1 and 2 components

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Filter and Sort Tasks (Priority: P4)

**Goal**: Allow users to filter and sort tasks by different criteria

**Independent Test**: Can be fully tested by adding tasks with different priorities and tags, then filtering and sorting by various criteria. This delivers advanced organizational functionality.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [ ] T034 [P] [US4] Contract test for filter_tasks endpoint in tests/contract/test_filter_tasks.py
- [ ] T035 [P] [US4] Contract test for sort_tasks endpoint in tests/contract/test_sort_tasks.py

### Implementation for User Story 4

- [ ] T036 [P] [US4] Add filter_tasks logic in src/services/todo_service.py
- [ ] T037 [P] [US4] Add sort_tasks logic in src/services/todo_service.py
- [ ] T038 [US4] Implement filter_tasks CLI interface in src/cli/main.py
- [ ] T039 [US4] Implement sort_tasks CLI interface in src/cli/main.py
- [ ] T040 [US4] Add support for multiple filter criteria
- [ ] T041 [US4] Add support for different sort orders
- [ ] T042 [US4] Integrate with previous user story components

**Checkpoint**: All user stories should now be independently functional

---

[Add more user stories as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T043 [P] Documentation updates in docs/
- [ ] T044 Code cleanup and refactoring
- [ ] T045 Performance optimization across all stories
- [ ] T046 [P] Additional unit tests (if requested) in tests/unit/
- [ ] T047 Security hardening
- [ ] T048 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for add_task endpoint in tests/contract/test_add_task.py"
Task: "Contract test for view_tasks endpoint in tests/contract/test_view_tasks.py"

# Launch all models for User Story 1 together:
Task: "Create Task model with all required fields in src/models/task.py"
Task: "Implement task creation logic in src/services/todo_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence