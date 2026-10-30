#!/usr/bin/env python3
"""Step 1 — Convert Gemini TTS raw PCM (base64, 24 kHz, 16-bit mono) to WAV.

Voice is generated with Composio tool GEMINI_GENERATE_CONTENT:
  model = gemini-2.5-pro-preview-tts, voice_name = Charon (both languages)
The tool returns data.audio_data (base64 PCM). Save that string to a file, then:

  python3 scripts/voice.py audio_b64.txt public/vo/ep03_ar.wav

Voice prompt prefixes (fixed — do not change):
  AR: اقرأ بالعربية الفصحى، بصوت رجالي واثق وحماسي، بإيقاع سريع مناسب لفيديو قصير، مع وقفة قصيرة بين الجمل:
  EN: Read in a confident, energetic male voice, fast pacing suitable for a short video, with brief pauses between sentences:
In the Arabic spoken text write "كلود" (not "Claude") so it is pronounced correctly.
"""
import base64, sys, wave

src, dst = sys.argv[1], sys.argv[2]
pcm = base64.b64decode(open(src).read().strip())
with wave.open(dst, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
print(f'{dst}: {len(pcm) / 48000:.2f}s')
