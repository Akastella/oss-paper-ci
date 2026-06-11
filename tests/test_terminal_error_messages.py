"""Tests for structured error messages."""

from __future__ import annotations

import pytest

from oss_paper_ci.errors import (
    OssPaperError, get_error, format_error_plain, ERRORS,
)


class TestErrorCodes:
    """Test predefined error codes."""

    def test_all_errors_have_code(self):
        for code, err in ERRORS.items():
            assert err.code == code

    def test_all_errors_have_what(self):
        for code, err in ERRORS.items():
            assert err.what, f"{code} missing 'what'"

    def test_all_errors_have_next_steps(self):
        for code, err in ERRORS.items():
            assert err.next_steps, f"{code} missing next_steps"

    def test_get_error_valid(self):
        err = get_error("E001")
        assert err is not None
        assert err.code == "E001"

    def test_get_error_invalid(self):
        err = get_error("E999")
        assert err is None


class TestErrorFormatting:
    """Test error message formatting."""

    def test_format_plain_basic(self):
        err = OssPaperError(code="E001", what="Something broke")
        text = format_error_plain(err)
        assert "E001" in text
        assert "Something broke" in text

    def test_format_plain_with_why(self):
        err = OssPaperError(code="E001", what="Broken", why="Because reasons")
        text = format_error_plain(err)
        assert "Because reasons" in text

    def test_format_plain_with_next_steps(self):
        err = OssPaperError(
            code="E001", what="Broken",
            next_steps=["Fix it", "Try again"],
        )
        text = format_error_plain(err)
        assert "Fix it" in text
        assert "Try again" in text

    def test_format_plain_with_retry(self):
        err = OssPaperError(
            code="E001", what="Broken",
            retry_command="oss-paper-ci scan .",
        )
        text = format_error_plain(err)
        assert "oss-paper-ci scan ." in text

    def test_format_plain_with_docs(self):
        err = OssPaperError(
            code="E001", what="Broken",
            docs_url="https://example.com/docs",
        )
        text = format_error_plain(err)
        assert "https://example.com/docs" in text

    def test_format_plain_debug_shows_traceback(self):
        err = OssPaperError(
            code="E001", what="Broken",
            traceback="Traceback: ...",
        )
        text = format_error_plain(err, debug=True)
        assert "Traceback" in text

    def test_format_plain_no_debug_hides_traceback(self):
        err = OssPaperError(
            code="E001", what="Broken",
            traceback="Traceback: ...",
        )
        text = format_error_plain(err, debug=False)
        assert "Traceback" not in text


class TestErrorToDict:
    """Test error serialization."""

    def test_to_dict_basic(self):
        err = OssPaperError(code="E001", what="Broken")
        d = err.to_dict()
        assert d["error_code"] == "E001"
        assert d["what"] == "Broken"

    def test_to_dict_full(self):
        err = OssPaperError(
            code="E001", what="Broken", why="reason",
            next_steps=["fix"], retry_command="cmd",
            docs_url="http://example.com",
        )
        d = err.to_dict()
        assert d["why"] == "reason"
        assert d["next_steps"] == ["fix"]
        assert d["retry_command"] == "cmd"
        assert d["docs_url"] == "http://example.com"
