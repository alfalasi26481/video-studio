#!/usr/bin/env python3
"""Read-only check of the performance log docs/metrics.csv (STYLE_PLAN §4, PLATFORM_STRATEGY §3).

Both plans decide on numbers that nobody was asked for: "after 6 episodes compare by hook
and theme, keep the best" and "after 8 weeks compare the English accounts with the Arabic
ones". The numbers are copied by hand from each platform's dashboard 48 h after a post.
On 6 Nov 2026 EP01 had been live for five days and the log still held three empty rows.

errors (the file itself)
  header    a required column is missing
  episode   EPNN with no master-claude/episodes/epNN.md
  lang      not AR / EN
  platform  not tiktok / instagram / youtube (Snapchat stopped 1 Nov 2026)
  percent   a *_pct value that is not a number in 0..100
  count     views/saves/shares that is not a whole number >= 0
  dup       the same episode + lang + platform twice
  style     theme · hook · breaks differ from the episode's own style (EP01-05: engine v1 =
            ember · stop · none; EP06+: the «الأسلوب» line of epNN.md) — a wrong label
            would poison the comparison the log exists for
warnings (against docs/publishing/CALENDAR.md, current posts only)
  due       a post of an episode went out more than 48 h ago and its row has no views_48h

Prints how many episodes are measured (the style comparison needs 6). Nothing is fetched
from any platform. Usage: python3 tools/metrics_check.py [--now YYYY-MM-DDTHH:MM]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import calendar_check as cc  # noqa: E402
import style_check as sc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "docs" / "metrics.csv"
EPISODES = ROOT / "master-claude" / "episodes"
COLUMNS = ["episode", "lang", "platform", "published", "views_48h", "hold_3s_pct",
           "avg_watched_pct", "completion_pct", "saves", "shares", "theme", "hook", "breaks"]
PLATFORMS = {"tiktok", "instagram", "youtube"}
PERCENT = ["hold_3s_pct", "avg_watched_pct", "completion_pct"]
COUNTS = ["views_48h", "saves", "shares"]
V1 = sc.Style("ember", "stop", "none")
NEEDED = 6  # STYLE_PLAN §4: compare after 6 measured episodes
WINDOW = dt.timedelta(hours=48)

Finding = tuple[str, str, str]


def parse(text: str) -> tuple[list[dict], list[Finding]]:
    reader = csv.DictReader(io.StringIO(text))
    missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        return [], [("error", "header", f"missing column(s): {', '.join(missing)}")]
    rows = []
    for n, row in enumerate(reader, 2):
        row = {k: (v or "").strip() for k, v in row.items() if k}
        row["_line"] = n
        rows.append(row)
    return rows, []


def episode_style(n: int, episodes: Path = EPISODES) -> sc.Style | None:
    if n < sc.FIRST_V2:
        return V1
    md = episodes / f"ep{n:02d}.md"
    return sc.style_from_md(md.read_text(encoding="utf-8")) if md.exists() else None


def check(rows: list[dict], episodes: Path = EPISODES) -> list[Finding]:
    out: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()
    for r in rows:
        at = f"line {r['_line']}"
        ep = r["episode"].upper()
        num = int(ep[2:]) if ep.startswith("EP") and ep[2:].isdigit() else None
        if num is None or not (episodes / f"ep{num:02d}.md").exists():
            out.append(("error", "episode", f"{at}: «{r['episode']}» has no epNN.md"))
            num = None
        if r["lang"].upper() not in {"AR", "EN"}:
            out.append(("error", "lang", f"{at}: lang «{r['lang']}» is not AR/EN"))
        if r["platform"].lower() not in PLATFORMS:
            out.append(("error", "platform", f"{at}: platform «{r['platform']}» is not one of {sorted(PLATFORMS)}"))
        key = (ep, r["lang"].upper(), r["platform"].lower())
        if key in seen:
            out.append(("error", "dup", f"{at}: {' '.join(key)} appears twice"))
        seen.add(key)
        for c in PERCENT:
            v = r[c]
            if v:
                try:
                    ok = 0 <= float(v) <= 100
                except ValueError:
                    ok = False
                if not ok:
                    out.append(("error", "percent", f"{at}: {c}={v} is not 0..100"))
        for c in COUNTS:
            v = r[c]
            if v and not v.isdigit():
                out.append(("error", "count", f"{at}: {c}={v} is not a whole number >= 0"))
        if num is not None:
            want = episode_style(num, episodes)
            got = sc.Style(r["theme"], r["hook"], r["breaks"] or "none")
            if want is not None and got != want:
                out.append(("error", "style", f"{at}: {ep} is {want.theme} · {want.hook} · {want.breaks}, "
                                              f"row says {got.theme} · {got.hook} · {got.breaks}"))
    return out


def due(rows: list[dict], posts: list[cc.Post], now: dt.datetime) -> list[Finding]:
    filled = {(r["episode"].upper(), r["lang"].upper(), r["platform"].lower())
              for r in rows if r["views_48h"]}
    out: list[Finding] = []
    for p in sorted(posts, key=lambda p: p.when):
        if p.ep is None or p.when + WINDOW > now:
            continue
        platform, lang = p.channel.split("-", 1)
        key = (f"EP{p.ep}", lang.upper(), platform)
        if key not in filled:
            out.append(("warning", "due", f"{' '.join(key)}: posted {p.when:%d %b %H:%M} UTC, "
                                          f"48 h passed — copy the dashboard numbers into docs/metrics.csv"))
    return out


def measured(rows: list[dict]) -> list[str]:
    return sorted({r["episode"].upper() for r in rows if r["views_48h"]})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--now", help="UTC time to judge 48 h against (default: now)")
    args = ap.parse_args(argv)
    now = (dt.datetime.fromisoformat(args.now) if args.now
           else dt.datetime.now(dt.timezone.utc).replace(tzinfo=None))
    rows, problems = parse(METRICS.read_text(encoding="utf-8"))
    posts, _ = cc.parse(cc.CALENDAR.read_text(encoding="utf-8"))
    findings = problems + check(rows) + due(rows, cc.current(posts), now)
    for lvl, rule, msg in findings:
        print(f"  [{lvl}] {rule}: {msg}")
    done = measured(rows)
    print(f"measured episodes: {len(done)}/{NEEDED} for the hook/theme comparison"
          + (f" ({', '.join(done)})" if done else ""))
    errors = sum(1 for f in findings if f[0] == "error")
    warnings = sum(1 for f in findings if f[0] == "warning")
    print(f"metrics check: {len(rows)} row(s), {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
