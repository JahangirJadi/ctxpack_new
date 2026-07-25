# Research Document: ctxpack CLI Tool

## 1. CLI Argument Parsing and Validation

- **Decision**: Use the standard library `argparse` module.
- **Rationale**: Meets the zero-dependencies constraint. To fulfill the requirement of failing loudly on invalid arguments with exit code 1 (while avoiding standard multi-line tracebacks/usage outputs), we will subclass `argparse.ArgumentParser` and override its `error(self, message)` method to print a concise, one-line message to `stderr` and call `sys.exit(1)`.
- **Alternatives Considered**:
  - `sys.argv` manual parsing: Rejected because it is error-prone, fragile, and lacks structured help generation.

## 2. Walk Phase & Binary Detection

- **Decision**: Recursively walk the `--path` using `os.walk`.
  - At each directory node, sort the directory list and file list alphabetically in-place to guarantee deterministic walker traversal.
  - To check if a file is text vs. binary/unreadable:
    - Attempt to open it with UTF-8 encoding.
    - Check the first block of data (e.g. 1024 bytes) for binary control characters (such as null bytes `\x00`).
    - If a `UnicodeDecodeError` or `IOError` is raised, gracefully classify it as `binary or unreadable` without crashing.
- **Rationale**: Robust, performant, and fully deterministic offline processing.

## 3. Relevance Ranking Model

- **Decision**: Keyword overlap scoring with a depth penalty.
  - Tokenize `--task` into lowercase alphanumeric words of length $\ge 3$.
  - For each text file, count matching token occurrences:
    - Relative path matches: 3 points per occurrence.
    - File content matches: 1 point per occurrence, capped at 10 points per unique token to prevent oversized files with repetitive words from dominating.
  - Apply normalization and depth penalty:
    $$\text{score} = \frac{\text{path\_score} + \text{content\_score}}{\text{len(file\_content)} \times (1 + \text{depth})}$$
    where `depth` is the number of path separators (e.g. `/`) in the relative path.
  - Sort ranked list by `score` descending, then alphabetically by relative path to break ties.
- **Rationale**: Simple, highly performant, completely offline, and perfectly deterministic.

## 4. Bundle Assembly & Truncation Mechanics

- **Decision**: 
  - Generate the directory tree first in alphabetical order. If the tree's token count (using `math.ceil(len(tree_str) / 4)`) is $\le 5\%$ of the total budget, include it at the top of the bundle.
  - Iterate through the ranked files. For each file, compute its full markdown block:
    ```markdown
    ## {path}

    ```
    {content}
    ```


    ```
  - Measure the cumulative token count of the entire assembled bundle string (`math.ceil(len(bundle) / 4)`) after appending each file block.
  - If a file block does not fit within the remaining budget, calculate the maximum content tokens available ($\text{remaining\_tokens} - 50$ tokens) and truncate the content at the nearest line boundary. Append the `[TRUNCATED: N lines omitted]` marker inside the code block.
  - If even a single line from the truncated head does not fit, exclude the file completely with the reason `budget exhausted`.
- **Rationale**: Ensures the final bundle token size is strictly within the hard token budget ceiling while maximizing the context of high-relevance files.
