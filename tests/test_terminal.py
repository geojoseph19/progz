"""Tests for terminal detection utilities."""

import io

import pytest

from progz.terminal import supports_color


class TestSupportsColor:
    def test_stringio_no_color(self):
        assert supports_color(io.StringIO()) is False

    def test_no_color_env_disables(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert supports_color(io.StringIO()) is False

    def test_force_color_env_enables(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
        assert supports_color(io.StringIO()) is True

    def test_no_color_overrides_force_color(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setenv("FORCE_COLOR", "1")
        assert supports_color(io.StringIO()) is False

    def test_dumb_term_disables(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        monkeypatch.setenv("TERM", "dumb")

        class Tty(io.StringIO):
            def isatty(self):
                return True

        assert supports_color(Tty()) is False

    def test_tty_with_capable_term_enables(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        monkeypatch.setenv("TERM", "xterm-256color")

        class Tty(io.StringIO):
            def isatty(self):
                return True

        assert supports_color(Tty()) is True
