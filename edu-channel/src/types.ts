import type {FlowSpec} from './Flow';

export type Lang = 'ar' | 'en';

type Base = {
  narration: string;
  /** Optional voiceover clip in /public, e.g. "ep01/ar-1.mp3". Sets the scene length when present. */
  audio?: string;
  /** Optional screen recording in /public, shown instead of the drawn visual. */
  video?: string;
  /** Caption chunks timed to the voiceover (seconds from scene start), written by scripts/sync-audio.py. */
  cues?: {text: string; start: number; end: number}[];
  /** Optional background art in /public (e.g. Higgsfield plate), slow zoom; bgOpacity 0..1. */
  bg?: string;
  bgOpacity?: number;
  /** Push the art down (px) so its subject sits under the headline. */
  bgY?: number;
};

export type Scene =
  | (Base & {type: 'hook'; kicker: string; title: string; body?: string})
  | (Base & {type: 'prompt'; tone: 'bad' | 'good' | 'tip'; label: string; prompt: string})
  | (Base & {type: 'steps'; title: string; items: string[]})
  | (Base & {type: 'cta'; title: string; body?: string})
  /** One concept of a 2–3 way comparison; the tab bar stays on screen across the set. */
  | (Base & {type: 'compare'; tabs: string[]; active: number; term: string; def: string; analogy: string; example: string; exampleLabel: string})
  /** Closing card: every compared concept with its one-line "use it when" rule. */
  | (Base & {type: 'trio'; title: string; items: {term: string; rule: string}[]})
  /** Motion diagram: boxes, drawn arrows, travelling packets; optional tab bar + headline above. */
  | (Base & {type: 'flow'; tabs?: string[]; active?: number; term?: string; def?: string; spec: FlowSpec});

export type LangTrack = {
  dir: 'rtl' | 'ltr';
  caption: string;
  hashtags: string[];
  scenes: Scene[];
};

export type EpisodeData = {
  id: string;
  level: string;
  topic: string;
  channel: Record<Lang, string>;
  ar: LangTrack;
  en: LangTrack;
};

export type EpisodeProps = {
  lang: Lang;
  episode: EpisodeData;
  /** Filled by calculateMetadata: frames per scene. */
  sceneFrames?: number[];
};
