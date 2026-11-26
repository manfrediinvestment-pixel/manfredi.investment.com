/*
 * manfredi-indec
 * Datos oficiales del INDEC para la sub-pestaña "Argentina en datos" (Noticias).
 *
 * Fuentes:
 *  1. Catálogo API-INDEC (api.indec.gob.ar/v1, beta desde nov-2026). Pide un JWT
 *     (secreto INDEC_TOKEN) que NUNCA puede llegar al navegador: por eso este worker.
 *     Estilo PostgREST, máx. 1000 filas por pedido, 429 si se abusa → todo se cachea.
 *  2. Calendario de difusión del INDEC (indec.gob.ar/Calendario/FiltrosCalendario/mes/...):
 *     fragmento HTML sin CORS, se parsea acá.
 *  3. apis.datos.gob.ar/series: para lo que el catálogo todavía no tiene (PBI trimestral)
 *     y para el buscador del Explorador. Rechaza clientes sin User-Agent de navegador.
 *
 * Caché: Cache API de Cloudflare (no KV: el cupo de 1.000 escrituras/día ya se agotó una vez).
 */

const INDEC_API = 'https://api.indec.gob.ar/v1/';
const INDEC_WEB = 'https://www.indec.gob.ar';
const SERIES_API = 'https://apis.datos.gob.ar/series/api/';
const UA = 'Mozilla/5.0 (compatible; ManfrediDatos/1.0)';

// Servicios del catálogo que se pueden consultar a través del worker.
const DATASETS = {
  ipc_nacional: 'clasificador,nivel,codigo,descripcion,periodo,anio,mes,indicador,tipo_de_indicador,tipo_de_indicador_descripcion,region,unidad_de_medida',
  valorizacion_canastas_cba_cbt: 'clasificador,nivel,codigo,descripcion,periodo,anio,mes,indicador,tipo_de_indicador,tipo_de_indicador_descripcion,region,unidad_de_medida',
  indice_salarios: 'clasificador,nivel,codigo,descripcion,periodo,anio,mes,indicador,tipo_de_indicador,tipo_de_indicador_descripcion,unidad_de_medida',
  icc_precios_construccion: 'indicador,codigo_apertura,codigo_CPC_1,clasificador,nivel,descripcion,periodo,anio,mes,tipo_de_indicador,tipo_de_indicador_descripcion,region,unidad_de_medida',
  sipm_precios_mayoristas: 'operativo,indicador,clasificador,nivel,codigo_apertura,descripcion,periodo,anio,mes,tipo_de_indicador,tipo_de_indicador_descripcion,region,unidad_de_medida',
  'estimador-mensual-de-actividad-economica-nivel-general': 'tipo_de_indicador_descripcion,anio,mes,periodo,tipo_de_indicador',
  'estimador-mensual-de-actividad-economica-sectores': 'anio,mes,codigo,descripcion,periodo,tipo_de_indicador',
  pobreza_eph: 'area_geografica_cod,periodo',
  mercado_trabajo_eph: 'area_geografica_cod,periodo',
  'canasta-crianza': 'Periodo',
  ipi_manufacturero: 'periodo,indicador,codigo_CLaNAE_2004,serie,tipo_de_indicador',
  ipi_minero: 'periodo,indicador,codigo_ClaNAE_2010,codigo_CPC_2_1,serie,tipo_de_indicador',
  comercio_exterior_nomenclaturas: 'nombre_columna,codigo',
  comercio_exterior_exportacion_bienes: 'Anio,Mes,Periodo,rubro_cod,subrubro_cod,pais_cod',
  comercio_exterior_importacion_bienes: 'Anio,Mes,Periodo,uso_economico_cod,gce_cod,pais_cod',
  proyecciones_poblacion_nacional_2022_2040: 'edad,sexo_cod,fecha',
  proyecciones_poblacion_jurisdiccion_2022_2040: 'jurisdiccion_cod,sexo_cod,edad_cod,fecha',
};

const TTL = { datos: 6 * 3600, calendario: 6 * 3600, series: 6 * 3600, buscar: 24 * 3600, tablero: 3 * 3600 };
const MAX_PAGINAS = 30; // 30.000 filas como techo para ?todo=1

const ORIGENES = [/^https:\/\/(www\.)?manfredinvestment\.com$/, /^https:\/\/[a-z0-9-]+\.manfredi[a-z0-9-]*\.pages\.dev$/, /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/];

function cors(req) {
  const o = req.headers.get('Origin') || '';
  return {
    'Access-Control-Allow-Origin': ORIGENES.some(r => r.test(o)) ? o : 'https://manfredinvestment.com',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    Vary: 'Origin',
  };
}
function json(req, data, status = 200, maxAge = 300) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=' + maxAge, ...cors(req) },
  });
}

