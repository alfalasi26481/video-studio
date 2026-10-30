import React from 'react';
import {Composition} from 'remotion';
import {Episode} from './engine/Episode';
import {FPS, TAIL} from './engine/types';
import {EPISODES} from './episodes';

export const Root: React.FC = () => (
  <>
    {Object.entries(EPISODES).map(([id, data]) => (
      <Composition key={id} id={id} component={Episode} durationInFrames={Math.round((data.voiceDur + TAIL) * FPS)} fps={FPS} width={1080} height={1920} defaultProps={{data}} />
    ))}
  </>
);
