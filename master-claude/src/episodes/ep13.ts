import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep13_words_ar.json';
import wEn from './ep13_words_en.json';

// الحلقة 13 — كلّم Claude بصوتك / Talk to Claude out loud
// المحرك v2: ثيم ember + افتتاحية question + كسر نمط snap (لا يكرر EP12: mint/reveal).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP13 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'ember', hook: 'question', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اضغط الموجة', ex: 'أسفل المحادثة', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'اختر صوتاً', ex: 'أول مرة، ثم تحدّث', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'اضغط إيقاف', ex: 'الحوار مكتوب', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Tap the wave', ex: 'Bottom of the chat', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Pick a voice', ex: 'First time, then talk', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'Tap stop', ex: 'Saved as text', color: COLORS.green, icon: 'format'},
];

export const EP13_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep13_ar.wav',
  voiceDur: 31.05,
  cues: {problem: 2.98, typeAt: 3.38, badAt: 5.92, formula: 7.9, steps: [10.62, 14.6, 19.1], diff: 24.2, cta: 27.9},
  text: {
    stop: 'صوتك؟',
    hookSub: 'حوار بلا كتابة',
    userMsg: 'لنتمرّن على لغة جديدة',
    badLabel: 'الكتابة لا تدرّب النطق',
    formulaTitle: 'الوضع الصوتي',
    steps: STEPS_AR,
    before: 'كتابة فقط',
    after: 'حوار بصوتك',
    proResult: 'تمرين نطق جاهز',
    emailSubject: 'تمرين المشي — صوت',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep13_ar.wav',
  words: wAr,
};

export const EP13_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep13_en.wav',
  voiceDur: 29.33,
  cues: {problem: 2.36, typeAt: 2.76, badAt: 4.76, formula: 7.22, steps: [10.16, 13.86, 18.66], diff: 23.26, cta: 27.12},
  text: {
    stop: 'SPEAK?',
    hookSub: "Talk, don't type",
    userMsg: "Let's practice a new language",
    badLabel: "Typing won't do it",
    formulaTitle: 'Voice mode',
    steps: STEPS_EN,
    before: 'Typing only',
    after: 'A spoken chat',
    proResult: 'Practice, out loud',
    emailSubject: 'Walk practice — voice',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep13_en.wav',
  words: wEn,
};
