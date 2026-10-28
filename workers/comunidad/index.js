// workers/comunidad/index.js
// Worker "manfredi-comunidad": los chats de Manfredi Pro y los resúmenes del día.
//
// 1) Chats (pestaña Chat de Manfredi Pro, assets/comunidad/chat.js), mensajes en D1:
//    - "gratis" (Mercados): lo lee cualquiera; escribe cualquiera con sesión iniciada.
//    - "ideas", "socios", "preguntas" (Manfredi Pro): solo socios (verificado contra
//      workers/memberships) y creadores. En "ideas" publica solo el creador.
//    GET  /chat/:sala?ts=&antes=   mensajes (los últimos, los cambiados desde ts o los anteriores)
//    POST /chat/:sala              { texto, responde }           -> mensaje nuevo
//    POST /chat/:sala/:id/reaccion { emoji }                      -> pone/saca la reacción
//    POST /chat/:sala/:id/borrar                                  -> el autor o un creador
//
// 2) Resúmenes de apertura y cierre (los mismos que se comparten en la Comunidad de WhatsApp):
//    - Datos: worker mercados (/pulso y /mercados) y calendario (/calendario y /earnings).
//    - Texto: Gemini (cupo gratis, clave SIN facturación) redacta un párrafo corto SOLO con los
//      números que se le pasan; si inventa un número, falla o no hay cupo, sale la plantilla.
//    - Se publican como mensaje oficial del chat gratis (1 por día y momento: regenerar lo reemplaza).
//    - Horario de Wall Street: 30 min antes de la apertura (9:00 NY) y 30 min después del cierre
//      (16:30 NY; 13:30 los días que cierra temprano). Sin resumen los feriados de la NYSE.
//      10 min después se reintenta la IA si hizo falta y sale el mail (si hay RESEND_API_KEY).
//    GET /wa/apertura · /wa/cierre  (?regenerar=1)  -> solo creadores (Panel de creador)

const CREADORES = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
// En orden: si uno está saturado (503), tarda o no tiene cupo (429), prueba el siguiente.
// El liviano va primero: el principal suele estar saturado y tarda más de 25 s.
const MODELOS = ['gemini-3.5-flash-lite', 'gemini-flash-latest', 'gemini-flash-lite-latest'];
const PANEL_LIDER = ['ALUA', 'BBAR', 'BMA', 'BYMA', 'CEPU', 'COME', 'CRES', 'EDN', 'GGAL', 'IRSA', 'LOMA', 'METR', 'PAMP', 'SUPV', 'TECO2', 'TGNO4', 'TGSU2', 'TRAN', 'TXAR', 'VALO', 'YPFD'];
const BONOS = ['AL30D', 'GD30D', 'GD35D', 'AE38D', 'GD41D'];
const MEMBERSHIPS_BASE = 'https://manfredi-memberships.nachito2502.workers.dev';
// Salas: "gratis" (Mercados) y los chats de Manfredi Pro (solo socios).
// soloCreador: los socios leen y reaccionan, pero publica solo Ignacio.
const SALAS = {
  gratis:    { pro: false },
  ideas:     { pro: true, soloCreador: true },
  socios:    { pro: true },
  preguntas: { pro: true },
};
const EMOJIS = ['👍', '🔥', '📈', '📉', '🤔'];
const MAX_TEXTO = 800;
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Content-Type': 'application/json',
};
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: CORS });

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const url = new URL(request.url);
    try {
      const c = url.pathname.match(/^\/chat\/(gratis|ideas|socios|preguntas)(?:\/(\d+)\/(reaccion|borrar))?$/);
      if (c) return await chat(request, env, url, c[1], c[2] ? +c[2] : null, c[3] || null);

      const m = url.pathname.match(/^\/wa\/(apertura|cierre)$/);
      if (!m || request.method !== 'GET') return json({ error: 'Ruta no encontrada' }, 404);
      const u = await usuarioDelToken(request);
      if (!u) return json({ error: 'No autenticado' }, 401);
      if (!CREADORES.includes(u.email)) return json({ error: 'Solo para creadores' }, 403);
      return json(await resumen(env, m[1], url.searchParams.get('regenerar') === '1'));
    } catch (e) {
      return json({ error: e.message }, 500);
    }
  },

  // El cron corre cada 10/30 min en las horas posibles (UTC) y acá se decide con la hora de
  // Nueva York, que cambia de horario de verano en fechas distintas que la Argentina.
  async scheduled(event, env, ctx) {
    const turno = turnoDeResumen(new Date(event.scheduledTime));
    if (!turno) return;
    ctx.waitUntil((async () => {
      let r = await resumen(env, turno.momento, !turno.reintento);
      if (turno.reintento && !r.ia) r = await resumen(env, turno.momento, true);
      if (turno.reintento) await avisarPorMail(env, r);
    })());
  },
};

