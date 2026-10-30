"""Safe-zone + clipped-text check for episodes of the approved engine (master-claude/).

Roadmap item d (post-render QA), read-only. It does NOT edit the engine.

Two parts:
  1. tools/layout_check/measure.mjs  — opens each episode in Chromium (via
     @remotion/player <Thumbnail>, engine imported as-is), steps through the
     frames and records the box of every visible text line + the card it sits in.
  2. this file — applies the rules to those boxes (pure Python, unit-tested).

Rules (1080x1920 canvas; zones match the channel checklist in master-claude/CLAUDE.md):
  bottom      text inside the bottom 20% (y > 1536): covered by caption/UI on
              TikTok / Reels / Snapchat                              -> error
  right-rail  text in the right 120 px between 40% and 80% height (the like /
              comment / share column). Warning, not error: the column's exact
              width differs per platform/device (غير مؤكد), and the approved
              episodes 1–2 touch it by ~20–40 px                    -> warning
  top         text in the top 100 px (status bar + tabs)             -> warning
  off-canvas  text crosses the frame edge (word cut by the frame)    -> error
  spill       text sticks out of the card/box that holds it by > 4 px
              ("no word cut at the edge of a card or box")           -> error

Camera punches/shakes move everything for a few frames, so a finding only
counts when it holds on >= MIN_RUN consecutive sampled frames.

Usage:
    python3 tools/layout_check.py                 # all compositions (needs node + playwright)
    python3 tools/layout_check.py EP01-AR EP02-EN
    python3 tools/layout_check.py --json boxes.json   # rules only, on saved measurements
Exit code 1 when any error is found.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASURE_DIR = HERE / "layout_check"
ROOT = HERE.parent / "master-claude"

W, H = 1080, 1920
BOTTOM_Y = H * 0.80          # 1536
RIGHT_X = W - 120            # 960 (the engine's own captions keep right: 120)
RAIL_Y = (H * 0.40, H * 0.80)
TOP_Y = 100
SPILL_PX = 4
MIN_RUN = 2
EPS = 1.0                    # sub-pixel tolerance


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # "error" | "warning"
    text: str
    first_frame: int
    last_frame: int
    depth: float   # typical (median) px into the zone / out of the box over the run

    def line(self, fps: int = 30) -> str:
        a, b = self.first_frame / fps, self.last_frame / fps
        return f"[{self.severity}] {self.rule:<10} {a:5.1f}s–{b:5.1f}s  {self.depth:5.0f}px  «{self.text}»"


def _median(xs: list[float]) -> float:
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def frame_hits(t: dict) -> list[tuple[str, str, float]]:
    """Rule hits for one measured text line: [(rule, severity, depth_px)]."""
    x0, y0, x1, y1 = t["x0"], t["y0"], t["x1"], t["y1"]
    hits: list[tuple[str, str, float]] = []
    if y1 > BOTTOM_Y + EPS:
        hits.append(("bottom", "error", y1 - BOTTOM_Y))
    if x1 > RIGHT_X + EPS and y1 > RAIL_Y[0] and y0 < RAIL_Y[1]:
        hits.append(("right-rail", "warning", x1 - RIGHT_X))
    if y0 < TOP_Y - EPS:
        hits.append(("top", "warning", TOP_Y - y0))
    off = max(0.0, -x0, x1 - W, -y0, y1 - H)
    if off > EPS:
        hits.append(("off-canvas", "error", off))
    box = t.get("box")
    if box:
        bx0, by0, bx1, by1 = box
        spill = max(0.0, bx0 - x0, x1 - bx1, by0 - y0, y1 - by1)
        if spill > SPILL_PX:
            hits.append(("spill", "error", spill))
    return hits


def evaluate(measure: dict, min_run: int = MIN_RUN) -> list[Finding]:
    """Turn per-frame hits into findings that persist for >= min_run sampled frames."""
    frames = sorted(measure["frames"], key=lambda fr: fr["f"])
    # (rule, text) -> list of (frame_index, frame_no, severity, depth)
    seen: dict[tuple[str, str], list[tuple[int, int, str, float]]] = {}
    for i, fr in enumerate(frames):
        per_frame: dict[tuple[str, str], tuple[str, float]] = {}
        for t in fr["texts"]:
            for rule, sev, depth in frame_hits(t):
                key = (rule, t["t"])
                if key not in per_frame or depth > per_frame[key][1]:
                    per_frame[key] = (sev, depth)
        for key, (sev, depth) in per_frame.items():
            seen.setdefault(key, []).append((i, fr["f"], sev, depth))

    out: list[Finding] = []
    for (rule, text), hits in seen.items():
        run: list[tuple[int, int, str, float]] = []
        for h in hits + [(-99, 0, "", 0.0)]:  # sentinel flushes the last run
            if run and h[0] != run[-1][0] + 1:
                if len(run) >= min_run:
                    out.append(Finding(rule, run[0][2], text, run[0][1], run[-1][1], _median([r[3] for r in run])))
                run = []
            run.append(h)
    out.sort(key=lambda f: (f.severity != "error", f.first_frame, f.rule))
    return out


def _prepare() -> None:
    if not (MEASURE_DIR / "node_modules").exists():
        subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=MEASURE_DIR, check=True)
    subprocess.run(["node", "build.mjs"], cwd=MEASURE_DIR, check=True)


def measure(comp_id: str, step: int = 6) -> dict:
    """Browser measurement of one composition (call _prepare() first)."""
    res = subprocess.run(["node", "measure.mjs", comp_id, str(step)], cwd=MEASURE_DIR,
                         check=True, capture_output=True, text=True)
    return json.loads(res.stdout)


def all_compositions() -> list[str]:
    src = (ROOT / "src/episodes/index.ts").read_text(encoding="utf-8")
    import re
    return re.findall(r"'(EP\d+-(?:AR|EN))'\s*:", src)


def report(m: dict, findings: list[Finding]) -> bool:
    errs = [f for f in findings if f.severity == "error"]
    noise = [e for e in m.get("errors", []) if "MediaPlaybackError" not in e]
    head = f"{m['id']}: {len(m['frames'])} frames sampled (every {m.get('step', '?')})"
    print(f"{head} — {len(errs)} errors, {len(findings) - len(errs)} warnings")
    for e in noise:
        print(f"  [page-error] {e[:200]}")
    for f in findings:
        print("  " + f.line(m.get("fps", 30)))
    return not errs and not noise


def main(argv: list[str]) -> int:
    if argv[:1] == ["--json"]:
        ok = True
        for p in argv[1:]:
            m = json.loads(Path(p).read_text(encoding="utf-8"))
            ok &= report(m, evaluate(m))
        return 0 if ok else 1
    ids = argv or all_compositions()
    _prepare()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(measure, ids))
    ok = True
    for m in results:
        ok &= report(m, evaluate(m))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
