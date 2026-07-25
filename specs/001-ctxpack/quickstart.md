# Quickstart Guide: ctxpack CLI Tool

`ctxpack` is a fast, deterministic, zero-dependency Python command-line tool designed to pack folder contents into a single markdown bundle suitable for sending to large language models (LLMs).

## 1. Prerequisites

- Python 3.10 or higher.
- No third-party packages or virtual environments needed.

---

## 2. Basic Command Line Usage

To run `ctxpack` from your terminal:

```bash
python ctxpack.py --path <folder_to_pack> --task "fix bugs" --budget 4000
```

### Advanced Usage Examples

1. **Pack files and output to a file**:
   ```bash
   python ctxpack.py --path ./src --task "add database index" --budget 10000 --out bundle.md
   ```

2. **Save a detailed JSON manifest for auditing**:
   ```bash
   python ctxpack.py --path ./src --task "write tests" --budget 8000 --out bundle.md --manifest manifest.json
   ```

---

## 3. Programmatic Python Import

You can import components directly within your Python scripts:

```python
import ctxpack

# 1. Walk and classify files
files = ctxpack.walk_files("./src")

# 2. Rank files by relevance
ranked = ctxpack.rank_files(files, "implement login")

# 3. Assemble the bundle
bundle, included, excluded = ctxpack.assemble_bundle(ranked, 8000, "./src")

print(f"Generated a {len(bundle)} char bundle!")
```
