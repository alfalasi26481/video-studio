import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep11_words_ar.json';
import wEn from './ep11_words_en.json';

// الحلقة 11 — اصنع مهارة (Skill) لـ Claude / Build a skill for Claude
// المحرك v2: ثيم gold + افتتاحية question + كسر نمط snap (جدول docs/STYLE_PLAN.md).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP11 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'gold', hook: 'question', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اطلبها', ex: '«أريد أن أصنع مهارة»', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'أجب ورتّب', ex: 'خطواتك واحدة واحدة', color: COLORS.blue, icon: 'format'},
  {n: '3', label: 'احفظ وفعّل', ex: 'من الإعدادات', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Ask', ex: '"Create a skill"', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Answer', ex: 'Your steps, in order', color: COLORS.blue, icon: 'format'},
  {n: '3', label: 'Save it', ex: 'Switch it on', color: COLORS.green, icon: 'context'},
];

export const EP11_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep11_ar.wav',
  voiceDur: 30.05,
  cues: {problem: 3.18, typeAt: 3.68, badAt: 5.64, formula: 7.7, steps: [9.76, 13.62, 18.26], diff: 21.22, cta: 27.0},
  text: {
    stop: 'ماذا لو؟',
    hookSub: 'مهارة صنعتها أنت',
    userMsg: 'خطّط لرحلتنا القادمة',
    badLabel: 'من الصفر كل مرة',
    formulaTitle: 'اصنع مهارة',
    steps: STEPS_AR,
    before: 'تخطيط من الصفر',
    after: 'خطة على ترتيبك',
    proResult: 'الخطة كاملة',
    emailSubject: 'رحلة الجبل — يومان',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep11_ar.wav',
  words: wAr,
};

export const EP11_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep11_en.wav',
  voiceDur: 28.61,
  cues: {problem: 2.94, typeAt: 3.58, badAt: 5.46, formula: 7.76, steps: [9.78, 13.76, 17.76], diff: 21.16, cta: 26.68},
  text: {
    stop: 'WHAT IF',
    hookSub: 'A skill you built',
    userMsg: 'Plan our next trip',
    badLabel: 'From scratch, every time',
    formulaTitle: 'Build a skill',
    steps: STEPS_EN,
    before: 'From scratch',
    after: 'Your order',
    proResult: 'The full plan',
    emailSubject: 'Mountain trip — 2 days',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep11_en.wav',
  words: wEn,
};
