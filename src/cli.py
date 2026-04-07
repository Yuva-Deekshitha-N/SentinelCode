import argparse
import subprocess
import sys
from pathlib import Path
from src.scanner import collect_files, run_scan
from rich.console import Console

console = Console()


def install_global_hook():
    # Global hooks folder inside SentinelCodeAI
    hooks_dir = Path(__file__).resolve().parents[2] / "global_hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_src  = Path(__file__).resolve().parent / "git_hooks" / "pre_commit_hook.sh"
    hook_dest = hooks_dir / "pre-commit"

    if not hook_src.exists():
        console.print("[red]ERROR: Hook source file not found.[/red]")
        sys.exit(1)

    import shutil
    shutil.copy(str(hook_src), str(hook_dest))
    hook_dest.chmod(0o755)

    # Tell git to use this folder for hooks in every repo
    result = subprocess.run(
        ["git", "config", "--global", "core.hooksPath", str(hooks_dir)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        console.print(f"[red]ERROR: Failed to set global hooks path: {result.stderr}[/red]")
        sys.exit(1)

    console.print("[bold green]SentinelCodeAI global hook installed successfully.[/bold green]")
    console.print(f"Hooks folder : {hooks_dir}")
    console.print("Every git commit on this machine is now protected automatically.")


def main():
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="SentinelCodeAI — scan a file or folder for secrets, leaks, and sensitive context.",
    )
    parser.add_argument(
        "--path",
        help="Path to a file or folder to scan.",
    )
    parser.add_argument(
        "--install-global",
        action="store_true",
        help="Install SentinelCodeAI as a global Git hook (runs on every repo on this machine).",
    )
    args = parser.parse_args()

    if args.install_global:
        install_global_hook()
        sys.exit(0)

    if not args.path:
        parser.print_help()
        sys.exit(1)

    files = collect_files(args.path)

    if not files:
        console.print("[yellow]No scannable files found.[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold]Scanning {len(files)} file(s) in: {args.path}[/bold]\n")

    has_high_risk = run_scan(files)

    if has_high_risk:
        console.print("\n[bold red]HIGH risk issues found. Fix them before committing.[/bold red]")
        sys.exit(1)

    console.print("\n[bold green]Scan complete. No HIGH risk issues found.[/bold green]")
    sys.exit(0)


if __name__ == "__main__":
    main()
