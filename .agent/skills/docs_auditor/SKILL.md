---
name: docs-auditor
description: Audits documentation in docs/ for compliance with cleanmybelly documentation standards. Checks directory structure, SRP taxonomy, English language enforcement, Mermaid diagrams, emoji policy adherence (allowing emojis only in docs/README.md and blue-squared number/alert emojis in non-README files), accurate file naming/descriptions, prohibition of host-specific absolute paths (e.g. /home/user/...), broken links, and master indexing across index files. Generates a correction proposal for user approval before making changes. Activate this skill whenever the user asks to audit, check, or verify documentation consistency or structure.
---

# Documentation Auditor Skill (`docs-auditor`)

This skill performs automated compliance audits on the project documentation located in `docs/`. It verifies adherence to single responsibility principles, language rules, emoji policies, accurate file naming/descriptions, link integrity, diagram standards, and master indexing.

---

## 1. Reference Standards

Before running an audit, read the authoritative rules in:
[Documentation Standards Reference](../references/documentation_standards.md)

---

## 2. Audit Workflow & Checklist

When activated, systematically scan all files in `docs/` and execute these 7 compliance checks:

### Check 1: Taxonomy & SRP Compliance
* Verify that files are placed strictly inside `docs/architecture/`, `docs/operations/`, `docs/reference/`, `docs/getting_started.md`, or `docs/README.md`.
* **Flag Violation**: Any `README.md` file inside `architecture/`, `operations/`, or `reference/` (subfolder READMEs are prohibited).
* **Flag Violation**: Any terminal command runbooks inside `architecture/` documents.

### Check 2: English Language Enforcement
* Scan all markdown text, code comments, and diagram labels inside `docs/*.md`.
* **Flag Violation**: Any text written in Spanish or languages other than English (except user prompts in conversation).

### Check 3: Emoji Policy Compliance
* Scan all documentation files outside `docs/README.md`.
* **Flag Violation**: Any decorative emoji (e.g. 🚀, 🗺️, 📚, 📄, 🔍, 🛠️, etc.) in non-README files.
* **Permitted**: Emojis inside `docs/README.md`, or blue-squared number/alert symbol emojis (`ℹ️`, `⚠️`, `❗`, `1️⃣` through `🔟`) in non-README files.

### Check 4: File Naming & Description Accuracy
* Compare document filenames and section titles against their catalog entry in `docs/README.md`.
* **Flag Violation**: Misleading filenames or descriptions (e.g., calling a directory layout / state standards spec `project_planning.md` instead of `infrastructure_standards.md`).

### Check 5: Master Indexing & Cross-File Alignment
* Read `docs/README.md`, `docs/getting_started.md`, `docs/architecture/aws_services.md`, and `docs/reference/agent_skills.md`.
* Verify that every `.md` file in `architecture/`, `operations/`, and `reference/` is explicitly hyperlinked in `docs/README.md`.
* Verify that the Mermaid Navigation Map in `docs/README.md` accurately reflects the document structure.
* Verify that all AWS services and agent skills are cataloged in their respective index files.

### Check 6: Link & Path Integrity
* Extract all markdown links (`[text](path)`) in all documentation files.
* Verify that referenced relative paths exist and resolve to valid target files.

### Check 7: Mermaid Visual Standards & Onboarding Consistency
* Check all files in `docs/architecture/` for valid Mermaid diagrams (`graph TD` or `sequenceDiagram`).
* Verify that node labels containing special characters are enclosed in double quotes and contain no HTML tags.
* Verify that steps in `docs/getting_started.md` are strictly sequential.

### Check 8: Host-Specific Path Audit
* Scan all markdown text, code blocks, and comments in `docs/*.md`.
* **Flag Violation**: Any hardcoded local workstation path or user home directory (e.g. `/home/user/...`, `/Users/dev/...`, `/home/jose/...`). All paths must be relative or use generic placeholders like `<REPO_ROOT>`.

---

## 3. Proposal Protocol (Mandatory Confirmation)

If the audit detects **ANY** violation or inconsistency:

1. **DO NOT** edit or modify files automatically without confirmation.
2. Generate an **Audit & Correction Proposal Report** using standard markdown detailing:
   * **Discovered Inconsistencies** (categorized by Check 1–8).
   * **Affected Files**.
   * **Proposed Correction Plan** (exact diffs or file reorganization).
3. Present the report to the user and request explicit confirmation to apply the proposed fixes.

