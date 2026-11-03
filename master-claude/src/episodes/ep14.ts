import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep14_words_ar.json';
import wEn from './ep14_words_en.json';

// الحلقة 14 — اطلب ملفاً حقيقياً / Ask Claude for a real file
// المحرك v2: ثيم gold + افتتاحية stop + كسر نمط snap (لا يكرر EP13: ember/question).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP14 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'gold', hook: 'stop', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اطلب ملف PDF', ex: 'وسمِّ ما تريده', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'انتظر لحظة', ex: 'يظهر في المحادثة', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'نزّله واطبعه', ex: 'من جهازك', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Ask for a PDF', ex: 'Say what goes in it', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Give it a moment', ex: 'It shows up in chat', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'Download, then print', ex: 'From your device', color: COLORS.green, icon: 'format'},
];

export const EP14_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep14_ar.wav',
  voiceDur: 31.37,
  cues: {problem: 2.94, typeAt: 3.34, badAt: 4.34, formula: 7.08, steps: [9.86, 15.38, 19.24], diff: 22.22, cta: 28.16},
  text: {
    stop: 'توقف!',
    hookSub: 'تريده على ورق؟',
    userMsg: 'اصنع لي ملف PDF لتماريني',
    badLabel: 'نص لا يصلح للطباعة',
    formulaTitle: 'ملف حقيقي',
    steps: STEPS_AR,
    before: 'نص في المحادثة',
    after: 'ورقة على الجدار',
    proResult: 'أسبوعك مطبوع',
    emailSubject: 'تمارين الأسبوع — PDF',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep14_ar.wav',
  words: wAr,
};

export const EP14_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep14_en.wav',
  voiceDur: 27.93,
  cues: {problem: 2.56, typeAt: 2.96, badAt: 3.94, formula: 6.54, steps: [9.32, 13.74, 17.48], diff: 20.96, cta: 25.58},
  text: {
    stop: 'STOP!',
    hookSub: 'Need it on paper?',
    userMsg: 'Make a PDF of my workouts',
    badLabel: "Chat text won't print well",
    formulaTitle: 'A real file',
    steps: STEPS_EN,
    before: 'Chat text',
    after: 'On your wall',
    proResult: 'Your week, printed',
    emailSubject: 'Weekly workouts — PDF',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep14_en.wav',
  words: wEn,
};
