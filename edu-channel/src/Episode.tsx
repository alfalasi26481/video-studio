import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {C, F, L, T, TRIO} from './theme';
import type {Cue, EpisodeProps, Lang, Scene} from './types';
import {Backdrop, Flow, Icon, flowSfx} from './Flow';
import type {IconName} from './Flow';
import {Mascot} from './Mascot';
import {BiText, isLatin, tokens} from './Text';
import {itemDelay, resolveSpec} from './timing';

type Dir = 'rtl' | 'ltr';

// ---------- helpers ----------
const useIn = (delay = 0, dur = 18) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: dur});
};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

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
    const AR = 'عربي ابجد', LA = 'Claude Ab@1';
    Promise.all([
      document.fonts.load(`700 80px "IBM Plex Sans Arabic"`, AR),
      document.fonts.load(`600 40px "IBM Plex Sans Arabic"`, AR),
      document.fonts.load(`500 40px "IBM Plex Sans Arabic"`, AR),
      document.fonts.load(`700 80px "IBM Plex Sans"`, LA),
      document.fonts.load(`600 40px "IBM Plex Sans"`, LA),
      document.fonts.load(`500 30px "IBM Plex Mono"`, LA),
    ]).then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);
};

// ---------- sound design ----------
type SfxKind = 'pop' | 'swish' | 'tick' | 'whoosh' | 'type' | 'send';
const SFX_VOL: Record<SfxKind, number> = {pop: 0.26, swish: 0.16, tick: 0.3, whoosh: 0.2, type: 0.18, send: 0.3};
const Sfx: React.FC<{at: number; kind: SfxKind; dur?: number; loop?: boolean}> = ({at, kind, dur = 40, loop}) => (
  <Sequence from={Math.max(0, Math.round(at))} durationInFrames={Math.max(1, Math.round(dur))} layout="none">
    <Audio src={staticFile(`sfx/${kind}.mp3`)} volume={SFX_VOL[kind]} loop={loop} />
  </Sequence>
);

// ---------- frame chrome ----------
const TopBar: React.FC<{handle: string; level: string; lang: Lang; segs: number[]}> = ({handle, level, lang, segs}) => {
  const frame = useCurrentFrame();
  let acc = 0;
  return (
    <div style={{position: 'absolute', top: L.headerTop, left: L.left, right: L.right, display: 'flex', flexDirection: 'column', gap: 26}}>
      {/* story-style progress, one segment per scene, filling in reading direction */}
      <div style={{display: 'flex', gap: 10}}>
        {segs.map((len, i) => {
          const start = acc; acc += len;
          const fill = Math.min(1, Math.max(0, (frame - start) / len));
          return (
            <div key={i} style={{flex: len, height: 7, borderRadius: 4, background: C.line, overflow: 'hidden'}}>
              <div style={{width: `${fill * 100}%`, height: '100%', background: C.accent}} />
            </div>
          );
        })}
      </div>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <bdi style={{fontFamily: F.latin, fontWeight: 600, fontSize: T.micro + 2, color: C.muted, letterSpacing: 0.5}}>{handle}</bdi>
        <span style={{fontFamily: F.text, fontWeight: 700, fontSize: T.micro, color: C.bg, background: C.accent,
          padding: '6px 22px', borderRadius: 999, letterSpacing: lang === 'en' ? 3 : 0}}>{levelLabel(level, lang)}</span>
      </div>
    </div>
  );
};

/**
 * Karaoke captions: the phrase being spoken, the current word lit in the
 * channel colour, words not yet spoken dimmed. Timings are the voice's own
 * (whisper word stamps), so the highlight never runs ahead of the speaker.
 */
