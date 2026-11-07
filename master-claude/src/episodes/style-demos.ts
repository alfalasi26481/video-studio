import type {EpisodeDataV2} from '../engine2/Episode';
import type {Style} from '../engine2/theme';
import {EP05_AR, EP05_EN} from './ep05';

/**
 * Engine v2 style demos — EP05 content re-dressed, for the owner's before/after approval only.
 * Not episodes: never published, not in the factory. Ids: DEMO-<theme>-<hook>-<LANG>.
 */
const STYLES: Style[] = [
  {theme: 'electric', hook: 'question', breaks: 'snap'},
  {theme: 'gold', hook: 'reveal', breaks: 'snap'},
  {theme: 'mint', hook: 'stop', breaks: 'snap'},
];

export const STYLE_DEMOS: Record<string, EpisodeDataV2> = Object.fromEntries(
  STYLES.flatMap((st) => [
    [`DEMO-${st.theme}-${st.hook}-AR`, {...EP05_AR, engine: 2 as const, style: st, text: {...EP05_AR.text, stop: st.hook === 'question' ? 'لماذا؟' : st.hook === 'reveal' ? 'هكذا؟' : EP05_AR.text.stop}}],
    [`DEMO-${st.theme}-${st.hook}-EN`, {...EP05_EN, engine: 2 as const, style: st, text: {...EP05_EN.text, stop: st.hook === 'question' ? 'WHY?' : st.hook === 'reveal' ? 'LIKE THIS?' : EP05_EN.text.stop}}],
  ]),
);
