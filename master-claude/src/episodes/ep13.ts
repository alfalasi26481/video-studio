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
  {n: '1', label: 'اضغط الموجة', ex: 'بجانب الميكروفون', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'اختر صوتاً', ex: 'وتحدّث بحرية', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'اضغط إيقاف', ex: 'الحوار محفوظ', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Tap the wave', ex: 'Next to the mic', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Pick a voice', ex: 'Then just talk', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'Tap stop', ex: 'Saved as text', color: COLORS.green, icon: 'format'},
];

export const EP13_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep13_ar.wav',
  voiceDur: 28.37,
  cues: {problem: 2.28, typeAt: 2.68, badAt: 5.38, formula: 7.18, steps: [9.18, 13.24, 17.14], diff: 21.96, cta: 25.34},
  text: {
    stop: 'بصوتك؟',
    hookSub: 'حوار بلا كتابة',
    userMsg: 'لنتمرّن على الإنجليزية',
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
  voiceDur: 25.61,
  cues: {problem: 2.32, typeAt: 2.72, badAt: 4.46, formula: 6.58, steps: [8.5, 11.78, 15.8], diff: 19.96, cta: 23.48},
  text: {
    stop: 'SPEAK?',
    hookSub: "Talk, don't type",
    userMsg: "Let's practice my Spanish",
    badLabel: "Typing won't train speaking",
    formulaTitle: 'Voice mode',
    steps: STEPS_EN,
    before: 'Typing only',
    after: 'Out loud',
    proResult: 'Speaking practice, on',
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
