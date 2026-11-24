# hcp — hierarchical copy

`hcp` copies files selected by a regular expression while preserving each
file's directory hierarchy relative to the source directory.

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

# Copy files named config.json
hcp ./project ./configs '^config\.json$'

# Preview without creating or changing destination files
hcp ./project ./context '\.md$' --dry-run
```

## Behaviour

- The regex is compiled using Python's `re` module and searched against the
  **basename only** (for example, `index.md`, not `parrtos/index.md`).
- Matching files are copied to the same relative path under the destination.
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
