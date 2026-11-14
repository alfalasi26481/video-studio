import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep09_words_ar.json';
import wEn from './ep09_words_en.json';

// الحلقة 9 — ذاكرة Claude / Claude's memory
// المحرك v2: ثيم ember + افتتاحية reveal (النتيجة أولاً) + كسر نمط snap.
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP09 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'ember', hook: 'reveal', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'قل «تذكّر»', ex: 'عندي شرفة صغيرة', color: COLORS.orange, icon: 'heart'},
  {n: '2', label: 'انسَ أو عدّل', ex: 'متى شئت', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'محادثة خفية', ex: 'عند البدء · فوق يميناً', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Say "remember"', ex: 'Small balcony only', color: COLORS.orange, icon: 'heart'},
  {n: '2', label: 'Forget or update', ex: 'Anytime', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'Incognito', ex: 'Chat start · top right', color: COLORS.green, icon: 'context'},
];

export const EP09_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep09_ar.wav',
  voiceDur: 32.41,
  cues: {problem: 3.5, typeAt: 4.44, badAt: 6.54, formula: 8.56, steps: [10.72, 14.42, 18.58], diff: 25.12, cta: 29.34},
  text: {
    stop: 'هكذا؟',
    hookSub: 'يتذكّر شرفتك الصغيرة',
    userMsg: 'ماذا أزرع هذا الشهر؟',
    badLabel: 'حديقة لا تملكها',
    formulaTitle: 'ذاكرة Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'نباتات لشرفتك',
    emailSubject: 'خطة زراعة الشرفة',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep09_ar.wav',
  words: wAr,
};

export const EP09_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep09_en.wav',
  voiceDur: 31.21,
  cues: {problem: 3.54, typeAt: 4.16, badAt: 6.22, formula: 8.7, steps: [10.82, 14.46, 18.44], diff: 24.58, cta: 28.3},
  text: {
    stop: 'THIS?',
    hookSub: 'Remembers your balcony',
    userMsg: 'What should I plant this month?',
    badLabel: 'No garden here',
    formulaTitle: "Claude's memory",
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Plants for your balcony',
    emailSubject: 'Balcony planting plan',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep09_en.wav',
  words: wEn,
};
