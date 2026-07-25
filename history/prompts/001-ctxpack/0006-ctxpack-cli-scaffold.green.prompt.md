---
id: 0006
title: ctxpack-cli-scaffold
stage: green
date: 2026-07-25
surface: CLI
model: google/gemini-3.5-flash
feature: 001-ctxpack
branch: 001-ctxpack
user: jahangirjadi
command: None
labels: [cli, scaffold, argparse]
links:
  spec: specs/001-ctxpack/spec.md
  ticket: none
  adr: none
  pr: none
files:
  - ctxpack.py: Created
tests:
  - none
---

## Prompt

```text
Spawn a sub-agent to implement Task 1: Create ctxpack.py with the argparse CLI. The file must define a main() function and an if __name__ == '__main__' guard. It must parse --path (required, str), --task (required, str), --budget (required, int), --out (optional, str), --manifest (optional, str). Invalid arguments must print a one-line error to stderr and exit with code 1. --path not existing must print a one-line error to stderr and exit with code 2. Do not implement any logic beyond argument parsing and these exit codes yet. After writing the file, run `python ctxpack.py --help` and show me the output.
```

## Response snapshot

Implemented ctxpack.py CLI scaffold with argparse custom sub-classing. Validated that --help, non-existent path (exit code 2), non-positive budgets (exit code 1), and invalid argument types (exit code 1) fail loudly with single-line error messages.

## Outcome

- ✅ Impact: High impact; successfully completed Task T001 and T003, establishing correct and verified CLI parameter contracts and exit statuses.
- 🧪 Tests: Validated manually in terminal using help, invalid parameters, and nonexistent path checks.
- 📁 Files: Created and validated root file ctxpack.py.
- 🔁 Next prompts: Implement recursive walking and text/binary/noise filtering.
- 🧠 Reflection: Overriding ArgumentParser.error() is the most robust way to intercept tracebacks and print standard clean single lines to stderr on bad parameters.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
