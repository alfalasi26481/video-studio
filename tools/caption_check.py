"""Karaoke caption tokens that the browser's bidi algorithm will scramble.

An Arabic caption token glued to a Latin word (e.g. «لـClaude:») is one word for the
karaoke but two bidi runs for the browser: on screen it renders as «Claudeلـ» (EP11
preview, 2 Nov 2026). Write the Arabic prefix and the Latin word as two tokens
(«لـ Claude:»), as approved EP01 does.

Reads master-claude/src/episodes/epNN_words_ar.json only (read-only).
    python3 tools/caption_check.py            # all episodes
    python3 tools/caption_check.py 11         # selected episodes
EP01–EP07 were approved before this rule: warnings only. Exit 1 on any error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "master-claude" / "src" / "episodes"
LEGACY = {f"{n:02d}" for n in range(1, 8)}
_AR = re.compile("[\u0620-\u064A\u066E-\u06D3]")  # letters (+tatweel), not punctuation such as «،»
_LAT = re.compile(r"[A-Za-z]")


def mixed_tokens(lines: list[dict]) -> list[tuple[float, str]]:
    """(time, token) for every caption token holding both Arabic and Latin letters."""
    out = []
    for line in lines:
        for t, tok in line.get("words", []):
            if _AR.search(tok) and _LAT.search(tok):
                out.append((t, tok))
    return out


def check(episodes: list[str]) -> tuple[int, int]:
    errors = warnings = 0
    for nn in episodes:
        path = ROOT / f"ep{nn}_words_ar.json"
        if not path.exists():
            continue
        for t, tok in mixed_tokens(json.loads(path.read_text(encoding="utf-8"))):
            legacy = nn in LEGACY
            kind = "warning" if legacy else "error"
            note = " — مقبول قديماً: معتمدة قبل القاعدة" if legacy else " — افصل: «لـ Claude»"
            print(f"  [{kind}] EP{nn} {t:6.2f}s  «{tok}» حرف عربي ملتصق بكلمة لاتينية{note}")
            if legacy:
                warnings += 1
            else:
                errors += 1
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    eps = [a.zfill(2) for a in args] or sorted(p.name[2:4] for p in ROOT.glob("ep*_words_ar.json"))
    errors, warnings = check(eps)
    print(f"caption check: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
