"""Tests for configuration loading."""

import pytest
from pathlib import Path

from oss_paper_ci.config import Config, load_config, generate_default_config, _parse_config_file


class TestLoadConfig:
    def test_default_config(self, tmp_path):
        # Use tmp_path to avoid picking up project's own config
        config = load_config(repo_root=tmp_path)
        assert config.version == "0.1"
        assert config.checks.min_score == 70
        assert config.checks.require_license is True

    def test_load_from_file(self, tmp_path):
        cfg = tmp_path / "oss-paper-ci.yml"
        cfg.write_text("""\
version: 0.1
checks:
  min_score: 80
  require_license: false
""")
        config = load_config(config_path=cfg)
        assert config.checks.min_score == 80
        assert config.checks.require_license is False

    def test_load_nonexistent_file(self):
        config = load_config(config_path="/nonexistent/file.yml")
        assert config.checks.min_score == 70  # defaults

    def test_load_invalid_yaml(self, tmp_path):
        cfg = tmp_path / "bad.yml"
        cfg.write_text("{{{{invalid yaml")
        config = load_config(config_path=cfg)
        assert config.checks.min_score == 70  # defaults

    def test_load_empty_file(self, tmp_path):
        cfg = tmp_path / "empty.yml"
        cfg.write_text("")
        config = load_config(config_path=cfg)
        assert config.checks.min_score == 70  # defaults

    def test_search_repo_root(self, tmp_path):
        cfg = tmp_path / "oss-paper-ci.yml"
        cfg.write_text("checks:\n  min_score: 90")
        config = load_config(repo_root=tmp_path)
        assert config.checks.min_score == 90

    def test_partial_config(self, tmp_path):
        cfg = tmp_path / "oss-paper-ci.yml"
        cfg.write_text("""\
project:
  name: "my-paper"
""")
        config = load_config(config_path=cfg)
        assert config.project.name == "my-paper"
        assert config.checks.min_score == 70  # default


class TestGenerateConfig:
    def test_generates_valid_yaml(self):
        import yaml
        content = generate_default_config()
        data = yaml.safe_load(content)
        assert data["version"] == 1
        assert "checks" in data
        assert "project" in data
