<!--
=== Sync Impact Report ===
Version change: None -> 1.0.0
Modified principles:
  - None (Initial Adoption)
Added sections:
  - Core Principles (ctxpack principles I-VI)
  - Technical Constraints & Compliance
  - Development Workflow & Quality Gates
  - Governance
Removed sections:
  - None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ updated
  - .specify/templates/spec-template.md: ✅ updated
  - .specify/templates/tasks-template.md: ✅ updated
  - .specify/templates/checklist-template.md: ✅ updated
Follow-up TODOs:
  - None
==========================
-->

# ctxpack Constitution

## Core Principles

### I. Standard Library Only
The tool MUST be developed using standard library modules only, meaning there are zero
third-party dependencies ever. No external libraries from PyPI or other sources are allowed to be
imported or introduced to the codebase.

**Rationale**: This ensures absolute portability, zero installation overhead, minimal security attack
surface, and long-term maintainability without dependency rot.

### II. Deterministic Output
Identical input MUST produce byte-identical output across all executions, runs, and target
platforms. Output generation, file ordering, object serialization, timestamps, and formatting
MUST be fully deterministic.

**Rationale**: Absolute predictability and consistency are essential for testing, caching,
diffing, and cryptographic integrity.

### III. Fail Loudly with Clear Diagnostics
The tool MUST fail loudly with readable error messages and correct non-zero exit codes. Under
normal operation, raw Python tracebacks MUST be intercepted and suppressed. Errors MUST be printed
directly to standard error (stderr) in a user-friendly and actionable format.

**Rationale**: Enhances CLI usability, integrates cleanly into shell pipelines, and provides a
professional, predictable interface.

### IV. Manifest Transparency
Every file considered, processed, read, or ignored during tool execution MUST appear in the
final output manifest. Silent omissions are strictly prohibited.

**Rationale**: Prevents hidden behaviors, ensures absolute auditability, and guarantees full
visibility into the tool's runtime file operations.

### V. Hard Token Budget Ceiling
The token budget is a hard ceiling that MUST never be exceeded by even one token. If a token
budget limit is defined, the tool MUST enforce it strictly. If processing would cause the budget
to be exceeded, the tool MUST truncate or fail deterministically according to the specification.

**Rationale**: Prevents unexpected context window overflows, cost overruns, or API failures due
to oversized payloads.

### VI. Spec-Driven Development
The specification MUST be written and approved before any code is modified or implemented. The
code MUST strictly match the approved feature specification. If implementation details diverge,
the specification MUST be amended and approved first.

**Rationale**: Prevents ad-hoc scope creep, ensures alignment between implementation and design,
and guarantees documentation remains the source of truth.

## Technical Constraints & Compliance

- **Compatibility**: Code MUST be fully compatible with Python 3.8 and above.
- **Testing**: Complete unit testing using the Python standard `unittest` library is mandatory.
- **Code Quality**: Strict adherence to PEP 8 style guidelines is required for all source code.

## Development Workflow & Quality Gates

- **Phase 0 (Research) & Phase 1 (Design)**: Every feature must have a spec file (`spec.md`) and implementation plan (`plan.md`) created first.
- **Self-Verification**: Code changes must be validated against the specification and tested.
- **Code Review**: Contributions must be peer-reviewed to ensure compliance with all six core principles.

## Governance

- This constitution is the supreme authority for the development of ctxpack. It supersedes all other documentation, guidelines, or code implementations.
- Any amendments to the constitution require an explicit pull request, detailed justification of the changes, and an increment in the constitution version.
- Compliance with all core principles is a mandatory gate for any pull request approval or release candidate verification.

**Version**: 1.0.0 | **Ratified**: 2026-07-25 | **Last Amended**: 2026-07-25
