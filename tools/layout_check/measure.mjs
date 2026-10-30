// Measures every visible text line of an engine episode, frame by frame, in Chromium.
//   node measure.mjs EP01-AR [stepFrames=6] > boxes.json
// Output: {id, width, height, total, cues, frames:[{f, texts:[{t, x0,y0,x1,y1, opacity, box:[x0,y0,x1,y1]|null}]}]}
// `box` = the nearest ancestor that draws a card (background/border) — used to catch text spilling out.
// Read-only: serves master-claude/public and the bundled harness; writes nothing.
import http from 'http';
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';
import {createRequire} from 'module';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const pub = path.resolve(here, '../../master-claude/public');
const [id, stepArg] = process.argv.slice(2);
if (!id) { console.error('usage: node measure.mjs EP01-AR [step]'); process.exit(2); }
const step = Number(stepArg || 6);
const TYPES = {'.js': 'text/javascript', '.html': 'text/html', '.woff2': 'font/woff2', '.wav': 'audio/wav', '.mp4': 'video/mp4'};

const server = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (u === '/') { res.writeHead(200, {'content-type': 'text/html'}); return res.end('<!doctype html><meta charset="utf-8"><body style="margin:0;background:#000"><div id="root"></div><script src="/harness.js"></script>'); }
  const file = u === '/harness.js' ? path.join(here, 'dist/harness.js') : path.join(pub, path.normalize(u).replace(/^([/\\])+/, ''));
  if (!file.startsWith(pub) && !file.startsWith(here)) { res.writeHead(403); return res.end(); }
  // media is irrelevant to layout: answer 204 so the page never waits on large clips
  if (/\.(mp4|wav)$/.test(file)) { res.writeHead(204); return res.end(); }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404); return res.end(); }
    res.writeHead(200, {'content-type': TYPES[path.extname(file)] || 'application/octet-stream'});
    res.end(buf);
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch();
try {
  const page = await browser.newPage({viewport: {width: 1080, height: 1920}});
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${port}/?id=${encodeURIComponent(id)}`);
  await page.waitForFunction(() => window.__ready === true || document.getElementById('missing'), null, {timeout: 30000});
  if (await page.$('#missing')) throw new Error(`unknown episode ${id}; known: ${await page.evaluate(() => window.__EPISODES.join(', '))}`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.fonts].filter((f) => f.status === 'loaded').length >= 12, null, {timeout: 30000});
  const total = await page.evaluate(() => window.__total);
  const cues = await page.evaluate(() => window.__cues);
  const frames = [];
  for (let f = 0; f < total; f += step) {
    await page.evaluate((fr) => window.__setFrame(fr), f);
    const texts = await page.evaluate(() => {
      const root = document.getElementById('canvas');
      const out = [];
      const opacityOf = (el) => {
        let o = 1;
        for (let e = el; e && e !== root; e = e.parentElement) {
          const cs = getComputedStyle(e);
          if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
          o *= Number(cs.opacity);
        }
        return o;
      };
      const cardOf = (el) => {
        for (let e = el; e && e !== root; e = e.parentElement) {
          const cs = getComputedStyle(e);
          const bg = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.backgroundImage !== 'none';
          const border = parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none';
          if (bg || border) {
            const r = e.getBoundingClientRect();
            if (r.width >= 1080 && r.height >= 1920) return null; // full-frame layers are not cards
            return [r.left, r.top, r.right, r.bottom];
          }
        }
        return null;
      };
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        const t = n.textContent.trim();
        if (!t) continue;
        const el = n.parentElement;
        const op = opacityOf(el);
        if (op < 0.5) continue;
        // glitch layers duplicate their child text with a colour shift; the base copy is enough
        const cs = getComputedStyle(el.closest('[style]') || el);
        if (cs.mixBlendMode === 'screen') continue;
        const range = document.createRange();
        range.selectNodeContents(n);
        const card = cardOf(el);
        for (const r of range.getClientRects()) {
          if (r.width < 2 || r.height < 2) continue;
          out.push({t, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, opacity: Math.round(op * 100) / 100, box: card});
        }
      }
      return out;
    });
    frames.push({f, texts});
  }
  process.stdout.write(JSON.stringify({id, width: 1080, height: 1920, fps: 30, total, cues, step, errors, frames}));
} finally {
  await browser.close();
  server.close();
}
