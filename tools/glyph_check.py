"""Glyph coverage check for episodes of the approved engine (master-claude/).

Every character the audience sees must exist in the font that will draw it.
If a character is missing, Chromium silently falls back to a system font
(or draws a box) — a broken letter in a rendered video.

How the engine picks fonts (src/engine/fonts.ts, read-only here):
  * Arabic composition  -> family Tajawal (arabic + latin subsets)
  * English composition -> family Inter (latin subset)
  * each subset file only applies inside its CSS `unicode-range`
  * weights 500/700/800/900 are all loaded, so a char must exist in all four

Texts checked:
  * src/episodes/epNN.ts           string literals, by the const they belong to
                                   (`..._AR` -> Tajawal, `..._EN` -> Inter)
  * src/episodes/epNN_words_LL.json karaoke caption words (LL = ar | en)

Never edits the engine. Needs fontTools + brotli (requirements-dev.txt).
Usage:
    python3 tools/glyph_check.py            # all episodes
    python3 tools/glyph_check.py 01 02
Exit code 1 when any character is not covered.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine_content_check import ts_texts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "master-claude"
WEIGHTS = ("500", "700", "800", "900")
FAMILY = {"ar": "Tajawal", "en": "Inter"}

_UR_MAP = re.compile(r"const UR[^=]*=\s*(\{.*?\});", re.S)
_CONST = re.compile(r"^\s*(?:export\s+)?const\s+(\w+)")
_AR = re.compile(r"[؀-ۿ]")


@dataclass(frozen=True)
class Missing:
    episode: str
    source: str
    lang: str
    char: str
    text: str

    @property
    def codepoint(self) -> str:
        return f"U+{ord(self.char):04X}"

    @property
    def name(self) -> str:
        return unicodedata.name(self.char, "?")


def parse_ranges(spec: str) -> list[tuple[int, int]]:
    """CSS unicode-range ("U+0600-06FF, U+200C") -> [(lo, hi), ...]."""
    out = []
    for part in spec.split(","):
        part = part.strip().upper()
        if not part:
            continue
        if not part.startswith("U+"):
            raise ValueError(f"bad unicode-range part: {part!r}")
        lo, _, hi = part[2:].partition("-")
        out.append((int(lo, 16), int(hi or lo, 16)))
    return out


def in_ranges(cp: int, ranges: list[tuple[int, int]]) -> bool:
    return any(lo <= cp <= hi for lo, hi in ranges)


def load_unicode_ranges(root: Path = ROOT) -> dict[str, list[tuple[int, int]]]:
    src = (root / "src" / "engine" / "fonts.ts").read_text(encoding="utf-8")
    m = _UR_MAP.search(src)
    if not m:
        raise RuntimeError("UR map not found in fonts.ts")
    return {name: parse_ranges(spec) for name, spec in json.loads(m.group(1)).items()}


@lru_cache(maxsize=None)
def _cmap(path: str) -> frozenset[int]:
    from fontTools.ttLib import TTFont  # imported lazily: needs brotli for woff2

    return frozenset(TTFont(path).getBestCmap())


class Coverage:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.ranges = load_unicode_ranges(root)

    def covered(self, ch: str, family: str) -> bool:
        """True when every loaded weight of `family` can draw `ch`."""
        cp = ord(ch)
        for w in WEIGHTS:
            files = [f for f in self.ranges if f.startswith(f"{family}-{w}-")]
            if not any(in_ranges(cp, self.ranges[f]) and cp in _cmap(str(self.root / "public" / "fonts" / f)) for f in files):
                return False
        return True


def _skip(ch: str) -> bool:
    # whitespace and invisible format controls (ZWJ/ZWNJ/bidi marks) draw nothing
    return ch.isspace() or unicodedata.category(ch) == "Cf"


def ts_texts_by_lang(ts: str) -> list[tuple[str, str]]:
    """(lang, text) for every on-screen literal, lang from the enclosing const name."""
    out: list[tuple[str, str]] = []
    current = ""
    for line in ts.splitlines():
        m = _CONST.match(line)
        if m:
            current = m.group(1).upper()
        for text in ts_texts(line):
            if current.endswith("_AR"):
                lang = "ar"
            elif current.endswith("_EN"):
                lang = "en"
            else:
                lang = "ar" if _AR.search(text) else "en"
            out.append((lang, text))
    return out


def words_texts(data: list) -> list[str]:
    return [w[1] for line in data for w in line.get("words", []) if isinstance(w, list) and len(w) > 1]


def episode_texts(nn: str, root: Path = ROOT) -> list[tuple[str, str, str]]:
    """(source, lang, text) for one episode."""
    out: list[tuple[str, str, str]] = []
    ts = root / "src" / "episodes" / f"ep{nn}.ts"
    if ts.exists():
        out += [(ts.name, lang, t) for lang, t in ts_texts_by_lang(ts.read_text(encoding="utf-8"))]
    for lang in ("ar", "en"):
        wj = root / "src" / "episodes" / f"ep{nn}_words_{lang}.json"
        if wj.exists():
            out += [(wj.name, lang, t) for t in words_texts(json.loads(wj.read_text(encoding="utf-8")))]
    return out


def check_episode(nn: str, root: Path = ROOT, cov: Coverage | None = None) -> list[Missing]:
    cov = cov or Coverage(root)
    found: dict[tuple[str, str, str], Missing] = {}
    for source, lang, text in episode_texts(nn, root):
        for ch in text:
            if _skip(ch) or cov.covered(ch, FAMILY[lang]):
                continue
            found.setdefault((source, lang, ch), Missing(nn, source, lang, ch, text))
    return list(found.values())


def all_episode_ids(root: Path = ROOT) -> list[str]:
    return sorted(p.stem[2:] for p in (root / "src" / "episodes").glob("ep[0-9][0-9].ts"))


def main(argv: list[str], root: Path | None = None) -> int:
    root = root or ROOT
    ids = argv[1:] or all_episode_ids(root)
    cov = Coverage(root)
    missing = [m for nn in ids for m in check_episode(nn, root, cov)]
    for m in missing:
        print(f"EP{m.episode} {m.source} [{m.lang}/{FAMILY[m.lang]}] {m.codepoint} {m.name} «{m.char}» — {m.text}")
    print(f"checked {len(ids)} episode(s): {len(missing)} uncovered character(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
