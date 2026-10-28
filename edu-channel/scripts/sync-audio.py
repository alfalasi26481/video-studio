"""Voiceover → timed captions.

For each scene clip public/<id>/<lang>-<n>.mp3 (raw TTS kept in public/<id>/raw/):
  1. tighten pacing (atempo) and normalise loudness,
  2. get word timestamps with faster-whisper,
  3. write scene.audio + scene.cues (caption chunks with start/end seconds)
     into public/episodes/<id>.json. Chunk text comes from the SCRIPT, timing from the audio.
Usage: python3 scripts/sync-audio.py ep02 [tempo]
"""
import json, re, shutil, subprocess, sys, pathlib, wave
import numpy as np
from faster_whisper import WhisperModel

ep_id = sys.argv[1]
tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.07
root = pathlib.Path(__file__).resolve().parent.parent
pub = root / 'public' / ep_id
raw = pub / 'raw'; raw.mkdir(exist_ok=True)
ep_path = root / 'public/episodes' / f'{ep_id}.json'
ep = json.loads(ep_path.read_text())
model = WhisperModel('small', device='cpu', compute_type='int8')

def chunks(text, per):
    out = []
    for phrase in re.split(r'(?<=[.،,؟?:!])\s+', text.strip()):
        w = phrase.split()
        if not w: continue
        n = -(-len(w) // per); size = -(-len(w) // n)
        out += [w[i:i + size] for i in range(0, len(w), size)]
    return out

for lang in ('ar', 'en'):
    per = 3 if lang == 'ar' else 4
    for i, scene in enumerate(ep[lang]['scenes']):
        name = f'{lang}-{i + 1}.mp3'
        src = pub / name
        if not src.exists() and not (raw / name).exists():
            print('missing', name); continue
        if not (raw / name).exists(): shutil.move(src, raw / name)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw / name), '-af',
                        f'atempo={tempo},loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '44100', str(src)], check=True)
        wav = raw / (name + '.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-ac', '1', '-ar', '16000', str(wav)], check=True)
        w = wave.open(str(wav)); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        segs, _ = model.transcribe(a, language=lang, word_timestamps=True)
        words = [x for s in segs for x in s.words]
        cs = chunks(scene['narration'], per)
        total = sum(len(c) for c in cs); M = len(words)
        cues, k = [], 0
        for c in cs:
            a_i = min(M - 1, round(k * M / total)); b_i = min(M - 1, max(a_i, round((k + len(c)) * M / total) - 1))
            cues.append({'text': ' '.join(c), 'start': round(words[a_i].start, 2), 'end': round(words[b_i].end, 2)})
            k += len(c)
        scene['audio'] = f'{ep_id}/{name}'
        scene['cues'] = cues
        print(lang, i + 1, f'{len(a)/16000:.1f}s', len(cues), 'cues')
ep_path.write_text(json.dumps(ep, ensure_ascii=False, indent=1))
