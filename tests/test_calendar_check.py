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
