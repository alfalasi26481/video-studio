import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import postiz_reconcile as pr  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOW = dt.datetime(2026, 11, 7, 9, 0)
ACCOUNTS = {"IG AR": {"id": "x", "channel": "instagram-ar"},
            "IG EN": {"id": "y", "channel": "instagram-en"}}


def pid(n: int) -> str:
    return f"cmw{n:022d}"


def cal(rows: list[tuple[str, str, str, str]], title: str = "إنستغرام العربي") -> str:
    out = [f"## {title} 2026", "| الموعد (UTC) | الحلقة | Postiz id | الحالة |", "|---|---|---|---|"]
    out += [f"| {w} | {lbl} | {i} | {st} |" for w, lbl, i, st in rows]
    return "\n".join(out) + "\n"


def snap(posts: list[dict], fetched: str = "2026-11-07T08:30:00Z") -> dict:
    return {"fetched": fetched, "window": ["2026-10-31T00:00:00", "2027-01-31T00:00:00"],
            "accounts": ACCOUNTS, "posts": posts}


def post(n: int, when: str, state: str = "QUEUE", integration: str = "IG AR",
         first: str = "جملة عربية", **kw) -> dict:
    return {"id": pid(n), "publishDate": when, "state": state, "platform": "instagram-standalone",
            "integration": integration, "first": first, **kw}


def rules(text: str, s: dict, now: dt.datetime = NOW) -> list[str]:
    return [rule for _, rule, _ in pr.reconcile(text, s, now)]


def test_matching_calendar_is_clean():
    text = cal([("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1), "مجدول"),
                ("2026-11-05 16:00", "AR EP02", pid(2), "منشور")])
    s = snap([post(1, "2026-11-08T16:00:00"), post(2, "2026-11-05T16:00:00", "PUBLISHED")])
    assert rules(text, s) == []


def test_replaced_id_is_missing_error():
    # 7 Nov 2026: three past Arabic rows carried ids Postiz no longer had
    text = cal([("2026-11-03 16:00", "AR EP02", pid(1), "مجدول")])
    s = snap([post(9, "2026-11-03T16:00:00", "PUBLISHED")])
    found = pr.reconcile(text, s, NOW)
    assert ("error", "missing") in [(lvl, r) for lvl, r, _ in found]
    assert "untracked" in [r for _, r, _ in found]


def test_row_outside_snapshot_window_is_not_missing():
    text = cal([("2026-10-20 16:00", "AR EP01", pid(1), "منشور")])
    assert rules(text, snap([])) == []


def test_moved_time_and_account_are_errors():
    text = cal([("2026-11-08 16:00", "AR EP03", pid(1), "مجدول"),
                ("2026-11-10 16:00", "AR EP04", pid(2), "مجدول")])
    s = snap([post(1, "2026-11-08T18:00:00"),
              post(2, "2026-11-10T16:00:00", integration="IG EN", first="English")])
    assert rules(text, s).count("moved") == 2


def test_published_but_unmarked_warns():
    text = cal([("2026-11-01 16:00", "AR EP01", pid(1), "مجدول (من جلسة سابقة)")])
    s = snap([post(1, "2026-11-01T16:00:00", "PUBLISHED")])
    assert rules(text, s) == ["unmarked"]


def test_failed_and_late_posts():
    text = cal([("2026-11-05 16:00", "AR EP02", pid(1), "مجدول"),
                ("2026-11-06 16:00", "AR EP03", pid(2), "مجدول")])
    s = snap([post(1, "2026-11-05T16:00:00", "ERROR", error="token expired"),
              post(2, "2026-11-06T16:00:00", "QUEUE")])
    found = pr.reconcile(text, s, NOW)
    assert ("error", "failed") in [(lvl, r) for lvl, r, _ in found]
    assert ("warning", "late") in [(lvl, r) for lvl, r, _ in found]


def test_a_note_naming_the_id_acknowledges_it():
    text = cal([]) + f"\nملاحظة: المنشور {pid(5)} خرج قبل القرار.\n"
    s = snap([post(5, "2026-10-31T18:00:00", "PUBLISHED", first="English intro")])
    assert rules(text, s) == []


def test_account_map_beats_caption_language():
    # 31 Oct 2026: the English intro went out on the Arabic Instagram account
    p = post(1, "2026-10-31T18:00:00", "PUBLISHED", first="Stop spending half an hour")
    assert pr.postiz_channel(p, ACCOUNTS) == "instagram-ar"
    assert pr.postiz_channel(p) == "instagram-en"  # fallback without a map
    msg = [m for _, r, m in pr.reconcile(cal([]), snap([p]), NOW) if r == "untracked"][0]
    assert "caption language differs" in msg


def test_stale_snapshot_warns():
    assert rules(cal([]), snap([], fetched="2026-11-05T08:00:00Z")) == ["stale"]


def test_cli_missing_snapshot_exits_2(tmp_path, capsys):
    assert pr.main(["--snapshot", str(tmp_path / "none.json")]) == 2
    assert "no snapshot" in capsys.readouterr().out


def test_repo_snapshot_matches_calendar():
    s = json.loads((ROOT / "docs" / "publishing" / "postiz_snapshot.json").read_text(encoding="utf-8"))
    text = (ROOT / "docs" / "publishing" / "CALENDAR.md").read_text(encoding="utf-8")
    fetched = pr.ts(s["fetched"])
    # rows scheduled after the snapshot may legitimately be absent from it
    found = pr.reconcile(text, s, fetched)
    assert [r for _, r, _ in found if r in ("moved", "failed")] == []