// ─── Horario de Wall Street ──────────────────────────────────────────────────

// NYSE: feriados y días de cierre temprano (13:00 NY). Actualizar una vez por año.
const NYSE_FERIADOS = new Set([
  '2026-11-26', '2026-12-25',
  '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18',
  '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24',
]);
const NYSE_MEDIO_DIA = new Set(['2026-11-27', '2026-12-24', '2027-11-26']);

function horaNY(d) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York', hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', weekday: 'short',
  }).formatToParts(d).map(x => [x.type, x.value]));
  return { iso: `${p.year}-${p.month}-${p.day}`, min: +p.hour * 60 + +p.minute, finde: p.weekday === 'Sat' || p.weekday === 'Sun' };
}
// apertura: 9:00 NY (30 min antes de las 9:30) · cierre: 30 min después de las 16:00 (o 13:00)
function turnoDeResumen(d) {
  const ny = horaNY(d);
  if (ny.finde || NYSE_FERIADOS.has(ny.iso)) return null;
  const cierre = NYSE_MEDIO_DIA.has(ny.iso) ? 13 * 60 + 30 : 16 * 60 + 30;
  if (ny.min === 9 * 60) return { momento: 'apertura', reintento: false };
  if (ny.min === 9 * 60 + 10) return { momento: 'apertura', reintento: true };
  if (ny.min === cierre) return { momento: 'cierre', reintento: false };
  if (ny.min === cierre + 10) return { momento: 'cierre', reintento: true };
  return null;
}

// ─── Resumen del día ─────────────────────────────────────────────────────────

// El resumen vive en el chat gratis como mensaje oficial (clave única por día y momento):
// el Panel, el chat del sitio y WhatsApp muestran exactamente el mismo mensaje.
async function resumen(env, momento, regenerar) {
  const hoy = hoyART();
  const clave = `resumen:${hoy.iso}:${momento}`;
  await esquema(env);
  if (!regenerar) {
    const fila = await env.DB.prepare('SELECT id, datos FROM mensajes WHERE clave = ?').bind(clave).first();
    if (fila) return { ...JSON.parse(fila.datos), id: fila.id };
  }
  const datos = await juntarDatos(env, momento, hoy);
  const ia = await redactar(env, momento, datos);
  const r = {
    momento,
    fecha: hoy.iso,
    fechaLarga: hoy.larga,
    generado: new Date().toISOString(),
    ia: !!ia,
    clave: ia ? ia.clave : null,             // "La clave del día": una frase, solo con IA
    intro: ia ? ia.parrafo : introPlantilla(momento, datos),
    datos,
  };
  r.texto = textoWhatsApp(r, env.SITE_URL);
  const ahora = Date.now();
  const fila = await env.DB.prepare(
    `INSERT INTO mensajes (sala, h, nombre, rol, tipo, texto, datos, clave, creado, editado)
     VALUES ('gratis', 'oficial', 'Manfredi Investment', 'oficial', 'resumen', ?, ?, ?, ?, ?)
     ON CONFLICT(clave) DO UPDATE SET texto = excluded.texto, datos = excluded.datos, editado = excluded.editado, borrado = 0
     RETURNING id`
  ).bind(r.texto, JSON.stringify(r), clave, ahora, ahora).first();
  // el id del mensaje arma el link del epígrafe de WhatsApp (abre el chat en este resumen)
  return { ...r, id: fila.id };
}

function hoyART() {
  const d = new Date(Date.now() - 3 * 3600e3);
  const iso = d.toISOString().slice(0, 10);
  const larga = d.toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC' });
  return { d, iso, larga, ddmm: iso.slice(8, 10) + '/' + iso.slice(5, 7) };
}

async function getJSON(url) {
  try {
    const r = await fetch(url, { signal: AbortSignal.timeout(20000) });
    return r.ok ? await r.json() : null;
  } catch (e) { return null; }
}

