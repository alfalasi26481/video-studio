import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {useAudioData, visualizeAudio} from '@remotion/media-utils';
import {C} from './theme';

// The channel presenter: a robot that "talks" in sync with the voiceover.
// Loudness of the current frame drives the head bob, the eye glow and the
// antenna light, so it reads as speaking without needing a mouth.

const useLoudness = (src?: string) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const audio = useAudioData(src ? staticFile(src) : staticFile('brand/silence.wav'));
  if (!src || !audio) return 0;
  const bins = visualizeAudio({fps, frame, audioData: audio, numberOfSamples: 16, optimizeFor: 'speed'});
  const v = bins.slice(0, 8).reduce((a, b) => a + b, 0) / 8;
  return Math.min(1, v * 5);
};

export const Mascot: React.FC<{
  audio?: string;
  pose?: 'idle' | 'present';
  size: number;
  x: number;
  y: number;
  flip?: boolean;
  delay?: number;
}> = ({audio, pose = 'idle', size, x, y, flip = false, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const loud = useLoudness(audio);
  const enter = spring({frame: frame - delay, fps, config: {damping: 11, stiffness: 120}});
  const bob = Math.sin(frame / 9) * 6 + loud * 10;
  const tilt = Math.sin(frame / 23) * 3 + loud * 2.5 * Math.sin(frame / 3);
  const eyeGlow = interpolate(loud, [0, 1], [0.15, 0.95]);

  return (
    <div style={{position: 'absolute', left: x, top: y, width: size, height: size,
      translate: `0 ${(1 - enter) * 220 - bob}px`, rotate: `${tilt}deg`, opacity: Math.min(1, enter * 1.5)}}>
      {/* soft halo behind the presenter, brighter while speaking */}
      <div style={{position: 'absolute', inset: '12%', borderRadius: '50%',
        background: `radial-gradient(circle, #5ec8ff${Math.round(30 + loud * 60).toString(16).padStart(2, '0')}, transparent 70%)`}} />
      <div style={{position: 'absolute', inset: 0, scale: flip ? '-1 1' : '1 1'}}>
        <Img src={staticFile(pose === 'present' ? 'brand/mascot-present.png' : 'brand/mascot-idle.png')}
          style={{width: '100%', height: '100%', scale: String(1 + loud * 0.035)}} />
        {/* visor light: eyes brighten with the voice (position matches the idle/present art) */}
        <div style={{position: 'absolute', left: pose === 'present' ? '36%' : '27%', top: pose === 'present' ? '18%' : '21%',
          width: pose === 'present' ? '42%' : '46%', height: '18%', borderRadius: '30%',
          background: `radial-gradient(ellipse, #8fe3ff, transparent 70%)`, opacity: eyeGlow, mixBlendMode: 'screen'}} />
        {/* antenna light */}
        <div style={{position: 'absolute', left: pose === 'present' ? '58%' : '44%', top: pose === 'present' ? '1%' : '2.5%',
          width: '12%', height: '12%', borderRadius: '50%', mixBlendMode: 'screen',
          background: `radial-gradient(circle, ${C.accent}, transparent 70%)`, opacity: 0.25 + loud * 0.75,
          scale: String(1 + loud * 0.6)}} />
      </div>
      {/* speech bars under the presenter */}
      <div style={{position: 'absolute', left: '50%', bottom: -10, translate: '-50% 0', display: 'flex', gap: 6, alignItems: 'flex-end', height: 34}}>
        {[0.6, 1, 0.75, 1, 0.6].map((k, i) => (
          <div key={i} style={{width: 7, borderRadius: 4, background: '#5ec8ff',
            height: 6 + loud * 28 * k * (0.7 + 0.3 * Math.abs(Math.sin(frame / 2 + i)))}} />
        ))}
      </div>
    </div>
  );
};
