# JOURNAL.md - Engineering Journal

## 1. Three decisions we made, and what we rejected in each case.

- **Decision 1: Keyword overlap with depth penalty for ranking.** We rejected TF-IDF because calculating global document frequencies requires multiple passes over all files, increasing memory and overhead for a simple CLI. We also rejected Semantic Vector Embeddings because it requires network access (violating the offline constraint), extra third-party libraries, and is non-deterministic.
- **Decision 2: Line-by-line head truncation with a 50-token margin.** We rejected arbitrary word/character truncation because breaking lines mid-word or mid-sentence creates unreadable code blocks. We also rejected tail-only truncation or semantic sectioning because it is too complex for a standard-library-only tool.
- **Decision 3: Walk-and-classify approach for noise directories (walking them but skipping read).** We rejected completely pruning noise directories because that would make it impossible to list individual noise files in the manifest (violating "say so in the manifest" requirement). We also rejected reading all noise files because it would be too slow and fail the speed/time limits.

## 2. The hardest bug we hit, and how we found the root cause.

- The hardest bug was cross-platform determinism of file paths and ranking score depth penalties. Specifically, on Windows, file path separators are backslashes `\`, whereas on Unix they are forward slashes `/`. This meant that running `ctxpack` on the exact same directory across different OS platforms produced different manifest JSON outputs (violating byte-identical determinism constraint SC-001) and also resulted in incorrect depth penalty calculations because depth relied on `os.sep`. We identified this by analyzing how `rel_path` was handled and solved it by normalizing all path separators to forward slashes `/` inside `walk_files` and `generate_tree`.

## 3. Something Claude Code got wrong or confidently misled us on, and how we caught it.

- Claude Code generated a manifest builder that returned `'score'` inside `included` objects instead of the required `'reason'` key, and `'status'` inside `excluded` objects instead of only having `'path'` and `'reason'` keys. It also didn't populate the `reason` key for text files excluded due to budget exhaustion (leaving them as empty strings). We caught this by carefully auditing the code against the exact JSON schema requested in the brief: `{"budget": 8000, "used": 7912, "included": [{"path": "...", "tokens": 812, "reason": "..."}], "excluded": [{"path": "...", "reason": "..."}]}`.

## 4. What we would do differently with two more hours.

- If we had two more hours, we would implement more sophisticated glob matching for `.gitignore` files (supporting negations `!` and double asterisks `**` edge cases perfectly), add support for custom user-defined ignore files (`.ctxpackignore`), and implement a concurrency mechanism for walking and processing text files safely to speed up execution on directories containing more than 10,000 files.

## 5. Who wrote what — per person.

- We worked as a unified pair programming team. The initial specification and structure was drafted collaboratively, while the core implementation of the CLI argument parsing, ranking algorithm, and `.gitignore` integration was written during our active pair programming session, iteratively debugging issues like cross-platform path separators and manifest schema mismatches.
