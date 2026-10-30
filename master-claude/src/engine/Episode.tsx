import React from 'react';
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  Easing,
  random,
} from 'remotion';
import {COLORS, EpisodeData, FPS, Step, TAIL} from './types';
import './fonts';

const s = (sec: number) => Math.round(sec * FPS);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const BPM = 112;
const BEAT = (60 / BPM) * FPS;

type Ctx = {d: EpisodeData; font: string; rtl: boolean};
const C = React.createContext<Ctx>(null as unknown as Ctx);
const useCtx = () => React.useContext(C);

const sp = (frame: number, delay: number, cfg: Partial<{damping: number; stiffness: number; mass: number}> = {}) =>
  spring({frame: frame - delay, fps: FPS, config: {damping: 14, stiffness: 150, mass: 0.8, ...cfg}});

/* ============ ICONS ============ */
type IconKind = Step['icon'] | 'check' | 'x' | 'bookmark' | 'bell' | 'spark';
const Icon: React.FC<{kind: IconKind; color: string; size?: number}> = ({kind, color, size = 64}) => {
  const p = {fill: 'none', stroke: color, strokeWidth: 2.4, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{display: 'block'}}>
      {kind === 'role' && (<g {...p}><circle cx="12" cy="8" r="3.6" /><path d="M4.5 20c1.2-4 4.2-6 7.5-6s6.3 2 7.5 6" /></g>)}
      {kind === 'task' && (<g {...p}><rect x="4" y="3.5" width="16" height="17" rx="2.5" /><path d="M8 9h8M8 13h8M8 17h5" /></g>)}
      {kind === 'context' && (<g {...p}><circle cx="12" cy="12" r="8.5" /><path d="M12 7v5l3.2 2" /></g>)}
      {kind === 'format' && (<g {...p}><rect x="3.5" y="4" width="17" height="4.5" rx="1.2" /><rect x="3.5" y="10.5" width="10.5" height="9.5" rx="1.2" /><path d="M17 11v9" /></g>)}
      {kind === 'budget' && (<g {...p}><circle cx="12" cy="12" r="8.5" /><path d="M14.8 9.2c-.5-1-1.6-1.6-2.8-1.6-1.6 0-2.8.9-2.8 2.2 0 3 5.6 1.6 5.6 4.5 0 1.3-1.2 2.2-2.8 2.2-1.3 0-2.4-.6-2.9-1.7M12 6v1.6M12 16.4V18" /></g>)}
      {kind === 'heart' && (<g {...p}><path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0112 7.3 4.3 4.3 0 0119.5 10c0 5.4-7.5 10-7.5 10z" /></g>)}
      {kind === 'check' && (<g {...p} strokeWidth={3}><path d="M5 12.5l4.5 4.5L19 7.5" /></g>)}
      {kind === 'x' && (<g {...p} strokeWidth={3}><path d="M6 6l12 12M18 6L6 18" /></g>)}
      {kind === 'bookmark' && (<g {...p}><path d="M6.5 3.5h11v17l-5.5-4-5.5 4z" fill={color} fillOpacity={0.3} /></g>)}
      {kind === 'bell' && (<g {...p}><path d="M6 16.5V11a6 6 0 1112 0v5.5l1.5 2h-15z" /><path d="M10 20.5a2 2 0 004 0" /></g>)}
      {kind === 'spark' && (<g {...p} fill={color}><path d="M12 2.5l1.9 6.4 6.6 1.9-6.6 1.9L12 19.1l-1.9-6.4-6.6-1.9 6.6-1.9z" /></g>)}
    </svg>
  );
};

/* ============ FX PRIMITIVES ============ */

const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'overlay', opacity: 0.18, zIndex: 90}}>
      <svg width="100%" height="100%">
        <filter id="g">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 12} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#g)" />
      </svg>
    </AbsoluteFill>
  );
};

const Vignette: React.FC = () => (
  <AbsoluteFill style={{pointerEvents: 'none', zIndex: 89, background: 'radial-gradient(120% 90% at 50% 45%, transparent 55%, rgba(0,0,0,0.65) 100%)'}} />
);

/** Particle burst radiating from center of its parent */
const Burst: React.FC<{at: number; color: string; count?: number; radius?: number; seed?: string}> = ({at, color, count = 22, radius = 260, seed = 'b'}) => {
  const frame = useCurrentFrame();
  const t = frame - at;
  if (t < 0 || t > 32) return null;
  const p = Easing.out(Easing.cubic)(Math.min(1, t / 22));
  return (
    <div style={{position: 'absolute', left: '50%', top: '50%', width: 0, height: 0, pointerEvents: 'none', zIndex: 5}}>
      {Array.from({length: count}).map((_, i) => {
        const ang = (i / count) * Math.PI * 2 + random(seed + i) * 0.4;
        const r = radius * (0.55 + random(seed + 'r' + i) * 0.6) * p;
        const size = 6 + random(seed + 's' + i) * 10;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: Math.cos(ang) * r - size / 2,
              top: Math.sin(ang) * r - size / 2,
              width: size,
              height: size,
              borderRadius: size,
              background: i % 3 === 0 ? '#FFFFFF' : color,
              boxShadow: `0 0 12px ${color}`,
              opacity: 1 - t / 32,
            }}
          />
        );
      })}
      <div
        style={{
          position: 'absolute',
          left: -radius * p,
          top: -radius * p,
          width: radius * 2 * p,
          height: radius * 2 * p,
          borderRadius: '50%',
          border: `4px solid ${color}`,
          opacity: (1 - p) * 0.8,
        }}
      />
    </div>
  );
};

/** Light sweep shine across an element */
const Shine: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + 16], [-40, 140], clamp);
  if (frame < at || frame > at + 18) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        borderRadius: 'inherit',
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 4,
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: -50,
          bottom: -50,
          left: `${p}%`,
          width: 140,
          transform: 'skewX(-20deg)',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.55), transparent)',
        }}
      />
    </div>
  );
};

