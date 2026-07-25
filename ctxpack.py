import argparse
import sys
import os
import json
from math import ceil
import re

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"Error: {message}\n")
        sys.exit(1)

def walk_files(path: str) -> list[dict]:
    abs_path = os.path.abspath(path)
    results = []

    NOISE_DIRS = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', '.next', 'target', '.idea', '.vscode'}
    NOISE_EXTS = {'.lock', '.min.js', '.min.css', '.map', '.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.exe', '.whl', '.egg'}
    MAX_SIZE = 1_048_576

    for root, dirs, files in os.walk(abs_path):
        dirs[:] = [d for d in dirs if d not in NOISE_DIRS]

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, abs_path)

            matched_ext = None
            for ext in NOISE_EXTS:
                if file.endswith(ext):
                    matched_ext = ext
                    break

            if matched_ext:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'noise_ext',
                    'reason': f"Skipped file with extension: {matched_ext}"
                })
                continue

            try:
                size = os.path.getsize(file_path)
            except OSError:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'unreadable',
                    'reason': "Could not determine file size"
                })
                continue

            if size > MAX_SIZE:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'too_large',
                    'reason': f"File size {size} exceeds maximum allowed size of {MAX_SIZE} bytes"
                })
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                results.append({
                    'path': rel_path,
                    'content': content,
                    'tokens': ceil(len(content) / 4),
                    'status': 'text',
                    'reason': ""
                })
            except UnicodeDecodeError:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'binary',
                    'reason': "File is binary (could not decode as UTF-8)"
                })
            except IOError:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'unreadable',
                    'reason': "File could not be read"
                })

    results.sort(key=lambda r: r['path'])
    return results


def rank_files(files: list[dict], task: str) -> list[dict]:
    tokens = [t.lower() for t in re.findall(r'[a-zA-Z0-9]+', task) if len(t) >= 3]

    for f in files:
        if f['status'] != 'text':
            f['score'] = 0
            continue

        path_lower = f['path'].lower()
        content_lower = f['content'].lower()
        total = 0

        for token in tokens:
            path_score = 3 * path_lower.count(token)
            content_score = min(content_lower.count(token), 10)
            total += path_score + content_score

        depth = f['path'].count(os.sep)
        f['score'] = total / (1 + depth)

    return sorted(files, key=lambda f: (-f['score'], f['path']))


def format_file_block(path: str, content: str) -> str:
    return f"## {path}\n\n```\n{content}\n```\n\n"

NOISE_DIRS_TREE = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', '.next', 'target', '.idea', '.vscode'}

