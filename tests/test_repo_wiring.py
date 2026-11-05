"""Repo wiring: every tool is tested, reachable from the Makefile, documented,
and every `make check` dependency is a real target.

Why (5 Nov 2026, cycle 44): 43 cycles added a tool each; nothing caught a tool
that lost its test, a target missing from .PHONY, or a `check` dependency that
no longer exists (make would then fail only in a fresh container).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = sorted(p.stem for p in (ROOT / "tools").glob("*.py"))
MAKEFILE = (ROOT / "Makefile").read_text(encoding="utf-8")
CLAUDE_MD = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")


def _targets():
    return set(re.findall(r"^([a-z][a-z-]*):", MAKEFILE, re.M))


def _phony():
    m = re.search(r"^\.PHONY:(.*)$", MAKEFILE, re.M)
    return set(m.group(1).split()) if m else set()


def _check_deps():
    m = re.search(r"^check:(.*)$", MAKEFILE, re.M)
    return m.group(1).split() if m else []


def test_tools_found():
    assert len(TOOLS) >= 10


def test_every_tool_has_a_test_file():
    missing = [t for t in TOOLS if not (ROOT / "tests" / f"test_{t}.py").exists()]
    assert not missing, f"tools without tests/test_<tool>.py: {missing}"


def _reachable():
    """Tools a make target runs, plus tools those import (transitively)."""
    seen = {t for t in TOOLS if f"tools/{t}.py" in MAKEFILE}
    frontier = list(seen)
    while frontier:
        src = (ROOT / "tools" / f"{frontier.pop()}.py").read_text(encoding="utf-8")
        for t in TOOLS:
            if t not in seen and re.search(rf"^\s*(from|import)\s+{t}\b", src, re.M):
                seen.add(t)
                frontier.append(t)
    return seen


def test_every_tool_is_reachable_from_the_makefile():
    missing = [t for t in TOOLS if t not in _reachable()]
    assert not missing, f"tools no make target runs or imports: {missing}"


def test_reachability_follows_imports():
    # content_check runs through engine_content_check; remaster through episode_factory
    assert {"content_check", "remaster"} <= _reachable()


def test_every_tool_is_documented_in_claude_md():
    # either named as tools/<x>.py or through its make target (make frozen-check)
    def documented(t):
        return f"tools/{t}.py" in CLAUDE_MD or f"make {t.replace('_', '-')}" in CLAUDE_MD

    missing = [t for t in TOOLS if not documented(t)]
    assert not missing, f"tools CLAUDE.md does not mention: {missing}"


def test_check_dependencies_are_real_targets():
    deps = _check_deps()
    assert deps, "Makefile has no check target"
    missing = [d for d in deps if d not in _targets()]
    assert not missing, f"check depends on missing targets: {missing}"


def test_check_runs_the_tests():
    assert "test" in _check_deps()


def test_every_target_is_phony():
    missing = sorted(_targets() - _phony())
    assert not missing, f"targets missing from .PHONY: {missing}"
