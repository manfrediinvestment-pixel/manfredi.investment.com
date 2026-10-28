// workers/whatsapp/index.js
// Worker "manfredi-whatsapp": arma los resúmenes de la Comunidad de WhatsApp
// (apertura y cierre del mercado) para compartir en 1 toque desde el Panel de creador.
//
// - Datos: worker mercados (/pulso y /mercados) y calendario (/calendario y /earnings).
// - Texto: Gemini (cupo gratis, clave SIN facturación) redacta un párrafo corto SOLO con los
//   números que se le pasan; si inventa un número, falla o no hay cupo, sale la plantilla.
// - Se guarda 1 vez por día y momento en KV (≤ 4 escrituras por día).
// - Cron de lunes a viernes: genera y avisa por mail (si hay RESEND_API_KEY).
//
// GET /wa/apertura · /wa/cierre  (?regenerar=1)  -> solo cuentas CREADORES (ID token de Firebase)

const CREADORES = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
// En orden: si uno está saturado (503) o sin cupo (429), prueba el siguiente.
const MODELOS = ['gemini-flash-latest', 'gemini-3.5-flash-lite', 'gemini-flash-lite-latest'];
const PANEL_LIDER = ['ALUA', 'BBAR', 'BMA', 'BYMA', 'CEPU', 'COME', 'CRES', 'EDN', 'GGAL', 'IRSA', 'LOMA', 'METR', 'PAMP', 'SUPV', 'TECO2', 'TGNO4', 'TGSU2', 'TRAN', 'TXAR', 'VALO', 'YPFD'];
const BONOS = ['AL30D', 'GD30D', 'GD35D', 'AE38D', 'GD41D'];
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Content-Type': 'application/json',
};
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: CORS });

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/wa\/(apertura|cierre)$/);
    if (!m || request.method !== 'GET') return json({ error: 'Ruta no encontrada' }, 404);
    try {
      const u = await usuarioDelToken(request);
      if (!u) return json({ error: 'No autenticado' }, 401);
      if (!CREADORES.includes(u.email)) return json({ error: 'Solo para creadores' }, 403);
      return json(await resumen(env, m[1], url.searchParams.get('regenerar') === '1'));
    } catch (e) {
      return json({ error: e.message }, 500);
    }
  },

  async scheduled(event, env, ctx) {
    const momento = event.cron.startsWith('15 13') ? 'apertura' : 'cierre';
    ctx.waitUntil(resumen(env, momento, true).then(r => avisarPorMail(env, r)));
  },
};

// ─── Resumen del día ─────────────────────────────────────────────────────────

async function resumen(env, momento, regenerar) {
  const hoy = hoyART();
  const clave = `wa:${hoy.iso}:${momento}`;
  if (!regenerar && env.WA_KV) {
    const guardado = await env.WA_KV.get(clave, 'json');
    if (guardado) return guardado;
  }
  const datos = await juntarDatos(env, momento, hoy);
  const ia = await redactar(env, momento, datos);
  const r = {
    momento,
    fecha: hoy.iso,
    fechaLarga: hoy.larga,
    generado: new Date().toISOString(),
    ia: !!ia,
    intro: ia || introPlantilla(momento, datos),
    datos,
  };
  r.texto = textoWhatsApp(r, env.SITE_URL);
  if (env.WA_KV) {
    // tolerante: si el cupo diario de KV se agotó, el resumen sale igual (ver mercados)
    try { await env.WA_KV.put(clave, JSON.stringify(r), { expirationTtl: 3 * 86400 }); } catch (e) { /* sin guardar */ }
  }
  return r;
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
      .sort((a, b) => b.volume - a.volume).slice(0, 8).map(c => ({ n: c.symbol, c: c.change }));
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

  const noticias = [...(pulso.argentina.noticias || []).slice(0, 3), ...(pulso.mundo.noticias || []).slice(0, 2)]
    .map(n => ({ t: n.titulo, f: n.fuente, r: (n.resumen || '').slice(0, 200) }));

  return { argentina, bonos, mundo, panel, cedears, agenda, noticias };
}

// ─── Redacción con IA (Gemini, cupo gratis) ─────────────────────────────────

