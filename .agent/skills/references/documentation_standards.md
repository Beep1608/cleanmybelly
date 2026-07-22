# Documentation Standards & Taxonomy Reference

This document defines the authoritative guidelines for maintaining, writing, and auditing documentation in the **cleanmybelly** repository.

---

## 1. Language Rule
* **Mandatory English**: All documentation content (`.md` files) must be written strictly in **English**.
* Comments in code, diagrams, and markdown text must adhere to English technical terminology.

---

## 2. Directory Taxonomy & Single Responsibility Principle (SRP)

Every document must reside in its designated directory according to its purpose:

```text
docs/
├── README.md                              # MASTER INDEX: Central entry point & global navigation map
├── getting_started.md                     # LINEAR ONBOARDING: Step-by-step walkthrough from zero
├── architecture/                          # EXPLANATION: Conceptual understanding, data flows, diagrams
├── operations/                            # HOW-TO: Actionable step-by-step procedures for specific tasks
└── reference/                             # REFERENCE: Technical specs, directory layouts, YAML templates
```

### Directory Responsibilities:
1. **`docs/README.md` (Master Index)**:
   * Serves as the single entry point for all documentation.
   * Contains a high-level Mermaid navigation map.
   * **Rule**: No subfolder `README.md` files are allowed (`docs/architecture/README.md`, `docs/operations/README.md`, `docs/reference/README.md` are prohibited to prevent index bloat). Every document must be linked directly in `docs/README.md`.

2. **`docs/getting_started.md` (Linear Walkthrough)**:
   * 100% sequential, chronological guide for spinning up the full infrastructure from scratch.
   * Contains terminal commands in exact execution order.
   * Links to `operations/`, `architecture/`, and `reference/` files for deep dives.

3. **`docs/architecture/` (Conceptual Explanations)**:
   * Explains *how* system components interact (e.g. `backend.md`, `frontend.md`, `aws_services.md`).
   * **Rule**: Must contain Mermaid sequence or flow diagrams. Must NOT contain terminal deployment runbooks (which belong in `operations/` or `getting_started.md`).

4. **`docs/operations/` (Actionable How-To Guides)**:
   * Goal-oriented procedural guides for specific operational tasks (e.g. `bootstrap.md`, `dns_delegation.md`, `secrets_management.md`, `cdn_invalidation.md`, `github_oidc_verification.md`).
   * Contains precise CLI commands, console steps, and operational warnings.

5. **`docs/reference/` (Specs & Blueprints)**:
   * Information-oriented specifications (e.g. `project_planning.md`, `github_actions_monorepo.md`, `agent_skills.md`).
   * Contains directory trees, HCL code snippets, state key tables, and YAML workflow blueprints.

---

## 3. Diagrams & Visual Standard
* **Mermaid Diagrams**: All architectural and flow documents MUST include GitHub-Flavored Mermaid diagrams (`graph TD` or `sequenceDiagram`).
* Node labels with special characters must be enclosed in double quotes (e.g. `id["Label (Info)"]`). No HTML tags allowed inside node labels.

---

## 4. Skill Documentation Standard
* **Manual Launch Command**: Every skill must explicitly define its manual launch command (e.g. `@skill-name` or `run skill <name>`).
* **Activation Keywords**: Every skill must explicitly document its automatic activation triggers/keywords.
* **Auto-Cataloging**: When a skill is created or updated, its manual command and keywords MUST be added to `docs/reference/agent_skills.md`.

---

## 5. Master Indexing & Sequential Update Rule

Whenever a new document or feature is added/updated, changes must be applied in the following strict order:

1. **Create/Update Content Document**: Write the target document in `architecture/`, `operations/`, or `reference/`.
2. **Update Linear Guide or Skills Catalog**: 
   * If infrastructure lifecycle changes &rarr; update `getting_started.md`.
   * If a skill is created/modified &rarr; update `docs/reference/agent_skills.md` with manual commands and keywords.
3. **Update Master Index (`docs/README.md`)**: Register the new file under the appropriate catalog section in `docs/README.md` and update the Mermaid Navigation Map if needed.
