# ctxpack

Zero-dependency Python CLI that packs folder files into a token-budgeted markdown bundle, ranked by relevance to a task.

```bash
python ctxpack.py --path ./src --task "fix bugs" --budget 4000 --out bundle.md --manifest manifest.json
```

## Features

- **Recursive walk** with noise directory/extension filtering
- **Binary detection** via UTF-8 decode attempt
- **Relevance ranking** by keyword overlap (3× path weight, 1× content weight capped at 10 per token, depth penalty)
- **Token budget enforcement** with `math.ceil(len(text)/4)` formula
- **Head-only truncation** with `[TRUNCATED]` marker and 50-token margin
- **Directory tree** included if ≤ 5% of budget
- **JSON manifest** with full audit trail (`--manifest`)
- **Deterministic** — byte-identical across identical runs

## CLI

| Flag | Required | Description |
|------|----------|-------------|
| `--path` | Yes | Directory to traverse |
| `--task` | Yes | Task description for ranking |
| `--budget` | Yes | Maximum token ceiling |
| `--out` | No | Output file (default: stdout) |
| `--manifest` | No | JSON manifest file (default: stderr summary) |

Exit codes: 0 success, 1 invalid args, 2 path not found.

## Python API

```python
from ctxpack import walk_files, rank_files, assemble_bundle, build_manifest

files = walk_files("./src")
ranked = rank_files(files, "implement login")
bundle, included, excluded = assemble_bundle(ranked, 8000, "./src")
manifest = build_manifest(8000, bundle, included, excluded)
```

## Install

Requires Python 3.10+. No third-party dependencies.

```bash
pip install -e .
# or just run directly:
python ctxpack.py --path . --task "hello" --budget 1000
```

## Test

```bash
python -m pytest
```