const Captions: React.FC<{text: string; frames: number; lang: Lang; dir: Dir; cues?: Cue[]; left: number}> = ({
  text, frames, lang, dir, cues, left,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  let items: Cue[];
  if (cues && cues.length) items = cues;
  else {
    // No voiceover yet: spread chunks over the scene by word count (preview only).
    const per = lang === 'ar' ? 4 : 5;
    const chunks: string[] = [];
    for (const phrase of text.split(/(?<=[.،,؟?:!])\s+/)) {
      const w = phrase.split(/\s+/).filter(Boolean);
      for (let i = 0; i < w.length; i += per) chunks.push(w.slice(i, i + per).join(' '));
    }
    const total = chunks.reduce((a, c) => a + c.split(' ').length, 0);
    const span = (frames - 16) / fps;
    let acc = 0.2;
    items = chunks.map((c) => { const d = (span * c.split(' ').length) / total; const cue = {text: c, start: acc, end: acc + d}; acc += d; return cue; });
  }
  let idx = -1;
  for (let i = 0; i < items.length; i++) if (t >= items[i].start - 0.06) idx = i;
  if (idx < 0) return null;
  const cue = items[idx];
  const next = items[idx + 1];
  if (t > cue.end + 0.7 && (!next || t < next.start - 0.06)) return null; // pause in speech → clear screen

  // per-word timing (fallback: spread evenly over the cue)
  const raw = cue.text.split(/\s+/).filter(Boolean);
  const words = cue.words && cue.words.length === raw.length
    ? cue.words.map((w, i) => ({t: raw[i], s: w.s, e: w.e}))
    : raw.map((w, i) => ({t: w, s: cue.start + ((cue.end - cue.start) * i) / raw.length, e: cue.start + ((cue.end - cue.start) * (i + 1)) / raw.length}));
  // merge consecutive Latin words so their order survives inside an RTL line
  const groups: {t: string; s: number; e: number}[] = [];
  for (const w of words) {
    const last = groups[groups.length - 1];
    if (last && isLatin(w.t) && isLatin(last.t)) { last.t += ' ' + w.t; last.e = w.e; } else groups.push({...w});
  }

  const pop = spring({frame: frame - Math.round(cue.start * fps), fps, config: {damping: 14, stiffness: 240}});
  return (
    <div style={{position: 'absolute', left, right: L.right, top: L.captionTop, display: 'flex', justifyContent: 'center'}}>
      <div dir={dir} style={{fontFamily: F.text, fontWeight: 700, fontSize: lang === 'ar' ? T.caption : T.caption - 4,
        lineHeight: 1.45, textAlign: 'center', textWrap: 'balance', maxWidth: '100%',
        opacity: Math.min(1, pop * 1.6), translate: `0 ${(1 - pop) * 12}px`,
        textShadow: '0 3px 0 rgba(4,9,18,.9), 0 6px 26px rgba(4,9,18,.85)'} as React.CSSProperties}>
        {groups.map((g, i) => {
          const spoken = t >= g.s - 0.04;
          const active = spoken && (i === groups.length - 1 ? t <= cue.end + 0.25 : t < groups[i + 1].s - 0.04);
          const col = active ? C.accent : spoken ? C.ink : 'rgba(238,242,248,.42)';
          // trailing punctuation belongs to the sentence, not inside the English run
          const m = isLatin(g.t) ? g.t.match(/^(.*?[A-Za-z0-9+#])([^A-Za-z0-9+#]*)$/) : null;
          const node = m
            ? <><bdi dir="ltr" style={{fontFamily: F.latin, color: col}}>{m[1]}</bdi><span style={{color: col}}>{m[2]}</span></>
            : <span style={{color: col}}>{g.t}</span>;
          return <React.Fragment key={i}>{i > 0 && ' '}{node}</React.Fragment>;
        })}
      </div>
    </div>
  );
};

// ---------- building blocks ----------
const Stage: React.FC<{children: React.ReactNode; top?: number; bottom?: number; gap?: number}> = ({children, top = 300, bottom = L.contentBottom, gap = 40}) => (
  <div style={{position: 'absolute', top, height: bottom - top, left: L.left, right: L.right, display: 'flex',
    flexDirection: 'column', justifyContent: 'center', gap}}>{children}</div>
);

/** A title that honours manual line breaks (\n) and balances the rest. */
const Title: React.FC<{text: string; dir: Dir; size: number; color?: string; align?: 'center' | 'start'; style?: React.CSSProperties}> = ({
  text, dir, size, color = C.ink, align = 'start', style,
}) => (
  <div style={{fontFamily: F.text, fontWeight: 700, fontSize: size, lineHeight: 1.3, color, textAlign: align,
    textWrap: 'balance', ...style} as React.CSSProperties}>
    {text.split('\n').map((ln, i) => <div key={i}><BiText text={ln} dir={dir} /></div>)}
  </div>
);

const Kicker: React.FC<{text: string; dir: Dir; delay?: number}> = ({text, dir, delay = 0}) => {
  const a = useIn(delay);
  return (
    <div style={{alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 14, opacity: a, translate: `0 ${(1 - a) * 16}px`}}>
      <span style={{width: 14, height: 14, borderRadius: 7, background: C.accent, boxShadow: `0 0 18px ${C.accent}`}} />
      <BiText text={text} dir={dir} style={{fontWeight: 600, fontSize: T.label, color: C.accent}} />
    </div>
  );
};

/** Kinetic headline: word by word, *emphasis* lit with an underline that draws itself. */
const KineticTitle: React.FC<{text: string; dir: Dir; size: number; delay?: number; step?: number}> = ({text, dir, size, delay = 4, step = 3}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  let k = 0;
  return (
    <div style={{fontFamily: F.text, fontWeight: 700, fontSize: size, lineHeight: 1.32, color: C.ink}}>
      {text.split('\n').map((ln, li) => (
        <div key={li}>
          {tokens(ln).map((tk, ti) => {
            const d = delay + k * step; k += tk.n;
            const p = spring({frame: frame - d, fps, config: {damping: 16, stiffness: 170}});
            const line = interpolate(frame, [d + 8, d + 20], [0, 1], clamp);
            return (
              <React.Fragment key={ti}>
                {ti > 0 && ' '}
                <span style={{display: 'inline-block', position: 'relative', opacity: Math.min(1, p * 1.5),
                  translate: `0 ${(1 - p) * 38}px`, filter: `blur(${(1 - Math.min(1, p)) * 8}px)`,
                  color: tk.em ? C.accent : C.ink}}>
                  {tk.latin ? <bdi dir="ltr" style={{fontFamily: F.latin}}>{tk.text}</bdi> : tk.text}
                  {tk.em && <span style={{position: 'absolute', insetInlineStart: 0, bottom: '0.02em', height: '0.09em',
                    width: `${line * 100}%`, background: C.accent, borderRadius: 4, opacity: 0.9}} />}
                </span>
              </React.Fragment>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ---------- scene bodies ----------
const Hook: React.FC<{s: Extract<Scene, {type: 'hook'}>; dir: Dir}> = ({s, dir}) => {
  const words = tokens(s.title.replace(/\n/g, ' ')).reduce((a, t) => a + t.n, 0);
  const b = useIn(10 + words * 3);
  return (
    <Stage gap={34}>
      {s.kicker && <Kicker text={s.kicker} dir={dir} />}
      <KineticTitle text={s.title} dir={dir} size={T.hero} />
      {s.body && <div style={{opacity: b, translate: `0 ${(1 - b) * 20}px`}}>
        <BiText text={s.body} dir={dir} style={{fontWeight: 600, fontSize: T.body + 4, color: C.muted, lineHeight: 1.5}} />
      </div>}
    </Stage>
  );
};

const toneIcon = {bad: '✕', good: '✓', tip: '★'} as const;

const typeWindow = (len: number, frames: number) => {
  const start = 12;
  const end = Math.min(start + len * 0.9, frames * 0.45);
  return {start, end};
};

const Prompt: React.FC<{s: Extract<Scene, {type: 'prompt'}>; frames: number; dir: Dir}> = ({s, frames, dir}) => {
  const frame = useCurrentFrame();
  const a = useIn(0);
  const col = C[s.tone];
  const {start, end} = typeWindow(s.prompt.length, frames);
  const shown = Math.round(interpolate(frame, [start, end], [0, s.prompt.length], clamp));
  const done = shown >= s.prompt.length;
  const sendPop = spring({frame: frame - end - 2, fps: 30, config: {damping: 12}});
  return (
    <Stage>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: a}}>
        <span style={{width: 60, height: 60, borderRadius: 30, background: col, color: C.bg, display: 'grid',
          placeItems: 'center', fontSize: 34, fontWeight: 700, fontFamily: F.latin}}>{toneIcon[s.tone]}</span>
        <BiText text={s.label} dir={dir} style={{fontWeight: 700, fontSize: T.head - 4, color: col}} />
      </div>
      <div style={{background: C.panel, border: `2px solid ${col}`, borderRadius: 32, padding: '38px 42px 28px',
        opacity: a, scale: String(0.97 + a * 0.03), display: 'flex', flexDirection: 'column', gap: 24,
        boxShadow: '0 30px 80px rgba(0,0,0,.35)'}}>
        <div style={{minHeight: 96, lineHeight: 1.6}}>
          <BiText text={s.prompt.slice(0, shown)} dir={dir} style={{fontWeight: 500, fontSize: s.prompt.length > 80 ? T.body - 2 : T.body + 6, color: C.ink}} />
          {!done && <span style={{display: 'inline-block', width: 4, height: '1em', background: C.accent,
            marginInlineStart: 6, verticalAlign: 'middle', opacity: Math.floor(frame / 8) % 2 ? 0.2 : 1}} />}
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end'}}>
          <span style={{width: 72, height: 72, borderRadius: 36, background: done ? C.accent : C.line,
            display: 'grid', placeItems: 'center', scale: String(done ? 1 + (sendPop - 1) * 0.3 : 1)}}>
            <Icon name="send" color={C.bg} size={36} />
          </span>
        </div>
      </div>
    </Stage>
  );
};

/** Generic chat window: file chip → typed message → send → thinking → streamed reply. */
const Chat: React.FC<{s: Extract<Scene, {type: 'chat'}>; frames: number; dir: Dir}> = ({s, frames, dir}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const win = useIn(0, 16);
  const head = useIn(2);
  const tl = chatTimeline(s, frames);
  const chip = spring({frame: frame - tl.attach, fps, config: {damping: 13}});
  const typed = Math.round(interpolate(frame, [tl.typeStart, tl.typeEnd], [0, s.user.length], clamp));
  const sent = frame >= tl.send;
  const bubble = spring({frame: frame - tl.send, fps, config: {damping: 16, stiffness: 150}});
  const thinking = frame >= tl.send + 6 && frame < tl.replyStart;
  const replyWords = s.reply.split(/(\s+)/);
  const wordCount = replyWords.filter((w) => w.trim()).length;
  const nShown = Math.round(interpolate(frame, [tl.replyStart, tl.replyEnd], [0, wordCount], clamp));
  let c = 0;
  const replyText = replyWords.filter((w) => (w.trim() ? ++c <= nShown : c < nShown)).join('');
  const replyIn = spring({frame: frame - tl.replyStart, fps, config: {damping: 18}});
  const tone = s.replyTone ? C[s.replyTone] : C.line;
  const top = s.title ? 470 : 360;

  return (
    <>
      {s.title && <div style={{position: 'absolute', top: 300, left: L.left, right: L.right, opacity: head, translate: `0 ${(1 - head) * 18}px`}}>
        <Title text={s.title} dir={dir} size={T.head} />
      </div>}
      <div style={{position: 'absolute', top, left: L.left, right: L.right, height: L.contentBottom - top,
        background: C.bg2, border: `2px solid ${C.line}`, borderRadius: 36, overflow: 'hidden',
        opacity: win, translate: `0 ${(1 - win) * 40}px`, boxShadow: '0 40px 100px rgba(0,0,0,.45)',
        display: 'flex', flexDirection: 'column'}}>
        {/* window header — neutral, no product logo */}
        <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '20px 28px', borderBottom: `2px solid ${C.line}`}}>
          <span style={{width: 44, height: 44, borderRadius: 12, background: C.panel2, display: 'grid', placeItems: 'center'}}>
            <Icon name="spark" color={C.accent} size={28} />
          </span>
          <bdi dir="ltr" style={{fontFamily: F.latin, fontWeight: 600, fontSize: T.micro + 2, color: C.ink}}>Claude</bdi>
          <span style={{flex: 1}} />
          {[0, 1, 2].map((i) => <span key={i} style={{width: 12, height: 12, borderRadius: 6, background: C.line}} />)}
        </div>
        {/* thread */}
        <div style={{flex: 1, padding: '28px 28px 0', display: 'flex', flexDirection: 'column', gap: 22, justifyContent: 'flex-end', overflow: 'hidden'}}>
          {sent && (
            <div style={{alignSelf: 'flex-end', maxWidth: '86%', background: C.panel2, borderRadius: 28,
              borderEndEndRadius: 8, padding: '18px 26px', opacity: bubble, translate: `0 ${(1 - bubble) * 120}px`,
              display: 'flex', flexDirection: 'column', gap: 12}}>
              {s.attach && <FileChip name={s.attach} dir={dir} />}
              <BiText text={s.user} dir={dir} style={{fontWeight: 500, fontSize: T.label + 2, lineHeight: 1.55, color: C.ink}} />
            </div>
          )}
          {thinking && (
            <div style={{alignSelf: 'flex-start', display: 'flex', gap: 10, padding: '18px 8px'}}>
              {[0, 1, 2].map((i) => <span key={i} style={{width: 14, height: 14, borderRadius: 7, background: C.muted,
                opacity: 0.35 + 0.65 * Math.max(0, Math.sin((frame - i * 4) / 4))}} />)}
            </div>
          )}
          {frame >= tl.replyStart && (
            <div style={{alignSelf: 'flex-start', maxWidth: '94%', opacity: replyIn, borderInlineStart: `4px solid ${tone}`,
              paddingInlineStart: 22, whiteSpace: 'pre-wrap'}}>
              <BiText text={replyText} dir={dir} style={{fontWeight: 500, fontSize: T.label + 2, lineHeight: 1.6, color: C.ink}} />
            </div>
          )}
        </div>
        {/* composer */}
        <div style={{margin: 22, background: C.panel, border: `2px solid ${frame >= tl.typeStart && !sent ? C.accent : C.line}`,
          borderRadius: 26, padding: '16px 18px 16px 22px', display: 'flex', alignItems: 'center', gap: 14, minHeight: 84}}>
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 10}}>
            {s.attach && !sent && frame >= tl.attach && <div style={{scale: String(chip), alignSelf: 'flex-start'}}><FileChip name={s.attach} dir={dir} /></div>}
            <div style={{minHeight: 44, lineHeight: 1.5}}>
              {!sent && typed > 0
                ? <BiText text={s.user.slice(0, typed)} dir={dir} style={{fontWeight: 500, fontSize: T.label, color: C.ink}} />
                : !sent && <span style={{fontFamily: F.text, fontSize: T.label, color: C.muted}}>{dir === 'rtl' ? 'اكتب رسالتك…' : 'Write a message…'}</span>}
              {!sent && typed > 0 && typed < s.user.length && <span style={{display: 'inline-block', width: 3, height: '1em',
                background: C.accent, marginInlineStart: 4, verticalAlign: 'middle'}} />}
            </div>
          </div>
          <span style={{width: 60, height: 60, borderRadius: 30, background: typed >= s.user.length && !sent ? C.accent : C.line,
            display: 'grid', placeItems: 'center', flexShrink: 0}}>
            <Icon name="send" color={C.bg} size={30} />
          </span>
        </div>
      </div>
    </>
  );
};
const FileChip: React.FC<{name: string; dir: Dir}> = ({name, dir}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 10, background: C.bg, border: `2px solid ${C.line}`,
    borderRadius: 16, padding: '8px 16px'}}>
    <Icon name="doc" color={C.sky} size={30} />
    <BiText text={name} dir={dir} style={{fontWeight: 600, fontSize: T.micro, color: C.ink}} />
  </div>
);
export const chatTimeline = (s: Extract<Scene, {type: 'chat'}>, frames: number) => {
  const attach = s.attach ? 10 : 0;
  const typeStart = s.attach ? 22 : 12;
  const typeEnd = Math.min(typeStart + s.user.length * 0.75, frames * 0.38);
  const send = typeEnd + 6;
  const replyStart = send + 22;
  const replyEnd = Math.max(replyStart + 10, frames * 0.88);
  return {attach, typeStart, typeEnd, send, replyStart, replyEnd};
};

const Steps: React.FC<{s: Extract<Scene, {type: 'steps'}>; frames: number; dir: Dir}> = ({s, frames, dir}) => {
  const a = useIn(0);
  const {fps} = useVideoConfig();
  const gap = stepGap(frames, s.items.length);
  return (
    <Stage>
      <div style={{opacity: a, translate: `0 ${(1 - a) * 20}px`}}><Title text={s.title} dir={dir} size={T.title} /></div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 22}}>
        {s.items.map((it, i) => <StepRow key={i} n={i + 1} text={it} dir={dir} delay={itemDelay(s, s.itemsOn, i, frames, fps, 14 + i * gap)} />)}
      </div>
    </Stage>
  );
};
const stepGap = (frames: number, n: number) => Math.max(10, Math.floor((frames * 0.55) / n));
const StepRow: React.FC<{n: number; text: string; dir: Dir; delay: number}> = ({n, text, dir, delay}) => {
  const p = useIn(delay);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 26, background: C.bg2, border: `2px solid ${C.line}`,
      borderRadius: 26, padding: '24px 28px', opacity: p, translate: `0 ${(1 - p) * 30}px`}}>
      <span style={{fontFamily: F.latin, fontWeight: 700, fontSize: 42, color: C.bg, background: C.accent, width: 72, height: 72,
        borderRadius: 18, display: 'grid', placeItems: 'center', flexShrink: 0}}>{n}</span>
      <BiText text={text} dir={dir} style={{fontWeight: 600, fontSize: T.body + 2, color: C.ink, lineHeight: 1.4}} />
    </div>
  );
};

