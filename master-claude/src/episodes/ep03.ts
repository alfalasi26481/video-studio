import {COLORS} from '../engine/types';
import type {EpisodeData, Step} from '../engine/types';
import wAr from './ep03_words_ar.json';
import wEn from './ep03_words_en.json';

// الحلقة 3 — أربع عادات لطلب أوضح / Four Habits for a Clearer Request
// معاينة: اللقطات مؤقتة من الحلقة 1 (بلا Higgsfield) حتى يوافق المالك.
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'الوضوح', ex: 'قل ما تريده ببساطة', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'السياق', ex: 'مبتدئ في الطبخ، ولدي 20 دقيقة', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'الخطوات', ex: 'مهمة كبيرة، أجزاء صغيرة', color: COLORS.green, icon: 'format'},
  {n: '4', label: 'الملاحظات', ex: 'لم يعجبك؟ اطلب إعادة الكتابة', color: COLORS.purple, icon: 'role'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Clarity', ex: 'Say what you want, simply', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Context', ex: 'New cook, 20 minutes', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Steps', ex: 'Big task, small parts', color: COLORS.green, icon: 'format'},
  {n: '4', label: 'Feedback', ex: 'Not right? Ask for a rewrite', color: COLORS.purple, icon: 'role'},
];

export const EP03_AR: EpisodeData = {
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep03_ar.wav',
  voiceDur: 34.05,
  cues: {problem: 3.85, typeAt: 4.66, badAt: 5.92, formula: 7.9, steps: [9.52, 13.08, 17.6, 21.74], diff: 26.54, cta: 30.38},
  text: {
    stop: 'توقف!',
    hookSub: 'الرد العام سببه طريقة الطلب',
    userMsg: 'اقترح لي عشاء',
    badLabel: 'اقتراح لا يناسبك',
    formulaTitle: 'أربع عادات لطلب أوضح',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'نتيجة تناسبك',
    emailSubject: '3 وجبات عشاء في 20 دقيقة',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep03_ar.wav',
  words: wAr,
};

export const EP03_EN: EpisodeData = {
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep03_en.wav',
  voiceDur: 31.09,
  cues: {problem: 4.0, typeAt: 4.78, badAt: 5.84, formula: 7.96, steps: [9.82, 12.88, 16.3, 19.98], diff: 23.96, cta: 27.12},
  text: {
    stop: 'STOP!',
    hookSub: 'Vague answers start with the request',
    userMsg: 'Suggest a dinner',
    badLabel: "An idea that doesn't fit",
    formulaTitle: '4 Clear-Prompt Habits',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Made for you',
    emailSubject: '3 dinners in 20 minutes',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep03_en.wav',
  words: wEn,
};