async function juntarDatos(env, momento, hoy) {
  const [pulso, mercados, cal, earn] = await Promise.all([
    getJSON(env.MERCADOS_URL + '/pulso'),
    getJSON(env.MERCADOS_URL + '/mercados'),
    getJSON(env.CALENDARIO_URL + '/calendario'),
    getJSON(env.CALENDARIO_URL + '/earnings'),
  ]);
  if (!pulso) throw new Error('No se pudieron leer las cotizaciones (worker mercados /pulso)');

  const fila = c => c && c.price != null ? { id: c.id, n: c.name, v: c.price, u: c.unit || '', c: c.change ?? null, d: c.delta ?? null } : null;
  const argentina = pulso.argentina.cotizaciones.map(fila).filter(Boolean);
  const mundo = pulso.mundo.cotizaciones.map(fila).filter(Boolean);

  const cat = k => (mercados && mercados.categorias && mercados.categorias[k] && mercados.categorias[k].items) || [];
  const porSimbolo = k => Object.fromEntries(cat(k).map(i => [i.symbol, i]));
  const bonosMap = porSimbolo('arg_bonds');
  const bonos = BONOS.map(s => bonosMap[s]).filter(b => b && b.price != null && b.change != null)
    .map(b => ({ n: b.symbol.replace(/D$/, ''), v: b.price, u: 'US$', c: b.change }));

  // Los que más se movieron solo tienen sentido al cierre (a la mañana son los de ayer).
  let panel = null, cedears = null;
  if (momento === 'cierre') {
    const acc = porSimbolo('arg_stocks');
    const lider = PANEL_LIDER.map(s => acc[s]).filter(a => a && a.change != null)
      .sort((a, b) => b.change - a.change).map(a => ({ n: a.symbol, c: a.change }));
    if (lider.length >= 6) {
      panel = { suben: lider.filter(a => a.c > 0).slice(0, 3), bajan: lider.filter(a => a.c < 0).slice(-3).reverse() };
    }
    const ced = cat('arg_cedears').filter(c => c.change != null && c.volume)
      .sort((a, b) => b.volume - a.volume).slice(0, 6).map(c => ({ n: c.symbol, c: c.change }));
    if (ced.length) cedears = ced;
  }

  // Agenda: hoy a la mañana, el próximo día hábil al cierre.
  const agendaDe = ddmm => {
    const evs = [];
    for (const src of [cal, earn]) {
      const dia = src && (src.dias || []).find(x => x.fecha === ddmm);
      if (dia) evs.push(...dia.eventos.map(e => ({ tipo: e.tipo, t: e.titulo })));
    }
    return evs.slice(0, 6);
  };
  const proximo = new Date(hoy.d);
  do { proximo.setUTCDate(proximo.getUTCDate() + 1); } while ([0, 6].includes(proximo.getUTCDay()));
  const ddmmProx = proximo.toISOString().slice(8, 10) + '/' + proximo.toISOString().slice(5, 7);
  const agenda = momento === 'apertura'
    ? { titulo: 'Agenda de hoy', eventos: agendaDe(hoy.ddmm) }
    : { titulo: hoy.d.getUTCDay() === 5 ? 'Agenda del lunes' : 'Agenda de mañana', eventos: agendaDe(ddmmProx) };

  // En el mensaje van 5 titulares; la IA recibe además las bajadas de todos para explicar el porqué.
  const nota = n => ({ t: n.titulo, f: n.fuente, r: (n.resumen || '').slice(0, 260) });
  const ar = pulso.argentina.noticias || [], mu = pulso.mundo.noticias || [];
  const noticias = [...ar.slice(0, 3), ...mu.slice(0, 2)].map(nota);
  const contexto = [...ar, ...mu].map(nota);

  // Brecha (MEP contra oficial) y canje (CCL contra MEP), en %.
  const v = id => (argentina.find(f => f.id === id) || {}).v;
  const of = v('oficial'), mep = v('bolsa'), ccl = v('contadoconliqui');
  const derivados = {
    brecha: of && mep ? (mep / of - 1) * 100 : null,
    canje: mep && ccl ? (ccl / mep - 1) * 100 : null,
  };

  return { argentina, derivados, bonos, mundo, panel, cedears, agenda, noticias, contexto };
}

// ─── Redacción con IA (Gemini, cupo gratis) ─────────────────────────────────

