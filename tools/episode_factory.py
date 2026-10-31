"""Episode factory for the approved engine (master-claude/) — roadmap item e.

    python3 tools/episode_factory.py all 02              # preflight -> render -> QA -> hand-off kit
    python3 tools/episode_factory.py all 02 --no-render  # reuse out/EP02-*.mp4 already rendered
    python3 tools/episode_factory.py preflight 02        # what is missing, and which engine step makes it
    python3 tools/episode_factory.py qa 02               # final checks on out/EP02-AR.mp4 / EN
    python3 tools/episode_factory.py kit 02              # captions (.srt) + per-platform post text

It WRAPS the engine; it never edits it. Rendering calls the unchanged `scripts/render.sh`.
It never calls Higgsfield or any paid service, and never publishes: the kit in
`out/EPNN/` is a manual hand-off.
Exit code 1 when preflight or QA fails.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_check import check_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "master-claude"
LANGS = ("AR", "EN")

# ---- platform rules --------------------------------------------------------
# Limits come from secondary sources found on 31 Oct 2026, NOT from official platform
# pages — treat as "غير مؤكد" and re-check before relying on them.
PLATFORMS = {
    "tiktok": {"name": "TikTok", "caption_max": 4000, "hashtags_max": 5, "body": "full"},
    # Instagram capped hashtags at 5 per post/Reel (Dec 2025, widely reported).
    "instagram": {"name": "Instagram Reels", "caption_max": 2200, "hashtags_max": 5, "body": "full"},
    # Snapchat Spotlight: short description; 160 chars is commonly cited.
    "snapchat": {"name": "Snapchat Spotlight", "caption_max": 160, "hashtags_max": 3, "body": "first"},
}

# Final QA thresholds — same as step 10 of master-claude/CLAUDE.md.
QA_RULES = {"width": 1080, "height": 1920, "fps": 30.0, "lufs": -14.0, "lufs_tol": 0.3, "peak_max": -1.0}

# Which engine step (master-claude/CLAUDE.md table) produces each asset.
STEP_FOR = {"script": 1, "vo": 2, "words": 5, "episode": 4, "registry": 4, "clips": 6, "music": 7}

_FENCE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)
_ASSET = re.compile(r"""['"]((?:clips|vo|music)/[^'"]+)['"]""")
_HASHTAG = re.compile(r"#[\w\u0600-\u06FF]+")


# ---- preflight -------------------------------------------------------------
@dataclass
class Missing:
    kind: str
    path: str

    @property
    def step(self) -> int:
        return STEP_FOR[self.kind]


def preflight(nn: str, root: Path = ROOT) -> list[Missing]:
    """Everything the render needs, checked before burning minutes in Chromium."""
    out: list[Missing] = []
    md = root / "episodes" / f"ep{nn}.md"
    ts = root / "src" / "episodes" / f"ep{nn}.ts"
    if not md.exists():
        out.append(Missing("script", str(md.relative_to(root))))
    if not ts.exists():
        out.append(Missing("episode", str(ts.relative_to(root))))
    else:
        for rel in sorted(set(_ASSET.findall(ts.read_text(encoding="utf-8")))):
            if not (root / "public" / rel).exists():
                kind = rel.split("/", 1)[0]
                out.append(Missing(kind, f"public/{rel}"))
    for lang in ("ar", "en"):
        w = root / "src" / "episodes" / f"ep{nn}_words_{lang}.json"
        if not w.exists():
            out.append(Missing("words", str(w.relative_to(root))))
    index = root / "src" / "episodes" / "index.ts"
    reg = index.read_text(encoding="utf-8") if index.exists() else ""
    for lang in LANGS:
        if f"'EP{nn}-{lang}'" not in reg and f'"EP{nn}-{lang}"' not in reg:
            out.append(Missing("registry", f"src/episodes/index.ts: EP{nn}-{lang}"))
    return out


# ---- episode markdown ------------------------------------------------------
def post_captions(md: str) -> dict[str, str]:
    """The two fenced blocks under '## تعليق النشر': Arabic first, English second."""
    m = re.search(r"^##\s*تعليق النشر\s*$(.*?)(?=^##\s|\Z)", md, re.S | re.M)
    if not m:
        return {}
    blocks = [b.strip() for b in _FENCE.findall(m.group(1))]
    out: dict[str, str] = {}
    for b in blocks:
        lang = "ar" if re.search(r"[\u0600-\u06FF]", _HASHTAG.sub("", b)) else "en"
        out.setdefault(lang, b)
    return out


def split_caption(text: str) -> tuple[list[str], list[str]]:
    """(body lines, hashtags in order, de-duplicated)."""
    body, tags = [], []
    for line in text.splitlines():
        found = _HASHTAG.findall(line)
        rest = _HASHTAG.sub("", line).strip()
        for t in found:
            if t.lower() not in (x.lower() for x in tags):
                tags.append(t)
        if rest:
            body.append(rest)
    return body, tags


def platform_post(text: str, platform: str) -> str:
    rule = PLATFORMS[platform]
    body, tags = split_caption(text)
    if rule["body"] == "first":
        body = body[:1]
    tags = tags[: rule["hashtags_max"]]
    post = "\n".join(body + ([" ".join(tags)] if tags else []))
    while len(post) > rule["caption_max"] and tags:
        tags = tags[:-1]  # drop hashtags first, never cut a sentence mid-word
        post = "\n".join(body + ([" ".join(tags)] if tags else []))
    if len(post) > rule["caption_max"]:
        raise ValueError(f"{rule['name']}: caption {len(post)} chars > {rule['caption_max']} — shorten it in epNN.md")
    return post


# ---- captions (.srt) -------------------------------------------------------
def _ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(lines: list[dict], rtl: bool) -> str:
    """Karaoke lines from scripts/captions.py -> SRT (for platform auto-caption upload)."""
    out = []
    for i, line in enumerate(lines, 1):
        text = " ".join(w[1] for w in line["words"])
        if rtl:
            text = "\u202b" + text + "\u202c"  # RLE…PDF keeps Arabic order with mixed Latin words
        out.append(f"{i}\n{_ts(line['start'])} --> {_ts(line['end'])}\n{text}\n")
    return "\n".join(out)


# ---- final QA ----------------------------------------------------------------
@dataclass
class QA:
    id: str
    width: int = 0
    height: int = 0
    fps: float = 0.0
    duration: float = 0.0
    has_audio: bool = False
    lufs: float | None = None
    peak: float | None = None
    problems: list[str] = field(default_factory=list)


def parse_ebur128(stderr: str) -> tuple[float | None, float | None]:
    """Integrated loudness and true peak from the ffmpeg ebur128 summary block."""
    summary = stderr.split("Summary:")[-1]
    i = re.search(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", summary)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS", summary)
    f = lambda m: None if not m or m.group(1) == "-inf" else float(m.group(1))  # noqa: E731
    return f(i), f(p)


def judge(q: QA, voice_dur: float | None = None) -> QA:
    r = QA_RULES
    if (q.width, q.height) != (r["width"], r["height"]):
        q.problems.append(f"size {q.width}x{q.height} (need {r['width']}x{r['height']})")
    if abs(q.fps - r["fps"]) > 0.01:
        q.problems.append(f"fps {q.fps:g} (need {r['fps']:g})")
    if not q.has_audio:
        q.problems.append("no audio stream")
    elif q.lufs is None or abs(q.lufs - r["lufs"]) > r["lufs_tol"]:
        q.problems.append(f"loudness {q.lufs} LUFS (need {r['lufs']}±{r['lufs_tol']})")
    if q.has_audio and (q.peak is None or q.peak >= r["peak_max"]):
        q.problems.append(f"true peak {q.peak} dBTP (need < {r['peak_max']})")
    if voice_dur and q.duration < voice_dur:
        q.problems.append(f"duration {q.duration:.2f}s shorter than the voice ({voice_dur:.2f}s)")
    return q


def probe(path: Path, vid: str) -> QA:
    q = QA(vid)
    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout)
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            q.width, q.height = int(s["width"]), int(s["height"])
            num, den = (s.get("r_frame_rate") or "0/1").split("/")
            q.fps = float(num) / float(den or 1)
        elif s.get("codec_type") == "audio":
            q.has_audio = True
    q.duration = float(info.get("format", {}).get("duration", 0))
    if q.has_audio:
        err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                              "-f", "null", "-"], capture_output=True, text=True).stderr
        q.lufs, q.peak = parse_ebur128(err)
    return q


def voice_dur(nn: str, lang: str, root: Path = ROOT) -> float | None:
    ts = root / "src" / "episodes" / f"ep{nn}.ts"
    if not ts.exists():
        return None
    m = re.search(rf"EP{nn}_{lang}\s*:\s*EpisodeData\s*=\s*\{{.*?voiceDur:\s*([\d.]+)", ts.read_text(encoding="utf-8"), re.S)
    return float(m.group(1)) if m else None


def run_qa(nn: str, langs=LANGS, root: Path = ROOT) -> list[QA]:
    res = []
    for lang in langs:
        vid = f"EP{nn}-{lang}"
        f = root / "out" / f"{vid}.mp4"
        if not f.exists():
            q = QA(vid)
            q.problems.append(f"missing out/{vid}.mp4 (render first)")
        else:
            q = judge(probe(f, vid), voice_dur(nn, lang, root))
        res.append(q)
    return res


# ---- hand-off kit -----------------------------------------------------------
def build_kit(nn: str, root: Path = ROOT, langs=LANGS, qa: list[QA] | None = None) -> Path:
    kit = root / "out" / f"EP{nn}"
    kit.mkdir(parents=True, exist_ok=True)
    md = (root / "episodes" / f"ep{nn}.md").read_text(encoding="utf-8")
    caps = post_captions(md)
    flags = []
    lines = [f"# EP{nn} — حزمة النشر اليدوي", "",
             "> النشر يدوي. حدود المنصات من مصادر ثانوية — **غير مؤكد**، راجعها قبل النشر.", ""]
    for lang in langs:
        lc = lang.lower()
        video = root / "out" / f"EP{nn}-{lang}.mp4"
        if video.exists():
            shutil.copy2(video, kit / video.name)
        words = root / "src" / "episodes" / f"ep{nn}_words_{lc}.json"
        if words.exists():
            data = json.loads(words.read_text(encoding="utf-8"))
            (kit / f"EP{nn}-{lang}.srt").write_text(to_srt(data, rtl=lc == "ar"), encoding="utf-8")
        text = caps.get(lc)
        lines.append(f"## {'العربية' if lc == 'ar' else 'English'} — `EP{nn}-{lang}.mp4` + `EP{nn}-{lang}.srt`")
        if not text:
            lines += ["", f"⚠️ لا يوجد تعليق نشر {lang} في `episodes/ep{nn}.md`", ""]
            continue
        flags += [f"{lang}: {f.code} «{f.text}»" for f in check_text(text, lc)]
        for key, rule in PLATFORMS.items():
            post = platform_post(text, key)
            lines += ["", f"**{rule['name']}** ({len(post)}/{rule['caption_max']} حرف)", "", "```", post, "```"]
        lines.append("")
    if qa:
        lines += ["## الفحص النهائي", ""]
        for q in qa:
            status = "✅" if not q.problems else "❌ " + "؛ ".join(q.problems)
            lines.append(f"- {q.id}: {q.width}x{q.height} · {q.fps:g}fps · {q.duration:.1f}ث · "
                         f"{q.lufs} LUFS · ذروة {q.peak} — {status}")
        lines.append("")
    if flags:
        lines += ["## ⚠️ فحص المحتوى على تعليق النشر", ""] + [f"- {f}" for f in flags] + [""]
    (kit / "PUBLISH.md").write_text("\n".join(lines), encoding="utf-8")
    return kit


# ---- CLI -----------------------------------------------------------------------
def _print_preflight(nn: str, miss: list[Missing]) -> None:
    if not miss:
        print(f"preflight EP{nn}: ready")
        return
    print(f"preflight EP{nn}: {len(miss)} missing")
    for m in miss:
        print(f"  step {m.step:>2}  {m.kind:<8} {m.path}")


def _print_qa(res: list[QA]) -> bool:
    ok = True
    for q in res:
        print(f"{q.id}: {q.width}x{q.height} {q.fps:g}fps {q.duration:.2f}s I={q.lufs} peak={q.peak}"
              + ("  OK" if not q.problems else "  FAIL: " + "; ".join(q.problems)))
        ok &= not q.problems
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["preflight", "qa", "kit", "all"])
    ap.add_argument("nn", help="two-digit episode number, e.g. 02")
    ap.add_argument("--langs", default="AR EN")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    nn = a.nn.zfill(2)
    langs = tuple(a.langs.split())
    if a.cmd in ("preflight", "all"):
        miss = preflight(nn, a.root)
        _print_preflight(nn, miss)
        if miss:
            return 1
        if a.cmd == "preflight":
            return 0
    if a.cmd == "all" and not a.no_render:
        subprocess.run(["bash", "scripts/render.sh", nn, " ".join(langs)], cwd=a.root, check=True)
    qa = None
    if a.cmd in ("qa", "all"):
        qa = run_qa(nn, langs, a.root)
        ok = _print_qa(qa)
        if a.cmd == "qa":
            return 0 if ok else 1
    kit = build_kit(nn, a.root, langs, qa)
    print(f"kit: {kit}/PUBLISH.md")
    return 0 if (qa is None or all(not q.problems for q in qa)) else 1


if __name__ == "__main__":
    sys.exit(main())
