---
id: 0001
title: ctxpack-constitution-v1-0-0
stage: constitution
date: 2026-07-25
surface: CLI
model: google/gemini-3.5-flash
feature: none
branch: 001-ctxpack-cli
user: jahangirjadi
command: /sp.constitution
labels: [constitution, ctxpack, principles]
links:
  spec: none
  ticket: none
  adr: none
  pr: none
files:
  - .specify/memory/constitution.md: Modified
  - .specify/templates/plan-template.md: Modified
  - .specify/templates/spec-template.md: Modified
  - .specify/templates/tasks-template.md: Modified
  - .opencode/command/sp.constitution.md: Modified
tests:
  - none
---

## Prompt

```text
Create principles for a Python CLI tool called ctxpack. Principles must include: (1) Standard library only — zero third-party dependencies, ever. (2) Determinism — identical input must produce byte-identical output. (3) Fail loudly with readable errors and correct exit codes, never raw tracebacks. (4) Every file considered must appear in the manifest — no silent omissions. (5) Token budget is a hard ceiling — never exceed it by even one token. (6) Spec is written before any code; code must match the spec or the spec must be updated first.
```

## Response snapshot

Drafted and ratified ctxpack constitution v1.0.0 outlining the six core principles. Propagated principles across templates and configured checklists accordingly.

## Outcome

- ✅ Impact: Highly impactful; established project constitution and synced all dependent templates.
- 🧪 Tests: N/A - Constitution and templates only
- 📁 Files: Updated .specify/memory/constitution.md, .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md, and .opencode/command/sp.constitution.md.
- 🔁 Next prompts: Build feature specification for ctxpack using spec template.
- 🧠 Reflection: Establishing strong, testable principles early in development ensures high alignment and reduces technical debt.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
