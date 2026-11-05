import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import calendar_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TODAY = dt.date(2026, 11, 4)


def pid(n: int) -> str:
    return f"cmw{n:022d}"


def run(md: str, today: dt.date = TODAY, episodes: Path = ROOT / "master-claude" / "episodes"):
    posts, problems = cc.parse(md)
    assert problems == []
    return [(lvl, rule) for lvl, rule, _ in cc.check(posts, today, episodes)]


def channel_table(title: str, rows: list[tuple[str, str, str]]) -> str:
    out = [f"### {title}", "| الموعد (UTC) | الحلقة | Postiz id |", "|---|---|---|"]
    out += [f"| {w} | {lbl} | {i} |" for w, lbl, i in rows]
    return "\n".join(out) + "\n"


def test_clean_schedule_passes():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))])
    md += channel_table("تيك توك الإنجليزي", [("2026-11-08 18:00", "EN EP03 Four habits", pid(2))])
    assert run(md) == []


def test_english_post_on_arabic_account_is_error():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "EN EP03 Four habits", pid(1))])
    assert ("error", "lang") in run(md)


def test_arabic_label_without_prefix_reads_as_arabic():
    md = channel_table("تيك توك الإنجليزي", [("2026-11-08 18:00", "تحقق قبل أن تثق", pid(1))])
    assert ("error", "lang") in run(md)


def test_same_episode_twice_on_one_channel():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1)),
                                           ("2026-11-10 16:00", "AR EP03 ب", pid(2))])
    assert ("error", "dup-ep") in run(md)


def test_same_episode_on_two_channels_is_fine():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    md += channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(2))])
    assert run(md) == []


def test_two_posts_in_one_slot():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1)),
                                           ("2026-11-08 16:00", "AR EP04 ب", pid(2))])
    assert ("error", "dup-slot") in run(md)


def test_deleted_id_column_removes_the_old_post():
    """The 4 Nov cycle re-created posts and recorded the old ids as deleted."""
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    md += ("## دورة 4 نوفمبر 2026\n"
           "| الموعد (UTC) | الحلقة | القناة | id جديد | id محذوف |\n|---|---|---|---|---|\n"
           f"| 11-10 16:00 | AR EP03 أ | إنستغرام AR | {pid(2)} | {pid(1)} |\n")
    posts, _ = cc.parse(md)
    live = cc.current(posts)
    assert [p.post_id for p in live] == [pid(2)]
    assert live[0].when == dt.datetime(2026, 11, 10, 16, 0)  # year from the heading
    assert run(md) == []


def test_unknown_episode_number():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP99 لا توجد", pid(1))])
    assert ("error", "no-ep") in run(md)


def test_future_slot_and_weekday_warnings_only():
    md = channel_table("إنستغرام الإنجليزي", [("2026-11-09 16:00", "EN EP03 Four habits", pid(1))])
    found = run(md)
    assert ("warning", "time") in found and ("warning", "weekday") in found
    assert not any(lvl == "error" for lvl, _ in found)


def test_past_posts_are_not_held_to_the_new_slot():
    md = channel_table("إنستغرام الإنجليزي", [("2026-11-02 16:00", "EN EP03 Four habits", pid(1))])
    assert run(md) == []


def test_tables_without_a_schedule_are_ignored():
    md = ("| المنصة | العربي | الإنجليزي |\n|---|---|---|\n| تيك توك | @x | جديد |\n"
          "| ما الناقص | لماذا | ما يفعله |\n|---|---|---|\n| حساب | تحقق | ينشئه |\n")
    posts, problems = cc.parse(md)
    assert posts == [] and problems == []


def test_unknown_channel_language_is_reported():
    md = channel_table("حساب ما", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    posts, problems = cc.parse(md)
    assert posts == [] and len(problems) == 1


def test_real_calendar_passes():
    assert cc.main(["--today", "2026-11-04"]) == 0


# --- runway (5 Nov 2026): how many days of scheduled posts are left per account

def runway(md: str, today: dt.date = TODAY, days: int = 7):
    posts, _ = cc.parse(md)
    return cc.runway(posts, today, days)


def test_runway_warns_when_account_schedule_ends_within_days():
    md = channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))])
    out = runway(md)
    assert [(lvl, rule) for lvl, rule, _ in out] == [("warning", "runway")]
    assert "2026-11-08" in out[0][2] and "4 day" in out[0][2]


def test_runway_quiet_when_schedule_reaches_beyond_days():
    md = channel_table("تيك توك العربي", [("2026-11-20 16:00", "AR EP03 أربع عادات", pid(1))])
    assert runway(md) == []


def test_runway_is_per_account():
    md = channel_table("تيك توك العربي", [("2026-11-20 16:00", "AR EP03 أربع عادات", pid(1))])
    md += channel_table("إنستغرام الإنجليزي", [("2026-11-06 18:00", "EN EP03 Four habits", pid(2))])
    out = runway(md)
    assert len(out) == 1 and "instagram-en" in out[0][2]


def test_runway_flags_account_with_nothing_left():
    md = channel_table("إنستغرام العربي", [("2026-11-01 16:00", "AR EP01 المعادلة", pid(1))])
    out = runway(md)
    assert len(out) == 1 and "nothing scheduled" in out[0][2]


def test_runway_ignores_deleted_posts():
    md = ("### إنستغرام العربي\n| الموعد (UTC) | الحلقة | Postiz id | id محذوف |\n|---|---|---|---|\n"
          f"| 2026-11-20 16:00 | AR EP03 أربع عادات | {pid(1)} | |\n"
          f"| 2026-11-06 16:00 | AR EP04 المشاريع | {pid(2)} | {pid(1)} |\n")
    out = runway(md)
    assert len(out) == 1 and "2026-11-06" in out[0][2]


def test_main_prints_runway_and_stays_green(tmp_path, capsys):
    f = tmp_path / "CALENDAR.md"
    f.write_text(channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))]),
                 encoding="utf-8")
    assert cc.main(["--file", str(f), "--today", "2026-11-04"]) == 0
    out = capsys.readouterr().out
    assert "[warning] runway" in out and "1 warning(s)" in out
