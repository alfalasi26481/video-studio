# سجل التطوير

## 2026-10-30 — الدورة 1: الأساس (فرع dev/foundation)
**ما تم**
- إعادة كتابة CLAUDE.md للقناة (سكل الطيران باقٍ كما هو).
- صيغة الحلقة `episodes/<id>.yaml` موثّقة في `docs/EPISODE_FORMAT.md`.
- `tools/validate_episode.py` + `tools/content_check.py` (جهات، عمل/مكتب، لهجة خليجية).
- 3 حلقات نموذجية ep08–ep10 (طلب أوضح، المشاريع، الـ Artifacts) — كل معلومة مُراجعة على support.claude.com في 30 أكتوبر.
- `episodes/backlog.yaml` (18 حلقة)، `Makefile` (`make check`)، CI على GitHub Actions.
- 46 اختباراً ناجحاً. اكتُشف وأُصلح خطأ: «الخلاصة» كانت تُعلَّم لهجةً بسبب «خلاص».

**ملاحظة مهمة**: فرع `edu-channel-template` يحوي محرك Remotion متقدماً (7 حلقات، مكوّنات Flow/Chat، مزامنة صوت، QA) غير مدموج وبلا PR. لم يُذكر في وصف حالة المستودع.

**المتبقي**: البنود b–e.
**الخطوة التالية**: البند b — بانتظار قرار مانع: نقل محرك edu-channel إلى `remotion/` (موصى به) أو البناء من الصفر.
