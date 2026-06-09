"""Tests for the scale gate script."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestSyntheticCorpus:
    """Test synthetic corpus generation."""

    def test_generate_corpus(self, tmp_path):
        from generate_synthetic_corpus import generate_repo

        repo_dir = tmp_path / "repo_001"
        generate_repo(repo_dir, 1)

        assert (repo_dir / "README.md").exists()
        assert (repo_dir / "LICENSE").exists()
        assert (repo_dir / "requirements.txt").exists()
        assert (repo_dir / "main.py").exists()
        assert (repo_dir / "src" / "model.py").exists()
        assert (repo_dir / "scripts" / "train.py").exists()
        assert (repo_dir / "results" / "metrics.json").exists()

    def test_generate_corpus_deterministic(self, tmp_path):
        from generate_synthetic_corpus import generate_repo

        dir1 = tmp_path / "repo1"
        dir2 = tmp_path / "repo2"
        generate_repo(dir1, 5)
        generate_repo(dir2, 5)

        # Same index should produce same content
        assert (dir1 / "README.md").read_text(encoding="utf-8") == \
               (dir2 / "README.md").read_text(encoding="utf-8")


class TestScaleGate:
    """Test scale gate functionality."""

    def _generate_corpus(self, tmp_path, count=3):
        """Generate a small corpus for testing."""
        from generate_synthetic_corpus import generate_repo
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        for i in range(1, count + 1):
            generate_repo(corpus / f"repo_{i:03d}", i)
        return corpus

    def test_scale_gate_mini(self, tmp_path):
        """Run scale gate on a tiny corpus."""
        from scale_gate import run_scale_gate

        corpus = self._generate_corpus(tmp_path, 3)
        result = run_scale_gate(corpus, repo_count=3)

        assert result["repo_count"] == 3
        assert result["semantic_match"] is True
        assert result["pass"] is True
        assert result["jobs_1_runtime"] > 0
        assert result["jobs_2_runtime"] > 0

    def test_scale_gate_format_markdown(self, tmp_path):
        from scale_gate import format_markdown, run_scale_gate

        corpus = self._generate_corpus(tmp_path, 2)
        result = run_scale_gate(corpus, repo_count=2)
        md = format_markdown(result)

        assert "Scale Gate Report" in md
        assert "Semantic match" in md

    def test_scale_gate_json_serializable(self, tmp_path):
        from scale_gate import run_scale_gate

        corpus = self._generate_corpus(tmp_path, 1)
        result = run_scale_gate(corpus, repo_count=1)
        text = json.dumps(result)
        parsed = json.loads(text)
        assert parsed["pass"] is True
