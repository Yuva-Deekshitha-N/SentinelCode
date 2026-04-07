import pytest
from src.core.leaks import detect_leaks


def test_detects_unclosed_file():
    code = 'f = open("data.txt", "r")\ndata = f.read()'
    findings = detect_leaks(code)
    assert any(f["type"] == "python_unclosed_file" for f in findings)


def test_no_leak_with_context_manager():
    code = 'with open("data.txt") as f:\n    data = f.read()'
    findings = detect_leaks(code)
    assert findings == []


def test_syntax_error_handled():
    # detect_leaks is regex-based and does not raise on syntax errors
    code = "def broken(:"
    findings = detect_leaks(code)
    assert isinstance(findings, list)
