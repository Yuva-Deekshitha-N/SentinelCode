# SentinelCodeAI — Usage Guide

## Installation

### Option A — pip install (recommended)
```bash
pip install sentinelcodeai
```
Hook installs automatically. No extra steps needed.

### Option B — without pip install
```bash
pip install -r requirements.txt
python install_hook.py
```

---

## Manual Scanning

Scan any file or folder at any time:

```bash
# Scan a single file
sentinel --path path/to/file.py

# Scan an entire folder (recursive)
sentinel --path path/to/project/

# Without pip install
python -m src.cli --path path/to/file_or_folder
```

### Example Output

```
Scanning 3 file(s) in: ./myproject

>> HIGH RISK in myproject/config.py
  password (line 4)
   Detected : password = "admin123"
   Why      : A plaintext password is hardcoded...

>> Leak Issues in myproject/db.py
  ast_malloc_no_free [AST] (line 12) [C/C++]
   Code     : ptr = malloc(sizeof(Node));
   Why      : [AST] malloc detected but no free() found...

SAFE: myproject/utils.py

HIGH risk issues found. Fix them before committing.
```

---

## Auto-Fix Secrets

The `--fix` flag automatically replaces hardcoded secrets with `os.environ` references.

```bash
sentinel --path your_project/ --fix
```

**When to use it:**
- After a scan shows HIGH risk secrets
- Before committing — fix first, then commit

**Before:**
```python
password = "supersecret123"
api_key = "AIzaSyD-9tSrke72I6hDl53b2yhsQ0T9H8ntxyz"
aws_key = "AKIAIOSFODNN7EXAMPLE"
```

**After:**
```python
import os
password = os.environ["DB_PASSWORD"]
api_key = os.environ["GOOGLE_API_KEY"]
aws_key = os.environ["AWS_ACCESS_KEY_ID"]
```

**What gets fixed automatically:**

| Secret Type | Replaced With |
|---|---|
| `password = "..."` | `os.environ["DB_PASSWORD"]` |
| `api_key = "..."` | `os.environ["API_KEY"]` |
| AWS Access Key literal | `os.environ["AWS_ACCESS_KEY_ID"]` |
| GitHub token (`ghp_...`) | `os.environ["GITHUB_TOKEN"]` |
| Google API key (`AIza...`) | `os.environ["GOOGLE_API_KEY"]` |

**Note:** `--fix` modifies files directly. Always run `git diff` after to review changes before committing.

---

## Ignore Files with `.sentinelignore`

Create a `.sentinelignore` file in your project root to skip files or folders from scanning:

```
# .sentinelignore
tests/
*.example.py
config.sample.js
docs/
```

**Rules:**
- Lines starting with `#` are comments
- Folder paths skip the entire folder recursively
- File patterns support `*` wildcards
- Works on both manual scans and pre-commit hook scans

**Example — skip test files and sample configs:**
```
tests/
*.sample.*
*.example.*
fixtures/
```

---

## Git Hook — Automatic Protection

### Install globally (protects every repo on your machine)
```bash
sentinel --install-global
```

### Install into a specific repo only
```bash
python install_hook.py --path C:/path/to/your/repo
```

### How it works
Once installed, every `git commit` is intercepted BEFORE the commit is saved:

```
git commit -m "my changes"
      │
      ▼
SentinelCodeAI scans all staged files
      │
      ├── HIGH risk found  →  commit BLOCKED + report shown
      └── All clean        →  commit proceeds normally
```

Secrets never enter git history because the hook runs before git saves anything.

### Uninstall global hook
```bash
git config --global --unset core.hooksPath
```

---

## Running Tests

```bash
pytest tests/
```

---

## Supported File Types

All text-based files are scanned. The following are skipped:

`.png .jpg .jpeg .gif .svg .ico .pdf .zip .tar .gz .exe .bin .pyc .pyo .so .dll .class`

### C/C++ files get extra AST analysis

Files with extensions `.c .cpp .cc .cxx .h .hpp` are additionally processed by the AST engine (`cpp_ast.py`) which performs structural analysis beyond regex matching.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Scan clean, no HIGH risk |
| 1    | HIGH risk found (commit blocked) |
