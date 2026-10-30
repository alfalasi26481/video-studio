import {COLORS} from '../engine/types';
import type {EpisodeData, Step} from '../engine/types';
import wAr from './ep02_words_ar.json';
import wEn from './ep02_words_en.json';

// الحلقة 2 — الجملة السحرية / The Magic Line
const clips = {hook: 'clips/ep02_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep02_magic.mp4', burst: 'clips/ep02_map.mp4', outro: 'clips/ep01_outro.mp4'};

const Q_AR: Step[] = [
  {n: '1', label: 'كم ميزانيتك؟', ex: '', color: COLORS.orange, icon: 'budget'},
  {n: '2', label: 'كم يوماً لديك؟', ex: '', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'طبيعة أم تسوق؟', ex: '', color: COLORS.green, icon: 'heart'},
];
const Q_EN: Step[] = [
  {n: '1', label: "What's your budget?", ex: '', color: COLORS.orange, icon: 'budget'},
  {n: '2', label: 'How many days?', ex: '', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Nature or shopping?', ex: '', color: COLORS.green, icon: 'heart'},
];

export const EP02_AR: EpisodeData = {
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep02_ar.wav',
  voiceDur: 27.81,
  cues: {problem: 3.5, typeAt: 3.8, badAt: 5.6, formula: 8.5, steps: [15.35, 16.45, 17.65], diff: 19.9, cta: 23.8},
  text: {
    stop: 'توقف!',
    hookSub: 'Claude يحتاج أن يسألك قبل أن يجيب',
    userMsg: 'خطط لي رحلة',
    badLabel: 'خطة عامة لا تناسبك',
    formulaTitle: 'الجملة السحرية',
    steps: Q_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'مفصّلة لك أنت',
    emailSubject: 'خطتك: 5 أيام في الطبيعة',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'اكتب هذه الجملة',
  },
  clips,
  music: 'music/ep02_ar.wav',
  words: wAr,
  magic: {label: 'الجملة السحرية', line: 'قبل أن تجيب، اسألني 3 أسئلة', at: 10.6, asks: 'Claude يسألك:', asksAt: 13.25},
  chips: ['5000 درهم', '5 أيام', 'طبيعة'],
};

export const EP02_EN: EpisodeData = {
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep02_en.wav',
  voiceDur: 25.73,
  cues: {problem: 2.55, typeAt: 3.0, badAt: 4.45, formula: 7.05, steps: [14.3, 15.5, 16.6], diff: 19.0, cta: 22.35},
  text: {
    stop: 'STOP!',
    hookSub: 'Claude needs to ask you first',
    userMsg: 'Plan me a trip',
    badLabel: 'A generic plan',
    formulaTitle: 'The Magic Line',
    steps: Q_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Made for you',
    emailSubject: 'Your plan: 5 days in nature',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'Type this line',
  },
  clips,
  music: 'music/ep02_en.wav',
  words: wEn,
  magic: {label: 'The Magic Line', line: 'Before you answer, ask me 3 questions', at: 9.6, asks: 'Claude asks:', asksAt: 12.8},
  chips: ['$1,500', '5 days', 'Nature'],
};