def generate_tree(path: str) -> str:
    abs_path = os.path.abspath(path)
    root_name = os.path.basename(abs_path) or abs_path
    lines = [f"{root_name}/"]

    def _build_tree(dirpath, prefix=""):
        try:
            entries = sorted(os.listdir(dirpath))
        except OSError:
            return
        dirs = []
        files = []
        for e in entries:
            full = os.path.join(dirpath, e)
            if os.path.isdir(full):
                if e not in NOISE_DIRS_TREE:
                    dirs.append(e)
            else:
                files.append(e)
        all_entries = dirs + files
        for i, name in enumerate(all_entries):
            is_last = i == len(all_entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            full = os.path.join(dirpath, name)
            if os.path.isdir(full):
                extension = "    " if is_last else "│   "
                _build_tree(full, prefix + extension)

    _build_tree(abs_path)
    return "\n".join(lines) + "\n"

def truncate_file_content(content: str, remaining_budget: int) -> str:
    margin = 50
    usable = remaining_budget - margin
    if usable <= 0:
        return ""
    lines = content.split("\n")
    truncated_lines = []
    for line in lines:
        candidate = "\n".join(truncated_lines + [line])
        marker = "\n[TRUNCATED]"
        candidate_with_marker = candidate + marker
        if ceil(len(candidate_with_marker) / 4) > usable:
            if not truncated_lines:
                return ""
            truncated_lines.append(marker)
            break
        truncated_lines.append(line)
    return "\n".join(truncated_lines)

def assemble_bundle(ranked_files: list[dict], budget: int, path: str) -> tuple[str, list[dict], list[dict]]:
    bundle = "# ctxpack bundle\n\n"
    included = []
    excluded = []

    tree_str = generate_tree(path)
    tree_tokens = ceil(len(tree_str) / 4)
    tree_budget_share = budget * 0.05
    if tree_tokens <= tree_budget_share and tree_tokens <= budget:
        bundle += tree_str + "\n"
    elif tree_tokens > tree_budget_share:
        excluded.append({'path': '__directory_tree__', 'content': None, 'tokens': tree_tokens, 'status': 'noise_dir',
                         'reason': f'Directory tree exceeds 5% budget threshold ({tree_tokens} > {int(tree_budget_share)} tokens)', 'score': 0})

    for f in ranked_files:
        if f['status'] != 'text':
            excluded.append(f)
            continue
        block = format_file_block(f['path'], f['content'])
        block_tokens = ceil(len(bundle + block) / 4)

        if block_tokens <= budget:
            bundle += block
            included.append(f)
        else:
            remaining = budget - ceil(len(bundle) / 4)
            truncated = truncate_file_content(f['content'], remaining)
            if not truncated:
                excluded.append(f)
                continue
            block = format_file_block(f['path'], truncated)
            block_tokens = ceil(len(bundle + block) / 4)
            if block_tokens <= budget:
                bundle += block
                included.append(f)
            else:
                excluded.append(f)

    return bundle, included, excluded


def build_manifest(budget: int, bundle: str, included: list[dict], excluded: list[dict]) -> dict:
    return {
        'budget': budget,
        'used': ceil(len(bundle) / 4),
        'included': [
            {'path': f['path'], 'tokens': f.get('tokens', 0), 'score': f.get('score', 0)}
            for f in included
        ],
        'excluded': [
            {'path': f['path'], 'status': f['status'], 'reason': f.get('reason', '')}
            for f in excluded
        ],
    }

def write_output(bundle: str, manifest: dict, out: str | None, manifest_path: str | None):
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(bundle)
    else:
        sys.stdout.write(bundle)

    if manifest_path:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

    sys.stderr.write(f"Bundle: {manifest['used']}/{manifest['budget']} tokens, "
                     f"{len(manifest['included'])} included, "
                     f"{len(manifest['excluded'])} excluded\n")

def main():
    try:
        parser = CustomArgumentParser(description="ctxpack CLI tool")
        parser.add_argument("--path", required=True, type=str, help="Path to the directory")
        parser.add_argument("--task", required=True, type=str, help="Task description")
        parser.add_argument("--budget", required=True, type=int, help="Budget value (integer)")
        parser.add_argument("--out", required=False, type=str, help="Optional output path")
        parser.add_argument("--manifest", required=False, type=str, help="Optional manifest path")

        args = parser.parse_args()

        # Validate budget
        if args.budget <= 0:
            sys.stderr.write("Error: Budget must be greater than 0\n")
            sys.exit(1)

        # Validate path
        if not os.path.isdir(args.path):
            sys.stderr.write(f"Error: Path '{args.path}' does not exist or is not a directory\n")
            sys.exit(2)

        files = walk_files(args.path)
        ranked = rank_files(files, args.task)
        bundle, included, excluded = assemble_bundle(ranked, args.budget, args.path)
        manifest = build_manifest(args.budget, bundle, included, excluded)
        write_output(bundle, manifest, args.out, args.manifest)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

def global_excepthook(exc_type, exc_value, traceback):
    sys.stderr.write(f"Error: {exc_value}\n")
    sys.exit(1)

sys.excepthook = global_excepthook

if __name__ == "__main__":
    main()
