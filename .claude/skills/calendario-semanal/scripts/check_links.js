#!/usr/bin/env node
// Comprueba que cada evento de una semana del calendario resuelva a un link de fuente,
// usando la MISMA tabla que el sitio (CAL_SOURCES + calSourceFor en index.html).
//
// Uso:  node check_links.js <ruta/index.html> <ruta/semana.json> [--soft]
//   Sale con codigo 1 si algun evento queda sin link (salvo con --soft).
// Sirve tambien para probar contra la semana en vivo y detectar regresiones:
//   curl -s https://manfredi-calendario.nachito2502.workers.dev/calendario -o vivo.json
//   node check_links.js index.html vivo.json

const fs = require('fs');

const [, , htmlPath, jsonPath, flag] = process.argv;
if (!htmlPath || !jsonPath) {
  console.error('Uso: node check_links.js <index.html> <semana.json> [--soft]');
  process.exit(2);
}

const html = fs.readFileSync(htmlPath, 'utf8');
const i = html.indexOf('var CAL_SOURCES = [');
const j = html.indexOf('var HTX_CAL_MESES');
if (i < 0 || j < 0 || j < i) {
  console.error('No encontre CAL_SOURCES / HTX_CAL_MESES en ' + htmlPath +
    '. Se movio o renombro la tabla? Revisar index.html.');
  process.exit(2);
}

// Evalua solo el fragmento de la tabla, aislado del resto de la pagina.
const ctx = {};
new Function(html.slice(i, j) + '\nthis.calSourceFor = calSourceFor;').call(ctx);

let semana;
try {
  semana = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
} catch (e) {
  console.error('El JSON de la semana no parsea: ' + e.message);
  process.exit(2);
}

const GENERICO = /Calendario-Fecha-0|Principales_variables/; // paginas generales, no especificas
let total = 0, sinLink = [], genericos = [];

for (const dia of semana.dias || []) {
  console.log('## ' + dia.nombre + ' ' + dia.fecha + (dia.eventos.length ? '' : '  (sin eventos)'));
  for (const ev of dia.eventos) {
    total++;
    const s = ctx.calSourceFor(ev);
    const destino = s ? (s.fuente.padEnd(12) + s.url.replace(/^https?:\/\/(www\.)?/, '')) : 'SIN LINK';
    console.log('  ' + destino.slice(0, 92).padEnd(94) + '| ' + ev.titulo.slice(0, 60));
    if (!s) sinLink.push(ev.titulo);
    else if (GENERICO.test(s.url)) genericos.push(ev.titulo);
  }
}

console.log('\nEventos: ' + total + ' | sin link: ' + sinLink.length +
  ' | con link a pagina general (mejorable): ' + genericos.length);
if (sinLink.length) console.log('SIN LINK:\n  - ' + sinLink.join('\n  - '));
if (genericos.length) console.log('Pagina general (considerar una regla mas especifica):\n  - ' + genericos.join('\n  - '));
process.exit(sinLink.length && flag !== '--soft' ? 1 : 0);
