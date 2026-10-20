// Saca del sitio el rendimiento REAL de la Cartera Manfredi desde el 22/05/2026
// y el del S&P 500 en la MISMA ventana (rebasado a esa fecha), con la misma cuenta
// que la sección Asesoría (mfBuildPerformanceSeries). No usa el "YTD proyectado".
// Escribe data.json, que lee video.html. Correrlo el día del render.
//   node data.mjs            → sirve el repo en local (misma lógica que el sitio)
//   node data.mjs --live     → usa https://manfredinvestment.com
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile, writeFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = join(HERE, '../..');
const LIVE = process.argv.includes('--live');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.woff2': 'font/woff2' };

let server, base = 'https://manfredinvestment.com';
if (!LIVE) {
  server = createServer(async (req, res) => {
    const p = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
    const file = p.endsWith('/') || p.endsWith('\\') ? p + 'index.html' : p;
    try {
      const body = await readFile(join(ROOT, file));
      res.writeHead(200, { 'Content-Type': TYPES[extname(file)] || 'application/octet-stream' }).end(body);
    } catch { res.writeHead(404).end(); }
  }).listen(0, '127.0.0.1');
  await new Promise(r => server.once('listening', r));
  base = 'http://127.0.0.1:' + server.address().port;
}

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(base + '/?preview=asesoria#asesoria', { waitUntil: 'networkidle', timeout: 120000 });
const out = await page.evaluate(async () => {
  const w = mfGetWindows().find(x => x.key === 'ytd');
  const m = await mfBuildPerformanceSeries(w.portfolioDays, w.benchDays, w.granularity);
  if (!m || m.dataUnavailable) return null;
  const rows = [];
  for (let i = 0; i < m.dates.length; i++) {
    if (m.portfolioPct[i] == null || m.benchPct[i] == null || !(m.dates[i] instanceof Date)) continue;
    rows.push({ d: m.dates[i], m: m.portfolioPct[i], s: m.benchPct[i] });
  }
  if (rows.length < 5) return null;
  const s0 = 1 + rows[0].s / 100, m0 = 1 + rows[0].m / 100;
  const iso = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  return rows.map(r => [iso(r.d), +((1 + r.m / 100) / m0 * 100 - 100).toFixed(3), +((1 + r.s / 100) / s0 * 100 - 100).toFixed(3)]);
});
// el parámetro de vista previa queda en localStorage: se borra al terminar
await page.evaluate(() => localStorage.removeItem('mf_asesoria_preview'));
await browser.close();
server?.close();

if (!out) { console.error('No se pudieron leer los datos de la cartera.'); process.exit(1); }
const last = out[out.length - 1];
await writeFile(join(HERE, 'data.json'), JSON.stringify({ source: base, from: out[0][0], asOf: last[0], mine: last[1], spx: last[2], rows: out }, null, 1) + '\n');
console.log(`Desde ${out[0][0]} hasta ${last[0]}: cartera ${last[1].toFixed(1)} % · S&P 500 ${last[2].toFixed(1)} %`);
