# Implementation Plan: ctxpack CLI Tool

**Branch**: `001-ctxpack` | **Date**: 2026-07-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ctxpack/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.opencode/command/sp.plan.md` for the execution workflow.

## Summary

`ctxpack` is a single-file Python CLI tool that recursively traverses a folder, skips binary and blocklisted noise files, ranks the remaining text files by relevance to a given task description using a keyword-overlap scoring model, and bundles them into a single markdown file matching a strict token budget. It also produces a detailed JSON manifest accounting for every considered file.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: None (Standard library only)  
**Storage**: N/A  
**Testing**: Python standard `unittest` library  
**Target Platform**: Linux, macOS, Windows  
**Project Type**: Single-file CLI tool (`ctxpack.py` at repository root)  
**Performance Goals**: Traverse and score repositories with up to 10,000 files in under 5 seconds.  
**Constraints**: Zero third-party packages allowed, completely offline, 100% deterministic, strict hard token budget ceiling.  
**Scale/Scope**: Single project walking, processing files up to 1 MB.  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Standard Library Only: Zero third-party dependencies, ever.
- [x] Determinism: Identical input must produce byte-identical output.
- [x] Fail Loudly: Readable errors and correct exit codes, never raw tracebacks.
- [x] Manifest Transparency: Every file considered must appear in the manifest (no silent omissions).
- [x] Token Budget: Hard ceiling — never exceed it by even one token.
- [x] Spec-Driven: Spec is written and approved before any code changes.

## Project Structure

### Documentation (this feature)

```text
specs/001-ctxpack/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── cli-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
.
├── ctxpack.py             # Single-file core CLI and logic
├── pyproject.toml         # Packaging configuration and console scripts entry point
├── specs/                 # Feature branch specs and plans
│   └── 001-ctxpack/
└── tests/                 # Complete unittest test suite
    └── test_ctxpack.py
```

**Structure Decision**: Single-file layout with `pyproject.toml` console script entry point. This minimizes overhead, ensures perfect portability, and naturally enforces standard library guidelines.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Fully compliant with all constitutional principles.
