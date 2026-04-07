"""
Run this once to activate the SentinelCodeAI pre-commit hook.

Usage:
    # install into current directory's repo
    python install_hook.py

    # install into any repo on your machine
    python install_hook.py --path C:/Users/you/your-project
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def get_repo_root(path: str) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, cwd=path
    )
    if result.returncode != 0:
        print(f"ERROR: '{path}' is not inside a git repository.")
        sys.exit(1)
    return Path(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Install SentinelCodeAI pre-commit hook into a git repository."
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the git repository to protect (default: current directory).",
    )
    args = parser.parse_args()

    target = str(Path(args.path).resolve())
    repo_root = get_repo_root(target)
    hooks_dir = repo_root / ".git" / "hooks"
    hook_dest = hooks_dir / "pre-commit"
    hook_src  = Path(__file__).parent / "src" / "git_hooks" / "pre_commit_hook.sh"

    if not hooks_dir.exists():
        print(f"ERROR: .git/hooks not found in '{repo_root}'.")
        sys.exit(1)

    if not hook_src.exists():
        print(f"ERROR: Hook source not found at '{hook_src}'.")
        sys.exit(1)

    if hook_dest.exists():
        print(f"WARNING: Existing hook at '{hook_dest}' will be overwritten.")

    shutil.copy(str(hook_src), str(hook_dest))
    hook_dest.chmod(0o755)

    print(f"SentinelCodeAI: hook installed into '{repo_root}'")
    print(f"Every 'git commit' in that repo will now be scanned automatically.")


if __name__ == "__main__":
    main()
