---
name: docs-auditor
description: Audits documentation in docs/ for compliance with cleanmybelly documentation standards. Checks directory structure, SRP taxonomy, English language enforcement, Mermaid diagrams, broken links, and master indexing in docs/README.md. Generates a correction proposal for user approval before making changes. Activate this skill whenever the user asks to audit, check, or verify documentation consistency or structure.
---

# Documentation Auditor Skill (`docs-auditor`)

This skill performs automated compliance audits on the project documentation located in `docs/`. It verifies adherence to single responsibility principles, language rules, link integrity, diagram standards, and master indexing.

---

## 1. Reference Standards

Before running an audit, read the authoritative rules in:
👉 **[Documentation Standards Reference](../references/documentation_standards.md)**

---

## 2. Audit Workflow & Checklist

When activated, systematically scan all files in `docs/` and execute these 6 compliance checks:

### Check 1: Taxonomy & SRP Compliance
* Verify that files are placed strictly inside `docs/architecture/`, `docs/operations/`, `docs/reference/`, `docs/getting_started.md`, or `docs/README.md`.
* **Flag Violation**: Any `README.md` file inside `architecture/`, `operations/`, or `reference/` (subfolder READMEs are prohibited).
* **Flag Violation**: Any terminal command runbooks inside `architecture/` documents.

### Check 2: English Language Enforcement
* Scan all markdown text, code comments, and diagram labels inside `docs/*.md`.
* **Flag Violation**: Any text written in Spanish or languages other than English (except user prompts in conversation).

### Check 3: Master Indexing & Map Alignment
* Read `docs/README.md`.
* Verify that every `.md` file residing in `architecture/`, `operations/`, and `reference/` is explicitly hyperlinked in `docs/README.md`.
* Verify that the Mermaid Navigation Map in `docs/README.md` accurately reflects the document structure.

### Check 4: Link & Path Integrity
* Extract all markdown links (`[text](path)`) in all documentation files.
* Verify that referenced relative paths exist and resolve to valid target files.

### Check 5: Mermaid Visual Standards
* Check all files in `docs/architecture/`.
* Verify that each document contains valid Mermaid diagrams (`graph TD` or `sequenceDiagram`).
* Verify that node labels containing special characters are enclosed in double quotes and contain no HTML tags.

### Check 6: Onboarding Walkthrough Consistency
* Read `docs/getting_started.md`.
* Verify that execution steps (Paso 0 to N) are strictly sequential and reference valid files in `operations/`, `architecture/`, and `reference/`.

---

## 3. Proposal Protocol (Mandatory Confirmation)

If the audit detects **ANY** violation or inconsistency:

1. **DO NOT** edit or modify files automatically.
2. Generate an **Audit & Correction Proposal Report** using standard markdown detailing:
   * 🔍 **Discovered Inconsistencies** (categorized by Check 1–6).
   * 📄 **Affected Files**.
   * 🛠️ **Proposed Correction Plan** (exact diffs or file reorganization).
3. Present the report to the user and request explicit confirmation to apply the proposed fixes.
