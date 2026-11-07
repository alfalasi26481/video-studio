import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep07_words_ar.json';
import wEn from './ep07_words_en.json';

// الحلقة 7 — بحث الويب في Claude / Web search in Claude
// المحرك v2: ثيم gold + افتتاحية reveal (النتيجة أولاً) + كسر نمط snap.
// معاينة: لقطات الحلقة 1 مؤقتاً (يلوّنها ثيم gold) حتى يقرر المالك لقطات EP07 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'gold', hook: 'reveal', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'اسأل بوضوح', ex: 'يبحث حين يفيد', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'قلها صراحة', ex: '«ابحث في الويب»', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'افتح المصادر', ex: 'وتحقق بنفسك', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Ask clearly', ex: 'It searches when it helps', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Say it', ex: '"Search the web"', color: COLORS.blue, icon: 'role'},
  {n: '3', label: 'Open sources', ex: 'Check for yourself', color: COLORS.green, icon: 'context'},
];

export const EP07_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep07_ar.wav',
  voiceDur: 31.57,
  cues: {problem: 3.82, typeAt: 4.4, badAt: 6.5, formula: 8.32, steps: [10.7, 15.52, 19.16], diff: 22.56, cta: 27.48},
  text: {
    stop: 'هكذا؟',
    hookSub: 'إجابة حديثة بمصادرها',
    userMsg: 'متى أرى الشهب هذا الأسبوع؟',
    badLabel: 'هل المعلومة قديمة؟',
    formulaTitle: 'بحث الويب في Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'حديثة ومعها المصادر',
    emailSubject: 'الشهب: الموعد والمصادر',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة كل يوم',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep07_ar.wav',
  words: wAr,
};

export const EP07_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep07_en.wav',
  voiceDur: 27.17,
  cues: {problem: 2.74, typeAt: 3.3, badAt: 5.48, formula: 6.72, steps: [9.46, 12.8, 16.0], diff: 19.38, cta: 23.96},
  text: {
    stop: 'THIS?',
    hookSub: 'Fresh answer, with sources',
    userMsg: 'Meteor shower this week: when?',
    badLabel: 'Is this out of date?',
    formulaTitle: 'Web search in Claude',
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Fresh, with sources',
    emailSubject: 'Meteor shower: times + sources',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every day',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep07_en.wav',
  words: wEn,
};
