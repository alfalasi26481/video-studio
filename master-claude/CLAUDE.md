# أتقن Claude / Master Claude — محرك الحلقات المعتمد

هذا المجلد هو **المصدر الوحيد** لمونتاج حلقات القناة. أي حلقة جديدة تُنتج بهذا المحرك كما هو، حتى تخرج كل الحلقات بنفس المستوى المعتمد بالضبط (منذ الحلقة 1، 28 أكتوبر 2026).

## قواعد ملزمة

1. **لا تبنِ مونتاجاً جديداً، ولا تعدّل التصميم.** لا تغيّر `src/engine/Episode.tsx` ولا `src/engine/types.ts` ولا `scripts/music.py` ولا إعدادات `scripts/render.sh`. الحلقة الجديدة = ملف بيانات جديد فقط.
2. **تعديل المحرك يكون بطلب صريح من صاحب القناة**، وبعد موافقته على لقطات ثابتة (stills) تقارن قبل وبعد. إذا احتاجت حلقة نوع مشهد غير موجود، اقترحه أولاً ولا تضفه من نفسك.
3. **قواعد المحتوى:**
   - بدون وجه وبدون صوت صاحب القناة.
   - لا ذكر لأي جهة أو قطاع حكومي أو خاص أو شركة.
   - لا مواضيع عن العمل أو الوظيفة.
   - عربية فصحى مبسطة (لا لهجة)، وكل حلقة عربية لها نسخة إنجليزية مطابقة.
   - أي ميزة في Claude تُذكر يجب أن تكون موجودة فعلاً.
4. **التكلفة:** أخبر صاحب القناة بتكلفة Higgsfield قبل توليد اللقطات (Kling 4.0 = 16.25 رصيداً للقطة، 3 لقطات لكل حلقة).
5. **الردود** بالعربي المبسط، والروابط مباشرة، وأي نص يحتاج لصقه في بلوك جاهز للنسخ.

## التجهيز (مرة واحدة لكل جلسة)

```bash
cd master-claude
npm ci || npm install
npx remotion browser ensure
pip install --break-system-packages faster-whisper numpy
npx remotion compositions src/index.ts   # يجب أن تظهر EP01-AR … بنفس المدد
```

## إنتاج حلقة جديدة (NN = رقم الحلقة بخانتين)

| # | الخطوة | الأمر / الأداة |
|---|---|---|
| 1 | **السكربت** عربي + إنجليزي، 25-35 ثانية: افتتاحية «توقف!» ← المشكلة ← الحل ← قبل/بعد ← احفظ وتابع | اكتبه في `episodes/epNN.md` (انسخ `episodes/ep02.md`) |
| 2 | **الصوت** للغتين بالتوازي | Composio `GEMINI_GENERATE_CONTENT`، model `gemini-2.5-pro-preview-tts`، voice `Charon`، مع البادئة الثابتة (في `scripts/voice.py`). احفظ `audio_data` ثم: `python3 scripts/voice.py b64.txt public/vo/epNN_ar.wav` |
| 3 | **توقيت الكلمات** | `python3 scripts/words.py public/vo/epNN_ar.wav ar work/epNN_ar_words.json` (وكذلك en) |
| 4 | **بيانات الحلقة** | انسخ `src/episodes/ep01.ts` (معادلة/خطوات) أو `ep02.ts` (جملة سحرية + أسئلة) إلى `epNN.ts`. ضع النصوص، و`voiceDur` من ffprobe، و`cues` من توقيت الكلمات. سجّلها في `src/episodes/index.ts` |
| 5 | **الترجمة** | اكتب `work/epNN_ar_lines.json` ثم `python3 scripts/captions.py work/epNN_ar_words.json work/epNN_ar_lines.json <voiceDur> src/episodes/epNN_words_ar.json` |
| 6 | **اللقطات** 3 جديدة: افتتاحية، وسط مرتبط بالموضوع، ذروة النتيجة | Higgsfield `generate_video_batch`، model `kling4_0`، `aspect_ratio 9:16`، `resolution 1080p`، `duration 5`. البرومبت ينتهي دائماً بـ `cinematic, no text, no people`. احفظها في `public/clips/epNN_*.mp4`. الـ glitch والخاتمة تُعاد من الحلقة 1 |
| 7 | **الموسيقى** | `python3 scripts/music.py public/music/epNN_ar.wav <formula> <diff> <cta> <voiceDur+1.2>` (وكذلك en بتوقيتاتها) |
| 8 | **فحص قبل الرندر** | `bash scripts/check.sh NN AR stills` ثم انظر للصورة وأصلح أي قص أو تداخل |
| 9 | **الرندر + الماستر** | `bash scripts/render.sh NN` ← `out/EPNN-AR.mp4` و`out/EPNN-EN.mp4` |
| 10 | **فحص نهائي** | `bash scripts/check.sh NN AR final` (وكذلك EN). يجب: -14 LUFS (±0.3)، ذروة أقل من -1 dBTP، 1080×1920، 30fps |
| 11 | **التسليم** | الملفان + تعليق النشر باللغتين من `episodes/epNN.md`. اعمل commit لملفات الحلقة (عدا `out/` و`work/`) |

## قائمة فحص الجودة

- [ ] الافتتاحية مفهومة بدون صوت في أول 3 ثوانٍ
- [ ] لا كلمة مقطوعة عند حافة بطاقة أو صندوق (النص الإنجليزي أطول عادة: اختصره)
- [ ] الحروف العربية متصلة، وترتيب RTL صحيح، والترجمة متزامنة كلمة بكلمة
- [ ] النصوص أعلى من 20% السفلية، وبعيدة عن الجانب الأيمن
- [ ] نقاط `cues.steps` تطابق لحظة نطق كل خطوة، والـ Drop يقع على `formula`
- [ ] النسخة الإنجليزية مطابقة للعربية في المعنى والترتيب

## أنواع المشهد الثالث المتاحة

- **معادلة/خطوات** (الحلقة 1): 3 أو 4 بطاقات، كل بطاقة `label` + `ex`.
- **جملة سحرية** (الحلقة 2): `magic: {line, at, asks, asksAt}` + بطاقات مضغوطة (`ex: ''`) + `chips` في النتيجة.

## الملفات

```
src/engine/Episode.tsx   المحرك (5 مشاهد + كاميرا + انتقالات + كاريوكي + مؤثرات)  — لا يُعدّل
src/engine/types.ts      الألوان والأنواع                                          — لا يُعدّل
src/engine/fonts.ts      Tajawal + Inter محلياً
src/episodes/epNN.ts     بيانات كل حلقة  ← هنا فقط تعمل
src/episodes/index.ts    سجل الحلقات
public/clips|vo|music|sfx|fonts
scripts/                 voice · words · captions · music · check · render
episodes/epNN.md         السكربت + برومبتات اللقطات + تعليق النشر
```
