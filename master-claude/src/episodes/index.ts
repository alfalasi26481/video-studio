import type {EpisodeData} from '../engine/types';
import {EP01_AR, EP01_EN} from './ep01';
import {EP02_AR, EP02_EN} from './ep02';
import {EP03_AR, EP03_EN} from './ep03';
import {EP04_AR, EP04_EN} from './ep04';
import {EP05_AR, EP05_EN} from './ep05';
import {EP06_AR, EP06_EN} from './ep06';

/**
 * Episode registry. Composition ids = `EP<NN>-AR` / `EP<NN>-EN`.
 * To add an episode: create episodes/epNN.ts (copy the closest existing one), then add one line here.
 */
export const EPISODES: Record<string, EpisodeData> = {
  'EP01-AR': EP01_AR,
  'EP01-EN': EP01_EN,
  'EP02-AR': EP02_AR,
  'EP02-EN': EP02_EN,
  'EP03-AR': EP03_AR,
  'EP03-EN': EP03_EN,
  'EP04-AR': EP04_AR,
  'EP04-EN': EP04_EN,
  'EP05-AR': EP05_AR,
  'EP05-EN': EP05_EN,
  'EP06-AR': EP06_AR,
  'EP06-EN': EP06_EN,
};
