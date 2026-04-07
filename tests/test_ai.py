import pytest
from src.ai.nlp import analyze_context


def test_detects_sensitive_keyword():
    # 'token' appears as a standalone word on this line
    code = 'token = get_token()'
    findings = analyze_context(code)
    assert any(f["keyword"] == "token" for f in findings)


def test_case_insensitive():
    code = 'PASSWORD = os.environ["DB_PASS"]'
    findings = analyze_context(code)
    assert any(f["keyword"] == "password" for f in findings)


def test_no_findings_on_clean_code():
    code = 'def add(a, b):\n    return a + b'
    assert analyze_context(code) == []


def test_returns_line_number():
    code = 'x = 1\nsecret = "abc"'
    findings = analyze_context(code)
    assert findings[0]["line"] == 2
