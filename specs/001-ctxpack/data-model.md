# Data Model: ctxpack CLI Tool

## 1. Entities

### FileItem

Represents a single file discovered during directory traversal, along with its metadata, classification status, relevance score, and exclusion/inclusion reasoning.

| Attribute | Type | Description |
|:---|:---|:---|
| `path` | String | Relative file path from the specified root directory (`--path`). |
| `status` | String | Classification state: `text`, `binary`, `noise_dir`, `noise_ext`, `too_large`, `unreadable`, `budget exhausted`. |
| `content` | String \| None | Raw file contents (only populated if `status` is `text` or truncated). |
| `tokens` | Integer | The token count contributed by this file's markdown block (0 if excluded). |
| `score` | Float | Calculated relevance score (0 if non-text). |
| `reason` | String | Explanation of inclusion or exclusion (e.g. `relevance_score: 1.54`, `noise_dir`, `budget exhausted`). |

### Bundle

Represents the aggregated markdown output containing the directory structure tree and the included files formatted with markdown headers and code blocks.

| Attribute | Type | Description |
|:---|:---|:---|
| `header` | String | Root header of the markdown output (`# ctxpack bundle\n\n`). |
| `tree` | String \| None | visual ASCII representation of the directory structure (if within the 5% budget threshold). |
| `content` | String | Concatenated file markdown blocks. |
| `tokens` | Integer | Total token count of the compiled bundle string. |

### Manifest

Represents the overall execution summary and audit trail, capturing the state of every file considered.

| Attribute | Type | Description |
|:---|:---|:---|
| `budget` | Integer | Configured token budget ceiling. |
| `used` | Integer | Token count of the actual assembled bundle string. |
| `included` | List[FileItem] | Collection of files successfully written into the bundle (with partial or full content). |
| `excluded` | List[FileItem] | Collection of files skipped, ignored, or truncated entirely. |

---

## 2. Relationships

- A `Manifest` has a **1-to-Many** relationship with `included` `FileItem`s.
- A `Manifest` has a **1-to-Many** relationship with `excluded` `FileItem`s.
- A `Bundle` is composed of **0-or-1** directory tree, and **1-to-Many** formatted blocks matching the `included` list of `FileItem`s in the `Manifest`.

---

## 3. State Transitions for FileItem

```text
[Discovered File]
       │
       ├── Matches directory blocklist? ──────► [noise_dir] (Excluded)
       │
       ├── Matches extension blocklist? ──────► [noise_ext] (Excluded)
       │
       ├── Size > 1 MB? ──────────────────────► [too_large] (Excluded)
       │
       ├── Fails UTF-8 reading/binary test? ──► [binary or unreadable] (Excluded)
       │
       └── Readable UTF-8 Text ───────────────► [text]
                                                    │
                                             Ranked & Packed
                                                    │
                                                    ├── Fits in budget? ──────► [included: fully packed]
                                                    │
                                                    ├── Partially fits? ──────► [included: truncated]
                                                    │
                                                    └── Budget exhausted? ────► [excluded: budget exhausted]
```
