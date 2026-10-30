import {COLORS} from '../engine/types';
import type {EpisodeData, Step} from '../engine/types';
import wAr from './ep01_words_ar.json';
import wEn from './ep01_words_en.json';

// الحلقة 1 — معادلة الطلب الاحترافي / The Pro Prompt Formula
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'الدور', ex: 'أنت مساعد محترف في خدمة العملاء', color: COLORS.orange, icon: 'role'},
  {n: '2', label: 'المهمة', ex: 'اكتب إيميل اعتذار', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'السياق', ex: 'لعميل تأخر طلبه 3 أيام', color: COLORS.green, icon: 'context'},
  {n: '4', label: 'الشكل', ex: '3 فقرات قصيرة، بنبرة ودودة', color: COLORS.purple, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Role', ex: "You're a pro support assistant", color: COLORS.orange, icon: 'role'},
  {n: '2', label: 'Task', ex: 'Write an apology email', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'Context', ex: 'Customer order is 3 days late', color: COLORS.green, icon: 'context'},
  {n: '4', label: 'Format', ex: '3 short paragraphs, friendly tone', color: COLORS.purple, icon: 'format'},
];

export const EP01_AR: EpisodeData = {
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep01_ar.wav',
  voiceDur: 32.3,
  cues: {problem: 2.7, typeAt: 4.0, badAt: 5.2, formula: 7.6, steps: [10.1, 13.9, 16.8, 20.8], diff: 25.0, cta: 28.3},
  text: {
    stop: 'توقف!',
    hookSub: 'أنت تكتب لـ Claude بالطريقة الخطأ',
    userMsg: 'اكتب لي إيميل',
    badLabel: 'رد عام لا يشبهك',
    formulaTitle: 'معادلة الطلب الاحترافي',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'نتيجة احترافية',
    emailSubject: 'نعتذر عن تأخر طلبك',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep01_ar.wav',
  words: wAr,
};

export const EP01_EN: EpisodeData = {
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep01_en.wav',
  voiceDur: 30.25,
  cues: {problem: 2.6, typeAt: 3.6, badAt: 4.4, formula: 6.4, steps: [8.6, 12.6, 15.7, 19.9], diff: 23.9, cta: 27.1},
  text: {
    stop: 'STOP!',
    hookSub: "You're prompting Claude the wrong way",
    userMsg: 'Write me an email',
    badLabel: 'A generic reply',
    formulaTitle: 'The Pro Prompt Formula',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Pro result',
    emailSubject: 'Sorry about your order delay',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep01_en.wav',
  words: wEn,
};
