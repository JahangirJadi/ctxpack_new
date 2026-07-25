# Tasks: ctxpack CLI Tool

**Input**: Design documents from `/specs/001-ctxpack/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/cli-contract.md

**Tests**: Test tasks are included as standard verification criteria for high quality and robustness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different functions/aspects, no incomplete dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Contains exact file paths in descriptions

## Path Conventions

- Single project structure: `ctxpack.py`, `tests/test_ctxpack.py`, and `pyproject.toml` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic packaging setup.

- [X] T001 Create `pyproject.toml` at repository root to configure Setuptools console scripts entry point.
- [X] T002 Initialize `tests/test_ctxpack.py` at repository root with a base standard `unittest.TestCase` harness.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modules and exception mappings that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Implement `argparse` CLI parser in `ctxpack.py` to parse path, task, budget, out, and manifest flags, overriding `.error()` to print a single-line message to `stderr` and exit with code 1.
- [X] T004 Implement recursive Walker and UTF-8 decoder `walk_files(path: str)` in `ctxpack.py` to traverse files, sorting nodes alphabetically and checking readability.
- [X] T005 Implement global exception hooks in the core `main()` function in `ctxpack.py` to intercept tracebacks, print single-line error descriptions to `stderr`, and return exit codes 2 (path missing/unreadable) or 1 (general errors).

**Checkpoint**: Foundation ready - CLI flags, file walkers, and traceback handling are fully functional.

---

## Phase 3: User Story 1 - Assemble Standard Markdown Bundle (Priority: P1) 🎯 MVP

**Goal**: Walk, filter, and concatenate text files into standard markdown file blocks.

**Independent Test**: Running the tool on a directory containing text files and a large token budget generates a formatted bundle containing markdown headers and file contents in stdout or the specified output file.

### Tests for User Story 1

- [X] T006 [P] [US1] Create unit tests in `tests/test_ctxpack.py` validating alphabetized walker sorting, UTF-8 text vs binary classification, and directory blocklisting.
- [X] T007 [P] [US1] Create unit tests in `tests/test_ctxpack.py` verifying the token counting ceiling formula: `math.ceil(len(text) / 4)`.

### Implementation for User Story 1

- [X] T008 [US1] Implement file block formatter in `ctxpack.py` wrapping paths in `## {path}` headings and content inside code blocks.
- [X] T009 [US1] Implement greedy bundle concatenation loops in `ctxpack.py` to append formatted blocks in alphabetical path order.

**Checkpoint**: At this point, User Story 1 is fully functional and can bundle text files deterministically.

---

## Phase 4: User Story 2 - Relevance Ranking & Budget Enforcement (Priority: P1)

**Goal**: Sort files by keyword relevance scores with depth penalties and enforce budget limits by line-by-line truncation.

**Independent Test**: Running the tool with a small token budget ranks files, includes matching keywords first, and truncates large files at line boundaries with `[TRUNCATED]` markers without exceeding the budget by even one token.

### Tests for User Story 2

- [X] T010 [P] [US2] Create unit tests in `tests/test_ctxpack.py` verifying lowercase task tokenization and weighted scoring (3x path, 1x content, 10x cap, length normalization, depth penalty).
- [X] T011 [P] [US2] Create unit tests in `tests/test_ctxpack.py` verifying strict budget checks, conditional directory tree inclusion (≤ 5% budget), and line-by-line head truncation.

### Implementation for User Story 2

- [X] T012 [US2] Implement tokenized relevance calculation function `rank_files(files: list[dict], task: str)` in `ctxpack.py`.
- [X] T013 [US2] Implement deterministic visual directory tree generator `generate_tree(path: str)` in `ctxpack.py` sorting entries alphabetically.
- [X] T014 [US2] Implement line-by-line head truncation function `truncate_file_content(content: str, remaining_budget: int)` in `ctxpack.py` with 50-token margin and `[TRUNCATED]` markers.
- [X] T015 [US2] Integrate ranking, tree size checking (≤ 5%), and greedy truncation into `assemble_bundle()` in `ctxpack.py`.

**Checkpoint**: At this point, User Stories 1 and 2 are fully integrated; budget constraints and relevance sorting are actively enforced.

---

## Phase 5: User Story 3 - Manifest Generation & Transparency (Priority: P2)

**Goal**: Serializing audit trails and summaries for every file processed.

**Independent Test**: Running the tool with `--manifest` creates a valid JSON matching the schema containing included/excluded files with precise token counts and reasons.

### Tests for User Story 3

- [X] T016 [P] [US3] Create unit tests in `tests/test_ctxpack.py` validating manifest dictionary structure, sorted key dumps, and single-line summary stdout formatting.

### Implementation for User Story 3

- [X] T017 [US3] Implement detailed JSON serializable structure `build_manifest()` in `ctxpack.py` tracking included and excluded reasons.
- [X] T018 [US3] Implement output writer `write_output()` in `ctxpack.py` supporting stdout, bundle file output, manifest file serialization, and stderr summary printing.

**Checkpoint**: Manifest serialization is completed and fully traceable.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Non-functional validations, documentation, and final system testing.

- [X] T019 Write complete, developer-friendly documentation in `README.md` in the project root.
- [X] T020 Run integration and platform testing in `tests/test_ctxpack.py` verifying byte-identical outputs across multiple identical runs.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - Can proceed sequentially in priority order: US1 → US2 → US3.
- **Polish (Final Phase)**: Depends on all user stories being complete.

```text
  [Phase 1: Setup]
         │
         ▼
[Phase 2: Foundational]
         │
         ▼
[Phase 3: User Story 1]
         │
         ▼
[Phase 4: User Story 2]
         │
         ▼
[Phase 5: User Story 3]
         │
         ▼
  [Phase N: Polish]
```

### Parallel Opportunities

Within each story phase:
- Test writing and implementation can be developed in parallel (e.g. T006, T007 in parallel; T010, T011 in parallel).
- Independent modular helpers (e.g. tree generation T013 and ranking algorithm T012) can be implemented in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CLI parsing, walks, exception handling).
3. Complete Phase 3: User Story 1 (Basic bundling).
4. **STOP and VALIDATE**: Confirm basic directory bundling runs successfully without crashes.

### Incremental Delivery

1. Setup + Foundational ready.
2. Add US1 → Test basic deterministic walks & formatting (MVP).
3. Add US2 → Test task rankings & strict budget head truncations.
4. Add US3 → Test JSON serialized audits.
5. Finish N → Verify byte-for-byte determinism & write README.md.
