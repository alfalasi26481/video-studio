export type Lang = 'ar' | 'en';

type Base = {
  narration: string;
  /** Optional voiceover clip in /public, e.g. "ep01/ar-1.mp3". Sets the scene length when present. */
  audio?: string;
  /** Optional screen recording in /public, shown instead of the drawn visual. */
  video?: string;
};

export type Scene =
  | (Base & {type: 'hook'; kicker: string; title: string; body?: string})
  | (Base & {type: 'prompt'; tone: 'bad' | 'good' | 'tip'; label: string; prompt: string})
  | (Base & {type: 'steps'; title: string; items: string[]})
  | (Base & {type: 'cta'; title: string; body?: string});

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
