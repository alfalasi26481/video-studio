import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {C, F, TRIO} from './theme';
import type {EpisodeProps, Lang, Scene} from './types';
import {Backdrop, Flow, Icon} from './Flow';
import {Mascot} from './Mascot';

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

const Captions: React.FC<{text: string; frames: number; lang: Lang; cues?: {text: string; start: number; end: number}[]; left: number}> = ({text, frames, lang, cues, left}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  let items: {text: string; at: number}[];
  if (cues && cues.length) {
    // Timed to the real voice: each chunk appears on its first spoken word.
    items = cues.map((c) => ({text: c.text, at: Math.round(c.start * fps)}));
  } else {
    // No voiceover yet: spread chunks over the scene by word count.
    const per = lang === 'ar' ? 3 : 4;
    const chunks: string[] = [];
    for (const phrase of text.split(/(?<=[.،,؟?:!])\s+/)) {
      const words = phrase.split(/\s+/).filter(Boolean);
      const n = Math.ceil(words.length / per);
      const size = Math.ceil(words.length / n);
      for (let i = 0; i < words.length; i += size) chunks.push(words.slice(i, i + size).join(' '));
    }
    const start = 6, end = Math.max(start + 1, frames - 10);
    const total = chunks.reduce((a, c) => a + c.split(' ').length, 0);
    let t = start;
    items = chunks.map((c) => { const at = Math.round(t); t += ((end - start) * c.split(' ').length) / total; return {text: c, at}; });
  }
  let idx = -1;
  for (let i = 0; i < items.length; i++) if (frame >= items[i].at) idx = i;
  if (idx < 0) return null;
  const pop = spring({frame: frame - items[idx].at, fps, config: {damping: 12, stiffness: 220}});
  return (
    <div style={{position: 'absolute', left, right: 140, top: 1330, display: 'flex', justifyContent: 'center'}}>
      <span style={{fontFamily: F.display, fontWeight: 800, fontSize: lang === 'ar' ? 58 : 56, lineHeight: 1.5,
        color: C.ink, background: 'rgba(8,14,26,0.82)', padding: '10px 30px', borderRadius: 18, textAlign: 'center',
        boxShadow: `inset 0 -6px 0 ${C.accent}`, scale: String(0.85 + 0.15 * pop), translate: `0 ${(1 - pop) * 14}px`}}>
        {items[idx].text}
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
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = useIn(0), b = useIn(10), c = useIn(20);
  // The save icon drops in, then "taps" itself: fills and bounces once.
  const drop = spring({frame: frame - 4, fps, config: {damping: 8, stiffness: 120}});
  const tap = spring({frame: frame - 28, fps, config: {damping: 6, stiffness: 200}});
  const ring = interpolate(frame, [28, 52], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Stage>
      <div style={{alignSelf: 'center', position: 'relative', width: 220, height: 220, translate: `0 ${(1 - drop) * -260}px`}}>
        {ring > 0 && ring < 1 && <div style={{position: 'absolute', inset: -ring * 70, borderRadius: '50%',
          border: `5px solid ${C.accent}`, opacity: 1 - ring}} />}
        <div style={{position: 'absolute', inset: 0, borderRadius: 56, background: frame > 30 ? C.accent : C.panel,
          border: `5px solid ${C.accent}`, display: 'grid', placeItems: 'center', scale: String(1 + (tap - 1) * 0.25)}}>
          <Icon name="bookmark" color={frame > 30 ? C.bg : C.accent} size={120} />
        </div>
      </div>
      <div style={{fontFamily: F.display, fontWeight: 800, fontSize: 110, color: C.accent, opacity: a, textAlign: 'center',
        scale: String(0.9 + a * 0.1)}}>{s.title}</div>
      {s.body && <div style={{fontFamily: F.body, fontWeight: 600, fontSize: 52, color: C.ink, lineHeight: 1.5, opacity: b,
        textAlign: 'center'}}>{s.body}</div>}
      <div style={{fontFamily: F.mono, fontSize: 48, color: C.muted, direction: 'ltr', unicodeBidi: 'plaintext', opacity: c,
        textAlign: 'center'}}>{handle}</div>
    </Stage>
  );
};

// ---------- comparison format ----------
// The tab bar is the viewer's map: it stays put across the set and lights the
// concept being explained, so the viewer always knows "where" they are.
const TabBar: React.FC<{tabs: string[]; active: number}> = ({tabs, active}) => {
  const a = useIn(0);
  return (
    <div style={{display: 'flex', gap: 14, direction: 'ltr', opacity: 0.4 + a * 0.6}}>
      {tabs.map((t, i) => {
        const on = i === active;
        const col = TRIO[i % TRIO.length];
        return (
          <div key={i} style={{flex: 1, textAlign: 'center', padding: '18px 8px', borderRadius: 20,
            fontFamily: F.mono, fontSize: 34, letterSpacing: 2, color: on ? col : C.muted,
            background: on ? C.panel : 'transparent', border: `3px solid ${on ? col : C.line}`,
            boxShadow: on ? `inset 0 -8px 0 ${col}` : 'none'}}>{t}</div>
        );
      })}
    </div>
  );
};

const Compare: React.FC<{s: Extract<Scene, {type: 'compare'}>}> = ({s}) => {
  const col = TRIO[s.active % TRIO.length];
  const a = useIn(4), b = useIn(14), c = useIn(26), d = useIn(40);
  return (
    <div style={{position: 'absolute', top: 290, bottom: 620, left: 80, right: 140, display: 'flex',
      flexDirection: 'column', gap: 34}}>
      <TabBar tabs={s.tabs} active={s.active} />
      <div style={{fontFamily: F.mono, fontWeight: 500, fontSize: 104, color: col, direction: 'ltr', textAlign: 'center',
        opacity: a, transform: `scale(${0.92 + a * 0.08})`, marginTop: 10}}>{s.term}</div>
      <div style={{fontFamily: F.display, fontWeight: 700, fontSize: 58, lineHeight: 1.5, color: C.ink, textAlign: 'center',
        opacity: b}}>{s.def}</div>
      <div style={{alignSelf: 'center', fontFamily: F.body, fontWeight: 600, fontSize: 44, color: col,
        border: `2px dashed ${col}`, borderRadius: 999, padding: '10px 32px', opacity: c}}>{s.analogy}</div>
      <div style={{background: C.bg2, border: `2px solid ${C.line}`, borderRadius: 28, padding: '24px 30px',
        display: 'flex', flexDirection: 'column', gap: 8, opacity: d, transform: `translateY(${(1 - d) * 24}px)`}}>
        <span style={{fontFamily: F.display, fontWeight: 700, fontSize: 32, color: C.muted}}>{s.exampleLabel}</span>
        <span style={{fontFamily: F.body, fontWeight: 600, fontSize: 46, lineHeight: 1.45, color: C.ink}}>{s.example}</span>
      </div>
    </div>
  );
};

const Trio: React.FC<{s: Extract<Scene, {type: 'trio'}>; frames: number}> = ({s, frames}) => {
  const a = useIn(0);
  const gap = Math.max(8, Math.floor((frames * 0.5) / s.items.length));
  return (
    <Stage>
      <div style={{fontFamily: F.display, fontWeight: 800, fontSize: 80, color: C.ink, opacity: a}}>{s.title}</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 22}}>
        {s.items.map((it, i) => <TrioRow key={i} i={i} term={it.term} rule={it.rule} delay={12 + i * gap} />)}
      </div>
    </Stage>
  );
};
const TRIO_ICONS = ['doc', 'bot', 'plan'] as const;
const TrioRow: React.FC<{i: number; term: string; rule: string; delay: number}> = ({i, term, rule, delay}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useIn(delay);
  const pop = spring({frame: frame - delay - 6, fps, config: {damping: 9, stiffness: 160}});
  const sweep = interpolate(frame, [delay + 10, delay + 34], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const col = TRIO[i % TRIO.length];
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 24, background: C.bg2, borderRadius: 26,
      border: `3px solid ${col}`, padding: '20px 26px', opacity: p, translate: `${(1 - p) * (i % 2 ? -120 : 120)}px 0`,
      position: 'relative', overflow: 'hidden'}}>
      <div style={{position: 'absolute', insetInlineStart: 0, bottom: 0, height: 6, width: `${sweep * 100}%`, background: col}} />
      <div style={{width: 96, height: 96, borderRadius: 24, background: C.panel, border: `3px solid ${col}`, flexShrink: 0,
        display: 'grid', placeItems: 'center', scale: String(pop), rotate: `${(1 - pop) * -25}deg`}}>
        <Icon name={TRIO_ICONS[i % 3]} color={col} size={56} />
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0}}>
        <span style={{fontFamily: F.mono, fontSize: 40, color: col, direction: 'ltr', unicodeBidi: 'plaintext'}}>{term}</span>
        <span style={{fontFamily: F.body, fontWeight: 600, fontSize: 46, lineHeight: 1.4, color: C.ink}}>{rule}</span>
      </div>
    </div>
  );
};

