# Feature Specification: ctxpack CLI Tool

**Feature Branch**: `001-ctxpack`  
**Created**: 2026-07-25  
**Status**: Draft  
**Input**: User description: "Build a Python CLI tool called ctxpack. It takes a folder path, a task description string, and a token budget integer. It recursively walks the folder, reads every readable text file, ranks files by relevance to the task description, then greedily packs the highest-ranked files into a single markdown bundle that fits within the token budget. Token counting rule: tokens = math.ceil(len(text) / 4) — applied to the entire bundle output, not just file contents. It outputs the bundle to stdout or a file, and outputs a manifest JSON (to a file or a one-line summary to stderr) accounting for every file it considered — included files with token count and reason, excluded files with reason. Non-text and unreadable files must be handled gracefully without crashing. Obvious noise directories and files (like .git, node_modules, lockfiles, build artifacts) must be excluded and noted in the manifest. The tool must be deterministic: same command, same output, byte-for-byte. Exit code 0 on success, 1 on invalid arguments, 2 on path not found or unreadable."

## Clarifications

### Session 2026-07-25
- Q: Relevance Ranking Method → A: Keyword overlap scoring (Option A)
- Q: Truncation Policy → A: Head-only Truncation (Option A)
- Q: Noise Detection Policy → A: Hardcoded blocklists + size limit (Option A)
- Q: Directory Tree Budget Allocation → A: Threshold budget tree (Option A)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assemble Standard Markdown Bundle (Priority: P1)

As a developer, I want to pack a project directory into a single markdown bundle so that I can send it to an LLM context window.

**Why this priority**: Core MVP functionality without which the tool does not work.

**Independent Test**: Can be fully tested by running the CLI with a valid folder path, a task description, and a large token budget, and verifying that the output is a correctly formatted markdown bundle.

**Acceptance Scenarios**:

1. **Given** a directory containing valid text files, **When** run with a valid budget, **Then** a markdown bundle is generated containing all included file paths as headings followed by their contents inside code blocks.
2. **Given** a directory containing text and binary/unreadable files, **When** run, **Then** binary files are skipped gracefully and noted in the manifest, while text files are bundled without crashes.

---

### User Story 2 - Relevance Ranking & Budget Enforcement (Priority: P1)

As a developer, I want the most relevant files to be packed first within a strict budget constraint so that I don't waste LLM tokens.

**Why this priority**: Essential to prevent budget overflow while keeping the most useful context.

**Independent Test**: Can be verified by passing a small budget and checking that only top-scored files or their truncated heads are included, without exceeding the budget by even a single token.

**Acceptance Scenarios**:

1. **Given** a task keyword that matches specific files, **When** run, **Then** those matching files are ranked higher and included before non-matching files.
2. **Given** a budget constraint, **When** the total tokens exceed it, **Then** the output token count is strictly less than or equal to the budget, and any file that doesn't fit is truncated or skipped.

---

### User Story 3 - Manifest Generation & Transparency (Priority: P2)

As a developer, I want to see a detailed manifest of all files considered and why they were included or excluded.

**Why this priority**: Provides auditing, debugging, and transparency of what was packed.

**Independent Test**: Check that a valid JSON manifest is produced matching the schema with entries for all files.

**Acceptance Scenarios**:

1. **Given** a workspace run, **When** `--manifest` is specified, **Then** a detailed JSON file is saved containing the exact list of included and excluded files with reasons.

---

### Edge Cases

- **Empty Folder**: What happens when the folder is empty? The tool must exit 0, produce an empty bundle (or only the header if fits), and manifest with 0 included and 0 excluded.
- **Budget of 1**: What happens when the budget is extremely small (e.g., 1)? The tool must exit 0, bundle must only contain the header if it fits, or be empty. It must never exceed the budget.
- **Single File Larger than Budget**: What happens when a single file is larger than the budget? The file must be truncated correctly or skipped entirely if not even a minimal truncated block fits.
- **Binary/Unreadable File**: The tool must catch any read exceptions, log the file as status='binary' or 'unreadable' with reason, and continue without crashing.
- **Invalid Path**: If `--path` is missing or not a directory, exit with code 2.
- **Invalid Budget**: If `--budget` is not an integer or is less than or equal to 0, exit with code 1.

