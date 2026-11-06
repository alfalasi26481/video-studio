#!/usr/bin/env python3
"""Backlog check: episodes/backlog.yaml agrees with the engine episodes (6 Nov 2026).

The backlog is where the next topic comes from, but it was last edited by hand on
3 Nov: EP08–EP15 were all approved by 6 Nov while their backlog rows still said
«draft», EP04/EP05/EP01/EP02 had no row pointing at them, and the only «idea» left
(ep18, connectors) is deferred by the content rule — so the list looked like it had
work in it and had none. Each row may carry `engine: N` = master-claude/episodes/epNN.md.

errors
  status   status not one of STATUSES
  dup      the same id twice, or two rows on the same engine episode
  missing  `engine: N` points at an epNN.md that does not exist
warnings
  stale    the engine episode is approved («- الحالة: **معتمدة…**») but the row is not
           approved/handed_off — or the row says approved and the episode is not
  unmapped an engine epNN.md that no row points at
  ideas    fewer than --min-ideas (3) rows with status «idea»: the next draft needs a
           new topic, checked on an official Anthropic page first
Read-only. Usage: python3 tools/backlog_check.py [--min-ideas N]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calendar_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "episodes" / "backlog.yaml"
EPISODES = cc.EPISODES
STATUSES = ("idea", "deferred", "draft", "verified", "rendered", "approved",
            "handed_off", "rendered_elsewhere")
DONE = ("approved", "handed_off")
EP_FILE = re.compile(r"^ep(\d{2})\.md$")


@dataclass
class Finding:
    level: str  # error | warning
    kind: str
    msg: str


def engine_numbers(episodes: Path = EPISODES) -> list[int]:
    return sorted(int(m.group(1)) for p in episodes.glob("ep*.md")
                  if (m := EP_FILE.match(p.name)))


def check(rows: list[dict], episodes: Path = EPISODES, min_ideas: int = 3) -> list[Finding]:
    out: list[Finding] = []
    existing = set(engine_numbers(episodes))
    seen_ids: set[str] = set()
    by_engine: dict[int, str] = {}
    for r in rows:
        rid, st = str(r.get("id", "?")), r.get("status", "")
        if rid in seen_ids:
            out.append(Finding("error", "dup", f"{rid}: id appears twice"))
        seen_ids.add(rid)
        if st not in STATUSES:
            out.append(Finding("error", "status", f"{rid}: status «{st}» not one of {', '.join(STATUSES)}"))
        n = r.get("engine")
        if n is None:
            continue
        if not isinstance(n, int) or n not in existing:
            out.append(Finding("error", "missing", f"{rid}: engine {n} — no master-claude/episodes/ep{n:02d}.md"
                               if isinstance(n, int) else f"{rid}: engine «{n}» is not a number"))
            continue
        if n in by_engine:
            out.append(Finding("error", "dup", f"{rid}: engine EP{n:02d} already on {by_engine[n]}"))
            continue
        by_engine[n] = rid
        approved = cc.approved(n, episodes)
        if approved and st not in DONE:
            out.append(Finding("warning", "stale", f"{rid}: EP{n:02d} is approved, backlog says «{st}» — set approved"))
        elif not approved and st in DONE:
            out.append(Finding("warning", "stale", f"{rid}: backlog says «{st}», EP{n:02d} status is "
                               f"«{cc.status(n, episodes) or 'missing'}»"))
    for n in sorted(existing - set(by_engine)):
        out.append(Finding("warning", "unmapped", f"EP{n:02d}: no backlog row has `engine: {n}`"))
    ideas = [str(r.get("id")) for r in rows if r.get("status") == "idea"]
    if len(ideas) < min_ideas:
        out.append(Finding("warning", "ideas",
                           f"{len(ideas)} idea(s) left ({', '.join(ideas) or 'none'}), fewer than {min_ideas} — "
                           "the next draft needs a new topic checked on an official Anthropic page"))
    return out


def load(path: Path = BACKLOG) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("episodes") or [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min-ideas", type=int, default=3)
    a = ap.parse_args(argv)
    rows = load()
    found = check(rows, min_ideas=a.min_ideas)
    for f in found:
        print(f"  [{f.level}] {f.kind}: {f.msg}")
    errs = sum(f.level == "error" for f in found)
    print(f"backlog check: {len(rows)} row(s), {errs} error(s), {len(found) - errs} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
