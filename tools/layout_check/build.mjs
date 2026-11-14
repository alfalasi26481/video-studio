// Bundles harness.tsx; every `remotion`/`react` import (engine included) resolves to ONE copy here.
import {build} from 'esbuild';
import {createRequire} from 'module';
import path from 'path';
import {fileURLToPath} from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
const req = createRequire(import.meta.url);
const pkgDir = (p) => path.dirname(req.resolve(p + '/package.json'));
await build({
  entryPoints: [path.join(here, 'harness.tsx')],
  bundle: true,
  outfile: path.join(here, 'dist/harness.js'),
  format: 'iife',
  jsx: 'automatic',
  loader: {'.json': 'json'},
  define: {'process.env.NODE_ENV': '"production"'},
  alias: {remotion: pkgDir('remotion'), react: pkgDir('react'), 'react-dom': pkgDir('react-dom')},
  logLevel: 'warning',
});
