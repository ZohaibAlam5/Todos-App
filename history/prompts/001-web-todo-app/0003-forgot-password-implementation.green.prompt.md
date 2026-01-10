---
id: "0003"
title: "Forgot Password Implementation"
stage: "green"
date: "2026-01-09"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "001-web-todo-app"
branch: "001-web-todo-app"
user: "zohai"
command: "/sp.phr"
labels: ["authentication", "password-reset", "security", "frontend", "backend", "react", "fastapi"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "backend/src/services/auth_service.py"
  - "backend/src/api/auth_routes.py"
  - "frontend/src/services/auth.ts"
  - "frontend/src/components/AuthForm.tsx"
tests: []
---

# Forgot Password Implementation

## PROMPT_TEXT

<command-message>sp.phr</command-message>
<command-name>/sp.phr</command-name># COMMAND: Record this AI exchange as a structured PHR artifact

## CONTEXT

The user has just completed work (or is requesting work) and needs to capture this exchange as a Prompt History Record (PHR) for:

- Learning and pattern recognition (spaced repetition)
- Team knowledge sharing and traceability
- Compliance and audit requirements
- Building a searchable corpus of effective prompts

**User's input to record:**

$ARGUMENTS

**CRITICAL**: The complete text above is the PROMPT to preserve verbatim. Do NOT truncate to first line only.

## YOUR ROLE

Act as a meticulous documentation specialist with expertise in:

- Knowledge management and organizational learning
- Software development lifecycle documentation
- Metadata extraction and classification
- Creating structured, searchable technical records

## QUICK OVERVIEW (strict)

After completing ANY work, automatically create a PHR:

1. **Detect work type**: constitution|spec|plan|tasks|implementation|debugging|refactoring|discussion|general
2. **Generate title**: 3-7 word descriptive title summarizing the work
3. **Capture context**: COMPLETE conversation (never truncate to summaries)
4. **Route correctly**:
   - Pre-feature work → `history/prompts/`
   - Feature-specific work → `specs/<feature>/prompts/`
5. **Confirm**: Show "📝 PHR-NNNN recorded"

## OUTPUT STRUCTURE (with quick flywheel hooks)

Execute this workflow in 5 sequential steps, reporting progress after each:

## Step 1: Execute User's Request (if not already done)

If the user provided a task/question in $ARGUMENTS:

- Complete the requested work first
- Provide full response to user
- Then proceed to Step 2 to record the exchange

If you already completed work and user just wants to record it:

- Skip to Step 2

## Step 2: Determine Stage and Routing

Select ONE stage that best describes the work:

**Constitution** (→ `history/prompts/constitution/`):
- `constitution` - Defining quality standards, project principles

**Feature-specific** (→ `history/prompts/<feature-name>/` - requires feature context):
- `spec` - Creating feature specifications
- `plan` - Architecture design and technical approach
- `tasks` - Implementation breakdown with test cases
- `red` - Debugging, fixing errors, test failures
- `green` - Implementation, new features, passing tests
- `refactor` - Code cleanup, optimization
- `explainer` - Code explanations, documentation
- `misc` - Other feature-specific work

**General/Catch-all** (→ `history/prompts/general/`):
- `general` - General work not tied to a specific feature

## Step 5: Report Completion

## FORMATTING REQUIREMENTS

Present results in this exact structure:

```
✅ Exchange recorded as PHR-{id} in {context} context
📁 {relative-path-from-repo-root}

Stage: {stage}
Feature: {feature or "none"}
Files modified: {count}
Tests involved: {count}

Acceptance Criteria (PASS only if all true)
- Full prompt preserved verbatim (no truncation)
- Stage and routing determined correctly
- Metadata fields populated; missing values noted explicitly
```

## ERROR HANDLING

If create-phr.sh fails:

1. Display the exact error message from script
2. Explain what went wrong in plain language
3. Provide specific corrective action with commands
4. Do NOT fail silently or hide errors

## TONE

Be professional, concise, and action-oriented. Focus on what was accomplished and what's next.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.