# ctxpack SPEC.md

## (1) CLI Contract

The tool MUST be a single-file executable module or run via a clear command-line interface. It accepts the following arguments:

### Flags and Types

- `--path` (required, string): The folder path of the directory to be walked, indexed, and packed.
- `--task` (required, string): A task description string used for computing relevance scores of text files.
- `--budget` (required, integer): The strict maximum token budget ceiling allowed for the entire output bundle.
- `--out` (optional, string): File path to save the generated markdown bundle. If omitted, the bundle MUST be output directly to `stdout`.
- `--manifest` (optional, string): File path to save the detailed JSON manifest. If omitted, the tool MUST output a single-line summary to `stderr`.

### Exit Codes

- `0`: Execution succeeded without any unhandled errors.
- `1`: Invalid arguments provided (e.g. invalid budget value, missing required flags).
- `2`: Path provided under `--path` does not exist, is not a directory, or is completely unreadable.

---

## (2) Token Counting Rule

The token count of any text string is determined by the following exact formula:

$$\text{tokens} = \lceil \frac{\text{len(text)}}{4} \rceil$$

Which is represented in Python as:
```python
import math
tokens = math.ceil(len(text) / 4)
```

### Scope of Token Constraint

This token counting rule MUST be applied to the **entire, final bundle output string** (including the root headers, directory tree, file separators, markdown formatting, and file blocks), and NOT just to the raw, isolated file contents.

---

## (3) Manifest Schema

The manifest output MUST account for every single file considered during traversal. If outputted to a file via `--manifest`, it MUST be a valid JSON matching this exact structure:

```json
{
  "budget": 8000,
  "used": 4512,
  "included": [
    {
      "path": "src/main.py",
      "tokens": 1200,
      "reason": "relevance_score: 1.54"
    }
  ],
  "excluded": [
    {
      "path": "node_modules/package/index.js",
      "reason": "noise_dir"
    },
    {
      "path": "poetry.lock",
      "reason": "noise_ext"
    },
    {
      "path": "assets/huge_image.png",
      "reason": "binary or unreadable"
    },
    {
      "path": "tests/test_large.py",
      "reason": "budget exhausted"
    }
  ]
}
```

If `--manifest` is omitted, a one-line summary MUST be printed to `stderr` in this exact format:
```text
ctxpack: {used}/{budget} tokens used, {len(included)} files included, {len(excluded)} files excluded
```

---

## (4) Ranking Strategy

### Chosen Method: Keyword Overlap Scoring with Depth Penalty

1. **Task Tokenization**: The `--task` string is split on whitespace and punctuation, converted to lowercase, and all tokens shorter than 3 characters are discarded.
2. **Frequency Counting**: For each valid text file, we count occurrences of these task tokens in:
   - File's relative path (lowercase, weighted: **3 points per occurrence**).
   - File's content (lowercase, weighted: **1 point per occurrence**, capped at **10 occurrences per unique token** to prevent extremely large files from dominating).
3. **Depth Penalty**: A penalty is applied to favor files closer to the project root:
   $$\text{score} = \frac{\text{path\_matches} \times 3 + \text{content\_matches} \times 1}{\text{len(file\_content)} \times (1 + \text{depth})}$$
   where `depth` is the number of path separators (e.g. `/` or `\`) in the relative path.
4. **Ordering**: Files with `status != 'text'` get a score of `0`. The file list is sorted by `score` in descending order. If there is a tie, files are sorted alphabetically by their relative path.

### Alternatives Rejected with Reasons

- **TF-IDF Similarity**: Rejected because calculating document frequencies requires gathering global term counts across all files prior to indexing, which increases computational complexity and memory usage for a simple CLI utility.
- **Semantic Vector Embeddings**: Rejected because it requires external API network calls, violates the offline-first constraint, requires third-party libraries (e.g. `numpy` or `tiktoken`), and introduces non-deterministic outputs.

---

## (5) Truncation Policy

If a high-ranked file's full markdown block (including headings and code block separators) exceeds the remaining token budget:

1. Calculate the available budget space for content: $\text{remaining\_tokens} - 50$ tokens (which reserves 50 tokens for the markdown headers and surrounding syntax).
2. Truncate the file content at line boundaries such that the resulting file block (including the header, truncated content, and a `[TRUNCATED: N lines omitted]` trailer) fits exactly within the remaining budget.
3. If not even a single line of the file's content can fit within the remaining budget minus 50 tokens, the file MUST be skipped entirely and marked as excluded with the reason `budget exhausted`.

---

## (6) Noise Detection

To optimize budget utilization and prevent cluttering the LLM context, ctxpack implements strict, deterministic filters:

### Directory Blocklist

Any file located inside these directories (or their subdirectories) is marked as `noise_dir` and excluded:
- `.git`, `.hg`, `.svn`, `node_modules`, `__pycache__`, `.venv`, `venv`, `env`, `dist`, `build`, `.next`, `target`, `.idea`, `.vscode`.

### File Extension Blocklist

Files ending with the following extensions are marked as `noise_ext` and excluded:
- `.lock`, `.min.js`, `.min.css`, `.map`, `.pyc`, `.pyo`, `.class`, `.o`, `.so`, `.dll`, `.exe`, `.whl`, `.egg`.

### File Size Limit

Any file exceeding **1,048,576 bytes (1 MB)** is marked as `too_large` and excluded.

---

## (7) Determinism Guarantee

To guarantee byte-identical (byte-for-byte) output across identical runs and different platforms:

1. **Preserve Walk Order**: The recursive walker MUST sort the list of discovered files alphabetically by relative path before any scoring, ranking, or packing occurs.
2. **Deterministic Tie-Breaking**: When two files have the same relevance score, their relative paths are compared alphabetically to determine their sort order.
3. **Sorted Manifest Serialization**: Manifest keys MUST be serialized deterministically. The JSON encoder must be configured with sorted keys: `json.dumps(manifest, sort_keys=True, indent=2)`.
4. **Alphabetical Directory Tree**: If a directory tree is included in the output bundle, directories and files in the tree representation MUST be generated in alphabetical order.

---

## (8) Definition of Done

The `ctxpack` tool is considered complete and production-ready when the following criteria are met:

- [ ] Command-line argument parser handles all five flags (`--path`, `--task`, `--budget`, `--out`, `--manifest`) and enforces validation correctly.
- [ ] Correct exit codes are returned under all conditions (0 on success, 1 on invalid arguments, 2 on missing/unreadable paths).
- [ ] No raw Python tracebacks escape to the user; all exceptions are caught, and clean, user-friendly, single-line error messages are printed to `stderr`.
- [ ] Walk phase correctly discovers, classifies, and filters noise directories, noise extensions, binary files, and files exceeding the 1 MB limit.
- [ ] Relevance score calculations exactly follow the keyword overlap algorithm with the 3x path weight, content cap of 10, normalization, and depth penalty.
- [ ] Bundle assembler strictly respects the hard token budget ceiling based on the entire output bundle size, conditionally including the directory tree (only if ≤ 5% of budget) and applying truncation cleanly.
- [ ] Determinism is validated: running the tool twice on the same folder produces byte-identical outputs.
- [ ] Codebase has zero third-party dependencies and runs purely using Python's standard library.
