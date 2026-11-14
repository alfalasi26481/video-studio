#!/usr/bin/env python3
"""Content similarity check between episodes (owner request 2 Nov 2026: «أهم شيء ما يكون تشابه في المحتوى»).

No two episodes may say the same thing in the same words. For every pair of episodes
in master-claude/episodes/epNN.md this compares, per language:

- the spoken script: a shared run of 4+ content words = error, 3 words = warning;
- the on-screen texts (hookSub, userMsg, badLabel, proResult, emailSubject, formulaTitle,
  step label / ex — from src/episodes/epNN.ts, or the md «نصوص الشاشة» table when the .ts
  does not exist yet): two texts that are the same or nearly the same (ratio >= 0.75) = error.

The series signature is allowed on purpose and never counted: the opening «توقف!/Stop!»,
«الحل/The fix», «واحد/اثنان/ثلاثة», «شاهد الفرق/See the difference», and the closing
«احفظ الفيديو وتابعنا…/Save this video…» sentence.

Pairs that were already approved or published before this rule are listed in ACCEPTED:
they are reported as warnings («مقبول قديماً») so the owner sees them, but do not fail.
Short labels (1–2 content words) count only when their words are identical; longer texts
by character ratio. A new episode can never be added to ACCEPTED silently — it needs the owner's word.

Read-only. Usage: python3 tools/similarity_check.py [NN ...]   (NN limits the report to
pairs that include those episodes)
"""
from __future__ import annotations

import difflib
import itertools
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "master-claude"
FIELD_RATIO = 0.75
MIN_FIELD_CHARS = 6

# Series signature + function words: a shared run made only of these is not "similar content".
SIGNATURE = set(
    """توقف الحل واحد اثنان ثلاثة اربعة أربعة شاهد الفرق احفظ الفيديو وتابعنا لمهارة جديدة كل يوم
    في من الى إلى على عن او أو و ثم هل لا ما قد هذا هذه انت أنت له لك لي بها به كيف بسيط
    stop the fix is one two three four see difference save this video and follow for more a an of to in
    it you your on or with new skill every day simple how
    قبل بعد before after""".split()
)

# Episodes the owner had approved (or published) when the rule was added, 2 Nov 2026.
# Overlaps between two of them are reported as warnings, not errors.
LEGACY = {"01", "02", "03", "04", "05", "06", "07"}
ACCEPTED: dict[frozenset, str] = {}  # extra pairs only with the owner's word

FIELDS = ("hookSub", "userMsg", "badLabel", "proResult", "emailSubject", "formulaTitle", "before", "after")
MD_FIELDS = {"hookSub", "userMsg", "badLabel", "proResult", "emailSubject", "formulaTitle"}


@dataclass
class Finding:
    level: str  # error | warning
    a: str
    b: str
    lang: str
    kind: str  # script | screen
    text: str

    def __str__(self) -> str:
        return f"  [{self.level}] EP{self.a}↔EP{self.b} {self.lang} {self.kind}: {self.text}"


def normalize(text: str) -> list[str]:
    t = text.lower()
    t = re.sub(r"[ً-ْـ]", "", t)  # diacritics, tatweel
    t = re.sub(r"[إأآ]", "ا", t).replace("ى", "ي").replace("ة", "ه")
    t = t.replace("’", "'").replace("'", "")
    t = re.sub(r"\bclaude\b|كلود", " claude ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return t.split()


def _sig(words: set[str]) -> set[str]:
    return {w for ws in words for w in normalize(ws)} | {"claude"}


SIG = _sig(SIGNATURE)


def strip_cta(script: str) -> str:
    """Drop the closing call-to-action sentence (series signature)."""
    m = re.search(r"(احفظ الفيديو|Save this video)", script)
    return script[: m.start()] if m else script


def scripts_from_md(text: str) -> tuple[str, str]:
    def block(header: str) -> str:
        m = re.search(header + r".*?```\n(.*?)\n```", text, re.S)
        return m.group(1) if m else ""

    return block(r"## السكربت"), block(r"## Script")


def screen_from_ts(text: str) -> tuple[list[str], list[str]]:
    out = []
    for lang in ("AR", "EN"):
        m = re.search(rf"export const EP\d\d_{lang}\b.*?(?=export const|\Z)", text, re.S)
        body = m.group(0) if m else ""
        steps = re.search(rf"const STEPS_{lang}[^=]*=\s*\[(.*?)\];", text, re.S)
        vals = []
        for f in FIELDS:
            mm = re.search(rf"\b{f}\s*:\s*(['\"])(.*?)\1\s*,", body)
            if mm:
                vals.append(mm.group(2))
        if steps:
            vals += [v for _, v in re.findall(r"\b(?:label|ex)\s*:\s*(['\"])(.*?)\1", steps.group(1))]
        out.append([v for v in vals if v.strip()])
    return out[0], out[1]


def screen_from_md(text: str) -> tuple[list[str], list[str]]:
    ar, en = [], []
    sec = re.search(r"## نصوص الشاشة.*?(?=\n## |\Z)", text, re.S)
    if not sec:
        return ar, en
    for row in sec.group(0).splitlines():
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) != 3 or not cells[0] or set(cells[0]) <= set("-: "):
            continue
        key = cells[0]
        if key in MD_FIELDS or key.isdigit() or key == "before / after":
            sep = r"\s+/\s+" if key == "before / after" else r"\s+—\s+"
            for side, dst in ((cells[1], ar), (cells[2], en)):
                dst += [p.strip() for p in re.split(sep, side) if p.strip()]
    return ar, en


