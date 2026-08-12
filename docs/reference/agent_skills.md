# Reference: Agent Skills Catalog & Auto-Documentation Standard

This reference document catalogs all automated agent skills available in the **cleanmybelly** repository, specifying their manual launch commands, activation keywords, and the protocol for auto-documenting new skills.

---

## 1. Skill Location & Repository Taxonomy

Project skills reside in the `.agent/skills/` directory at the root of the repository:

```text
.agent/skills/
├── references/
│   └── documentation_standards.md    # Shared rules & taxonomy guidelines
├── context_compressor/
│   └── SKILL.md                      # Context Compressor skill (exports session to llm-context/YYYY-MM-DD/)
├── context_loader/
│   └── SKILL.md                      # Context Loader skill (restores session state in clean chat window)
├── docs_auditor/
│   └── SKILL.md                      # Audit skill (compliance checking & proposal generation)
└── docs_writer/
    └── SKILL.md                      # Writer skill (3-step update sequence & doc creation)
```

---

## 2. Active Skills Catalog

| Skill Name | Location | Manual Launch Command | Activation Keywords | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`context-compressor`** | [.agent/skills/context_compressor/SKILL.md](../../.agent/skills/context_compressor/SKILL.md) | `@context-compressor` or `run skill context-compressor` | `compress context`, `export session context`, `save chat context`, `export context`, `save session` | Exports and compresses the active chat context into structured handoff files (`context_export.md`, `initial_request.md`, `master_refactor_plan.md`) stored in `llm-context/YYYY-MM-DD/` at the repository root, ensuring `.gitignore` ignores `llm-context/`. |
| **`context-loader`** | [.agent/skills/context_loader/SKILL.md](../../.agent/skills/context_loader/SKILL.md) | `@context-loader` or `run skill context-loader` | `load context`, `restore context`, `import context`, `load chat session`, `resume context` | Loads and restores an exported conversation context package from `llm-context/YYYY-MM-DD/` into a new clean chat window, presents a concise state summary to the user, and prompts for confirmation to begin the next execution step. |
| **`docs-auditor`** | [.agent/skills/docs_auditor/SKILL.md](../../.agent/skills/docs_auditor/SKILL.md) | `@docs-auditor` or `run skill docs-auditor` | `audit docs`, `check documentation`, `verify docs structure`, `audit documentation`, `check docs quality` | Audits `docs/` for SRP compliance, English language enforcement, Mermaid diagrams, emoji policy compliance (allowing emojis only in `docs/README.md` and blue-squared number/alert emojis in non-README files), accurate file naming/descriptions, broken links, and master index alignment across all index files. Generates a proposal report for user confirmation before editing. |
| **`docs-writer`** | [.agent/skills/docs_writer/SKILL.md](../../.agent/skills/docs_writer/SKILL.md) | `@docs-writer` or `run skill docs-writer` | `document feature`, `write docs`, `create documentation`, `document module`, `update docs` | Authors new documentation or documents completed features following SRP (`architecture/`, `operations/`, `reference/`). Enforces strict emoji restrictions, accurate file naming/descriptions, and executes a mandatory indexing analysis plan across `docs/README.md`, `docs/getting_started.md`, `docs/architecture/aws_services.md`, and `docs/reference/agent_skills.md`. |

---

## 3. Auto-Documentation Protocol for New Skills

Whenever a new skill is created or an existing skill is updated:

1. **Create Skill Package**: Place the skill in `.agent/skills/<skill_name>/SKILL.md`.
2. **Define Invocation Specification**: Include the exact **Manual Launch Command** (e.g. `@skill-name`) and **Activation Keywords** in the skill description.
3. **Update Skills Catalog**: Add the skill definition, manual command, keywords, and purpose to this document (`docs/reference/agent_skills.md`).
4. **Register in Master Index**: Verify that `docs/reference/agent_skills.md` is registered in `docs/README.md` catalog table and navigation map.
