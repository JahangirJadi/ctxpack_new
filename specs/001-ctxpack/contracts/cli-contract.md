# CLI and Programmatic Contract: ctxpack

As a pure Python CLI utility with zero external dependencies, `ctxpack` defines two strict contracts:
1. **The Command Line Interface (CLI) Contract**
2. **The Programmatic API Interface (Python) Contract**

---

## 1. Command Line Interface (CLI) Contract

### Command Invocation

```bash
ctxpack --path <path> --task <task_string> --budget <budget_integer> [--out <output_file>] [--manifest <manifest_file>]
```

### Options

| Flag | Type | Required | Default | Description |
|:---|:---|:---|:---|:---|
| `--path` | Directory Path | Yes | N/A | Absolute or relative path of the folder to traverse. |
| `--task` | String | Yes | N/A | Task description string for keyword-relevance ranking. |
| `--budget` | Integer | Yes | N/A | Hard maximum limit of estimated tokens for the bundle. |
| `--out` | File Path | No | `stdout` | File path to write the markdown bundle. |
| `--manifest`| File Path | No | `stderr` | File path to save the full JSON manifest. |

---

## 2. Programmatic Python Contract

For programmatic imports and test suites, the `ctxpack` module exposes the following standard library function signatures:

### `walk_files`
```python
def walk_files(path: str) -> list[dict]:
    """
    Recursively traverses the path, classifying files and checking readability.
    
    Args:
        path (str): The folder path to traverse.
        
    Returns:
        list[dict]: A list of dicts sorted alphabetically by relative path, each containing:
            - 'path': relative path (str)
            - 'content': UTF-8 text contents or None (str/None)
            - 'tokens': calculated token count (int)
            - 'status': classification status (str)
            - 'reason': explanation for exclusion/status (str)
    """
```

### `rank_files`
```python
def rank_files(files: list[dict], task: str) -> list[dict]:
    """
    Ranks text files by relevance to the task description.
    
    Args:
        files (list[dict]): The output of walk_files.
        task (str): The task description string.
        
    Returns:
        list[dict]: Sorted list of files by score descending, breaking ties alphabetically by path.
    """
```

### `assemble_bundle`
```python
def assemble_bundle(ranked_files: list[dict], budget: int, path: str) -> tuple[str, list[dict], list[dict]]:
    """
    Greedily packs files into a markdown bundle, enforcing the token budget ceiling.
    
    Args:
        ranked_files (list[dict]): The ranked list of files.
        budget (int): The maximum token budget.
        path (str): The folder path being packed.
        
    Returns:
        tuple[str, list[dict], list[dict]]: A tuple containing:
            - bundle_str (str): The formatted markdown bundle.
            - included_list (list[dict]): Metadata of included files.
            - excluded_list (list[dict]): Metadata of excluded files.
    """
```

### `build_manifest`
```python
def build_manifest(budget: int, bundle: str, included: list[dict], excluded: list[dict]) -> dict:
    """
    Constructs the detailed JSON manifest dict.
    
    Args:
        budget (int): The original budget.
        bundle (str): The final bundle markdown string.
        included (list): List of included files.
        excluded (list): List of excluded files.
        
    Returns:
        dict: The serialized JSON-compliant manifest dictionary.
    """
```