const Cta: React.FC<{s: Extract<Scene, {type: 'cta'}>; handle: string; dir: Dir}> = ({s, handle, dir}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = useIn(0), b = useIn(10), c = useIn(20);
  const drop = spring({frame: frame - 4, fps, config: {damping: 8, stiffness: 120}});
  const tap = spring({frame: frame - 28, fps, config: {damping: 6, stiffness: 200}});
  const ring = interpolate(frame, [28, 52], [0, 1], clamp);
  return (
    <Stage top={300} bottom={1160}>
      <div style={{alignSelf: 'center', position: 'relative', width: 200, height: 200, translate: `0 ${(1 - drop) * -260}px`}}>
        {ring > 0 && ring < 1 && <div style={{position: 'absolute', inset: -ring * 70, borderRadius: '50%',
          border: `5px solid ${C.accent}`, opacity: 1 - ring}} />}
        <div style={{position: 'absolute', inset: 0, borderRadius: 52, background: frame > 30 ? C.accent : C.panel,
          border: `5px solid ${C.accent}`, display: 'grid', placeItems: 'center', scale: String(1 + (tap - 1) * 0.25)}}>
          <Icon name="bookmark" color={frame > 30 ? C.bg : C.accent} size={110} />
        </div>
      </div>
      <div style={{opacity: a, scale: String(0.92 + a * 0.08)}}><Title text={s.title} dir={dir} size={T.hero} color={C.accent} align="center" /></div>
      {s.body && <div style={{opacity: b, textAlign: 'center'}}>
        <BiText text={s.body} dir={dir} style={{fontWeight: 600, fontSize: T.body, color: C.ink, lineHeight: 1.5}} />
      </div>}
      <div style={{textAlign: 'center', opacity: c}}><bdi style={{fontFamily: F.latin, fontWeight: 600, fontSize: T.label + 6, color: C.muted}}>{handle}</bdi></div>
    </Stage>
  );
};