## Requirements *(mandatory)*

### Core Constraints

- **CON-001**: Standard library only — zero third-party dependencies, ever.
- **CON-002**: Determinism — identical input must produce byte-identical output.
- **CON-003**: Fail loudly with readable errors and correct exit codes, never raw tracebacks.
- **CON-004**: Every file considered must appear in the manifest — no silent omissions.
- **CON-005**: Token budget is a hard ceiling — never exceed it by even one token.
- **CON-006**: Spec must match implementation — code and spec must not diverge.

### Functional Requirements

- **FR-001**: System MUST accept arguments: `--path` (required, string), `--task` (required, string), `--budget` (required, integer), `--out` (optional, string), and `--manifest` (optional, string).
- **FR-002**: System MUST recursively walk the path, identifying text files and excluding noise. Noise directories blocklisted are: `.git`, `.hg`, `.svn`, `node_modules`, `__pycache__`, `.venv`, `venv`, `env`, `dist`, `build`, `.next`, `target`, `.idea`, `.vscode`. Noise extensions blocklisted are: `.lock`, `.min.js`, `.min.css`, `.map`, `.pyc`, `.pyo`, `.class`, `.o`, `.so`, `.dll`, `.exe`, `.whl`, `.egg`. Files larger than 1 MB (1,048,576 bytes) MUST also be excluded as `too_large`.
- **FR-003**: System MUST compute tokens using `math.ceil(len(text) / 4)` on the entire output bundle.
- **FR-004**: System MUST score and rank files using keyword overlap scoring. The `--task` string is tokenized into lowercase words (length >= 3). Points are awarded for matches in path (3 points) and content (1 point, capped at 10 per token), and divided by `1 + depth` where depth is the number of path separators.
- **FR-005**: System MUST truncate files gracefully. If a file's full block does not fit in the remaining budget, the tool MUST include the head of the file up to the remaining budget minus 50 tokens (reserved for the file header) and append a `[TRUNCATED]` marker. If even a single line from the truncated head does not fit, the file MUST be skipped entirely and marked as `budget exhausted`.
- **FR-006**: System MUST output a deterministic manifest JSON containing all considered files.
- **FR-007**: System MUST exit with code 0 on success, 1 on invalid arguments, and 2 on unreadable/missing paths.
- **FR-008**: System MUST conditionally include a visual directory tree structure at the start of the bundle output. The tree is generated deterministically and sorted alphabetically. The tree's token cost is computed as `math.ceil(len(tree_str) / 4)`. The tree MUST be included in the bundle if and only if its token cost is ≤ 5% of the total budget.

### Key Entities *(include if feature involves data)*

- **FileItem**: Represents a discovered file in the directory tree. Attributes:
  - `path`: relative path to root directory
  - `status`: status (text, binary, noise_dir, noise_ext, unreadable)
  - `content`: content of the file
  - `tokens`: estimated token count of file content
  - `score`: relevance score
  - `reason`: inclusion or exclusion reason
- **Manifest**: Represents the overall execution summary. Attributes:
  - `budget`: original budget
  - `used`: final token count used
  - `included`: list of included files
  - `excluded`: list of excluded files

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Output is 100% deterministic (byte-for-byte identical across runs with identical inputs).
- **SC-002**: Verification that the bundle token count never exceeds the user-specified budget (SC-002 is verified using the `math.ceil(len(text) / 4)` formula on the final output string).
- **SC-003**: The tool runs successfully on repositories with up to 10,000 files in under 5 seconds.
