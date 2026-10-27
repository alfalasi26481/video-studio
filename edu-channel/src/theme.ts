import '@fontsource/noto-kufi-arabic/700.css';
import '@fontsource/noto-kufi-arabic/800.css';
import '@fontsource/ibm-plex-sans-arabic/500.css';
import '@fontsource/ibm-plex-sans-arabic/600.css';
import '@fontsource/ibm-plex-mono/500.css';

// Channel look: a dark "chat screen" — the subject is typing to Claude, so the frame borrows a chat UI.
export const C = {
  bg: '#0f1b2d',
  bg2: '#16263f',
  panel: '#1c2f4d',
  line: '#2c4468',
  ink: '#eef2f8',
  muted: '#9fb0c8',
  accent: '#ffb547', // highlight, channel colour
  bad: '#ff7a7a',
  good: '#4fd1a5',
  tip: '#ffb547',
};

export const F = {
  display: '"Noto Kufi Arabic", "IBM Plex Sans Arabic", sans-serif',
  body: '"IBM Plex Sans Arabic", "Noto Kufi Arabic", sans-serif',
  mono: '"IBM Plex Mono", monospace',
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;

/** Words per second when no voiceover clip exists yet (estimate only). */
export const WPS = {ar: 2.2, en: 2.6} as const;
