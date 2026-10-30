/**
 * Master Claude — engine types & design tokens.
 * DO NOT change colors, FPS or TAIL: they define the approved look of every episode.
 */
export type Lang = 'ar' | 'en';

export const COLORS = {
  bg: '#070B14',
  bg2: '#0F1A2E',
  orange: '#FF7A1A',
  blue: '#3B9CFF',
  green: '#22D39A',
  purple: '#A77BFF',
  red: '#FF4D5E',
  white: '#F5F7FB',
  muted: '#8A96B2',
};

export type IconKind = 'role' | 'task' | 'context' | 'format' | 'budget' | 'heart';
export type Step = {n: string; label: string; ex: string; color: string; icon: IconKind};

export type EpisodeData = {
  lang: Lang;
  dir: 'rtl' | 'ltr';
  /** public/ path, e.g. vo/ep03_ar.wav */
  voice: string;
  /** exact voiceover duration in seconds (ffprobe) */
  voiceDur: number;
  /** scene cue times in seconds, taken from whisper word timings */
  cues: {
    problem: number; // start of scene 2 (chat UI)
    typeAt: number; // the weak prompt starts typing
    badAt: number; // generic reply appears (stamp hits +10 frames)
    formula: number; // start of scene 3 (solution) — music drop lands here
    steps: number[]; // each card fills at the moment its word is spoken (3 or 4)
    diff: number; // start of scene 4 (before/after)
    cta: number; // start of scene 5 (save/follow)
  };
  text: {
    stop: string;
    hookSub: string;
    userMsg: string;
    badLabel: string;
    formulaTitle: string;
    steps: Step[];
    before: string;
    after: string;
    proResult: string;
    emailSubject: string;
    save: string;
    follow: string;
    daily: string;
    youLabel: string;
  };
  /** public/ paths of the 5 AI clips */
  clips: {hook: string; glitch: string; mid: string; burst: string; outro: string};
  /** public/ path of the music track (scripts/music.py output) */
  music: string;
  /** karaoke captions: [{start, end, words:[[t, word], ...]}] from scripts/captions.py */
  words: unknown;
  /** optional: "magic line" variant of scene 3 */
  magic?: {label: string; line: string; at: number; asks: string; asksAt: number};
  /** optional: chips shown in the "after" card (default = step labels) */
  chips?: string[];
};

export const FPS = 30;
export const TAIL = 1.2;
