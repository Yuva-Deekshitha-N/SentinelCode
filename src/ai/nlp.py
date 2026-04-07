import re

SENSITIVE_KEYWORDS = {
    "password":    "A variable named 'password' likely holds a plaintext credential. Plaintext passwords in code are a critical security risk.",
    "secret":      "A variable named 'secret' may contain a cryptographic secret or API secret that should never be hardcoded.",
    "token":       "A variable named 'token' may expose an authentication or API token that grants access to a service.",
    "private":     "A variable named 'private' may reference a private key or sensitive private data.",
    "credential":  "A variable named 'credential' likely holds authentication data such as a username/password pair or certificate.",
    "api_key":     "A variable named 'api_key' almost certainly contains a service API key that should be stored in environment variables.",
    "auth":        "A variable named 'auth' may hold authentication headers, tokens, or credentials used to access protected resources.",
    "access_key":  "A variable named 'access_key' likely contains a cloud or service access key that grants programmatic access.",
    "passphrase":  "A variable named 'passphrase' contains a passphrase used to protect a private key or encrypted data.",
}


def analyze_context(code: str) -> list[dict]:
    findings = []
    for line_num, line in enumerate(code.splitlines(), start=1):
        for keyword, explanation in SENSITIVE_KEYWORDS.items():
            if re.search(rf"\b{keyword}\b", line, re.IGNORECASE):
                findings.append({
                    "line": line_num,
                    "keyword": keyword,
                    "content": line.strip(),
                    "risk": "MEDIUM",
                    "explanation": explanation,
                })
    return findings
