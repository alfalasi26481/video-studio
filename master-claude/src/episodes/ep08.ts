import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep08_words_ar.json';
import wEn from './ep08_words_en.json';

// الحلقة 8 — علّم Claude طريقتك مرة واحدة / Teach Claude your way, once
// المحرك v2: ثيم mint + افتتاحية stop + كسر نمط snap.
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP08 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'mint', hook: 'stop', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اضغط اسمك', ex: 'ثم Settings · أسفل اليسار', color: COLORS.orange, icon: 'role'},
  {n: '2', label: 'Account أو Your Claude', ex: 'خانة Instructions', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'اكتب طريقتك', ex: 'باختصار · 3 نقاط', color: COLORS.green, icon: 'format'},
  {n: '4', label: 'محادثة جديدة', ex: 'جرّب الآن', color: COLORS.purple, icon: 'task'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Your initials', ex: 'Then Settings · bottom left', color: COLORS.orange, icon: 'role'},
  {n: '2', label: 'Account / Your\u00a0Claude', ex: 'Instructions box', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Write your way', ex: 'Short · 3 bullets', color: COLORS.green, icon: 'format'},
  {n: '4', label: 'New chat', ex: 'Test it', color: COLORS.purple, icon: 'task'},
];

export const EP08_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep08_ar.wav',
  voiceDur: 32.05,
  cues: {problem: 1.2, typeAt: 1.45, badAt: 2.26, formula: 3.02, steps: [6.84, 11.56, 15.64, 21.24], diff: 24.78, cta: 28.74},
  text: {
    stop: 'توقف!',
    hookSub: 'ردود طويلة جداً؟',
    userMsg: 'لماذا السماء زرقاء؟',
    badLabel: 'خمس فقرات طويلة',
    formulaTitle: 'علّم Claude طريقتك',
    steps: STEPS_AR,
    before: '5 فقرات',
    after: '3 نقاط',
    proResult: 'قصير وبنبرتك',
    emailSubject: 'جواب قصير في 3 نقاط',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep08_ar.wav',
  words: wAr,
};

export const EP08_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep08_en.wav',
  voiceDur: 29.69,
  cues: {problem: 1.05, typeAt: 1.3, badAt: 2.0, formula: 2.9, steps: [6.9, 10.5, 15.14, 20.28], diff: 23.1, cta: 27.0},
  text: {
    stop: 'STOP!',
    hookSub: 'Too long?',
    userMsg: 'Why is the sky blue?',
    badLabel: 'Five long paragraphs',
    formulaTitle: 'Teach Claude your way',
    steps: STEPS_EN,
    before: '5 paragraphs',
    after: '3 bullets',
    proResult: 'Short, your tone',
    emailSubject: 'Short answer, 3 bullets',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep08_en.wav',
  words: wEn,
};
