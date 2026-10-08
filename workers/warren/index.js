// workers/warren/index.js
// Backend de Warren IA como Cloudflare Worker (antes vivia en
// netlify/functions/warren.js, que en realidad nunca corria en produccion --
// el sitio se sirve por Cloudflare Pages, no Netlify. Ver .claude/plans/
// stateful-roaming-ladybug.md para el contexto completo del rediseño).
//
// Oct-2026 (feat/warren-institucional):
// - La identidad sale del ID token de Firebase (header Authorization), nunca
//   de un email del body, y el chat es solo para socios. Antes cualquiera podia
//   mandar cualquier email (incluido el del admin) y su propio prompt.
// - El prompt de sistema vive en prompt.js, no viaja desde el navegador.
// - POST /chat responde en streaming (SSE): pasos ("Leyendo el informe de
//   NVDA…"), el texto a medida que se escribe y un evento final.
// - Tope duro de costo: USD 0,10 por consulta (USD 10 cada 100). Todo corre en
//   Haiku 5.5 y cada llamada se dimensiona con lo que queda de presupuesto.

import { WARREN_SYSTEM } from './prompt.js';

const ADMIN_EMAILS = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
const SITE_URL = 'https://manfredinvestment.com';
const MEMBERSHIPS_BASE = 'https://manfredi-memberships.nachito2502.workers.dev';
const MERCADOS_BASE = 'https://manfredi-mercados.nachito2502.workers.dev';
const NOTICIAS_BASE = 'https://manfredi-noticias.nachito2502.workers.dev';
const CALENDARIO_BASE = 'https://manfredi-calendario.nachito2502.workers.dev';

// ─── Modelo y presupuesto ───────────────────────────────────────────────────
// Haiku 5.5: USD 0,10 / 0,50 por millon de tokens (entrada / salida) mientras
// el prompt tenga 100K tokens o menos; USD 0,50 / 2,50 por encima. Cada
// busqueda web cuesta USD 0,01. Opus y Sonnet no entran en USD 0,10 para un
// informe de ~10.000 palabras, por eso no se usan.
const MODEL = 'claude-haiku-5-5';
const PRICE = { inLow: 0.10, outLow: 0.50, inHigh: 0.50, outHigh: 2.50, tierTokens: 100000, search: 0.01 };
const BUDGET_USD = 0.09;            // tope por consulta; deja margen hasta USD 0,10 por errores de estimacion
const SEARCH_INPUT_RESERVE = 20000; // tokens de entrada que puede sumar cada resultado de busqueda
const PROMPT_GUARD = 88000;         // con mas prompt que esto ya no se buscan datos: se escribe
const MODES = {
    rapida:   { effort: 'low',    maxIter: 4,  maxOut: 6000,  minFinal: 800,  searchesPerCall: 1, maxSearches: 2 },
    profunda: { effort: 'medium', maxIter: 10, maxOut: 32000, minFinal: 5000, searchesPerCall: 2, maxSearches: 4 }
};

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
};
const JSON_HEADERS = { ...CORS_HEADERS, 'Content-Type': 'application/json' };
const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: JSON_HEADERS });

// ─── Identidad (mismo esquema que workers/memberships) ──────────────────────
let _jwksCache = { keys: null, exp: 0 };
async function firebaseKeys() {
    if (_jwksCache.keys && Date.now() < _jwksCache.exp) return _jwksCache.keys;
    const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
    const { keys } = await r.json();
    const m = /max-age=(\d+)/.exec(r.headers.get('cache-control') || '');
    _jwksCache = { keys, exp: Date.now() + (m ? +m[1] : 3600) * 1000 };
    return keys;
}
function b64urlBytes(s) {
    s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
    return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
// Devuelve el email verificado del ID token de Firebase, o null.
async function emailDelToken(request) {
    const auth = request.headers.get('Authorization') || '';
    const token = auth.startsWith('Bearer ') ? auth.slice(7) : '';
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    try {
        const header = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[0])));
        const p = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[1])));
        const now = Math.floor(Date.now() / 1000);
        if (header.alg !== 'RS256' || p.aud !== FIREBASE_PROJECT || p.iss !== 'https://securetoken.google.com/' + FIREBASE_PROJECT) return null;
        if (!p.exp || p.exp < now || !p.email || p.email_verified === false) return null;
        const jwk = (await firebaseKeys()).find(k => k.kid === header.kid);
        if (!jwk) return null;
        const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
        const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
        return ok ? String(p.email).toLowerCase() : null;
    } catch (e) { return null; }
}

