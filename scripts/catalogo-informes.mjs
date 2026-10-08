// Arma informes/catalogo.json con los datos de cada informe de empresa
// (trimestre de los datos, secciones, gráficos, tablas, palabras, las cifras
// de la tapa, el primer título como tesis y la fecha de publicación) para la
// estantería de la pestaña Informes (assets/informes/estanteria.js).
// Corre en el workflow diario; también se puede correr a mano:
//   node scripts/catalogo-informes.mjs
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const DIR = 'informes';
const ent = (s) => String(s || '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
  .replace(/&ndash;/g, '–').replace(/&mdash;/g, '—').replace(/&minus;/g, '−').replace(/&middot;/g, '·')
  .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n));
const txt = (s) => ent(String(s || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const uno = (s, re) => { const m = s.match(re); return m ? m[1] : ''; };

// fecha de publicación: la más reciente del manifest; si no está, el primer commit del archivo
const fechas = {};
try {
  for (const x of JSON.parse(fs.readFileSync(path.join(DIR, 'manifest.json'), 'utf8'))) {
    if (x.ticker && x.publishedAt && (!fechas[x.ticker] || x.publishedAt > fechas[x.ticker])) fechas[x.ticker] = x.publishedAt;
  }
} catch (e) { /* sin manifest */ }
function fechaGit(f) {
  try { return execSync(`git log --diff-filter=A --follow --format=%cs -- "${f}"`, { encoding: 'utf8' }).trim().split('\n').pop() || ''; }
  catch (e) { return ''; }
}

const out = {};
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith('.html')).sort()) {
  const s = fs.readFileSync(path.join(DIR, f), 'utf8');
  if (!s.includes('class="ticker-big"') || !s.includes('class="frontbox"')) continue; // solo informes de empresa
  const t = txt(uno(s, /class="ticker-big">([^<]+)</)).toUpperCase();
  if (!t) continue;
  const cuerpo = txt(s.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ' '));
  const datos = txt(uno(s, /class="doctype">([\s\S]*?)<\/div>/));
  const q = uno(datos, /Datos (?:al|a) ([^(]+?)\s*\(/) || uno(datos, /Datos (?:al|a) (.+)$/);
  const stats = [...s.matchAll(/class="k">([\s\S]*?)<\/div>\s*<div class="v[^"]*">([\s\S]*?)<\/div>/g)].slice(0, 4).map((m) => [txt(m[1]), txt(m[2])]);
  out[t] = {
    q: q.trim(),
    secs: (s.match(/class="secnum"/g) || []).length,
    ch: (s.match(/class="chartbox"/g) || []).length,
    tb: (s.match(/<table/g) || []).length,
    w: cuerpo.split(' ').length,
    stats,
    tesis: txt(uno(s, /<h2[^>]*>([\s\S]*?)<\/h2>/)),
    f: fechas[t] || fechaGit(path.join(DIR, f)),
    href: `${DIR}/${f}`
  };
}
fs.writeFileSync(path.join(DIR, 'catalogo.json'), JSON.stringify(out, null, 1) + '\n');
console.log(`catalogo.json: ${Object.keys(out).length} informes`);
