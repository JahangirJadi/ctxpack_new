# CLAUDE.md - ctxpack Context

## Project Purpose
`ctxpack` is a single-file Python CLI utility designed to recursively crawl a directory, filter out development noise and binary files, rank remaining text files by relevance to a given task description using keyword-overlap, and bundle them into a single markdown file respecting a strict token budget.

## Architecture
The tool consists of the following components implemented purely inside `ctxpack.py`:
1. **CLI Argument Parser**: Custom subclass of `argparse.ArgumentParser` that intercepts errors, outputting a clean single line to `stderr` with exit code 1.
2. **File Walker**: Recursive directory explorer using `os.walk` with alphabetized sorting and blocklists.
3. **Relevance Ranker**: Lowercase keyword-overlap counter with path boosts, content capping (10), normalization, and depth penalties.
4. **Bundle Assembler**: Greedily packs files, calculates token sizes using `math.ceil(len(text) / 4)`, and handles conditional directory tree representation and head truncation.
5. **Manifest Builder**: Generates the audit summary dictionary.
6. **Output Writer**: Outputs the bundle to stdout/file, and the manifest to stderr/file.

## CLI Contract
- Invocations: `ctxpack --path <dir> --task <string> --budget <int> [--out <file>] [--manifest <file>]`
- Exit Codes: `0` on success, `1` on invalid arguments, `2` on path missing/unreadable.

## Core Invariants
- **Never exceed token budget** by even a single token.
- **100% Deterministic**: Alphabetize walkers, tie-breakers, and sorted JSON manifest dumps.
- **Fail Loudly**: No raw tracebacks may reach the user. Intercept all unexpected exceptions in `main()` with exit code 1.
- **Zero Third-Party Dependencies**: Standard library imports only.
