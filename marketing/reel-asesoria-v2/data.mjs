// Saca los datos reales del sitio con la misma cuenta que la pestaña Portfolio
// (asesoria.js → getData + drawHold). Guarda data/cartera.json.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const PORT = 8820;

const srv = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
try {
  const page = await browser.newPage();
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text().slice(0, 200)); });
  await page.goto(`http://127.0.0.1:${PORT}/?preview=asesoria#asesoria`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForFunction(() => typeof mfBuildPerformanceSeries === 'function' && typeof mfGetWindows === 'function', null, { timeout: 30000 });
  const out = await page.evaluate(async () => {
    // getData (asesoria.js)
    const w = mfGetWindows().filter(x => x.key === 'ytd')[0];
    const m = await mfBuildPerformanceSeries(w.portfolioDays, w.benchDays, w.granularity);
    if (!m || m.dataUnavailable) return { error: 'dataUnavailable' };
    const rows = [];
    for (let i = 0; i < m.dates.length; i++) {
      if (m.benchPct[i] == null || !(m.dates[i] instanceof Date)) continue;
      rows.push({ d: m.dates[i], s: m.benchPct[i], m: m.portfolioPct[i] == null ? null : m.portfolioPct[i] });
    }
    const k = rows.findIndex(r => r.m != null);
    if (rows.length < 5 || k < 0) return { error: 'serie vacía' };
    // drawHold (asesoria.js)
    const NOMBRES = { MSFT: 'Microsoft', META: 'Meta Platforms', MELI: 'MercadoLibre', IBIT: 'iShares Bitcoin Trust (BlackRock)', NU: 'Nu Holdings (Nubank)',
      XOM: 'ExxonMobil', LLY: 'Eli Lilly', PEP: 'PepsiCo', AMZN: 'Amazon', AIG: 'American International Group', PAMP: 'Pampa Energía', GGAL: 'Grupo Financiero Galicia' };
    const LOGOS = { MSFT: 1, META: 1, MELI: 1, LLY: 1, PEP: 1, AMZN: 1, GGAL: 1 };
    const dates = m.dates, ops = typeof MF_OPERACIONES !== 'undefined' ? MF_OPERACIONES : [];
    const inc = typeof MF_INCEPTION_DATE !== 'undefined' ? MF_INCEPTION_DATE : rows[k].d;
    const closeAt = (c, d) => { let j = dates.findIndex(x => x >= d); if (j < 0) j = dates.length - 1; const v = c[c.length - (dates.length - j)]; return v == null ? null : v; };
    const pos = [];
    MF_HOLDINGS.forEach(h => {
      const c = m.closesByTicker && m.closesByTicker[h.ticker];
      if (!c || !c.length) return;
      const last = c[c.length - 1], lots = []; let later = 0;
      ops.forEach(o => { if (o.ticker === h.ticker) { lots.push({ q: o.cantidad, d: new Date(o.fecha + 'T00:00:00') }); later += o.cantidad; } });
      if (h.cantidad - later > 0) lots.push({ q: h.cantidad - later, d: inc });
      let cost = 0, ok = true;
      lots.forEach(l => { const p = closeAt(c, l.d); if (p == null) ok = false; else cost += l.q * p; });
      pos.push({ t: h.ticker, val: h.cantidad * last, ret: ok && cost ? (h.cantidad * last / cost - 1) * 100 : null });
    });
    pos.sort((a, b) => b.val - a.val); // = orden por peso
    const top = pos.filter(p => LOGOS[p.t] && p.ret != null).slice(0, 3).map(p => ({ ticker: p.t, nombre: NOMBRES[p.t] || p.t, logo: 'assets/logos/' + p.t.toLowerCase() + '.png', ret: +p.ret.toFixed(4) }));
    const iso = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    const serie = rows.slice(k).map(r => ({ fecha: iso(r.d), cartera: +r.m.toFixed(4), sp500: +(r.s - rows[k].s).toFixed(4) }));
    // S&P desde el 22-may: rebasado a la misma fecha de inicio de la cartera
    const last = rows[rows.length - 1];
    const spxReal = ((1 + last.s / 100) / (1 + rows[k].s / 100) - 1) * 100;
    serie.forEach((p, i) => { const r = rows[k + i]; p.sp500 = +(((1 + r.s / 100) / (1 + rows[k].s / 100) - 1) * 100).toFixed(4); });
    return {
      corte: iso(last.d), inicio: iso(rows[k].d),
      real: { cartera: +last.m.toFixed(4), sp500: +spxReal.toFixed(4) },
      ytd: { carteraProyectado: +m.totalReturn.toFixed(4), sp500: +last.s.toFixed(4) },
      activos: top, totalPosiciones: pos.length, masPosiciones: pos.length - top.length,
      serie
    };
  });
  if (out.error) { console.error('FALLÓ:', out.error); process.exitCode = 1; }
  else {
    writeFileSync(path.join(HERE, 'data/cartera.json'), JSON.stringify({ fuente: 'manfredinvestment.com · misma cuenta que Portfolio (mfBuildPerformanceSeries, ventana ytd)', ...out }, null, 2));
    const { serie, ...resumen } = out; console.log(JSON.stringify(resumen, null, 2), 'puntos:', serie.length);
  }
} finally { await browser.close(); srv.kill(); }
