import pytest
from src.core.secrets import detect_secrets


def test_detects_aws_access_key():
    code = 'key = "AKIAIOSFODNN7EXAMPLE"'
    findings = detect_secrets(code)
    assert any(f["type"] == "aws_access_key" for f in findings)


def test_detects_password():
    code = 'password = "supersecret123"'
    findings = detect_secrets(code)
    assert any(f["type"] == "password" for f in findings)


def test_no_false_positive():
    code = 'x = 42\nprint("hello world")'
    assert detect_secrets(code) == []


def test_returns_correct_line_number():
    code = "x = 1\npassword = 'mypassword'"
    findings = detect_secrets(code)
    assert findings[0]["line"] == 2