async function redactar(env, momento, datos) {
  if (!env.GEMINI_KEY) return null;
  const consigna = momento === 'apertura'
    ? `Es el resumen de la MAÑANA, media hora antes de que abra Wall Street. Los precios son del último cierre.
"clave": lo que define el día que empieza (un dato de la agenda, una noticia o el último movimiento importante).
"parrafo": 1) en qué quedó el último cierre en la Argentina y por qué, 2) cómo viene el mundo, 3) qué hay que mirar hoy en la agenda.`
    : `Es el resumen del CIERRE, media hora después de que cerró Wall Street.
"clave": lo que definió la rueda de hoy.
"parrafo": 1) qué pasó en la Argentina y por qué, 2) qué pasó en Wall Street y el mundo y por qué, 3) qué hay en la agenda de mañana, si es relevante.`;
  const prompt = `Sos el analista que escribe el resumen diario de "Manfredi Investment" para una comunidad de inversores argentinos (chat del sitio y WhatsApp).
${consigna}

Respondé SOLO un JSON: {"clave": "...", "parrafo": "..."}

"clave": una sola frase, de 8 a 16 palabras, tipo titular de diario financiero serio. Sin punto final.
"parrafo": de 50 a 85 palabras, 3 oraciones como máximo.

Reglas estrictas:
- Español rioplatense neutro y profesional, con tildes y ortografía correctas. Sin emojis, hashtags, saludos ni signos de exclamación.
- Interpretá: conectá los movimientos con lo que dicen los titulares y sus bajadas ("contexto"). Si ninguna noticia explica un movimiento, describilo sin inventar causas.
- Usá SOLO números que estén en los DATOS, con formato argentino: punto de miles, coma decimal, máximo 1 decimal (ej.: $1.560,9; 753 puntos; 1,1%). Si un dato no está, no lo menciones.
- "c" es la variación del día en %; en riesgo país, "d" es la diferencia en puntos básicos. "derivados.brecha" es la brecha del MEP con el oficial y "derivados.canje" la del CCL con el MEP, en %.
- Nada de recomendaciones de compra o venta ni predicciones de precios.
- Sin adjetivos exagerados ("explosivo", "brutal", "histórico", "sangría").

DATOS:
${JSON.stringify(datos)}`;

  for (const modelo of MODELOS) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-goog-api-key': env.GEMINI_KEY },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.4, maxOutputTokens: 2048, responseMimeType: 'application/json' },
        }),
        signal: AbortSignal.timeout(30000),
      });
      if (!r.ok) { console.warn(`[resumen] ${modelo} HTTP ${r.status}`); continue; } // sin cupo (429) u otro error: siguiente
      const d = await r.json();
      const crudo = (d.candidates?.[0]?.content?.parts || []).filter(p => !p.thought).map(p => p.text || '').join('');
      let o;
      try { o = JSON.parse(crudo.replace(/^```(?:json)?|```$/g, '').trim()); } catch (e) { console.warn(`[resumen] ${modelo} no devolvió JSON`); continue; }
      const limpio = t => String(t || '').replace(/\s+/g, ' ').replace(/[*_~`]/g, '').trim();
      const clave = limpio(o.clave).replace(/\.$/, ''), parrafo = limpio(o.parrafo);
      if (clave.length < 25 || clave.length > 140 || parrafo.length < 120 || parrafo.length > 700) {
        console.warn(`[resumen] ${modelo} largo clave ${clave.length} / párrafo ${parrafo.length}`); continue;
      }
      // a veces el modelo liviano escribe sin tildes: mejor el siguiente modelo o la plantilla
      if (/(dolar|pais|decision|indices|politica|economia|tecnologico|atencion|mas alla|segun)/i.test(clave + ' ' + parrafo)) {
        console.warn(`[resumen] ${modelo} sin tildes`); continue;
      }
      const malos = numerosInvalidos(clave + ' ' + parrafo, datos);
      if (malos.length) { console.warn(`[resumen] ${modelo} números fuera de los datos: ${malos.join(', ')}`); continue; } // inventó o redondeó mal
      return { clave, parrafo };
    } catch (e) { console.warn(`[resumen] ${modelo} ${e.message}`); }
  }
  return null;
}

// Cada número del texto de la IA tiene que salir de los datos (o de los titulares, la agenda,
// la fecha de hoy o los horarios del mercado). Devuelve los que no.
function numerosInvalidos(txt, datos) {
  const ok = new Set();
  const sinSep = s => s.replace(/[.,]/g, '').replace(/^0+(?=\d)/, '');
  const agregar = v => {
    if (typeof v !== 'number' || !isFinite(v)) return;
    for (const dec of [0, 1, 2]) {
      ok.add(sinSep(Math.abs(v).toLocaleString('es-AR', { minimumFractionDigits: dec, maximumFractionDigits: dec })));
    }
  };
  const recorrer = o => {
    if (o == null) return;
    if (typeof o === 'number') agregar(o);
    else if (typeof o === 'string') (o.match(/\d+(?:[.,]\d+)*/g) || []).forEach(n => ok.add(sinSep(n)));
    else if (typeof o === 'object') Object.values(o).forEach(recorrer);
  };
  recorrer(datos);
  const hoy = hoyART();
  [hoy.d.getUTCDate(), hoy.d.getUTCFullYear(), 11, 16, 17].forEach(agregar);
  return (txt.match(/\d+(?:[.,]\d+)*/g) || []).filter(n => +sinSep(n) >= 10 && !ok.has(sinSep(n)));
}

function introPlantilla(momento, datos) {
  const buscar = id => datos.argentina.find(f => f.id === id) || datos.mundo.find(f => f.id === id);
  const partes = [];
  const merval = buscar('merval'), riesgo = buscar('riesgo'), mep = buscar('bolsa'), sp = buscar('sp500');
  if (merval && merval.c != null) partes.push(`el Merval ${verbo(merval.c)} ${pct(merval.c, false)}`);
  if (riesgo) partes.push(`el riesgo país quedó en ${num(riesgo.v, 0)} puntos`);
  if (mep && mep.c != null) partes.push(`el dólar MEP ${verbo(mep.c)} ${pct(mep.c, false)} a $${num(mep.v, 2)}`);
  if (sp && sp.c != null) partes.push(`en Wall Street el S&P 500 ${verbo(sp.c)} ${pct(sp.c, false)}`);
  if (!partes.length) return momento === 'apertura' ? 'Lo que hay que saber antes de la apertura.' : 'Así cerró el mercado hoy.';
  const cuerpo = partes.length > 1 ? partes.slice(0, -1).join(', ') + ' y ' + partes[partes.length - 1] : partes[0];
  return (momento === 'apertura' ? 'En el último cierre, ' : 'Hoy ') + cuerpo + '.';
}

// ─── Formato WhatsApp ────────────────────────────────────────────────────────
// *negrita*, _cursiva_, > cita, - lista y ```bloque``` de ancho fijo para que las cotizaciones
// queden en columnas (el chat del sitio lo muestra igual). En los bloques, solo caracteres de
// ancho fijo seguro: "-" común en vez de "−" y sin flechas.

function num(v, dec) {
  const d = dec != null ? dec : Math.abs(v) >= 10000 ? 0 : 2;
  return v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
}
// Todo se decide sobre el valor ya redondeado a 1 decimal (−0,04% es "0,0%").
const r1 = c => Math.round(c * 10) / 10;
function pct(c, signo = true, menos = '−') {
  const s = Math.abs(r1(c)).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
  return signo ? (r1(c) > 0 ? '+' : r1(c) < 0 ? menos : '') + s : s;
}
function verbo(c) { return r1(c) > 0 ? 'subió' : r1(c) < 0 ? 'bajó' : 'quedó estable,'; }
function precio(f, sinUsd) {
  if (f.u === 'pb') return num(f.v, 0) + ' pb';
  if (sinUsd && f.u === 'US$') return num(f.v);
  return (f.u === '$' ? '$' : f.u ? f.u + ' ' : '') + num(f.v);
}
const CORTOS = { 'Dólar oficial': 'Oficial', 'Dólar MEP': 'MEP', 'Dólar CCL': 'CCL', 'Dólar blue': 'Blue', 'Petróleo WTI': 'Petróleo' };
// Columnas: nombre 12 · precio 10 · variación 8 (en dólares sin "US$": el título ya lo dice).
function filaTabla(nombre, valor, vari) { return nombre.padEnd(12) + valor.padStart(10) + vari.padStart(8); }
function tabla(filas, extra) {
  const lineas = filas.map(f => {
    const vari = f.d != null ? (f.d > 0 ? '+' : f.d < 0 ? '-' : '') + Math.abs(f.d) + ' pb' : f.c != null ? pct(f.c, true, '-') : '';
    return filaTabla(CORTOS[f.n] || f.n, precio(f, true), vari);
  });
  return ['```', ...lineas, ...(extra || []), '```'];
}

function textoWhatsApp(r, site) {
  const d = r.datos, ape = r.momento === 'apertura';
  const fecha = r.fechaLarga.charAt(0).toUpperCase() + r.fechaLarga.slice(1);
  const out = [`*MANFREDI · ${ape ? 'ANTES DE LA APERTURA' : 'CIERRE DEL MERCADO'}*`, `_${fecha}_`, ''];
  if (r.clave) out.push(`> *${r.clave}*`, '');
  out.push(r.intro, '');

  // Argentina (a la mañana es el último cierre)
  out.push(`*🇦🇷 Argentina*${ape ? ' _· último cierre_' : ''}`);
  const der = d.derivados || {}, extra = [];
  if (der.brecha != null) extra.push(filaTabla('Brecha MEP', '', pct(der.brecha, true, '-')));
  if (der.canje != null) extra.push(filaTabla('Canje CCL', '', pct(der.canje, true, '-')));
  out.push(...tabla(d.argentina, extra));

  if (d.bonos.length) {
    out.push('', '*Bonos en dólares*', '```');
    for (let i = 0; i < d.bonos.length; i += 2) {
      out.push(d.bonos.slice(i, i + 2).map(b => (b.n.padEnd(6) + pct(b.c, true, '-').padStart(7))).join('   '));
    }
    out.push('```');
  }
  if (d.panel) {
    out.push('', '*Panel líder*');
    if (d.panel.suben.length) out.push('▲ ' + d.panel.suben.map(a => `${a.n} ${pct(a.c)}`).join(' · '));
    if (d.panel.bajan.length) out.push('▼ ' + d.panel.bajan.map(a => `${a.n} ${pct(a.c)}`).join(' · '));
  }
  if (d.cedears) out.push('', '*CEDEARs más operados*', d.cedears.map(c => `${c.n} ${pct(c.c)}`).join(' · '));

  out.push('', `*🇺🇸 Wall Street y el mundo* _· ${ape ? 'último cierre, ' : ''}en US$_`, ...tabla(d.mundo));
  if (d.agenda.eventos.length) out.push('', `*📅 ${d.agenda.titulo}*`, ...d.agenda.eventos.map(e => `- ${e.t}`));
  if (d.noticias.length) out.push('', '*📰 Lo que se lee*', ...d.noticias.map(n => `- ${n.t} _(${n.f})_`));
  out.push('', `_Cotizaciones en vivo y la Comunidad: ${site.replace(/^https?:\/\//, '')}_`);
  return out.join('\n');
}

