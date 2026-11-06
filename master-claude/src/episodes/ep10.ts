import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep10_words_ar.json';
import wEn from './ep10_words_en.json';

// الحلقة 10 — أعطِ Claude أمثلة فيكتب بأسلوبك / Give Claude examples, get your style
// المحرك v2: ثيم electric + افتتاحية stop + كسر نمط snap.
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP10 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'electric', hook: 'stop', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'الصق 3 أمثلة', ex: 'كتبتها أنت', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'نوّعها', ex: 'قصيرة · طويلة · مناسبة أخرى', color: COLORS.blue, icon: 'format'},
  {n: '3', label: '«بالأسلوب نفسه»', ex: 'لصديقي في تخرّجه', color: COLORS.green, icon: 'heart'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Paste 3 examples', ex: 'Your own', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Vary them', ex: 'Short · long · other occasion', color: COLORS.blue, icon: 'format'},
  {n: '3', label: '"Same style"', ex: "Friend's graduation", color: COLORS.green, icon: 'heart'},
];

export const EP10_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep10_ar.wav',
  voiceDur: 31.13,
  cues: {problem: 0.8, typeAt: 1.2, badAt: 2.66, formula: 4.24, steps: [6.72, 10.94, 17.48], diff: 23.72, cta: 27.92},
  text: {
    stop: 'توقف!',
    hookSub: 'لا يشبه كلامك؟',
    userMsg: 'اكتب لي تهنئة',
    badLabel: 'كأن غريباً كتبها',
    formulaTitle: 'أعطه أمثلة',
    steps: STEPS_AR,
    before: 'تهنئة باردة',
    after: 'بأسلوبك أنت',
    proResult: 'تهنئة تشبهك',
    emailSubject: 'مبروك التخرّج يا صديقي',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep10_ar.wav',
  words: wAr,
};

export const EP10_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep10_en.wav',
  voiceDur: 25.45,
  cues: {problem: 0.72, typeAt: 1.1, badAt: 2.12, formula: 3.86, steps: [6.14, 9.18, 13.72], diff: 19.12, cta: 23.3},
  text: {
    stop: 'STOP!',
    hookSub: 'Not your voice?',
    userMsg: 'Write me a greeting',
    badLabel: 'A stranger wrote it',
    formulaTitle: 'Give examples',
    steps: STEPS_EN,
    before: 'Flat greeting',
    after: 'Your style',
    proResult: 'Sounds like you',
    emailSubject: 'Congrats on graduating!',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep10_en.wav',
  words: wEn,
};
