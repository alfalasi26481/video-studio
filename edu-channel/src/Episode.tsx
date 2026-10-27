import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {C, F} from './theme';
import type {EpisodeProps, Lang, Scene} from './types';

// ---------- helpers ----------
const useIn = (delay = 0) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 18});
};

const levelLabel = (level: string, lang: Lang) => {
  const map: Record<string, [string, string]> = {
    beginner: ['مبتدئ', 'BEGINNER'], intermediate: ['متوسط', 'INTERMEDIATE'], pro: ['محترف', 'PRO'],
  };
  const v = map[level] ?? [level, level];
  return lang === 'ar' ? v[0] : v[1];
};

const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all([
      document.fonts.load('800 80px "Noto Kufi Arabic"', 'عربي'),
      document.fonts.load('700 80px "Noto Kufi Arabic"', 'عربي Ab'),
      document.fonts.load('600 40px "IBM Plex Sans Arabic"', 'عربي Ab'),
      document.fonts.load('500 40px "IBM Plex Sans Arabic"', 'عربي Ab'),
      document.fonts.load('500 30px "IBM Plex Mono"', '@ab'),
    ]).then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);
};

// ---------- frame chrome ----------
const TopBar: React.FC<{handle: string; level: string; lang: Lang; progress: number; segs: number[]}> = ({
  handle, level, lang, segs,
}) => {
  const frame = useCurrentFrame();
  let acc = 0;
  return (
    <div style={{position: 'absolute', top: 110, left: 80, right: 140, display: 'flex', flexDirection: 'column', gap: 28}}>
      <div style={{display: 'flex', gap: 10, direction: 'ltr'}}>
        {segs.map((len, i) => {
          const start = acc; acc += len;
          const fill = Math.min(1, Math.max(0, (frame - start) / len));
          return (
            <div key={i} style={{flex: len, height: 8, borderRadius: 4, background: C.line, overflow: 'hidden'}}>
              <div style={{width: `${fill * 100}%`, height: '100%', background: C.accent}} />
            </div>
          );
        })}
      </div>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <span style={{fontFamily: F.mono, fontSize: 34, color: C.muted, direction: 'ltr', unicodeBidi: 'plaintext'}}>{handle}</span>
        <span style={{fontFamily: F.display, fontWeight: 700, fontSize: 30, color: C.bg, background: C.accent,
          padding: '6px 22px', borderRadius: 999, letterSpacing: lang === 'en' ? 3 : 0}}>{levelLabel(level, lang)}</span>
      </div>
    </div>
  );
};

const Captions: React.FC<{text: string; frames: number; lang: Lang}> = ({text, frames, lang}) => {
  const frame = useCurrentFrame();
  const per = lang === 'ar' ? 3 : 4;
  const chunks: string[] = [];
  // Break at sentence/clause punctuation first, then into short groups.
  for (const phrase of text.split(/(?<=[.،,؟?:!])\s+/)) {
    const words = phrase.split(/\s+/).filter(Boolean);
    const n = Math.ceil(words.length / per);
    const size = Math.ceil(words.length / n);
    for (let i = 0; i < words.length; i += size) chunks.push(words.slice(i, i + size).join(' '));
  }
  const start = 6, end = Math.max(start + 1, frames - 10);
  const weights = chunks.map((c) => c.split(' ').length);
  const total = weights.reduce((a, b) => a + b, 0);
  let t = start, idx = chunks.length - 1;
  for (let i = 0; i < chunks.length; i++) {
    const len = ((end - start) * weights[i]) / total;
    if (frame < t + len) { idx = i; break; }
    t += len;
  }
  if (frame < start) return null;
  return (
    <div style={{position: 'absolute', left: 80, right: 140, top: 1330, display: 'flex', justifyContent: 'center'}}>
      <span style={{fontFamily: F.display, fontWeight: 800, fontSize: lang === 'ar' ? 58 : 56, lineHeight: 1.5,
        color: C.ink, background: 'rgba(8,14,26,0.82)', padding: '10px 30px', borderRadius: 18, textAlign: 'center',
        boxShadow: `inset 0 -6px 0 ${C.accent}`}}>
        {chunks[idx]}
      </span>
    </div>
  );
};

// ---------- scene bodies ----------
const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{position: 'absolute', top: 300, bottom: 640, left: 80, right: 140, display: 'flex',
    flexDirection: 'column', justifyContent: 'center', gap: 40}}>{children}</div>
);

const Hook: React.FC<{s: Extract<Scene, {type: 'hook'}>}> = ({s}) => {
  const a = useIn(0), b = useIn(8);
  return (
    <Stage>
      <div style={{fontFamily: F.display, fontWeight: 800, fontSize: 112, lineHeight: 1.35, color: C.ink,
        opacity: a, transform: `translateY(${(1 - a) * 40}px)`}}>{s.title}</div>
      {s.body && <div style={{fontFamily: F.body, fontWeight: 600, fontSize: 54, color: C.accent, opacity: b}}>{s.body}</div>}
    </Stage>
  );
};

const toneMark = {bad: '✕', good: '✓', tip: '★'} as const;

