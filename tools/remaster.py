"""Second master, OUTSIDE the engine — used only when the final QA fails on audio.

Why (EP11-EN, 2 Nov 2026): `scripts/render.sh` masters with single-pass loudnorm
(I=-14, TP=-1.5). After the AAC encode the true peak can land anywhere between
-1.5 and 0 dBTP, and it jumps ±0.8 dB with a 0.25 dB change of the voice level —
four EN renders all failed the -1.0 dBTP gate. A two-pass, linear loudnorm on the
SAME raw render with TP=-3 gave -14.0 LUFS / -2.3 dBTP in seconds.
Owner decision 2 Nov 2026 («اعتمد» = option 2). `render.sh` stays untouched.

Trim pass (4 Nov 2026): when the audio is too hot for linear mode, loudnorm falls
back to DYNAMIC mode and can miss the target (a test signal landed -14.4 LUFS, one
run in ~20). The result is measured, and if it is more than 0.15 dB off, the second
pass is redone from the raw render with a small extra gain, capped so the true
peak stays at or under -1.5 dBTP.

Input : master-claude/out/raw/EPNN-L.mp4   (written by render.sh, untouched picture)
Output: master-claude/out/EPNN-L.mp4       (video copied, audio re-mastered)

    python3 tools/remaster.py 11 EN
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "master-claude"
TARGET_I, TARGET_TP, TARGET_LRA = -14.0, -3.0, 9
TRIM_TOLERANCE = 0.15   # dB: closer than this to TARGET_I, no trim
PEAK_CEILING = -1.5     # dBTP: a trim never pushes the true peak above this (QA gate is -1.0)


def parse_loudnorm_json(stderr: str) -> dict:
    """The JSON block loudnorm prints with print_format=json (last {...} in stderr)."""
    blocks = re.findall(r"\{[^{}]*\}", stderr, re.S)
    if not blocks:
        raise ValueError("loudnorm printed no measurement")
    return json.loads(blocks[-1])


def second_pass_filter(m: dict, i: float = TARGET_I, tp: float = TARGET_TP, lra: float = TARGET_LRA) -> str:
    return (f"loudnorm=I={i}:TP={tp}:LRA={lra}:linear=true"
            f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}")


def trim_gain(lufs: float | None, peak: float | None, target: float = TARGET_I) -> float:
    """Extra gain (dB) that brings a measured master onto the target, capped by PEAK_CEILING."""
    if lufs is None or peak is None:
        return 0.0
    g = target - lufs
    if abs(g) <= TRIM_TOLERANCE:
        return 0.0
    if g > 0:
        g = max(min(g, PEAK_CEILING - peak), 0.0)
    return round(g, 2)


def measure(path: Path) -> tuple[float, float]:
    """Integrated loudness (LUFS) and true peak (dBTP), same meter as the final QA."""
    from episode_factory import parse_ebur128  # local import: episode_factory imports this module
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return parse_ebur128(err)


def _encode(raw: Path, dst: Path, flt: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", flt,
                    "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dst)], check=True)


def remaster(raw: Path, out: Path, tp: float = TARGET_TP) -> None:
    first = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-vn",
         "-af", f"loudnorm=I={TARGET_I}:TP={tp}:LRA={TARGET_LRA}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True)
    flt = second_pass_filter(parse_loudnorm_json(first.stderr), tp=tp)
    tmp = out.with_suffix(".remaster.mp4")
    _encode(raw, tmp, flt)
    g = trim_gain(*measure(tmp))
    if g:
        _encode(raw, tmp, f"{flt},volume={g}dB")
    tmp.replace(out)


def remaster_episode(nn: str, lang: str, root: Path = ROOT) -> Path:
    vid = f"EP{nn}-{lang}"
    raw = root / "out" / "raw" / f"{vid}.mp4"
    if not raw.exists():
        raise FileNotFoundError(f"missing out/raw/{vid}.mp4 (render first)")
    out = root / "out" / f"{vid}.mp4"
    remaster(raw, out)
    return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: remaster.py NN AR|EN", file=sys.stderr)
        return 2
    print(f"remastered: {remaster_episode(args[0].zfill(2), args[1].upper())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
