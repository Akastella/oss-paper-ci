"""Tests for smoke runner security."""

import pytest


class TestDangerousCommands:
    """Test detection of dangerous shell commands."""

    def test_dangerous_rm_rf_root(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("rm -rf /")

    def test_dangerous_rm_rf_glob(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("rm -rf /*")

    def test_dangerous_sudo(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("sudo apt install something")

    def test_dangerous_curl_pipe_sh(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("curl | sh")

    def test_dangerous_curl_pipe_bash(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("curl |bash")

    def test_dangerous_wget_pipe_sh(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("wget | sh")

    def test_dangerous_wget_pipe_bash(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("wget | bash")

    def test_dangerous_format(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("format C:")

    def test_dangerous_del(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("del /s /q C:\\")

    def test_dangerous_shutdown(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("shutdown -h now")

    def test_dangerous_mkfs(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("mkfs.ext4 /dev/sda1")

    def test_dangerous_dd(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("dd if=/dev/zero of=/dev/sda")

    def test_dangerous_redirect_dev_sd(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("> /dev/sda")

    def test_dangerous_case_insensitive(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert is_dangerous_command("SUDO rm -rf /")
        assert is_dangerous_command("Curl | sh")


class TestSafeCommands:
    """Test that normal commands are NOT flagged as dangerous."""

    def test_safe_python_command(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("python scripts/train.py")

    def test_safe_python_module(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("python -m pytest")

    def test_safe_make_command(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("make smoke")

    def test_safe_echo(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("echo hello world")

    def test_safe_pip_install(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("pip install numpy")

    def test_safe_git_command(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("git status")

    def test_safe_ls(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("ls -la")

    def test_safe_cat(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("cat README.md")

    def test_safe_pip_freeze(self):
        from oss_paper_ci.runner import is_dangerous_command
        assert not is_dangerous_command("pip freeze > requirements.txt")


class TestSmokeResult:
    """Test SmokeResult data model."""

    def test_result_defaults(self):
        from oss_paper_ci.runner import SmokeResult
        r = SmokeResult()
        assert r.exit_code == -1
        assert r.duration_seconds == 0.0
        assert r.timed_out is False
        assert r.blocked is False

    def test_result_to_dict(self):
        from oss_paper_ci.runner import SmokeResult
        r = SmokeResult(experiment_id="test", command="echo ok", exit_code=0)
        d = r.to_dict()
        assert d["experiment_id"] == "test"
        assert d["command"] == "echo ok"
        assert d["exit_code"] == 0

    def test_result_to_dict_with_timeout(self):
        from oss_paper_ci.runner import SmokeResult
        r = SmokeResult(timed_out=True, block_reason="timeout")
        d = r.to_dict()
        assert d["timed_out"] is True
        assert d["block_reason"] == "timeout"

    def test_result_to_dict_with_outputs(self):
        from oss_paper_ci.runner import SmokeResult
        r = SmokeResult(expected_outputs=[{"path": "out.csv", "exists": True}])
        d = r.to_dict()
        assert len(d["expected_outputs"]) == 1


class TestRunSmoke:
    """Test the run_smoke function."""

    def test_dry_run(self, tmp_path):
        from oss_paper_ci.runner import run_smoke
        result = run_smoke(str(tmp_path), "echo hello", dry_run=True)
        assert result.exit_code == 0
        assert result.block_reason == "dry_run"

    def test_dangerous_command_blocked(self, tmp_path):
        from oss_paper_ci.runner import run_smoke
        result = run_smoke(str(tmp_path), "rm -rf /")
        assert result.blocked is True
        assert "dangerous" in result.block_reason.lower()

    def test_simple_command(self, tmp_path):
        from oss_paper_ci.runner import run_smoke
        result = run_smoke(str(tmp_path), "echo hello", timeout=10)
        assert result.exit_code == 0
        assert "hello" in result.stdout_excerpt

    def test_expected_output_exists(self, tmp_path):
        from oss_paper_ci.runner import run_smoke
        (tmp_path / "output.txt").write_text("done")
        result = run_smoke(
            str(tmp_path), "echo ok",
            expected_outputs=["output.txt"], timeout=10,
        )
        assert len(result.expected_outputs) == 1
        assert result.expected_outputs[0]["exists"] is True

    def test_expected_output_missing(self, tmp_path):
        from oss_paper_ci.runner import run_smoke
        result = run_smoke(
            str(tmp_path), "echo ok",
            expected_outputs=["nonexistent.txt"], timeout=10,
        )
        assert len(result.expected_outputs) == 1
        assert result.expected_outputs[0]["exists"] is False

    def test_nonexistent_repo(self):
        from oss_paper_ci.runner import run_smoke
        result = run_smoke("/nonexistent/path", "echo ok")
        assert result.blocked is True
        assert "does not exist" in result.block_reason
