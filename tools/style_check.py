#!/usr/bin/env python3
"""Style variety check (owner request 1 Nov 2026, docs/STYLE_PLAN.md).

From episode 06 every episode runs on engine v2 with a style (theme · hook · break), and
"the hook and the theme never repeat in two consecutive episodes". This makes that rule a check:

- every master-claude/episodes/epNN.md with NN >= 06 declares its style on the
  «الأسلوب» line (`theme` · `hook` · `break` in backticks);
- the values exist in engine v2 (theme.ts);
- when src/episodes/epNN.ts exists, its `style` matches the .md (the script was written for it);
- consecutive episodes differ in theme AND hook (error);
- a style that differs from the STYLE_PLAN table is a warning (the table is a plan, not a law).

Read-only. Usage: python3 tools/style_check.py [NN ...]
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "master-claude"
FIRST_V2 = 6
THEMES = {"ember", "electric", "gold", "mint"}
HOOKS = {"stop", "question", "reveal"}
BREAKS = {"none", "snap"}


@dataclass(frozen=True)
class Style:
    theme: str
    hook: str
    breaks: str


def style_from_md(text: str) -> Style | None:
    line = next((ln for ln in text.splitlines() if ln.lstrip("- ").startswith("الأسلوب")), None)
    if not line:
        return None
    vals = re.findall(r"`([a-z]+)`", line)
    theme = next((v for v in vals if v in THEMES), None)
    hook = next((v for v in vals if v in HOOKS), None)
    brk = next((v for v in vals if v in BREAKS), "none")
    if not theme or not hook:
        return None
    return Style(theme, hook, brk)


def style_from_ts(text: str) -> Style | None:
    m = re.search(r"style\s*:\s*Style\s*=\s*\{([^}]*)\}", text)
    if not m:
        return None
    body = m.group(1)
    get = lambda k: (re.search(rf"{k}\s*:\s*'([a-z]+)'", body) or [None, None])[1]  # noqa: E731
    if not get("theme") or not get("hook"):
        return None
    return Style(get("theme"), get("hook"), get("breaks") or "none")


def plan_table(text: str) -> dict[int, Style]:
    out = {}
    for m in re.finditer(r"^\|\s*(\d{2})[^|]*\|\s*([a-z]+)\s*\|\s*([a-z]+)\s*\|\s*([a-z]+)\s*\|", text, re.M):
        out[int(m.group(1))] = Style(m.group(2), m.group(3), m.group(4))
    return out


def check(styles: dict[int, Style | None], ts_styles: dict[int, Style | None], plan: dict[int, Style]):
    errors: list[str] = []
    warnings: list[str] = []
    for n in sorted(styles):
        s = styles[n]
        tag = f"EP{n:02d}"
        if s is None:
            errors.append(f"{tag}: لا يوجد سطر «الأسلوب» بثيم وافتتاحية معروفة")
            continue
        if n in ts_styles and ts_styles[n] is not None and ts_styles[n] != s:
            errors.append(f"{tag}: الأسلوب في epNN.ts {ts_styles[n]} ≠ الأسلوب في epNN.md {s}")
        prev = styles.get(n - 1)
        if prev is not None:
            if prev.theme == s.theme:
                errors.append(f"{tag}: نفس ثيم الحلقة السابقة ({s.theme})")
            if prev.hook == s.hook:
                errors.append(f"{tag}: نفس افتتاحية الحلقة السابقة ({s.hook})")
        if n in plan and plan[n] != s:
            warnings.append(f"{tag}: يختلف عن جدول STYLE_PLAN ({plan[n]})")
    return errors, warnings


def load(only: set[int] | None = None):
    styles, ts_styles = {}, {}
    for p in sorted((MC / "episodes").glob("ep[0-9][0-9].md")):
        n = int(p.stem[2:])
        if n < FIRST_V2:
            continue
        styles[n] = style_from_md(p.read_text(encoding="utf-8"))
        ts = MC / "src" / "episodes" / f"ep{n:02d}.ts"
        if ts.exists():
            ts_styles[n] = style_from_ts(ts.read_text(encoding="utf-8"))
    plan = plan_table((ROOT / "docs" / "STYLE_PLAN.md").read_text(encoding="utf-8"))
    errors, warnings = check(styles, ts_styles, plan)
    if only:
        keep = tuple(f"EP{n:02d}:" for n in only)
        errors = [e for e in errors if e.startswith(keep)]
        warnings = [w for w in warnings if w.startswith(keep)]
    return styles, errors, warnings


def main(argv: list[str]) -> int:
    only = {int(a) for a in argv} or None
    styles, errors, warnings = load(only)
    for n, s in sorted(styles.items()):
        if only is None or n in only:
            print(f"EP{n:02d}: {s.theme} · {s.hook} · {s.breaks}" if s else f"EP{n:02d}: —")
    for w in warnings:
        print("تحذير:", w)
    for e in errors:
        print("خطأ:", e)
    print(f"style check: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
