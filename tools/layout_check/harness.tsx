// Read-only harness: renders one frame of an approved-engine episode in a plain page
// (via @remotion/player's <Thumbnail>) so measure.mjs can read real text boxes.
// It imports the engine and episode data as-is; nothing in master-claude/ is modified.
import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Thumbnail} from '@remotion/player';
import {Episode} from '../../master-claude/src/engine/Episode';
import {FPS, TAIL} from '../../master-claude/src/engine/types';
import {EPISODES} from '../../master-claude/src/episodes';

const id = new URLSearchParams(location.search).get('id') || '';
const data = (EPISODES as Record<string, any>)[id];
const w = window as any;
w.__EPISODES = Object.keys(EPISODES);

const App: React.FC = () => {
  const [frame, setFrame] = useState(0);
  useEffect(() => {
    w.__setFrame = (f: number) =>
      new Promise<void>((res) => {
        setFrame(f);
        requestAnimationFrame(() => requestAnimationFrame(() => res()));
      });
    w.__ready = true;
  }, []);
  if (!data) return <div id="missing">unknown episode {id}</div>;
  const total = Math.round((data.voiceDur + TAIL) * FPS);
  w.__total = total;
  w.__cues = data.cues;
  return (
    <div id="canvas" style={{width: 1080, height: 1920, position: 'relative'}}>
      <Thumbnail
        component={Episode as any}
        inputProps={{data}}
        compositionWidth={1080}
        compositionHeight={1920}
        durationInFrames={total}
        fps={FPS}
        frameToDisplay={frame}
        style={{width: 1080, height: 1920}}
      />
    </div>
  );
};

createRoot(document.getElementById('root')!).render(<App />);
