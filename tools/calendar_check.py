#!/usr/bin/env python3
"""Read-only check of the publishing calendar (docs/publishing/CALENDAR.md).

The calendar is edited by hand and by the automated Postiz task, cycle after
cycle; rows are added and old Postiz ids are recorded as deleted. This tool
rebuilds the *current* schedule (every row with a Postiz id, minus the ids
listed in an «id محذوف» column) and checks the owner's publishing rules on it:

errors
  lang      a post whose language differs from its channel (EN on an Arabic
            account — 1 Nov 2026 the owner had English posts removed from the
            Arabic Instagram account)
  dup-ep    the same episode scheduled twice on one channel
  dup-slot  two posts at the same date+time on one channel
  no-ep     an EPNN with no master-claude/episodes/epNN.md
warnings (future posts only, from --today)
  time      Arabic not at 16:00 UTC, English not at 18:00 UTC (4 Nov 2026)
  weekday   not Sunday / Tuesday / Thursday (the published cadence)
  runway    an account's last current post is fewer than --runway-days days
            away (default 7), or nothing is left at all — the masters for the
            next episodes need the owner's go-ahead before the feed runs dry
            (5 Nov 2026: Arabic TikTok and YouTube end 12 Nov, the rest 15 Nov)

Nothing is fetched from Postiz; the file is the only input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CALENDAR = ROOT / "docs" / "publishing" / "CALENDAR.md"
EPISODES = ROOT / "master-claude" / "episodes"

POSTIZ_ID = re.compile(r"\bc[a-z0-9]{24}\b")
YEAR = re.compile(r"\b(20\d\d)\b")
DATE = re.compile(r"^(?:(20\d\d)-)?(\d\d)-(\d\d)\s+(\d\d):(\d\d)$")
EP = re.compile(r"\bEP(\d\d)\b")
ARABIC = re.compile(r"[؀-ۿ]")
CADENCE = {6, 1, 3}  # Sunday, Tuesday, Thursday (Monday = 0)
SLOT = {"ar": (16, 0), "en": (18, 0)}


@dataclass
class Post:
    line: int
    when: dt.datetime
    label: str
    channel: str
    lang: str          # channel language
    post_id: str
    deleted: list[str] = field(default_factory=list)

    @property
    def ep(self) -> str | None:
        m = EP.search(self.label)
        return m.group(1) if m else None

    @property
    def label_lang(self) -> str:
        if re.match(r"^\s*EN\b", self.label):
            return "en"
        if re.match(r"^\s*AR\b", self.label) or ARABIC.search(self.label):
            return "ar"
        return "en"


def channel_lang(name: str) -> str | None:
    if re.search(r"\bEN\b|الإنجليزي", name):
        return "en"
    if re.search(r"\bAR\b|العربي", name):
        return "ar"
    return None


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def parse(text: str) -> tuple[list[Post], list[str]]:
    """Every calendar row with a Postiz id; problems that stop a row parsing."""
    posts: list[Post] = []
    problems: list[str] = []
    heading = ""
    year = None
    header: list[str] | None = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            header = None
            m = YEAR.search(heading)
            if m:
                year = int(m.group(1))
            continue
        if not line.startswith("|"):
            header = None
            continue
        row = cells(line)
        if header is None:
            header = row
            continue
        if set("".join(row)) <= set("-: "):
            continue
        col = {h: (row[i] if i < len(row) else "") for i, h in enumerate(header)}
        when_txt = next((v for h, v in col.items() if "الموعد" in h), "")
        m = DATE.match(when_txt)
        if not m:
            continue  # not a schedule table (accounts, to-do, ...)
        id_cell = next((v for h, v in col.items() if "Postiz" in h or h == "id جديد"), "")
        ids = POSTIZ_ID.findall(id_cell)
        if not ids:
            continue
        deleted = POSTIZ_ID.findall(next((v for h, v in col.items() if "محذوف" in h), ""))
        y = int(m.group(1)) if m.group(1) else (year or dt.date.today().year)
        when = dt.datetime(y, int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
        channel = col.get("القناة") or heading
        lang = channel_lang(channel)
        if lang is None:
            problems.append(f"line {n}: channel language unknown: «{channel}»")
            continue
        label = next((v for h, v in col.items() if "الحلقة" in h), "")
        posts.append(Post(n, when, label, normalise(channel), lang, ids[0], deleted))
    return posts, problems


def normalise(channel: str) -> str:
    """One key per account: platform + language."""
    platform = ("instagram" if re.search(r"إنستغرام|instagram", channel, re.I)
                else "tiktok" if re.search(r"تيك توك|tiktok", channel, re.I)
                else "youtube" if re.search(r"يوتيوب|youtube", channel, re.I)
                else channel)
    return f"{platform}-{channel_lang(channel)}"


def current(posts: list[Post]) -> list[Post]:
    gone = {d for p in posts for d in p.deleted}
    return [p for p in posts if p.post_id not in gone]


def check(posts: list[Post], today: dt.date, episodes: Path = EPISODES) -> list[tuple[str, str, str]]:
    """(level, rule, message) for the current schedule."""
    out: list[tuple[str, str, str]] = []
    live = current(posts)
    seen_ep: dict[tuple[str, str], Post] = {}
    seen_slot: dict[tuple[str, dt.datetime], Post] = {}
    for p in sorted(live, key=lambda p: (p.channel, p.when)):
        where = f"{p.channel} {p.when:%Y-%m-%d %H:%M} «{p.label}» (line {p.line})"
        if p.label_lang != p.lang:
            out.append(("error", "lang", f"{where}: {p.label_lang.upper()} post on a {p.lang.upper()} account"))
        if p.ep:
            key = (p.channel, p.ep)
            if key in seen_ep:
                out.append(("error", "dup-ep", f"{where}: EP{p.ep} already scheduled at "
                            f"{seen_ep[key].when:%Y-%m-%d %H:%M} (line {seen_ep[key].line})"))
            seen_ep[key] = p
            if not (episodes / f"ep{p.ep}.md").exists():
                out.append(("error", "no-ep", f"{where}: no master-claude/episodes/ep{p.ep}.md"))
        slot = (p.channel, p.when)
        if slot in seen_slot:
            out.append(("error", "dup-slot", f"{where}: slot taken by «{seen_slot[slot].label}» (line {seen_slot[slot].line})"))
        seen_slot[slot] = p
        if p.when.date() >= today:
            if (p.when.hour, p.when.minute) != SLOT[p.lang]:
                out.append(("warning", "time", f"{where}: {p.lang.upper()} slot is {SLOT[p.lang][0]:02d}:00 UTC"))
            if p.when.weekday() not in CADENCE:
                out.append(("warning", "weekday", f"{where}: {p.when:%A}, cadence is Sun/Tue/Thu"))
    return out


RUNWAY_DAYS = 7


def runway(posts: list[Post], today: dt.date, days: int = RUNWAY_DAYS) -> list[tuple[str, str, str]]:
    """One warning per account whose current schedule ends within `days` of today."""
    last: dict[str, dt.datetime] = {}
    for p in current(posts):
        if p.channel not in last or p.when > last[p.channel]:
            last[p.channel] = p.when
    out: list[tuple[str, str, str]] = []
    for channel, when in sorted(last.items()):
        left = (when.date() - today).days
        if left < 0:
            out.append(("warning", "runway", f"{channel}: nothing scheduled after "
                        f"{when:%Y-%m-%d} — the feed is dry"))
        elif left < days:
            out.append(("warning", "runway", f"{channel}: schedule ends {when:%Y-%m-%d} "
                        f"({left} day(s) left, threshold {days})"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", type=Path, default=CALENDAR)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date())
    ap.add_argument("--runway-days", type=int, default=RUNWAY_DAYS,
                    help="warn when an account's schedule ends sooner than this (0 = off)")
    ap.add_argument("--list", action="store_true", help="print the current schedule")
    a = ap.parse_args(argv)
    if not a.file.exists():
        print(f"calendar check: {a.file} not found", file=sys.stderr)
        return 2
    posts, problems = parse(a.file.read_text(encoding="utf-8"))
    for msg in problems:
        print(f"  [error] parse: {msg}")
    if a.list:
        for p in sorted(current(posts), key=lambda p: (p.when, p.channel)):
            print(f"  {p.when:%Y-%m-%d %H:%M}  {p.channel:<13} {p.label}")
    findings = check(posts, a.today)
    if a.runway_days > 0:
        findings += runway(posts, a.today, a.runway_days)
    for level, rule, msg in findings:
        print(f"  [{level}] {rule}: {msg}")
    errors = len(problems) + sum(1 for f in findings if f[0] == "error")
    warnings = sum(1 for f in findings if f[0] == "warning")
    print(f"calendar check: {len(current(posts))} current post(s), {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
