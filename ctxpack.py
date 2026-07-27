import argparse
import sys
import os
import json
from math import ceil
import re
import fnmatch

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"Error: {message}\n")
        sys.exit(1)

def load_gitignore(path: str) -> list[str]:
    gitignore_path = os.path.join(path, '.gitignore')
    patterns = []
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    patterns.append(line)
        except Exception:
            pass
    return patterns

def is_ignored(rel_path: str, patterns: list[str]) -> bool:
    # Normalize path separators to forward slashes for matching
    rel_path_norm = rel_path.replace('\\', '/')
    parts = rel_path_norm.split('/')
    for pattern in patterns:
        pattern = pattern.replace('\\', '/')
        anchored = False
        if pattern.startswith('/'):
            pattern = pattern[1:]
            anchored = True
        
        is_dir_pattern = pattern.endswith('/')
        if is_dir_pattern:
            pattern = pattern[:-1]

        has_slash = '/' in pattern

        if not has_slash and not anchored:
            # Match against any part of the path
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        else:
            # Match against the entire relative path or a prefix
            if fnmatch.fnmatch(rel_path_norm, pattern) or fnmatch.fnmatch(rel_path_norm, pattern + '/*'):
                return True
    return False

def walk_files(path: str) -> list[dict]:
    abs_path = os.path.abspath(path)
    results = []

    NOISE_DIRS = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', '.next', 'target', '.idea', '.vscode'}
    NOISE_EXTS = {'.lock', '.min.js', '.min.css', '.map', '.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.exe', '.whl', '.egg'}
    MAX_SIZE = 1_048_576

    gitignore_patterns = load_gitignore(abs_path)

    for root, dirs, files in os.walk(abs_path):
        rel_root = os.path.relpath(root, abs_path).replace(os.path.sep, '/')
        
        # Check if the current directory is inside a noise directory or ignored by gitignore
        in_noise_dir = False
        in_ignored_dir = False
        if rel_root != '.':
            parts = rel_root.split('/')
            if any(p in NOISE_DIRS for p in parts):
                in_noise_dir = True
            if gitignore_patterns and is_ignored(rel_root, gitignore_patterns):
                in_ignored_dir = True

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, abs_path).replace(os.path.sep, '/')

            # 1. Check if inside noise directory
            if in_noise_dir:
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'noise_dir',
                    'reason': "Excluded: noise directory"
                })
                continue

            # 2. Check if inside ignored directory or file is ignored by gitignore
            if in_ignored_dir or (gitignore_patterns and is_ignored(rel_path, gitignore_patterns)):
                results.append({
                    'path': rel_path,
                    'content': None,
                    'tokens': 0,
                    'status': 'ignored',
                    'reason': "Excluded: matched .gitignore pattern"
                })
                continue

            # 3. Check noise extensions
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

            # 4. Check file readability and size
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
            f['score'] = 0.0
            continue

        path_lower = f['path'].lower()
        content_lower = f['content'].lower()
        total = 0.0

        for token in tokens:
            path_score = 3.0 * path_lower.count(token)
            content_score = min(content_lower.count(token), 10.0)
            total += path_score + content_score

        depth = f['path'].count('/')
        f['score'] = total / (1.0 + depth)

    return sorted(files, key=lambda f: (-f['score'], f['path']))

def format_file_block(path: str, content: str) -> str:
    return f"## {path}\n\n```\n{content}\n```\n\n"

NOISE_DIRS_TREE = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', '.next', 'target', '.idea', '.vscode'}