// Cache API: guarda la respuesta JSON ya procesada bajo una URL sintética.
async function cacheado(ctx, clave, ttl, producir) {
  const cache = caches.default;
  const key = new Request('https://cache.manfredi-indec/' + encodeURIComponent(clave));
  const hit = await cache.match(key);
  if (hit) return { data: await hit.json(), cache: 'hit' };
  const data = await producir();
  ctx.waitUntil(cache.put(key, new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=' + ttl },
  })));
  return { data, cache: 'miss' };
}

/* ───────────────────────── Catálogo API-INDEC ───────────────────────── */

async function indecFetch(env, dataset, params) {
  if (!env.INDEC_TOKEN) throw new Error('Falta el secreto INDEC_TOKEN');
  const url = INDEC_API + dataset + '?' + params.toString();
  const r = await fetch(url, {
    headers: { Authorization: 'Bearer ' + env.INDEC_TOKEN, Accept: 'application/json', 'User-Agent': UA, Prefer: 'count=exact' },
    cf: { cacheTtl: 0 },
  });
  if (!r.ok && r.status !== 206) {
    const txt = (await r.text()).slice(0, 300);
    const e = new Error('INDEC ' + r.status + ': ' + txt); e.status = r.status; throw e;
  }
  const total = Number(((r.headers.get('Content-Range') || '').split('/')[1]) || NaN);
  return { filas: await r.json(), total: Number.isFinite(total) ? total : null };
}

// Pide todas las páginas (limit 1000) ordenando por la clave completa, como pide la doc.
async function indecTodo(env, dataset, params) {
  const p = new URLSearchParams(params);
  if (!p.get('order')) p.set('order', DATASETS[dataset]);
  p.set('limit', '1000');
  let offset = 0, filas = [], total = null;
  for (let i = 0; i < MAX_PAGINAS; i++) {
    p.set('offset', String(offset));
    const r = await indecFetch(env, dataset, p);
    filas = filas.concat(r.filas); total = r.total;
    if (r.filas.length < 1000 || (total != null && filas.length >= total)) break;
    offset += 1000;
  }
  return { filas, total };
}

function limpiarParams(sp) {
  const p = new URLSearchParams();
  for (const [k, v] of sp) {
    if (k === 'todo' || k === 'nocache') continue;
    if (!/^[A-Za-z0-9_]+$/.test(k) || v.length > 400) continue;
    p.append(k, v);
  }
  if (!p.get('limit')) p.set('limit', '1000');
  return p;
}

/* ───────────────────────── Calendario de difusión ───────────────────────── */

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

function desHtml(s) {
  return s.replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)))
    .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

// Agrupa cada publicación en un tema del sitio (sirve para filtrar y para el ícono).
// Ojo: las siglas (ICA, IPC, EMAE…) se buscan con \b y distinguiendo mayúsculas:
// con /i "ica" aparece en "estadísticas", "farmacéutica", "pública".
const TEMAS = [
  ['precios', [/\b(IPC|ICC|SIPM|CBA|CBT)\b/, /precios|canasta|costo de la construcci/i]],
  ['externo', [/\b(ICA)\b/, /comercio exterior|intercambio comercial|exportaci|importaci|balanza de pagos|deuda externa|posici[oó]n de inversi|t[eé]rminos del intercambio/i]],
  ['trabajo', [/\b(EPH)\b/, /salarios|mercado de trabajo|empleo|desocupaci|pobreza|indigencia|distribuci[oó]n del ingreso|dotaci[oó]n de personal/i]],
  ['actividad', [/\b(EMAE|PIB|IPI|ISSP|UCII|EPI)\b/, /actividad|producto interno|industria|construcci|capacidad instalada|servicios p[uú]blicos|supermercados|autoservicios|centros de compras|turismo|hotelera|energ[eé]tic|tendencia de negocios|cuentas nacionales|capital fijo/i]],
];
// Se aplica DESPUÉS de la caché: cambiar las reglas no obliga a esperar 6 h.
function clasificar(e) { return { ...e, tema: tema(e.titulo), clave: CLAVE.test(e.titulo) }; }
function tema(t) { for (const [k, res] of TEMAS) if (res.some(re => re.test(t))) return k; return 'otros'; }
// Las que mueven al mercado: se destacan en la grilla.
const CLAVE = /IPC\)|Índice de precios al consumidor|canasta b[aá]sica alimentaria|Estimador mensual de actividad|Informe de avance del nivel de actividad|Índice de salarios|Intercambio comercial argentino|Mercado de trabajo. Tasas|Incidencia de la pobreza|Balanza de pagos/i;

