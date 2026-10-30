"""Content rules applied to episodes of the approved engine (master-claude/).

Reads only what the audience sees or hears:
  * episodes/epNN.md  — fenced blocks: spoken script, caption lines (JSON), post captions
                        (command blocks such as `python3 ...` are skipped, so are
                        English clip prompts in tables, which are never shown on screen)
  * src/episodes/epNN.ts — string literals (on-screen text), minus asset paths and enums

Never edits the engine. Usage:
    python3 tools/engine_content_check.py            # all episodes
    python3 tools/engine_content_check.py 01 02      # selected episodes
Exit code 1 when anything is flagged.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_check import check_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "master-claude"

_FENCE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)
_COMMAND = re.compile(r"^\s*(python3?|bash|npx|npm|pip|cd|git)\b")
_TS_STR = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")
_TS_SKIP = {"ar", "en", "rtl", "ltr", "role", "task", "context", "format", "budget", "heart"}
_AR = re.compile(r"[؀-ۿ]")


@dataclass(frozen=True)
class Flag:
    episode: str
    source: str
    code: str
    message: str
    text: str


def lang_of(text: str) -> str:
    return "ar" if _AR.search(text) else "en"


def md_texts(md: str) -> list[str]:
    """Audience-facing strings from an episode markdown file."""
    out: list[str] = []
    for block in _FENCE.findall(md):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        if not lines or all(_COMMAND.match(l) for l in lines):
            continue
        stripped = block.strip()
        if stripped.startswith("["):
            try:
                data = json.loads(stripped)
            except json.JSONDecodeError:
                data = None
            if isinstance(data, list):
                out += [row[1] for row in data if isinstance(row, list) and len(row) > 1 and isinstance(row[1], str)]
                continue
        out += [l for l in lines if not _COMMAND.match(l)]
    return out


def ts_texts(ts: str) -> list[str]:
    """On-screen string literals from an episode data file."""
    out: list[str] = []
    for line in ts.splitlines():
        s = line.strip()
        if s.startswith(("import ", "//", "export type")):
            continue
        for a, b in _TS_STR.findall(line):
            v = a or b
            if not v or v in _TS_SKIP or "/" in v or v.startswith("#") or v.startswith("../"):
                continue
            out.append(v.replace("\\'", "'"))
    return out


def check_episode(nn: str, root: Path = ROOT) -> list[Flag]:
    flags: list[Flag] = []
    sources = [(root / "episodes" / f"ep{nn}.md", md_texts), (root / "src" / "episodes" / f"ep{nn}.ts", ts_texts)]
    for path, extract in sources:
        if not path.exists():
            continue
        for text in extract(path.read_text(encoding="utf-8")):
            for f in check_text(text, lang_of(text)):
                flags.append(Flag(nn, path.name, f.code, f.message, text))
    return flags


def all_episode_ids(root: Path = ROOT) -> list[str]:
    ids = {p.stem[2:] for p in (root / "episodes").glob("ep*.md")}
    ids |= {p.stem[2:] for p in (root / "src" / "episodes").glob("ep[0-9][0-9].ts")}
    return sorted(ids)


def main(argv: list[str]) -> int:
    ids = argv[1:] or all_episode_ids()
    flags = [f for nn in ids for f in check_episode(nn)]
    for f in flags:
        print(f"EP{f.episode} {f.source} [{f.code}] {f.message} — {f.text}")
    print(f"checked {len(ids)} episode(s): {len(flags)} flag(s)")
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