const FlowScene: React.FC<{s: Extract<Scene, {type: 'flow'}>; frames: number}> = ({s, frames}) => {
  const col = s.active !== undefined ? TRIO[s.active % TRIO.length] : C.accent;
  const a = useIn(2), b = useIn(10);
  return (
    <>
      <div style={{position: 'absolute', top: 290, left: 80, right: 140, display: 'flex', flexDirection: 'column', gap: 18}}>
        {s.tabs && <TabBar tabs={s.tabs} active={s.active ?? 0} />}
        {s.term && (
          <div style={{display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 22, flexWrap: 'wrap'}}>
            <span style={{fontFamily: F.mono, fontSize: 64, color: col, direction: 'ltr', opacity: a,
              translate: `0 ${(1 - a) * 30}px`}}>{s.term}</span>
            {s.def && <span style={{fontFamily: F.display, fontWeight: 700, fontSize: 40, color: C.ink, opacity: b,
              textAlign: 'center'}}>{s.def}</span>}
          </div>
        )}
      </div>
      {/* Tabs + headline take ~270px; the canvas starts below them. */}
      <Flow spec={s.spec} frames={frames} top={s.tabs ? 560 : 500} />
    </>
  );
};

const SceneView: React.FC<{s: Scene; frames: number; lang: Lang; dir: 'rtl' | 'ltr'; handle: string}> = ({s, frames, lang, dir, handle}) => {
  const frame = useCurrentFrame();
  const fadeOut = interpolate(frame, [frames - 8, frames], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: fadeOut}}>
      {s.bg && (
        <AbsoluteFill style={{opacity: s.bgOpacity ?? 0.35}}>
          <Img src={staticFile(s.bg)} style={{width: '100%', height: '100%', objectFit: 'cover',
            scale: String(interpolate(frame, [0, frames], [1.04, 1.14])), translate: `0 ${s.bgY ?? 0}px`}} />
          <AbsoluteFill style={{background: `linear-gradient(180deg, ${C.bg}00 30%, ${C.bg} 92%)`}} />
        </AbsoluteFill>
      )}
      {s.video ? (
        <div style={{position: 'absolute', top: 280, bottom: 620, left: 80, right: 140, borderRadius: 36, overflow: 'hidden',
          border: `3px solid ${C.line}`}}>
          <OffthreadVideo src={staticFile(s.video)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      ) : s.type === 'hook' ? <Hook s={s} />
        : s.type === 'prompt' ? <Prompt s={s} frames={frames} dir={dir} />
        : s.type === 'steps' ? <Steps s={s} frames={frames} />
        : s.type === 'compare' ? <Compare s={s} />
        : s.type === 'trio' ? <Trio s={s} frames={frames} />
        : s.type === 'flow' ? <FlowScene s={s} frames={frames} />
        : <Cta s={s} handle={handle} />}
      {/* The presenter appears whenever the scene has a real voiceover. */}
      {s.audio && <Mascot audio={s.audio} pose={s.type === 'flow' && s.tabs ? 'idle' : 'present'}
        size={s.type === 'cta' ? 300 : 215} x={s.type === 'cta' ? 50 : 30} y={s.type === 'cta' ? 1180 : 1290} flip delay={4} />}
      <Captions text={s.narration} frames={frames} lang={lang} cues={s.cues} left={s.audio ? 280 : 80} />
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
      <Backdrop />
      {track.scenes.map((s, i) => {
        const seq = (
          <Sequence key={i} from={from} durationInFrames={frames[i]} name={`${i + 1}-${s.type}`}>
            <SceneView s={s} frames={frames[i]} lang={lang} dir={track.dir} handle={episode.channel[lang]} />
          </Sequence>
        );
        from += frames[i];
        return seq;
      })}
      {/* Soft music bed under the voice (generated in-house, royalty-free). */}
      {track.scenes.some((x) => x.audio) && <Audio src={staticFile('brand/bed.mp3')} volume={0.07} loop />}
      <TopBar handle={episode.channel[lang]} level={episode.level} lang={lang} progress={0} segs={frames} />
    </AbsoluteFill>
  );
};
