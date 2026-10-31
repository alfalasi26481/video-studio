import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import source_check as sc  # noqa: E402

TODAY = dt.date(2026, 10, 31)
GOOD = "- المصدر الرسمي (رُوجع 31 أكتوبر 2026): https://support.claude.com/en/articles/7996857-x — نصائح"


def test_good_line_passes():
    r = sc.check_text("ep03", f"# t\n{GOOD}\n", TODAY)
    assert r.errors == [] and r.warnings == []
    assert r.reviewed == dt.date(2026, 10, 31)
    assert r.urls == ["https://support.claude.com/en/articles/7996857-x"]


def test_missing_source_is_error():
    r = sc.check_text("ep01", "# الحلقة 1\n- الحالة: معتمدة\n", TODAY)
    assert len(r.errors) == 1


def test_unofficial_url_is_error():
    line = "- المصدر الرسمي (رُوجع 2026-10-31): https://some-blog.example.com/claude-tips"
    r = sc.check_text("ep04", line, TODAY)
    assert any("غير رسمي" in e for e in r.errors)


def test_lookalike_domain_is_not_official():
    assert not sc.is_official("https://claude.com.evil.example/x")
    assert not sc.is_official("https://notanthropic.com/x")
    assert sc.is_official("https://academy.claude.com/tutorials/x")
    assert sc.is_official("https://www.anthropic.com/news/x")
    assert sc.is_official("https://claude.ai/x")


def test_missing_date_is_error():
    r = sc.check_text("ep04", "- المصدر الرسمي: https://support.claude.com/x", TODAY)
    assert any("تاريخ" in e for e in r.errors)


def test_line_without_url_is_error():
    r = sc.check_text("ep04", "- المصدر الرسمي (رُوجع 31 أكتوبر 2026): سيُضاف لاحقاً", TODAY)
    assert any("بلا رابط" in e for e in r.errors)


def test_stale_review_is_warning_not_error():
    line = "- المصدر الرسمي (رُوجع 1 يوليو 2026): https://support.claude.com/x"
    r = sc.check_text("ep04", line, TODAY)
    assert r.errors == []
    assert len(r.warnings) == 1


def test_newest_of_several_lines_counts():
    md = ("- المصدر الرسمي (رُوجع 1 يوليو 2026): https://support.claude.com/a\n"
          "- المصدر الرسمي (رُوجع 2026-10-30): https://academy.claude.com/b\n")
    r = sc.check_text("ep04", md, TODAY)
    assert r.reviewed == dt.date(2026, 10, 30)
    assert r.warnings == [] and len(r.urls) == 2


def test_future_date_is_error():
    r = sc.check_text("ep04", "- المصدر الرسمي (رُوجع 2027-01-01): https://claude.com/x", TODAY)
    assert any("المستقبل" in e for e in r.errors)


def test_status_line_mentioning_source_word_is_not_a_source():
    # "المصدر" alone (e.g. a note) must not be read as the official source line.
    r = sc.check_text("ep04", "- ملاحظة: المصدر سيُراجع لاحقاً https://x.example\n", TODAY)
    assert len(r.errors) == 1 and r.urls == []


def test_real_engine_episodes_pass():
    files = sc.episodes()
    assert files, "engine episodes missing"
    for f in files:
        r = sc.check_text(f.stem, f.read_text(encoding="utf-8"), TODAY)
        assert r.errors == [], (f.stem, r.errors)
