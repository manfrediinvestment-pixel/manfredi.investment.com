// Sirve esta carpeta en local y abre video.html listo para hacer seek cuadro por cuadro.
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

export const HERE = fileURLToPath(new URL('.', import.meta.url));
export const FPS = 30;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.woff2': 'font/woff2' };

export async function openVideo(file = 'video.html') {
  const server = createServer(async (req, res) => {
    const p = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
    try { res.writeHead(200, { 'Content-Type': TYPES[extname(p)] || 'application/octet-stream' }).end(await readFile(join(HERE, p))); }
    catch { res.writeHead(404).end(); }
  }).listen(0, '127.0.0.1');
  await new Promise(r => server.once('listening', r));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('[video.html]', e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/${file}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; })));
    await Promise.all([...document.images].map(i => i.decode().catch(() => {})));
  });
  const duration = await page.evaluate(() => window.DURATION);
  const shot = async t => { await page.evaluate(t => window.seek(t), t); return page.screenshot({ type: 'png' }); };
  const close = async () => { await browser.close(); server.close(); };
  return { page, duration, shot, close };
}