async function calendarioMes(anio, mes) {
  const url = `${INDEC_WEB}/Calendario/FiltrosCalendario/mes/${MESES[mes - 1]}-${anio}/1`;
  const r = await fetch(url, { headers: { 'User-Agent': UA }, cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error('INDEC calendario ' + r.status);
  const html = await r.text();
  const tok = /class="nro-dia">\s*(\d{1,2})\s*<|class="cal-content text-calendario(?: text-center)?">\s*([\s\S]*?)\s*<\/div>/g;
  const eventos = [];
  let dia = null, m;
  while ((m = tok.exec(html))) {
    if (m[1]) { dia = +m[1]; continue; }
    const txt = desHtml(m[2]);
    if (!txt || dia == null) continue;
    const hora = txt.match(/^(\d{1,2}):(\d{2})\s*hs$/i);
    if (hora) { const ult = eventos[eventos.length - 1]; if (ult && !ult.hora) ult.hora = hora[1].padStart(2, '0') + ':' + hora[2]; continue; }
    eventos.push({
      fecha: `${anio}-${String(mes).padStart(2, '0')}-${String(dia).padStart(2, '0')}`,
      hora: null, titulo: txt,
    });
  }
  return { mes: `${anio}-${String(mes).padStart(2, '0')}`, fuente: url, eventos };
}

/* ───────────────────────── datos.gob.ar series ───────────────────────── */

async function seriesFetch(path, sp) {
  const r = await fetch(SERIES_API + path + '?' + sp.toString(), { headers: { 'User-Agent': UA, Accept: 'application/json' } });
  if (!r.ok) throw new Error('series ' + r.status);
  return r.json();
}

/* ───────────────────────── tablero (todo lo de la primera vista) ─────────────────────────
 * Un solo JSON chico, armado acá y cacheado 3 h, para que la página haga UN pedido.
 * Ojo con los datos del catálogo (beta): las descripciones cambian de mayúsculas y de
 * plural entre filas ("NIVEL GENERAL"/"Nivel general", "Estacional"/"Estacionales"), así
 * que se filtra SIEMPRE por código. Las incidencias del IPC solo vienen por región.
 */

const per = s => s.slice(0, 4) + '-' + s.slice(4, 6);           // '202610' → '2026-10'
const r1 = v => (v == null || !Number.isFinite(+v) ? null : Math.round(+v * 10) / 10);
const r2 = v => (v == null || !Number.isFinite(+v) ? null : Math.round(+v * 100) / 100);
async function filas(env, ds, obj) { return (await indecTodo(env, ds, new URLSearchParams(obj))).filas; }
async function agregado(env, ds, obj) { return (await indecFetch(env, ds, new URLSearchParams({ limit: '1000', ...obj }))).filas; }
function porPeriodo(rows, key = 'periodo') {
  const m = new Map();
  for (const x of rows) { const p = x[key]; if (!m.has(p)) m.set(p, { p: per(p) }); }
  return m;
}
const ordenar = m => [...m.values()].sort((a, b) => (a.p < b.p ? -1 : 1));

async function secIPC(env) {
  const rows = await filas(env, 'ipc_nacional', { region: 'eq.Nacional', codigo: 'in.(0,N,R,E,B,S)', tipo_de_indicador: 'in.(v_m,v_ia,Indice)' });
  const m = porPeriodo(rows);
  const K = { '0': '', N: 'n', R: 'r', E: 'e', B: 'b', S: 's' };
  for (const x of rows) {
    const o = m.get(x.periodo), k = K[x.codigo]; if (k == null) continue;
    const campo = x.tipo_de_indicador === 'Indice' ? 'idx' : x.tipo_de_indicador === 'v_m' ? 'm' : 'ia';
    o[(k ? k + '_' : '') + campo] = campo === 'idx' ? r2(x.valor) : r1(x.valor);
  }
  const serie = ordenar(m).filter(o => o.idx != null);
  const ult = [...serie].reverse().find(o => o.m != null);
  const lat = ult.p.replace('-', '');
  const [acum, reg, rub] = await Promise.all([
    filas(env, 'ipc_nacional', { periodo: 'eq.' + lat, region: 'eq.Nacional', codigo: 'eq.0', tipo_de_indicador: 'eq.v_acum' }),
    filas(env, 'ipc_nacional', { periodo: 'eq.' + lat, codigo: 'eq.0', tipo_de_indicador: 'in.(v_m,v_ia)' }),
    filas(env, 'ipc_nacional', { periodo: 'eq.' + lat, region: 'eq.Nacional', nivel: 'eq.División', tipo_de_indicador: 'in.(v_m,v_ia)' }),
  ]);
  const regiones = {}; for (const x of reg) { (regiones[x.region] ||= { region: x.region })[x.tipo_de_indicador === 'v_m' ? 'm' : 'ia'] = r1(x.valor); }
  const rubros = {}; for (const x of rub) { (rubros[x.codigo] ||= { codigo: x.codigo, nombre: x.descripcion })[x.tipo_de_indicador === 'v_m' ? 'm' : 'ia'] = r1(x.valor); }
  return {
    ultimo: { ...ult, acum: acum[0] ? r1(acum[0].valor) : null },
    serie,
    regiones: Object.values(regiones).sort((a, b) => (a.region === 'Nacional' ? -1 : b.region === 'Nacional' ? 1 : (b.m ?? 0) - (a.m ?? 0))),
    rubros: Object.values(rubros).sort((a, b) => (b.m ?? 0) - (a.m ?? 0)),
  };
}

async function secCanasta(env) {
  const rows = await filas(env, 'valorizacion_canastas_cba_cbt', { anio: 'gte.2016' });
  const m = porPeriodo(rows);
  for (const x of rows) {
    const o = m.get(x.periodo), c = x.codigo, t = x.tipo_de_indicador;
    if ((c === 'CBA' || c === 'CBT') && t === c) o[c.toLowerCase()] = r2(x.valor);
    else if ((c === 'CBA' || c === 'CBT') && (t === 'v_m' || t === 'v_ia')) o[c.toLowerCase() + '_' + t.slice(2)] = r1(x.valor);
    else if (c === 'CBT H2') o.cbt_h2 = Math.round(x.valor);
    else if (c === 'CBA H2') o.cba_h2 = Math.round(x.valor);
  }
  const serie = ordenar(m).filter(o => o.cbt != null);
  return { ultimo: serie[serie.length - 1], serie, region: 'GBA', nota: 'Hogar 2: dos adultos de 35 y 31 años con dos hijos de 6 y 8 (la "familia tipo" del INDEC).' };
}

async function secSalarios(env, ipcSerie) {
  const rows = await filas(env, 'indice_salarios', { codigo: 'in.(0,110,120,200)', tipo_de_indicador: 'in.(Indice,v_m,v_ia)' });
  const m = porPeriodo(rows);
  const K = { '0': 'tot', '110': 'priv', '120': 'pub', '200': 'noreg' };
  for (const x of rows) {
    const o = m.get(x.periodo), k = K[x.codigo]; if (!k) continue;
    const t = x.tipo_de_indicador;
    o[k + (t === 'Indice' ? '' : t === 'v_m' ? '_m' : '_ia')] = t === 'Indice' ? r2(x.valor) : r1(x.valor);
  }
  const serie = ordenar(m).filter(o => o.tot != null || o.priv != null);
  // Salario real = índice de salarios / IPC nacional, base 100 en el primer mes con ambos.
  const ipc = new Map(ipcSerie.map(o => [o.p, o.idx]));
  const base = {};
  const real = [];
  for (const o of serie) {
    const pi = ipc.get(o.p); if (!pi) continue;
    const r = { p: o.p };
    for (const k of ['tot', 'priv', 'pub', 'noreg']) {
      if (o[k] == null) continue;
      const v = o[k] / pi;
      if (base[k] == null) base[k] = v;
      r[k] = r1((v / base[k]) * 100);
    }
    real.push(r);
  }
  const conIa = (lista, k) => {
    const idx = new Map(lista.map(o => [o.p, o[k]]));
    const u = [...lista].reverse().find(o => o[k] != null); if (!u) return null;
    const [a, mm] = u.p.split('-').map(Number), atras = `${a - 1}-${String(mm).padStart(2, '0')}`;
    const prev = idx.get(atras); return prev ? { p: u.p, ia: r1((u[k] / prev - 1) * 100) } : null;
  };
  return {
    ultimo: { ...serie[serie.length - 1], real_tot: conIa(real, 'tot'), real_priv: conIa(real, 'priv'), real_pub: conIa(real, 'pub') },
    serie, real,
  };
}

async function secEMAE(env) {
  const rows = await filas(env, 'estimador-mensual-de-actividad-economica-nivel-general', { anio: 'gte.2016' });
  const m = porPeriodo(rows);
  for (const x of rows) {
    const o = m.get(x.periodo), d = (x.tipo_de_indicador_descripcion || '').toLowerCase();
    if (d.includes('interanual')) o.ia = r1(x.valor);
    else if (d.includes('mensual') && d.includes('desest')) o.m = r1(x.valor);
    else if (d.includes('ndice') && d.includes('desest')) o.desest = r1(x.valor);
    else if (d.includes('ndice') && d.includes('original')) o.orig = r1(x.valor);
    else if (d.includes('ndice') && d.includes('tendencia')) o.tc = r1(x.valor);
  }
  const serie = ordenar(m).filter(o => o.desest != null || o.orig != null);
  const ult = serie[serie.length - 1];
  // Máximo histórico de la serie desestacionalizada: "¿estamos en récord?"
  const max = serie.reduce((a, o) => (o.desest != null && (!a || o.desest > a.desest) ? o : a), null);
  const sec = await filas(env, 'estimador-mensual-de-actividad-economica-sectores', { periodo: 'eq.' + ult.p.replace('-', ''), tipo_de_indicador: 'ilike.*interanual*' });
  return {
    ultimo: { ...ult, maximo: max && { p: max.p, desest: max.desest } },
    serie,
    sectores: sec.map(x => ({ codigo: x.codigo, nombre: x.descripcion, ia: r1(x.valor) })).filter(x => x.ia != null).sort((a, b) => b.ia - a.ia),
  };
}

const trim = p => (p.length === 6 ? p.slice(4, 5) + (p[5] === 'T' ? 'T ' : 'S ') + p.slice(0, 4) : p); // '20262T' → '2T 2026'
async function secTrabajo(env) {
  const rows = await filas(env, 'mercado_trabajo_eph', {});
  const serie = rows.filter(x => x.tasa_de_desocupacion != null)
    .map(x => ({ p: x.anio + '-T' + x.trimestre, label: trim(x.periodo), desoc: r1(x.tasa_de_desocupacion), act: r1(x.tasa_de_actividad), emp: r1(x.tasa_de_empleo), informal: x.tasa_de_empleo && x.tasa_de_empleo_informal != null ? r1((x.tasa_de_empleo_informal / x.tasa_de_empleo) * 100) : null, subocup: r1(x.tasa_de_subocupacion), prov: !!x.observaciones }))
    .sort((a, b) => (a.p < b.p ? -1 : 1));
  return { ultimo: serie[serie.length - 1], serie, area: '31 aglomerados urbanos (EPH)' };
}

async function secPobreza(env) {
  const rows = await filas(env, 'pobreza_eph', {});
  const serie = rows.filter(x => x.tasa_pobreza_personas != null)
    .map(x => ({ p: x.anio + '-S' + x.semestre, label: trim(x.periodo), pers: r1(x.tasa_pobreza_personas), hog: r1(x.tasa_pobreza_hogares), indig: r1(x.tasa_indigencia_personas), prov: !!x.observaciones }))
    .sort((a, b) => (a.p < b.p ? -1 : 1));
  return { ultimo: serie[serie.length - 1], serie, area: '31 aglomerados urbanos (EPH)' };
}

async function secComex(env) {
  const [x, m] = await Promise.all([
    agregado(env, 'comercio_exterior_exportacion_bienes', { select: 'Periodo,valor_FOB.sum()', Anio: 'gte.2017' }),
    agregado(env, 'comercio_exterior_importacion_bienes', { select: 'Periodo,valor_CIF.sum()', Anio: 'gte.2017' }),
  ]);
  const mp = new Map();
  for (const r of x) (mp.get(r.Periodo) || mp.set(r.Periodo, { p: per(r.Periodo) }).get(r.Periodo)).x = Math.round(r.sum / 1e6);
  for (const r of m) (mp.get(r.Periodo) || mp.set(r.Periodo, { p: per(r.Periodo) }).get(r.Periodo)).m = Math.round(r.sum / 1e6);
  const serie = ordenar(mp).filter(o => o.x != null && o.m != null).map(o => ({ ...o, saldo: o.x - o.m }));
  const ult = serie[serie.length - 1];
  const ult12 = serie.slice(-12), sum = k => ult12.reduce((a, o) => a + o[k], 0);
  const lat = ult.p.replace('-', '');
  const [rub, pais, nom] = await Promise.all([
    agregado(env, 'comercio_exterior_exportacion_bienes', { select: 'rubro_cod,valor_FOB.sum()', Periodo: 'eq.' + lat }),
    agregado(env, 'comercio_exterior_exportacion_bienes', { select: 'pais_cod,valor_FOB.sum()', Periodo: 'eq.' + lat }),
    agregado(env, 'comercio_exterior_nomenclaturas', { nombre_columna: 'in.(rubro_cod,pais_cod)' }),
  ]);
  const nombre = {}; for (const n of nom) nombre[n.nombre_columna + ':' + n.codigo] = n.codigo_descripcion;
  const RUBROS = { '1': 'Productos primarios', '2': 'Manufacturas de origen agropecuario (MOA)', '3': 'Manufacturas de origen industrial (MOI)', '4': 'Combustibles y energía', '9': 'Confidencial' };
  return {
    ultimo: { ...ult, x12: sum('x'), m12: sum('m'), saldo12: sum('saldo') },
    serie,
    rubros: rub.map(r => ({ codigo: r.rubro_cod, nombre: RUBROS[r.rubro_cod] || nombre['rubro_cod:' + r.rubro_cod] || r.rubro_cod, x: Math.round(r.sum / 1e6) })).sort((a, b) => b.x - a.x),
    destinos: pais.filter(r => r.sum && !/^X/.test(r.pais_cod) && !/indeterminado|confidencial|desconocido/i.test(nombre['pais_cod:' + r.pais_cod] || '')).map(r => ({ codigo: r.pais_cod, nombre: nombre['pais_cod:' + r.pais_cod] || r.pais_cod, x: Math.round(r.sum / 1e6) })).sort((a, b) => b.x - a.x).slice(0, 10),
    unidad: 'millones de USD',
  };
}

async function secPBI() {
  const d = await seriesFetch('series/', new URLSearchParams({ ids: '4.2_OGP_2004_T_17', limit: '80', sort: 'desc', format: 'json' }));
  const lv = (d.data || []).map(([f, v]) => ({ f, v })).reverse();
  const serie = [];
  for (let i = 4; i < lv.length; i++) {
    const [a, mm] = lv[i].f.split('-').map(Number);
    serie.push({ p: a + '-T' + ((mm - 1) / 3 + 1), label: ((mm - 1) / 3 + 1) + 'T ' + a, ia: r1((lv[i].v / lv[i - 4].v - 1) * 100) });
  }
  return { ultimo: serie[serie.length - 1], serie, fuente: 'INDEC vía datos.gob.ar (PIB a precios de 2004)' };
}

// Corre las tareas de a `n` para no recibir 429 del catálogo.
async function enTandas(tareas, n = 3) {
  const out = new Array(tareas.length); let i = 0;
  await Promise.all(Array.from({ length: n }, async () => {
    while (i < tareas.length) { const k = i++; try { out[k] = { ok: true, v: await tareas[k]() }; } catch (e) { out[k] = { ok: false, e: e.message }; } }
  }));
  return out;
}

async function armarTablero(env, ctx) {
  const ipc = await secIPC(env); // va primero: salarios lo necesita para el salario real
  const nombres = ['canasta', 'salarios', 'emae', 'trabajo', 'pobreza', 'comex', 'pbi', 'proximos'];
  const res = await enTandas([
    () => secCanasta(env), () => secSalarios(env, ipc.serie), () => secEMAE(env), () => secTrabajo(env),
    () => secPobreza(env), () => secComex(env), () => secPBI(),
    async () => {
      const hoy = new Date(Date.now() - 3 * 3600e3); const out = [];
      for (let i = 0; i < 2; i++) {
        const d = new Date(Date.UTC(hoy.getUTCFullYear(), hoy.getUTCMonth() + i, 1));
        const c = await cacheado(ctx, 'cal:' + d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1), TTL.calendario, () => calendarioMes(d.getUTCFullYear(), d.getUTCMonth() + 1));
        out.push(...c.data.eventos.map(clasificar));
      }
      const desde = hoy.toISOString().slice(0, 10);
      return out.filter(e => e.fecha >= desde);
    },
  ]);
  const t = { actualizado: new Date().toISOString(), ipc, errores: {} };
  nombres.forEach((n, i) => { if (res[i].ok) t[n] = res[i].v; else { t[n] = null; t.errores[n] = res[i].e; } });
  return t;
}

/* ───────────────────────── IPC a fondo (por región) ───────────────────────── */

const REGIONES = ['Nacional', 'GBA', 'Pampeana', 'Noreste', 'Noroeste', 'Cuyo', 'Patagonia'];
async function ipcDetalle(env, region) {
  // Rubros (divisiones) de los últimos 37 meses: alcanza para 3 años de interanuales.
  const ult = await filas(env, 'ipc_nacional', { region: 'eq.Nacional', codigo: 'eq.0', tipo_de_indicador: 'eq.v_m', order: 'periodo.desc', limit: '1' });
  const lat = ult[0].periodo;
  const [a, m] = [+lat.slice(0, 4), +lat.slice(4)];
  const d = new Date(Date.UTC(a, m - 1 - 36, 1)), desde = '' + d.getUTCFullYear() + String(d.getUTCMonth() + 1).padStart(2, '0');
  const [div, inc, clases, cats] = await Promise.all([
    filas(env, 'ipc_nacional', { region: 'eq.' + region, nivel: 'eq.División', tipo_de_indicador: 'in.(v_m,v_ia)', periodo: 'gte.' + desde }),
    region === 'Nacional' ? Promise.resolve([]) : filas(env, 'ipc_nacional', { region: 'eq.' + region, periodo: 'eq.' + lat, tipo_de_indicador: 'eq.Incidencia_m' }),
    filas(env, 'ipc_nacional', { region: 'eq.' + region, periodo: 'eq.' + lat, nivel: 'in.(Grupo,Clase)', tipo_de_indicador: 'in.(v_m,v_ia)' }),
    filas(env, 'ipc_nacional', { region: 'eq.' + region, codigo: 'in.(0,N,R,E,B,S)', tipo_de_indicador: 'in.(v_m,v_ia)', periodo: 'gte.' + desde }),
  ]);
  const rub = {};
  for (const x of div) {
    const r = (rub[x.codigo] ||= { codigo: x.codigo, nombre: x.descripcion, serie: {} });
    (r.serie[per(x.periodo)] ||= { p: per(x.periodo) })[x.tipo_de_indicador === 'v_m' ? 'm' : 'ia'] = r1(x.valor);
  }
  const rubros = Object.values(rub).map(r => ({ ...r, serie: ordenar(new Map(Object.entries(r.serie))) })).sort((a, b) => a.codigo.localeCompare(b.codigo));
  const incid = inc.map(x => ({ codigo: x.codigo, nombre: x.descripcion, inc: r2(x.valor) }));
  const cl = {}; for (const x of clases) (cl[x.codigo] ||= { codigo: x.codigo, nivel: x.nivel, nombre: x.descripcion })[x.tipo_de_indicador === 'v_m' ? 'm' : 'ia'] = r1(x.valor);
  const cat = porPeriodo(cats); const K = { '0': 'ng', N: 'n', R: 'r', E: 'e', B: 'b', S: 's' };
  for (const x of cats) cat.get(x.periodo)[K[x.codigo] + '_' + (x.tipo_de_indicador === 'v_m' ? 'm' : 'ia')] = r1(x.valor);
  return { region, periodo: per(lat), rubros, incidencias: incid, aperturas: Object.values(cl).sort((a, b) => a.codigo.localeCompare(b.codigo)), categorias: ordenar(cat) };
}

/* ───────────────────────── router ───────────────────────── */

export default {
  async fetch(req, env, ctx) {
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors(req) });
    if (req.method !== 'GET') return json(req, { error: 'Solo GET' }, 405);
    const url = new URL(req.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';
    const sinCache = url.searchParams.has('nocache') && env.ADMIN_KEY && url.searchParams.get('nocache') === env.ADMIN_KEY;

    try {
      if (path === '/' || path === '/v1') {
        return json(req, {
          servicio: 'manfredi-indec',
          endpoints: ['/v1/d/<dataset>?<filtros PostgREST>[&todo=1]', '/v1/calendario?mes=AAAA-MM', '/v1/calendario/proximos?dias=30', '/v1/series?ids=...', '/v1/buscar?q=...'],
          datasets: Object.keys(DATASETS),
        });
      }

      // /v1/tablero → primera vista entera. Si el INDEC falla, sirve el último bueno (7 días).
      if (path === '/v1/tablero') {
        const cache = caches.default;
        const kFresco = new Request('https://cache.manfredi-indec/tablero-v1');
        const kBueno = new Request('https://cache.manfredi-indec/tablero-v1-ok');
        if (!sinCache) { const hit = await cache.match(kFresco); if (hit) return json(req, { ...(await hit.json()), cache: 'hit' }, 200, 900); }
        let t;
        try { t = await armarTablero(env, ctx); } catch (e) { t = null; console.error('[indec] tablero', e.message); }
        if (!t) {
          const viejo = await cache.match(kBueno);
          if (viejo) return json(req, { ...(await viejo.json()), cache: 'stale' }, 200, 300);
          return json(req, { error: 'El INDEC no respondió y no hay copia guardada' }, 503, 60);
        }
        const body = JSON.stringify(t);
        ctx.waitUntil(cache.put(kFresco, new Response(body, { headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=' + TTL.tablero } })));
        if (!Object.keys(t.errores).length) ctx.waitUntil(cache.put(kBueno, new Response(body, { headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=' + 7 * 86400 } })));
        return json(req, { ...t, cache: 'miss' }, 200, 900);
      }

      // /v1/ipc?region=GBA → rubros 3 años, incidencias, grupos/clases y categorías
      if (path === '/v1/ipc') {
        const region = REGIONES.find(r => r.toLowerCase() === (url.searchParams.get('region') || 'Nacional').toLowerCase());
        if (!region) return json(req, { error: 'Región inválida', regiones: REGIONES }, 400);
        const r = await cacheado(ctx, 'ipc-det:' + region, TTL.datos, () => ipcDetalle(env, region));
        return json(req, r.data, 200, 900);
      }

      // /v1/d/<dataset> → proxy cacheado al Catálogo API-INDEC
      if (path.startsWith('/v1/d/')) {
        const ds = decodeURIComponent(path.slice(6));
        if (!DATASETS[ds]) return json(req, { error: 'Dataset no habilitado', datasets: Object.keys(DATASETS) }, 404);
        const p = limpiarParams(url.searchParams);
        const todo = url.searchParams.get('todo') === '1';
        const clave = 'd:' + ds + ':' + (todo ? 'todo:' : '') + p.toString();
        const producir = () => (todo ? indecTodo(env, ds, p) : indecFetch(env, ds, p));
        const r = sinCache ? { data: await producir(), cache: 'bypass' } : await cacheado(ctx, clave, TTL.datos, producir);
        return json(req, { dataset: ds, total: r.data.total, filas: r.data.filas, cache: r.cache, fuente: 'INDEC · Catálogo API-INDEC' }, 200, 900);
      }

      // /v1/calendario?mes=2026-12
      if (path === '/v1/calendario') {
        const hoy = new Date(Date.now() - 3 * 3600e3);
        const q = (url.searchParams.get('mes') || '').match(/^(\d{4})-(\d{2})$/);
        const anio = q ? +q[1] : hoy.getUTCFullYear(), mes = q ? +q[2] : hoy.getUTCMonth() + 1;
        if (mes < 1 || mes > 12) return json(req, { error: 'mes inválido' }, 400);
        const r = await cacheado(ctx, 'cal:' + anio + '-' + mes, TTL.calendario, () => calendarioMes(anio, mes));
        return json(req, { ...r.data, eventos: r.data.eventos.map(clasificar) }, 200, 1800);
      }

      // /v1/calendario/proximos?dias=30 → desde hoy (hora AR), une este mes y el siguiente
      if (path === '/v1/calendario/proximos') {
        const dias = Math.min(Math.max(+url.searchParams.get('dias') || 30, 1), 62);
        const hoy = new Date(Date.now() - 3 * 3600e3);
        const meses = [];
        for (let i = 0; i < 3; i++) { const d = new Date(Date.UTC(hoy.getUTCFullYear(), hoy.getUTCMonth() + i, 1)); meses.push([d.getUTCFullYear(), d.getUTCMonth() + 1]); }
        const desde = hoy.toISOString().slice(0, 10);
        const hasta = new Date(hoy.getTime() + dias * 864e5).toISOString().slice(0, 10);
        const partes = await Promise.all(meses.map(([a, m]) => cacheado(ctx, 'cal:' + a + '-' + m, TTL.calendario, () => calendarioMes(a, m)).then(r => r.data).catch(() => ({ eventos: [] }))));
        const eventos = partes.flatMap(p => p.eventos).filter(e => e.fecha >= desde && e.fecha <= hasta).map(clasificar);
        return json(req, { desde, hasta, eventos, fuente: INDEC_WEB + '/indec/web/Calendario-Fecha-0' }, 200, 1800);
      }

      // /v1/series?ids=...&limit=...  (datos.gob.ar)
      if (path === '/v1/series') {
        const sp = new URLSearchParams();
        for (const k of ['ids', 'limit', 'start_date', 'end_date', 'representation_mode', 'collapse', 'collapse_aggregation', 'sort']) if (url.searchParams.get(k)) sp.set(k, url.searchParams.get(k));
        if (!sp.get('ids')) return json(req, { error: 'ids requerido' }, 400);
        sp.set('format', 'json'); sp.set('metadata', 'simple');
        const r = await cacheado(ctx, 's:' + sp.toString(), TTL.series, () => seriesFetch('series/', sp));
        return json(req, r.data, 200, 1800);
      }

      // /v1/buscar?q=...  (buscador de series de datos.gob.ar, para el Explorador)
      if (path === '/v1/buscar') {
        const q = (url.searchParams.get('q') || '').trim().slice(0, 80);
        if (q.length < 2) return json(req, { data: [] });
        const sp = new URLSearchParams({ q, limit: String(Math.min(+url.searchParams.get('limit') || 20, 50)) });
        const r = await cacheado(ctx, 'b:' + sp.toString(), TTL.buscar, () => seriesFetch('search/', sp));
        const data = (r.data.data || []).map(x => ({
          id: x.field.id, titulo: x.field.description, frecuencia: x.field.frequency,
          desde: x.field.time_index_start, hasta: x.field.time_index_end, unidad: x.field.units,
          fuente: x.dataset && x.dataset.source, dataset: x.dataset && x.dataset.title,
        }));
        return json(req, { count: r.data.count, data }, 200, 3600);
      }

      return json(req, { error: 'No encontrado' }, 404);
    } catch (e) {
      console.error('[indec]', e.message);
      return json(req, { error: e.message }, e.status === 429 ? 503 : 502, 60);
    }
  },
};
