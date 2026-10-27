import React from 'react';
import {CalculateMetadataFunction, Composition, staticFile} from 'remotion';
import {getAudioDurationInSeconds} from '@remotion/media-utils';
import {Episode} from './Episode';
import {FPS, H, W, WPS} from './theme';
import type {EpisodeData, EpisodeProps, Lang} from './types';

type Props = EpisodeProps & {id: string};

// Loads public/episodes/<id>.json and sets each scene's length:
// voiceover clip length when one exists, otherwise an estimate from the word count.
const calc: CalculateMetadataFunction<Props> = async ({props}) => {
  const episode: EpisodeData = await fetch(staticFile(`episodes/${props.id}.json`)).then((r) => r.json());
  const track = episode[props.lang];
  const sceneFrames = await Promise.all(
    track.scenes.map(async (s) => {
      if (s.audio) {
        const sec = await getAudioDurationInSeconds(staticFile(s.audio));
        return Math.ceil((sec + 0.5) * FPS);
      }
      const words = s.narration.split(/\s+/).filter(Boolean).length;
      return Math.ceil(Math.max(3, words / WPS[props.lang] + 0.9) * FPS);
    }),
  );
  return {
    durationInFrames: sceneFrames.reduce((a, b) => a + b, 0),
    props: {...props, episode, sceneFrames},
  };
};

const placeholder = {} as EpisodeData;
const langs: Lang[] = ['ar', 'en'];

export const RemotionRoot: React.FC = () => (
  <>
    {langs.map((lang) => (
      <Composition
        key={lang}
        id={`Episode-${lang}`}
        component={Episode as unknown as React.FC<Props>}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={300}
        defaultProps={{id: 'ep01', lang, episode: placeholder}}
        calculateMetadata={calc}
      />
    ))}
  </>
);
