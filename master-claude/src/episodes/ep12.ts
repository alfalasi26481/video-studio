import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep12_words_ar.json';
import wEn from './ep12_words_en.json';

// الحلقة 12 — Claude Code لأول مرة / Claude Code, first time
// المحرك v2: ثيم mint + افتتاحية reveal + كسر نمط snap (لا يكرر EP11: gold/question).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP12 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'mint', hook: 'reveal', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'افتح Code', ex: 'تطبيق الكمبيوتر', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'اختر مجلداً', ex: 'فيه قائمتك', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'راجع ووافق', ex: 'كل تغيير', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Open Code', ex: 'Desktop app', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Pick a folder', ex: 'Your list inside', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Review, approve', ex: 'Every change', color: COLORS.green, icon: 'format'},
];

export const EP12_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep12_ar.wav',
  voiceDur: 30.13,
  cues: {problem: 4.2, typeAt: 4.6, badAt: 7.32, formula: 9.06, steps: [10.72, 14.66, 18.0], diff: 22.72, cta: 26.9},
  text: {
    stop: 'هكذا؟',
    hookSub: 'صفحة بلا سطر كود',
    userMsg: 'اجعل قائمة كتبي صفحة جميلة',
    badLabel: 'البرمجة تخيفني',
    formulaTitle: 'Claude\u00a0Code',
    steps: STEPS_AR,
    before: 'قائمة في ملف',
    after: 'صفحة في مجلدك',
    proResult: 'صفحة كتبك جاهزة',
    emailSubject: 'كتبي — صفحة',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep12_ar.wav',
  words: wAr,
};

export const EP12_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep12_en.wav',
  voiceDur: 28.89,
  cues: {problem: 5.12, typeAt: 5.44, badAt: 8.3, formula: 9.64, steps: [11.7, 15.36, 18.0], diff: 22.64, cta: 26.82},
  text: {
    stop: 'THIS?',
    hookSub: 'A page, zero code',
    userMsg: 'Turn my book list into a nice page',
    badLabel: 'Coding scares me',
    formulaTitle: 'Claude Code',
    steps: STEPS_EN,
    before: 'A plain list',
    after: 'A page in your folder',
    proResult: 'Your book page, ready',
    emailSubject: 'My books — page',
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep12_en.wav',
  words: wEn,
};
