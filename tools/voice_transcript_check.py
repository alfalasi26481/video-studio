"""Does the voiceover say the script? (master-claude/public/vo/epNN_<lang>.wav vs epNN.md)

Why: the AI voice (Gemini TTS) sometimes drops, swaps or blurs a word — EP09-AR «أعلى» was
heard as «على», EP09-EN «Claude's memory» as «Claws memory», EP13-AR «الصوتي» still waits for
the owner's ear. Until now only a human listen caught these. This tool transcribes the voice
with faster-whisper (the same model the engine already uses in scripts/words.py) and aligns the
heard words with the spoken script, so every word the listener may miss gets a timestamp to
listen at. Read-only: it never regenerates a voice, never touches the engine.

It is a HINT, not a verdict: whisper 'small' mishears Arabic too. So:
  * word recall below MIN_RECALL[lang]          -> error   (the voice is probably wrong)
  * each run of script words not heard           -> warning «listen at t s»
Words match after normalisation (Arabic hamza/alef/ta-marbuta/ya forms, diacritics, digits
as words (AR 0-10, EN 0-20, 30), Claude = كلود) and fuzzily (similar spelling counts).

Usage:
    python3 tools/voice_transcript_check.py 09            # AR + EN of EP09
    python3 tools/voice_transcript_check.py 09 --langs ar
    python3 tools/voice_transcript_check.py all           # every episode with a voice
    python3 tools/voice_transcript_check.py 10 --model medium   # confirm a warning
7 Nov 2026 baseline (small): 30/30 voices pass, 16 warnings; the three checked with 'medium'
(EP10-EN «message», EP14-AR «لابني», EP07-AR «الويب») were whisper-small mishearings.
Transcripts are cached in master-claude/work/epNN_<lang>_heard.json (delete to redo).
Exit code 1 on any error, 2 when faster-whisper is missing.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "master-claude"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_length import spoken_scripts  # noqa: E402

MIN_RECALL = {"ar": 0.80, "en": 0.90}
FUZZY = 0.75

_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_TOKEN = re.compile(r"[\w'’]+", re.U)
_EN_NUM = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
           "fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()
_AR_NUM = "صفر واحد اثنان ثلاثه اربعه خمسه سته سبعه ثمانيه تسعه عشره".split()
_NUMBERS = {
    "ar": {str(i): w for i, w in enumerate(_AR_NUM)},
    "en": {**{str(i): w for i, w in enumerate(_EN_NUM)}, "30": "thirty"},
}
_ALIASES = {"claude": "كلود", "claudes": "كلود", "اثنين": "اثنان", "اثنتان": "اثنان"}


def normalize(word: str, lang: str) -> str:
    w = _DIACRITICS.sub("", word).lower().replace("’", "'")
    w = w.strip("'")
    if lang == "ar":
        w = re.sub("[أإآٱ]", "ا", w).replace("ى", "ي").replace("ة", "ه")
        w = w.replace("ؤ", "و").replace("ئ", "ي")
    else:
        w = w.replace("'s", "s").replace("'", "")
    w = _NUMBERS[lang].get(w, w)
    return _ALIASES.get(w, w) if lang == "ar" else w


_HARAKAT = re.compile("[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")  # combining marks only (no tatweel)
_TATWEEL_JOIN = re.compile(r"ـ\s+")                 # «الـ Artifact» / «لـ Claude» = one spoken word


def tokens(text: str, lang: str) -> list[str]:
    # Strip combining marks BEFORE cutting words: a shadda is not \w, so «قسّم»
    # used to become «قس» + «م» (7 Nov 2026, EP03/EP05 false warnings).
    text = _HARAKAT.sub("", text)
    if lang == "ar":
        text = _TATWEEL_JOIN.sub("ـ", text)
    out = []
    for t in _TOKEN.findall(text):
        parts = [p for p in t.split("ـ") if p] if lang == "ar" else [t]
        out.append("".join(normalize(p, lang) for p in parts))
    return [t for t in out if t]


def _similar(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, a, b).ratio() >= FUZZY


@dataclass(frozen=True)
class Miss:
    words: str      # script words, as written (normalised)
    heard: str      # what whisper heard in their place ("" = nothing)
    at: float       # seconds — where to listen


@dataclass(frozen=True)
class Report:
    lang: str
    total: int
    matched: int
    misses: list

    @property
    def recall(self) -> float:
        return self.matched / self.total if self.total else 1.0


def align(script: list[str], heard: list[tuple[float, str]]) -> tuple[int, list[Miss]]:
    """Count script words heard; return (matched, misses). heard = [(start_s, norm_word)]."""
    hw = [w for _, w in heard]
    sm = difflib.SequenceMatcher(None, script, hw, autojunk=False)
    matched, misses = 0, []

    def time_at(j: int) -> float:
        if not heard:
            return 0.0
        return heard[min(j, len(heard) - 1)][0]

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            matched += i2 - i1
            continue
        if op == "insert":
            continue
        s, h = script[i1:i2], hw[j1:j2]
        # joined / split words («شاهدالفرق» vs «شاهد الفرق»): compare the whole run
        if h and _similar("".join(s), "".join(h)) and len("".join(s)) >= 4:
            matched += len(s)
            continue
        missed: list[str] = []
        free = list(h)
        for w in s:
            hit = next((x for x in free if _similar(w, x)), None)
            if hit is None:
                missed.append(w)
            else:
                matched += 1
                free.remove(hit)
        if missed:
            misses.append(Miss(" ".join(missed), " ".join(h), time_at(j1)))
    return matched, misses


def check(script_text: str, heard_words: list, lang: str) -> Report:
    """heard_words = engine words.json rows: [start, end, word]."""
    script = tokens(script_text, lang)
    heard = []
    for start, _end, word in heard_words:
        for t in tokens(word, lang):
            heard.append((float(start), t))
    matched, misses = align(script, heard)
    return Report(lang, len(script), matched, misses)


def transcribe(wav: Path, lang: str, model: str = "small") -> list:  # pragma: no cover - needs the model
    import subprocess

    import numpy as np
    from faster_whisper import WhisperModel

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
        audio, language=lang, word_timestamps=True)
    return [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]


MODEL = "small"


def heard_for(nn: str, lang: str, root: Path = ROOT) -> list:
    tag = "" if MODEL == "small" else f"_{MODEL}"
    cache = root / "work" / f"ep{nn}_{lang}_heard{tag}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    words = transcribe(root / "public" / "vo" / f"ep{nn}_{lang}.wav", lang, MODEL)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    return words


def episodes_with_voice(root: Path = ROOT) -> list[str]:
    out = []
    for md in sorted((root / "episodes").glob("ep[0-9][0-9].md")):
        nn = md.stem[2:]
        if any((root / "public" / "vo" / f"ep{nn}_{l}.wav").exists() for l in ("ar", "en")):
            out.append(nn)
    return out


def run(nns: list[str], langs: list[str], root: Path = ROOT, heard=heard_for) -> int:
    errors = warnings = 0
    for nn in nns:
        md = root / "episodes" / f"ep{nn}.md"
        if not md.exists():
            print(f"  [error] EP{nn}: no {md.name}")
            errors += 1
            continue
        scripts = spoken_scripts(md.read_text(encoding="utf-8"))
        for lang in langs:
            wav = root / "public" / "vo" / f"ep{nn}_{lang}.wav"
            if lang not in scripts or not wav.exists():
                print(f"  EP{nn}-{lang.upper()}: skipped (no script or no voice)")
                continue
            rep = check(scripts[lang], heard(nn, lang, root), lang)
            bad = rep.recall < MIN_RECALL[lang]
            level = "error" if bad else "ok"
            print(f"  [{level}] EP{nn}-{lang.upper()}: heard {rep.matched}/{rep.total} script words "
                  f"({rep.recall:.0%}, min {MIN_RECALL[lang]:.0%})")
            errors += bad
            for m in rep.misses:
                heard_txt = f"heard «{m.heard}»" if m.heard else "not heard"
                print(f"    [warning] listen at {m.at:.1f} s: «{m.words}» — {heard_txt}")
                warnings += 1
    print(f"voice transcript check: {errors} error(s), {warnings} warning(s) "
          f"(whisper '{MODEL}' is a hint — re-check with --model medium, then by ear)")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("nn", help="episode number (09) or 'all'")
    ap.add_argument("--langs", default="ar en")
    ap.add_argument("--model", default="small",
                    help="whisper model; 'medium' to re-check a warning (slower, fewer false alarms)")
    a = ap.parse_args(argv)
    global MODEL
    MODEL = a.model
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        print("faster-whisper missing: pip install --break-system-packages faster-whisper numpy")
        return 2
    nns = episodes_with_voice() if a.nn == "all" else [a.nn.zfill(2)]
    return run(nns, a.langs.split())


if __name__ == "__main__":
    sys.exit(main())
