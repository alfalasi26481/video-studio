#!/usr/bin/env python3
"""Step 3 — Build karaoke caption JSON (src/episodes/epNN_words_LANG.json).

  python3 scripts/captions.py work/ep03_ar_words.json work/ep03_ar_lines.json 27.81 src/episodes/ep03_words_ar.json

lines.json = [[start_seconds, "caption line exactly as shown on screen"], ...]
  - one line per spoken sentence/phrase, short (fits 2 lines on screen)
  - write Claude in Latin letters on screen; "توقف!" style punctuation allowed
The last arg before output = voiceover duration (ffprobe).
Each on-screen word gets the time of the matching spoken word when counts match,
otherwise words are spread evenly across the spoken span.
"""
import json, sys

W = json.load(open(sys.argv[1]))
lines = json.load(open(sys.argv[2]))
end_all = float(sys.argv[3])
out = []
for i, (st, txt) in enumerate(lines):
    en = lines[i + 1][0] if i + 1 < len(lines) else end_all
    ww = [w for w in W if st - 0.15 <= w[0] < en - 0.1]
    toks = txt.split()
    if ww and len(ww) == len(toks):
        times = [w[0] for w in ww]
    elif ww:
        a, b = ww[0][0], ww[-1][1]
        times = [a + (b - a) * k / len(toks) for k in range(len(toks))]
    else:
        times = [st + 0.25 * k for k in range(len(toks))]
    out.append({'start': st, 'end': en, 'words': [[round(t, 2), tok] for t, tok in zip(times, toks)]})
json.dump(out, open(sys.argv[4], 'w'), ensure_ascii=False)
print(f'{len(out)} caption lines -> {sys.argv[4]}')
