# صيغة الحلقة — `episodes/<id>.yaml`

ملف واحد لكل حلقة يحمل النسختين العربية (فصحى) والإنجليزية، مشهداً بمشهد.

```yaml
id: ep08                 # يطابق اسم الملف
level: beginner          # beginner | intermediate | pro
status: verified         # draft | verified | rendered
title: {ar: ..., en: ...}
sources:                 # إلزامي: صفحة رسمية من Anthropic لكل معلومة عن Claude
  - url: https://support.claude.com/...
    claim: ما الذي تثبته الصفحة
    checked: 2026-10-30
scenes:
  - role: hook           # hook | step | recap | cta
    motion: KineticTitle # KineticTitle | BoxReveal | Arrow | FlowDiagram | ChatMock
    ar:
      narration: النص المسموع (4–45 كلمة)
      on_screen: نص الشاشة (10 كلمات كحد أقصى)
      items: [...]       # BoxReveal / FlowDiagram: 2–5 عناصر، العدد نفسه في en
      chat: {user: ..., reply: ...}   # ChatMock فقط
    en: { ...same shape... }
```

## القواعد التي يفرضها `tools/validate_episode.py`
- الترتيب: hook واحد أولاً ← step واحد أو أكثر ← recap واحد ← cta واحد أخيراً.
- كل مشهد له `ar` و `en`. العربي فيه حروف عربية، والإنجليزي بلا حروف عربية.
- `motion` من قائمة المكوّنات المتحركة فقط (لا شرائح نصية ثابتة).
- المصادر من نطاقات Anthropic الرسمية فقط (`support.claude.com`, `docs.claude.com`, `platform.claude.com`, `anthropic.com`, `claude.com` ...).
- فحص المحتوى (`tools/content_check.py`) على كل نص: لا أسماء أو أوصاف جهات حكومية أو خاصة، لا مواضيع عمل/مكتب، ولا كلمات لهجة خليجية في العربي.
- المدة التقديرية (عربي 2.2 كلمة/ث، إنجليزي 2.6) بين 15 و90 ثانية — تحذير فقط حتى يُقاس الصوت الحقيقي.

## التوافق مع محرك `edu-channel` (فرع edu-channel-template)
| هذه الصيغة | نوع المشهد هناك |
|---|---|
| KineticTitle (hook) | `hook` |
| KineticTitle (cta) | `cta` |
| ChatMock | `chat` |
| BoxReveal | `steps` |
| FlowDiagram / Arrow | `flow` |
