import subprocess
import sys
from pathlib import Path
from src.scanner import run_scan
from rich.console import Console

console = Console()


# ✅ Get repo root
repo_root = Path(subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True
).stdout.strip()).resolve()


# ✅ Load .sentinelignore
def load_ignore_patterns(base: Path) -> list[str]:
    ignore_file = base / ".sentinelignore"
    if not ignore_file.exists():
        return []

    lines = ignore_file.read_text(encoding="utf-8").splitlines()

    return [
        l.strip().replace("\\", "/")
        for l in lines
        if l.strip() and not l.startswith("#")
    ]


# ✅ Correct ignore logic
def is_ignored(file: Path, base: Path, patterns: list[str]) -> bool:
    try:
        rel = file.relative_to(base).as_posix()
    except ValueError:
        return False

    for pattern in patterns:
        pattern = pattern.rstrip("/")

        # Exact file OR folder match
        if rel == pattern or rel.startswith(pattern + "/"):
            return True

    return False


# ✅ Get staged files (with ignore applied)
def get_staged_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"]
        )

        patterns = load_ignore_patterns(repo_root)

        files = []
        for f in output.decode().splitlines():
            resolved = (repo_root / f).resolve()

            if not resolved.is_file():
                continue

            # 🔥 APPLY IGNORE HERE
            if is_ignored(resolved, repo_root, patterns):
                console.print(f"[dim]SKIPPED: {resolved}[/dim]")
                continue

            files.append(resolved)

        return files

    except Exception:
        return []


# ✅ Main hook logic
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