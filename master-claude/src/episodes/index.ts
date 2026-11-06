import type {EpisodeData} from '../engine/types';
import {EP01_AR, EP01_EN} from './ep01';
import {EP02_AR, EP02_EN} from './ep02';
import {EP03_AR, EP03_EN} from './ep03';
import {EP04_AR, EP04_EN} from './ep04';
import {EP05_AR, EP05_EN} from './ep05';
import {EP06_AR, EP06_EN} from './ep06';
import {EP07_AR, EP07_EN} from './ep07';
import {EP08_AR, EP08_EN} from './ep08';
import {EP09_AR, EP09_EN} from './ep09';
import {EP10_AR, EP10_EN} from './ep10';
import {EP11_AR, EP11_EN} from './ep11';
import {EP12_AR, EP12_EN} from './ep12';
import {EP13_AR, EP13_EN} from './ep13';
import {EP14_AR, EP14_EN} from './ep14';
import {EP15_AR, EP15_EN} from './ep15';

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
  'EP07-AR': EP07_AR,
  'EP07-EN': EP07_EN,
  'EP08-AR': EP08_AR,
  'EP08-EN': EP08_EN,
  'EP09-AR': EP09_AR,
  'EP09-EN': EP09_EN,
  'EP10-AR': EP10_AR,
  'EP10-EN': EP10_EN,
  'EP11-AR': EP11_AR,
  'EP11-EN': EP11_EN,
  'EP12-AR': EP12_AR,
  'EP12-EN': EP12_EN,
  'EP13-AR': EP13_AR,
  'EP13-EN': EP13_EN,
  'EP14-AR': EP14_AR,
  'EP14-EN': EP14_EN,
  'EP15-AR': EP15_AR,
  'EP15-EN': EP15_EN,
};
