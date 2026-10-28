import type {Scene} from './types';
import type {FlowSpec} from './Flow';

/**
 * Frame at which the voice says `needle` in this scene ("word#2" = second
 * occurrence). Uses the real word timings when the scene is synced; otherwise
 * estimates from the word's position in the narration.
 */
export const wordFrame = (s: Scene, needle: string, frames: number, fps: number): number | null => {
  const [want, nth] = needle.split('#');
  const n = nth ? Number(nth) : 1;
  const strip = (w: string) => w.replace(/[*.,،؟?:!؛]/g, '');
  const words = s.cues?.flatMap((c) => c.words ?? []) ?? [];
  if (words.length) {
    let seen = 0;
    for (const w of words) if (strip(w.t).includes(want) && ++seen === n) return Math.round(w.s * fps);
    return null;
  }
  const raw = s.narration.split(/\s+/);
  let seen = 0;
  for (let i = 0; i < raw.length; i++) if (strip(raw[i]).includes(want) && ++seen === n) return Math.round(((i + 0.3) / raw.length) * frames * 0.92);
  return null;
};

/** Turn word anchors into scene fractions so the diagram engine stays fraction-based. */
export const resolveSpec = (s: Scene, spec: FlowSpec, frames: number, fps: number): FlowSpec => ({
  ...spec,
  events: spec.events.map((e) => {
    if (!e.on) return e;
    const f = wordFrame(s, e.on, frames, fps);
    return f === null ? e : {...e, at: Math.max(0, f / frames + (e.at ?? 0))};
  }),
});

/** Delay (frames) for list item i: on its anchor word when given, else evenly spaced. */
export const itemDelay = (s: Scene, on: string[] | undefined, i: number, frames: number, fps: number, fallback: number) => {
  const w = on?.[i] ? wordFrame(s, on[i], frames, fps) : null;
  return w ?? fallback;
};
