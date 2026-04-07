# SentinelCodeAI — Usage Guide

## Installation

### Option A — pip install (recommended)
```bash
pip install -e .
```

### Option B — without pip install
```bash
pip install -r requirements.txt
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
Once installed, every `git commit` is intercepted:

```
git commit -m "my changes"
      │
      ▼
SentinelCodeAI scans all staged files
      │
      ├── HIGH risk found  →  commit BLOCKED + report shown
      └── All clean        →  commit proceeds normally
```

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