// ─── Chats (D1) ──────────────────────────────────────────────────────────────

let _esquemaListo = false;
async function esquema(env) {
  if (_esquemaListo) return;
  await env.DB.batch([
    env.DB.prepare(`CREATE TABLE IF NOT EXISTS mensajes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sala TEXT NOT NULL,
      uid TEXT, h TEXT, nombre TEXT, foto TEXT, rol TEXT,
      tipo TEXT NOT NULL DEFAULT 'texto',
      texto TEXT, datos TEXT, cita TEXT, responde INTEGER,
      clave TEXT UNIQUE,
      reacciones TEXT NOT NULL DEFAULT '{}',
      creado INTEGER NOT NULL, editado INTEGER NOT NULL,
      borrado INTEGER NOT NULL DEFAULT 0)`),
    env.DB.prepare('CREATE INDEX IF NOT EXISTS ix_sala_editado ON mensajes (sala, editado)'),
    env.DB.prepare('CREATE INDEX IF NOT EXISTS ix_sala_id ON mensajes (sala, id)'),
  ]);
  // Primer mensaje de cada sala: la bienvenida oficial (una sola vez, por clave).
  const ahora = Date.now();
  const bienvenida = {
    gratis: 'Bienvenidos a la Comunidad de *Manfredi Investment*. Acá se publica el resumen del mercado antes de la apertura y al cierre, todos los días hábiles, y se charla de mercados con respeto. Nadie del equipo te va a escribir por privado ni a pedirte dinero.',
    ideas: 'Acá publica Ignacio sus *ideas*, los *seguimientos* y los *cierres*, con resultado. Para comentar, usá la Charla de socios; para consultar, Preguntas a Ignacio.',
    socios: 'La *charla de los socios* de Manfredi Pro. Lo que se comparte acá queda entre socios.',
    preguntas: 'Dejá tu pregunta para Ignacio: te responde citando tu mensaje. Una pregunta por mensaje ayuda a que nada quede sin respuesta.',
  };
  await env.DB.batch(Object.keys(SALAS).map(sala => env.DB.prepare(
    `INSERT OR IGNORE INTO mensajes (sala, h, nombre, rol, tipo, texto, clave, creado, editado)
     VALUES (?, 'oficial', 'Manfredi Investment', 'oficial', 'texto', ?, ?, ?, ?)`
  ).bind(sala, bienvenida[sala], 'bienvenida:' + sala, ahora, ahora)));
  _esquemaListo = true;
}

