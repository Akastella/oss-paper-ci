"""Tests for security scan CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_security_scan_clean_repo(tmp_path: Path) -> None:
    """Security scan on clean empty dir finds no secrets."""
    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "findings" in data
    assert "files_scanned" in data


def test_security_scan_finds_fake_key(tmp_path: Path) -> None:
    """Security scan detects fake OpenAI key."""
    fake_file = tmp_path / "config.py"
    fake_file.write_text('OPENAI_KEY = "sk-TESTTESTTESTTESTTESTT3BlTESTFJTESTTESTTESTTESTTEST"\n', encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    secret_findings = [f for f in data["findings"] if f["category"] == "secret"]
    assert len(secret_findings) > 0
    # Check redaction
    for f in secret_findings:
        if f.get("redacted_preview"):
            assert "sk-" not in f["redacted_preview"] or "..." in f["redacted_preview"]


def test_security_scan_finds_private_key(tmp_path: Path) -> None:
    """Security scan detects private key block."""
    fake_file = tmp_path / "key.pem"
    fake_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEow...\n-----END RSA PRIVATE KEY-----\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    secret_findings = [f for f in data["findings"] if f["category"] == "secret"]
    assert any("private-key" in f["id"] for f in secret_findings)


def test_security_scan_finds_env_file(tmp_path: Path) -> None:
    """Security scan warns about .env files."""
    env_file = tmp_path / ".env"
    env_file.write_text("DB_PASSWORD=secret123\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    env_findings = [f for f in data["findings"] if f["id"] == "env-file-committed"]
    assert len(env_findings) > 0


def test_security_scan_finds_dangerous_curl(tmp_path: Path) -> None:
    """Security scan detects curl pipe to bash."""
    fake_file = tmp_path / "install.sh"
    fake_file.write_text("#!/bin/bash\ncurl https://example.com/install.sh | bash\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    exec_findings = [f for f in data["findings"] if f["category"] == "execution"]
    assert any("curl" in f["id"] for f in exec_findings)


def test_security_scan_markdown_format(tmp_path: Path) -> None:
    """Security scan markdown output works."""
    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "Security Scan Report" in result.stdout


def test_security_scan_output_file(tmp_path: Path) -> None:
    """Security scan can write to file."""
    output_file = tmp_path / "security-report.md"
    result = subprocess.run(
        ["oss-paper-ci", "security", "scan", str(tmp_path), "--output", str(output_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert output_file.exists()