// ---------- comparison format ----------
const TabBar: React.FC<{tabs: string[]; active: number}> = ({tabs, active}) => {
  const a = useIn(0);
  return (
    <div style={{display: 'flex', gap: 12, direction: 'ltr', opacity: 0.4 + a * 0.6}}>
      {tabs.map((t, i) => {
        const on = i === active;
        const col = TRIO[i % TRIO.length];
        return (
          <div key={i} style={{flex: 1, textAlign: 'center', padding: '16px 8px', borderRadius: 18,
            fontFamily: F.latin, fontWeight: 600, fontSize: T.label - 2, letterSpacing: 1, color: on ? col : C.muted,
            background: on ? C.panel : 'transparent', border: `2px solid ${on ? col : C.line}`,
            boxShadow: on ? `inset 0 -6px 0 ${col}` : 'none'}}>{t}</div>
        );
      })}
    </div>
  );
};

const Compare: React.FC<{s: Extract<Scene, {type: 'compare'}>; dir: Dir}> = ({s, dir}) => {
  const col = TRIO[s.active % TRIO.length];
  const a = useIn(4), b = useIn(14), c = useIn(26), d = useIn(40);
  return (
    <div style={{position: 'absolute', top: 290, bottom: 1920 - L.contentBottom, left: L.left, right: L.right, display: 'flex',
      flexDirection: 'column', gap: 32}}>
      <TabBar tabs={s.tabs} active={s.active} />
      <bdi dir="ltr" style={{fontFamily: F.latin, fontWeight: 700, fontSize: 96, color: col, textAlign: 'center',
        opacity: a, scale: String(0.92 + a * 0.08), marginTop: 10}}>{s.term}</bdi>
      <div style={{opacity: b}}><Title text={s.def} dir={dir} size={T.head} align="center" /></div>
      <div style={{alignSelf: 'center', border: `2px dashed ${col}`, borderRadius: 999, padding: '10px 32px', opacity: c}}>
        <BiText text={s.analogy} dir={dir} style={{fontWeight: 600, fontSize: T.label + 6, color: col}} />
      </div>
      <div style={{background: C.bg2, border: `2px solid ${C.line}`, borderRadius: 26, padding: '22px 28px',
        display: 'flex', flexDirection: 'column', gap: 8, opacity: d, translate: `0 ${(1 - d) * 24}px`}}>
        <BiText text={s.exampleLabel} dir={dir} style={{fontWeight: 600, fontSize: T.micro + 2, color: C.muted}} />
        <BiText text={s.example} dir={dir} style={{fontWeight: 600, fontSize: T.body, lineHeight: 1.45, color: C.ink}} />
      </div>
    </div>
  );
};

