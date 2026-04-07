import subprocess
import sys
from pathlib import Path
from src.scanner import collect_files, run_scan
from rich.console import Console

console = Console()

repo_root = Path(subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True
).stdout.strip()).resolve()


# Files belonging to SentinelCodeAI itself — skip to avoid false positives
SENTINEL_OWN_FILES = {
    "src/core/secrets.py",
    "src/core/leaks.py",
    "src/ai/nlp.py",
    "src/scanner.py",
    "src/cli.py",
    "src/git_hooks/pre_commit.py",
    "README.md",
    "tests/test_secrets.py",
    "tests/test_leaks.py",
    "tests/test_ai.py",
}


def get_staged_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"]
        )
        files = []
        for f in output.decode().splitlines():
            if f in SENTINEL_OWN_FILES:
                continue
            resolved = (repo_root / f).resolve()
            if str(resolved).startswith(str(repo_root)) and resolved.is_file():
                files.append(resolved)
        return files
    except Exception:
        return []


def main():
    files = get_staged_files()

    if not files:
        sys.exit(0)

    console.print(f"[bold]SentinelCodeAI scanning {len(files)} staged file(s)...[/bold]\n")

    has_high_risk = run_scan(files)

    if has_high_risk:
        console.print("\nCommit BLOCKED due to HIGH risk issues!", style="bold red")
        sys.exit(1)

    console.print("\nCommit Allowed", style="bold green")
    sys.exit(0)


if __name__ == "__main__":
    main()
