"""Tests for Docker and devcontainer files."""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent


class TestDockerfile:
    """Test Dockerfile exists and is valid."""

    def test_dockerfile_exists(self):
        assert (ROOT / "Dockerfile").exists()

    def test_dockerfile_has_from(self):
        content = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "FROM" in content

    def test_dockerfile_has_entrypoint(self):
        content = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "ENTRYPOINT" in content or "CMD" in content

    def test_dockerfile_no_forbidden_paths(self):
        content = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        # Should not copy dist/build/site/cache
        assert "COPY dist/" not in content
        assert "COPY build/" not in content
        assert "COPY site/" not in content

    def test_dockerfile_non_root_user(self):
        content = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "USER" in content

    def test_dockerignore_exists(self):
        assert (ROOT / ".dockerignore").exists()

    def test_dockerignore_covers_dist(self):
        content = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        assert "dist/" in content

    def test_dockerignore_covers_build(self):
        content = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        assert "build/" in content

    def test_dockerignore_covers_cache(self):
        content = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        assert "__pycache__" in content or ".pytest_cache" in content


class TestDevcontainer:
    """Test devcontainer files."""

    def test_devcontainer_dir_exists(self):
        assert (ROOT / ".devcontainer").is_dir()

    def test_devcontainer_json_exists(self):
        assert (ROOT / ".devcontainer" / "devcontainer.json").exists()

    def test_devcontainer_json_valid(self):
        content = (ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "name" in data
        assert "image" in data or "build" in data

    def test_devcontainer_has_post_create(self):
        """Should have postCreateCommand or postCreateCommand.sh."""
        dc_json = (ROOT / ".devcontainer" / "devcontainer.json")
        if dc_json.exists():
            content = dc_json.read_text(encoding="utf-8")
            data = json.loads(content)
            # Either inline command or script reference
            has_command = "postCreateCommand" in data
            has_script = (ROOT / ".devcontainer" / "postCreateCommand.sh").exists()
            assert has_command or has_script
