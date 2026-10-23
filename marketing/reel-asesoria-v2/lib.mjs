// Servidor estático en la raíz del repo + página lista para buscar cuadros.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { existsSync } from 'node:fs';
import { W, H } from './config.mjs';

export const HERE = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(HERE, '../..');
export const CHROMIUM = process.env.CHROMIUM || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);

export async function openComposition({ port = 8821, cuts = null, file = 'index.html' } = {}) {
  const srv = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 700));
  const browser = await chromium.launch({ executablePath: CHROMIUM, args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('[page error]', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  const q = cuts ? '?cuts=' + encodeURIComponent(JSON.stringify(cuts)) : '';
  await page.goto(`http://127.0.0.1:${port}/marketing/reel-asesoria-v2/${file}${q}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
  const close = async () => { await browser.close(); srv.kill(); };
  return { page, close };
}
