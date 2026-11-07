# سناب شات — «Limited Distribution» و«undisclosed AI-generated content» (1 نوفمبر 2026)

## ما ظهر للمالك (لقطات شاشة، حساب «سلّم Stepwise»)
1. «Reach More Viewers — It looks like your Post features **undisclosed AI-generated content**…» + رابط استئناف.
2. «Limited Distribution — It looks like your Post has a **content quality issue**…» (منشوران، أحدهما فيه «افتح claude.ai» على الشاشة).

## ما تقوله سناب نفسها
- [Content Guidelines for Recommendation Eligibility](https://snap.com/content-recommendation-guidelines) (نصاً):
  - «Our content ranking algorithm rewards authentic, human-made content over **wholly AI-generated content created outside of Snapchat, even when AI-generated content has transparency disclosures**.» · «AI-generated content that was created within Snapchat is eligible for recommendation.»
  - غير مؤهل للتوصية: «**Off-platform links (URLs, QR codes, etc.)**» · «Substandard Video Quality… letterboxed videos; or missing audio» · «**Flashes or strobes**. Intense visual effects without a warning for photosensitive users» · «Repeatedly posting the same content… with minimal creative difference».
- القرار معلن في 31 يوليو 2026 ([Engadget](https://www.engadget.com/2228152/snapchat-is-cracking-down-on-ai-slop-in-spotlight/)، [PPC Land](https://ppc.land/snap-blocks-ai-only-videos-from-spotlight-as-contributors-climb-120/)): يخص **توصية Spotlight** فقط؛ لا حذف ولا حظر للحساب. لم توضّح سناب هل التعليق الصوتي الاصطناعي وحده يكفي لاعتبار الفيديو «AI بالكامل» — **غير مؤكد**.

## التشخيص
| السبب المرجّح | الدليل | قوة الاستنتاج |
|---|---|---|
| الفيديو مصنوع بالكامل بأدوات ذكاء اصطناعي خارج سناب (صوت + لقطات) | نص التنبيه الأول + القاعدة أعلاه | قوي |
| رابط `claude.ai` على الشاشة | «Off-platform links» غير مؤهل؛ ظاهر في لقطة المنشور | قوي لذلك المنشور |
| ومضات/وميض سريع (glitch، flash عند القطع) | «Flashes or strobes» بلا تحذير | **غير مؤكد** (ومضاتنا قصيرة، لا تكرار سريع) |
| نشر النسخة نفسها أكثر من مرة | «Repeatedly posting the same content» | **غير مؤكد** — يعتمد على ما نُشر |

## ما يعني هذا
- الإفصاح وحده **لا يعيد** التوصية في Spotlight للفيديو المصنوع بالكامل بالذكاء الاصطناعي خارج سناب — هذا نص سياستهم.
- القصص (Stories) والملف العام لا تذكرهما القاعدة؛ القيد على **التوصية** في Spotlight.

## ما تم في المستودع
- `tools/content_check.py` (`check_links`): أي رابط/نطاق في السكربت أو نصوص الشاشة أو تعليق النشر = خطأ `LINK` (ضمن `make check` و`make episode`). الحلقات 1–6: لا روابط.
