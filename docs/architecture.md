# SentinelCodeAI — Architecture

## Overview

SentinelCodeAI is a local, offline security auditor that intercepts Git commits and scans staged files through three independent analysis engines before allowing the commit to proceed.

```
Developer types: git commit
        │
        ▼
┌───────────────────────┐
│   Git Pre-Commit Hook │  (pre_commit_hook.sh → pre_commit.py)
└──────────┬────────────┘
           │  staged files
           ▼
┌───────────────────────────────────────────────────┐
│                  scanner.py                       │
│  ┌─────────────────┐  ┌──────────────────────┐   │
│  │  secrets.py     │  │  leaks.py            │   │
│  │  Regex engine   │  │  Regex leak engine   │   │
│  │  15 patterns    │  │  Multi-language       │   │
│  └────────┬────────┘  └──────────┬───────────┘   │
│           │                      │                │
│  ┌────────▼────────┐  ┌──────────▼───────────┐   │
│  │  nlp.py         │  │  cpp_ast.py          │   │
│  │  Keyword NLP    │  │  AST engine (C/C++)  │   │
│  │  9 keywords     │  │  pycparser + logic   │   │
│  └────────┬────────┘  └──────────┬───────────┘   │
│           └──────────┬───────────┘                │
│                      ▼                            │
│              display_results()                    │
└──────────────────────┬────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │  HIGH risk found?       │
          │  YES → block commit     │
          │  NO  → allow commit     │
          └─────────────────────────┘
```

## Module Breakdown

### `src/core/secrets.py` — Regex Secret Detection
- Scans every line with 15 compiled regex patterns
- Covers: AWS keys, GitHub tokens, Google API keys, Slack tokens, Firebase, MongoDB, Postgres/MySQL URLs, JWT tokens, private keys, passwords
- Each pattern has a risk level (HIGH / MEDIUM / LOW) and a human-readable explanation

### `src/core/leaks.py` — Regex Resource Leak Detection
- Multi-language regex patterns for resource management issues
- Languages: Python, C/C++, Java, JavaScript/TypeScript
- Detects: unclosed files, DB connections, sockets, HTTP sessions, malloc/fopen without close

### `src/core/cpp_ast.py` — AST Static Analysis Engine (C/C++)
- Uses `pycparser` to build a real Abstract Syntax Tree from C/C++ source
- Walks the AST with a `NodeVisitor` to find `malloc`, `free`, `fopen`, `fclose` call sites
- Performs pairing logic: malloc without free → leak, fopen without fclose → leak
- Detects dangling pointers: pointer reassigned before free
- Detects C++ `new` without `delete`
- Falls back silently if the file uses complex C++ syntax the parser can't handle

### `src/ai/nlp.py` — NLP Context Analysis
- Scans for 9 sensitive variable name keywords (password, token, secret, api_key, etc.)
- Case-insensitive whole-word matching
- Flags lines as MEDIUM risk even if no actual secret value is present
- Catches cases that regex patterns miss (e.g. `my_token = get_token()`)

### `src/git_hooks/pre_commit.py` — Git Hook Logic
- Gets staged files via `git diff --cached --name-only`
- Skips SentinelCodeAI's own source files to avoid false positives
- Calls `run_scan()` and exits with code 1 (blocking the commit) if HIGH risk found

### `src/scanner.py` — Scan Orchestrator
- `collect_files()`: resolves a path to a list of scannable files
- `scan_file()`: runs all 4 engines on a single file; routes C/C++ files to AST engine
- `display_results()`: rich-formatted terminal output with colour-coded risk levels
- `run_scan()`: iterates files and aggregates HIGH risk flag

### `src/cli.py` — CLI Entry Point
- `sentinel --path <file_or_folder>`: manual scan
- `sentinel --install-global`: installs hook globally for all repos on the machine

## Data Flow

```
file content (str)
    │
    ├──► detect_secrets(code)     → List[{type, risk, line, matched, explanation}]
    ├──► detect_leaks(code)       → List[{type, line, content, explanation, languages}]
    ├──► analyze_cpp_ast(code)    → List[{type, line, content, explanation, languages, engine}]
    └──► analyze_context(code)    → List[{keyword, line, content, risk, explanation}]
```

## Risk Levels

| Level  | Colour  | Commit Action |
|--------|---------|---------------|
| HIGH   | Red     | Blocked       |
| MEDIUM | Yellow  | Warning only  |
| LOW    | Dim     | Warning only  |
| SAFE   | Green   | Allowed       |
