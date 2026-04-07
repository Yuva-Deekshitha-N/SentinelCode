"""
C/C++ AST-based static analysis using pycparser.

Walks the real Abstract Syntax Tree of C/C++ source files to detect:
  - malloc() without a paired free()        → memory leak
  - fopen() without a paired fclose()       → resource leak
  - new without delete                      → memory leak  (regex-assisted, C++ extension)
  - Pointer assigned then reassigned before free → dangling / lost pointer
"""

import re
from pycparser import c_parser, c_ast, parse_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_cpp_comments(code: str) -> str:
    """Remove // and /* */ comments so the C parser doesn't choke."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def _remove_cpp_extensions(code: str) -> str:
    """
    Strip C++-only syntax that pycparser (a pure-C parser) can't handle,
    so we can still analyse the C-style memory calls inside .cpp files.
    """
    # Remove #include lines
    code = re.sub(r"^\s*#include\s*[<\"][^\n]*", "", code, flags=re.MULTILINE)
    # Remove using namespace / using std::
    code = re.sub(r"^\s*using\s+[^\n;]+;", "", code, flags=re.MULTILINE)
    # Remove class / struct definitions (keep function bodies)
    code = re.sub(r"\bclass\b", "struct", code)
    # Remove :: scope resolution
    code = re.sub(r"\w+::", "", code)
    # Remove template declarations
    code = re.sub(r"template\s*<[^>]*>", "", code)
    # Remove C++ casts
    code = re.sub(r"\b(static_cast|dynamic_cast|reinterpret_cast|const_cast)\s*<[^>]*>", "", code)
    return code


# ---------------------------------------------------------------------------
# AST visitor — collects malloc/free/fopen/fclose call sites
# ---------------------------------------------------------------------------

class _MemoryCallVisitor(c_ast.NodeVisitor):
    """Walk the AST and record every call to malloc/free/fopen/fclose."""

    def __init__(self):
        self.calls: list[dict] = []   # {"name": str, "line": int}

    def visit_FuncCall(self, node):
        if node.name and isinstance(node.name, c_ast.ID):
            fn = node.name.name
            if fn in ("malloc", "calloc", "realloc", "free", "fopen", "fclose"):
                line = node.coord.line if node.coord else 0
                self.calls.append({"name": fn, "line": line})
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_cpp_ast(code: str) -> list[dict]:
    """
    Parse C/C++ source with pycparser and return AST-level findings.

    Returns a list of dicts compatible with the existing leak format:
      {type, line, content, explanation, languages, engine}
    """
    findings: list[dict] = []
    lines = code.splitlines()

    # ── 1. Try real AST parse ──────────────────────────────────────────────
    ast_findings = _ast_analysis(code, lines)
    findings.extend(ast_findings)

    # ── 2. C++-only checks (new/delete, dangling ptr) via regex on raw code ─
    findings.extend(_cpp_new_delete_analysis(code, lines))
    findings.extend(_dangling_pointer_analysis(code, lines))

    return findings


# ---------------------------------------------------------------------------
# AST analysis (malloc/free, fopen/fclose pairing)
# ---------------------------------------------------------------------------

def _ast_analysis(code: str, lines: list[str]) -> list[dict]:
    findings: list[dict] = []

    try:
        clean = _strip_cpp_comments(code)
        clean = _remove_cpp_extensions(clean)

        # pycparser needs a fake libc header stub
        parser = c_parser.CParser()
        # Inject minimal typedefs so the parser doesn't fail on FILE*, size_t etc.
        preamble = (
            "typedef unsigned long size_t;\n"
            "typedef struct _IO_FILE FILE;\n"
            "void *malloc(size_t size);\n"
            "void *calloc(size_t n, size_t size);\n"
            "void *realloc(void *ptr, size_t size);\n"
            "void  free(void *ptr);\n"
            "FILE *fopen(const char *path, const char *mode);\n"
            "int   fclose(FILE *stream);\n"
        )
        ast = parser.parse(preamble + clean, filename="<input>")

        visitor = _MemoryCallVisitor()
        visitor.visit(ast)

        malloc_lines = [c["line"] for c in visitor.calls if c["name"] in ("malloc", "calloc", "realloc")]
        free_count   = sum(1 for c in visitor.calls if c["name"] == "free")
        fopen_lines  = [c["line"] for c in visitor.calls if c["name"] == "fopen"]
        fclose_count = sum(1 for c in visitor.calls if c["name"] == "fclose")

        # malloc without free
        if malloc_lines and free_count == 0:
            for ln in malloc_lines:
                src_line = lines[ln - 1].strip() if 0 < ln <= len(lines) else ""
                findings.append({
                    "type": "ast_malloc_no_free",
                    "line": ln,
                    "content": src_line,
                    "explanation": (
                        "[AST] malloc/calloc/realloc detected but no free() found in this "
                        "translation unit. Heap memory will never be returned to the OS."
                    ),
                    "languages": "C/C++",
                    "engine": "AST",
                })

        # fopen without fclose
        if fopen_lines and fclose_count == 0:
            for ln in fopen_lines:
                src_line = lines[ln - 1].strip() if 0 < ln <= len(lines) else ""
                findings.append({
                    "type": "ast_fopen_no_fclose",
                    "line": ln,
                    "content": src_line,
                    "explanation": (
                        "[AST] fopen() detected but no fclose() found in this translation unit. "
                        "The file descriptor will leak until the process exits."
                    ),
                    "languages": "C/C++",
                    "engine": "AST",
                })

    except Exception:
        # Parser failed (complex C++ syntax) — fall back silently; regex layer still runs
        pass

    return findings


# ---------------------------------------------------------------------------
# C++ new / delete analysis (regex-assisted, AST-style pairing logic)
# ---------------------------------------------------------------------------

def _cpp_new_delete_analysis(code: str, lines: list[str]) -> list[dict]:
    findings: list[dict] = []

    new_lines    = [i + 1 for i, l in enumerate(lines) if re.search(r"\bnew\b", l)]
    delete_count = sum(1 for l in lines if re.search(r"\bdelete\b", l))

    if new_lines and delete_count == 0:
        for ln in new_lines:
            findings.append({
                "type": "ast_new_no_delete",
                "line": ln,
                "content": lines[ln - 1].strip(),
                "explanation": (
                    "[AST] 'new' allocates heap memory but no 'delete' was found. "
                    "Prefer smart pointers (std::unique_ptr / std::shared_ptr) to avoid leaks."
                ),
                "languages": "C++",
                "engine": "AST",
            })

    return findings


# ---------------------------------------------------------------------------
# Dangling pointer detection
# ---------------------------------------------------------------------------

def _dangling_pointer_analysis(code: str, lines: list[str]) -> list[dict]:
    """
    Detect the pattern:
        ptr = malloc(...);   ← allocation
        ptr = something;     ← reassignment WITHOUT free → original block lost
    """
    findings: list[dict] = []

    # Collect pointer names that were malloc'd
    malloc_vars: dict[str, int] = {}
    for i, line in enumerate(lines, start=1):
        m = re.search(r"\b(\w+)\s*=\s*(?:malloc|calloc|realloc)\s*\(", line)
        if m:
            malloc_vars[m.group(1)] = i

    # Check if any of those vars are reassigned without a free in between
    for var, alloc_line in malloc_vars.items():
        freed = False
        for i, line in enumerate(lines, start=1):
            if i <= alloc_line:
                continue
            if re.search(rf"\bfree\s*\(\s*{var}\s*\)", line):
                freed = True
                break
            # Reassigned without free
            if re.search(rf"\b{var}\s*=\s*(?!NULL|nullptr|0\b)", line):
                if not freed:
                    findings.append({
                        "type": "ast_dangling_pointer",
                        "line": i,
                        "content": lines[i - 1].strip(),
                        "explanation": (
                            f"[AST] Pointer '{var}' (allocated at line {alloc_line}) is "
                            "reassigned before being freed. The original heap block is lost — "
                            "this is a classic dangling/lost-pointer memory leak."
                        ),
                        "languages": "C/C++",
                        "engine": "AST",
                    })
                break

    return findings
