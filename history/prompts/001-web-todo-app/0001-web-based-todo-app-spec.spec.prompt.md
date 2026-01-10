---
id: 0001
title: "Web-Based Todo App Spec"
stage: spec
date: 2026-01-01
surface: agent
model: Claude Sonnet 4.5
feature: 001-web-todo-app
branch: 001-web-todo-app
user: claude
command: "/sp.specify Phase 2: Full-Stack Web-Based Todo Application"
labels: ["spec", "todo-app", "authentication", "multi-user", "web"]
links:
  spec: "specs/001-web-todo-app/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "specs/001-web-todo-app/spec.md"
  - "specs/001-web-todo-app/checklists/requirements.md"
  - "history/prompts/001-web-todo-app/0001-web-based-todo-app-spec.spec.prompt.md"
tests:
  - "none"
---

## Prompt

/sp.specify Phase 2: Full-Stack Web-Based Todo Application

Target audience:
- Developers advancing from console to full-stack systems
- Hackathon evaluators reviewing spec-driven workflows
- AI agents (Claude Code) responsible for implementation

Focus:
- Transforming the Phase 1 console Todo app into a modern web application
- Introducing persistent storage, multi-user support, and authentication
- Preserving all Phase 1 features while enabling web-based interaction


--------------------------------------------------
PROJECT CONTEXT
--------------------------------------------------

Phase 1 delivered a fully functional, single-user, in-memory console Todo app
supporting all Basic and Intermediate features.

Phase 2 upgrades the system into a **full-stack, multi-user web application**
with a RESTful backend, responsive frontend, and persistent database storage.

All Phase 1 features must remain functionally intact, now accessed via a web UI.


--------------------------------------------------
FEATURE REQUIREMENTS
--------------------------------------------------

### Carried-Forward Features (From Phase 1)

The following features must be fully supported in the web application:

- Add task
- View task list
- Update task
- Delete task
- Mark task as complete / incomplete
- Priority management (High / Medium / Low)
- Tags / categories
- Search by keyword
- Filter by status, priority, and tags
- Sort by title, priority, and creation order


--------------------------------------------------
NEW PHASE 2 FEATURES (MANDATORY)
--------------------------------------------------

1. Multi-User Support
- Each user has an independent task list
- Users must not see or modify other users' tasks

2. Authentication
- Users can sign up and sign in
- Authentication must be handled via Better Auth
- JWT tokens must be issued and validated on every API request

3. Persistent Storage
- Tasks must be stored in a PostgreSQL database
- Data must persist across server restarts

4. RESTful API Layer
- Backend must expose REST endpoints for all task operations
- All endpoints must be secured with JWT authentication
- API behavior must be deterministic and spec-defined

5. Responsive Web Interface
- Users interact with the Todo app via a web browser
- UI must support desktop and mobile layouts
- UI must expose all task features without loss of functionality


--------------------------------------------------
TECHNICAL ARCHITECTURE
--------------------------------------------------

### Frontend
- Framework: Next.js (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- Authentication client: Better Auth
- API communication via HTTP requests

### Backend
- Framework: Python FastAPI
- ORM: SQLModel
- Authentication: JWT verification
- Business logic exposed via REST endpoints

### Database
- PostgreSQL (Neon Serverless)
- One-to-many relationship: User → Tasks


--------------------------------------------------
API REQUIREMENTS
--------------------------------------------------

Base path: `/api/{user_id}/tasks`

Endpoints:

- GET    /api/{user_id}/tasks
- POST   /api/{user_id}/tasks
- GET    /api/{user_id}/tasks/{id}
- PUT    /api/{user_id}/tasks/{id}
- DELETE /api/{user_id}/tasks/{id}
- PATCH  /api/{user_id}/tasks/{id}/complete

All endpoints:
- Require valid JWT token
- Must verify user identity matches `{user_id}`
- Must return JSON responses only


--------------------------------------------------
DATA MODEL REQUIREMENTS
--------------------------------------------------

Task entity must include:

- id: integer (primary key)
- user_id: string (foreign key)
- title: string
- description: string (optional)
- completed: boolean
- priority: enum (High | Medium | Low)
- tags: array of strings
- created_at: timestamp
- updated_at: timestamp


--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

Phase 2 is successful when:

- All Phase 1 features work through the web UI
- Multiple users can use the system independently
- Authentication and authorization are enforced everywhere
- Tasks persist in the database
- REST API behavior matches this specification
- Frontend and backend integrate correctly
- No Phase 1 functionality is lost


--------------------------------------------------
CONSTRAINTS
--------------------------------------------------

- Web-based interaction only (no console UI)
- Database-backed persistence required
- JWT authentication required for all API calls
- Single backend service (no microservices yet)
- No AI, chatbot, or MCP features in this phase


--------------------------------------------------
NOT BUILDING (EXPLICITLY OUT OF SCOPE)
--------------------------------------------------

- AI-powered chatbot
- Natural language task management
- MCP server or agent tools
- Kubernetes or Docker deployment
- Event-driven architecture
- Notifications or reminders
- Recurring tasks
- Voice input
- Multi-language UI


--------------------------------------------------
DELIVERY EXPECTATION
--------------------------------------------------

- Functional full-stack web application
- Public GitHub repository
- Deployed frontend (e.g., Vercel)
- Running backend API
- Specs updated to reflect final behavior
- Implementation traceable back to this specification

## Response snapshot

Created comprehensive specification for the web-based multi-user todo application with 5 prioritized user stories, 20 functional requirements, key entities, and 10 success criteria. Specification includes authentication, multi-user isolation, persistent storage, and all Phase 1 features preserved in web interface.

## Outcome

- ✅ Impact: Complete feature specification created with all requirements from Phase 2 description
- 🧪 Tests: none
- 📁 Files: specs/001-web-todo-app/spec.md, specs/001-web-todo-app/checklists/requirements.md, history/prompts/001-web-todo-app/0001-web-based-todo-app-spec.spec.prompt.md
- 🔁 Next prompts: /sp.plan to create implementation plan
- 🧠 Reflection: Specification successfully captures all Phase 1 features while adding required Phase 2 functionality with proper user isolation and authentication

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
