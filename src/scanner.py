import sys
from pathlib import Path
from src.core.secrets import detect_secrets, summarize_findings
from src.core.leaks import detect_leaks
from src.core.cpp_ast import analyze_cpp_ast
from src.ai.nlp import analyze_context
from rich.console import Console

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

console = Console()

# File types to skip (binaries, media, etc.)
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".bin",
    ".pyc", ".pyo", ".so", ".dll", ".class",
}


def collect_files(path: str) -> list[Path]:
    """Return all scannable files from a file path or folder."""
    target = Path(path).resolve()
    if target.is_file():
        return [target]
    return [
        f for f in target.rglob("*")
        if f.is_file() and f.suffix not in SKIP_EXTENSIONS
    ]


CPP_EXTENSIONS = {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}


def scan_file(file_path: Path) -> tuple:
    try:
        code = file_path.read_text(encoding="utf-8", errors="ignore")
        findings = detect_secrets(code)
        summary = summarize_findings(findings)
        leaks = detect_leaks(code)
        # Run AST engine for C/C++ files
        if file_path.suffix.lower() in CPP_EXTENSIONS:
            leaks = leaks + analyze_cpp_ast(code)
        nlp_findings = analyze_context(code)
        return findings, summary, leaks, nlp_findings
    except Exception:
        return [], {"HIGH": 0, "MEDIUM": 0, "LOW": 0}, [], []


def display_results(file: str, findings, summary, leaks, nlp_findings) -> bool:
    """Print findings for one file. Returns True if HIGH risk was found."""
    has_high = False

    # 🔴 HIGH
    if summary["HIGH"] > 0:
        has_high = True
        console.print(f"[bold red]>> HIGH RISK in {file}[/bold red]")
        for f in findings:
            if f["risk"] == "HIGH":
                console.print(f"[red]  {f['type']} (line {f['line']})[/red]")
                console.print(f"   Detected : {f['matched']}")
                console.print(f"   Why      : {f['explanation']}")

    # MEDIUM
    if summary["MEDIUM"] > 0:
        console.print(f"[bold yellow]>> MEDIUM RISK in {file}[/bold yellow]")
        for f in findings:
            if f["risk"] == "MEDIUM":
                console.print(f"[yellow]  {f['type']} (line {f['line']})[/yellow]")
                console.print(f"   Detected : {f['matched']}")
                console.print(f"   Why      : {f['explanation']}")

    # LOW
    if summary["LOW"] > 0:
        console.print(f"[dim yellow]>> LOW RISK in {file}[/dim yellow]")
        for f in findings:
            if f["risk"] == "LOW":
                console.print(f"[yellow]  {f['type']} (line {f['line']})[/yellow]")
                console.print(f"   Detected : {f['matched']}")
                console.print(f"   Why      : {f['explanation']}")

    # Leaks
    if leaks:
        console.print(f"[yellow]>> Leak Issues in {file}[/yellow]")
        for leak in leaks:
            engine_tag = f" [{leak.get('engine', 'regex')}]" if leak.get('engine') else ""
            console.print(f"[yellow]  {leak['type']}{engine_tag} (line {leak['line']}) [{leak['languages']}][/yellow]")
            console.print(f"   Code     : {leak['content']}")
            console.print(f"   Why      : {leak['explanation']}")

    # NLP
    if nlp_findings:
        console.print(f"[bold cyan]>> NLP Findings in {file}[/bold cyan]")
        for n in nlp_findings:
            console.print(f"[cyan]  '{n['keyword']}' (line {n['line']}) - {n['risk']}[/cyan]")
            console.print(f"   Code     : {n['content']}")
            console.print(f"   Why      : {n['explanation']}")

    # ✅ SAFE
    if (
        summary["HIGH"] == 0
        and summary["MEDIUM"] == 0
        and summary["LOW"] == 0
        and not leaks
        and not nlp_findings
    ):
        console.print(f"[bold green]SAFE: {file}[/bold green]")

    return has_high


def run_scan(files: list[Path]) -> bool:
    """Scan a list of files. Returns True if any HIGH risk found."""
    has_high_risk = False
    for file_path in files:
        findings, summary, leaks, nlp_findings = scan_file(file_path)
        if display_results(str(file_path), findings, summary, leaks, nlp_findings):
            has_high_risk = True
    return has_high_risk
