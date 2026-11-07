#!/usr/bin/env python3
"""Proof that EP01–EP05 never change while engine v2 (EP06+) evolves.

Owner order (1 Nov 2026): episodes from EP06 vary in style; earlier episodes stay exactly as approved.

  python3 tools/frozen_check.py            # static: v1 engine files unchanged, EP01–05 do not opt into v2
  python3 tools/frozen_check.py --render   # + renders 5 frames of each EP01–05 composition and compares
                                           #   the pixels with the approved reference (needs node, ~3 min)
  python3 tools/frozen_check.py --record   # (re)write the reference — only with the owner's approval
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "master-claude"
REF = Path(__file__).with_name("frozen_reference.json")
FROZEN_FILES = ["src/engine/Episode.tsx", "src/engine/types.ts", "src/engine/fonts.ts"]
FROZEN_EPISODES = ["01", "02", "03", "04", "05"]
FRAMES = [15, 120, 330, 560, 800]


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pixel_hash(png: Path) -> str:
    from PIL import Image

    im = Image.open(png).convert("RGB")
    return hashlib.sha256(im.tobytes()).hexdigest()


def static_problems(ref: dict) -> list[str]:
    out = []
    for rel, h in ref["files"].items():
        p = MC / rel
        if not p.exists():
            out.append(f"{rel}: missing")
        elif file_hash(p) != h:
            out.append(f"{rel}: changed (engine v1 is frozen — put changes in src/engine2/)")
    for nn in FROZEN_EPISODES:
        ts = MC / "src" / "episodes" / f"ep{nn}.ts"
        if ts.exists() and "engine: 2" in ts.read_text(encoding="utf-8"):
            out.append(f"ep{nn}.ts opts into engine v2 — EP01–05 must stay on v1")
    return out


def render(bundle: Path, comp: str, frame: int, out: Path) -> None:
    subprocess.run(["npx", "remotion", "still", str(bundle), comp, str(out), f"--frame={frame}", "--log=error"],
                   cwd=MC, check=True, capture_output=True)


def render_hashes(tmp: Path) -> dict[str, str]:
    bundle = tmp / "bundle"
    subprocess.run(["npx", "remotion", "bundle", "src/index.ts", "--out-dir", str(bundle)], cwd=MC, check=True, capture_output=True)
    hashes = {}
    for nn in FROZEN_EPISODES:
        for lang in ("AR", "EN"):
            comp = f"EP{nn}-{lang}"
            for f in FRAMES:
                png = tmp / f"{comp}_{f}.png"
                render(bundle, comp, f, png)
                hashes[f"{comp}@{f}"] = pixel_hash(png)
    return hashes


def main(argv: list[str]) -> int:
    if "--record" in argv:
        ref = {"files": {rel: file_hash(MC / rel) for rel in FROZEN_FILES}}
        if "--from-dir" in argv:  # pre-rendered stills named EPNN-LANG_FRAME.png
            d = Path(argv[argv.index("--from-dir") + 1])
            ref["pixels"] = {f"{p.stem.split('_')[0]}@{p.stem.split('_')[1]}": pixel_hash(p) for p in sorted(d.glob("EP*_*.png"))}
        else:
            with tempfile.TemporaryDirectory() as t:
                ref["pixels"] = render_hashes(Path(t))
        REF.write_text(json.dumps(ref, indent=1, sort_keys=True) + "\n")
        print(f"reference written: {len(ref['files'])} files, {len(ref['pixels'])} frames")
        return 0
    ref = json.loads(REF.read_text())
    probs = static_problems(ref)
    if "--render" in argv and not probs:
        with tempfile.TemporaryDirectory() as t:
            got = render_hashes(Path(t))
        for k, h in ref["pixels"].items():
            if got.get(k) != h:
                probs.append(f"{k}: pixels differ from the approved render")
        print(f"rendered {len(got)} frames of EP01–05")
    for p in probs:
        print("FAIL", p)
    print("frozen check:", "OK" if not probs else f"{len(probs)} problem(s)")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
