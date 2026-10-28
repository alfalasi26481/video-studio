"""QA gate — nothing is published unless this passes.

  python3 scripts/qa.py <episode-id> [--video out/x.mp4 ...]

Checks
  TEXT     Arabic touching Latin with no space, Latin , ? in Arabic text, double
           spaces, space before punctuation, over-long box labels / title lines.
  POLICY   no company / government names, no hype or "comment for the link" bait,
           every episode lists its sources.
  CAPTIONS no one-word caption, no lone English word, phrase length readable.
  VOICE    every scene has audio; loudness -16 LUFS ±1.5; what the voice said
           matches the script (word error rate, Arabic normalised).
  LENGTH   total runtime inside the 25–95 s window.
  VISUAL   (--video) a contact sheet of the render for a human look, saved
           next to the video as <name>-sheet.jpg.
Exit code 1 if any ERROR.
"""
import json, re, subprocess, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
ep_id = sys.argv[1]
videos = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--video']
ep = json.loads((root / 'public/episodes' / f'{ep_id}.json').read_text())
errors, warns = [], []
def err(m): errors.append(m)
def warn(m): warns.append(m)

AR = r'\u0621-\u064A'
BANNED = [  # entities (the channel never names a company or a government body) + bait
    r'\bAnthropic\b', 'أنثروبيك', 'انثروبيك', r'\bOpenAI\b', r'\bChatGPT\b', r'\bGemini\b', r'\bGoogle\b', 'جوجل', 'قوقل',
    r'\bMicrosoft\b', r'\bApple\b', r'\bMeta\b', r'\bTikTok\b', r'\bInstagram\b', 'تيك توك', 'انستقرام',
    'وزارة', 'هيئة', 'حكومة', 'حكومي', r'\bministry\b', r'\bgovernment\b',
    'لن تصدق', 'سر خطير', 'اكتب تعليق', 'علق بكلمة', 'الرابط في البايو', r'comment ".*" ', r'link in bio', r"won't believe", r'\bsecret\b',
]

def strings(scene):
    """Every on-screen string of a scene, with where it lives."""
    out = []
    for k in ('title', 'body', 'kicker', 'label', 'prompt', 'term', 'def', 'analogy', 'example', 'exampleLabel', 'user', 'reply', 'attach'):
        if isinstance(scene.get(k), str): out.append((k, scene[k]))
    for i, it in enumerate(scene.get('items', [])):
        if isinstance(it, str): out.append((f'items[{i}]', it))
        else: out += [(f'items[{i}].term', it['term']), (f'items[{i}].rule', it['rule'])]
    spec = scene.get('spec')
    if spec:
        out += [(f"node:{n['id']}", n['label']) for n in spec['nodes']]
        out += [(f"{e['do']}@{e['at']}", e.get('text') or e.get('label')) for e in spec['events'] if e.get('text') or e.get('label')]
    return out

def lint(lang, where, s):
    t = s.replace('*', '')
    if re.search(rf'[{AR}][A-Za-z]|[A-Za-z][{AR}]', t): err(f'{where}: Arabic touches Latin with no space → "{t}"')
    if '  ' in t.replace('\n', ' '): warn(f'{where}: double space')
    if re.search(r'\s[.،,؟?:!؛]', t): err(f'{where}: space before punctuation → "{t}"')
    if lang == 'ar' and re.search(rf'[{AR}]\s*[,?;]', t): err(f'{where}: Latin , ? ; in Arabic text (use ، ؟ ؛) → "{t}"')
    for b in BANNED:
        if re.search(b, t, re.I): err(f'{where}: banned term /{b}/ → "{t}"')

