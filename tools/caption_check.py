"""Karaoke caption tokens that the browser's bidi algorithm will scramble.

An Arabic caption token glued to a Latin word (e.g. «لـClaude:») is one word for the
karaoke but two bidi runs for the browser: on screen it renders as «Claudeلـ» (EP11
preview, 2 Nov 2026). Write the Arabic prefix and the Latin word as two tokens
(«لـ Claude:»), as approved EP01 does.

Second rule (EP12 preview, 2 Nov 2026): two Latin words as two karaoke tokens in
an Arabic line («Claude Code») are two separate spans in an RTL row, so the screen
shows «Code Claude». The same happens to the Arabic on-screen fields the engine
animates word by word (formulaTitle, hookSub, step ex). Join them with a no-break
space («Claude\u00a0Code») so they stay one token.

Reads master-claude/src/episodes/epNN_words_ar.json and epNN.ts only (read-only).
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


def _latin_only(tok: str) -> bool:
    return bool(_LAT.search(tok)) and not _AR.search(tok)


def latin_runs(lines: list[dict]) -> list[tuple[float, str]]:
    """(time, 'A B') for two consecutive Latin-only tokens in one Arabic caption line."""
    out = []
    for line in lines:
        words = line.get("words", [])
        for (t, a), (_, b) in zip(words, words[1:]):
            if _latin_only(a) and _latin_only(b):
                out.append((t, f"{a} {b}"))
    return out


_AR_FIELD = re.compile(r"(?:formulaTitle|hookSub|ex):\s*'([^']*)'")


def ar_field_runs(ts: str) -> list[str]:
    """Arabic-side per-word fields in epNN.ts holding two space-separated Latin words."""
    ar = ts.split("_EN: EpisodeData")[0].split("const STEPS_EN")[0] + (
        ts.split("_AR: EpisodeData", 1)[1].split("_EN: EpisodeData")[0] if "_AR: EpisodeData" in ts else "")
    out = []
    for val in _AR_FIELD.findall(ar):
        toks = val.split(" ")
        if any(_latin_only(a) and _latin_only(b) for a, b in zip(toks, toks[1:])):
            out.append(val)
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
        for t, run in latin_runs(json.loads(path.read_text(encoding="utf-8"))):
            print(f"  [error] EP{nn} {t:6.2f}s  «{run}» كلمتان لاتينيتان منفصلتان في سطر عربي تظهران مقلوبتين — اربطهما بمسافة غير منقسمة")
            errors += 1
        ts = ROOT / f"ep{nn}.ts"
        if ts.exists():
            for val in ar_field_runs(ts.read_text(encoding="utf-8")):
                print(f"  [error] EP{nn} نص شاشة عربي «{val}» يُحرَّك كلمة كلمة فيظهر مقلوباً — اربط الكلمتين بمسافة غير منقسمة")
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
