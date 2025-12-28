<!--
Sync Impact Report:
Version change: N/A → 1.0.0
Modified principles: N/A
Added sections: All principles and sections from user input
Removed sections: Template placeholders
Templates requiring updates:
- ✅ .specify/templates/plan-template.md (Constitution Check section now aligned with new principles)
- ✅ .specify/templates/spec-template.md (no direct changes needed)
- ✅ .specify/templates/tasks-template.md (no direct changes needed)
- ✅ .claude/commands/sp.constitution.md (this command file follows the template)
Follow-up TODOs: None
-->
# Spec-Driven Todo Application (CLI → Web → AI → Cloud-Native) Constitution

## Core Principles

### Spec-Driven Authority
Specifications are the single source of truth. Code must not exist without an approved specification. Behavior, architecture, APIs, and data models must originate from specs. If behavior is unclear, the specification must be refined before implementation.

### Spec-First Development
Specifications must always be written or updated before implementation. Manual edits to code are permitted only when explicitly allowed by the spec. Any manual change must remain fully compliant with the active specification.

### Determinism & Reproducibility
Given the same specs, the system must be reproducible. Specs must be explicit, deterministic, and unambiguous. Hidden assumptions are forbidden.

### Progressive Evolution
The system must evolve phase-by-phase. Earlier phases must remain functional as new capabilities are added. No breaking changes without explicit specification updates.

### AI-Native Architecture
AI agents are first-class system components. AI behavior must be governed, tool-based, and spec-defined. No uncontrolled or implicit AI behavior is allowed.

### Constitutional Compliance
All implementations must comply with this constitution. If a spec conflicts with the constitution, the constitution overrides the spec. Violations must be resolved by updating the spec or constitution, not by ad-hoc code changes.

## Key Standards and Technology Constraints

### Specification Standards
- Every feature must have a dedicated spec file.
- Specs must include:
  - Purpose
  - User stories
  - Inputs and outputs
  - Constraints
  - Acceptance criteria
- Specs must be written in clear, structured Markdown.
- Vague language such as "should", "maybe", or "etc." is prohibited.

### Traceability
- Every feature must be traceable to a spec file.
- Every API, database field, and AI tool must map to a written specification.
- Undocumented functionality is forbidden.

### Error Handling Standards
- Errors must be explicit, descriptive, and deterministic.
- Silent failures are forbidden.
- User-facing errors must be human-readable.
- System errors must be logged and traceable.

### Security & Isolation
- User data must be isolated per user.
- Authentication and authorization rules must be enforced at every layer.
- No endpoint or tool may bypass user identity verification.

### Development Stack
- Spec-Kit Plus for specification management
- Claude Code for AI-assisted implementation
- Python (CLI & backend)
- FastAPI for backend services
- Next.js for frontend
- SQLModel with PostgreSQL for persistence
- OpenAI Agents SDK + MCP SDK for AI tooling
- Docker and Kubernetes for deployment

### Forbidden Actions
- Modifying system behavior without updating the corresponding specification
- Adding libraries, services, or infrastructure not defined in specs
- Introducing undocumented endpoints, tools, or database fields
- Hardcoding secrets or credentials
- Bypassing authentication or authorization rules

### Environment Configuration
- All secrets must come from environment variables or secret managers.
- No credentials may be committed to version control.

### AI Agent Governance
#### Tool-Based Control
- AI agents may only act through explicitly defined tools.
- Tools must be stateless and spec-defined.
- Direct database or filesystem access by AI is forbidden unless specified.

#### Predictable Behavior
- AI agents must follow deterministic decision rules.
- Natural language input must map to explicit tool calls.
- All AI actions must be explainable and traceable.

#### Safety & Validation
- AI agents must validate inputs before executing tools.
- Invalid or ambiguous commands must result in clarification requests.
- Destructive actions require explicit user intent.

### Quality & Review Rules
#### Acceptance Criteria Enforcement
- Every feature must satisfy all acceptance criteria defined in its spec.
- Partial implementations are not acceptable.

#### Testing Responsibility
- Specs must define testable outcomes.
- Implementations must include tests where applicable.
- AI behavior must be validated against example scenarios.

#### Documentation Quality
- Specs must be readable by humans and machines.
- README files must reflect actual system behavior.
- Outdated documentation is considered a defect.

## Success Criteria and Enforcement

### Success Criteria
The project is considered successful when:
- All features are traceable to specifications
- Specifications remain the source of truth
- Each phase builds correctly on the previous phase
- AI agents operate only through defined MCP tools
- The system can be reproduced from specs and repository state
- The application passes functional, security, and architectural review

### Enforcement
- Any violation of this constitution invalidates the implementation.
- Fixes must occur at the specification or constitution level.
- The constitution may only be changed intentionally and explicitly.
- Silence or ambiguity does not imply permission.

This constitution is binding for the entire lifecycle of the project.

## Governance

The constitution serves as the governing document for all development activities. All implementations must comply with this constitution. If a spec conflicts with the constitution, the constitution overrides the spec. Violations must be resolved by updating the spec or constitution, not by ad-hoc code changes. The constitution may only be changed intentionally and explicitly, with any amendments requiring proper documentation and approval.

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27