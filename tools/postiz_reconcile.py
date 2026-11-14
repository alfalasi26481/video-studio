#!/usr/bin/env python3
"""Compare the publishing calendar with what Postiz actually holds (read-only).

calendar_check reads docs/publishing/CALENDAR.md alone: the file says what was
*scheduled*. Posts are also re-created by the automated Postiz task, so the
file drifts (7 Nov 2026: three past Arabic posts carried ids Postiz no longer
had, nine published posts were not in the file at all, and five posts that
went out were still «unconfirmed»). This tool takes a snapshot of Postiz's
post list (docs/publishing/postiz_snapshot.json, refreshed from the Postiz MCP
read `postsListTool` before each run) and reports:

errors
  missing    a current calendar row inside the snapshot window whose Postiz id
             is not in Postiz (deleted or replaced — record the new id)
  moved      the same id at another date/time or on another account
  failed     a Postiz post in ERROR state
warnings
  untracked  a Postiz post whose id appears nowhere in CALENDAR.md (a note
             line naming the id is enough to acknowledge it)
  unmarked   Postiz says PUBLISHED, the calendar row is not marked «منشور»
  late       a post dated before the snapshot time that Postiz has not
             published yet
  stale      the snapshot is older than --max-age-hours (default 24): read
             Postiz again before trusting the rest

Nothing is sent to Postiz and nothing is edited; the output says which rows
to fix by hand. Not part of `make check` (it needs a fresh Postiz read).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calendar_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "docs" / "publishing" / "postiz_snapshot.json"
PLATFORM = {"instagram-standalone": "instagram", "instagram": "instagram",
            "tiktok-business": "tiktok", "tiktok": "tiktok", "youtube": "youtube"}
ARABIC = re.compile(r"[؀-ۿ]")


def ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "")).replace(tzinfo=None, second=0, microsecond=0)


def postiz_channel(post: dict, accounts: dict | None = None) -> str:
    """Account key in calendar_check's shape (platform-lang).

    The snapshot's «accounts» map (integration name → channel) decides: an
    English caption on the Arabic account must stay on the Arabic account
    (31 Oct 2026: the English intro went out on Arabic Instagram). The caption
    language is only a fallback for an integration the map does not name.
    """
    acc = (accounts or {}).get(post.get("integration", ""))
    if acc:
        return acc["channel"] if isinstance(acc, dict) else acc
    platform = PLATFORM.get(post.get("platform", ""), post.get("platform", "?"))
    lang = "ar" if ARABIC.search(post.get("first", "")) else "en"
    return f"{platform}-{lang}"


def reconcile(calendar_text: str, snap: dict, now: dt.datetime,
              max_age_hours: float = 24) -> list[tuple[str, str, str]]:
    posts, _ = cc.parse(calendar_text)
    rows = {p.post_id: p for p in cc.current(posts)}
    remote = {p["id"]: p for p in snap.get("posts", [])}
    accounts = snap.get("accounts", {})
    fetched = ts(snap["fetched"])
    start, end = (ts(x) for x in snap["window"])
    out: list[tuple[str, str, str]] = []

    age = (now - fetched).total_seconds() / 3600
    if age > max_age_hours:
        out.append(("warning", "stale", f"snapshot fetched {fetched:%Y-%m-%d %H:%M} UTC, "
                    f"{age:.0f} h ago (max {max_age_hours:g}) — read Postiz again"))

    for pid, row in sorted(rows.items(), key=lambda kv: (kv[1].channel, kv[1].when)):
        where = f"{row.channel} {row.when:%Y-%m-%d %H:%M} «{row.label}» (line {row.line})"
        r = remote.get(pid)
        if r is None:
            if start <= row.when <= end:
                out.append(("error", "missing", f"{where}: id {pid} not in Postiz — "
                            "deleted or replaced; record the new id (old one in «id محذوف»)"))
            continue
        rw, rc = ts(r["publishDate"]), postiz_channel(r, accounts)
        if rw != row.when or rc != row.channel:
            out.append(("error", "moved", f"{where}: Postiz has it on {rc} at {rw:%Y-%m-%d %H:%M}"))
        if r.get("state") == "PUBLISHED" and not row.state.startswith(cc.PUBLISHED):
            out.append(("warning", "unmarked", f"{where}: PUBLISHED in Postiz — mark «{cc.PUBLISHED}»"))

    for pid, r in sorted(remote.items(), key=lambda kv: kv[1]["publishDate"]):
        rw, rc = ts(r["publishDate"]), postiz_channel(r, accounts)
        what = f"{rc} {rw:%Y-%m-%d %H:%M} «{r.get('first', '')[:40]}» ({pid})"
        if rc.rsplit("-", 1)[-1] != ("ar" if ARABIC.search(r.get("first", "")) else "en"):
            what += " [caption language differs from the account]"
        if r.get("state") == "ERROR":
            out.append(("error", "failed", f"{what}: {r.get('error') or 'ERROR'}"))
        elif r.get("state") != "PUBLISHED" and rw < fetched:
            out.append(("warning", "late", f"{what}: dated before the snapshot, state {r.get('state')}"))
        if pid not in calendar_text:
            out.append(("warning", "untracked", f"{what}: {r.get('state')} in Postiz, "
                        "not in CALENDAR.md — add a row (or a note naming the id)"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--calendar", type=Path, default=cc.CALENDAR)
    ap.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    ap.add_argument("--now", help="UTC time, YYYY-MM-DDTHH:MM (default: now)")
    ap.add_argument("--max-age-hours", type=float, default=24)
    a = ap.parse_args(argv)
    if not a.snapshot.exists():
        print(f"no snapshot at {a.snapshot} — save a Postiz postsListTool read there first")
        return 2
    snap = json.loads(a.snapshot.read_text(encoding="utf-8"))
    now = ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    found = reconcile(a.calendar.read_text(encoding="utf-8"), snap, now, a.max_age_hours)
    for lvl, rule, msg in found:
        print(f"  [{lvl}] {rule}: {msg}")
    errors = sum(1 for f in found if f[0] == "error")
    print(f"postiz reconcile: {len(snap.get('posts', []))} Postiz post(s), "
          f"{errors} error(s), {len(found) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
