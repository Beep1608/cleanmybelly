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
   * Information-oriented specifications (e.g. `infrastructure_standards.md`, `github_actions_monorepo.md`, `agent_skills.md`).
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

## 5. Strict Emoji Usage Policy

To maintain professional technical documentation standards:
* **Default Prohibition**: Emojis are forbidden in documentation content by default.
* **Allowed Location 1 (`docs/README.md`)**: Decorative emojis are permitted ONLY inside the main master index (`docs/README.md`) for visual navigation and section headers.
* **Allowed Location 2 (Non-README documents)**: In all other files (`docs/getting_started.md`, `docs/architecture/*`, `docs/operations/*`, `docs/reference/*`), standard decorative emojis (e.g., 🚀, 🗺️, 📚, 📄, 🔍, 🛠️) are **PROHIBITED**.
* **Blue-Square Emoji Exemption**: The ONLY emojis allowed outside `docs/README.md` are blue-squared symbol emojis used strictly for step numbering, alerts, or exclamation badges (e.g. `ℹ️`, `⚠️`, `❗`, `1️⃣`, `2️⃣`, `3️⃣`, `4️⃣`, `5️⃣`, `6️⃣`, `7️⃣`, `8️⃣`, `9️⃣`, `🔟`).

---

## 6. Accurate File Naming & Description Standard

* Document filenames, section titles, and catalog descriptions in `docs/README.md` must accurately reflect the exact technical content of the file.
* **No Misleading Names**: Never name a file after planning (`project_planning.md`) if its content defines architecture standards, directory layouts, or state key conventions. Use precise names like `infrastructure_standards.md`.

---

## 7. No Host-Specific / Machine-Specific Absolute Paths

* **Strict Prohibition of Local Host Paths**: Documentation content must NEVER contain hardcoded developer machine paths, workstation user directories, or local environment roots (e.g., `/home/jose/...`, `/home/username/...`, `/Users/developer/...`).
* **Generic Path Placeholders**: Always use repository-relative paths (e.g. `aws/infra/...`) or generic placeholders like `<REPO_ROOT>` (e.g. `<REPO_ROOT>/aws/pre-infra/github/repository`) in example commands and code snippets.

---

## 8. Master Indexing & Sequential Update Rule

Whenever a new document or feature is added/updated, changes must be applied in the following strict order:

1. **Create/Update Content Document**: Write the target document in `architecture/`, `operations/`, or `reference/`.
2. **Update Linear Guide or Skills Catalog**: 
   * If infrastructure lifecycle changes &rarr; update `getting_started.md`.
   * If a skill is created/modified &rarr; update `docs/reference/agent_skills.md` with manual commands and keywords.
   * If AWS services are added/modified &rarr; update `docs/architecture/aws_services.md`.
3. **Update Master Index (`docs/README.md`)**: Register the new file under the appropriate catalog section in `docs/README.md` with an accurate description, and update the Mermaid Navigation Map.
4. **Execute Indexing Audit Plan**: Verify cross-file indexing completeness across `docs/README.md`, `docs/getting_started.md`, `docs/architecture/aws_services.md`, and `docs/reference/agent_skills.md`.


