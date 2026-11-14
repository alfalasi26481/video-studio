#!/usr/bin/env python3
"""Cue check — scene cues in master-claude/src/episodes/epNN.ts agree with the voice.

Read-only, outside the engine. For every exported episode (AR and EN):
  - cues are in speaking order: problem < typeAt < badAt < formula < steps... < diff < cta
  - the last cue (cta) comes before voiceDur, and the karaoke lines end by voiceDur
  - caption line starts increase
  - (warning only) every cue except typeAt is within ALIGN s of a caption line start;
    a cue far from any line start cuts the scene mid-sentence — fine when deliberate
    (EP07/EP10 drop badAt on a keyword), worth a look when typed by hand

Episodes approved before this check (EP01–EP12) report warnings only.

  python3 tools/cue_check.py          # all episodes
  python3 tools/cue_check.py 13       # one episode
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPS = ROOT / 'master-claude' / 'src' / 'episodes'
TOL = 0.05
ALIGN = 0.15
LEGACY_MAX = 12  # approved before this check (3 Nov 2026)
ORDER = ['problem', 'typeAt', 'badAt', 'formula', 'steps', 'diff', 'cta']


def parse_ts(text):
    """Return [(name, lang, voiceDur, cues, words_file)] for each exported episode."""
    imports = dict(re.findall(r"import (\w+) from '\./([\w.]+\.json)'", text))
    out = []
    for m in re.finditer(r'export const (\w+)\s*:\s*\w+\s*=\s*\{', text):
        body = text[m.end():]
        nxt = re.search(r'\nexport const ', body)
        body = body[:nxt.start()] if nxt else body
        lang = re.search(r"lang:\s*'(\w+)'", body)
        vd = re.search(r'voiceDur:\s*([\d.]+)', body)
        cm = re.search(r'cues:\s*\{(.*?)\}\s*,\s*\n', body, re.S)
        wm = re.search(r'words:\s*(\w+)', body)
        if not (lang and vd and cm):
            continue
        cues = {}
        for k, v in re.findall(r'(\w+):\s*(\[[^\]]*\]|[\d.]+)', cm.group(1)):
            cues[k] = json.loads(v) if v.startswith('[') else float(v)
        out.append((m.group(1), lang.group(1), float(vd.group(1)), cues,
                    imports.get(wm.group(1)) if wm else None))
    return out


def check_episode(cues, voice_dur, lines):
    """Pure check. lines = [{'start', 'end', 'words'}]. Returns (errors, warnings)."""
    errs, warns = [], []
    seq = []
    for k in ORDER:
        if k not in cues:
            continue
        v = cues[k]
        seq += [(f'steps[{i}]', float(x)) for i, x in enumerate(v)] if isinstance(v, list) else [(k, float(v))]
    for (a, ta), (b, tb) in zip(seq, seq[1:]):
        if not ta < tb:
            errs.append(f'order: {a}={ta} is not before {b}={tb}')
    if seq and seq[-1][1] >= voice_dur:
        errs.append(f'{seq[-1][0]}={seq[-1][1]} is not before voiceDur={voice_dur}')
    if lines:
        starts = [float(l['start']) for l in lines]
        for a, b in zip(starts, starts[1:]):
            if not a < b:
                errs.append(f'caption line starts not increasing: {a} then {b}')
        last = max((float(w[0]) for l in lines for w in l.get('words', [])), default=0.0)
        if last > voice_dur + TOL:
            errs.append(f'last caption word at {last} after voiceDur={voice_dur}')
        for name, t in seq:
            if name == 'typeAt':
                continue
            near = min(starts, key=lambda s: abs(s - t))
            if abs(near - t) > ALIGN:
                warns.append(f'{name}={t} is mid-sentence (nearest caption line {near})')
    return errs, warns


def main(argv):
    only = argv[1].zfill(2) if len(argv) > 1 else None
    n_err = n_warn = 0
    for ts in sorted(EPS.glob('ep[0-9][0-9].ts')):
        num = ts.stem[2:]
        if only and num != only:
            continue
        for name, lang, vd, cues, wf in parse_ts(ts.read_text(encoding='utf-8')):
            lines = json.loads((EPS / wf).read_text(encoding='utf-8')) if wf and (EPS / wf).exists() else []
            legacy = int(num) <= LEGACY_MAX
            errs, warns = check_episode(cues, vd, lines)
            for e in errs:
                tag = 'warning' if legacy else 'error'
                n_warn += legacy
                n_err += not legacy
                print(f'  [{tag}] {name}: {e}')
            for w in warns:
                n_warn += 1
                print(f'  [warning] {name}: {w}')
    print(f'cue check: {n_err} error(s), {n_warn} warning(s)')
    return 1 if n_err else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
