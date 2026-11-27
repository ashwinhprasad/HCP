# hcp — hierarchical copy

`hcp` copies files and directories selected by a regular expression while
preserving each item's directory hierarchy relative to the source directory.

It uses only the Python standard library.

## Requirements

- Python 3.8 or newer
- macOS, Linux, or Windows

## Install

Make the script executable on macOS/Linux:

```bash
chmod +x hcp
```

Put it somewhere on your `PATH`, or invoke it as `./hcp`.

On Windows, run it with:

```powershell
python hcp <source> <destination> <regex>
```

## Usage

```bash
hcp <source_directory> <destination_directory> <regex-file-matcher>
```

Examples:

```bash
# Copy every Markdown file
hcp ./docs ./docs-subset '\.md$'

# Copy AGENTS.md and index.md wherever they occur
hcp ./project ./context '^(AGENTS\.md|index\.md)$'

# Copy every directory named docs, with everything inside
hcp ./project ./out '^docs$'

# Copy files named config.json
hcp ./project ./configs '^config\.json$'

# Match against the relative path instead of the basename (partial match)
hcp ./project ./out 'docs/api' --full-path

# Pick one specific directory among same-named ones in other subtrees
hcp ./project ./out '^a/docs$' --full-path

# Pick several specific directories
hcp ./project ./out '^(a/docs|b/assets)$' --full-path

# Preview without creating or changing destination files
hcp ./project ./context '\.md$' --dry-run
```

## Behaviour

- The regex is compiled using Python's `re` module and searched against the
  **basename only** (for example, `index.md`, not `parrtos/index.md`). This
  applies to both file and directory names.
- With `--full-path`, the regex is instead searched against the path relative
  to the source directory, always with `/` separators (for example
  `a/docs/x.txt`, `a/docs`). It is still a search, so partial patterns work;
  anchor with `^`/`$` for exact paths. Notes:
  - `docs/api` also matches `a/docs/apiv2` and `a/docs/api.md`; use `docs/api$`
    for an exact name.
  - Directory paths have no trailing slash, so `docs/` matches the files under
    `a/docs` (copied individually), not the directory itself; use `docs$`.
  - Paths are relative to the source root; don't start patterns with `/`.
- Matching files are copied to the same relative path under the destination.
- A matching directory is copied recursively with all its contents (symlinks
  skipped) to the same relative path. Its contents are not matched separately.
  Non-matching directories are still searched.
- Required parent directories are created automatically.
- Hidden files are included if their basenames match.
- Existing matching destination files are overwritten.
- Unmatched destination files are left untouched.
- Symbolic-link files and symbolic-link directories are skipped.
- File metadata is copied using `shutil.copy2` where supported by the OS.
- An empty match set prints a message and exits successfully.
- `--dry-run` lists planned copies and does not create the destination.
- Source and destination cannot be the same directory or nested inside one
  another.
- Regex syntax follows Python `re`, not necessarily the syntax of `grep -E`
  or PCRE. Matching is case-sensitive unless the expression opts out, e.g.
  `(?i)\.md$`.

## Exit codes

- `0`: success (including no matching files)
- `1`: one or more files could not be inspected or copied
- `2`: invalid arguments, paths, or regular expression

## Tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

The tests use temporary directories and do not modify your project files.
