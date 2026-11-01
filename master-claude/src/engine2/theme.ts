/**
 * Master Claude — engine v2 themes (from EP06 on; owner request 1 Nov 2026).
 * Engine v1 (src/engine/) stays frozen for EP01–EP05.
 * `ember` = the exact v1 palette, so a v2 episode with default style looks like v1.
 */
import {COLORS as V1} from '../engine/types';

export type Palette = {
  bg: string; bg2: string;
  orange: string; // main accent (name kept from v1 so the scene code reads the same)
  blue: string; green: string; purple: string; red: string; white: string; muted: string;
  accent2: string; // lighter end of accent gradients
  bar: string; // light end of the progress bar
  ink: string; // dark text on accent
  leak: string; // light-leak tint (6-digit hex)
  keySaid: string; // karaoke: key word after it was said
  particle: string; // background particles
  gold: string; // "magic line" highlight
  flash: string; // cut flash
  grade: string; // CSS filter on the AI clips so they sit in the palette ('none' = v1)
};

export const THEMES = {
  ember: {...V1, accent2: '#FF9A4D', bar: '#FFB066', ink: '#1A0E05', leak: '#FF3D7F', keySaid: '#FFD08A', particle: '#9FB6E6', gold: '#FFC861', flash: '#FFF6EC', grade: 'none'},
  electric: {bg: '#06061A', bg2: '#1A0F3D', orange: '#FF2E88', blue: '#00E5FF', green: '#B6FF3B', purple: '#8C5CFF', red: '#FF3B3B', white: '#F7F5FF', muted: '#9A93C4',
    accent2: '#FF7AB8', bar: '#FF7AB8', ink: '#1A0410', leak: '#00E5FF', keySaid: '#FFB3D6', particle: '#7FE9FF', gold: '#FFE45C', flash: '#F2F0FF', grade: 'hue-rotate(55deg) saturate(1.35)'},
  gold: {bg: '#0B0906', bg2: '#22180A', orange: '#FFC531', blue: '#2EE6D6', green: '#4BE38A', purple: '#FF8A3D', red: '#FF4D4D', white: '#FFF8EC', muted: '#B3A58A',
    accent2: '#FFE08A', bar: '#FFE08A', ink: '#1A1200', leak: '#FF8A3D', keySaid: '#FFE9A8', particle: '#E8D3A0', gold: '#2EE6D6', flash: '#FFF6E0', grade: 'sepia(0.55) saturate(1.5) hue-rotate(-12deg)'},
  mint: {bg: '#03100E', bg2: '#082A22', orange: '#2BFFB0', blue: '#5AB2FF', green: '#E8FF5A', purple: '#C08BFF', red: '#FF5577', white: '#F2FFFA', muted: '#86B3A6',
    accent2: '#9CFFDA', bar: '#9CFFDA', ink: '#00180F', leak: '#5AB2FF', keySaid: '#B8FFE4', particle: '#9FE8D2', gold: '#E8FF5A', flash: '#EFFFF8', grade: 'hue-rotate(-45deg) saturate(1.2)'},
} satisfies Record<string, Palette>;

export type ThemeName = keyof typeof THEMES;
export type HookKind = 'stop' | 'question' | 'reveal';
/** Visual pattern interrupt on each step + before/after: none (v1 behaviour) or a diagonal accent wipe. */
export type BreakKind = 'none' | 'snap';
export type Style = {theme: ThemeName; hook: HookKind; breaks: BreakKind};
export const DEFAULT_STYLE: Style = {theme: 'ember', hook: 'stop', breaks: 'none'};

let current: Palette = THEMES.ember;
/** Set once at the top of the v2 Episode render (Remotion renders one composition per tab). */
export const setTheme = (name: ThemeName) => {
  current = THEMES[name];
};
export const COLORS = new Proxy({} as Palette, {get: (_t, k: string) => current[k as keyof Palette]});

/** A v1 color (e.g. COLORS.orange imported from engine/types in episode data) -> the same role in the current theme. */
export const themed = (c: string) => {
  const k = (Object.keys(V1) as (keyof typeof V1)[]).find((key) => V1[key].toLowerCase() === c.toLowerCase());
  return k ? current[k] : c;
};
