# PROMPTS.md - Prompt History

## Section 1: Constitution Setup
- **Prompt**: Setup the core project principles and ratify the constitution.
- **Generated**: `constitution.md` updated to v1.0.0.
- **Modifications**: None.

## Section 2: Specification Creation
- **Prompt**: Create the feature specification for ctxpack.
- **Generated**: `specs/001-ctxpack/spec.md`.
- **Modifications**: Updated functional requirements to match exactly.

## Section 3: Feature Clarification
- **Prompt**: sp.clarify design decisions.
- **Generated**: Interactive clarification QA.
- **Modifications**: Updated `spec.md` with keyword-overlap scoring, truncation, noise detection, and directory tree policies.

## Section 4: Technical Planning
- **Prompt**: Generate the technical implementation plan.
- **Generated**: `specs/001-ctxpack/plan.md`, `specs/001-ctxpack/research.md`, etc.
- **Modifications**: Aligned with single-file layout.

## Section 5: Auditing and Refining Core Requirements
- **Prompt**: Audit the codebase against the hackathon requirement brief, ensure manifest schema correctness, implement .gitignore support, and fix any remaining edge cases.
- **Generated**: `ctxpack.py`, `tests/test_ctxpack.py`, `SPEC.md`, `specs/001-ctxpack/spec.md`, and `JOURNAL.md` updated.
- **Modifications**: Integrated standard-library `.gitignore` pattern parser, updated manifest JSON keys (to include `reason` for included files and clean up excluded keys), corrected relevance scoring formula in specs to match tests, normalized all paths to forward slashes for cross-platform determinism, and filled in the engineering journal answers.
