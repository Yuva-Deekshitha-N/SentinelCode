# SentinelCodeAI

Static analysis tool that detects secrets, memory leaks, and sensitive context in any language — with automatic Git pre-commit hook integration.

## Structure

```
src/core/secrets.py           # Regex-based secret detection (15 patterns)
src/core/leaks.py             # Multi-language memory leak detection
src/core/cpp_ast.py           # C/C++ AST-based analysis
src/core/fixer.py             # Auto-fix hardcoded secrets
src/ai/nlp.py                 # NLP keyword context analysis
src/git_hooks/pre_commit.py   # Git pre-commit hook logic
src/scanner.py                # Shared scan + display engine
src/cli.py                    # CLI entry point
install_hook.py               # One-time hook installer
```

## Setup

### Option A — pip install (hook auto-installs)
```bash
pip install sentinelcodeai
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

# auto-fix hardcoded secrets
sentinel --path path/to/folder/ --fix

# without pip install
python -m src.cli --path path/to/file_or_folder
```

## Auto-Fix Secrets

The `--fix` flag automatically replaces hardcoded secrets with `os.environ` references:

```bash
sentinel --path your_project/ --fix
```

**Before:**
```python
password = "supersecret123"
api_key = "AIzaSyD-9tSrke72I6hDl53b2yhsQ0T9H8ntxyz"
```

**After:**
```python
import os
password = os.environ["DB_PASSWORD"]
api_key = os.environ["GOOGLE_API_KEY"]
```

**Note:** `--fix` runs separately from scanning — it modifies files directly. Always review changes with `git diff` before committing.

---

## Ignore Files with `.sentinelignore`

Create a `.sentinelignore` file in your project root to skip certain files/folders:

```
# .sentinelignore
tests/
*.example.py
config.sample.js
docs/
```

Works like `.gitignore` — supports file patterns and folder paths.

---

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

**Important:** The hook runs BEFORE the commit is saved — secrets never enter git history.

## Run Tests

```bash
pytest tests/
```
