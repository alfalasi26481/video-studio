#!/usr/bin/env python3
"""Step 4 — Original music (no copyright), timed to the episode cues. Deterministic.

  python3 scripts/music.py public/music/ep03_ar.wav <formula> <diff> <cta> <total>

formula/diff/cta = the same cue seconds as in episodes/epNN.ts; total = voiceDur + 1.2
112 BPM electronic, Am-F-C-G: quiet intro -> snare roll -> DROP exactly at `formula`
-> short break before `diff` -> DROP 2 -> calm outro. Do not change the sound design.
"""
import sys, wave
import numpy as np

out_path = sys.argv[1]
formula, diff, cta, total = map(float, sys.argv[2:6])
SR = 44100
BPM = 112
beat = 60 / BPM
N = int(SR * (total + 0.5))
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)

def note(m):
    return 440 * 2 ** ((m - 69) / 12)

def add(start, sig, pan=0.0, gain=1.0):
    i = int(round(start * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * l * gain
    mix[i:i + len(sig), 1] += sig * r * gain

def onepole(x, cutoff):
    # vectorised-ish one pole via lfilter equivalent
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc = (1 - a) * x[k] + a * acc
        y[k] = acc
    return y

def env(n, a, d, sl, r):
    e = np.full(n, sl, dtype=float)
    na, nd, nr = max(1, int(a * SR)), max(1, int(d * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, sl, len(e[na:na + nd]))
    e[-nr:] *= np.linspace(1, 0, nr)
    return e

prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
roots = [45, 41, 36, 43]
bar = 4 * beat

def section(t):
    if t < formula - 0.02:
        return 'intro'
    if t < diff - beat - 0.02:
        return 'drop'
    if t < diff - 0.02:
        return 'break'
    if t < cta - 0.02:
        return 'drop2'
    return 'outro'

# beat grid anchored at formula
first = int(np.floor(-formula / beat))
last = int(np.ceil((total - formula) / beat))

# --- PAD (per bar, always) ---
for bi in range(int(np.floor(first / 4)), int(np.ceil(last / 4)) + 1):
    t0 = formula + bi * bar
    if t0 + bar < 0 or t0 > total:
        continue
    ch = prog[bi % 4]
    n = int((bar + 0.5) * SR)
    tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in ch:
        f = note(m)
        for det in (-0.15, 0.15):
            sig += 0.5 * np.sin(2 * np.pi * f * (1 + det / 100) * tt) + 0.16 * np.sin(2 * np.pi * 2 * f * (1 + det / 100) * tt)
    sec = section(max(0, t0))
    g = {'intro': 0.05, 'drop': 0.04, 'break': 0.05, 'drop2': 0.045, 'outro': 0.06}[sec]
    add(t0, sig * env(n, 0.3, 0.3, 0.85, 0.5) * g)

# --- per-beat elements ---
kick_n = int(0.4 * SR)
tk = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * (46 * tk + 130 / 28 * (1 - np.exp(-tk * 28)))) * np.exp(-tk * 7.5) * 0.7
clap_n = int(0.2 * SR)
clap = rng.standard_normal(clap_n)
clap = onepole(clap, 4000) - onepole(clap, 900)
clap *= np.exp(-np.arange(clap_n) / SR * 20) * 0.22
hat_n = int(0.05 * SR)
hat = rng.standard_normal(hat_n)
hat = hat - onepole(hat, 7500)
hat *= np.exp(-np.arange(hat_n) / SR * 80) * 0.07
snare_n = int(0.12 * SR)
snare = rng.standard_normal(snare_n)
snare = onepole(snare, 6000) - onepole(snare, 1500)
snare *= np.exp(-np.arange(snare_n) / SR * 30) * 0.14

kick_times = []
for k in range(first, last + 1):
    t = formula + k * beat
    if t < 0 or t > total:
        continue
    sec = section(t)
    bi = int(np.floor(k / 4))
    if sec in ('drop', 'drop2'):
        add(t, kick)
        kick_times.append(t)
        if k % 2 == 1:
            add(t, clap, 0.05)
        add(t + beat / 2, hat, 0.3)
        add(t + beat / 4, hat * 0.5, -0.3)
        add(t + 3 * beat / 4, hat * 0.5, -0.3)
        # bass (off-beat pumping)
        f = note(roots[bi % 4])
        n = int(beat * 0.45 * SR)
        tt = np.arange(n) / SR
        saw = 2 * ((f * tt) % 1) - 1
        b = onepole(saw, 500) * env(n, 0.005, 0.08, 0.6, 0.05) * 0.32
        add(t + beat / 2, b)
    elif sec == 'intro':
        # ticking hats only in the second half of intro
        if t > formula * 0.35:
            add(t + beat / 2, hat * 0.7, 0.3)
    elif sec == 'outro':
        if k % 2 == 0:
            add(t, kick * 0.6)
        add(t + beat / 2, hat * 0.6, 0.3)

    # arp 8ths
    if sec != 'break':
        ch = [m + 12 for m in prog[bi % 4]]
        pat = [0, 1, 2, 1]
        for h in range(2):
            m = ch[pat[(2 * (k % 2) + h) % 4]] + (12 if sec == 'drop2' and h == 1 else 0)
            f = note(m)
            n = int(0.3 * SR)
            tt = np.arange(n) / SR
            saw = 2 * ((f * tt) % 1) - 1
            cutoff = {'intro': 900 + 2200 * max(0, t / formula), 'drop': 3200, 'drop2': 4200, 'outro': 1600}[sec]
            sig = onepole(saw, cutoff) * np.exp(-tt * 10)
            g = {'intro': 0.05, 'drop': 0.07, 'drop2': 0.075, 'outro': 0.05}[sec]
            add(t + h * beat / 2, sig * g, pan=0.4 if h else -0.4)

# snare roll build into formula (last 2 beats) and into diff
for target, beats_n in ((formula, 2), (diff, 1)):
    steps = beats_n * 4
    for i in range(steps):
        t = target - beats_n * beat + i * beat / 4
        if t >= 0:
            add(t, snare * (0.35 + 0.65 * i / steps), 0)

# sidechain ducking
duck = np.ones(N)
for kt in kick_times:
    i = int(kt * SR)
    n = int(0.22 * SR)
    seg = np.linspace(0.5, 1, n)
    e = min(N, i + n)
    duck[i:e] = np.minimum(duck[i:e], seg[: e - i])
mix *= duck[:, None]

fi = int(0.5 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(2.0 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.5)
mix /= np.max(np.abs(mix)) * 1.1
out = (mix * 32767).astype(np.int16)
with wave.open(out_path, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print('music ->', out_path)
