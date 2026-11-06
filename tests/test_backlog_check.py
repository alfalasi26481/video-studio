import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import backlog_check as bc  # noqa: E402


def _eps(tmp_path, statuses):
    d = tmp_path / "episodes"
    d.mkdir()
    for n, st in statuses.items():
        (d / f"ep{n:02d}.md").write_text(f"# الحلقة {n}\n\n- الحالة: **{st}** (تاريخ)\n", encoding="utf-8")
    return d


def _kinds(found, level=None):
    return [f.kind for f in found if level is None or f.level == level]


IDEAS = [{"id": f"i{k}", "status": "idea"} for k in range(3)]


def test_consistent_backlog_is_clean(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة", 2: "مسودة"})
    rows = [{"id": "a", "engine": 1, "status": "approved"}, {"id": "b", "engine": 2, "status": "draft"}] + IDEAS
    assert bc.check(rows, d) == []


def test_approved_episode_with_draft_row_is_stale(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة 6 نوفمبر 2026"})
    found = bc.check([{"id": "a", "engine": 1, "status": "draft"}] + IDEAS, d)
    assert _kinds(found) == ["stale"] and found[0].level == "warning"


def test_row_approved_but_episode_not_is_stale(tmp_path):
    d = _eps(tmp_path, {1: "مسودة v2"})
    found = bc.check([{"id": "a", "engine": 1, "status": "approved"}] + IDEAS, d)
    assert _kinds(found) == ["stale"] and "مسودة v2" in found[0].msg


def test_handed_off_counts_as_done(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة"})
    assert bc.check([{"id": "a", "engine": 1, "status": "handed_off"}] + IDEAS, d) == []


def test_engine_episode_without_row_is_unmapped(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة", 2: "معتمدة"})
    found = bc.check([{"id": "a", "engine": 1, "status": "approved"}] + IDEAS, d)
    assert _kinds(found) == ["unmapped"] and "EP02" in found[0].msg


def test_engine_pointing_at_missing_file_is_error(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة"})
    found = bc.check([{"id": "a", "engine": 1, "status": "approved"},
                      {"id": "b", "engine": 9, "status": "draft"}] + IDEAS, d)
    assert _kinds(found, "error") == ["missing"]
    found = bc.check([{"id": "a", "engine": "one", "status": "draft"}] + IDEAS, d)
    assert "missing" in _kinds(found, "error")


def test_duplicates_are_errors(tmp_path):
    d = _eps(tmp_path, {1: "معتمدة"})
    found = bc.check([{"id": "a", "engine": 1, "status": "approved"},
                      {"id": "a", "status": "idea"},
                      {"id": "c", "engine": 1, "status": "approved"}] + IDEAS, d)
    assert _kinds(found, "error") == ["dup", "dup"]


def test_unknown_status_is_error(tmp_path):
    d = _eps(tmp_path, {})
    found = bc.check([{"id": "a", "status": "done"}] + IDEAS, d)
    assert _kinds(found, "error") == ["status"]


def test_few_ideas_warns_and_deferred_does_not_count(tmp_path):
    d = _eps(tmp_path, {})
    found = bc.check([{"id": "x", "status": "deferred"}, {"id": "y", "status": "idea"}], d)
    assert _kinds(found) == ["ideas"] and "1 idea(s) left (y)" in found[0].msg
    assert bc.check([{"id": "y", "status": "idea"}], d, min_ideas=1) == []


def test_repo_backlog_has_no_errors():
    assert _kinds(bc.check(bc.load()), "error") == []
