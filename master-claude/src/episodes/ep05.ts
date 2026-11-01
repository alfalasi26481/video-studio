import {COLORS} from '../engine/types';
import type {EpisodeData, Step} from '../engine/types';
import wAr from './ep05_words_ar.json';
import wEn from './ep05_words_en.json';

// الحلقة 5 — الـ Artifact في Claude / Artifacts in Claude
// معتمدة من المالك 1 نوفمبر 2026 — لقطات الحلقة 1 (قرار اللقطات الخاصة معلّق).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اطلبه', ex: 'يفتح بجانب المحادثة', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'عدّله', ex: 'اطلب أي تغيير', color: COLORS.blue, icon: 'format'},
  {n: '3', label: 'شاركه', ex: 'خاص بك أولاً', color: COLORS.green, icon: 'role'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Ask', ex: 'Opens beside your chat', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Edit', ex: 'Ask for any change', color: COLORS.blue, icon: 'format'},
  {n: '3', label: 'Share', ex: 'Private first', color: COLORS.green, icon: 'role'},
];

export const EP05_AR: EpisodeData = {
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep05_ar.wav',
  voiceDur: 31.13,
  cues: {problem: 4.7, typeAt: 5.1, badAt: 6.02, formula: 8.66, steps: [10.3, 14.6, 16.98], diff: 20.5, cta: 27.66},
  text: {
    stop: 'توقف!',
    hookSub: 'طلبت أداة فوصلك نص؟',
    userMsg: 'اصنع لي جدول مذاكرة أسبوعياً',
    badLabel: 'نص طويل ترتبه بنفسك',
    formulaTitle: 'الـ Artifact في Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'جدول جاهز تستخدمه',
    emailSubject: 'جدول المذاكرة الأسبوعي',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep05_ar.wav',
  words: wAr,
};

export const EP05_EN: EpisodeData = {
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep05_en.wav',
  voiceDur: 30.17,
  cues: {problem: 4.55, typeAt: 5.0, badAt: 6.34, formula: 8.7, steps: [10.62, 14.62, 17.34], diff: 20.82, cta: 26.56},
  text: {
    stop: 'STOP!',
    hookSub: 'Asked for a tool, got text?',
    userMsg: 'Make me a weekly study planner',
    badLabel: 'A wall of text to sort out',
    formulaTitle: 'Artifacts in Claude',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'A planner, ready to use',
    emailSubject: 'Weekly study planner',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep05_en.wav',
  words: wEn,
};
