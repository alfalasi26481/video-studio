import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep14_words_ar.json';
import wEn from './ep14_words_en.json';

// الحلقة 14 — اطلب ملفاً حقيقياً (شهادة تقدير) / Ask Claude for a real file — بعد مراجعة الناقد 4 نوفمبر
// المحرك v2: ثيم gold + افتتاحية stop + كسر نمط snap (لا يكرر EP13: ember/question).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP14 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'gold', hook: 'stop', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اطلب ملف PDF', ex: 'واذكر ما فيه', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'انتظر قليلاً', ex: 'حتى يظهر الملف', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'نزّله واطبعه', ex: 'من جهازك', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Ask for a PDF', ex: 'Say what goes in it', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Wait a little', ex: 'Till the file appears', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'Download, then print', ex: 'From your device', color: COLORS.green, icon: 'format'},
];

export const EP14_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep14_ar.wav',
  voiceDur: 29.41,
  cues: {problem: 2.58, typeAt: 2.98, badAt: 4.42, formula: 7.18, steps: [9.52, 14.6, 18.86], diff: 21.78, cta: 26.42},
  text: {
    stop: 'ورق؟',
    hookSub: 'شهادة لابنك تطبعها',
    userMsg: 'اصنع شهادة تقدير PDF لابني',
    badLabel: 'نص لا يصلح للطباعة',
    formulaTitle: 'ملف حقيقي',
    steps: STEPS_AR,
    before: 'نص في المحادثة',
    after: 'شهادة على الجدار',
    proResult: 'شهادته جاهزة للطباعة',
    emailSubject: 'شهادة تقدير — PDF',
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
  voiceDur: 28.33,
  cues: {problem: 2.74, typeAt: 3.14, badAt: 4.36, formula: 7.14, steps: [9.84, 14.3, 18.2], diff: 21.26, cta: 26.14},
  text: {
    stop: 'PAPER?',
    hookSub: 'A certificate to print',
    userMsg: 'Make a PDF certificate for my son',
    badLabel: "Won't print well",
    formulaTitle: 'A real file',
    steps: STEPS_EN,
    before: 'Chat text',
    after: 'On his wall',
    proResult: 'Ready to print',
    emailSubject: 'Certificate — PDF',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep14_en.wav',
  words: wEn,
};