const Prompt: React.FC<{s: Extract<Scene, {type: 'prompt'}>; frames: number; dir: 'rtl' | 'ltr'}> = ({s, frames, dir}) => {
  const frame = useCurrentFrame();
  const a = useIn(0);
  const col = C[s.tone];
  const typeEnd = Math.min(frames * 0.6, 12 + s.prompt.length * 0.9);
  const shown = Math.round(interpolate(frame, [10, typeEnd], [0, s.prompt.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const done = shown >= s.prompt.length;
  const sendPop = spring({frame: frame - typeEnd - 4, fps: 30, config: {damping: 12}});
  return (
    <Stage>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: a}}>
        <span style={{width: 64, height: 64, borderRadius: 32, background: col, color: C.bg, display: 'grid',
          placeItems: 'center', fontSize: 38, fontWeight: 800, fontFamily: F.body}}>{toneMark[s.tone]}</span>
        <span style={{fontFamily: F.display, fontWeight: 700, fontSize: 52, color: col}}>{s.label}</span>
      </div>
      <div style={{background: C.panel, border: `3px solid ${col}`, borderRadius: 36, padding: '40px 44px 30px',
        opacity: a, transform: `scale(${0.96 + a * 0.04})`, display: 'flex', flexDirection: 'column', gap: 28}}>
        <div dir={dir} style={{fontFamily: F.body, fontWeight: 500, fontSize: s.prompt.length > 80 ? 46 : 58,
          lineHeight: 1.6, color: C.ink, minHeight: 90}}>
          {s.prompt.slice(0, shown)}
          {!done && <span style={{display: 'inline-block', width: 5, height: '1em', background: C.accent,
            marginInlineStart: 6, verticalAlign: 'middle', opacity: Math.floor(frame / 8) % 2 ? 0.2 : 1}} />}
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end', direction: 'ltr'}}>
          <span style={{width: 78, height: 78, borderRadius: 39, background: done ? C.accent : C.line, color: C.bg,
            display: 'grid', placeItems: 'center', fontSize: 44, fontWeight: 800,
            transform: `scale(${done ? 1 + (sendPop - 1) * 0.3 : 1})`}}>↑</span>
        </div>
      </div>
    </Stage>
  );
};

const Steps: React.FC<{s: Extract<Scene, {type: 'steps'}>; frames: number}> = ({s, frames}) => {
  const a = useIn(0);
  const gap = Math.max(10, Math.floor((frames * 0.55) / s.items.length));
  return (
    <Stage>
      <div style={{fontFamily: F.display, fontWeight: 800, fontSize: 92, color: C.ink, opacity: a}}>{s.title}</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 26}}>
        {s.items.map((it, i) => <StepRow key={i} n={i + 1} text={it} delay={14 + i * gap} />)}
      </div>
    </Stage>
  );
};
const StepRow: React.FC<{n: number; text: string; delay: number}> = ({n, text, delay}) => {
  const p = useIn(delay);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 28, background: C.bg2, border: `2px solid ${C.line}`,
      borderRadius: 28, padding: '26px 30px', opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>
      <span style={{fontFamily: F.mono, fontSize: 48, color: C.bg, background: C.accent, width: 80, height: 80,
        borderRadius: 20, display: 'grid', placeItems: 'center', flexShrink: 0}}>{n}</span>
      <span style={{fontFamily: F.body, fontWeight: 600, fontSize: 54, color: C.ink, lineHeight: 1.4}}>{text}</span>
    </div>
  );
};

const Cta: React.FC<{s: Extract<Scene, {type: 'cta'}>; handle: string}> = ({s, handle}) => {
  const a = useIn(0), b = useIn(10), c = useIn(20);
  return (
    <Stage>
      <div style={{fontFamily: F.display, fontWeight: 800, fontSize: 120, color: C.accent, opacity: a,
        transform: `scale(${0.9 + a * 0.1})`}}>{s.title}</div>
      {s.body && <div style={{fontFamily: F.body, fontWeight: 600, fontSize: 56, color: C.ink, lineHeight: 1.5, opacity: b}}>{s.body}</div>}
      <div style={{fontFamily: F.mono, fontSize: 52, color: C.muted, direction: 'ltr', unicodeBidi: 'plaintext', opacity: c}}>{handle}</div>
    </Stage>
  );
};

const SceneView: React.FC<{s: Scene; frames: number; lang: Lang; dir: 'rtl' | 'ltr'; handle: string}> = ({s, frames, lang, dir, handle}) => {
  const frame = useCurrentFrame();
  const fadeOut = interpolate(frame, [frames - 8, frames], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: fadeOut}}>
      {s.video ? (
        <div style={{position: 'absolute', top: 280, bottom: 620, left: 80, right: 140, borderRadius: 36, overflow: 'hidden',
          border: `3px solid ${C.line}`}}>
          <OffthreadVideo src={staticFile(s.video)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      ) : s.type === 'hook' ? <Hook s={s} />
        : s.type === 'prompt' ? <Prompt s={s} frames={frames} dir={dir} />
        : s.type === 'steps' ? <Steps s={s} frames={frames} />
        : <Cta s={s} handle={handle} />}
      <Captions text={s.narration} frames={frames} lang={lang} />
      {s.audio && <Audio src={staticFile(s.audio)} />}
    </AbsoluteFill>
  );
};

// ---------- composition ----------
export const Episode: React.FC<EpisodeProps> = ({lang, episode, sceneFrames}) => {
  useFonts();
  const track = episode[lang];
  const frames = sceneFrames ?? track.scenes.map(() => 90);
  let from = 0;
  return (
    <AbsoluteFill dir={track.dir} style={{background: `radial-gradient(120% 70% at 50% 35%, ${C.bg2} 0%, ${C.bg} 70%)`,
      fontFamily: F.body, color: C.ink}}>
      {track.scenes.map((s, i) => {
        const seq = (
          <Sequence key={i} from={from} durationInFrames={frames[i]} name={`${i + 1}-${s.type}`}>
            <SceneView s={s} frames={frames[i]} lang={lang} dir={track.dir} handle={episode.channel[lang]} />
          </Sequence>
        );
        from += frames[i];
        return seq;
      })}
      <TopBar handle={episode.channel[lang]} level={episode.level} lang={lang} progress={0} segs={frames} />
    </AbsoluteFill>
  );
};
