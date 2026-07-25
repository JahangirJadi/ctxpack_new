---
id: 0003
title: ctxpack-spec-md
stage: spec
date: 2026-07-25
surface: CLI
model: google/gemini-3.5-flash
feature: 001-ctxpack
branch: 001-ctxpack
user: jahangirjadi
command: None
labels: [spec, spec-md, cli-contract]
links:
  spec: SPEC.md
  ticket: none
  adr: none
  pr: none
files:
  - SPEC.md: Created
tests:
  - none
---

## Prompt

```text
Based on the spec and clarifications, create a SPEC.md file in the project root (not inside .specify/). It must contain these exact sections: (1) CLI Contract — the exact flags, types, and exit codes. (2) Token Counting Rule — the exact formula. (3) Manifest Schema — the exact JSON keys and structure. (4) Ranking Strategy — the method chosen and the alternatives rejected with reasons. (5) Truncation Policy — what happens when a file doesn't fit in the remaining budget. (6) Noise Detection — what counts as noise and how it is detected. (7) Determinism Guarantee — how byte-identical output is ensured. (8) Definition of Done — the checklist that determines when the tool is complete.
```

## Response snapshot

Successfully created SPEC.md in the project root, containing all eight required sections: CLI Contract, Token Counting Rule, Manifest Schema, Ranking Strategy, Truncation Policy, Noise Detection, Determinism Guarantee, and Definition of Done.

## Outcome

- ✅ Impact: High impact; formalized the product and technical specification directly in the project root folder for easy visibility and verification.
- 🧪 Tests: N/A - Documentation phase only
- 📁 Files: Created SPEC.md in the project root.
- 🔁 Next prompts: Stage and commit SPEC.md only as the first git commit.
- 🧠 Reflection: Providing extremely detailed constraints and deterministic logic sets up a clear definition of correctness for future sub-agents.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
