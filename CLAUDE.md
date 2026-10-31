# video-studio — قناة «أتقن Claude / Master Claude» (بلا وجه)

قناة تواصل اجتماعي تعلّم الجمهور العام استخدام Claude من المبتدئ إلى المحترف. المالك: مانع الفلاسي — يقرأ العربية المبسطة على الجوال؛ الروابط مباشرة، وأي نص للصق يوضع في كتلة كود.

## المحرك المعتمد (الأهم)
- **أي حلقة للقناة تُنتج بالمحرك المعتمد في `master-claude/` فقط** — اقرأ `master-claude/CLAUDE.md` أولاً (سكل `master-claude-episode`).
- لا تبنِ مونتاجاً جديداً، ولا تعدّل `master-claude/src/engine/` إلا بطلب صريح من المالك وبعد موافقته على لقطات قبل/بعد.

## قواعد القناة (إلزامية)
- لا وجه ولا صوت للمالك — تعليق صوتي بالذكاء الاصطناعي فقط.
- كل حلقة بالعربية الفصحى (لا لهجة خليجية) **ومعها** نسخة إنجليزية مطابقة.
- فيديو عمودي 9:16 (1080×1920) لـ TikTok و Reels و Snapchat.
- حركة مستمرة — لا شرائح نصية ثابتة.
- لا تذكر أي جهة حكومية أو خاصة أو منظمة (أسماء منتجات Claude/Anthropic مسموحة)، ولا مواضيع العمل/المكتب.
- كل معلومة عن ميزة في Claude يجب أن تُراجع على صفحة رسمية من Anthropic.
- معيار الجودة: المونتاج السينمائي للحلقتين 1 و2 المعتمدتين.
- أقل تكلفة: لا تصرف أرصدة مدفوعة (Higgsfield، vidIQ، ...) دون موافقة صريحة. النشر على المنصات يدوي دائماً.

## الهيكل
- `master-claude/` — المحرك المعتمد (Remotion) وحلقاته `episodes/epNN.md` و`src/episodes/epNN.ts`.
- `tools/engine_content_check.py` — يفحص نصوص حلقات المحرك (السكربت، الترجمة، تعليق النشر، نصوص الشاشة) ضد قواعد المحتوى.
- `tools/glyph_check.py` — يتأكد أن كل حرف على الشاشة موجود في خطوط المحرك (Tajawal/Inter، كل الأوزان) — `make glyph-check`.
- `tools/source_check.py` — كل `master-claude/episodes/epNN.md` يجب أن يحوي سطر «المصدر الرسمي (رُوجع <تاريخ>): <رابط>» من نطاق Anthropic رسمي (anthropic.com · claude.com · claude.ai)؛ مراجعة أقدم من 90 يوماً = تحذير — `make source-check` (ضمن `make check` و`make episode`).
- `tools/script_length.py` — مدة السكربت المنطوق قبل الصوت (تقدير بمعدل كلمات معاير من EP01/EP02) وبعده (`voiceDur`): 25–35 ث، والعربي ≈ الإنجليزي — `make script-length`.
- `tools/layout_check.py` (+ `tools/layout_check/`) — يقيس صناديق النص الحقيقية في Chromium إطاراً بإطار (المحرك يُستورد كما هو) ويفحص المناطق الآمنة والنص الخارج عن بطاقته أو عن الإطار — `make layout-check` (يحتاج node + playwright، ~1.5 دقيقة).
- `tools/episode_factory.py` — المصنع: `make episode NN=02` (فحص مسبق ← فحوص ← `render.sh` ← فحص نهائي ← حزمة تسليم في `master-claude/out/EPNN/`)؛ `make episode-preflight NN=..` يبيّن الناقص وأي خطوة تنتجه. لا يستدعي Higgsfield ولا ينشر.
- `tools/voice_level.py` — مستوى صوت التعليق مقابل مرجع EP03-AR (-19.6 LUFS)؛ أداة إصلاح لا بوابة: `make voice-level NN=04 FIX=1` فقط إذا فشل الفحص النهائي في الصوت (حدث في EP04-AR).
- `episodes/<id>.yaml` + `tools/validate_episode.py` + `tools/content_check.py` — صيغة YAML ومدققها (مسودات أفكار؛ الإنتاج يبقى بالمحرك).
- `tests/` — pytest. شغّل `make check` قبل أي push.
- `docs/ROADMAP.md` و `docs/DEV_LOG.md` — الخطة والسجل (أضف إدخالاً مؤرخاً كل دورة).
- `video_studio.ipynb` — المحرك القديم على Colab (لا يُستخدم للقناة).

## سير العمل
- الفروع: `dev/<topic>` ← PR. لا push على main ولا merge.
- السكلز في `.claude/skills/`: `master-claude-episode` للحلقات، `remotion-*` للمرجع، المنهجية `brainstorming` → `writing-plans` → `executing-plans` → `verification-before-completion`.
- المستندات: `docx` / `pptx` / `xlsx` / `pdf`.
- Higgsfield عبر MCP: الصور مجانية، الفيديو مدفوع — اطلب موافقة قبل أي `generate_video`.
- سكل `aviation-safety-video` من مشروع سابق (السلامة الجوية) — باقٍ كما هو، لا يُستخدم لهذه القناة.
