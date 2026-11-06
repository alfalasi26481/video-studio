import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import calendar_check as cc  # noqa: E402
import metrics_check as mc  # noqa: E402

HEADER = "episode,lang,platform,published,views_48h,hold_3s_pct,avg_watched_pct,completion_pct,saves,shares,theme,hook,breaks\n"
NOW = dt.datetime(2026, 11, 6, 12, 0)


def pid(n: int) -> str:
    return f"cmw{n:022d}"


def calendar(rows):
    out = ["### إنستغرام العربي", "| الموعد (UTC) | الحلقة | Postiz id |", "|---|---|---|"]
    out += [f"| {w} | {lbl} | {pid(i)} |" for i, (w, lbl) in enumerate(rows, 1)]
    posts, problems = cc.parse("\n".join(out) + "\n")
    assert problems == []
    return cc.current(posts)


def rules(csv_text, posts=(), now=NOW):
    rows, problems = mc.parse(csv_text)
    found = problems + mc.check(rows) + mc.due(rows, list(posts), now)
    return {(lvl, rule) for lvl, rule, _ in found}


def test_empty_rows_and_nothing_due_is_clean():
    assert rules(HEADER + "EP01,AR,tiktok,,,,,,,,ember,stop,none\n") == set()


def test_missing_column_is_error():
    assert ("error", "header") in rules("episode,lang,platform\nEP01,AR,tiktok\n")


def test_unknown_episode_lang_platform_are_errors():
    found = rules(HEADER + "EP99,AR,tiktok,,,,,,,,ember,stop,none\n"
                  "EP01,FR,tiktok,,,,,,,,ember,stop,none\n"
                  "EP01,AR,snapchat,,,,,,,,ember,stop,none\n")
    assert {("error", "episode"), ("error", "lang"), ("error", "platform")} <= found


def test_percent_out_of_range_and_negative_count_are_errors():
    found = rules(HEADER + "EP01,AR,tiktok,2026-11-01,500,140,40,20,-3,2,ember,stop,none\n")
    assert ("error", "percent") in found
    assert ("error", "count") in found


def test_duplicate_row_is_error():
    row = "EP01,AR,tiktok,,,,,,,,ember,stop,none\n"
    assert ("error", "dup") in rules(HEADER + row + row)


def test_style_must_match_the_episode():
    # EP06 is electric · question · snap (epNN.md); EP01-05 are engine v1 = ember · stop · none
    assert ("error", "style") in rules(HEADER + "EP06,AR,tiktok,,,,,,,,ember,stop,none\n")
    assert ("error", "style") in rules(HEADER + "EP01,AR,tiktok,,,,,,,,gold,stop,none\n")
    assert rules(HEADER + "EP06,AR,tiktok,,,,,,,,electric,question,snap\n") == set()


def test_post_older_than_48h_without_numbers_is_due():
    posts = calendar([("2026-11-01 16:00", "EP01 المعادلة")])
    assert ("warning", "due") in rules(HEADER, posts)


def test_filled_row_clears_due():
    posts = calendar([("2026-11-01 16:00", "EP01 المعادلة")])
    csv = HEADER + "EP01,AR,instagram,2026-11-01,812,61,48,22,9,4,ember,stop,none\n"
    assert rules(csv, posts) == set()


def test_post_inside_48h_is_not_due_yet():
    posts = calendar([("2026-11-05 16:00", "EP03 أربع عادات")])
    assert rules(HEADER, posts) == set()


def test_post_without_episode_is_ignored():
    posts = calendar([("2026-10-31 16:00", "التعريف")])
    assert rules(HEADER, posts) == set()


def test_progress_counts_measured_episodes():
    csv = HEADER + ("EP01,AR,instagram,2026-11-01,812,61,48,22,9,4,ember,stop,none\n"
                    "EP02,AR,instagram,2026-11-03,500,55,44,20,3,1,ember,stop,none\n"
                    "EP02,AR,tiktok,,,,,,,,ember,stop,none\n")
    rows, _ = mc.parse(csv)
    assert mc.measured(rows) == ["EP01", "EP02"]


def test_real_file_has_no_errors():
    rows, problems = mc.parse(mc.METRICS.read_text(encoding="utf-8"))
    assert [p for p in problems + mc.check(rows) if p[0] == "error"] == []