/** Text with RGB split glitch */
const GlitchText: React.FC<{children: string; style: React.CSSProperties; intensity: number; seed: string}> = ({children, style, intensity, seed}) => {
  const frame = useCurrentFrame();
  const jx = intensity > 0 ? (random(seed + frame) - 0.5) * 30 * intensity : 0;
  const jy = intensity > 0 ? (random(seed + 'y' + frame) - 0.5) * 10 * intensity : 0;
  const slice = intensity > 0.3 && random(seed + 'sl' + frame) > 0.5;
  return (
    <div style={{position: 'relative', ...style}}>
      <div style={{position: 'absolute', inset: 0, color: '#FF2D55', transform: `translate(${-8 * intensity + jx}px, ${jy}px)`, mixBlendMode: 'screen', opacity: intensity > 0 ? 0.9 : 0}}>{children}</div>
      <div style={{position: 'absolute', inset: 0, color: '#00E5FF', transform: `translate(${8 * intensity - jx}px, ${-jy}px)`, mixBlendMode: 'screen', opacity: intensity > 0 ? 0.9 : 0}}>{children}</div>
      <div style={{position: 'relative', clipPath: slice ? `inset(${random(seed + 'c' + frame) * 60}% 0 ${random(seed + 'd' + frame) * 30}% 0)` : undefined}}>{children}</div>
    </div>
  );
};

/* ============ BACKGROUND ============ */

const Background: React.FC<{energy: number}> = ({energy}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const gy = (frame * (0.8 + energy * 2.2)) % 90;
  return (
    <AbsoluteFill style={{background: `radial-gradient(120% 80% at 50% 0%, ${COLORS.bg2} 0%, ${COLORS.bg} 60%)`}}>
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(rgba(120,150,210,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(120,150,210,0.08) 1px, transparent 1px)',
          backgroundSize: '90px 90px',
          backgroundPosition: `0px ${gy}px`,
          transform: 'perspective(900px) rotateX(38deg) scale(1.9) translateY(18%)',
          transformOrigin: '50% 100%',
          maskImage: 'linear-gradient(180deg, transparent 0%, black 45%, black 100%)',
          opacity: 0.9,
        }}
      />
      {[
        {c: COLORS.orange, x: 90, y: 360, w: 900, sx: 0.5, sy: 0.4},
        {c: COLORS.blue, x: -250, y: 1000, w: 820, sx: 0.35, sy: 0.45},
        {c: COLORS.purple, x: 520, y: 1300, w: 700, sx: 0.42, sy: 0.3},
      ].map((b, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            width: b.w,
            height: b.w,
            borderRadius: '50%',
            left: b.x + Math.sin(t * b.sx + i) * 140,
            top: b.y + Math.cos(t * b.sy + i) * 120,
            background: `radial-gradient(circle, ${b.c}${energy > 0.5 ? '38' : '24'} 0%, transparent 65%)`,
            filter: 'blur(40px)',
          }}
        />
      ))}
      {/* floating dust */}
      {Array.from({length: 26}).map((_, i) => {
        const x = random('dx' + i) * 1080;
        const speed = 0.6 + random('ds' + i) * 1.6;
        const y = (random('dy' + i) * 2100 - frame * speed * (1 + energy)) % 2100;
        const yy = y < 0 ? y + 2100 : y;
        const sz = 2 + random('dz' + i) * 4;
        return <div key={i} style={{position: 'absolute', left: x, top: yy - 100, width: sz, height: sz, borderRadius: sz, background: i % 4 === 0 ? COLORS.orange : '#9FB6E6', opacity: 0.35}} />;
      })}
    </AbsoluteFill>
  );
};

/* ============ CAMERA ============ */

type Shake = {at: number; amp: number; len?: number};
const Camera: React.FC<{punches: number[]; shakes: Shake[]; beatFrom: number; beatTo: number; children: React.ReactNode}> = ({punches, shakes, beatFrom, beatTo, children}) => {
  const frame = useCurrentFrame();
  let scale = 1;
  for (const p of punches) {
    const t = frame - p;
    if (t >= 0 && t < 24) scale += 0.09 * Math.exp(-t / 6);
  }
  if (frame >= beatFrom && frame < beatTo) {
    const ph = ((frame - beatFrom) % BEAT) / BEAT;
    scale += 0.012 * Math.exp(-ph * 6);
  }
  let x = 0;
  let y = 0;
  let rot = 0;
  for (const sh of shakes) {
    const t = frame - sh.at;
    const len = sh.len ?? 14;
    if (t >= 0 && t < len) {
      const k = (1 - t / len) * sh.amp;
      x += (random('sx' + sh.at + t) - 0.5) * 2 * k;
      y += (random('sy' + sh.at + t) - 0.5) * 2 * k;
      rot += (random('sr' + sh.at + t) - 0.5) * 0.6 * (k / 20);
    }
  }
  return <AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${scale}) rotate(${rot}deg)`}}>{children}</AbsoluteFill>;
};

/* ============ TRANSITIONS ============ */

const Whip: React.FC<{dur: number; first?: boolean; last?: boolean; children: React.ReactNode}> = ({dur, first, last, children}) => {
  const {rtl} = useCtx();
  const frame = useCurrentFrame();
  const dir = rtl ? -1 : 1;
  const inP = first ? 1 : interpolate(frame, [0, 7], [0, 1], {...clamp, easing: Easing.out(Easing.exp)});
  const outP = last ? 1 : interpolate(frame, [dur - 6, dur], [1, 0], {...clamp, easing: Easing.in(Easing.exp)});
  const x = (1 - inP) * 700 * dir - (1 - outP) * 700 * dir;
  const blur = (1 - Math.min(inP, outP)) * 26;
  const op = Math.min(1, Math.min(inP, outP) * 1.6);
  return (
    <AbsoluteFill style={{transform: `translateX(${x}px) scale(${1 + (1 - inP) * 0.15})`, filter: blur > 0.3 ? `blur(${blur}px)` : undefined, opacity: op}}>
      {children}
    </AbsoluteFill>
  );
};

const Flash: React.FC<{at: number[]}> = ({at}) => {
  const frame = useCurrentFrame();
  let o = 0;
  let leak = -1;
  for (const a of at) {
    const t = frame - a;
    if (t >= -2 && t < 8) o = Math.max(o, interpolate(t, [-2, 0, 8], [0, 0.55, 0], clamp));
    if (t >= -4 && t < 16) leak = t;
  }
  return (
    <>
      <AbsoluteFill style={{background: '#FFF6EC', opacity: o, zIndex: 80, pointerEvents: 'none', mixBlendMode: 'screen'}} />
      {leak >= -4 && (
        <AbsoluteFill
          style={{
            zIndex: 81,
            pointerEvents: 'none',
            mixBlendMode: 'screen',
            opacity: interpolate(leak, [-4, 2, 16], [0, 0.9, 0], clamp),
            background: `radial-gradient(60% 40% at ${interpolate(leak, [-4, 16], [-10, 110])}% 40%, ${COLORS.orange}CC 0%, #FF3D7F55 40%, transparent 70%)`,
          }}
        />
      )}
    </>
  );
};

