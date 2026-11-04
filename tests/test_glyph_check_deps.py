"""glyph_check must fail with one clear line, not a traceback, when brotli is missing.

Separate file from test_glyph_check.py: that one skips entirely without brotli,
so it could never cover this case (cycle 33, 4 Nov 2026 — every fresh container
hit `ImportError: No module named brotli` deep inside fontTools).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import glyph_check as gc  # noqa: E402


def test_missing_modules_reports_absent():
    assert gc.missing_modules(("json", "no_such_module_xyz")) == ["no_such_module_xyz"]


def test_main_exits_2_with_hint_when_dependency_missing(monkeypatch, capsys):
    monkeypatch.setattr(gc, "missing_modules", lambda names=gc.REQUIRED_MODULES: ["brotli"])
    assert gc.main(["glyph_check.py", "01"]) == 2
    err = capsys.readouterr().err
    assert "brotli" in err and "make setup" in err
    assert "Traceback" not in err


def test_required_modules_cover_woff2():
    assert "brotli" in gc.REQUIRED_MODULES and "fontTools" in gc.REQUIRED_MODULES