def generate_tree(path: str) -> str:
    abs_path = os.path.abspath(path)
    root_name = os.path.basename(abs_path) or abs_path
    lines = [f"{root_name}/"]
    
    gitignore_patterns = load_gitignore(abs_path)

    def _build_tree(dirpath, prefix=""):
        try:
            entries = sorted(os.listdir(dirpath))
        except OSError:
            return
        dirs = []
        files = []
        for e in entries:
            full = os.path.join(dirpath, e)
            rel = os.path.relpath(full, abs_path).replace(os.path.sep, '/')
            
            if os.path.isdir(full):
                if e in NOISE_DIRS_TREE:
                    continue
                if gitignore_patterns and is_ignored(rel, gitignore_patterns):
                    continue
                dirs.append(e)
            else:
                if gitignore_patterns and is_ignored(rel, gitignore_patterns):
                    continue
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
    if ceil(len(bundle) / 4) > budget:
        bundle = ""

    included = []
    excluded = []

    tree_str = generate_tree(path)
    tree_tokens = ceil(len(tree_str) / 4)
    tree_budget_share = budget * 0.05
    
    if tree_tokens <= tree_budget_share:
        candidate_bundle = bundle + tree_str + "\n"
        if ceil(len(candidate_bundle) / 4) <= budget:
            bundle = candidate_bundle
        else:
            excluded.append({
                'path': '__directory_tree__',
                'content': None,
                'tokens': tree_tokens,
                'status': 'noise_dir',
                'reason': 'Directory tree does not fit in remaining budget',
                'score': 0.0
            })
    else:
        excluded.append({
            'path': '__directory_tree__',
            'content': None,
            'tokens': tree_tokens,
            'status': 'noise_dir',
            'reason': f'Directory tree exceeds 5% budget threshold ({tree_tokens} > {int(tree_budget_share)} tokens)',
            'score': 0.0
        })

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
                f_copy = f.copy()
                f_copy['reason'] = "budget exhausted"
                excluded.append(f_copy)
                continue
            
            block = format_file_block(f['path'], truncated)
            block_tokens = ceil(len(bundle + block) / 4)
            if block_tokens <= budget:
                bundle += block
                f_truncated = f.copy()
                f_truncated['tokens'] = ceil(len(truncated) / 4)
                f_truncated['is_truncated'] = True
                included.append(f_truncated)
            else:
                f_copy = f.copy()
                f_copy['reason'] = "budget exhausted"
                excluded.append(f_copy)

    return bundle, included, excluded

def build_manifest(budget: int, bundle: str, included: list[dict], excluded: list[dict]) -> dict:
    manifest_included = []
    for f in included:
        score = f.get('score', 0.0)
        is_truncated = f.get('is_truncated', False)
        reason = f"relevance score: {score:.2f}"
        if is_truncated:
            reason += " (truncated)"
        manifest_included.append({
            'path': f['path'],
            'tokens': f.get('tokens', 0),
            'reason': reason
        })

    manifest_excluded = []
    for f in excluded:
        reason = f.get('reason', '')
        if not reason:
            status = f.get('status', '')
            if status == 'noise_dir':
                reason = "Excluded: noise directory"
            elif status == 'noise_ext':
                reason = "Excluded: noise file extension"
            elif status == 'too_large':
                reason = "Excluded: file size too large (> 1MB)"
            elif status == 'binary':
                reason = "Excluded: binary file"
            elif status == 'unreadable':
                reason = "Excluded: unreadable file"
            elif status == 'ignored':
                reason = "Excluded: matched .gitignore pattern"
            else:
                reason = f"Excluded: status {status}"
        manifest_excluded.append({
            'path': f['path'],
            'reason': reason
        })

    return {
        'budget': budget,
        'used': ceil(len(bundle) / 4),
        'included': manifest_included,
        'excluded': manifest_excluded,
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

    sys.stderr.write(f"ctxpack: {manifest['used']}/{manifest['budget']} tokens used, "
                     f"{len(manifest['included'])} files included, "
                     f"{len(manifest['excluded'])} files excluded\n")

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
        if not os.path.exists(args.path):
            sys.stderr.write(f"Error: Path '{args.path}' does not exist\n")
            sys.exit(2)
        if not os.path.isdir(args.path):
            sys.stderr.write(f"Error: Path '{args.path}' is not a directory\n")
            sys.exit(2)
        if not os.access(args.path, os.R_OK):
            sys.stderr.write(f"Error: Path '{args.path}' is not readable (permission denied)\n")
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
