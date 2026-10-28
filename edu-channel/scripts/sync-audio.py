"""Voiceover → word-timed karaoke captions.

For each scene clip public/<id>/<lang>-<n>.mp3 (raw TTS kept in public/<id>/raw/):
  1. tighten pacing (atempo) and normalise loudness to -16 LUFS,
  2. get word timestamps with faster-whisper,
  3. map the SCRIPT's words (scene.narration, what the viewer reads) onto the
     voice's word timings (the voice may read `scene.voice`: tashkeel, "كلود"),
  4. cut captions into phrases a viewer can read at a glance:
       - break at punctuation and at natural pauses in the voice (> 0.45 s),
       - at most ~26 characters (Arabic) / 30 (English) and 5 words,
       - never split a run of English words ("Claude Code"),
       - never leave one word alone on screen,
  5. write scene.audio + scene.cues (with per-word timings) into the episode JSON.
Usage: python3 scripts/sync-audio.py <episode-id> [tempo=1.0]
"""
import json, re, shutil, subprocess, sys, pathlib, wave
import numpy as np
from faster_whisper import WhisperModel

ep_id = sys.argv[1]
tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
only = sys.argv[3] if len(sys.argv) > 3 else None  # optional "ar" / "en"
root = pathlib.Path(__file__).resolve().parent.parent
pub = root / 'public' / ep_id
raw = pub / 'raw'; raw.mkdir(parents=True, exist_ok=True)
ep_path = root / 'public/episodes' / f'{ep_id}.json'
ep = json.loads(ep_path.read_text())
model = WhisperModel('small', device='cpu', compute_type='int8')

ARABIC = re.compile(r'[ء-ي]')
END = re.compile(r'[.،,؟?:!؛;]$')
def latin(w): return bool(re.search(r'[A-Za-z]', w)) and not ARABIC.search(w)

def word_times(script_words, voice_words):
    """Give every script word a (start, end) from the voice's words."""
    N, M = len(script_words), len(voice_words)
    out = []
    for i in range(N):
        a = i * M / N; b = (i + 1) * M / N
        ja, jb = int(a), min(M - 1, max(int(a), int(np.ceil(b)) - 1))
        wa, wb = voice_words[ja], voice_words[jb]
        # several script words on one voice word: split that word's time
        s = wa.start + (wa.end - wa.start) * (a - ja) if ja == jb else wa.start
        e = wa.start + (wa.end - wa.start) * min(1, b - ja) if ja == jb else wb.end
        out.append((round(s, 2), round(max(e, s + 0.05), 2)))
    return out

def phrases(words, times, maxc, maxw=5, mixed=True):
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        text = ' '.join(words[k] for k in cur)
        nxt = i + 1 < len(words)
        end_p = bool(END.search(w))
        gap = times[i + 1][0] - times[i][1] if nxt else 0
        long_next = nxt and len(text) + 1 + len(words[i + 1]) > maxc
        if end_p or gap > 0.45 or long_next or len(cur) >= maxw:
            if nxt and not end_p and mixed and latin(w) and latin(words[i + 1]) and len(text) < maxc + 10:
                continue  # keep "Claude Code" together inside Arabic
            if nxt and not end_p and (re.fullmatch(r'[\d.,+]+', w) or w in ('و', 'a', 'the', 'to', 'of', 'in', 'and')) and len(text) < maxc + 10:
                continue  # never end a line on a number or a joining word
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    # no orphans: a single word joins its neighbour
    i = 0
    while i < len(chunks):
        if len(chunks[i]) == 1 and len(chunks) > 1:
            w = words[chunks[i][0]]
            prev_ok = i > 0 and not END.search(words[chunks[i - 1][-1]]) and len(' '.join(words[k] for k in chunks[i - 1])) + len(w) <= maxc + 8
            if prev_ok or i == len(chunks) - 1:
                chunks[i - 1] += chunks[i]; del chunks[i]; continue
            chunks[i + 1] = chunks[i] + chunks[i + 1]; del chunks[i]; continue
        i += 1
    return chunks

class W:
    def __init__(s, word, start, end): s.word, s.start, s.end = word, start, end

def transcribe(a, lang, sr=16000, win=6.0):
    """Whisper can silently drop a whole sentence from a 15 s clip. Cut the
    clip at its quietest points into ~6 s windows and transcribe each."""
    hop = sr // 50
    rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, 'same'))[::hop]  # 20 ms frames
    cuts, t = [0], 0
    while t + win + 1.5 < len(a) / sr:  # never leave a sliver window at the end
        lo, hi = int((t + win - 2) * 50), int((t + win + 1) * 50)
        k = lo + int(np.argmin(rms[lo:hi]))
        cuts.append(k * hop); t = k / 50
    cuts.append(len(a))
    out = []
    for c0, c1 in zip(cuts, cuts[1:]):
        if c1 - c0 < sr // 3: continue
        try:
            segs, _ = model.transcribe(a[c0:c1], language=lang, word_timestamps=True, condition_on_previous_text=False, beam_size=5, temperature=0)
            segs = list(segs)
        except IndexError:  # whisper alignment bug on near-silent windows
            continue
        off = c0 / sr
        out += [W(x.word, x.start + off, x.end + off) for g in segs for x in g.words]
    return out

for lang in ('ar', 'en'):
    if only and lang != only: continue
    maxc = 26 if lang == 'ar' else 30
    for i, scene in enumerate(ep[lang]['scenes']):
        name = f'{lang}-{i + 1}.mp3'
        src = pub / name
        if not src.exists() and not (raw / name).exists():
            print('missing', name); continue
        if src.exists() and not (raw / name).exists(): shutil.move(src, raw / name)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw / name), '-af',
                        f'silenceremove=start_periods=1:start_threshold=-45dB,atempo={tempo},loudnorm=I=-16:TP=-1.5:LRA=11',
                        '-ar', '44100', str(src)], check=True)
        # single-pass loudnorm undershoots on short clips: measure, then correct the gain exactly
        r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
        I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])
        if abs(I + 16) > 0.3:
            tmp = src.with_suffix('.tmp.mp3')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', f'volume={-16 - I:.2f}dB,alimiter=limit=0.89',
                            '-ar', '44100', str(tmp)], check=True)
            tmp.replace(src)
        wav = raw / (name + '.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-ac', '1', '-ar', '16000', str(wav)], check=True)
        w = wave.open(str(wav)); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        voice_words = transcribe(a, lang)
        script_words = scene['narration'].split()
        times = word_times(script_words, voice_words)
        cues = []
        for ch in phrases(script_words, times, maxc, 5 if lang == 'ar' else 6, lang == 'ar'):
            cues.append({'text': ' '.join(script_words[k] for k in ch), 'start': times[ch[0]][0], 'end': times[ch[-1]][1],
                         'words': [{'t': script_words[k], 's': times[k][0], 'e': times[k][1]} for k in ch]})
        scene['audio'] = f'{ep_id}/{name}'
        scene['cues'] = cues
        scene['_heard'] = ' '.join(x.word.strip() for x in voice_words)  # for the QA gate (WER)
        print(lang, i + 1, f'{len(a)/16000:.1f}s', len(cues), 'cues |', ' / '.join(c['text'] for c in cues))
ep_path.write_text(json.dumps(ep, ensure_ascii=False, indent=1))
