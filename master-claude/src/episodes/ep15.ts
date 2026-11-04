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
  {n: '1', label: 'زر المشاركة', ex: 'على الكمبيوتر، أعلى المحادثة', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'مشاركة مرة ثانية', ex: 'يظهر الرابط', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'أرسل الرابط', ex: 'بلا حساب، للقراءة', color: COLORS.green, icon: 'format'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Press Share', ex: 'Desktop, top of chat', color: COLORS.orange, icon: 'task'},
  {n: '2', label: 'Share again', ex: 'The link appears', color: COLORS.blue, icon: 'context'},
  {n: '3', label: 'Send the link', ex: 'No account, view only', color: COLORS.green, icon: 'format'},
];

export const EP15_AR: EpisodeDataV2 = {
  engine: 2,
  style,
  lang: 'ar',
  dir: 'rtl',
  voice: 'vo/ep15_ar.wav',
  voiceDur: 30.73,
  cues: {problem: 5.16, typeAt: 5.56, badAt: 8.72, formula: 10.62, steps: [12.7, 16.84, 19.96], diff: 24.28, cta: 27.78},
  text: {
    stop: 'رابط؟',
    hookSub: 'بلا نسخ ولا صور شاشة',
    userMsg: 'خطة حفلة أمي',
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
  voiceDur: 28.89,
  cues: {problem: 5.1, typeAt: 5.5, badAt: 8.88, formula: 10.92, steps: [13.2, 16.56, 19.32], diff: 23.3, cta: 26.62},
  text: {
    stop: 'LINK?',
    hookSub: 'No copy, no screenshots',
    userMsg: "Plan mom's party",
    badLabel: 'Screenshot chaos',
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
