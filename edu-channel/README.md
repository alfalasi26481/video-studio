# قالب قناة تعليم Claude (Remotion)

فيديو عمودي 1080×1920 بنسختين عربية وإنجليزية من ملف واحد لكل حلقة.

## حلقة جديدة
1. انسخ `public/episodes/ep01.json` إلى `ep02.json` وعدّل المشاهد.
2. أنواع المشاهد: `hook` · `prompt` (tone: bad / good / tip) · `steps` · `cta`.
3. بعد توليد الصوت من ElevenLabs ضع كل مقطع في `public/ep02/` وأضف لكل مشهد:
   `"audio": "ep02/ar-1.mp3"` ← طول المشهد يُضبط على طول الصوت تلقائياً.
4. لتسجيل شاشة بدل الرسم: `"video": "ep02/screen-3.mp4"`.

## التشغيل على الماك
```bash
cd edu-channel
npm i
npx remotion studio
```

## الإخراج
```bash
npx remotion render Episode-ar out/ep02-ar.mp4 --props='{"id":"ep02","lang":"ar"}'
npx remotion render Episode-en out/ep02-en.mp4 --props='{"id":"ep02","lang":"en"}'
```

## مناطق آمنة
المحتوى بين 300 و1300 بكسل من الأعلى، والترجمة عند 1330، والهامش الأيمن 140 بكسل حتى لا تغطيه أزرار TikTok.
