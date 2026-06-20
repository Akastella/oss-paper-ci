"""Tests for security documentation truthfulness."""

from __future__ import annotations

from pathlib import Path


def test_security_md_exists() -> None:
    """SECURITY.md exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "SECURITY.md").exists()


def test_security_md_no_certified_secure() -> None:
    """SECURITY.md does not claim 'certified secure'."""
    repo_root = Path(__file__).parent.parent
    content = (repo_root / "SECURITY.md").read_text(encoding="utf-8").lower()
    assert "certified secure" not in content
    assert "completely secure" not in content
    assert "100% secure" not in content


def test_security_md_no_slsa_claim() -> None:
    """SECURITY.md does not claim SLSA compliance."""
    repo_root = Path(__file__).parent.parent
    content = (repo_root / "SECURITY.md").read_text(encoding="utf-8").lower()
    # Should mention SLSA only in "not" context
    if "slsa" in content:
        # Should be in a "not" or "no" context
        lines = [l for l in content.splitlines() if "slsa" in l]
        for line in lines:
            assert any(neg in line for neg in ["not", "no ", "don't", "doesn't", "do not", "isn't"]), \
                f"SLSA mention without negation: {line}"


def test_security_md_no_sigstore_claim() -> None:
    """SECURITY.md does not claim Sigstore integration."""
    repo_root = Path(__file__).parent.parent
    content = (repo_root / "SECURITY.md").read_text(encoding="utf-8").lower()
    if "sigstore" in content:
        lines = [l for l in content.splitlines() if "sigstore" in l]
        for line in lines:
            assert any(neg in line for neg in ["not", "no ", "don't", "doesn't", "do not"]), \
                f"Sigstore mention without negation: {line}"


def test_readme_no_certified_secure() -> None:
    """README.md does not claim 'certified secure'."""
    repo_root = Path(__file__).parent.parent
    content = (repo_root / "README.md").read_text(encoding="utf-8").lower()
    assert "certified secure" not in content
    # "security certification" is allowed when in negative context
    if "security certification" in content:
        lines = [l for l in content.splitlines() if "security certification" in l]
        for line in lines:
            assert any(neg in line for neg in ["not", "no ", "aren't", "is not", "are not"]), \
                f"Security certification mention without negation: {line}"


def test_readme_zh_no_overclaiming() -> None:
    """README.zh-CN.md does not overclaim security."""
    repo_root = Path(__file__).parent.parent
    readme_zh = repo_root / "README.zh-CN.md"
    if readme_zh.exists():
        content = readme_zh.read_text(encoding="utf-8").lower()
        # Should not claim security certification
        assert "安全认证" not in content or "不是" in content or "并非" in content


def test_readme_ja_no_overclaiming() -> None:
    """README.ja.md does not overclaim security."""
    repo_root = Path(__file__).parent.parent
    readme_ja = repo_root / "README.ja.md"
    if readme_ja.exists():
        content = readme_ja.read_text(encoding="utf-8").lower()
        # Should not claim security certification
        assert "セキュリティ認証" not in content or "ではありません" in content
