import React from 'react';
import {Composition} from 'remotion';
import {Episode} from './engine/Episode';
import {EpisodeV2} from './engine2/Episode';
import {FPS, TAIL} from './engine/types';
import {EPISODES} from './episodes';
import {STYLE_DEMOS} from './episodes/style-demos';

// EP01–EP05 render with the frozen v1 engine. An episode whose data has `engine: 2` uses engine v2 (EP06+).
const pick = (data: object) => ((data as {engine?: number}).engine === 2 ? EpisodeV2 : Episode);

export const Root: React.FC = () => (
  <>
    {Object.entries({...EPISODES, ...STYLE_DEMOS}).map(([id, data]) => (
      <Composition key={id} id={id} component={pick(data)} durationInFrames={Math.round((data.voiceDur + TAIL) * FPS)} fps={FPS} width={1080} height={1920} defaultProps={{data}} />
    ))}
  </>
);
