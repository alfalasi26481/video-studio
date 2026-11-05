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
  unapproved  a future post whose epNN.md status line («- الحالة: **…**») does
            not open with «معتمدة» — only owner-approved episodes go out
            (5 Nov 2026: --plan proposed EP08 «مسودة v2» and EP09 for 19/22 Nov)
warnings (future posts only, from --today)
  time      Arabic not at 16:00 UTC, English not at 18:00 UTC (4 Nov 2026)
  weekday   not Sunday / Tuesday / Thursday (the published cadence)
  runway    an account's last current post is fewer than --runway-days days
            away (default 7), or nothing is left at all — the masters for the
            next episodes need the owner's go-ahead before the feed runs dry
            (5 Nov 2026: Arabic TikTok and YouTube end 12 Nov, the rest 15 Nov)
  gap       an episode missing inside an account's own run (between its first
            and last episode) — an account that simply started later is fine
            (5 Nov 2026: EP03-AR was on Instagram only; Arabic TikTok jumped
            from EP02 to EP04)

--plan N (read-only proposal, never scheduled by this tool)
  the next N episodes per account on the next free cadence slots after its
  last current post (or after today if the feed is dry): a skipped episode
  inside the account's run first, then the episodes after its last one, up to
  the last master-claude/episodes/epNN.md. Printed as rows in the calendar's
  own table shape (id columns «—»), ready to paste once Postiz returns ids
  — an episode that is not approved is held back and listed, never proposed
  (5 Nov 2026: every feed ends 15 Nov; EP07+ wait for hosted masters).

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


STATUS = re.compile(r"^-\s*الحالة:\s*\*\*(.+?)\*\*", re.M)


def status(n: int, episodes: Path = EPISODES) -> str:
    """The bold status word(s) of epNN.md, or "" when missing."""
    f = episodes / f"ep{n:02d}.md"
    if not f.exists():
        return ""
    m = STATUS.search(f.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else ""


def approved(n: int, episodes: Path = EPISODES) -> bool:
    return status(n, episodes).startswith("معتمدة")


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
            elif p.when.date() >= today and not approved(int(p.ep), episodes):
                out.append(("error", "unapproved", f"{where}: ep{p.ep}.md status is "
                            f"«{status(int(p.ep), episodes) or 'missing'}», not «معتمدة»"))
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


def gaps(posts: list[Post]) -> list[tuple[str, str, str]]:
    """One warning per episode skipped inside an account's own EP run."""
    eps: dict[str, set[int]] = {}
    for p in current(posts):
        if p.ep:
            eps.setdefault(p.channel, set()).add(int(p.ep))
    out: list[tuple[str, str, str]] = []
    for channel, have in sorted(eps.items()):
        lang = channel.rsplit("-", 1)[-1]
        for n in range(min(have) + 1, max(have)):
            if n in have:
                continue
            on = sorted(c for c, s in eps.items() if c != channel and c.endswith(f"-{lang}") and n in s)
            where = f" (scheduled on {', '.join(on)})" if on else ""
            out.append(("warning", "gap", f"{channel}: EP{n:02d} missing between "
                        f"EP{min(have):02d} and EP{max(have):02d}{where}"))
    return out


def last_episode(episodes: Path = EPISODES) -> int:
    nums = [int(m.group(1)) for f in episodes.glob("ep*.md") if (m := re.fullmatch(r"ep(\d\d)\.md", f.name))]
    return max(nums, default=0)


def episode_title(n: int, lang: str, episodes: Path = EPISODES) -> str:
    """Short title from the episode heading «# الحلقة N — AR / EN»."""
    f = episodes / f"ep{n:02d}.md"
    if not f.exists():
        return ""
    head = f.read_text(encoding="utf-8").splitlines()[0]
    title = head.split("—", 1)[-1].strip()
    ar, _, en = title.partition(" / ")
    return (en if lang == "en" and en else ar).strip()


def held(posts: list[Post], last_ep: int | None = None,
         episodes: Path = EPISODES) -> list[int]:
    """Episodes the plan would reach but skips because they are not approved."""
    if last_ep is None:
        last_ep = last_episode(episodes)
    eps = [int(p.ep) for p in current(posts) if p.ep]
    if not eps:
        return []
    return [n for n in range(min(eps) + 1, last_ep + 1)
            if (episodes / f"ep{n:02d}.md").exists() and not approved(n, episodes)
            and str(n).zfill(2) not in {p.ep for p in current(posts)}]


def plan(posts: list[Post], today: dt.date, count: int = 3,
         last_ep: int | None = None,
         episodes: Path = EPISODES) -> list[tuple[str, dt.datetime, int]]:
    """(channel, slot, episode) proposals: next `count` approved episodes per account."""
    if last_ep is None:
        last_ep = last_episode(episodes)
    by_channel: dict[str, list[Post]] = {}
    for p in current(posts):
        by_channel.setdefault(p.channel, []).append(p)
    out: list[tuple[str, dt.datetime, int]] = []
    for channel, ps in sorted(by_channel.items()):
        lang = channel.rsplit("-", 1)[-1]
        if lang not in SLOT:
            continue
        have = {int(p.ep) for p in ps if p.ep}
        if not have:
            continue
        queue = [n for n in range(min(have) + 1, max(have)) if n not in have]
        queue += list(range(max(have) + 1, last_ep + 1))
        queue = [n for n in queue if approved(n, episodes)]
        taken = {p.when for p in ps}
        start = max(max(p.when for p in ps),
                    dt.datetime.combine(today, dt.time(0, 0)) - dt.timedelta(minutes=1))
        day = start.date()
        for ep in queue[:count]:
            while True:
                slot = dt.datetime.combine(day, dt.time(*SLOT[lang]))
                if slot > start and day.weekday() in CADENCE and slot not in taken:
                    break
                day += dt.timedelta(days=1)
            taken.add(slot)
            start = slot
            out.append((channel, slot, ep))
    return out


CHANNEL_NAME = {"instagram": "إنستغرام", "tiktok": "تيك توك", "youtube": "يوتيوب"}


def plan_table(rows: list[tuple[str, dt.datetime, int]]) -> str:
    lines = ["| الموعد (UTC) | الحلقة | القناة | id جديد | id محذوف |", "|---|---|---|---|---|"]
    for channel, when, ep in sorted(rows, key=lambda r: (r[1], r[0])):
        platform, lang = channel.rsplit("-", 1)
        title = episode_title(ep, lang)
        label = f"{lang.upper()} EP{ep:02d} {title}".strip()
        lines.append(f"| {when:%m-%d %H:%M} | {label} | {CHANNEL_NAME.get(platform, platform)} {lang.upper()} | — | — |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", type=Path, default=CALENDAR)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date())
    ap.add_argument("--runway-days", type=int, default=RUNWAY_DAYS,
                    help="warn when an account's schedule ends sooner than this (0 = off)")
    ap.add_argument("--list", action="store_true", help="print the current schedule")
    ap.add_argument("--plan", type=int, metavar="N", default=0,
                    help="propose the next N episodes per account on free cadence slots (read-only)")
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
    if a.plan > 0:
        rows = plan(posts, a.today, a.plan)
        print(f"calendar plan: {len(rows)} proposal(s), next {a.plan} per account — not scheduled; "
              "each needs a hosted master")
        print(plan_table(rows))
        hold = held(posts)
        if hold:
            print("held (not approved, never proposed): " + ", ".join(
                f"EP{n:02d} «{status(n) or 'no status'}»" for n in hold))
        return 0
    findings = check(posts, a.today) + gaps(posts)
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
