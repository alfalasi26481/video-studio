import React from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, L, TRIO} from './theme';
import {BiText} from './Text';

// Motion-graphics engine: a scene is boxes (nodes) + arrows (edges) + a
// timeline of events. Event times are FRACTIONS of the scene (0..1), so the
// same choreography stretches to fit the real voiceover length.

export type FlowNode = {
  id: string;
  label: string;
  x: number; // centre, in the 860×820 canvas
  y: number;
  icon?: IconName;
  color?: number | 'ink' | 'good'; // index into TRIO
  w?: number;
  h?: number;
};
export type FlowEdge = {id: string; from: string; to: string; bend?: number};
/**
 * `at` is a fraction of the scene (0..1). With `on`, the event fires when the
 * voice SAYS that word (first narration word containing it; "word#2" = 2nd
 * occurrence) and `at` becomes a small offset — motion lands on the word.
 */
type Anchor = {on?: string};
export type FlowEvent = Anchor & (
  | {at: number; do: 'show'; node: string}
  | {at: number; do: 'draw'; edge: string; dur?: number}
  | {at: number; do: 'packet'; edge: string; dur?: number; label?: string; reverse?: boolean; color?: number | 'good'}
  | {at: number; do: 'pulse'; node: string}
  | {at: number; do: 'spin'; node: string; dur: number}
  | {at: number; do: 'done'; node: string}
  | {at: number; do: 'badge'; node: string; text: string});
export type CameraKey = {at: number; zoom: number; x: number; y: number};

export type FlowSpec = {nodes: FlowNode[]; edges: FlowEdge[]; events: FlowEvent[]; camera?: CameraKey[]};

const W = 860;
const H = 820;
const EASE = Easing.bezier(0.16, 1, 0.3, 1);

const colorOf = (c: FlowNode['color']) =>
  c === 'good' ? C.good : c === 'ink' || c === undefined ? C.ink : TRIO[c % TRIO.length];

// ---------- icons (24×24, stroke) ----------
export type IconName = 'user' | 'doc' | 'spark' | 'bot' | 'plan' | 'search' | 'pen' | 'eye' | 'send' | 'check' | 'question' | 'gear' | 'bookmark'
  | 'globe' | 'laptop' | 'phone' | 'plus' | 'mail' | 'lock' | 'link' | 'shield' | 'clock' | 'warn' | 'chat' | 'image' | 'folder' | 'users' | 'cross' | 'scale' | 'ghost';