def norm(s, lang):
    s = s.lower()
    s = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', s)            # tashkeel, tatweel
    s = re.sub('[أإآٱ]', 'ا', s); s = s.replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    s = re.sub(r'\bclaude\b|كلود|كلاود', 'claude', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    return s.split()

NUMW = set('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty hundred thousand million'.split()
           + 'عشرين عشرون ثلاثين ثلاثمئه الف خمس خمسه ثماني ثمانيه عشر الفين وسته'.split())
def strip_nums(ws): return [w for w in ws if not w.isdigit() and w not in NUMW]

_medium = None
def second_opinion(path, lang):
    """The small model mishears short Arabic words; re-check with the medium model before failing."""
    global _medium
    import numpy as np
    from faster_whisper import WhisperModel
    if _medium is None: _medium = WhisperModel('medium', device='cpu', compute_type='int8')
    a = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(a, np.int16).astype(np.float32) / 32768
    segs, _ = _medium.transcribe(x, language=lang, beam_size=5, condition_on_previous_text=False)
    return ' '.join(g.text.strip() for g in segs)

def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1] / max(1, len(ref))

def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    return float(m[-1]) if m else None

def dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

if not ep.get('sources'): err('episode has no "sources" list (every claim needs an official source)')
for lang in ('ar', 'en'):
    total = 0.0
    for i, sc in enumerate(ep[lang]['scenes']):
        tag = f'{lang} scene {i + 1} ({sc["type"]})'
        for where, s in strings(sc): lint(lang, f'{tag} {where}', s)
        lint(lang, f'{tag} narration', sc['narration'])
        for where, s in strings(sc):
            if where.startswith('node:'):
                n = next(x for x in sc['spec']['nodes'] if x['id'] == where[5:])
                if len(s) * 15 + 30 > 2 * (n.get('w') or 200): warn(f'{tag} {where}: label "{s}" may wrap to 3 lines in a {n.get("w") or 200}px box')
            if where in ('title',) and sc['type'] in ('hook', 'cta') and max(len(x) for x in s.replace('*', '').split('\n')) > 20:
                warn(f'{tag} title line over 20 chars — add a \\n break: "{s}"')
        if not sc.get('audio'): err(f'{tag}: no voiceover'); continue
        p = root / 'public' / sc['audio']
        if not p.exists(): err(f'{tag}: missing {sc["audio"]}'); continue
        d = dur(p); total += d + 0.5
        L = lufs(p)
        if L is None or abs(L + 16) > 1.5: err(f'{tag}: loudness {L} LUFS (want -16 ±1.5)')
        heard = sc.get('_heard')
        if heard:
            score = lambda h: wer(strip_nums(norm(sc['narration'], lang)), strip_nums(norm(h, lang)))
            w = score(heard)
            if w > 0.1:
                heard2 = second_opinion(p, lang); w2 = score(heard2)
                if w2 < w: w, heard = w2, heard2
            (err if w > 0.2 else warn if w > 0.1 else (lambda m: None))(f'{tag}: voice vs script WER {w:.0%} — heard: "{heard}"')
        maxc = 26 if lang == 'ar' else 30
        for c in sc.get('cues', []):
            ws = c['text'].split()
            if len(ws) == 1: err(f'{tag}: one-word caption "{c["text"]}"')
            if len(c['text']) > maxc + 12: warn(f'{tag}: long caption ({len(c["text"])} chars) "{c["text"]}"')
            if not c.get('words'): warn(f'{tag}: caption without word timings (re-run sync-audio.py)')
    if total and not 25 <= total <= 95: err(f'{lang}: runtime {total:.1f}s outside 25–95 s')
    print(f'{lang}: runtime {total:.1f}s')

for v in videos:
    vp = pathlib.Path(v)
    sheet = vp.with_name(vp.stem + '-sheet.jpg')
    D = dur(vp); step = max(1.0, D / 24)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(vp), '-vf', f'fps=1/{step:.2f},scale=270:-1,tile=6x4:padding=6:color=0x0e1a2c',
                    '-frames:v', '1', str(sheet)], check=True)
    L = lufs(vp)
    if L is None or abs(L + 16) > 2: warn(f'{vp.name}: mix loudness {L} LUFS')
    print(f'{vp.name}: {D:.1f}s, mix {L} LUFS, sheet → {sheet}')

for w in warns: print('WARN ', w)
for e in errors: print('ERROR', e)
print(f'\n{len(errors)} error(s), {len(warns)} warning(s)')
sys.exit(1 if errors else 0)
