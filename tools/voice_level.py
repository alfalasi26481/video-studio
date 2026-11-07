#!/usr/bin/env python3
"""Bring a TTS voice file to the engine's reference level BEFORE render (outside the engine).

Why: render.sh masters with single-pass loudnorm (I=-14, TP=-1.5). A voice that comes out of
Gemini quiet but peaky (e.g. EP04-AR: -21.1 LUFS, peak -1.8) makes the final master miss the
QA gate (-14.4 LUFS, peak -1.0). Reference = EP03-AR's voice, which passed: -19.6 LUFS / -2.1 dBTP.

  python3 tools/voice_level.py master-claude/public/vo/ep04_ar.wav            # report only (never fails)
  python3 tools/voice_level.py master-claude/public/vo/ep04_ar.wav --fix      # two-pass loudnorm in place

Use --fix only when `make episode` final QA fails on loudness/peak: the approved voices range
-21.2…-18.1 LUFS and still pass, because the final level depends on the music mix too, so this is
a repair helper, not a gate. Duration, sample rate and channels are kept.
"""
import argparse
import json
import re
import subprocess
import sys

TARGET_I = -19.6
TARGET_TP = -2.1
TOL_I = 1.0  # LUFS


def measure(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return parse_ebur128(out)


def parse_ebur128(text):
    tail = text[text.rfind("Summary:"):] if "Summary:" in text else text
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    if not i or not p:
        raise ValueError("no ebur128 summary")
    peak = float("-inf") if p.group(1) == "-inf" else float(p.group(1))
    return float(i.group(1)), peak


def verdict(i, tp, target_i=TARGET_I, target_tp=TARGET_TP, tol=TOL_I):
    problems = []
    if abs(i - target_i) > tol:
        problems.append(f"loudness {i:.1f} LUFS (want {target_i}±{tol})")
    if tp > target_tp + 0.3:
        problems.append(f"peak {tp:.1f} dBTP (want ≤ {target_tp})")
    return problems


def fix(path):
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels",
                           "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip().split(",")
    flt = f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=11"
    first = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", flt + ":print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    d = json.loads(first[first.rfind("{"):first.rfind("}") + 1])
    second = (f"{flt}:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
              f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-af", second, "-ar", rate[0], "-ac", rate[1], tmp], check=True)
    import os
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for f in a.files:
        if a.fix:
            fix(f)
        i, tp = measure(f)
        probs = verdict(i, tp)
        print(f"{f}: {i:.1f} LUFS, peak {tp:.1f}" + ("  (off reference: " + "; ".join(probs) + ")" if probs else "  at reference"))
        bad += bool(probs)
    return 1 if (a.fix and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
