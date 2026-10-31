import {COLORS} from '../engine/types';
import type {EpisodeData, Step} from '../engine/types';
import wAr from './ep04_words_ar.json';
import wEn from './ep04_words_en.json';

// الحلقة 4 — المشاريع في Claude / Projects in Claude
// معتمدة من المالك 31 أكتوبر 2026 — لقطات Higgsfield خاصة بالحلقة (kling4_0).
const clips = {hook: 'clips/ep04_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep04_space.mp4', burst: 'clips/ep04_burst.mp4', outro: 'clips/ep01_outro.mp4'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'المشروع', ex: 'مساحة بمحادثاتها', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'المعرفة', ex: 'أضف ملفاتك', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'التعليمات', ex: 'اكتبها مرة واحدة', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Project', ex: 'Its own chats', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Knowledge', ex: 'Add your files', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Instructions', ex: 'Write once', color: COLORS.green, icon: 'format'},
];

export const EP04_AR: EpisodeData = {
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep04_ar.wav',
  voiceDur: 32.18,
  cues: {problem: 4.3, typeAt: 5.44, badAt: 8.56, formula: 10.04, steps: [11.58, 15.64, 18.66], diff: 21.94, cta: 28.34},
  text: {
    stop: 'توقف!',
    hookSub: 'تعيد الشرح في كل محادثة؟',
    userMsg: 'أنا أتعلم لغة جديدة، ومستواي مبتدئ',
    badLabel: 'البداية من الصفر كل مرة',
    formulaTitle: 'المشاريع في Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'سياقك في كل محادثة',
    emailSubject: 'درس اليوم على مستواك',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep04_ar.wav',
  words: wAr,
};

export const EP04_EN: EpisodeData = {
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep04_en.wav',
  voiceDur: 28.13,
  cues: {problem: 3.8, typeAt: 4.84, badAt: 6.66, formula: 8.28, steps: [9.94, 12.96, 15.58], diff: 18.54, cta: 24.92},
  text: {
    stop: 'STOP!',
    hookSub: 'Explaining it again, every chat?',
    userMsg: "I'm learning a new language, I'm a beginner",
    badLabel: 'Starting from zero, every time',
    formulaTitle: 'Projects in Claude',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Your context, every chat',
    emailSubject: "Today's lesson, at your level",
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep04_en.wav',
  words: wEn,
};
