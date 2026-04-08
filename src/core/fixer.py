import re
from pathlib import Path
from rich.console import Console

console = Console()

# Maps secret pattern type to the env var name it should use
FIX_MAP = {
    "password":        (r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",  "{key} = os.environ[\"{ENV}\"]"),
    "generic_api_key": (r"(?i)(api_key|apikey|api-key)\s*=\s*['\"][^'\"]+['\"]", "{key} = os.environ[\"{ENV}\"]"),
    "aws_access_key":  (r"AKIA[0-9A-Z]{16}", "os.environ[\"AWS_ACCESS_KEY_ID\"]"),
    "github_token":    (r"ghp_[A-Za-z0-9]{36}", "os.environ[\"GITHUB_TOKEN\"]"),
    "google_api_key":  (r"AIza[0-9A-Za-z\-_]{35}", "os.environ[\"GOOGLE_API_KEY\"]"),
}

ENV_NAMES = {
    "password":        "DB_PASSWORD",
    "passwd":          "DB_PASSWORD",
    "pwd":             "DB_PASSWORD",
    "api_key":         "API_KEY",
    "apikey":          "API_KEY",
    "api-key":         "API_KEY",
    "aws_access_key":  "AWS_ACCESS_KEY_ID",
    "github_token":    "GITHUB_TOKEN",
    "google_api_key":  "GOOGLE_API_KEY",
}


def fix_file(file_path: Path) -> int:
    """
    Auto-fix hardcoded secrets in a file.
    Returns number of fixes applied.
    """
    code = file_path.read_text(encoding="utf-8", errors="ignore")
    original = code
    fixes = 0
    needs_os_import = False

    lines = code.splitlines()
    new_lines = []

    for line in lines:
        new_line = line

        # Fix: password/api_key = "value"  →  password = os.environ["ENV"]
        m = re.search(r"(?i)(password|passwd|pwd|api_key|apikey|api-key)\s*=\s*['\"][^'\"]+['\"]", new_line)
        if m:
            key = m.group(1)
            env = ENV_NAMES.get(key.lower(), key.upper())
            new_line = re.sub(
                r"(?i)(password|passwd|pwd|api_key|apikey|api-key)\s*=\s*['\"][^'\"]+['\"]",
                f'{key} = os.environ["{env}"]',
                new_line
            )
            needs_os_import = True
            fixes += 1

        # Fix: AWS key literal
        if re.search(r"AKIA[0-9A-Z]{16}", new_line):
            new_line = re.sub(r"AKIA[0-9A-Z]{16}", 'os.environ["AWS_ACCESS_KEY_ID"]', new_line)
            needs_os_import = True
            fixes += 1

        # Fix: GitHub token
        if re.search(r"ghp_[A-Za-z0-9]{36}", new_line):
            new_line = re.sub(r"ghp_[A-Za-z0-9]{36}", 'os.environ["GITHUB_TOKEN"]', new_line)
            needs_os_import = True
            fixes += 1

        # Fix: Google API key
        if re.search(r"AIza[0-9A-Za-z\-_]{35}", new_line):
            new_line = re.sub(r"AIza[0-9A-Za-z\-_]{35}", 'os.environ["GOOGLE_API_KEY"]', new_line)
            needs_os_import = True
            fixes += 1

        new_lines.append(new_line)

    if fixes > 0:
        fixed_code = "\n".join(new_lines)
        # Add import os at top if not already present
        if needs_os_import and "import os" not in fixed_code:
            fixed_code = "import os\n" + fixed_code
        file_path.write_text(fixed_code, encoding="utf-8")
        console.print(f"[bold green]FIXED {fixes} issue(s) in {file_path}[/bold green]")
        console.print(f"[dim]  → Replaced hardcoded secrets with os.environ references.[/dim]")
        console.print(f"[dim]  → Add the real values to a .env file and load with python-dotenv.[/dim]")

    return fixes