@dataclass
class Episode:
    nn: str
    script: tuple[str, str]
    screen: tuple[list[str], list[str]]


def load(nn_filter: set[str] | None = None) -> list[Episode]:
    eps = []
    for md in sorted((MC / "episodes").glob("ep[0-9][0-9].md")):
        nn = md.stem[2:]
        text = md.read_text(encoding="utf-8")
        ts = MC / "src" / "episodes" / f"ep{nn}.ts"
        screen = screen_from_ts(ts.read_text(encoding="utf-8")) if ts.exists() else screen_from_md(text)
        eps.append(Episode(nn, scripts_from_md(text), screen))
    return eps


def shared_runs(a: list[str], b: list[str], n: int) -> set[str]:
    def grams(w):
        return {tuple(w[i : i + n]) for i in range(len(w) - n + 1)}

    return {" ".join(g) for g in grams(a) & grams(b) if not set(g) <= SIG and len(set(g) - SIG) >= 2}


def compare(x: Episode, y: Episode) -> list[Finding]:
    found: list[Finding] = []
    for li, lang in enumerate(("AR", "EN")):
        wa, wb = normalize(strip_cta(x.script[li])), normalize(strip_cta(y.script[li]))
        four = shared_runs(wa, wb, 4)
        for g in sorted(four):
            found.append(Finding("error", x.nn, y.nn, lang, "script", f"«{g}»"))
        covered = " | ".join(four)
        for g in sorted(shared_runs(wa, wb, 3)):
            if g not in covered:
                found.append(Finding("warning", x.nn, y.nn, lang, "script", f"«{g}»"))
        for s in x.screen[li]:
            for t in y.screen[li]:
                ns, nt = " ".join(normalize(s)), " ".join(normalize(t))
                ca, cb = [w for w in ns.split() if w not in SIG], [w for w in nt.split() if w not in SIG]
                if min(len(ns), len(nt)) < MIN_FIELD_CHARS or not ca or not cb:
                    continue
                if min(len(ca), len(cb)) <= 2:  # short labels: only the same words count
                    r = 1.0 if ca == cb else 0.0
                else:
                    r = difflib.SequenceMatcher(None, " ".join(ca), " ".join(cb)).ratio()
                if r >= FIELD_RATIO:
                    found.append(Finding("error", x.nn, y.nn, lang, "screen", f"«{s}» ≈ «{t}» ({r:.2f})"))
    acc = ACCEPTED.get(frozenset({x.nn, y.nn})) or (
        "معتمدتان قبل القاعدة" if {x.nn, y.nn} <= LEGACY else None)
    if acc:
        for f in found:
            if f.level == "error":
                f.level = "warning"
                f.text += f" — مقبول قديماً: {acc}"
    return found


def run(nns: set[str] | None = None) -> list[Finding]:
    eps = load()
    out = []
    for x, y in itertools.combinations(eps, 2):
        if nns and not ({x.nn, y.nn} & nns):
            continue
        out += compare(x, y)
    return out


def main(argv: list[str]) -> int:
    nns = {a.zfill(2) for a in argv} or None
    found = run(nns)
    for f in found:
        print(f)
    errs = sum(f.level == "error" for f in found)
    warns = len(found) - errs
    print(f"similarity check: {errs} error(s), {warns} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