async function redactar(env, momento, datos) {
  if (!env.GEMINI_KEY) return null;
  const consigna = momento === 'apertura'
    ? 'Escribí la introducción del resumen de la MAÑANA, antes de que abra el mercado argentino (11 h). Contá en qué quedó el último cierre y qué hay que mirar hoy (agenda y titulares).'
    : 'Escribí la introducción del resumen de CIERRE del día. Contá qué pasó hoy en el mercado argentino y en el mundo, y por qué, apoyándote en los titulares.';
  const prompt = `Sos el redactor de "Manfredi Investment", una comunidad de inversores argentinos en WhatsApp.
${consigna}

Reglas estrictas:
- Entre 45 y 75 palabras, 2 o 3 oraciones, en español rioplatense neutro y profesional (sin voseo exagerado, sin emojis, sin hashtags, sin saludos).
- Usá SOLO números que aparezcan en los DATOS, con formato argentino: punto de miles y coma decimal, máximo 1 decimal (ej.: $1.560,9; 753 puntos; 1,1%). Si un dato no está, no lo menciones.
- Las variaciones (campo "c") son porcentajes del día; en riesgo país "d" son puntos básicos de diferencia.
- Nada de recomendaciones de compra o venta, ni predicciones. Solo describir.
- Sin adjetivos exagerados ("explosivo", "brutal", "histórico").
- Devolvé solo el párrafo, en texto plano.

DATOS:
${JSON.stringify(datos)}`;

  for (const modelo of MODELOS) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-goog-api-key': env.GEMINI_KEY },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.4, maxOutputTokens: 2048 },
        }),
        signal: AbortSignal.timeout(25000),
      });
      if (!r.ok) continue; // sin cupo (429) u otro error: prueba el siguiente modelo
      const d = await r.json();
      const txt = ((d.candidates?.[0]?.content?.parts || []).filter(p => !p.thought).map(p => p.text || '').join('') || '').replace(/\s+/g, ' ').trim();
      if (txt.length < 80 || txt.length > 700) continue;
      if (!numerosValidos(txt, datos)) continue; // inventó o redondeó mal un número
      return txt;
    } catch (e) { /* siguiente modelo */ }
  }
  return null;
}

// Cada número del texto de la IA tiene que salir de los datos (o de los titulares).
function numerosValidos(txt, datos) {
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
  return (txt.match(/\d+(?:[.,]\d+)*/g) || []).every(n => +sinSep(n) < 10 || ok.has(sinSep(n)));
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

// ─── Formato WhatsApp (*negrita*, _cursiva_) ────────────────────────────────

function num(v, dec) {
  const d = dec != null ? dec : Math.abs(v) >= 10000 ? 0 : 2;
  return v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
}
// Todo se decide sobre el valor ya redondeado a 1 decimal (−0,04% es "0,0%", sin flecha).
const r1 = c => Math.round(c * 10) / 10;
function pct(c, signo = true) {
  const s = Math.abs(r1(c)).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
  return signo ? (r1(c) > 0 ? '+' : r1(c) < 0 ? '−' : '') + s : s;
}
function verbo(c) { return r1(c) > 0 ? 'subió' : r1(c) < 0 ? 'bajó' : 'quedó estable,'; }
function flecha(c) { return r1(c) > 0 ? '▲' : r1(c) < 0 ? '▼' : '='; }
function precio(f) {
  if (f.u === 'pb') return num(f.v, 0) + ' pb';
  return (f.u === '$' ? '$' : f.u ? f.u + ' ' : '') + num(f.v);
}
function variacion(f) {
  if (f.d != null) return `${flecha(f.d)} ${f.d > 0 ? '+' : f.d < 0 ? '−' : ''}${Math.abs(f.d)} pb`;
  return f.c != null ? `${flecha(f.c)} ${pct(f.c)}` : '';
}
function linea(f) { return `${f.n}: *${precio(f)}* ${variacion(f)}`.trim(); }

function textoWhatsApp(r, site) {
  const d = r.datos;
  const titulo = r.momento === 'apertura' ? 'ANTES DE LA APERTURA' : 'CIERRE DEL MERCADO';
  const out = [`*MANFREDI · ${titulo}*`, `_${r.fechaLarga.charAt(0).toUpperCase() + r.fechaLarga.slice(1)}_`, '', r.intro, ''];
  out.push('*🇦🇷 Argentina*', ...d.argentina.map(linea));
  if (d.bonos.length) out.push('', '*Bonos en dólares*', d.bonos.map(b => `${b.n} ${flecha(b.c)} ${pct(b.c)}`).join(' · '));
  if (d.panel) {
    out.push('', '*Panel líder*',
      ...(d.panel.suben.length ? ['Suben: ' + d.panel.suben.map(a => `${a.n} ${pct(a.c)}`).join(' · ')] : []),
      ...(d.panel.bajan.length ? ['Bajan: ' + d.panel.bajan.map(a => `${a.n} ${pct(a.c)}`).join(' · ')] : []));
  }
  if (d.cedears) out.push('', '*CEDEARs más operados*', d.cedears.map(c => `${c.n} ${pct(c.c)}`).join(' · '));
  out.push('', r.momento === 'apertura' ? '*🌎 Mundo · último cierre*' : '*🌎 Mundo*', ...d.mundo.map(linea));
  if (d.agenda.eventos.length) out.push('', `*📅 ${d.agenda.titulo}*`, ...d.agenda.eventos.map(e => `• ${e.t}`));
  if (d.noticias.length) out.push('', '*📰 Titulares*', ...d.noticias.map(n => `• ${n.t} _(${n.f})_`));
  out.push('', `Cotizaciones en vivo, calendario y noticias: ${site.replace(/^https?:\/\//, '')}`);
  return out.join('\n');
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
    return ok ? { email: String(p.email).toLowerCase() } : null;
  } catch (e) { return null; }
}
