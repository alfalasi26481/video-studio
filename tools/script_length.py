"""Spoken-length estimate for engine episode scripts (master-claude/episodes/epNN.md).

Why: the engine template expects 25-35 s of voice. Voice generation (Gemini TTS) is the
first step that costs time, so a script that is too long or too short should be caught
while it is still text. This tool never calls a TTS service and never edits the engine.

How: the speaking rate (words per second) is calibrated per language from episodes that
already have a voice, i.e. a spoken script in epNN.md AND `voiceDur` in src/episodes/epNN.ts
(first EpisodeData = AR, second = EN, as the engine data files are written). The estimate
for a new script = words / rate. It is an ESTIMATE (marked so in the output), not a measure.

Checks:
  * estimate outside 25-35 s            -> error
  * AR vs EN estimates differ by > 4 s  -> warning (the two versions should match)

Usage:
    python3 tools/script_length.py            # all episodes
    python3 tools/script_length.py 03         # one episode
Exit code 1 on any error.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "master-claude"
MIN_S, MAX_S, PARITY_S = 25.0, 35.0, 4.0
# Fallback rates if no calibrated episode exists (words per second).
DEFAULT_RATE = {"ar": 2.0, "en": 2.6}

_SECTION = {
    "ar": re.compile(r"^##\s*السكربت.*?\n```[a-z]*\n(.*?)```", re.S | re.M),
    "en": re.compile(r"^##\s*Script.*?\n```[a-z]*\n(.*?)```", re.S | re.M),
}
_VOICE_DUR = re.compile(r"voiceDur:\s*([0-9.]+)")
_WORD = re.compile(r"[\w'’]+", re.U)


def spoken_scripts(md: str) -> dict[str, str]:
    out = {}
    for lang, rx in _SECTION.items():
        m = rx.search(md)
        if m:
            out[lang] = m.group(1).strip()
    return out


def word_count(text: str) -> int:
    return len(_WORD.findall(text))


def voice_durations(ts: str) -> dict[str, float]:
    vals = [float(v) for v in _VOICE_DUR.findall(ts)]
    return dict(zip(("ar", "en"), vals))


def calibrate(root: Path = ROOT) -> dict[str, float]:
    words = {"ar": 0, "en": 0}
    secs = {"ar": 0.0, "en": 0.0}
    for md_path in sorted((root / "episodes").glob("ep[0-9][0-9].md")):
        ts_path = root / "src" / "episodes" / f"{md_path.stem}.ts"
        if not ts_path.exists():
            continue
        scripts = spoken_scripts(md_path.read_text(encoding="utf-8"))
        durs = voice_durations(ts_path.read_text(encoding="utf-8"))
        for lang in ("ar", "en"):
            if lang in scripts and lang in durs:
                words[lang] += word_count(scripts[lang])
                secs[lang] += durs[lang]
    return {lang: (words[lang] / secs[lang] if secs[lang] else DEFAULT_RATE[lang]) for lang in ("ar", "en")}


@dataclass(frozen=True)
class Finding:
    level: str  # error | warning
    message: str


def check(scripts: dict[str, str], rates: dict[str, float]) -> tuple[dict[str, float], list[Finding]]:
    return check_durations({lang: word_count(t) / rates[lang] for lang, t in scripts.items()})


def check_durations(est: dict[str, float]) -> tuple[dict[str, float], list[Finding]]:
    findings: list[Finding] = []
    for lang in ("ar", "en"):
        if lang not in est:
            findings.append(Finding("error", f"{lang.upper()}: spoken script block / duration not found"))
            continue
        s = est[lang]
        if s < MIN_S:
            findings.append(Finding("error", f"{lang.upper()}: ~{s:.1f}s is shorter than {MIN_S:.0f}s"))
        elif s > MAX_S:
            findings.append(Finding("error", f"{lang.upper()}: ~{s:.1f}s is longer than {MAX_S:.0f}s"))
    if "ar" in est and "en" in est and abs(est["ar"] - est["en"]) > PARITY_S:
        findings.append(Finding("warning", f"AR ~{est['ar']:.1f}s vs EN ~{est['en']:.1f}s differ by more than {PARITY_S:.0f}s"))
    return est, findings


def main(argv: list[str]) -> int:
    rates = calibrate()
    ids = argv[1:] or sorted(p.stem[2:] for p in (ROOT / "episodes").glob("ep[0-9][0-9].md"))
    print(f"rates (words/s, calibrated): AR {rates['ar']:.2f} · EN {rates['en']:.2f}")
    errors = 0
    for nn in ids:
        md = (ROOT / "episodes" / f"ep{nn}.md")
        if not md.exists():
            print(f"EP{nn}: episodes/ep{nn}.md not found")
            errors += 1
            continue
        scripts = spoken_scripts(md.read_text(encoding="utf-8"))
        ts = ROOT / "src" / "episodes" / f"ep{nn}.ts"
        measured = voice_durations(ts.read_text(encoding="utf-8")) if ts.exists() else {}
        if measured.keys() >= {"ar", "en"}:
            # voice already exists: judge the real duration, not the estimate
            est, findings = check_durations(measured)
            summary = " · ".join(f"{l.upper()} {est[l]:.1f}s (measured voiceDur)" for l in est)
        else:
            est, findings = check(scripts, rates)
            summary = " · ".join(f"{l.upper()} {word_count(scripts[l])} words ≈ {est[l]:.1f}s (estimate)" for l in est)
        print(f"EP{nn}: {summary}")
        for f in findings:
            print(f"  [{f.level}] {f.message}")
            errors += f.level == "error"
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
