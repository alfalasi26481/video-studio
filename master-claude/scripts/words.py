#!/usr/bin/env python3
"""Step 2 — Word timings from a voiceover (faster-whisper, model 'small').

  pip install --break-system-packages faster-whisper
  python3 scripts/words.py public/vo/ep03_ar.wav ar work/ep03_ar_words.json

Prints "t:word" for every word — use it to set the cues in episodes/epNN.ts.
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

wav, lang, out = sys.argv[1], sys.argv[2], sys.argv[3]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(audio, language=lang, word_timestamps=True)
words = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
json.dump(words, open(out, 'w'), ensure_ascii=False)
print(' '.join(f'{a}:{t}' for a, _, t in words))
