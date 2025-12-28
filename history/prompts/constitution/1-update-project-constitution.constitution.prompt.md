---
id: 1
title: Update-Project-Constitution
stage: constitution
date: 2025-12-27
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: User
command: /sp.constitution
labels: ["constitution", "governance", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution

Project: Spec-Driven Todo Application (CLI → Web → AI → Cloud-Native)

Purpose:
This constitution defines the non-negotiable rules, standards, and governance model
for building a Todo application using Spec-Kit Plus and Claude Code.
The project evolves from a simple in-memory console app into a distributed,
cloud-native, AI-powered system using strict spec-driven development.

All implementation decisions must comply with this constitution.


--------------------------------------------------
CORE PRINCIPLES
--------------------------------------------------

1. Spec-Driven Authority
- Specifications are the single source of truth.
- Code must not exist without an approved specification.
- Behavior, architecture, APIs, and data models must originate from specs.
- If behavior is unclear, the specification must be refined before implementation.

2. Spec-First Development
- Specifications must always be written or updated before implementation.
- Manual edits to code are permitted only when explicitly allowed by the spec.
- Any manual change must remain fully compliant with the active specification.

3. Determinism & Reproducibility
- Given the same specs, the system must be reproducible.
- Specs must be explicit, deterministic, and unambiguous.
- Hidden assumptions are forbidden.

4. Progressive Evolution
- The system must evolve phase-by-phase.
- Earlier phases must remain functional as new capabilities are added.
- No breaking changes without explicit specification updates.

5. AI-Native Architecture
- AI agents are first-class system components.
- AI behavior must be governed, tool-based, and spec-defined.
- No uncontrolled or implicit AI behavior is allowed.


--------------------------------------------------
KEY STANDARDS
--------------------------------------------------

1. Specification Standards
- Every feature must have a dedicated spec file.
- Specs must include:
  - Purpose
  - User stories
  - Inputs and outputs
  - Constraints
  - Acceptance criteria
- Specs must be written in clear, structured Markdown.
- Vague language such as "should", "maybe", or "etc." is prohibited.

2. Constitutional Compliance
- All implementations must comply with this constitution.
- If a spec conflicts with the constitution, the constitution overrides the spec.
- Violations must be resolved by updating the spec or constitution, not by ad-hoc code changes.

3. Traceability
- Every feature must be traceable to a spec file.
- Every API, database field, and AI tool must map to a written specification.
- Undocumented functionality is forbidden.

4. Error Handling Standards
- Errors must be explicit, descriptive, and deterministic.
- Silent failures are forbidden.
- User-facing errors must be human-readable.
- System errors must be logged and traceable.

5. Security & Isolation
- User data must be isolated per user.
- Authentication and authorization rules must be enforced at every layer.
- No endpoint or tool may bypass user identity verification.


--------------------------------------------------
TECHNOLOGY CONSTRAINTS
--------------------------------------------------

1. Development Stack
- Spec-Kit Plus for specification management
- Claude Code for AI-assisted implementation
- Python (CLI & backend)
- FastAPI for backend services
- Next.js for frontend
- SQLModel with PostgreSQL for persistence
- OpenAI Agents SDK + MCP SDK for AI tooling
- Docker and Kubernetes for deployment

2. Forbidden Actions
- Modifying system behavior without updating the corresponding specification
- Adding libraries, services, or infrastructure not defined in specs
- Introducing undocumented endpoints, tools, or database fields
- Hardcoding secrets or credentials
- Bypassing authentication or authorization rules

3. Environment Configuration
- All secrets must come from environment variables or secret managers.
- No credentials may be committed to version control.


--------------------------------------------------
AI AGENT GOVERNANCE
--------------------------------------------------

1. Tool-Based Control
- AI agents may only act through explicitly defined tools.
- Tools must be stateless and spec-defined.
- Direct database or filesystem access by AI is forbidden unless specified.

2. Predictable Behavior
- AI agents must follow deterministic decision rules.
- Natural language input must map to explicit tool calls.
- All AI actions must be explainable and traceable.

3. Safety & Validation
- AI agents must validate inputs before executing tools.
- Invalid or ambiguous commands must result in clarification requests.
- Destructive actions require explicit user intent.


--------------------------------------------------
QUALITY & REVIEW RULES
--------------------------------------------------

1. Acceptance Criteria Enforcement
- Every feature must satisfy all acceptance criteria defined in its spec.
- Partial implementations are not acceptable.

2. Testing Responsibility
- Specs must define testable outcomes.
- Implementations must include tests where applicable.
- AI behavior must be validated against example scenarios.

3. Documentation Quality
- Specs must be readable by humans and machines.
- README files must reflect actual system behavior.
- Outdated documentation is considered a defect.


--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

The project is considered successful when:

- All features are traceable to specifications
- Specifications remain the source of truth
- Each phase builds correctly on the previous phase
- AI agents operate only through defined MCP tools
- The system can be reproduced from specs and repository state
- The application passes functional, security, and architectural review


--------------------------------------------------
ENFORCEMENT
--------------------------------------------------

- Any violation of this constitution invalidates the implementation.
- Fixes must occur at the specification or constitution level.
- The constitution may only be changed intentionally and explicitly.
- Silence or ambiguity does not imply permission.

This constitution is binding for the entire lifecycle of the project.

## Response snapshot

The project constitution has been successfully updated with the provided content. The new constitution establishes the "Spec-Driven Todo Application (CLI → Web → AI → Cloud-Native)" with 6 core principles: Spec-Driven Authority, Spec-First Development, Determinism & Reproducibility, Progressive Evolution, AI-Native Architecture, and Constitutional Compliance.

The constitution also includes comprehensive sections on:
- Key Standards and Technology Constraints
- Specification Standards
- Traceability requirements
- Error Handling Standards
- Security & Isolation
- Development Stack requirements
- Forbidden Actions
- Environment Configuration
- AI Agent Governance
- Quality & Review Rules
- Success Criteria and Enforcement

The file `.specify/memory/constitution.md` has been created with version 1.0.0, ratified on 2025-12-27.

## Outcome

- ✅ Impact: Project constitution fully updated with comprehensive governance framework
- 🧪 Tests: No tests required for documentation update
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Ready to create feature specifications based on this constitution
- 🧠 Reflection: Constitution provides clear governance framework for spec-driven development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin creating feature specifications based on the constitution