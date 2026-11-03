import {COLORS} from '../engine/types';
import type {Step} from '../engine/types';
import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import wAr from './ep15_words_ar.json';
import wEn from './ep15_words_en.json';

// الحلقة 15 — شارك محادثتك برابط واحد / Share a chat with one link
// المحرك v2: ثيم electric + افتتاحية reveal + كسر نمط snap (لا يكرر EP14: gold/stop).
// معاينة: لقطات الحلقة 1 مؤقتاً حتى يقرر المالك لقطات EP15 الخاصة (48.75 رصيداً).
const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};
const style: Style = {theme: 'electric', hook: 'reveal', breaks: 'snap'};

const STEPS_AR: Step[] = [
  {n: '1', label: 'زر المشاركة', ex: 'أعلى المحادثة', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'مشاركة مرة ثانية', ex: 'ينشأ الرابط', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'أرسل الرابط', ex: 'بلا حساب، للقراءة', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Press Share', ex: 'Top of the chat', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Share again', ex: 'The link is made', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Send the link', ex: 'No account, view only', color: COLORS.green, icon: 'format'},
];

export const EP15_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep15_ar.wav',
  voiceDur: 32.41,
  cues: {problem: 5.38, typeAt: 5.78, badAt: 9.38, formula: 11.48, steps: [13.78, 16.96, 20.46], diff: 25.12, cta: 29.28},
  text: {
    stop: 'رابط؟',
    hookSub: 'المحادثة كلها لإخوتك',
    userMsg: 'خطة حفلة عيد ميلاد أمي',
    badLabel: 'نسخ طويل وصور كثيرة',
    formulaTitle: 'شارك برابط',
    steps: STEPS_AR,
    before: 'صور شاشة كثيرة',
    after: 'رابط واحد',
    proResult: 'الخطة عند الجميع',
    emailSubject: 'حفلة أمي — رابط',
    save: 'احفظ الفيديو',
    follow: 'تابعنا',
    daily: 'مهارة جديدة في كل حلقة',
    youLabel: 'أنت',
  },
  clips,
  music: 'music/ep15_ar.wav',
  words: wAr,
};

export const EP15_EN: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'en',
  dir: 'ltr',
  voice: 'vo/ep15_en.wav',
  voiceDur: 28.25,
  cues: {problem: 5.0, typeAt: 5.4, badAt: 9.04, formula: 10.76, steps: [13.28, 15.6, 18.2], diff: 22.12, cta: 25.76},
  text: {
    stop: 'LINK?',
    hookSub: 'The whole chat, shared',
    userMsg: "Plan mom's birthday party",
    badLabel: 'Too many screenshots',
    formulaTitle: 'Share a link',
    steps: STEPS_EN,
    before: 'Many screenshots',
    after: 'One link',
    proResult: 'Everyone has the plan',
    emailSubject: "Mom's party — link",
    save: 'Save this video',
    follow: 'Follow',
    daily: 'A new skill every episode',
    youLabel: 'You',
  },
  clips,
  music: 'music/ep15_en.wav',
  words: wEn,
};