const Trio: React.FC<{s: Extract<Scene, {type: 'trio'}>; frames: number; dir: Dir}> = ({s, frames, dir}) => {
  const a = useIn(0);
  const {fps} = useVideoConfig();
  const gap = trioGap(frames, s.items.length);
  return (
    <Stage top={300} bottom={1200} gap={34}>
      <div style={{opacity: a}}><Title text={s.title} dir={dir} size={T.title} /></div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 20}}>
        {s.items.map((it, i) => <TrioRow key={i} i={i} term={it.term} rule={it.rule} icon={it.icon} dir={dir} delay={itemDelay(s, s.itemsOn, i, frames, fps, 12 + i * gap)} />)}
      </div>
    </Stage>
  );
};
const trioGap = (frames: number, n: number) => Math.max(8, Math.floor((frames * 0.5) / n));
const TRIO_ICONS = ['doc', 'bot', 'plan'] as const;
const TrioRow: React.FC<{i: number; term: string; rule: string; icon?: IconName; dir: Dir; delay: number}> = ({i, term, rule, icon, dir, delay}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useIn(delay);
  const pop = spring({frame: frame - delay - 6, fps, config: {damping: 9, stiffness: 160}});
  const sweep = interpolate(frame, [delay + 10, delay + 34], [0, 1], clamp);
  const col = TRIO[i % TRIO.length];
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 24, background: C.bg2, borderRadius: 24,
      border: `2px solid ${col}`, padding: '20px 24px', opacity: p, translate: `${(1 - p) * (i % 2 ? -120 : 120)}px 0`,
      position: 'relative', overflow: 'hidden'}}>
      <div style={{position: 'absolute', insetInlineStart: 0, bottom: 0, height: 5, width: `${sweep * 100}%`, background: col}} />
      <div style={{width: 92, height: 92, borderRadius: 22, background: C.panel, border: `2px solid ${col}`, flexShrink: 0,
        display: 'grid', placeItems: 'center', scale: String(pop), rotate: `${(1 - pop) * -25}deg`}}>
        <Icon name={icon ?? TRIO_ICONS[i % 3]} color={col} size={54} />
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0}}>
        <bdi dir="ltr" style={{fontFamily: F.latin, fontWeight: 700, fontSize: T.label + 4, color: col, textAlign: dir === 'rtl' ? 'right' : 'left'}}>{term}</bdi>
        <BiText text={rule} dir={dir} style={{fontWeight: 600, fontSize: T.body - 2, lineHeight: 1.4, color: C.ink}} />
      </div>
    </div>
  );
};

