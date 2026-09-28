#!/usr/bin/env node
// Valida los tres JSON de la semana antes de cargarlos en el KV del worker.
//
// Uso:
//   node validar_semana.js <semana.json> <earnings.json> <dividendos.json> [carpeta-informes]
//
// Comprueba, y sale con codigo 1 si algo falla:
//  - los tres parsean, tienen fuente "Manual" y los mismos 5 dias (Lunes..Viernes, mismas fechas);
//  - la semana del economico usa el formato "d/m al d/m de aaaa";
//  - tipos: economico solo "ar"/"us"; earnings solo "earnings"; dividendos solo "dividend";
//  - earnings y dividendos: cada evento tiene ticker en minuscula y existe informes/<ticker>.html
//    (el sitio lo linkea ahi); titulo y descripcion no vacios; sin eventos repetidos.
const fs = require('fs');
const path = require('path');

const [, , fCal, fEarn, fDiv, dirInf = 'informes'] = process.argv;
if (!fCal || !fEarn || !fDiv) {
  console.error('Uso: node validar_semana.js <semana.json> <earnings.json> <dividendos.json> [carpeta-informes]');
  process.exit(2);
}

const errores = [];
const leer = (f) => {
  try { return JSON.parse(fs.readFileSync(f, 'utf8')); }
  catch (e) { errores.push(`${f}: no parsea (${e.message})`); return null; }
};
const cal = leer(fCal), earn = leer(fEarn), div = leer(fDiv);
if (errores.length) { errores.forEach((e) => console.error('ERROR ' + e)); process.exit(1); }

const NOMBRES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
const cfg = [
  ['economico', cal, ['ar', 'us'], false],
  ['earnings', earn, ['earnings'], true],
  ['dividendos', div, ['dividend'], true],
];

if (!/^\d{1,2}\/\d{1,2} al \d{1,2}\/\d{1,2} de \d{4}$/.test(cal.semana || '')) {
  errores.push(`economico: "semana" con formato raro: ${JSON.stringify(cal.semana)}`);
}
const fechasRef = (cal.dias || []).map((d) => d.fecha);

for (const [nombre, j, tipos, conTicker] of cfg) {
  if (j.fuente !== 'Manual') errores.push(`${nombre}: fuente debe ser "Manual" (es ${JSON.stringify(j.fuente)})`);
  if (j.semana !== cal.semana) errores.push(`${nombre}: semana ${JSON.stringify(j.semana)} distinta de la del economico ${JSON.stringify(cal.semana)}`);
  if (!Array.isArray(j.dias) || j.dias.length !== 5) { errores.push(`${nombre}: tiene que tener 5 dias`); continue; }
  const vistos = new Set();
  j.dias.forEach((d, i) => {
    if (d.nombre !== NOMBRES[i]) errores.push(`${nombre}: dia ${i + 1} se llama ${JSON.stringify(d.nombre)}, esperaba ${NOMBRES[i]}`);
    if (d.fecha !== fechasRef[i]) errores.push(`${nombre}: ${d.nombre} con fecha ${d.fecha}, el economico dice ${fechasRef[i]}`);
    if (!/^\d{1,2}\/\d{1,2}$/.test(d.fecha || '')) errores.push(`${nombre}: fecha ${JSON.stringify(d.fecha)} no es d/m`);
    for (const ev of d.eventos || []) {
      const id = `${nombre} ${d.fecha} "${(ev.titulo || '').slice(0, 50)}"`;
      if (!tipos.includes(ev.tipo)) errores.push(`${id}: tipo ${JSON.stringify(ev.tipo)} (validos: ${tipos.join(', ')})`);
      if (!ev.titulo || !ev.descripcion) errores.push(`${id}: falta titulo o descripcion`);
      const clave = ev.titulo + '|' + (ev.ticker || '');
      if (vistos.has(clave)) errores.push(`${id}: repetido`);
      vistos.add(clave);
      if (conTicker) {
        if (!ev.ticker || ev.ticker !== ev.ticker.toLowerCase()) errores.push(`${id}: ticker ausente o no esta en minuscula`);
        else if (!fs.existsSync(path.join(dirInf, ev.ticker + '.html'))) errores.push(`${id}: no existe ${path.join(dirInf, ev.ticker + '.html')}`);
      } else if (ev.ticker) {
        errores.push(`${id}: el economico no lleva ticker`);
      }
    }
  });
  const n = j.dias.reduce((a, d) => a + (d.eventos || []).length, 0);
  console.log(`${nombre.padEnd(11)} ${j.semana} | ${n} eventos | ${j.dias.map((d) => d.fecha + ':' + (d.eventos || []).length).join(' ')}`);
}

if (errores.length) {
  errores.forEach((e) => console.error('ERROR ' + e));
  process.exit(1);
}
console.log('OK: los tres JSON son validos y coinciden en la semana.');
