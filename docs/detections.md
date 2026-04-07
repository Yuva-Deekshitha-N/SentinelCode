# SentinelCodeAI — Detection Reference

## Secret Patterns (`src/core/secrets.py`)

| Pattern Name       | Risk   | What It Detects |
|--------------------|--------|-----------------|
| `aws_access_key`   | HIGH   | AWS Access Key ID (`AKIA...`) |
| `aws_secret_key`   | HIGH   | AWS Secret Access Key (40-char base64 near "aws") |
| `generic_api_key`  | HIGH   | `api_key = "..."` assignments |
| `private_key`      | HIGH   | PEM private key headers (RSA, EC, DSA, OPENSSH) |
| `password`         | HIGH   | `password = "..."` assignments |
| `github_token`     | HIGH   | GitHub PAT (`ghp_...`) |
| `google_api_key`   | HIGH   | Google API key (`AIza...`) |
| `slack_token`      | HIGH   | Slack tokens (`xox...`) |
| `database_url`     | HIGH   | Postgres/MySQL URLs with embedded credentials |
| `mongodb_url`      | HIGH   | MongoDB connection strings with credentials |
| `firebase_api_key` | HIGH   | Firebase API key assignments |
| `firebase_db_url`  | HIGH   | Firebase Realtime Database URLs |
| `firebase_secret`  | HIGH   | Firebase legacy admin secrets |
| `jwt_token`        | MEDIUM | Hardcoded JWT tokens (`eyJ...`) |
| `test_key`         | LOW    | Test key identifiers |

---

## Resource Leak Patterns (`src/core/leaks.py`) — Regex Engine

### Python
| Pattern Name              | What It Detects |
|---------------------------|-----------------|
| `python_unclosed_file`    | `open()` without `with` block |
| `python_unclosed_db`      | DB connect (psycopg2, pymysql, sqlite3, etc.) without context manager |
| `python_unclosed_socket`  | `socket.socket()` without `with` block |
| `python_unclosed_session` | `requests.Session()` without context manager |

### C / C++
| Pattern Name         | What It Detects |
|----------------------|-----------------|
| `cpp_malloc_no_free` | `malloc()` call (regex flag) |
| `cpp_new_no_delete`  | `new` keyword (regex flag) |
| `cpp_fopen_no_fclose`| `fopen()` call (regex flag) |

### Java
| Pattern Name               | What It Detects |
|----------------------------|-----------------|
| `java_unclosed_stream`     | `new FileInputStream/FileOutputStream/BufferedReader/...` without try-with-resources |
| `java_unclosed_connection` | `DriverManager.getConnection()` without close |

### JavaScript / TypeScript
| Pattern Name          | What It Detects |
|-----------------------|-----------------|
| `js_unclosed_fs`      | `fs.open()` without `fs.close()` |
| `js_event_listener`   | `addEventListener()` without `removeEventListener()` |

---

## AST Engine Detections (`src/core/cpp_ast.py`) — C/C++ Only

The AST engine parses C/C++ source into an Abstract Syntax Tree using `pycparser` and performs structural pairing analysis — not just line-by-line regex.

| Finding Type           | Engine | What It Detects |
|------------------------|--------|-----------------|
| `ast_malloc_no_free`   | AST    | `malloc/calloc/realloc` present in AST but no `free()` node found anywhere in the translation unit |
| `ast_fopen_no_fclose`  | AST    | `fopen()` present in AST but no `fclose()` node found |
| `ast_new_no_delete`    | AST    | `new` keyword present but no `delete` found (C++ extension) |
| `ast_dangling_pointer` | AST    | Pointer variable assigned from `malloc`, then reassigned to a new value before `free()` is called — the original heap block is permanently lost |

### How AST differs from regex

| Aspect | Regex Engine | AST Engine |
|--------|-------------|------------|
| Parsing | Line-by-line text matching | Full parse tree of the entire file |
| Pairing | Cannot pair malloc↔free across lines | Counts all malloc and free nodes in the whole file |
| Dangling pointers | Cannot detect | Tracks variable names across lines |
| False positives | Higher (matches commented code) | Lower (only real code nodes) |
| Fallback | Always runs | Falls back to regex if parse fails |

---

## NLP Context Keywords (`src/ai/nlp.py`)

| Keyword      | Risk   | Why It's Flagged |
|--------------|--------|------------------|
| `password`   | MEDIUM | Likely holds a plaintext credential |
| `secret`     | MEDIUM | May contain a cryptographic or API secret |
| `token`      | MEDIUM | May expose an auth or API token |
| `private`    | MEDIUM | May reference a private key or sensitive data |
| `credential` | MEDIUM | Likely holds authentication data |
| `api_key`    | MEDIUM | Almost certainly a service API key |
| `auth`       | MEDIUM | May hold auth headers, tokens, or credentials |
| `access_key` | MEDIUM | Likely a cloud or service access key |
| `passphrase` | MEDIUM | Contains a passphrase for a private key |
