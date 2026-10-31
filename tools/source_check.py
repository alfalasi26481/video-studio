"""Official-source check for engine episodes (master-claude/episodes/epNN.md).

Why: channel rule — every claim about Claude must be checked on an official Anthropic
page. Until now this lived only in prose; EP01 and EP02 had no source line at all.
This tool makes it a check. It reads the episode .md files only (never the engine,
never the network).

What an episode must contain (one or more lines, anywhere in the .md):
    - المصدر الرسمي (رُوجع 31 أكتوبر 2026): https://support.claude.com/... — note
The date may also be ISO (2026-10-31). Several URLs may share one line.

Checks:
  * no source line                                   -> error
  * source line without a review date                -> error
  * a URL on a source line that is not official      -> error
  * newest review date older than STALE_DAYS (90)    -> warning (re-check the page)

Official = anthropic.com, claude.com, claude.ai and their subdomains
(support., docs., platform., academy., code., www., ...).

Usage:
    python3 tools/source_check.py         # all episodes
    python3 tools/source_check.py 03      # one episode
Exit code 1 on any error.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent / "master-claude" / "episodes"
STALE_DAYS = 90
OFFICIAL = ("anthropic.com", "claude.com", "claude.ai")

_SOURCE_LINE = re.compile(r"^\s*[-*]?\s*(?:المصدر الرسمي|المصادر الرسمية|Official source)s?\b.*$", re.M | re.I)
_URL = re.compile(r"https?://[^\s)>\]»،,]+")
_AR_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "مايو": 5, "يونيو": 6,
    "يوليو": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9, "أكتوبر": 10, "اكتوبر": 10,
    "نوفمبر": 11, "ديسمبر": 12,
}
_AR_DATE = re.compile(r"(\d{1,2})\s+(" + "|".join(_AR_MONTHS) + r")\s+(\d{4})")
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


@dataclass
class Report:
    episode: str
    urls: list[str] = field(default_factory=list)
    reviewed: dt.date | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def is_official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in OFFICIAL)


def parse_date(text: str) -> dt.date | None:
    m = _AR_DATE.search(text)
    if m:
        return dt.date(int(m.group(3)), _AR_MONTHS[m.group(2)], int(m.group(1)))
    m = _ISO_DATE.search(text)
    if m:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def check_text(episode: str, md: str, today: dt.date | None = None) -> Report:
    today = today or dt.date.today()
    rep = Report(episode)
    lines = _SOURCE_LINE.findall(md)
    if not lines:
        rep.errors.append("لا يوجد سطر «المصدر الرسمي (رُوجع <تاريخ>): <رابط>»")
        return rep
    dates = []
    for line in lines:
        urls = _URL.findall(line)
        if not urls:
            rep.errors.append(f"سطر مصدر بلا رابط: {line.strip()[:80]}")
        for u in urls:
            rep.urls.append(u)
            if not is_official(u):
                rep.errors.append(f"رابط غير رسمي: {u}")
        d = parse_date(line.split("http", 1)[0])  # the date sits before the URLs
        if d is None:
            rep.errors.append(f"سطر مصدر بلا تاريخ مراجعة: {line.strip()[:80]}")
        else:
            dates.append(d)
    if dates:
        rep.reviewed = max(dates)
        age = (today - rep.reviewed).days
        if age > STALE_DAYS:
            rep.warnings.append(f"آخر مراجعة قبل {age} يوماً — أعد فتح الصفحة وتأكد")
        if age < 0:
            rep.errors.append(f"تاريخ مراجعة في المستقبل: {rep.reviewed}")
    return rep


def episodes(root: Path = ROOT, only: str | None = None) -> list[Path]:
    files = sorted(root.glob("ep[0-9][0-9].md"))
    if only:
        files = [f for f in files if f.stem == f"ep{int(only):02d}"]
    return files


def main(argv: list[str]) -> int:
    only = argv[1] if len(argv) > 1 else None
    files = episodes(only=only)
    if not files:
        print(f"no episode file found for {only!r}")
        return 1
    failed = False
    for f in files:
        rep = check_text(f.stem, f.read_text(encoding="utf-8"))
        status = "FAIL" if rep.errors else ("WARN" if rep.warnings else "OK")
        print(f"{f.stem}: {status} · {len(rep.urls)} رابط · رُوجع {rep.reviewed or '-'}")
        for e in rep.errors:
            print(f"  ✗ {e}")
        for w in rep.warnings:
            print(f"  ! {w}")
        failed |= bool(rep.errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
