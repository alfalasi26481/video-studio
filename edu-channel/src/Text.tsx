import React from 'react';
import {C, F} from './theme';

// Bidi-safe text. Mixed Arabic + English sentences break in the browser's
// default bidi algorithm: "الأول Skill:" renders as ":Skill الأول", and a
// lone "و" before an English word drifts. Every run of Latin text is isolated
// in its own <bdi dir="ltr">, and the whole line is isolated in the base
// direction, so punctuation stays with the sentence it belongs to.
//
// *word* marks an emphasised word (accent colour), used in hooks and titles.

const W1 = String.raw`[A-Za-z0-9](?:[A-Za-z0-9._+#@/\-]*[A-Za-z0-9+#])?`;
// Latin words joined by spaces or neutral separators (· & / -) form ONE run, so
// "Sonnet · Haiku" never flips in RTL; a run ends on a letter/digit so sentence
// punctuation ("Claude،" "Haiku.") stays with the Arabic sentence.
const LATIN_RUN = new RegExp(String.raw`(${W1}(?:\s*[·&/–-]\s*${W1}|\s+${W1})*)`, 'g');

type Piece = {text: string; latin: boolean; em: boolean};

export const splitRuns = (text: string): Piece[] => {
  const out: Piece[] = [];
  // emphasis first
  const parts = text.split(/(\*[^*]+\*)/g).filter(Boolean);
  for (const part of parts) {
    const em = part.startsWith('*') && part.endsWith('*');
    const body = em ? part.slice(1, -1) : part;
    let last = 0;
    for (const m of body.matchAll(LATIN_RUN)) {
      const i = m.index ?? 0;
      // Digits inside Arabic text stay Arabic-context (e.g. "مهمة 1") unless they touch Latin letters.
      if (!/[A-Za-z]/.test(m[0])) continue;
      if (i > last) out.push({text: body.slice(last, i), latin: false, em});
      out.push({text: m[0], latin: true, em});
      last = i + m[0].length;
    }
    if (last < body.length) out.push({text: body.slice(last), latin: false, em});
  }
  return out;
};

export const BiText: React.FC<{
  text: string;
  dir: 'rtl' | 'ltr';
  style?: React.CSSProperties;
  emColor?: string;
  latinStyle?: React.CSSProperties;
}> = ({text, dir, style, emColor = C.accent, latinStyle}) => (
  <span dir={dir} style={{unicodeBidi: 'isolate', fontFamily: F.text, ...style}}>
    {splitRuns(text).map((p, i) =>
      p.latin ? (
        <bdi key={i} dir="ltr" style={{fontFamily: F.latin, color: p.em ? emColor : undefined, ...latinStyle}}>{p.text}</bdi>
      ) : (
        <span key={i} style={{color: p.em ? emColor : undefined}}>{p.text}</span>
      ),
    )}
  </span>
);

/** Plain text for measuring / TTS (emphasis markers removed). */
export const plain = (t: string) => t.replace(/\*/g, '');

const ARABIC = /[ء-ي٠-٩]/;
export const isLatin = (w: string) => /[A-Za-z]/.test(w) && !ARABIC.test(w);

export type Tok = {text: string; latin: boolean; em: boolean; n: number};

/**
 * Words of one line as display tokens. Consecutive Latin words are merged into
 * ONE token: each token is an inline-block (so it can animate), and a row of
 * inline-blocks follows the paragraph direction — "Claude Code" as two tokens
 * in an RTL line would read "Code Claude". `n` = how many words it holds.
 */
export const tokens = (line: string): Tok[] => {
  const out: Tok[] = [];
  for (const part of line.split(/(\*[^*]+\*)/g).filter(Boolean)) {
    const em = part.startsWith('*') && part.endsWith('*');
    for (const w of (em ? part.slice(1, -1) : part).split(/\s+/).filter(Boolean)) {
      const latin = isLatin(w);
      const last = out[out.length - 1];
      if (latin && last && last.latin && last.em === em) { last.text += ' ' + w; last.n += 1; }
      else out.push({text: w, latin, em, n: 1});
    }
  }
  return out;
};
