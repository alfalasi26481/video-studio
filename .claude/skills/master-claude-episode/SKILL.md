---
name: master-claude-episode
description: Use for ANY episode of the "أتقن Claude / Master Claude" social channel (script, voice, clips, montage, render, captions). Produces episodes with the approved engine in master-claude/ — never a new montage.
---

# حلقات قناة أتقن Claude

1. اقرأ `master-claude/CLAUDE.md` كاملاً واتبعه حرفياً. هو المصدر الوحيد للمونتاج.
2. لا تبنِ مونتاجاً جديداً ولا تعدّل `master-claude/src/engine/`. الحلقة الجديدة = `src/episodes/epNN.ts` + أصولها فقط.
3. ابدأ بالتجهيز (npm install، browser ensure، faster-whisper)، ثم تأكد أن `npx remotion compositions src/index.ts` يعرض الحلقات السابقة.
4. اتبع خطوات الإنتاج الـ 11 بالترتيب، ولا تسلّم قبل `scripts/check.sh` النهائي.
