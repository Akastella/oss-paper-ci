"""Tests for eval CLI commands."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


CORPUS_DIR = Path(__file__).parent.parent / "examples" / "evaluation-corpus"


class TestEvalCLI:
    """Test eval command group."""

    def test_eval_run_json(self, tmp_path):
        """Test eval run with JSON output."""
        output_file = tmp_path / "result.json"
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "eval", "run",
             str(CORPUS_DIR), "--format", "json", "--output", str(output_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_file.exists()

        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert "version" in data
        assert "total_repos" in data
        assert "repos" in data
        assert "summary" in data
        assert data["total_repos"] > 0

    def test_eval_run_markdown(self, tmp_path):
        """Test eval run with Markdown output."""
        output_file = tmp_path / "result.md"
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "eval", "run",
             str(CORPUS_DIR), "--format", "markdown", "--output", str(output_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert "Evaluation Summary" in content
        assert "Repository Results" in content

    def test_eval_run_html(self, tmp_path):
        """Test eval run with HTML output (no external CDN)."""
        output_file = tmp_path / "result.html"
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "eval", "run",
             str(CORPUS_DIR), "--format", "html", "--output", str(output_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        # Check no external CDN
        assert "cdn." not in content.lower()
        assert "https://cdnjs" not in content
        assert "https://unpkg" not in content

    def test_eval_compare(self, tmp_path):
        """Test eval compare against baseline."""
        # First generate a result
        result_file = tmp_path / "result.json"
        subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "eval", "run",
             str(CORPUS_DIR), "--format", "json", "--output", str(result_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )

        # Compare against golden
        golden_file = Path(__file__).parent / "golden" / "evaluation_summary.json"
        if golden_file.exists():
            result = subprocess.run(
                [sys.executable, "-m", "oss_paper_ci", "eval", "compare",
                 "--baseline", str(golden_file), "--current", str(result_file)],
                capture_output=True, text=True, timeout=60,
                encoding="utf-8", errors="replace",
            )
            # Should not error
            assert result.returncode == 0 or "differ" in result.stdout.lower()


class TestEvalJSON:
    """Test eval JSON output structure."""

    @pytest.fixture
    def eval_result(self, tmp_path):
        """Run eval and return parsed JSON."""
        output_file = tmp_path / "result.json"
        subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "eval", "run",
             str(CORPUS_DIR), "--format", "json", "--output", str(output_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        return json.loads(output_file.read_text(encoding="utf-8"))

    def test_has_version(self, eval_result):
        assert "version" in eval_result
        assert eval_result["version"] == "3.5.0rc1"

    def test_has_summary(self, eval_result):
        summary = eval_result["summary"]
        assert "pass" in summary
        assert "partial" in summary
        assert "fail" in summary
        assert "evaluated" in summary

    def test_repos_have_ecosystems(self, eval_result):
        for repo in eval_result["repos"]:
            assert "ecosystems" in repo
            assert isinstance(repo["ecosystems"], list)

    def test_no_absolute_paths(self, eval_result):
        """Ensure no absolute paths in output."""
        json_str = json.dumps(eval_result)
        # Check for common absolute path patterns
        assert "C:\\" not in json_str
        assert "/home/" not in json_str
        assert "/Users/" not in json_str
