import React from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, TRIO} from './theme';

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
export type FlowEvent =
  | {at: number; do: 'show'; node: string}
  | {at: number; do: 'draw'; edge: string; dur?: number}
  | {at: number; do: 'packet'; edge: string; dur?: number; label?: string; reverse?: boolean; color?: number | 'good'}
  | {at: number; do: 'pulse'; node: string}
  | {at: number; do: 'spin'; node: string; dur: number}
  | {at: number; do: 'done'; node: string}
  | {at: number; do: 'badge'; node: string; text: string};
export type CameraKey = {at: number; zoom: number; x: number; y: number};

export type FlowSpec = {nodes: FlowNode[]; edges: FlowEdge[]; events: FlowEvent[]; camera?: CameraKey[]};

const W = 860;
const H = 820;
const EASE = Easing.bezier(0.16, 1, 0.3, 1);

const colorOf = (c: FlowNode['color']) =>
  c === 'good' ? C.good : c === 'ink' || c === undefined ? C.ink : TRIO[c % TRIO.length];

// ---------- icons (24×24, stroke) ----------
export type IconName = 'user' | 'doc' | 'spark' | 'bot' | 'plan' | 'search' | 'pen' | 'eye' | 'send' | 'check' | 'question' | 'gear' | 'bookmark';

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
  const w = (from.w ?? 190) / 2 + 10, h = (from.h ?? 150) / 2 + 10;
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
export const Flow: React.FC<{spec: FlowSpec; frames: number; top?: number}> = ({spec, frames, top = 470}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const T = (f: number) => f * frames; // fraction → frame
  const nodes = Object.fromEntries(spec.nodes.map((n) => [n.id, n]));
  const ev = spec.events;
  const firstAt = (kind: FlowEvent['do'], key: string) =>
    ev.find((e) => e.do === kind && ((e as any).node === key || (e as any).edge === key))?.at;

  // Camera: piecewise interpolation between keyframes.
  const cam = spec.camera && spec.camera.length > 0 ? spec.camera : [{at: 0, zoom: 1, x: 0, y: 0}];
  const camAt = (k: 'zoom' | 'x' | 'y') =>
    cam.length === 1 ? cam[0][k] : interpolate(frame, cam.map((c) => T(c.at)), cam.map((c) => c[k]),
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  return (
    <div style={{position: 'absolute', left: 80, top, width: W, height: H, overflow: 'visible'}}>
      <div style={{width: W, height: H, scale: String(camAt('zoom')), translate: `${camAt('x')}px ${camAt('y')}px`,
        transformOrigin: '50% 50%'}}>
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
            const s = 16;
            return (
              <g key={e.id}>
                <path d={`M${g.a.x},${g.a.y} Q${g.c.x},${g.c.y} ${g.b.x},${g.b.y}`} pathLength={1}
                  fill="none" stroke={C.muted} strokeWidth={4} strokeLinecap="round"
                  strokeDasharray="1 1" strokeDashoffset={1 - p} />
                {p > 0.92 && (
                  <path fill={C.muted} opacity={(p - 0.92) / 0.08}
                    d={`M${tip.x},${tip.y} L${tip.x - s * Math.cos(ang - 0.45)},${tip.y - s * Math.sin(ang - 0.45)} L${tip.x - s * Math.cos(ang + 0.45)},${tip.y - s * Math.sin(ang + 0.45)} Z`} />
                )}
              </g>
            );
          })}
          {/* packets travel along their edge, with a short glowing trail */}
          {ev.filter((x): x is Extract<FlowEvent, {do: 'packet'}> => x.do === 'packet').map((x, i) => {
            const d = x.dur ?? 0.12;
            const t = interpolate(frame, [T(x.at), T(x.at + d)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
            const vis = frame >= T(x.at) && frame <= T(x.at + d) + 4;
            if (!vis) return null;
            const e = spec.edges.find((k) => k.id === x.edge)!;
            const g = edgeGeom(e, nodes);
            const pos = (u: number) => bez(g.a, g.c, g.b, x.reverse ? 1 - u : u);
            const col = x.color === 'good' ? C.good : x.color !== undefined ? TRIO[x.color % TRIO.length] : C.accent;
            const head = pos(t);
            return (
              <g key={`p${i}`}>
                {[0.12, 0.08, 0.04].map((lag, k) => {
                  const q = pos(Math.max(0, t - lag));
                  return <circle key={k} cx={q.x} cy={q.y} r={10 - k * 2} fill={col} opacity={0.15 + k * 0.12} />;
                })}
                <circle cx={head.x} cy={head.y} r={15} fill={col} />
                <circle cx={head.x} cy={head.y} r={26} fill={col} opacity={0.18} />
                {x.label && (
                  <g>
                    <rect x={head.x - 70} y={head.y - 62} width={140} height={40} rx={20} fill={C.bg} stroke={col} strokeWidth={2} />
                    <text x={head.x} y={head.y - 34} textAnchor="middle" fontFamily={F.body} fontWeight={600} fontSize={22} fill={C.ink}>{x.label}</text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
        {spec.nodes.map((n) => <NodeBox key={n.id} n={n} ev={ev} T={T} fps={fps} />)}
      </div>
    </div>
  );
};

const NodeBox: React.FC<{n: FlowNode; ev: FlowEvent[]; T: (f: number) => number; fps: number}> = ({n, ev, T, fps}) => {
  const frame = useCurrentFrame();
  const show = ev.find((e) => e.do === 'show' && e.node === n.id);
  if (!show) return null;
  const pop = spring({frame: frame - T(show.at), fps, config: {damping: 11, stiffness: 140}});
  if (frame < T(show.at)) return null;
  const w = n.w ?? 190, h = n.h ?? 150;
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
        <span style={{fontFamily: F.display, fontWeight: 700, fontSize: n.label.length > 9 ? 26 : 32, color: C.ink,
          textAlign: 'center', lineHeight: 1.25, padding: '0 10px'}}>{n.label}</span>
      </div>
      {isDone && (
        <div style={{position: 'absolute', right: -18, top: -18, width: 56, height: 56, borderRadius: 28, background: C.good,
          display: 'grid', placeItems: 'center', scale: String(donePop)}}>
          <Icon name="check" color={C.bg} size={36} />
        </div>
      )}
      {badge && (
        <div style={{position: 'absolute', left: '50%', top: -58, translate: '-50% 0', scale: String(badgePop),
          background: base, color: C.bg, fontFamily: F.mono, fontSize: 30, padding: '4px 18px', borderRadius: 999,
          whiteSpace: 'nowrap'}}>{badge.text}</div>
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
