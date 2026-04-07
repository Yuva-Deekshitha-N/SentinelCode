# SentinelCodeAI

Static analysis tool that detects secrets, memory leaks, and sensitive context in any language — with automatic Git pre-commit hook integration.

## Structure

```
src/core/secrets.py           # Regex-based secret detection (11 patterns)
src/core/leaks.py             # AST-based memory leak detection
src/ai/nlp.py                 # NLP keyword context analysis
src/git_hooks/pre_commit.py   # Git pre-commit hook logic
src/scanner.py                # Shared scan + display engine
src/cli.py                    # CLI entry point
install_hook.py               # One-time hook installer
```

## Setup

### Option A — pip install (hook auto-installs)
```bash
pip install -e .
```

### Option B — clone without pip
```bash
pip install -r requirements.txt
python install_hook.py
```

## Scan manually (file or folder)

```bash
# scan a single file
sentinel --path path/to/file.py

# scan an entire folder
sentinel --path path/to/folder/

# without pip install
python -m src.cli --path path/to/file_or_folder
```

## How the pre-commit hook works

Once installed, every `git commit` is automatically intercepted:

```
git commit -m "my changes"
      |
      v
SentinelCodeAI scans all staged files
      |
      v
HIGH risk found  --> commit BLOCKED + report shown
All clean        --> commit goes through
```

## Run Tests

```bash
pytest tests/
```
