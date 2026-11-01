import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep06_words_ar.json';
import wEn from './ep06_words_en.json';

// الحلقة 6 — ارفع صورة أو ملفاً إلى Claude / Upload a photo or file to Claude
// أول حلقة على المحرك v2 (طلب المالك 1 نوفمبر 2026): ثيم electric + افتتاحية سؤال + كسر نمط snap.
// ألوان البطاقات تُكتب بأسماء v1 (orange/blue/green) ويحوّلها v2 إلى ألوان الثيم.
const clips = {hook: 'clips/ep06_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep06_portal.mp4', burst: 'clips/ep06_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'electric', hook: 'question', breaks: 'snap', gradeExcept: [clips.hook, clips.mid, clips.burst]};

const STEPS_AR: Step[] = [
  {n: '1', label: 'ارفعها', ex: 'زر + أو اسحبها', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'اسأل', ex: 'بكلماتك أنت', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'ملفات PDF', ex: 'والصور أيضاً', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Upload', ex: 'Tap + or drag it in', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Ask', ex: 'In your own words', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'PDFs too', ex: 'Photos and files', color: COLORS.green, icon: 'context'},
];

export const EP06_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep06_ar.wav',
  voiceDur: 27.57,
  cues: {problem: 2.3, typeAt: 3.3, badAt: 4.98, formula: 6.94, steps: [9.14, 13.1, 15.48], diff: 19.76, cta: 23.68},
  text: {
    stop: 'لماذا؟',
    hookSub: 'تكتب كل شيء بيدك؟',
    userMsg: 'اخلط 200 غرام دقيق مع...',
    badLabel: 'نسخ يدوي كلمة كلمة',
    formulaTitle: 'ارفع الصورة إلى Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'مترجمة ولشخصين',
    emailSubject: 'كعكة الشوكولاتة لشخصين',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep06_ar.wav',
  words: wAr,
};

export const EP06_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep06_en.wav',
  voiceDur: 28.25,
  cues: {problem: 2.05, typeAt: 2.7, badAt: 4.72, formula: 6.98, steps: [9.82, 13.56, 16.22], diff: 20.38, cta: 24.78},
  text: {
    stop: 'WHY?',
    hookSub: 'Typing it all by hand?',
    userMsg: 'Mix 200g of flour with...',
    badLabel: 'Copying it word by word',
    formulaTitle: 'Upload it to Claude',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Translated, for two',
    emailSubject: 'Chocolate cake for two',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep06_en.wav',
  words: wEn,
};