/** Header height above a diagram, so the diagram band starts right under it. */
const flowTop = (s: Extract<Scene, {type: 'flow'}>) =>
  290 + (s.tabs ? 104 : 0) + (s.term ? 100 : 0) + (s.def ? (s.def.length > 30 ? 128 : 70) : 0) + 24;

const FlowScene: React.FC<{s: Extract<Scene, {type: 'flow'}>; frames: number; dir: Dir}> = ({s, frames, dir}) => {
  const {fps} = useVideoConfig();
  const col = s.active !== undefined ? TRIO[s.active % TRIO.length] : C.accent;
  const a = useIn(2), b = useIn(10);
  return (
    <>
      <div style={{position: 'absolute', top: 290, left: L.left, right: L.right, display: 'flex', flexDirection: 'column', gap: 22}}>
        {s.tabs && <TabBar tabs={s.tabs} active={s.active ?? 0} />}
        {s.term && <bdi dir="ltr" style={{fontFamily: F.latin, fontWeight: 700, fontSize: 68, color: col, textAlign: 'center',
          opacity: a, translate: `0 ${(1 - a) * 26}px`}}>{s.term}</bdi>}
        {s.def && <div style={{opacity: b, translate: `0 ${(1 - b) * 16}px`}}>
          <Title text={s.def} dir={dir} size={s.term ? T.body : T.head} align="center" />
        </div>}
      </div>
      <Flow spec={resolveSpec(s, s.spec, frames, fps)} frames={frames} top={flowTop(s)} bottom={L.contentBottom} dir={dir} />
    </>
  );
};