async function isMemberEmail(env, email) {
    try {
        const res = await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/verificar-membresia?email=${encodeURIComponent(email)}`);
        const data = await res.json();
        return !!data.miembro;
    } catch (e) {
        console.error('[warren] verificar-membresia fallo, asumimos no-socio:', e && e.message);
        return false;
    }
}

// ─── Historial de conversaciones (barra estilo ChatGPT/Gemini, solo Socios) ─
// Guardado en WARREN_KV, dos claves por usuario:
//   convos:{email}      -> array liviano [{id,title,updatedAt}], para la lista
//   convo:{email}:{id}  -> conversacion completa {id,title,createdAt,updatedAt,messages}
// El titulo se autogenera truncando el primer mensaje del usuario -- sin
// llamada extra a un LLM, cero costo de API por el simple hecho de guardar.
// El email sale del token: antes venia en la URL y cualquiera podia leer las
// conversaciones de otro.
const CONVO_LIST_CAP = 100;   // conversaciones guardadas por usuario, las mas viejas se descartan
const CONVO_MSG_CAP = 60;     // mensajes por conversacion guardada
const CONVO_TITLE_LEN = 60;

function convoAutoTitle(messages) {
    const firstUser = (messages || []).find(m => m.role === 'user' && typeof m.content === 'string');
    if (!firstUser) return 'Conversación';
    const text = (firstUser.display || firstUser.content).trim();
    return text.length > CONVO_TITLE_LEN ? text.slice(0, CONVO_TITLE_LEN) + '…' : text;
}

async function handleConversationsList(email, env) {
    const listRaw = await env.WARREN_KV.get('convos:' + email);
    return json({ conversations: listRaw ? JSON.parse(listRaw) : [] });
}

async function handleConversationGet(request, email, env) {
    const id = new URL(request.url).searchParams.get('id') || '';
    if (!id) return json({ error: 'id requerido' }, 400);
    const raw = await env.WARREN_KV.get('convo:' + email + ':' + id);
    if (!raw) return json({ error: 'No encontrada' }, 404);
    return new Response(raw, { headers: JSON_HEADERS });
}

async function handleConversationSave(request, email, env) {
    const body = await request.json();
    const messages = body.messages;
    if (!Array.isArray(messages) || !messages.length) return json({ error: 'messages requerido' }, 400);
    const now = Date.now();
    let id = body.id || null;
    let createdAt = now, existingTitle = null;
    if (id) {
        const existingRaw = await env.WARREN_KV.get('convo:' + email + ':' + id);
        if (existingRaw) {
            const existing = JSON.parse(existingRaw);
            createdAt = existing.createdAt || now;
            existingTitle = existing.title || null;
        } else {
            id = null; // id vencido/de otro usuario -- se trata como conversacion nueva
        }
    }
    if (!id) id = now.toString(36) + Math.random().toString(36).slice(2, 8);
    const title = body.title || existingTitle || convoAutoTitle(messages);
    const convo = { id, title, createdAt, updatedAt: now, messages: messages.slice(-CONVO_MSG_CAP) };
    await env.WARREN_KV.put('convo:' + email + ':' + id, JSON.stringify(convo));

    const listRaw = await env.WARREN_KV.get('convos:' + email);
    let list = listRaw ? JSON.parse(listRaw) : [];
    list = list.filter(c => c.id !== id);
    list.unshift({ id, title, updatedAt: now });
    if (list.length > CONVO_LIST_CAP) {
        const dropped = list.slice(CONVO_LIST_CAP);
        list = list.slice(0, CONVO_LIST_CAP);
        await Promise.all(dropped.map(c => env.WARREN_KV.delete('convo:' + email + ':' + c.id)));
    }
    await env.WARREN_KV.put('convos:' + email, JSON.stringify(list));
    return json({ id, title });
}

async function handleConversationDelete(request, email, env) {
    const body = await request.json();
    const id = body.id;
    if (!id) return json({ error: 'id requerido' }, 400);
    await env.WARREN_KV.delete('convo:' + email + ':' + id);
    const listRaw = await env.WARREN_KV.get('convos:' + email);
    const list = (listRaw ? JSON.parse(listRaw) : []).filter(c => c.id !== id);
    await env.WARREN_KV.put('convos:' + email, JSON.stringify(list));
    return json({ ok: true });
}

// ─── Modo de respuesta ──────────────────────────────────────────────────────
// Sin llamada extra a un clasificador. El frontend puede forzar el modo (los
// botones de "análisis" mandan profunda); si no, se decide por el texto.
const DEEP_RE = /(anali[sz]|dcf|valuaci[oó]n|valu[aá]|fair value|precio objetivo|comparables|m[uú]ltiplos|tesis|compar[aá]|\bvs\.?\b|sector|industria|cartera|portafolio|portfolio|earnings|balance|resultados|riesgos|red flags?|impacta|impacto|escenario|macro)/i;
function chooseMode(text, requested) {
    if (requested === 'rapida' || requested === 'profunda') return requested;
    if (!text) return 'rapida';
    if (text.length > 260 || DEEP_RE.test(text)) return 'profunda';
    return 'rapida';
}

// ─── Herramientas ───────────────────────────────────────────────────────────
// La lista es fija por modo (solo cambia max_uses de la busqueda) para que el
// prefijo tools + system quede en cache entre consultas.
function buildTools(mode) {
    return [
        {
            name: 'get_manfredi_report',
            description: 'Devuelve el texto completo de un informe de equity research propio de Manfredi Investment (tesis, estados contables, DCF, comparables, escenarios, fair value y riesgos). Usala primero cuando el ticker esta en la cobertura de Manfredi.',
            input_schema: { type: 'object', properties: { ticker: { type: 'string', description: 'Ticker en mayusculas, ej. NVDA, BRK.B' } }, required: ['ticker'] }
        },
        {
            name: 'get_market_data',
            description: 'Precio en vivo, variacion del dia y (si aplica) ROE, P/E, dividend yield, sector y pais de un ticker trackeado por Manfredi Investment (acciones y CEDEARs argentinos, acciones y ADRs de EE.UU., bonos soberanos, cripto). Si el ticker existe en mas de una categoria devuelve todas con su moneda.',
            input_schema: { type: 'object', properties: { symbol: { type: 'string', description: 'Ticker en mayusculas, ej. AAPL, GGAL, MELI, AL30' } }, required: ['symbol'] }
        },
        {
            name: 'get_price_history',
            description: 'Cierres diarios de un ticker trackeado (misma cobertura que get_market_data), hasta 180 ruedas. Para tendencia, variacion en una ventana o un grafico de evolucion.',
            input_schema: { type: 'object', properties: { symbol: { type: 'string' }, days: { type: 'integer', description: '5 a 180. Default 60.' } }, required: ['symbol'] }
        },
        {
            name: 'get_calendar',
            description: 'Agenda de la semana segun Manfredi Investment: datos macro de Argentina y EE.UU., presentaciones de resultados y fechas de dividendos de las empresas cubiertas. Usala para catalizadores con fecha.',
            input_schema: { type: 'object', properties: {} }
        },
        {
            name: 'get_news',
            description: 'Titulares recientes de mercado argentino y Wall Street (Ambito, Cronista, Bloomberg Linea, Yahoo Finance, Investing.com, Seeking Alpha, The Economist). Podes filtrar por palabra clave.',
            input_schema: { type: 'object', properties: { query: { type: 'string', description: 'Palabra clave opcional (empresa, "tasas", "dolar")' } } }
        },
        {
            name: 'portfolio_risk',
            description: 'Calcula el riesgo de una cartera con un ano de precios diarios: volatilidad anual, beta contra el S&P 500, peor caida, peor mes, correlaciones entre posiciones y concentracion. Pasale todas las posiciones con su peso en %; el efectivo va como symbol "ARS" o "USD".',
            input_schema: {
                type: 'object',
                properties: {
                    positions: {
                        type: 'array',
                        items: { type: 'object', properties: { symbol: { type: 'string' }, weight: { type: 'number', description: 'Peso en % de la cartera' }, moneda: { type: 'string', enum: ['USD', 'ARS'], description: 'Moneda en la que el usuario tiene la posicion, si la dice' } }, required: ['symbol', 'weight'] }
                    }
                },
                required: ['positions']
            }
        },
        {
            // Haiku 5.5 no admite la variante _20260209 (filtrado dinamico); va la basica.
            type: 'web_search_20250305',
            name: 'web_search',
            max_uses: MODES[mode].searchesPerCall
        }
    ];
}

const STEP_LABELS = {
    get_manfredi_report: i => 'Leyendo el informe de Manfredi' + (i && i.ticker ? ' de ' + String(i.ticker).toUpperCase() : ''),
    get_market_data: i => 'Trayendo precio y métricas' + (i && i.symbol ? ' de ' + String(i.symbol).toUpperCase() : ''),
    get_price_history: i => 'Bajando el histórico' + (i && i.symbol ? ' de ' + String(i.symbol).toUpperCase() : ''),
    get_calendar: () => 'Revisando la agenda de la semana',
    get_news: i => 'Leyendo noticias' + (i && i.query ? ' sobre ' + i.query : ''),
    portfolio_risk: () => 'Calculando volatilidad, beta y correlaciones',
    web_search: i => 'Buscando' + (i && i.query ? ': ' + String(i.query).slice(0, 70) : ' en la web')
};

async function getJson(binding, url, timeout = 9000) {
    const res = await binding.fetch(url, { signal: AbortSignal.timeout(timeout) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
}

// /mercados se pide una vez por consulta aunque lo usen varias herramientas.
function mercadosLoader(env) {
    let p = null;
    return () => (p = p || getJson(env.MERCADOS, MERCADOS_BASE + '/mercados'));
}
function findInMercados(data, symbol) {
    const out = [];
    const categorias = (data && data.categorias) || {};
    for (const cat of Object.keys(categorias)) {
        const block = categorias[cat] || {};
        const item = (block.items || []).find(it => it.symbol === symbol);
        if (item) out.push({ category: cat, currency: block.currency, price: item.price, changePct: item.change, name: item.name });
    }
    return out;
}

async function toolGetMarketData(input, ctx) {
    const symbol = String((input && input.symbol) || '').toUpperCase().trim();
    if (!symbol) return { error: 'symbol requerido' };
    let data;
    try { data = await ctx.mercados(); } catch (e) { return { error: 'No se pudo conectar con la fuente de datos de mercado.' }; }
    const matches = findInMercados(data, symbol);
    if (!matches.length) return { error: `${symbol} no esta trackeado en los datos de Manfredi Investment. Si hace falta, usa web_search o deci que no lo podes confirmar.` };
    let fundamentals = null;
    try { fundamentals = await getJson(ctx.env.MERCADOS, MERCADOS_BASE + '/fundamentals?symbol=' + encodeURIComponent(symbol)); } catch (e) { /* best-effort */ }
    return { symbol, actualizado: data.updated, matches, fundamentals };
}

async function toolGetPriceHistory(input, ctx) {
    const symbol = String((input && input.symbol) || '').toUpperCase().trim();
    if (!symbol) return { error: 'symbol requerido' };
    const days = Math.min(180, Math.max(5, parseInt(input && input.days, 10) || 60));
    let data;
    try { data = await ctx.mercados(); } catch (e) { return { error: 'No se pudo conectar con la fuente de datos de mercado.' }; }
    const m = findInMercados(data, symbol)[0];
    if (!m) return { error: `${symbol} no esta trackeado en los datos de Manfredi Investment.` };
    try {
        const h = await getJson(ctx.env.MERCADOS, MERCADOS_BASE + '/historico?category=' + encodeURIComponent(m.category) + '&symbol=' + encodeURIComponent(symbol) + '&n=' + days);
        return { symbol, category: m.category, moneda: m.currency, days, closes: h.closes, min: h.min, max: h.max };
    } catch (e) { return { error: 'No se pudo obtener el historico.' }; }
}

async function toolGetNews(input, ctx) {
    const query = String((input && input.query) || '').toLowerCase().trim();
    let data;
    try { data = await getJson(ctx.env.NOTICIAS, NOTICIAS_BASE + '/noticias'); } catch (e) { return { error: 'No se pudieron obtener noticias.' }; }
    let items = [].concat(data.argentina || [], data.wallstreet || []);
    if (query) items = items.filter(it => ((it.titulo || '') + ' ' + (it.resumen || '')).toLowerCase().includes(query));
    return { actualizado: data.updated, items: items.slice(0, 8) };
}

async function toolGetCalendar(input, ctx) {
    const pick = d => (d && d.dias || []).map(x => ({ dia: x.nombre + ' ' + x.fecha, eventos: (x.eventos || []).map(e => ({ tipo: e.tipo, titulo: e.titulo, detalle: e.descripcion })) })).filter(x => x.eventos.length);
    const [eco, earn, div] = await Promise.all(['/calendario', '/earnings', '/dividends'].map(p =>
        getJson(ctx.env.CALENDARIO, CALENDARIO_BASE + p).catch(() => null)));
    if (!eco && !earn && !div) return { error: 'No se pudo leer el calendario.' };
    return {
        semana: (eco || earn || div).semana,
        macro: pick(eco), resultados: pick(earn), dividendos: pick(div),
        nota: 'Solo cubre esta semana. Para fechas posteriores confirmalas con web_search.'
    };
}

// Catalogo de informes: una vez por isolate (cambia cuando se publica un informe).
let _catalogo = { data: null, exp: 0 };
async function catalogo() {
    if (_catalogo.data && Date.now() < _catalogo.exp) return _catalogo.data;
    const r = await fetch(SITE_URL + '/informes/catalogo.json', { signal: AbortSignal.timeout(8000) });
    if (!r.ok) throw new Error('catalogo HTTP ' + r.status);
    _catalogo = { data: await r.json(), exp: Date.now() + 30 * 60 * 1000 };
    return _catalogo.data;
}

// HTML del informe -> texto con tablas en formato "a | b | c".
const REPORT_CHAR_CAP = 36000; // total por vuelta, repartido entre los informes pedidos juntos
function htmlToText(html) {
    let s = html
        .replace(/<(script|style|noscript|svg|nav|footer)[\s\S]*?<\/\1>/gi, ' ')
        .replace(/<!--[\s\S]*?-->/g, ' ');
    const main = /<body[\s\S]*?>([\s\S]*)<\/body>/i.exec(s);
    if (main) s = main[1];
    s = s
        .replace(/<\/(td|th)>\s*/gi, ' | ')
        .replace(/<\/tr>/gi, '\n')
        .replace(/<(br|\/p|\/div|\/li|\/h[1-6]|\/section|\/table|\/blockquote)[^>]*>/gi, '\n')
        .replace(/<h([1-6])[^>]*>/gi, '\n## ')
        .replace(/<li[^>]*>/gi, '- ')
        .replace(/<[^>]+>/g, ' ')
        .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
        .replace(/&mdash;/g, '—').replace(/&ndash;/g, '–').replace(/&[a-z]+;/g, ' ')
        .replace(/[ \t]+/g, ' ')
        .replace(/ *\n */g, '\n')
        .replace(/\n{3,}/g, '\n\n');
    return s.trim();
}

// Version compacta para el modelo: por seccion, el titulo, todas las tablas
// (ahi estan los numeros) y el comienzo de la prosa. Un informe entero son
// ~60.000 caracteres; con varios en la misma consulta el prompt pasaba los
// 100K tokens y el precio por token se quintuplicaba.
function compactReport(text, cap) {
    for (const prosePerSection of [700, 300, 120]) {
        const s = compactWith(text, prosePerSection);
        if (s.length <= cap) return s;
    }
    return compactWith(text, 0).slice(0, cap);
}
function compactWith(text, prosePerSection) {
    const out = [];
    for (const sec of text.split(/\n(?=## )/)) {
        let prose = 0;
        for (const line of sec.split('\n')) {
            const isTable = line.includes(' | ');
            if (line.startsWith('## ') || isTable) { out.push(line); continue; }
            if (prose < prosePerSection && line.trim()) {
                const room = prosePerSection - prose;
                out.push(line.length > room ? line.slice(0, room) + '…' : line);
                prose += line.length;
            }
        }
    }
    return out.join('\n');
}

async function toolGetManfrediReport(input, ctx) {
    const ticker = String((input && input.ticker) || '').toUpperCase().trim();
    let cat;
    try { cat = await catalogo(); } catch (e) { return { error: 'No se pudo leer el catalogo de informes.' }; }
    const entry = cat[ticker];
    if (!entry) return { error: `Manfredi Investment no tiene informe de ${ticker}.`, cobertura: Object.keys(cat) };
    const path = String(entry.href || '').replace(/\.html$/, '');
    const url = SITE_URL + '/' + path.replace(/^\//, '');
    try {
        // Pasar el HTML a texto gasta CPU (el plan de Workers da muy poca por
        // pedido): se hace una vez por version del informe y queda en KV.
        const cap = Math.max(14000, Math.floor(REPORT_CHAR_CAP / Math.max(1, ctx.reportsInTurn || 1)));
        const kvKey = 'informe_txt_v1:' + ticker + ':' + (entry.f || '') + ':' + cap;
        let texto = await ctx.env.WARREN_KV.get(kvKey);
        if (!texto) {
            const r = await fetch(url, { signal: AbortSignal.timeout(10000) });
            if (!r.ok) throw new Error('HTTP ' + r.status);
            texto = compactReport(htmlToText(await r.text()), cap);
            try { await ctx.env.WARREN_KV.put(kvKey, texto, { expirationTtl: 60 * 60 * 24 * 60 }); } catch (e) { /* sin cupo de escrituras: sigue sin cache */ }
        }
        return { ticker, url, fecha_informe: entry.f, trimestre: entry.q, tesis: entry.tesis, nota: 'Version resumida del informe: tablas completas y el comienzo de cada seccion.', texto };
    } catch (e) {
        return { error: 'No se pudo leer el informe de ' + ticker + '.', url };
    }
}

// ─── Riesgo de cartera ──────────────────────────────────────────────────────
// Un ano de cierres diarios por activo (/serie tf=1A, cache en memoria del
// worker de mercados, no gasta KV). Tope de activos por los subrequests del
// plan de Workers.
const RISK_MAX_ASSETS = 14;
const dayKey = t => new Date((t > 1e12 ? t : t * 1000)).toISOString().slice(0, 10);
function returnsByDay(points) {
    const out = new Map();
    for (let i = 1; i < points.length; i++) {
        const a = points[i - 1].c, b = points[i].c;
        if (a > 0 && b > 0) out.set(dayKey(points[i].t), b / a - 1);
    }
    return out;
}
const mean = a => a.reduce((s, x) => s + x, 0) / (a.length || 1);
function cov(a, b) { const ma = mean(a), mb = mean(b); let s = 0; for (let i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb); return s / ((a.length - 1) || 1); }
const sd = a => Math.sqrt(cov(a, a));
function maxDrawdown(rets) {
    let v = 1, peak = 1, dd = 0;
    for (const r of rets) { v *= 1 + r; peak = Math.max(peak, v); dd = Math.min(dd, v / peak - 1); }
    return dd;
}
function worstWindow(rets, n) {
    let worst = 0;
    for (let i = 0; i + n <= rets.length; i++) {
        let v = 1; for (let j = i; j < i + n; j++) v *= 1 + rets[j];
        worst = Math.min(worst, v - 1);
    }
    return worst;
}
const pct = (x, d = 1) => (x == null || !isFinite(x)) ? null : +(x * 100).toFixed(d);

async function toolPortfolioRisk(input, ctx) {
    const raw = Array.isArray(input && input.positions) ? input.positions : [];
    const positions = raw.map(p => ({ symbol: String(p.symbol || '').toUpperCase().trim(), weight: Number(p.weight) || 0, moneda: p.moneda === 'ARS' || p.moneda === 'USD' ? p.moneda : null })).filter(p => p.symbol && p.weight > 0);
    if (!positions.length) return { error: 'Sin posiciones.' };
    const totalW = positions.reduce((s, p) => s + p.weight, 0);
    positions.forEach(p => { p.weight = p.weight / totalW; });
    const cash = positions.filter(p => p.symbol === 'ARS' || p.symbol === 'USD');
    const cashWeight = cash.reduce((s, p) => s + p.weight, 0);

    let mdata;
    try { mdata = await ctx.mercados(); } catch (e) { return { error: 'No se pudo conectar con la fuente de datos de mercado.' }; }
    const risky = positions.filter(p => !cash.includes(p)).sort((a, b) => b.weight - a.weight);
    const evaluated = risky.slice(0, RISK_MAX_ASSETS);
    const sinDatos = [];
    const series = await Promise.all(evaluated.map(async p => {
        // Un mismo ticker puede estar como CEDEAR (ARS) y como accion de EE.UU.
        // (USD): se usa la moneda de la posicion; si no se sabe, la de EE.UU.
        const all = findInMercados(mdata, p.symbol);
        const m = (p.moneda && all.find(x => x.currency === p.moneda))
            || all.find(x => x.category === 'usa_stocks' || x.category === 'usa_adrs') || all[0];
        if (!m) { sinDatos.push(p.symbol); return null; }
        try {
            const s = await getJson(ctx.env.MERCADOS, MERCADOS_BASE + '/serie?category=' + encodeURIComponent(m.category) + '&symbol=' + encodeURIComponent(p.symbol) + '&tf=1A', 12000);
            return { ...p, category: m.category, moneda: m.currency, rets: returnsByDay(s.points || []) };
        } catch (e) { sinDatos.push(p.symbol); return null; }
    }));
    let bench;
    try { bench = returnsByDay((await getJson(ctx.env.MERCADOS, MERCADOS_BASE + '/serie?category=indices&symbol=SP500&tf=1A', 12000)).points || []); }
    catch (e) { bench = new Map(); }

    const assets = series.filter(Boolean).filter(a => a.rets.size > 40);
    if (!assets.length) return { error: 'No hay historico suficiente para calcular el riesgo.', sin_datos: sinDatos };

    // Dias comunes a todos los activos (y al S&P 500 si esta).
    let days = [...assets[0].rets.keys()].filter(d => assets.every(a => a.rets.has(d)));
    const daysWithBench = days.filter(d => bench.has(d));
    if (daysWithBench.length > 40) days = daysWithBench;
    days.sort();
    const wSum = assets.reduce((s, a) => s + a.weight, 0);
    const port = days.map(d => assets.reduce((s, a) => s + a.rets.get(d) * a.weight / wSum, 0));
    const b = bench.size ? days.map(d => bench.get(d) || 0) : null;

    const porActivo = assets.map(a => {
        const r = days.map(d => a.rets.get(d));
        const tot = r.reduce((v, x) => v * (1 + x), 1) - 1;
        return {
            symbol: a.symbol, peso_pct: pct(a.weight), moneda: a.moneda, categoria: a.category,
            retorno_1a_pct: pct(tot), volatilidad_anual_pct: pct(sd(r) * Math.sqrt(252)),
            beta_sp500: b ? +(cov(r, b) / cov(b, b)).toFixed(2) : null,
            peor_caida_pct: pct(maxDrawdown(r))
        };
    });
    const pares = [];
    for (let i = 0; i < assets.length; i++) for (let j = i + 1; j < assets.length; j++) {
        const ri = days.map(d => assets[i].rets.get(d)), rj = days.map(d => assets[j].rets.get(d));
        const c = cov(ri, rj) / (sd(ri) * sd(rj));
        if (isFinite(c)) pares.push({ par: assets[i].symbol + ' / ' + assets[j].symbol, correlacion: +c.toFixed(2) });
    }
    pares.sort((x, y) => y.correlacion - x.correlacion);
    const hhi = positions.reduce((s, p) => s + p.weight * p.weight, 0);

    return {
        ruedas: days.length, desde: days[0], hasta: days[days.length - 1],
        cartera_sin_efectivo: {
            volatilidad_anual_pct: pct(sd(port) * Math.sqrt(252)),
            beta_sp500: b ? +(cov(port, b) / cov(b, b)).toFixed(2) : null,
            retorno_1a_pct: pct(port.reduce((v, x) => v * (1 + x), 1) - 1),
            sp500_retorno_1a_pct: b ? pct(b.reduce((v, x) => v * (1 + x), 1) - 1) : null,
            peor_caida_pct: pct(maxDrawdown(port)), peor_dia_pct: pct(Math.min(...port)), peor_mes_pct: pct(worstWindow(port, 21))
        },
        concentracion: {
            mayor_posicion: positions.slice().sort((x, y) => y.weight - x.weight)[0].symbol,
            mayor_peso_pct: pct(Math.max(...positions.map(p => p.weight))),
            top3_pct: pct(positions.slice().sort((x, y) => y.weight - x.weight).slice(0, 3).reduce((s, p) => s + p.weight, 0)),
            posiciones_efectivas: +(1 / hhi).toFixed(1),
            efectivo_pct: pct(cashWeight)
        },
        correlacion_media: pares.length ? +(mean(pares.map(p => p.correlacion))).toFixed(2) : null,
        pares_mas_correlacionados: pares.slice(0, 4),
        pares_menos_correlacionados: pares.slice(-3).reverse(),
        por_activo: porActivo,
        sin_datos: sinDatos.concat(risky.slice(RISK_MAX_ASSETS).map(p => p.symbol)),
        nota: 'Retornos diarios en la moneda de cotizacion de cada activo: los CEDEARs y acciones en pesos incluyen el movimiento del tipo de cambio.'
    };
}

async function executeTool(name, input, ctx) {
    if (name === 'get_manfredi_report') return toolGetManfrediReport(input, ctx);
    if (name === 'get_market_data') return toolGetMarketData(input, ctx);
    if (name === 'get_price_history') return toolGetPriceHistory(input, ctx);
    if (name === 'get_calendar') return toolGetCalendar(input, ctx);
    if (name === 'get_news') return toolGetNews(input, ctx);
    if (name === 'portfolio_risk') return toolPortfolioRisk(input, ctx);
    return { error: 'Herramienta desconocida: ' + name };
}

// ─── Costo ──────────────────────────────────────────────────────────────────
function promptTokens(u) { return (u.input_tokens || 0) + (u.cache_read_input_tokens || 0) + (u.cache_creation_input_tokens || 0); }
function priceFor(prompt) {
    return prompt > PRICE.tierTokens ? { pin: PRICE.inHigh, pout: PRICE.outHigh } : { pin: PRICE.inLow, pout: PRICE.outLow };
}
function costOf(u) {
    const { pin, pout } = priceFor(promptTokens(u));
    const searches = (u.server_tool_use && u.server_tool_use.web_search_requests) || 0;
    return ((u.input_tokens || 0) * pin
        + (u.cache_creation_input_tokens || 0) * pin * 1.25
        + (u.cache_read_input_tokens || 0) * pin * 0.1
        + (u.output_tokens || 0) * pout) / 1e6
        + searches * PRICE.search;
}

// ─── Llamada en streaming a la API de Anthropic ─────────────────────────────
// Reconstruye los bloques de contenido completos (texto, thinking con firma,
// tool_use, server_tool_use, resultados de busqueda) para devolverlos tal cual
// en la vuelta siguiente, y va pasando el texto con onText.
async function streamClaude(apiKey, body, onText, onBlock) {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
        body: JSON.stringify({ ...body, stream: true })
    });
    if (!res.ok) {
        console.error('Anthropic API error:', res.status, await res.text());
        throw new Error('anthropic_api_error');
    }
    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
    const blocks = [];
    let usage = {}, stopReason = null, buf = '';
    for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += value;
        let i;
        while ((i = buf.indexOf('\n\n')) >= 0) {
            const raw = buf.slice(0, i); buf = buf.slice(i + 2);
            const data = raw.split('\n').filter(l => l.startsWith('data:')).map(l => l.slice(5).trim()).join('');
            if (!data) continue;
            const ev = JSON.parse(data);
            if (ev.type === 'message_start') {
                usage = { ...(ev.message && ev.message.usage) };
            } else if (ev.type === 'content_block_start') {
                const b = { ...ev.content_block };
                if (b.type === 'tool_use' || b.type === 'server_tool_use') b._json = '';
                if (b.type === 'text') b.text = b.text || '';
                if (b.type === 'thinking') b.thinking = b.thinking || '';
                blocks[ev.index] = b;
            } else if (ev.type === 'content_block_delta') {
                const b = blocks[ev.index], d = ev.delta;
                if (!b) continue;
                if (d.type === 'text_delta') { b.text += d.text; onText(d.text); }
                else if (d.type === 'input_json_delta') b._json += d.partial_json;
                else if (d.type === 'thinking_delta') b.thinking += d.thinking;
                else if (d.type === 'signature_delta') b.signature = (b.signature || '') + d.signature;
                else if (d.type === 'citations_delta') (b.citations = b.citations || []).push(d.citation);
            } else if (ev.type === 'content_block_stop') {
                const b = blocks[ev.index];
                if (b && '_json' in b) {
                    try { b.input = b._json ? JSON.parse(b._json) : {}; } catch (e) { b.input = {}; }
                    delete b._json;
                }
                if (b && onBlock) onBlock(b);
            } else if (ev.type === 'message_delta') {
                stopReason = ev.delta && ev.delta.stop_reason;
                Object.assign(usage, ev.usage || {});
            } else if (ev.type === 'error') {
                console.error('Anthropic stream error:', JSON.stringify(ev.error));
                throw new Error('anthropic_stream_error');
            }
        }
    }
    return { content: blocks.filter(Boolean), stopReason, usage };
}

// Llamada sin streaming (importar PDF, salida corta).
async function callClaude(apiKey, systemPrompt, messages, maxTokens, effort) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
        body: JSON.stringify({
            model: MODEL, max_tokens: maxTokens,
            system: [{ type: 'text', text: systemPrompt, cache_control: { type: 'ephemeral' } }],
            output_config: { effort }, messages
        })
    });
    if (!response.ok) {
        console.error('Anthropic API error:', response.status, await response.text());
        throw new Error('anthropic_api_error');
    }
    return response.json();
}

function extractText(content) {
    return (content || []).filter(b => b.type === 'text').map(b => b.text).join('').trim();
}

// Contexto variable del turno (fecha, cobertura, modo): va en el mensaje del
// usuario, no en el system, para no romper el cache del prompt fijo.
function turnContext(mode, cat) {
    const hoy = new Date().toLocaleDateString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
    const cobertura = cat ? Object.keys(cat).filter(t => t !== 'FOMC').join(', ') : '(no disponible)';
    return `[Contexto del turno — Hoy: ${hoy}. Modo: ${mode === 'profunda' ? 'PROFUNDA' : 'RÁPIDA'}. Informes propios de Manfredi Investment: ${cobertura}.]\n\n`;
}

// ─── POST /chat (SSE) ───────────────────────────────────────────────────────
async function handleChat(request, env, ctxWait) {
    // DEV_TOKEN solo existe en `wrangler dev` (--var); en produccion no esta.
    const devOk = env.DEV_TOKEN && request.headers.get('Authorization') === 'Dev ' + env.DEV_TOKEN;
    const email = devOk ? ADMIN_EMAILS[0] : await emailDelToken(request);
    if (!email) return json({ error: 'login_required', message: 'Iniciá sesión para hablar con Warren.' }, 401);
    const isAdmin = ADMIN_EMAILS.includes(email);
    if (!isAdmin && !(await isMemberEmail(env, email))) {
        return json({ error: 'members_only', message: 'Warren es exclusivo para socios.' }, 403);
    }
    if (!env.ANTHROPIC_API_KEY) return json({ error: 'config', message: 'API key no configurada.' }, 500);

    let body;
    try { body = await request.json(); } catch (e) { return json({ error: 'bad_request' }, 400); }
    const history = (Array.isArray(body.messages) ? body.messages : [])
        .filter(m => m && typeof m.content === 'string' && m.content.trim())
        .slice(-16)
        .map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content.slice(0, 40000) }));
    if (!history.length || history[history.length - 1].role !== 'user') return json({ error: 'bad_request' }, 400);
    while (history[0] && history[0].role !== 'user') history.shift();

    if (!isAdmin) {
        try {
            const q = await (await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/consultas?email=${encodeURIComponent(email)}`)).json();
            if (q.consultas === 0) return json({ error: 'quota', message: 'Agotaste tus 100 consultas del mes. Se renuevan el 1 del próximo mes.' }, 429);
        } catch (e) { console.error('[warren] chequeo de consultas fallo, dejamos pasar:', e && e.message); }
    }

    const lastUser = history[history.length - 1].content;
    const mode = chooseMode(lastUser, body.mode);
    const cfg = MODES[mode];
    let cat = null;
    try { cat = await catalogo(); } catch (e) { /* sin lista de cobertura igual se puede responder */ }
    history[history.length - 1] = { role: 'user', content: turnContext(mode, cat) + lastUser };

    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    const enc = new TextEncoder();
    const send = (event, data) => writer.write(enc.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)).catch(() => {});

    const run = async () => {
        const toolCtx = { env, mercados: mercadosLoader(env) };
        const tools = buildTools(mode);
        const messages = history.slice();
        let spent = 0, lastPrompt = 0, lastOut = 0, pendingChars = JSON.stringify(messages).length + WARREN_SYSTEM.length + 6000;
        let finalText = '', usedTool = false, cutByBudget = false, steps = 0, retriedEmpty = false;
        let toolsAllowed = true, toolsClosedNoted = false, searchesUsed = 0;
        const t0 = Date.now();

        send('step', { label: mode === 'profunda' ? 'Armando el plan del análisis' : 'Pensando' });
        try {
            for (let iter = 0; iter < cfg.maxIter; iter++) {
                // Dimensionar la llamada con lo que queda de presupuesto.
                const estIn = (lastPrompt ? lastPrompt + lastOut : 0) + Math.ceil(pendingChars / 2.5);
                let maxTokens = 0;
                if (searchesUsed >= cfg.maxSearches || estIn + cfg.searchesPerCall * SEARCH_INPUT_RESERVE > PROMPT_GUARD) toolsAllowed = false;
                for (const withTools of toolsAllowed ? [true, false] : [false]) {
                    const searchIn = withTools ? cfg.searchesPerCall * SEARCH_INPUT_RESERVE : 0;
                    const { pin, pout } = priceFor(estIn + searchIn);
                    const reserve = (estIn + searchIn) * pin / 1e6 + (withTools ? cfg.searchesPerCall * PRICE.search : 0);
                    maxTokens = Math.min(cfg.maxOut, Math.floor((BUDGET_USD - spent - reserve) / pout * 1e6));
                    if (maxTokens >= cfg.minFinal || !withTools) { toolsAllowed = withTools; break; }
                }
                if (maxTokens < 600) { cutByBudget = true; break; }
                if (!toolsAllowed && maxTokens < cfg.minFinal) cutByBudget = true;
                // Sin herramientas el modelo a veces cierra diciendo que "necesita mas
                // datos": se le avisa en el mismo turno que escriba con lo que tiene.
                const lastMsg = messages[messages.length - 1];
                if (!toolsAllowed && !toolsClosedNoted && lastMsg.role === 'user' && Array.isArray(lastMsg.content)) {
                    lastMsg.content.push({ type: 'text', text: 'No hay más herramientas disponibles en esta consulta. Escribí ahora la respuesta completa con los datos que ya tenés; marcá como "sin confirmar" lo que falte.' });
                    toolsClosedNoted = true;
                }

                const reqBody = {
                    model: MODEL,
                    max_tokens: maxTokens,
                    system: [{ type: 'text', text: WARREN_SYSTEM, cache_control: { type: 'ephemeral' } }],
                    tools,
                    tool_choice: { type: toolsAllowed ? 'auto' : 'none' },
                    output_config: { effort: cfg.effort },
                    messages
                };
                if (iter > 0) send('reset', {});
                let iterText = '', pend = '';
                const flush = () => { if (pend) { send('text', { t: pend }); pend = ''; } };
                const r = await streamClaude(env.ANTHROPIC_API_KEY, reqBody, t => { iterText += t; pend += t; if (pend.length > 240) flush(); }, b => {
                    flush();
                    // Las busquedas corren del lado de Anthropic dentro de la llamada: se avisan al cerrarse el bloque.
                    if (b.type === 'server_tool_use') { steps++; send('step', { label: STEP_LABELS.web_search(b.input) }); }
                });
                spent += costOf(r.usage);
                searchesUsed += (r.usage.server_tool_use && r.usage.server_tool_use.web_search_requests) || 0;
                console.log('[warren] vuelta', iter, JSON.stringify({ stop: r.stopReason, prompt: promptTokens(r.usage), out: r.usage.output_tokens, max: maxTokens, tools: toolsAllowed, usd: +costOf(r.usage).toFixed(4) }));
                lastPrompt = promptTokens(r.usage); lastOut = r.usage.output_tokens || 0; pendingChars = 0;


                if (r.stopReason === 'refusal') { finalText = 'No puedo ayudarte con esa consulta.'; break; }
                if (r.stopReason === 'pause_turn') {
                    messages.push({ role: 'assistant', content: r.content });
                    finalText = iterText;
                    continue;
                }
                if (r.stopReason !== 'tool_use') {
                    finalText = extractText(r.content) || iterText;
                    if (r.stopReason === 'max_tokens') cutByBudget = true;
                    // Cerro sin escribir nada (pasa tras leer muchos datos): una vuelta mas solo para escribir.
                    if (!finalText.trim() && !retriedEmpty) {
                        retriedEmpty = true;
                        if (r.content.length) messages.push({ role: 'assistant', content: r.content });
                        messages.push({ role: 'user', content: 'Escribí la respuesta completa ahora, con el formato pedido y los datos que ya juntaste.' });
                        toolsAllowed = false; toolsClosedNoted = true;
                        continue;
                    }
                    break;
                }

                usedTool = true;
                messages.push({ role: 'assistant', content: r.content });
                const calls = r.content.filter(b => b.type === 'tool_use');
                calls.forEach(b => { steps++; send('step', { label: (STEP_LABELS[b.name] || (() => 'Consultando datos'))(b.input) }); });
                toolCtx.reportsInTurn = calls.filter(b => b.name === 'get_manfredi_report').length;
                const results = await Promise.all(calls.map(async b => {
                    let out;
                    try { out = await executeTool(b.name, b.input, toolCtx); } catch (e) { out = { error: 'Error interno ejecutando la herramienta.' }; }
                    const content = JSON.stringify(out);
                    pendingChars += content.length;
                    return { type: 'tool_result', tool_use_id: b.id, content, is_error: !!(out && out.error) };
                }));
                messages.push({ role: 'user', content: results });
                send('step', { label: mode === 'profunda' ? 'Cruzando los datos y escribiendo' : 'Escribiendo' });
                if (iter === cfg.maxIter - 2) toolsAllowed = false; // la ultima vuelta es para escribir
            }

            if (!finalText) finalText = 'No pude completar el análisis dentro del límite de esta consulta. Probá con una pregunta más acotada.';
            else if (cutByBudget) finalText += '\n\n*El análisis llegó al límite de extensión de una consulta. Pedime que profundice en la sección que te interese y sigo desde ahí.*';

            if (!isAdmin) {
                try {
                    await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/restar-consulta`, {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email })
                    });
                } catch (e) { console.error('[warren] restar-consulta error:', e && e.message); }
            }
            console.log('[warren] consulta', JSON.stringify({ mode, usd: +spent.toFixed(4), steps, secs: Math.round((Date.now() - t0) / 1000), cut: cutByBudget }));
            await send('done', { response: finalText, mode, usedTool, costo_usd: isAdmin ? +spent.toFixed(4) : undefined });
        } catch (err) {
            console.error('Warren worker error:', err && err.message, err && err.stack);
            await send('error', { message: 'Hubo un error inesperado. Probá de nuevo en un momento.' });
        } finally {
            try { await writer.close(); } catch (e) {}
        }
    };
    ctxWait.waitUntil(run());

    return new Response(readable, {
        headers: { ...CORS_HEADERS, 'Content-Type': 'text/event-stream; charset=utf-8', 'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no' }
    });
}

// ─── Importar tenencias desde el PDF del broker ────────────────────────────
// Recibe el TEXTO ya extraido del PDF en el navegador (el archivo nunca se
// sube: PDF.js corre client-side). Se lo pasa a Claude con un esquema de
// salida fijo y devuelve las posiciones normalizadas para la tabla de
// revision de "Tu Portafolio". Cuota: socios (y admin) ilimitado; logueado
// no-socio 3 importaciones por mes, contador en WARREN_KV (pdfparse:email:mes).
const PDF_PARSE_FREE_LIMIT = 3;
const PDF_TEXT_CAP = 24000; // caracteres; acota costo y entra cualquier resumen de tenencias

function pdfParseMonthKey() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
}

// Extrae el primer objeto JSON de la respuesta del modelo (tolera fences ```json
// y texto envolvente, aunque el system prompt pide JSON puro).
function safeJsonFromModel(s) {
    if (!s) return null;
    let t = String(s).trim();
    const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/i);
    if (fence) t = fence[1].trim();
    const first = t.indexOf('{');
    const last = t.lastIndexOf('}');
    if (first === -1 || last === -1 || last <= first) return null;
    try { return JSON.parse(t.slice(first, last + 1)); } catch (e) { return null; }
}

const PDF_PARSE_SYSTEM = `Sos un extractor de datos de resumenes de tenencias de brokers argentinos (IOL / InvertirOnline, Balanz, Cocos Capital, PPI / Portfolio Personal, Bull Market Brokers, entre otros).
Recibis el texto plano de un PDF de posiciones/tenencias. Devolves UNICAMENTE un objeto JSON valido, sin markdown ni explicaciones, con esta forma exacta:
{
  "broker": string|null,
  "moneda_resumen": "ARS"|"USD"|null,
  "positions": [
    {
      "ticker": string,             // simbolo en MAYUSCULAS (ej "AAPL", "GGAL", "AL30"). Si el PDF solo da el nombre, inferi el ticker conocido; si no podes, deja un nombre corto.
      "nombre": string|null,
      "cantidad": number,           // nominales / cantidad de papeles. Obligatorio.
      "precioCompra": number|null,  // precio promedio de compra (PPC) por unidad si figura; si el PDF solo trae valor actual, null
      "moneda": "ARS"|"USD",
      "tipo": "accion"|"cedear"|"bono"|"cripto"|"fci"|"efectivo"|"otro",
      "confianza": "alta"|"media"|"baja"
    }
  ],
  "avisos": [ string ]
}
Reglas:
- No inventes posiciones. Si el texto no parece un resumen de tenencias, devolve positions:[] y un aviso explicandolo.
- "broker": SOLO si el nombre del broker / ALyC aparece textualmente en el PDF (ej. "Balanz", "IOL", "InvertirOnline", "Cocos", "Bull Market"). Si no figura, null. No lo adivines por el formato.
- Precio de compra: usa SIEMPRE la columna de costo / PPC / "precio promedio de compra". NUNCA uses la columna de precio actual / cotizacion / ultimo, aunque multiplicada por la cantidad de justo con la columna de importe. Costo x cantidad normalmente NO coincide con el importe, y esta bien: el importe se calcula con el precio actual, no con el costo.
- Efectivo / saldo disponible: tipo "efectivo", cantidad = monto, precioCompra = 1. Si la linea de efectivo es en dolares ("DOLAR CABLE", "DOLAR MEP", "DOLAR BILLETE", "U$S", "USD", "dolares"), moneda "USD" y cantidad = monto en USD. Efectivo en pesos: moneda "ARS".
- Ignora totales, subtotales, rendimientos y datos personales de la cuenta (titular, numero de cuenta/comitente, CUIT). No los pongas en ningun campo.
- Numeros en formato argentino (1.234,56) convertilos a number JS (1234.56).
- Cuotapartes de FCI / fondos comunes: la cantidad suele tener muchos decimales y el separador se lee mal (ej. "392.187,07" podria ser 392,18707). Para cualquier fila con tipo "fci": confianza "baja" y un aviso pidiendo al usuario que verifique cantidad y precio de compra contra su resumen.
- confianza "baja" si tuviste que adivinar el ticker, la cantidad no estaba clara, o es un FCI; "media" si el renglon estaba partido en varias lineas o la columna de costo no era obvia; "alta" si la fila se leia limpia.
- "avisos": SOLO advertencias utiles para el usuario (ej. "No se detecto el nombre del broker en el PDF", "El PPC de X no figuraba", "La fila Y quedo dudosa, revisala"). NO narres tu proceso de extraccion ni menciones que ignoraste datos personales.`;

async function handlePortfolioParse(request, env) {
    const ANTHROPIC_API_KEY = env.ANTHROPIC_API_KEY;
    if (!ANTHROPIC_API_KEY) {
        return new Response(JSON.stringify({ error: 'config', message: 'API key no configurada.' }), { status: 500, headers: JSON_HEADERS });
    }

    let body;
    try { body = await request.json(); } catch (e) {
        return new Response(JSON.stringify({ error: 'bad_request', message: 'Pedido invalido.' }), { status: 400, headers: JSON_HEADERS });
    }

    const email = await emailDelToken(request);
    if (!email) {
        return new Response(JSON.stringify({ error: 'login_required', message: 'Iniciá sesión para importar un PDF.' }), { status: 401, headers: JSON_HEADERS });
    }

    let text = String(body.text || '').replace(/ /g, ' ').replace(/ /g, '').trim();
    if (text.length < 40) {
        return new Response(JSON.stringify({ error: 'empty_pdf', message: 'No se pudo leer texto del PDF. Si es un PDF escaneado (imagen), por ahora solo soportamos PDF con texto real.' }), { status: 422, headers: JSON_HEADERS });
    }
    if (text.length > PDF_TEXT_CAP) text = text.slice(0, PDF_TEXT_CAP);

    const isAdmin = ADMIN_EMAILS.includes(email);
    const member = isAdmin || await isMemberEmail(env, email);
    const month = pdfParseMonthKey();
    const quotaKey = `pdfparse:${email}:${month}`;
    let usados = 0;
    if (!member) {
        try { usados = parseInt(await env.WARREN_KV.get(quotaKey), 10) || 0; } catch (e) {}
        if (usados >= PDF_PARSE_FREE_LIMIT) {
            return new Response(JSON.stringify({
                error: 'quota_exceeded',
                message: `Usaste tus ${PDF_PARSE_FREE_LIMIT} importaciones de PDF gratuitas de este mes. Con la membresía es ilimitado.`,
                cuota: { usados, limite: PDF_PARSE_FREE_LIMIT, ilimitado: false }
            }), { status: 429, headers: JSON_HEADERS });
        }
    }

    let claudeData;
    try {
        // Haiku 5.5 alcanza para extraccion estructurada de una lista de tenencias
        // y la importacion cuesta menos de un centavo.
        claudeData = await callClaude(ANTHROPIC_API_KEY, PDF_PARSE_SYSTEM, [
            { role: 'user', content: 'Texto del PDF de tenencias:\n\n' + text }
        ], 8000, 'low');
    } catch (e) {
        return new Response(JSON.stringify({ error: 'ai_error', message: 'No se pudo procesar el PDF en este momento. Probá de nuevo en un rato.' }), { status: 502, headers: JSON_HEADERS });
    }

    const parsed = safeJsonFromModel(extractText(claudeData.content));
    if (!parsed || !Array.isArray(parsed.positions)) {
        return new Response(JSON.stringify({ error: 'parse_failed', message: 'No pude entender el formato de este PDF. Cargá las posiciones a mano o probá con otro resumen.' }), { status: 422, headers: JSON_HEADERS });
    }

    const positions = parsed.positions
        .filter(p => p && p.ticker && Number(p.cantidad) > 0)
        .map(p => {
            const moneda = p.moneda === 'USD' ? 'USD' : 'ARS';
            const tipo = ['accion', 'cedear', 'bono', 'cripto', 'fci', 'efectivo', 'otro'].includes(p.tipo) ? p.tipo : 'otro';
            let ticker = String(p.ticker).toUpperCase().trim().slice(0, 20);
            if (tipo === 'efectivo') ticker = moneda; // "ARS"/"USD" en vez de "PESOS"/"DOLAR CABLE"
            return {
                ticker,
                nombre: p.nombre ? String(p.nombre).slice(0, 80) : null,
                cantidad: Number(p.cantidad),
                precioCompra: tipo === 'efectivo' ? 1 : ((p.precioCompra != null && Number(p.precioCompra) > 0) ? Number(p.precioCompra) : null),
                moneda,
                tipo,
                confianza: ['alta', 'media', 'baja'].includes(p.confianza) ? p.confianza : 'media'
            };
        })
        .slice(0, 100);

    if (!member) {
        usados += 1;
        // TTL ~40 dias: la clave del mes se limpia sola despues del reset.
        try { await env.WARREN_KV.put(quotaKey, String(usados), { expirationTtl: 60 * 60 * 24 * 40 }); } catch (e) {}
    }

    return new Response(JSON.stringify({
        broker: parsed.broker || null,
        positions,
        avisos: Array.isArray(parsed.avisos) ? parsed.avisos.slice(0, 8) : [],
        cuota: { usados, limite: PDF_PARSE_FREE_LIMIT, ilimitado: member }
    }), { headers: JSON_HEADERS });
}

export default {
    async fetch(request, env, ctx) {
        if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS_HEADERS });
        const url = new URL(request.url);
        try {
            if (request.method === 'POST' && url.pathname === '/chat') return await handleChat(request, env, ctx);
            if (request.method === 'POST' && url.pathname === '/portfolio/parse') return await handlePortfolioParse(request, env);
            if (url.pathname.startsWith('/conversation')) {
                const email = await emailDelToken(request);
                if (!email) return json({ error: 'login_required' }, 401);
                if (request.method === 'GET' && url.pathname === '/conversations') return await handleConversationsList(email, env);
                if (request.method === 'GET' && url.pathname === '/conversation') return await handleConversationGet(request, email, env);
                if (request.method === 'POST' && url.pathname === '/conversation/save') return await handleConversationSave(request, email, env);
                if (request.method === 'POST' && url.pathname === '/conversation/delete') return await handleConversationDelete(request, email, env);
            }
            // Ruta vieja (POST /): la usaban paginas anteriores a /chat, que
            // mandaban su propio prompt y un email sin verificar. Ya no responde.
            if (request.method === 'POST' && url.pathname === '/') {
                return json({ response: 'Warren se actualizó. Recargá la página para seguir.' });
            }
        } catch (err) {
            console.error('[warren] error:', err && err.message);
            return json({ error: 'internal' }, 500);
        }
        return new Response('Not Found', { status: 404, headers: CORS_HEADERS });
    }
};
