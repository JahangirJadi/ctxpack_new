---
id: 0001
title: ctxpack-specification
stage: spec
date: 2026-07-25
surface: CLI
model: google/gemini-3.5-flash
feature: 001-ctxpack
branch: 001-ctxpack
user: jahangirjadi
command: /sp.specify
labels: [spec, ctxpack, definition]
links:
  spec: specs/001-ctxpack/spec.md
  ticket: none
  adr: none
  pr: none
files:
  - specs/001-ctxpack/spec.md: Created
  - specs/001-ctxpack/checklists/requirements.md: Created
tests:
  - none
---

## Prompt

```text
Build a Python CLI tool called ctxpack. It takes a folder path, a task description string, and a token budget integer. It recursively walks the folder, reads every readable text file, ranks files by relevance to the task description, then greedily packs the highest-ranked files into a single markdown bundle that fits within the token budget. Token counting rule: tokens = math.ceil(len(text) / 4) — applied to the entire bundle output, not just file contents. It outputs the bundle to stdout or a file, and outputs a manifest JSON (to a file or a one-line summary to stderr) accounting for every file it considered — included files with token count and reason, excluded files with reason. Non-text and unreadable files must be handled gracefully without crashing. Obvious noise directories and files (like .git, node_modules, lockfiles, build artifacts) must be excluded and noted in the manifest. The tool must be deterministic: same command, same output, byte-for-byte. Exit code 0 on success, 1 on invalid arguments, 2 on path not found or unreadable.
```

## Response snapshot

Created feature branch '001-ctxpack', drafted and finalized the feature specification at 'specs/001-ctxpack/spec.md', and validated it with the requirements checklist.

## Outcome

- ✅ Impact: Highly impactful; established the core feature specification for ctxpack with clean requirements and zero unresolved gaps.
- 🧪 Tests: N/A - Specification phase only
- 📁 Files: Created specs/001-ctxpack/spec.md and specs/001-ctxpack/checklists/requirements.md.
- 🔁 Next prompts: /sp.clarify to resolve architectural design decisions.
- 🧠 Reflection: Drafting precise specifications first creates a clear roadmap, reducing downstream alignment issues during planning and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
