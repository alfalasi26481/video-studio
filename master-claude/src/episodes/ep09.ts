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
  {n: '2', label: 'انسَ أو عدّل', ex: 'في أي وقت', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'محادثة خفية', ex: 'الشبح أعلى اليمين', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Say "remember"', ex: 'Small balcony only', color: COLORS.orange, icon: 'heart'},
  {n: '2', label: 'Forget or update', ex: 'Anytime', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'Incognito', ex: 'Ghost icon, top right', color: COLORS.green, icon: 'context'},
];

export const EP09_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep09_ar.wav',
  voiceDur: 28.41,
  cues: {problem: 3.46, typeAt: 4.0, badAt: 5.36, formula: 7.96, steps: [9.84, 13.34, 17.18], diff: 21.56, cta: 25.44},
  text: {
    stop: 'هكذا؟',
    hookSub: 'يعرف ما لديك',
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
  voiceDur: 30.49,
  cues: {problem: 4.32, typeAt: 4.9, badAt: 6.52, formula: 9.2, steps: [11.36, 15.34, 19.36], diff: 24.2, cta: 27.74},
  text: {
    stop: 'THIS?',
    hookSub: 'Knows your setup',
    userMsg: 'What should I plant this month?',
    badLabel: "A garden you don't have",
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