/* ============ CAPTIONS (karaoke) ============ */

type Cap = {start: number; end: number; words: [number, string][]};
const Karaoke: React.FC<{hideBefore: number; hideFrom: number}> = ({hideBefore, hideFrom}) => {
  const {d, font, rtl} = useCtx();
  const frame = useCurrentFrame();
  if (frame < hideBefore || frame >= hideFrom) return null;
  const caps = d.words as unknown as Cap[];
  const cap = caps.reduce<Cap | null>((acc, c) => (frame >= s(c.start) - 2 ? c : acc), null);
  if (!cap) return null;
  const local = frame - s(cap.start);
  const enter = sp(frame, s(cap.start), {damping: 13, stiffness: 200});
  const out = interpolate(frame, [s(cap.end) - 4, s(cap.end)], [1, 0], clamp);
  const activeIdx = cap.words.reduce((acc, [t], i) => (frame >= s(t) - 1 ? i : acc), -1);
  return (
    <div style={{position: 'absolute', left: 60, right: 120, bottom: 400, display: 'flex', justifyContent: 'center', zIndex: 60, opacity: Math.min(1, enter) * out}}>
      <div
        style={{
          direction: d.dir,
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: rtl ? '6px 16px' : '6px 20px',
          maxWidth: 880,
          padding: '20px 30px',
          borderRadius: 26,
          background: 'rgba(5,8,15,0.66)',
          border: '1px solid rgba(255,255,255,0.10)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 16px 50px rgba(0,0,0,0.5)',
          transform: `translateY(${(1 - enter) * 30}px) scale(${0.9 + 0.1 * enter})`,
        }}
      >
        {cap.words.map(([t, w], i) => {
          const isActive = i === activeIdx;
          const said = i <= activeIdx;
          const pop = sp(frame, s(t) - 1, {damping: 10, stiffness: 260});
          const isKey = /Claude|الدور|المهمة|السياق|الشكل|Role|Task|Context|Format|احترافية|pro|الخطأ|wrong|generic|عام/.test(w);
          return (
            <span
              key={i}
              style={{
                fontFamily: font,
                fontWeight: 900,
                fontSize: rtl ? 54 : 48,
                lineHeight: 1.3,
                color: isActive ? COLORS.orange : said ? (isKey ? '#FFD08A' : COLORS.white) : 'rgba(245,247,251,0.38)',
                transform: `scale(${isActive ? 1 + 0.14 * Math.min(1, pop) : 1}) translateY(${isActive ? -4 * pop : 0}px)`,
                display: 'inline-block',
                textShadow: isActive ? `0 0 24px ${COLORS.orange}AA` : '0 2px 10px rgba(0,0,0,0.6)',
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const ProgressBar: React.FC<{total: number}> = ({total}) => {
  const frame = useCurrentFrame();
  const w = interpolate(frame, [0, total], [0, 100], clamp);
  return (
    <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 10, background: 'rgba(255,255,255,0.08)', zIndex: 95}}>
      <div style={{width: `${w}%`, height: '100%', background: `linear-gradient(90deg, ${COLORS.orange}, #FFB066)`, boxShadow: `0 0 18px ${COLORS.orange}`}} />
    </div>
  );
};

/* ============ SCENES ============ */

const Clip: React.FC<{src: string; opacity?: number; blend?: React.CSSProperties['mixBlendMode']; startFrom?: number}> = ({src, opacity = 1, blend, startFrom = 0}) => (
  <AbsoluteFill style={{opacity, mixBlendMode: blend}}>
    <OffthreadVideo src={staticFile(src)} muted startFrom={startFrom} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
  </AbsoluteFill>
);

const Hook: React.FC = () => {
  const {d, font} = useCtx();
  const frame = useCurrentFrame();
  const slam = sp(frame, 0, {damping: 8, stiffness: 240, mass: 0.6});
  const scale = interpolate(slam, [0, 1], [2.6, 1]);
  const glitch = frame < 10 ? 1 - frame / 10 : frame % 22 < 3 ? 0.7 : 0;
  const words = d.text.hookSub.split(' ');
  const wordGap = 4;
  const zoom = interpolate(frame, [0, s(d.cues.problem)], [1.15, 1.0], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <Clip src={d.clips.hook} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(7,11,20,0.6) 0%, rgba(7,11,20,0.25) 45%, rgba(7,11,20,0.9) 100%)'}} />
      {/* scanlines */}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0px, rgba(0,0,0,0.25) 2px, transparent 2px, transparent 5px)', opacity: 0.35}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 260}}>
        <div style={{transform: `scale(${scale})`, opacity: Math.min(1, slam * 2)}}>
          <GlitchText
            seed="stop"
            intensity={glitch}
            style={{
              fontFamily: font,
              fontWeight: 900,
              fontSize: d.lang === 'ar' ? 270 : 220,
              color: COLORS.red,
              letterSpacing: d.lang === 'en' ? 8 : 0,
              textShadow: `0 0 80px ${COLORS.red}CC, 0 12px 40px rgba(0,0,0,0.7)`,
              direction: d.dir,
              lineHeight: 1.1,
            }}
          >
            {d.text.stop}
          </GlitchText>
        </div>
        <div style={{marginTop: 36, maxWidth: 940, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '8px 18px', direction: d.dir}}>
          {words.map((w, i) => {
            const p = sp(frame, 10 + i * wordGap, {damping: 11, stiffness: 220});
            const isKey = /Claude|الخطأ|wrong/.test(w);
            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  fontFamily: font,
                  fontWeight: 900,
                  fontSize: 70,
                  color: isKey ? COLORS.orange : COLORS.white,
                  opacity: Math.min(1, p),
                  transform: `translateY(${(1 - p) * 50}px) scale(${0.6 + 0.4 * p})`,
                  filter: `blur(${(1 - Math.min(1, p)) * 10}px)`,
                  textShadow: isKey ? `0 0 30px ${COLORS.orange}` : '0 6px 20px rgba(0,0,0,0.7)',
                }}
              >
                {w}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Bars: React.FC<{widths: number[]; color: string; start: number; height?: number}> = ({widths, color, start, height = 22}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
      {widths.map((w, i) => {
        const p = interpolate(frame, [start + i * 4, start + i * 4 + 12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        return <div key={i} style={{width: w * p, height, borderRadius: height, background: color}} />;
      })}
    </div>
  );
};

const Problem: React.FC = () => {
  const {d, font, rtl} = useCtx();
  const frame = useCurrentFrame();
  const c = d.cues;
  const enter = sp(frame, 0, {damping: 15, stiffness: 110});
  const typeStart = s(c.typeAt - c.problem) - 4;
  const sendAt = s(c.typeAt - c.problem) + 14;
  const badStart = s(c.badAt - c.problem);
  const stampAt = badStart + 10;
  const msgLen = Math.floor(Math.max(0, frame - typeStart) * (20 / FPS));
  const sent = frame >= sendAt;
  const bubble = sp(frame, sendAt, {damping: 12, stiffness: 200});
  const reply = sp(frame, badStart, {damping: 14});
  const stamp = sp(frame, stampAt, {damping: 7, stiffness: 240});
  const glitchAmt = frame >= stampAt - 2 && frame < stampAt + 16 ? 1 - (frame - stampAt + 2) / 18 : 0;
  const rotY = interpolate(enter, [0, 1], [rtl ? -35 : 35, 0]) + Math.sin(frame / 30) * 3;
  const rotX = interpolate(enter, [0, 1], [25, 4]);
  return (
    <AbsoluteFill>
      {glitchAmt > 0 && <Clip src={d.clips.glitch} opacity={glitchAmt * 0.8} blend="screen" />}
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 210, perspective: 1600}}>
        <div
          style={{
            width: 940,
            padding: 40,
            borderRadius: 44,
            background: 'linear-gradient(160deg, rgba(22,32,54,0.96), rgba(10,15,28,0.96))',
            border: '1px solid rgba(255,255,255,0.12)',
            boxShadow: `0 40px 120px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.03), 0 0 ${60 * glitchAmt}px ${COLORS.red}`,
            opacity: enter,
            transform: `translateY(${(1 - enter) * 200}px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateX(${glitchAmt * (random('pj' + frame) - 0.5) * 40}px)`,
            direction: d.dir,
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 18, paddingBottom: 26, borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: 34, direction: 'ltr'}}>
            <div style={{width: 64, height: 64, borderRadius: 20, background: `${COLORS.orange}22`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{transform: `rotate(${frame * 2}deg)`}}>
                <Icon kind="spark" color={COLORS.orange} size={38} />
              </div>
            </div>
            <div style={{fontFamily: font, fontWeight: 800, fontSize: 42, color: COLORS.white}}>Claude</div>
            <div style={{marginLeft: 'auto', width: 16, height: 16, borderRadius: 8, background: COLORS.green, boxShadow: `0 0 16px ${COLORS.green}`}} />
          </div>
          <div style={{display: 'flex', flexDirection: 'column', gap: 30, minHeight: 520}}>
            {sent && (
              <div style={{display: 'flex', justifyContent: rtl ? 'flex-start' : 'flex-end', transform: `scale(${bubble})`, transformOrigin: rtl ? 'left bottom' : 'right bottom'}}>
                <div style={{padding: '28px 36px', borderRadius: 34, background: `linear-gradient(135deg, ${COLORS.orange}, #FF9A4D)`, boxShadow: `0 14px 40px ${COLORS.orange}55`, fontFamily: font, fontWeight: 900, fontSize: 56, color: '#1A0E05', position: 'relative'}}>
                  {d.text.userMsg}
                  <Shine at={sendAt + 2} />
                </div>
              </div>
            )}
            {frame >= badStart && (
              <div style={{position: 'relative', display: 'flex', justifyContent: rtl ? 'flex-end' : 'flex-start', opacity: reply, transform: `translateY(${(1 - reply) * 40}px)`}}>
                <div style={{padding: '30px 34px', borderRadius: 34, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', width: 640, filter: `saturate(0.2) ${glitchAmt > 0 ? `hue-rotate(${glitchAmt * 90}deg)` : ''}`}}>
                  <Bars widths={[560, 480, 530, 300]} color="rgba(200,210,230,0.3)" start={badStart + 2} />
                </div>
                <div
                  style={{
                    position: 'absolute',
                    top: 50,
                    left: rtl ? 100 : undefined,
                    right: rtl ? undefined : 100,
                    transform: `rotate(-9deg) scale(${interpolate(stamp, [0, 1], [3, 1])})`,
                    opacity: Math.min(1, Math.max(0, stamp * 1.5)),
                    display: 'flex',
                    alignItems: 'center',
                    gap: 14,
                    padding: '18px 34px',
                    border: `6px solid ${COLORS.red}`,
                    borderRadius: 22,
                    color: COLORS.red,
                    background: 'rgba(7,11,20,0.9)',
                    fontFamily: font,
                    fontWeight: 900,
                    fontSize: 58,
                    whiteSpace: 'nowrap',
                    boxShadow: `0 0 50px ${COLORS.red}88`,
                    direction: d.dir,
                  }}
                >
                  <Icon kind="x" color={COLORS.red} size={54} />
                  {d.text.badLabel}
                </div>
              </div>
            )}
          </div>
          <div
            style={{
              marginTop: 26,
              padding: '24px 30px',
              borderRadius: 28,
              background: 'rgba(255,255,255,0.05)',
              border: `2px solid ${!sent && frame >= typeStart ? COLORS.orange : 'rgba(255,255,255,0.1)'}`,
              boxShadow: !sent && frame >= typeStart ? `0 0 30px ${COLORS.orange}55` : 'none',
              fontFamily: font,
              fontWeight: 800,
              fontSize: 46,
              color: COLORS.white,
              minHeight: 62,
            }}
          >
            {!sent ? d.text.userMsg.slice(0, msgLen) : ''}
            {!sent && <span style={{opacity: frame % 14 < 7 ? 1 : 0, color: COLORS.orange}}>|</span>}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const StepCard: React.FC<{step: Step; placeAt: number; fillAt: number; active: boolean; dim: boolean; compact?: boolean}> = ({step, placeAt, fillAt, active, dim, compact}) => {
  const {d, font, rtl} = useCtx();
  const frame = useCurrentFrame();
  const place = sp(frame, placeAt, {damping: 14, stiffness: 120});
  const fill = sp(frame, fillAt, {damping: 9, stiffness: 200});
  const filled = frame >= fillAt;
  const exWords = step.ex.split(' ');
  const glow = active ? 0.5 + 0.5 * Math.sin(frame / 5) : 0;
  const fromX = rtl ? 1 : -1;
  const pop = filled ? 1 + Math.max(0, 1 - (frame - fillAt) / 10) * 0.05 : 1;
  return (
    <div
      style={{
        position: 'relative',
        width: 920,
        height: compact ? 150 : 196,
        borderRadius: 36,
        padding: '0 36px',
        display: 'flex',
        alignItems: 'center',
        gap: 30,
        direction: d.dir,
        opacity: place * (dim ? 0.5 : 1),
        transform: `translateX(${(1 - place) * 400 * fromX}px) rotateZ(${(1 - place) * 6 * fromX}deg) scale(${(filled ? (active ? 1.03 : 1) : 0.96) * pop})`,
        background: filled ? `linear-gradient(${rtl ? 270 : 90}deg, ${step.color}40 0%, rgba(12,18,32,0.95) 70%)` : 'rgba(12,18,32,0.55)',
        border: filled ? `3px solid ${step.color}` : '3px dashed rgba(255,255,255,0.18)',
        boxShadow: filled ? `0 0 ${30 + glow * 50}px ${step.color}${active ? '99' : '33'}, inset 0 0 30px ${step.color}22` : 'none',
        filter: dim ? 'saturate(0.6)' : undefined,
      }}
    >
      <Shine at={fillAt + 2} />
      <div style={{flexShrink: 0, width: 124, height: 124, borderRadius: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', background: filled ? `${step.color}2E` : 'rgba(255,255,255,0.05)', position: 'relative'}}>
        <Burst at={fillAt} color={step.color} seed={'st' + step.n} radius={220} />
        {filled ? (
          <div style={{transform: `scale(${fill}) rotate(${(1 - fill) * -90}deg)`}}>
            <Icon kind={step.icon} color={step.color} size={74} />
          </div>
        ) : (
          <div style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 64, color: 'rgba(255,255,255,0.22)'}}>{step.n}</div>
        )}
        {filled && (
          <div style={{position: 'absolute', top: -14, [rtl ? 'right' : 'left']: -14, width: 54, height: 54, borderRadius: 27, background: step.color, color: '#0A0F1A', fontFamily: 'Inter', fontWeight: 900, fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${fill})`, boxShadow: `0 0 20px ${step.color}`}}>
            {step.n}
          </div>
        )}
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0, flex: 1}}>
        <div style={{fontFamily: font, fontWeight: 900, fontSize: 62, color: filled ? step.color : 'rgba(255,255,255,0.28)', textShadow: filled && active ? `0 0 26px ${step.color}` : 'none'}}>
          {filled ? (
            <span style={{display: 'inline-block', transform: `translateY(${(1 - fill) * 30}px)`, opacity: Math.min(1, fill * 1.4)}}>{step.label}</span>
          ) : (
            '• • •'
          )}
        </div>
        {step.ex && <div style={{display: 'flex', flexWrap: 'nowrap', gap: rtl ? 12 : 10, minHeight: 52, overflow: 'hidden'}}>
          {filled &&
            exWords.map((w, i) => {
              const p = sp(frame, fillAt + 10 + i * 3, {damping: 12, stiffness: 220});
              return (
                <span key={i} style={{display: 'inline-block', fontFamily: font, fontWeight: 700, fontSize: d.lang === 'ar' ? 40 : 35, color: COLORS.white, opacity: Math.min(1, p), transform: `translateY(${(1 - p) * 24}px)`, whiteSpace: 'nowrap'}}>
                  {w}
                </span>
              );
            })}
        </div>}
      </div>
    </div>
  );
};

const Formula: React.FC = () => {
  const {d, font} = useCtx();
  const frame = useCurrentFrame();
  const c = d.cues;
  const stepFrames = c.steps.map((t) => s(t - c.formula));
  const activeIdx = stepFrames.reduce((acc, f, i) => (frame >= f ? i : acc), -1);
  const titleWords = d.text.formulaTitle.split(' ');
  const lineP = (i: number) => interpolate(frame, [stepFrames[i] - 8, stepFrames[i] + 4], [0, 1], clamp);
  const beamsOp = interpolate(frame, [0, 12, stepFrames[0] + 30, stepFrames[0] + 60], [0, 0.55, 0.55, 0.22], clamp);
  // stack drift to keep the active card near optical center
  const lastF = stepFrames[stepFrames.length - 1];
  const drift = d.magic ? 0 : interpolate(frame, [stepFrames[0], lastF + 10], [30, -30], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const mg = d.magic;
  const magicAt = mg ? s(mg.at - c.formula) : 0;
  const asksAt = mg ? s(mg.asksAt - c.formula) : 0;
  const typeDur = Math.max(20, asksAt - magicAt - 12);
  const typedLen = mg ? Math.floor(interpolate(frame, [magicAt, magicAt + typeDur], [0, mg.line.length], clamp)) : 0;
  const box = sp(frame, 12, {damping: 12, stiffness: 160});
  const done = frame >= magicAt + typeDur;
  const asks = sp(frame, asksAt, {damping: 11, stiffness: 220});
  return (
    <AbsoluteFill>
      <Clip src={d.clips.mid} opacity={beamsOp} blend="screen" />
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 140}}>
        <div style={{display: 'flex', gap: 22, direction: d.dir, marginBottom: 14, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1000}}>
          {titleWords.map((w, i) => {
            const p = sp(frame, 2 + i * 4, {damping: 11, stiffness: 200});
            return (
              <span key={i} style={{display: 'inline-block', fontFamily: font, fontWeight: 900, fontSize: 80, color: COLORS.white, opacity: Math.min(1, p), transform: `translateY(${(1 - p) * -60}px) scale(${0.7 + 0.3 * p})`, filter: `blur(${(1 - Math.min(1, p)) * 12}px)`, textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>
                {w}
              </span>
            );
          })}
        </div>
        <div style={{height: 9, borderRadius: 5, width: `${interpolate(frame, [8, 30], [0, 760], clamp)}px`, background: `linear-gradient(90deg, ${COLORS.orange}, ${COLORS.blue}, ${COLORS.green}, ${COLORS.purple})`, boxShadow: `0 0 24px ${COLORS.blue}88`, marginBottom: 44}} />
        {mg && (
          <div style={{position: 'relative', width: 960, marginBottom: 34, opacity: Math.min(1, box), transform: `scale(${0.8 + 0.2 * box})`}}>
            <Burst at={magicAt + typeDur} color="#FFC861" seed="magic" radius={420} count={34} />
            <div
              style={{
                position: 'relative',
                padding: '34px 40px',
                borderRadius: 36,
                background: 'linear-gradient(160deg, rgba(40,30,10,0.92), rgba(12,14,26,0.95))',
                border: '3px solid #FFC861',
                boxShadow: `0 0 ${50 + Math.sin(frame / 5) * 20 + (done ? 30 : 0)}px #FFC86188, inset 0 0 40px #FFC86122`,
                direction: d.dir,
                overflow: 'hidden',
              }}
            >
              <Shine at={magicAt + typeDur + 2} />
              <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14}}>
                <div style={{transform: `rotate(${frame * 3}deg)`}}><Icon kind="spark" color="#FFC861" size={40} /></div>
                <div style={{fontFamily: font, fontWeight: 800, fontSize: 34, color: '#FFC861', opacity: 0.9}}>{d.text.youLabel}</div>
              </div>
              <div style={{fontFamily: font, fontWeight: 900, fontSize: d.lang === 'ar' ? 64 : 54, lineHeight: 1.3, color: COLORS.white, minHeight: 90, textShadow: done ? '0 0 24px #FFC86199' : 'none'}}>
                {frame < magicAt ? <span style={{opacity: 0.35}}>• • •</span> : mg.line.slice(0, typedLen)}
                {!done && <span style={{opacity: frame % 14 < 7 ? 1 : 0, color: '#FFC861'}}>|</span>}
              </div>
            </div>
          </div>
        )}
        {mg && (
          <div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22, direction: 'ltr', opacity: Math.min(1, asks), transform: `translateY(${(1 - asks) * 30}px) scale(${0.8 + 0.2 * asks})`}}>
            <div style={{width: 58, height: 58, borderRadius: 18, background: `${COLORS.orange}26`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{transform: `rotate(${frame * 2}deg)`}}><Icon kind="spark" color={COLORS.orange} size={34} /></div>
            </div>
            <div style={{fontFamily: font, fontWeight: 900, fontSize: 52, color: COLORS.orange, direction: d.dir}}>{mg.asks}</div>
          </div>
        )}
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${drift}px)`}}>
          {d.text.steps.map((st, i) => (
            <React.Fragment key={i}>
              {i > 0 && (
                <div style={{height: 36, width: 6, borderRadius: 3, background: 'rgba(255,255,255,0.1)', overflow: 'hidden'}}>
                  <div style={{height: `${lineP(i) * 100}%`, background: d.text.steps[i].color, boxShadow: `0 0 12px ${d.text.steps[i].color}`}} />
                </div>
              )}
              <StepCard compact={!!mg} step={st} placeAt={mg ? asksAt + 4 + i * 4 : 10 + i * 5} fillAt={stepFrames[i]} active={activeIdx === i} dim={activeIdx > i} />
            </React.Fragment>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Diff: React.FC = () => {
  const {d, font, rtl} = useCtx();
  const frame = useCurrentFrame();
  const a = sp(frame, 0, {damping: 15});
  const b = sp(frame, 12, {damping: 13, stiffness: 120});
  const badgeAt = 34;
  const badge = sp(frame, badgeAt, {damping: 8, stiffness: 230});
  const shrink = interpolate(frame, [10, 24], [1, 0.9], clamp);
  const burstOp = interpolate(frame, [badgeAt - 6, badgeAt + 4, badgeAt + 40], [0, 0.85, 0.25], clamp);
  return (
    <AbsoluteFill>
      <Clip src={d.clips.burst} opacity={burstOp} blend="screen" />
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 150, direction: d.dir, perspective: 1600}}>
        <div
          style={{
            width: 940,
            padding: 32,
            borderRadius: 36,
            background: 'rgba(15,22,38,0.8)',
            border: `2px solid ${COLORS.red}77`,
            opacity: a * 0.85,
            transform: `translateY(${(1 - a) * -80}px) scale(${shrink}) rotateX(${(1 - shrink) * 60}deg)`,
            filter: `saturate(${shrink < 0.95 ? 0.4 : 1})`,
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16}}>
            <Icon kind="x" color={COLORS.red} size={44} />
            <div style={{fontFamily: font, fontWeight: 900, fontSize: 46, color: COLORS.red}}>{d.text.before}</div>
          </div>
          <div style={{display: 'flex', gap: 24, alignItems: 'center'}}>
            <div style={{padding: '16px 26px', borderRadius: 24, background: `${COLORS.orange}CC`, fontFamily: font, fontWeight: 800, fontSize: 40, color: '#1A0E05', whiteSpace: 'nowrap'}}>{d.text.userMsg}</div>
            <Bars widths={[300, 240]} color="rgba(200,210,230,0.25)" start={6} height={18} />
          </div>
        </div>
        <div
          style={{
            marginTop: 30,
            width: 960,
            padding: 36,
            borderRadius: 42,
            background: 'linear-gradient(160deg, rgba(18,32,40,0.97), rgba(10,16,28,0.97))',
            border: `3px solid ${COLORS.green}`,
            boxShadow: `0 0 ${70 + Math.sin(frame / 6) * 20}px ${COLORS.green}55`,
            opacity: b,
            transform: `translateY(${(1 - b) * 260}px) rotateY(${(1 - b) * (rtl ? 30 : -30)}deg) rotateX(${(1 - b) * 20}deg)`,
            position: 'relative',
          }}
        >
          <Shine at={14} />
          <div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16}}>
            <Icon kind="check" color={COLORS.green} size={48} />
            <div style={{fontFamily: font, fontWeight: 900, fontSize: 48, color: COLORS.green}}>{d.text.after}</div>
          </div>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: 14, marginBottom: 30}}>
            {d.text.steps.map((st, i) => {
              const p = sp(frame, 16 + i * 4, {damping: 9, stiffness: 240});
              const chipText = d.chips?.[i] ?? st.label;
              return (
                <div key={i} style={{padding: '12px 26px', borderRadius: 999, background: `${st.color}2E`, border: `2px solid ${st.color}`, color: st.color, fontFamily: font, fontWeight: 900, fontSize: 38, transform: `scale(${p})`, boxShadow: `0 0 18px ${st.color}55`}}>
                  {chipText}
                </div>
              );
            })}
          </div>
          <div style={{position: 'relative', borderRadius: 28, background: COLORS.white, padding: 34}}>
            <div style={{fontFamily: font, fontWeight: 900, fontSize: 42, color: '#0A0F1A', marginBottom: 22}}>{d.text.emailSubject}</div>
            <Bars widths={[720, 660, 700]} color="#C9D3E6" start={26} height={18} />
            <div style={{height: 20}} />
            <Bars widths={[690, 610]} color="#C9D3E6" start={32} height={18} />
            <div style={{height: 20}} />
            <Bars widths={[540]} color="#C9D3E6" start={38} height={18} />
            <div style={{position: 'absolute', bottom: -40, [rtl ? 'left' : 'right']: -28}}>
              <div style={{position: 'relative'}}>
                <Burst at={badgeAt} color={COLORS.green} seed="badge" radius={300} count={30} />
                <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '18px 32px', borderRadius: 999, background: COLORS.green, color: '#05140E', fontFamily: font, fontWeight: 900, fontSize: 46, transform: `scale(${badge}) rotate(${(1 - badge) * -20}deg)`, boxShadow: `0 10px 50px ${COLORS.green}AA`, whiteSpace: 'nowrap', position: 'relative'}}>
                  <Icon kind="check" color="#05140E" size={46} />
                  {d.text.proResult}
                  <Shine at={badgeAt + 8} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Cta: React.FC<{dur: number}> = ({dur}) => {
  const {d, font} = useCtx();
  const frame = useCurrentFrame();
  const a = sp(frame, 4, {damping: 9, stiffness: 170});
  const b = sp(frame, 16, {damping: 9, stiffness: 170});
  const c = sp(frame, 28, {damping: 13});
  const beat = ((frame - 16) % BEAT) / BEAT;
  const pulse = frame > 16 ? 1 + Math.exp(-beat * 5) * 0.06 : 1;
  const zoom = interpolate(frame, [0, dur], [1, 1.12]);
  const fadeOut = interpolate(frame, [dur - 12, dur], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: fadeOut}}>
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <Clip src={d.clips.outro} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(7,11,20,0.75) 0%, rgba(7,11,20,0.4) 50%, rgba(7,11,20,0.92) 100%)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 300, direction: d.dir, gap: 54}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 26, transform: `scale(${a})`, opacity: Math.min(1, a)}}>
          <div style={{transform: `translateY(${-Math.abs(Math.sin(frame / 5)) * 18 * Math.max(0, 1 - (frame - 10) / 40)}px)`}}>
            <Icon kind="bookmark" color={COLORS.orange} size={130} />
          </div>
          <div style={{fontFamily: font, fontWeight: 900, fontSize: 96, color: COLORS.white, textShadow: '0 8px 30px rgba(0,0,0,0.7)'}}>{d.text.save}</div>
        </div>
        <div style={{position: 'relative', transform: `scale(${b * pulse})`, opacity: Math.min(1, b)}}>
          {[0, 1, 2].map((i) => {
            const rp = ((frame - 20 - i * 12) % 36) / 36;
            if (frame < 20 + i * 12) return null;
            return <div key={i} style={{position: 'absolute', inset: 0, borderRadius: 999, border: `4px solid ${COLORS.orange}`, transform: `scale(${1 + rp * 0.6})`, opacity: (1 - rp) * 0.7}} />;
          })}
          <div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '32px 76px', borderRadius: 999, background: `linear-gradient(135deg, ${COLORS.orange}, #FF9A4D)`, boxShadow: `0 0 60px ${COLORS.orange}AA`, position: 'relative', overflow: 'hidden'}}>
            <div style={{transform: `rotate(${Math.sin(frame / 2.5) * 14 * Math.exp(-beat * 3)}deg)`}}>
              <Icon kind="bell" color="#1A0E05" size={74} />
            </div>
            <div style={{fontFamily: font, fontWeight: 900, fontSize: 88, color: '#1A0E05'}}>{d.text.follow}</div>
            <Shine at={30} />
            <Shine at={75} />
          </div>
        </div>
        <div style={{fontFamily: font, fontWeight: 800, fontSize: 60, color: COLORS.white, opacity: c, transform: `translateY(${(1 - c) * 40}px)`, textShadow: '0 6px 20px rgba(0,0,0,0.7)'}}>
          <span style={{color: COLORS.orange}}>+</span> {d.text.daily}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ============ EPISODE ============ */

export const Episode: React.FC<{data: EpisodeData}> = ({data}) => {
  const d = data;
  const c = d.cues;
  const frame = useCurrentFrame();
  const total = s(d.voiceDur + TAIL);
  const rtl = d.dir === 'rtl';
  const font = rtl ? 'Tajawal' : 'Inter';
  const cuts = [c.problem, c.formula, c.diff, c.cta].map(s);
  const scenes: [number, number][] = [
    [0, s(c.problem)],
    [s(c.problem), s(c.formula)],
    [s(c.formula), s(c.diff)],
    [s(c.diff), s(c.cta)],
    [s(c.cta), total],
  ];
  const stepF = c.steps.map(s);
  const stampF = s(c.badAt) + 10;
  const badgeF = s(c.diff) + 34;
  const energy = frame >= s(c.formula) && frame < s(c.cta) ? 1 : 0.3;
  const sfx = (name: string, at: number, vol = 0.5) => (
    <Sequence key={name + at} from={Math.max(0, at)}>
      <Audio src={staticFile(`sfx/sfx_${name}.wav`)} volume={vol} />
    </Sequence>
  );
  const typeStart = s(c.typeAt) - 4;
  const typeEnd = s(c.typeAt) + 14;
  return (
    <C.Provider value={{d, font, rtl}}>
      <AbsoluteFill style={{background: COLORS.bg, overflow: 'hidden'}}>
        <Camera
          punches={[0, ...cuts, ...stepF, stampF, badgeF]}
          shakes={[{at: 2, amp: 26, len: 16}, {at: stampF, amp: 22}, ...stepF.map((f) => ({at: f, amp: 8, len: 10})), {at: badgeF, amp: 14}]}
          beatFrom={s(c.formula)}
          beatTo={s(c.cta)}
        >
          <Background energy={energy} />
          {scenes.map(([a, b], i) => {
            const dur = b - a + (i < scenes.length - 1 ? 4 : 0);
            const Comp = [Hook, Problem, Formula, Diff][i];
            return (
              <Sequence key={i} from={a} durationInFrames={dur}>
                <Whip dur={dur} first={i === 0} last={i === scenes.length - 1}>
                  {i < 4 ? <Comp /> : <Cta dur={dur} />}
                </Whip>
              </Sequence>
            );
          })}
        </Camera>
        <Flash at={cuts} />
        <Karaoke hideBefore={s(c.problem) - 2} hideFrom={s(c.cta)} />
        <Vignette />
        <Grain />
        <ProgressBar total={total} />

        <Audio src={staticFile(d.voice)} volume={1} />
        <Audio src={staticFile(d.music)} volume={(f) => interpolate(f, [0, 6, total - 20, total], [0.0, 0.22, 0.22, 0], clamp)} />
        {sfx('impact', 0, 0.8)}
        {sfx('glitch', 1, 0.35)}
        {cuts.map((f) => sfx('whoosh', f - 5, 0.55))}
        {Array.from({length: Math.max(0, Math.floor((typeEnd - 14 - typeStart) / 3))}).map((_, i) => sfx('click', typeStart + i * 3, 0.25))}
        {sfx('send', typeEnd, 0.4)}
        {sfx('glitch', stampF - 2, 0.55)}
        {sfx('impact', stampF, 0.6)}
        {sfx('riser', s(c.formula) - 45, 0.5)}
        {sfx('subdrop', s(c.formula), 0.7)}
        {stepF.map((f) => sfx('pop', f, 0.55))}
        {stepF.map((f) => sfx('shine', f + 2, 0.3))}
        {sfx('riser', s(c.diff) - 40, 0.4)}
        {sfx('ding', badgeF, 0.55)}
        {sfx('subdrop', badgeF, 0.4)}
        {sfx('pop', s(c.cta) + 16, 0.5)}
      </AbsoluteFill>
    </C.Provider>
  );
};
