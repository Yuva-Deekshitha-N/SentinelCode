import re
from typing import List, Dict

#  Secret patterns with risk levels and explanations
SECRET_PATTERNS = {
    "aws_access_key": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "risk": "HIGH",
        "explanation": "Hardcoded AWS Access Key ID detected. Attackers can use this to access your AWS account, spin up resources, steal data, or incur massive charges."
    },
    "aws_secret_key": {
        "pattern": r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]",
        "risk": "HIGH",
        "explanation": "Hardcoded AWS Secret Access Key detected. Combined with an Access Key ID, this grants full programmatic access to your AWS account."
    },
    "generic_api_key": {
        "pattern": r"(?i)(api_key|apikey|api-key)\s*=\s*['\"][a-zA-Z0-9]{16,}['\"]",
        "risk": "HIGH",
        "explanation": "A hardcoded API key was found. If this key is pushed to a public repo, any third party can authenticate as you and abuse the associated service."
    },
    "private_key": {
        "pattern": r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
        "risk": "HIGH",
        "explanation": "A private cryptographic key is embedded in the code. This can be used to impersonate your server, decrypt communications, or forge signatures."
    },
    "password": {
        "pattern": r"(?i)(password|passwd|pwd)\s*=\s*['\"].{6,}['\"]",
        "risk": "HIGH",
        "explanation": "A plaintext password is hardcoded. Passwords in source code are permanently stored in Git history even after deletion and can be extracted by anyone with repo access."
    },
    "github_token": {
        "pattern": r"ghp_[A-Za-z0-9]{36}",
        "risk": "HIGH",
        "explanation": "A GitHub Personal Access Token was found. This grants the holder read/write access to your repositories and account settings."
    },
    "jwt_token": {
        "pattern": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "risk": "MEDIUM",
        "explanation": "A JWT token is hardcoded. If unexpired, it can be replayed to authenticate as the token's subject without needing credentials."
    },
    "google_api_key": {
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "risk": "HIGH",
        "explanation": "A Google API key was found. Exposure can lead to quota theft, unauthorized use of Google services, and unexpected billing on your account."
    },
    "slack_token": {
        "pattern": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        "risk": "HIGH",
        "explanation": "A Slack token is hardcoded. This allows an attacker to read messages, post as your bot/user, and access private channels in your workspace."
    },
    "database_url": {
        "pattern": r"(postgres|mysql)://.*:.*@",
        "risk": "HIGH",
        "explanation": "A database connection URL with embedded credentials was found. This exposes your database host, username, and password to anyone who reads the code."
    },
    "mongodb_url": {
        "pattern": r"mongodb(\+srv)?://[^:]+:[^@]+@",
        "risk": "HIGH",
        "explanation": "A MongoDB connection string with embedded credentials was found. Exposes your database host, username, and password publicly."
    },
    "firebase_api_key": {
        "pattern": r"(?i)firebase.*api.?key\s*[=:]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
        "risk": "HIGH",
        "explanation": "A Firebase API key was found. Exposes your Firebase project to unauthorized reads, writes, and abuse of Firebase services."
    },
    "firebase_db_url": {
        "pattern": r"https://[a-z0-9-]+\.firebaseio\.com",
        "risk": "HIGH",
        "explanation": "A Firebase Realtime Database URL was found. If database rules are misconfigured, attackers can read or write all data."
    },
    "firebase_secret": {
        "pattern": r"(?i)firebase.{0,20}secret\s*[=:]\s*['\"][A-Za-z0-9]{20,}['\"]",
        "risk": "HIGH",
        "explanation": "A Firebase legacy secret was found. This grants full admin access to your Firebase project."
    },
    "test_key": {
        "pattern": r"(?i)test[_-]?key",
        "risk": "LOW",
        "explanation": "A test key identifier was found. While likely not a real secret, test keys are sometimes accidentally swapped with production keys."
    }
}


def detect_secrets(code: str) -> List[Dict]:
    """
    Scan code and detect potential secrets.

    Returns:
        List of findings with:
        - type
        - risk
        - line number
        - matched content
    """
    findings = []

    for line_num, line in enumerate(code.splitlines(), start=1):
        for secret_type, config in SECRET_PATTERNS.items():
            pattern = config["pattern"]
            risk = config["risk"]

            matches = re.findall(pattern, line)

            for match in matches:
                findings.append({
                    "type": secret_type,
                    "risk": risk,
                    "line": line_num,
                    "content": line.strip(),
                    "matched": match if isinstance(match, str) else match[0],
                    "explanation": config["explanation"],
                })

    return findings


def summarize_findings(findings: List[Dict]) -> Dict:
    """
    Summarize findings into risk categories
    """
    summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for f in findings:
        summary[f["risk"]] += 1

    return summary