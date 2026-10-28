import '@fontsource/ibm-plex-sans-arabic/500.css';
import '@fontsource/ibm-plex-sans-arabic/600.css';
import '@fontsource/ibm-plex-sans-arabic/700.css';
import '@fontsource/ibm-plex-sans/600.css';
import '@fontsource/ibm-plex-sans/700.css';
import '@fontsource/ibm-plex-mono/500.css';

// ---------------------------------------------------------------------------
// Design system v2 — one source of truth for colour, type and layout.
// Arabic and Latin share one family (IBM Plex Sans Arabic + IBM Plex Sans), so
// mixed sentences look like one voice. Mono is only for tags and code.
// ---------------------------------------------------------------------------

export const C = {
  bg: '#0e1a2c',
  bg2: '#14243d',
  panel: '#172a47',
  panel2: '#1d3456',
  line: '#2a4166',
  ink: '#eef2f8',
  muted: '#93a3bc',
  accent: '#ffb547', // channel colour: highlights, active word, progress
  sky: '#5ec8ff',
  violet: '#b49cff',
  good: '#4fd1a5',
  bad: '#ff7a7a',
  tip: '#ffb547',
};

export const F = {
  // Arabic glyphs come from Plex Sans Arabic; Latin falls through to Plex Sans.
  text: '"IBM Plex Sans Arabic", "IBM Plex Sans", sans-serif',
  latin: '"IBM Plex Sans", "IBM Plex Sans Arabic", sans-serif',
  mono: '"IBM Plex Mono", monospace',
  // kept for older scene code
  display: '"IBM Plex Sans Arabic", "IBM Plex Sans", sans-serif',
  body: '"IBM Plex Sans Arabic", "IBM Plex Sans", sans-serif',
};

/** Type scale (px on a 1080×1920 canvas). Nothing on screen goes below `micro`. */
export const T = {
  hero: 96,
  title: 72,
  head: 56,
  body: 46,
  label: 34,
  micro: 28,
  caption: 54,
};

/**
 * Layout grid. Right margin is wider: TikTok/Reels put their buttons there.
 * Everything below `safeBottom` is covered by the app's caption/description UI.
 */
export const L = {
  left: 72,
  right: 152,
  width: 1080 - 72 - 152,
  headerTop: 96,
  contentTop: 430,
  contentBottom: 1290,
  captionTop: 1318,
  safeBottom: 1500,
};

/** One colour per compared concept, in tab order (amber, sky, violet). */
export const TRIO = [C.accent, C.sky, C.violet];

export const FPS = 30;
export const W = 1080;
export const H = 1920;

/** Words per second when no voiceover clip exists yet (estimate only). */
export const WPS = {ar: 2.2, en: 2.6} as const;