/** Every sound a scene implies, derived from the same timeline that drives its motion. */
const SceneSfx: React.FC<{s: Scene; frames: number; index: number}> = ({s, frames, index}) => {
  const {fps} = useVideoConfig();
  const cues: React.ReactNode[] = [];
  if (index > 0) cues.push(<Sfx key="w" at={0} kind="whoosh" />);
  if (s.type === 'flow') flowSfx(resolveSpec(s, s.spec, frames, fps), frames).forEach((c, i) => cues.push(<Sfx key={`f${i}`} at={c.at} kind={c.kind} />));
  if (s.type === 'prompt') {
    const {start, end} = typeWindow(s.prompt.length, frames);
    cues.push(<Sfx key="t" at={start} kind="type" dur={end - start} loop />, <Sfx key="s" at={end + 2} kind="send" />);
  }
  if (s.type === 'chat') {
    const tl = chatTimeline(s, frames);
    if (s.attach) cues.push(<Sfx key="a" at={tl.attach} kind="pop" />);
    cues.push(<Sfx key="t" at={tl.typeStart} kind="type" dur={tl.typeEnd - tl.typeStart} loop />,
      <Sfx key="s" at={tl.send} kind="send" />, <Sfx key="r" at={tl.replyEnd} kind="tick" />);
  }
  if (s.type === 'steps') s.items.forEach((_, i) => cues.push(<Sfx key={`p${i}`} at={itemDelay(s, s.itemsOn, i, frames, fps, 14 + i * stepGap(frames, s.items.length))} kind="pop" />));
  if (s.type === 'trio') s.items.forEach((_, i) => cues.push(<Sfx key={`p${i}`} at={itemDelay(s, s.itemsOn, i, frames, fps, 12 + i * trioGap(frames, s.items.length)) + 6} kind="pop" />));
  if (s.type === 'cta') cues.push(<Sfx key="d" at={10} kind="pop" />, <Sfx key="k" at={30} kind="tick" />);
  return <>{cues}</>;
};

