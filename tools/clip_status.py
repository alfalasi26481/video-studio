#!/usr/bin/env python3
"""Clip status: which episodes still render on another episode's footage (5 Nov 2026).

Every episode has three own Higgsfield shots (hook · mid · burst; master-claude/CLAUDE.md
step 6, 16.25 credits each); glitch and outro are shared from EP01 on purpose. Previews
render on EP01's shots until the owner approves the spend, and an approved episode can sit
on those placeholders unnoticed until it is scheduled. This reports, per src/episodes/epNN.ts:

- own        all three own slots point at clips/epNN_*.mp4
- placeholder one or more own slots borrow another episode's clip (warning when the
              episode is approved: it needs the owner's shot decision before it goes out)
- a referenced clip file that does not exist in public/clips = error (the render breaks)

and the credits the approved placeholder episodes would cost. Read-only, spends nothing.
Usage: python3 tools/clip_status.py [NN ...]
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calendar_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "master-claude"
SRC = MC / "src" / "episodes"
CLIPS_DIR = MC / "public"
OWN_SLOTS = ("hook", "mid", "burst")
CREDITS_PER_SHOT = 16.25
CLIPS_RE = re.compile(r"const\s+clips\s*=\s*\{([^}]*)\}")
SLOT_RE = re.compile(r"(\w+)\s*:\s*'([^']+)'")


@dataclass
class Status:
    n: int
    clips: dict[str, str]
    borrowed: list[str]   # own slots pointing at another episode's clip
    missing: list[str]    # referenced files absent from public/

    @property
    def own(self) -> bool:
        return not self.borrowed


def clips_from_ts(text: str) -> dict[str, str]:
    m = CLIPS_RE.search(text)
    return dict(SLOT_RE.findall(m.group(1))) if m else {}


def status_of(n: int, text: str, public: Path = CLIPS_DIR) -> Status:
    clips = clips_from_ts(text)
    prefix = f"clips/ep{n:02d}_"
    borrowed = [s for s in OWN_SLOTS if s in clips and not clips[s].startswith(prefix)]
    missing = sorted({p for p in clips.values() if not (public / p).exists()})
    return Status(n, clips, borrowed, missing)


def collect(src: Path = SRC, public: Path = CLIPS_DIR, only: set[int] | None = None) -> list[Status]:
    out = []
    for f in sorted(src.glob("ep[0-9][0-9].ts")):
        n = int(f.stem[2:])
        if only and n not in only:
            continue
        out.append(status_of(n, f.read_text(encoding="utf-8"), public))
    return out


def report(statuses: list[Status], is_approved) -> tuple[list[str], int, int, float]:
    """(lines, errors, warnings, credits for approved placeholder episodes)."""
    lines, errors, warnings, credits = [], 0, 0, 0.0
    for s in statuses:
        ok = is_approved(s.n)
        tag = "approved" if ok else "not approved"
        if s.own:
            lines.append(f"  EP{s.n:02d}: own clips ({tag})")
        else:
            level = "warning" if ok else "info"
            lines.append(f"  [{level}] EP{s.n:02d}: placeholder — {', '.join(s.borrowed)} from "
                         f"{', '.join(sorted({Path(s.clips[b]).name for b in s.borrowed}))} ({tag})")
            if ok:
                warnings += 1
                credits += CREDITS_PER_SHOT * len(s.borrowed)
        for p in s.missing:
            errors += 1
            lines.append(f"  [error] EP{s.n:02d}: {p} referenced but not in master-claude/public/")
    return lines, errors, warnings, credits


def placeholder_approved(src: Path = SRC, public: Path = CLIPS_DIR,
                         episodes: Path = cc.EPISODES) -> list[int]:
    return [s.n for s in collect(src, public) if not s.own and cc.approved(s.n, episodes)]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    only = {int(a) for a in argv} or None
    statuses = collect(only=only)
    lines, errors, warnings, credits = report(statuses, cc.approved)
    print("\n".join(lines))
    held = [s.n for s in statuses if not s.own and cc.approved(s.n)]
    if held:
        print(f"approved on placeholder clips: {', '.join(f'EP{n:02d}' for n in held)} — own shots "
              f"would cost {credits:g} credits (owner approval needed; nothing generated)")
    print(f"clip status: {len(statuses)} episode(s), {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
