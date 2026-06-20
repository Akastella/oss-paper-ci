"""Tests for secret scanning patterns."""

from __future__ import annotations

from pathlib import Path

from oss_paper_ci.security import scan_file, redact_secret


def test_detects_openai_key(tmp_path: Path) -> None:
    """Detects fake OpenAI API key."""
    f = tmp_path / "config.py"
    # Use a pattern that matches but is clearly not real
    f.write_text('KEY = "sk-TESTTESTTESTTESTTESTT3BlTESTFJTESTTESTTESTTESTTEST"\n', encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "openai-api-key" for fi in findings)


def test_detects_github_token(tmp_path: Path) -> None:
    """Detects fake GitHub token."""
    f = tmp_path / "env.py"
    f.write_text('TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz012345678"\n', encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "github-token" for fi in findings)


def test_detects_aws_key(tmp_path: Path) -> None:
    """Detects fake AWS access key."""
    f = tmp_path / "aws.py"
    f.write_text('ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"\n', encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "aws-access-key" for fi in findings)


def test_detects_private_key(tmp_path: Path) -> None:
    """Detects private key block."""
    f = tmp_path / "key.pem"
    f.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEow...\n-----END RSA PRIVATE KEY-----\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "private-key-block" for fi in findings)


def test_detects_curl_pipe_bash(tmp_path: Path) -> None:
    """Detects curl pipe to bash."""
    f = tmp_path / "install.sh"
    f.write_text("#!/bin/bash\ncurl https://example.com/setup.sh | bash\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "curl-pipe-bash" for fi in findings)


def test_detects_sudo(tmp_path: Path) -> None:
    """Detects sudo usage."""
    f = tmp_path / "script.sh"
    f.write_text("#!/bin/bash\nsudo apt-get install something\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "sudo-in-ci" for fi in findings)


def test_detects_chmod_777(tmp_path: Path) -> None:
    """Detects chmod 777."""
    f = tmp_path / "setup.sh"
    f.write_text("#!/bin/bash\nchmod 777 /tmp/data\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "chmod-777" for fi in findings)


def test_detects_eval_variable(tmp_path: Path) -> None:
    """Detects eval with variable."""
    f = tmp_path / "run.sh"
    f.write_text("#!/bin/bash\neval $INPUT\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "eval-variable" for fi in findings)


def test_detects_unsafe_pickle(tmp_path: Path) -> None:
    """Detects unsafe pickle.load."""
    f = tmp_path / "load.py"
    f.write_text("import pickle\ndata = pickle.load(f)\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert any(fi["id"] == "unsafe-pickle" for fi in findings)


def test_redact_secret_short() -> None:
    """Redact short secrets."""
    assert redact_secret("abc") == "***"


def test_redact_secret_long() -> None:
    """Redact long secrets showing first/last chars."""
    result = redact_secret("sk-TESTTESTTESTTESTTESTT3BlTESTFJTESTTESTTESTTESTTEST")
    assert result.startswith("sk-T")
    assert result.endswith("TEST")
    assert "..." in result


def test_no_false_positive_clean_code(tmp_path: Path) -> None:
    """Clean code produces no findings."""
    f = tmp_path / "main.py"
    f.write_text("def hello():\n    print('Hello, world!')\n", encoding="utf-8")
    findings = scan_file(f, tmp_path)
    assert len(findings) == 0