// Socio o no, con memoria de 10 minutos por email (el chat Pro consulta cada pocos segundos).
const _socios = new Map();
async function esSocio(env, email) {
  if (CREADORES.includes(email)) return true;
  const c = _socios.get(email);
  if (c && c.exp > Date.now()) return c.v;
  let v = false;
  try {
    const r = await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/verificar-membresia?email=${encodeURIComponent(email)}`);
    v = !!(await r.json()).miembro;
  } catch (e) { v = false; } // si memberships no responde, se asume no-socio (igual que warren)
  _socios.set(email, { v, exp: Date.now() + 600e3 });
  return v;
}

// Identificador público del autor (para colores, agrupar y "mis reacciones"): nunca el uid.
async function hashUid(uid) {
  const b = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode('mi-chat:' + uid)));
  return Array.from(b.slice(0, 6), x => x.toString(16).padStart(2, '0')).join('');
}

function publico(f) {
  const borrado = !!f.borrado;
  return {
    id: f.id, h: f.h, nombre: f.nombre, foto: f.foto || '', rol: f.rol, tipo: f.tipo,
    texto: borrado ? '' : f.texto,
    datos: borrado || !f.datos ? null : JSON.parse(f.datos),
    cita: borrado || !f.cita ? null : JSON.parse(f.cita),
    responde: f.responde, reacciones: borrado ? {} : JSON.parse(f.reacciones || '{}'),
    creado: f.creado, editado: f.editado, borrado,
  };
}

async function chat(request, env, url, sala, id, accion) {
  await esquema(env);
  const u = await usuarioDelToken(request);
  const creador = !!(u && CREADORES.includes(u.email));
  const socio = !!(u && await esSocio(env, u.email));
  const yo = u ? { h: await hashUid(u.uid), nombre: u.nombre || u.email.split('@')[0], rol: creador ? 'creador' : socio ? 'socio' : 'usuario' } : null;
  if (SALAS[sala].pro && !socio) return json({ error: u ? 'solo_socios' : 'sin_sesion', yo }, u ? 403 : 401);

  // ── leer
  if (request.method === 'GET' && !id) {
    const ts = +url.searchParams.get('ts') || 0, antes = +url.searchParams.get('antes') || 0;
    let filas;
    if (antes) {
      filas = (await env.DB.prepare('SELECT * FROM mensajes WHERE sala = ? AND id < ? ORDER BY id DESC LIMIT 60').bind(sala, antes).all()).results.reverse();
    } else if (ts) {
      filas = (await env.DB.prepare('SELECT * FROM mensajes WHERE sala = ? AND editado >= ? ORDER BY id LIMIT 200').bind(sala, ts - 1).all()).results;
    } else {
      filas = (await env.DB.prepare('SELECT * FROM mensajes WHERE sala = ? ORDER BY id DESC LIMIT 80').bind(sala).all()).results.reverse();
    }
    const hayMas = antes ? filas.length >= 60 : !ts && filas.length >= 80;
    // Resúmenes de hoy: la guía de arriba del chat lleva a ellos aunque la charla los deje lejos.
    let hoy = [];
    if (sala === 'gratis') {
      const f = hoyART().iso;
      hoy = (await env.DB.prepare('SELECT id, clave, creado FROM mensajes WHERE clave IN (?, ?) AND borrado = 0')
        .bind(`resumen:${f}:apertura`, `resumen:${f}:cierre`).all()).results
        .map(r => ({ id: r.id, momento: r.clave.split(':')[2], creado: r.creado }));
    }
    return json({ sala, ahora: Date.now(), mensajes: filas.map(publico), yo, hayMas, hoy });
  }
  if (request.method !== 'POST') return json({ error: 'Método no permitido' }, 405);
  if (!u) return json({ error: 'sin_sesion' }, 401);
  const body = await request.json().catch(() => ({}));
  const ahora = Date.now();

  // ── mensaje nuevo
  if (!id) {
    if (SALAS[sala].soloCreador && !creador) return json({ error: 'En este chat publica solo Ignacio' }, 403);
    const texto = String(body.texto || '').replace(/\r/g, '').replace(/\n{3,}/g, '\n\n').trim();
    if (!texto) return json({ error: 'El mensaje está vacío' }, 400);
    if (texto.length > MAX_TEXTO) return json({ error: `Máximo ${MAX_TEXTO} caracteres` }, 400);
    // Un mensaje cada 3 segundos por persona.
    const ult = await env.DB.prepare('SELECT creado FROM mensajes WHERE sala = ? AND h = ? ORDER BY id DESC LIMIT 1').bind(sala, yo.h).first();
    if (ult && ahora - ult.creado < 3000) return json({ error: 'Esperá unos segundos antes de mandar otro mensaje' }, 429);
    let cita = null, responde = null;
    if (body.responde) {
      const o = await env.DB.prepare('SELECT id, nombre, texto, tipo, datos, borrado FROM mensajes WHERE id = ? AND sala = ?').bind(+body.responde, sala).first();
      if (o && !o.borrado) {
        responde = o.id;
        const t = o.tipo === 'resumen' ? (JSON.parse(o.datos).momento === 'apertura' ? 'Resumen antes de la apertura' : 'Resumen del cierre') : o.texto;
        cita = JSON.stringify({ nombre: o.nombre, texto: t.slice(0, 160) });
      }
    }
    const r = await env.DB.prepare(
      `INSERT INTO mensajes (sala, uid, h, nombre, foto, rol, texto, cita, responde, creado, editado)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING *`
    ).bind(sala, u.uid, yo.h, yo.nombre.slice(0, 60), u.foto, yo.rol, texto, cita, responde, ahora, ahora).first();
    return json({ mensaje: publico(r), ahora });
  }

  const f = await env.DB.prepare('SELECT * FROM mensajes WHERE id = ? AND sala = ?').bind(id, sala).first();
  if (!f || f.borrado) return json({ error: 'El mensaje ya no existe' }, 404);

  // ── reacción (pone, cambia o saca la de esta persona)
  if (accion === 'reaccion') {
    if (!EMOJIS.includes(body.emoji)) return json({ error: 'Reacción no válida' }, 400);
    const re = JSON.parse(f.reacciones || '{}');
    const tenia = Object.keys(re).find(e => re[e].includes(yo.h));
    Object.keys(re).forEach(e => { re[e] = re[e].filter(x => x !== yo.h); if (!re[e].length) delete re[e]; });
    if (tenia !== body.emoji) (re[body.emoji] = re[body.emoji] || []).push(yo.h);
    await env.DB.prepare('UPDATE mensajes SET reacciones = ?, editado = ? WHERE id = ?').bind(JSON.stringify(re), ahora, id).run();
    return json({ mensaje: publico({ ...f, reacciones: JSON.stringify(re), editado: ahora }), ahora });
  }

  // ── borrar: el autor o un creador
  if (accion === 'borrar') {
    if (!creador && f.h !== yo.h) return json({ error: 'Solo podés borrar tus mensajes' }, 403);
    await env.DB.prepare('UPDATE mensajes SET borrado = 1, editado = ? WHERE id = ?').bind(ahora, id).run();
    return json({ mensaje: publico({ ...f, borrado: 1, editado: ahora }), ahora });
  }
  return json({ error: 'Ruta no encontrada' }, 404);
}

// ─── Aviso por mail (Resend) ────────────────────────────────────────────────

async function avisarPorMail(env, r) {
  if (!env.RESEND_API_KEY) return;
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const asunto = r.momento === 'apertura' ? 'Listo para WhatsApp: resumen antes de la apertura' : 'Listo para WhatsApp: resumen del cierre';
  const html = `<div style="background:#0b1629;padding:28px;font-family:Helvetica,Arial,sans-serif;color:#f3f6fb">
    <p style="margin:0 0 6px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#e9d3a0">Comunidad de WhatsApp</p>
    <p style="margin:0 0 18px;font-size:15px;color:#f3f6fb">El resumen está listo. Abrilo en el Panel y tocá <b>Compartir</b>:</p>
    <a href="${env.SITE_URL}/#panel" style="display:inline-block;padding:10px 18px;border:1px solid #e9d3a0;border-radius:8px;color:#e9d3a0;text-decoration:none;font-size:14px">Abrir el Panel</a>
    <pre style="margin:24px 0 0;white-space:pre-wrap;font:13px/1.55 Menlo,Consolas,monospace;color:#f3f6fb">${esc(r.texto)}</pre>
  </div>`;
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: 'Manfredi Investment <hola@manfredinvestment.com>', to: CREADORES[0], subject: asunto, html }),
  }).catch(() => {});
}

// ─── ID token de Firebase (misma verificación que workers/admin) ────────────
let _jwksCache = { keys: null, exp: 0 };
function b64urlBytes(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
async function usuarioDelToken(request) {
  const auth = request.headers.get('Authorization') || '';
  const parts = (auth.startsWith('Bearer ') ? auth.slice(7) : '').split('.');
  if (parts.length !== 3) return null;
  try {
    const header = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[0])));
    const p = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[1])));
    if (header.alg !== 'RS256' || p.aud !== FIREBASE_PROJECT || p.iss !== 'https://securetoken.google.com/' + FIREBASE_PROJECT) return null;
    if (!p.exp || p.exp < Math.floor(Date.now() / 1000) || !p.email || p.email_verified === false) return null;
    if (!_jwksCache.keys || Date.now() > _jwksCache.exp) {
      const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
      _jwksCache = { keys: (await r.json()).keys, exp: Date.now() + 3600e3 };
    }
    const jwk = _jwksCache.keys.find(k => k.kid === header.kid);
    if (!jwk) return null;
    const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
    return ok ? { email: String(p.email).toLowerCase(), uid: String(p.user_id || p.sub), nombre: p.name || '', foto: p.picture || '' } : null;
  } catch (e) { return null; }
}
