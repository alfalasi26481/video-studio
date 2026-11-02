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
  {n: '2', label: 'نوّعها', ex: 'قصير · طويل · مناسبة أخرى', color: COLORS.blue, icon: 'format'},
  {n: '3', label: '«بالأسلوب نفسه»', ex: 'لأخي في عيد ميلاده', color: COLORS.green, icon: 'heart'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Paste 3 examples', ex: 'Your own', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Mix them', ex: 'Short · long · new occasion', color: COLORS.blue, icon: 'format'},
  {n: '3', label: '"Same style"', ex: "Brother's birthday", color: COLORS.green, icon: 'heart'},
];

export const EP10_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep10_ar.wav',
  voiceDur: 28.61,
  cues: {problem: 2.0, typeAt: 2.3, badAt: 3.8, formula: 4.86, steps: [7.2, 10.7, 16.54], diff: 22.2, cta: 25.96},
  text: {
    stop: 'توقف!',
    hookSub: 'لا يشبه كلامك؟',
    userMsg: 'اكتب لي تهنئة',
    badLabel: 'كلام عام لا يشبهك',
    formulaTitle: 'أعطه أمثلة',
    steps: STEPS_AR,
    before: 'تهنئة عامة',
    after: 'بكلماتك أنت',
    proResult: 'تهنئة تشبهك',
    emailSubject: 'عيد ميلاد سعيد يا أخي',
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
  voiceDur: 26.37,
  cues: {problem: 1.9, typeAt: 2.2, badAt: 3.16, formula: 4.5, steps: [7.4, 10.16, 15.0], diff: 19.8, cta: 24.28},
  text: {
    stop: 'STOP!',
    hookSub: 'Not your voice?',
    userMsg: 'Write me a greeting',
    badLabel: 'Generic, not you',
    formulaTitle: 'Give examples',
    steps: STEPS_EN,
    before: 'Generic',
    after: 'Your words',
    proResult: 'Sounds like you',
    emailSubject: 'Happy birthday, bro',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep10_en.wav',
  words: wEn,
};
