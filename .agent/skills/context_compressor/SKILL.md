---
name: context-compressor
description: Exports and compresses the active chat context into structured markdown files (context_export.md, initial_request.md, master_refactor_plan.md) stored in llm-context/YYYY-MM-DD/ at the root of the repository. Ensures llm-context/ is added to .gitignore. Activate this skill whenever the user asks to compress, export, or save the conversation context to transition to a new chat window.
---

# Context Compressor Skill (`context-compressor`)

This skill extracts, compresses, and structures the full active conversation state, architectural decisions, initial requirements, and execution plan into a standardized handoff package inside `llm-context/<YYYY-MM-DD>/` at the repository root.

---

## 1. Trigger Specification

- **Manual Launch Command:** `@context-compressor` or `run skill context-compressor`
- **Activation Keywords:** `compress context`, `export session context`, `save chat context`, `export context`, `save session`, `prepare chat handoff`

---

## 2. Handoff Package Directory Layout

The skill creates a dated directory under `<REPO_ROOT>/llm-context/<YYYY-MM-DD>/`:

```text
cleanmybelly/
├── llm-context/
│   └── YYYY-MM-DD/
│       ├── context_export.md        # Technical summary, diagnostics, decisions & instructions for new AI session
│       ├── initial_request.md       # Polished, original user request and requirements
│       └── master_refactor_plan.md  # Complete plan (Approved items, Proposals, Open Questions)
└── .gitignore                       # Automatically updated to contain `llm-context/`
```

---

## 3. Execution Workflow & File Protocol

When activated, execute these 4 steps in order:

### Step 1: Ensure Git Ignore Safety
Verify that `<REPO_ROOT>/.gitignore` contains an entry for `llm-context/`. If missing, append `# LLM Context Export\nllm-context/\n` to `.gitignore`.

### Step 2: Create `initial_request.md`
Write `<REPO_ROOT>/llm-context/<YYYY-MM-DD>/initial_request.md` containing:
- The user's original task prompt, polished for readability.
- Technical requirements, architectural constraints, and target validations.

### Step 3: Create `context_export.md`
Write `<REPO_ROOT>/llm-context/<YYYY-MM-DD>/context_export.md` containing:
- **Session Metadata**: Date, repo path, task focus.
- **Completed Milestones**: Audits, diagnostics, and code/document changes made in the session.
- **Diagnostic Table**: Status of all codebase modules, identified issues, and hardcoded values.
- **Agreed Decisions**: Explicit technical choices confirmed by the user.
- **AI Handoff Instructions**: 3-step action guide for the AI assistant in the new session.

### Step 4: Create `master_refactor_plan.md`
Write `<REPO_ROOT>/llm-context/<YYYY-MM-DD>/master_refactor_plan.md` divided into 3 clear sections:
- **Part 1: APPROVED & READY FOR EXECUTION**: Every strategy confirmed by the user.
- **Part 2: PROPOSED IMPLEMENTATION PLAN**: Step-by-step technical execution plan (with diagrams or specs).
- **Part 3: OPEN QUESTIONS & DECISIONS**: Explicit decision points placed at the bottom for immediate follow-up.

---

## 4. Quality Checklist

Before completing:
- [ ] Is the package stored in `llm-context/<YYYY-MM-DD>/` relative to the repository root?
- [ ] Is `llm-context/` listed in `.gitignore`?
- [ ] Are all 3 markdown files (`context_export.md`, `initial_request.md`, `master_refactor_plan.md`) created and complete?
- [ ] Are there NO machine-specific absolute host paths (e.g. `/home/user/...`, `/Users/dev/...`) in the generated files?