const Icon: React.FC<{name: IconName; color: string; size: number}> = ({name, color, size}) => {
  const p = {fill: 'none', stroke: color, strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  const body: Record<IconName, React.ReactNode> = {
    user: <><circle cx={12} cy={8} r={4} {...p} /><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" {...p} /></>,
    doc: <><path d="M6 2h8l4 4v16H6z" {...p} /><path d="M14 2v4h4M9 11h6M9 15h6M9 19h4" {...p} /></>,
    spark: <path d="M12 2l2.2 7.8L22 12l-7.8 2.2L12 22l-2.2-7.8L2 12l7.8-2.2z" {...p} fill={color} fillOpacity={0.18} />,
    bot: <><rect x={5} y={8} width={14} height={11} rx={3} {...p} /><path d="M12 4v4M9 13h.01M15 13h.01M9 16h6" {...p} /><circle cx={12} cy={3.5} r={1} {...p} /></>,
    plan: <><rect x={5} y={4} width={14} height={18} rx={2} {...p} /><path d="M9 2h6v4H9zM8 11h8M8 15h8M8 19h5" {...p} /></>,
    search: <><circle cx={11} cy={11} r={6} {...p} /><path d="M20 20l-4.5-4.5" {...p} /></>,
    pen: <path d="M4 20l4-1L19 8l-3-3L5 16zM14 7l3 3" {...p} />,
    eye: <><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" {...p} /><circle cx={12} cy={12} r={3} {...p} /></>,
    send: <path d="M3 11L21 3l-8 18-2-8z M11 13l10-10" {...p} />,
    check: <path d="M5 12.5l4.5 4.5L19 7" {...p} strokeWidth={2.6} />,
    question: <><path d="M9 9a3 3 0 1 1 4.5 2.6c-1 .6-1.5 1.2-1.5 2.4" {...p} strokeWidth={2.4} /><circle cx={12} cy={18} r={0.6} {...p} strokeWidth={2.4} /></>,
    gear: <><circle cx={12} cy={12} r={3} {...p} /><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1" {...p} /></>,
    bookmark: <path d="M6 3h12v18l-6-4-6 4z" {...p} />,
    globe: <><circle cx={12} cy={12} r={9} {...p} /><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18" {...p} /></>,
    laptop: <><rect x={4} y={5} width={16} height={11} rx={1.5} {...p} /><path d="M2 19h20" {...p} /></>,
    phone: <><rect x={7} y={2.5} width={10} height={19} rx={2.5} {...p} /><path d="M11 18.5h2" {...p} /></>,
    plus: <path d="M12 5v14M5 12h14" {...p} strokeWidth={2.6} />,
    mail: <><rect x={3} y={5} width={18} height={14} rx={2} {...p} /><path d="M3.5 6l8.5 7 8.5-7" {...p} /></>,
    lock: <><rect x={5} y={10.5} width={14} height={10} rx={2} {...p} /><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3M12 14.5v2.5" {...p} /></>,
    link: <path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" {...p} />,
    shield: <><path d="M12 2.5l8 3v6c0 5-3.4 8.6-8 10-4.6-1.4-8-5-8-10v-6z" {...p} /><path d="M8.5 12l2.5 2.5 4.5-5" {...p} /></>,
    clock: <><circle cx={12} cy={12} r={9} {...p} /><path d="M12 7v5l3.5 2" {...p} /></>,
    warn: <><path d="M12 3l9.5 17h-19z" {...p} /><path d="M12 10v4.5M12 17.5h.01" {...p} strokeWidth={2.4} /></>,
    chat: <path d="M4 5h16v11H9l-5 4z" {...p} />,
    image: <><rect x={3} y={4} width={18} height={16} rx={2} {...p} /><circle cx={9} cy={10} r={2} {...p} /><path d="M3 17l5-4 4 3 3-2 6 4" {...p} /></>,
    folder: <path d="M3 6.5h6l2 2h10v10.5H3z" {...p} />,
    users: <><circle cx={9} cy={8.5} r={3.5} {...p} /><path d="M2.5 20c0-3.8 2.9-6 6.5-6s6.5 2.2 6.5 6M16 5a3.5 3.5 0 0 1 0 7M18 14.2c2.2.7 3.5 2.7 3.5 5.8" {...p} /></>,
    cross: <path d="M6 6l12 12M18 6L6 18" {...p} strokeWidth={2.6} />,
    scale: <><path d="M12 3v18M7 21h10M4 7h16M4 7l-2.5 6a3 3 0 0 0 5 0zM20 7l-2.5 6a3 3 0 0 0 5 0z" {...p} /></>,
    ghost: <><path d="M5 21V10a7 7 0 0 1 14 0v11l-2.5-2-2.3 2-2.2-2-2.2 2-2.3-2z" {...p} /><path d="M9.5 10h.01M14.5 10h.01" {...p} strokeWidth={2.6} /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24">{body[name]}</svg>;
};

// ---------- geometry ----------
type Pt = {x: number; y: number};
const bez = (a: Pt, c: Pt, b: Pt, t: number): Pt => ({
  x: (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * c.x + t * t * b.x,
  y: (1 - t) * (1 - t) * a.y + 2 * (1 - t) * t * c.y + t * t * b.y,
});
// Trim a segment so it starts/ends at the node's box edge, not its centre.
const edgePoint = (from: FlowNode, toward: Pt): Pt => {
  const w = (from.w ?? 200) / 2 + 10, h = (from.h ?? 150) / 2 + 10;
  const dx = toward.x - from.x, dy = toward.y - from.y;
  const s = Math.min(Math.abs(dx) > 0 ? w / Math.abs(dx) : Infinity, Math.abs(dy) > 0 ? h / Math.abs(dy) : Infinity);
  return {x: from.x + dx * s, y: from.y + dy * s};
};
const edgeGeom = (e: FlowEdge, nodes: Record<string, FlowNode>) => {
  const A = nodes[e.from], B = nodes[e.to];
  const mid = {x: (A.x + B.x) / 2, y: (A.y + B.y) / 2};
  const len = Math.hypot(B.x - A.x, B.y - A.y) || 1;
  const bend = e.bend ?? 0;
  const ctrl = {x: mid.x + (-(B.y - A.y) / len) * bend, y: mid.y + ((B.x - A.x) / len) * bend};
  const a = edgePoint(A, ctrl), b = edgePoint(B, ctrl);
  return {a, b, c: {x: (a.x + b.x) / 2 + (ctrl.x - mid.x), y: (a.y + b.y) / 2 + (ctrl.y - mid.y)}};
};

// ---------- the scene ----------
/** Bounding box of everything a diagram draws (nodes + the badge space above them). */
const bbox = (spec: FlowSpec) => {
  const hasBadge = (id: string) => spec.events.some((e) => e.do === 'badge' && e.node === id);
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const n of spec.nodes) {
    const w = n.w ?? 200, h = n.h ?? 150;
    x0 = Math.min(x0, n.x - w / 2 - 20); x1 = Math.max(x1, n.x + w / 2 + 20);
    y0 = Math.min(y0, n.y - h / 2 - (hasBadge(n.id) ? 74 : 20)); y1 = Math.max(y1, n.y + h / 2 + 20);
  }
  return {x0, x1, y0, y1};
};

/** Sound cues a diagram implies, in frames from scene start (deduped so it never clatters). */
export const flowSfx = (spec: FlowSpec, frames: number) => {
  const out: {at: number; kind: 'pop' | 'swish' | 'tick'}[] = [];
  for (const e of spec.events) {
    const at = Math.round(e.at * frames);
    const kind = e.do === 'show' ? 'pop' : e.do === 'packet' ? 'swish' : e.do === 'done' || e.do === 'badge' ? 'tick' : null;
    if (!kind) continue;
    if (out.some((o) => o.kind === kind && Math.abs(o.at - at) < 7)) continue;
    out.push({at, kind});
  }
  return out;
};

/**
 * Draws the diagram centred in the band [top, bottom] of the frame, whatever
 * coordinates the choreography used. No empty half-screens, no overlap with
 * the headline above or the captions below.
 */
export const Flow: React.FC<{spec: FlowSpec; frames: number; top?: number; bottom?: number; dir?: 'rtl' | 'ltr'}> = ({
  spec, frames, top = 470, bottom = L.contentBottom, dir = 'rtl',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const T = (f: number) => f * frames; // fraction → frame
  const nodes = Object.fromEntries(spec.nodes.map((n) => [n.id, n]));
  const ev = spec.events;
  const firstAt = (kind: FlowEvent['do'], key: string) =>
    ev.find((e) => e.do === kind && ((e as any).node === key || (e as any).edge === key))?.at;

  const b = bbox(spec);
  const bw = b.x1 - b.x0, bh = b.y1 - b.y0;
  const fit = Math.min(1.12, (L.width + 40) / bw, (bottom - top) / bh); // grow up to 12%, shrink if it would not fit
  const ox = L.left + (L.width - bw * fit) / 2 - b.x0 * fit;
  const oy = top + (bottom - top - bh * fit) / 2 - b.y0 * fit;

  const cam = spec.camera && spec.camera.length > 0 ? spec.camera : [{at: 0, zoom: 1, x: 0, y: 0}];
  const camAt = (k: 'zoom' | 'x' | 'y') =>
    cam.length === 1 ? cam[0][k] : interpolate(frame, cam.map((c) => T(c.at)), cam.map((c) => c[k]),
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  const packets = ev.filter((x): x is Extract<FlowEvent, {do: 'packet'}> => x.do === 'packet').map((x) => {
    const d = x.dur ?? 0.12;
    const t = interpolate(frame, [T(x.at), T(x.at + d)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
    const vis = frame >= T(x.at) && frame <= T(x.at + d) + 4;
    const e = spec.edges.find((k) => k.id === x.edge)!;
    const g = edgeGeom(e, nodes);
    const pos = (u: number) => bez(g.a, g.c, g.b, x.reverse ? 1 - u : u);
    const col = x.color === 'good' ? C.good : x.color !== undefined ? TRIO[x.color % TRIO.length] : C.accent;
    const fade = Math.min(1, (frame - T(x.at)) / 4, (T(x.at + d) + 4 - frame) / 4);
    return {x, t, vis, pos, col, head: pos(t), fade};
  });

  return (
    <div style={{position: 'absolute', left: ox, top: oy, width: W, height: H, overflow: 'visible',
      scale: String(fit), transformOrigin: '0 0'}}>
      <div style={{width: W, height: H, scale: String(camAt('zoom')), translate: `${camAt('x')}px ${camAt('y')}px`,
        transformOrigin: `${(b.x0 + b.x1) / 2}px ${(b.y0 + b.y1) / 2}px`}}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
          {spec.edges.map((e) => {
            const at = firstAt('draw', e.id);
            if (at === undefined) return null;
            const d = (ev.find((x) => x.do === 'draw' && x.edge === e.id) as any)?.dur ?? 0.08;
            const p = interpolate(frame, [T(at), T(at + d)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE});
            if (p <= 0) return null;
            const g = edgeGeom(e, nodes);
            const tip = bez(g.a, g.c, g.b, 1), pre = bez(g.a, g.c, g.b, 0.96);
            const ang = Math.atan2(tip.y - pre.y, tip.x - pre.x);
            const s = 18;
            return (
              <g key={e.id}>
                <path d={`M${g.a.x},${g.a.y} Q${g.c.x},${g.c.y} ${g.b.x},${g.b.y}`} pathLength={1}
                  fill="none" stroke={C.muted} strokeOpacity={0.75} strokeWidth={4} strokeLinecap="round"
                  strokeDasharray="1 1" strokeDashoffset={1 - p} />
                {p > 0.92 && (
                  <path fill={C.muted} opacity={(p - 0.92) / 0.08}
                    d={`M${tip.x},${tip.y} L${tip.x - s * Math.cos(ang - 0.42)},${tip.y - s * Math.sin(ang - 0.42)} L${tip.x - s * Math.cos(ang + 0.42)},${tip.y - s * Math.sin(ang + 0.42)} Z`} />
                )}
              </g>
            );
          })}
          {packets.filter((p) => p.vis).map((p, i) => (
            <g key={`p${i}`} opacity={p.fade}>
              {[0.12, 0.08, 0.04].map((lag, k) => {
                const q = p.pos(Math.max(0, p.t - lag));
                return <circle key={k} cx={q.x} cy={q.y} r={10 - k * 2} fill={p.col} opacity={0.15 + k * 0.12} />;
              })}
              <circle cx={p.head.x} cy={p.head.y} r={15} fill={p.col} />
              <circle cx={p.head.x} cy={p.head.y} r={26} fill={p.col} opacity={0.18} />
            </g>
          ))}
        </svg>
        {spec.nodes.map((n) => <NodeBox key={n.id} n={n} ev={ev} T={T} fps={fps} dir={dir} />)}
        {/* packet labels are HTML so mixed Arabic/English shapes and sizes itself */}
        {packets.filter((p) => p.vis && p.x.label).map((p, i) => (
          <div key={`l${i}`} style={{position: 'absolute', left: p.head.x, top: p.head.y - 44, translate: '-50% -100%',
            opacity: p.fade, background: C.bg, border: `2px solid ${p.col}`, borderRadius: 999, padding: '6px 20px',
            whiteSpace: 'nowrap', boxShadow: '0 8px 24px rgba(0,0,0,.35)'}}>
            <BiText text={p.x.label!} dir={dir} style={{fontWeight: 600, fontSize: 28, color: C.ink}} />
          </div>
        ))}
      </div>
    </div>
  );
};

const NodeBox: React.FC<{n: FlowNode; ev: FlowEvent[]; T: (f: number) => number; fps: number; dir: 'rtl' | 'ltr'}> = ({n, ev, T, fps, dir}) => {
  const frame = useCurrentFrame();
  const show = ev.find((e) => e.do === 'show' && e.node === n.id);
  if (!show) return null;
  const pop = spring({frame: frame - T(show.at), fps, config: {damping: 11, stiffness: 140}});
  if (frame < T(show.at)) return null;
  const w = n.w ?? 200, h = n.h ?? 150;
  const base = colorOf(n.color);
  const done = ev.find((e) => e.do === 'done' && e.node === n.id);
  const isDone = !!done && frame >= T(done.at);
  const col = isDone ? C.good : base;
  const donePop = done ? spring({frame: frame - T(done.at), fps, config: {damping: 9}}) : 0;

  const pulses = ev.filter((e) => e.do === 'pulse' && e.node === n.id);
  const spins = ev.filter((e): e is Extract<FlowEvent, {do: 'spin'}> => e.do === 'spin' && e.node === n.id);
  const spinning = spins.find((s) => frame >= T(s.at) && frame <= T(s.at + s.dur));
  const badges = ev.filter((e): e is Extract<FlowEvent, {do: 'badge'}> => e.do === 'badge' && e.node === n.id && frame >= T(e.at));
  const badge = badges[badges.length - 1];
  const badgePop = badge ? spring({frame: frame - T(badge.at), fps, config: {damping: 10}}) : 0;

  return (
    <div style={{position: 'absolute', left: n.x - w / 2, top: n.y - h / 2, width: w, height: h,
      scale: String(0.4 + 0.6 * pop), opacity: Math.min(1, pop * 1.4)}}>
      {pulses.map((p, i) => {
        const k = interpolate(frame, [T(p.at), T(p.at) + 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        if (k <= 0 || k >= 1) return null;
        return <div key={i} style={{position: 'absolute', inset: -10 - k * 40, borderRadius: 38 + k * 30,
          border: `4px solid ${col}`, opacity: 1 - k}} />;
      })}
      {spinning && (
        <svg style={{position: 'absolute', left: -34, top: -34, width: w + 68, height: h + 68, overflow: 'visible',
          rotate: `${(frame - T(spinning.at)) * 6}deg`}} viewBox={`0 0 ${w + 68} ${h + 68}`}>
          <rect x={4} y={4} width={w + 60} height={h + 60} rx={44} fill="none" stroke={col} strokeWidth={5}
            strokeDasharray="40 26" strokeLinecap="round" />
        </svg>
      )}
      <div style={{position: 'absolute', inset: 0, borderRadius: 32, background: C.panel,
        border: `4px solid ${col}`, boxShadow: `0 0 ${isDone || spinning ? 40 : 18}px ${col}55`,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 6}}>
        {n.icon && <Icon name={n.icon} color={col} size={h > 120 ? 64 : 48} />}
        <BiText text={n.label} dir={dir} style={{fontWeight: 700, fontSize: n.label.length > 10 ? 30 : 34, color: C.ink,
          textAlign: 'center', lineHeight: 1.3, padding: '0 12px', display: 'block'}} />
      </div>
      {isDone && (
        <div style={{position: 'absolute', right: -18, top: -18, width: 56, height: 56, borderRadius: 28, background: C.good,
          display: 'grid', placeItems: 'center', scale: String(donePop)}}>
          <Icon name="check" color={C.bg} size={36} />
        </div>
      )}
      {badge && (
        <div style={{position: 'absolute', left: '50%', top: -58, translate: '-50% 0', scale: String(badgePop),
          background: base, color: C.bg, padding: '6px 20px', borderRadius: 999, whiteSpace: 'nowrap'}}>
          <BiText text={badge.text} dir={dir} style={{fontWeight: 700, fontSize: 30}} />
        </div>
      )}
    </div>
  );
};

// ---------- living background ----------
// A slowly drifting dot grid and two soft light blobs, so no frame is static.
export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = (frame * 0.6) % 60;
  const bx = Math.sin(frame / 90) * 160, by = Math.cos(frame / 110) * 120;
  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: -60, translate: `${drift}px ${drift}px`, opacity: 0.35,
        backgroundImage: `radial-gradient(${C.line} 2px, transparent 2.5px)`, backgroundSize: '60px 60px'}} />
      <div style={{position: 'absolute', width: 900, height: 900, left: 90 + bx, top: 300 + by, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.accent}22, transparent 65%)`}} />
      <div style={{position: 'absolute', width: 800, height: 800, left: -200 - bx * 0.6, top: 1000 - by, borderRadius: '50%',
        background: `radial-gradient(circle, #5ec8ff1c, transparent 65%)`}} />
    </div>
  );
};

export {Icon};