const SceneView: React.FC<{s: Scene; frames: number; lang: Lang; dir: Dir; handle: string; index: number}> = ({s, frames, lang, dir, handle, index}) => {
  const frame = useCurrentFrame();
  // enter: rise + de-blur; exit: soften. A light sweep crosses at each cut.
  const enter = interpolate(frame, [0, 12], [0, 1], {...clamp, easing: (x) => 1 - Math.pow(1 - x, 3)});
  const exit = interpolate(frame, [frames - 9, frames], [1, 0], clamp);
  const sweep = interpolate(frame, [0, 16], [-0.3, 1.3], clamp);
  const mascot = !!s.audio && (s.type === 'hook' || s.type === 'trio' || s.type === 'cta');
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: Math.min(enter, exit), translate: `0 ${(1 - enter) * 28}px`,
        filter: `blur(${(1 - enter) * 6 + (1 - exit) * 4}px)`}}>
        {s.bg && (
          <AbsoluteFill style={{opacity: s.bgOpacity ?? 0.35}}>
            <Img src={staticFile(s.bg)} style={{width: '100%', height: '100%', objectFit: 'cover',
              scale: String(interpolate(frame, [0, frames], [1.04, 1.12])), translate: `0 ${s.bgY ?? 0}px`}} />
            <AbsoluteFill style={{background: `linear-gradient(180deg, ${C.bg}00 30%, ${C.bg} 92%)`}} />
          </AbsoluteFill>
        )}
        {s.video ? (
          <div style={{position: 'absolute', top: 290, bottom: 1920 - L.contentBottom, left: L.left, right: L.right, borderRadius: 32, overflow: 'hidden',
            border: `2px solid ${C.line}`}}>
            <OffthreadVideo src={staticFile(s.video)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          </div>
        ) : s.type === 'hook' ? <Hook s={s} dir={dir} />
          : s.type === 'prompt' ? <Prompt s={s} frames={frames} dir={dir} />
          : s.type === 'chat' ? <Chat s={s} frames={frames} dir={dir} />
          : s.type === 'steps' ? <Steps s={s} frames={frames} dir={dir} />
          : s.type === 'compare' ? <Compare s={s} dir={dir} />
          : s.type === 'trio' ? <Trio s={s} frames={frames} dir={dir} />
          : s.type === 'flow' ? <FlowScene s={s} frames={frames} dir={dir} />
          : <Cta s={s} handle={handle} dir={dir} />}
        {mascot && <Mascot audio={s.audio!} pose="present" size={s.type === 'cta' ? 280 : 210}
          x={s.type === 'cta' ? 40 : 30} y={s.type === 'cta' ? 1190 : 1290} flip delay={4} />}
      </AbsoluteFill>
      {index > 0 && sweep > -0.3 && sweep < 1.3 && (
        <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen',
          background: `linear-gradient(115deg, transparent ${sweep * 100 - 18}%, ${C.accent}14 ${sweep * 100 - 6}%, #ffffff10 ${sweep * 100}%, transparent ${sweep * 100 + 12}%)`}} />
      )}
      <Captions text={s.narration} frames={frames} lang={lang} dir={dir} cues={s.cues} left={mascot && s.type !== 'cta' ? 270 : L.left} />
      {s.audio && <Audio src={staticFile(s.audio)} />}
      <SceneSfx s={s} frames={frames} index={index} />
    </AbsoluteFill>
  );
};

/** Fine film grain: breaks the flat "rendered" look of pure vector colour. */
const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const x = Math.round(random(`gx${frame % 12}`) * 200), y = Math.round(random(`gy${frame % 12}`) * 200);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.07, mixBlendMode: 'overlay', overflow: 'hidden'}}>
      <svg width={1480} height={2320} style={{position: 'absolute', left: -x, top: -y}}>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} stitchTiles="stitch" /></filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
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
      fontFamily: F.text, color: C.ink}}>
      <Backdrop />
      {track.scenes.map((s, i) => {
        const seq = (
          <Sequence key={i} from={from} durationInFrames={frames[i]} name={`${i + 1}-${s.type}`}>
            <SceneView s={s} frames={frames[i]} lang={lang} dir={track.dir} handle={episode.channel[lang]} index={i} />
          </Sequence>
        );
        from += frames[i];
        return seq;
      })}
      {track.scenes.some((x) => x.audio) && <Audio src={staticFile('brand/bed.mp3')} volume={0.06} loop />}
      <TopBar handle={episode.channel[lang]} level={episode.level} lang={lang} segs={frames} />
      <Grain />
    </AbsoluteFill>
  );
};
