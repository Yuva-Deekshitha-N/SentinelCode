import re

# Regex-based leak patterns — works across Python, C++, Java, JS, etc.
LEAK_PATTERNS = {
    # Python
    "python_unclosed_file": {
        "pattern": r"\bopen\s*\([^)]+\)(?!\s*as\b)",
        "explanation": "open() called without a 'with' block. File handle may never be closed, leaking OS resources.",
        "languages": "Python",
    },
    "python_unclosed_db": {
        "pattern": r"\b(psycopg2|pymysql|sqlite3|cx_Oracle|pyodbc)\.connect\s*\(",
        "explanation": "Database connection opened. If not closed or used in a context manager, the connection leaks and exhausts the DB connection pool.",
        "languages": "Python",
    },
    "python_unclosed_socket": {
        "pattern": r"\bsocket\.socket\s*\(",
        "explanation": "Socket created without a 'with' block. Unclosed sockets leak file descriptors and can cause connection exhaustion.",
        "languages": "Python",
    },
    "python_unclosed_session": {
        "pattern": r"\brequests\.Session\s*\(\s*\)(?!\s*as\b)",
        "explanation": "requests.Session() opened without a context manager. Unclosed sessions leak TCP connections.",
        "languages": "Python",
    },

    # C / C++
    "cpp_malloc_no_free": {
        "pattern": r"\bmalloc\s*\(",
        "explanation": "malloc() allocates heap memory. If free() is never called, this causes a memory leak that grows over time.",
        "languages": "C/C++",
    },
    "cpp_new_no_delete": {
        "pattern": r"\bnew\s+\w+",
        "explanation": "'new' allocates heap memory. Without a matching 'delete', the memory is never returned to the OS.",
        "languages": "C/C++",
    },
    "cpp_fopen_no_fclose": {
        "pattern": r"\bfopen\s*\(",
        "explanation": "fopen() opens a file handle. If fclose() is never called, the file descriptor leaks.",
        "languages": "C/C++",
    },

    # Java
    "java_unclosed_stream": {
        "pattern": r"\bnew\s+(FileInputStream|FileOutputStream|BufferedReader|FileReader|FileWriter)\s*\(",
        "explanation": "Java stream opened without try-with-resources. If close() is not called, the stream leaks file descriptors.",
        "languages": "Java",
    },
    "java_unclosed_connection": {
        "pattern": r"\bDriverManager\.getConnection\s*\(",
        "explanation": "JDBC connection opened. If not closed in a finally block or try-with-resources, the DB connection leaks.",
        "languages": "Java",
    },

    # JavaScript / TypeScript
    "js_unclosed_fs": {
        "pattern": r"\bfs\.open\s*\(",
        "explanation": "fs.open() called without a corresponding fs.close(). Leaks file descriptors in Node.js.",
        "languages": "JavaScript/TypeScript",
    },
    "js_event_listener": {
        "pattern": r"\baddEventListener\s*\(",
        "explanation": "Event listener added. If removeEventListener() is never called, it prevents garbage collection and causes memory leaks.",
        "languages": "JavaScript/TypeScript",
    },
}


def detect_leaks(code: str) -> list[dict]:
    findings = []
    for line_num, line in enumerate(code.splitlines(), start=1):
        for leak_type, config in LEAK_PATTERNS.items():
            if re.search(config["pattern"], line):
                findings.append({
                    "type": leak_type,
                    "line": line_num,
                    "content": line.strip(),
                    "explanation": config["explanation"],
                    "languages": config["languages"],
                })
    return findings
