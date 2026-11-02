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
  {n: '1', label: 'قل «تذكّر»', ex: 'تذكّر أنني نباتي', color: COLORS.orange, icon: 'heart'},
  {n: '2', label: 'انسَ أو عدّل', ex: 'في أي وقت', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'محادثة خفية', ex: 'الشبح أعلى اليمين', color: COLORS.green, icon: 'context'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Say "remember"', ex: "I'm vegetarian", color: COLORS.orange, icon: 'heart'},
  {n: '2', label: 'Forget or update', ex: 'Anytime', color: COLORS.blue, icon: 'task'},
  {n: '3', label: 'Incognito', ex: 'Ghost icon, top right', color: COLORS.green, icon: 'context'},
];

export const EP09_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep09_ar.wav',
  voiceDur: 28.73,
  cues: {problem: 2.36, typeAt: 2.9, badAt: 4.5, formula: 7.02, steps: [8.54, 11.32, 15.38], diff: 20.64, cta: 25.92},
  text: {
    stop: 'هكذا؟',
    hookSub: 'يتذكّرك دون أن تكرر',
    userMsg: 'أنا نباتي… للمرة العاشرة',
    badLabel: 'ماذا تفضّل؟',
    formulaTitle: 'ذاكرة Claude',
    steps: STEPS_AR,
    before: 'قبل',
    after: 'بعد',
    proResult: 'عشاء نباتي من أول طلب',
    emailSubject: 'عشاء الليلة: نباتي',
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
  voiceDur: 30.13,
  cues: {problem: 3.76, typeAt: 4.3, badAt: 6.32, formula: 8.74, steps: [10.9, 14.08, 18.2], diff: 22.88, cta: 27.3},
  text: {
    stop: 'THIS?',
    hookSub: 'Remembers you',
    userMsg: "I'm vegetarian… again",
    badLabel: 'What do you prefer?',
    formulaTitle: "Claude's memory",
    steps: STEPS_EN,
    before: 'Before',
    after: 'After',
    proResult: 'Vegetarian, first ask',
    emailSubject: "Tonight's dinner: vegetarian",
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep09_en.wav',
  words: wEn,
};
