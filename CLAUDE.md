# video-studio — قناة تعليم Claude (بلا وجه)

قناة تواصل اجتماعي تعلّم الجمهور العام استخدام Claude من المبتدئ إلى المحترف. المالك: مانع الفلاسي — يقرأ العربية المبسطة على الجوال؛ أي نص للصق يوضع في كتلة كود.

## قواعد القناة (إلزامية)
- لا وجه ولا صوت للمالك — تعليق صوتي بالذكاء الاصطناعي فقط.
- كل حلقة بالعربية الفصحى (لا لهجة خليجية) **ومعها** نسخة إنجليزية مطابقة.
- فيديو عمودي 9:16 (1080×1920) لـ TikTok و Reels و Snapchat.
- حركة مستمرة: مربعات وأسهم ومخططات متدفقة ومحادثات وعناوين متحركة — لا شرائح نصية ثابتة.
- لا تذكر أي جهة حكومية أو خاصة أو منظمة (أسماء منتجات Claude/Anthropic مسموحة)، ولا مواضيع العمل/المكتب.
- كل معلومة عن ميزة في Claude يجب أن تُراجع على صفحة رسمية من Anthropic وتُكتب في `sources`.
- معيار الجودة: أسلوب المونتاج السينمائي للحلقة الأولى التي اعتمدها المالك.
- أقل تكلفة: لا تصرف أرصدة مدفوعة (Higgsfield، vidIQ، ...) دون موافقة صريحة. النشر على المنصات يدوي دائماً.

## الهيكل
- `episodes/<id>.yaml` — الحلقات (الصيغة في `docs/EPISODE_FORMAT.md`)، و`episodes/backlog.yaml` — القائمة.
- `tools/validate_episode.py` — المدقق؛ `tools/content_check.py` — فحص الجهات والعمل واللهجة.
- `tests/` — pytest. شغّل `make check` قبل أي push.
- `docs/ROADMAP.md` و `docs/DEV_LOG.md` — الخطة والسجل (أضف إدخالاً مؤرخاً كل دورة).
- `video_studio.ipynb` — المحرك القديم على Colab (شرائح Pillow + gTTS + ffmpeg).
- فرع `edu-channel-template` — محرك Remotion سابق (`edu-channel/`) غير مدموج.

## سير العمل
- الفروع: `dev/<topic>` ← PR. لا push على main ولا merge.
- السكلز في `.claude/skills/`: الفيديو المبرمج `remotion-*`، الترجمة `remotion-captions`، المنهجية `brainstorming` → `writing-plans` → `executing-plans` → `verification-before-completion`.
- سكل `aviation-safety-video` من مشروع سابق (السلامة الجوية) — باقٍ كما هو، لا يُستخدم لهذه القناة.
