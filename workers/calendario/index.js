export default {

  async fetch(request, env) {

    const url = new URL(request.url);

    const headers = {

      'Content-Type': 'application/json',

      'Access-Control-Allow-Origin': '*',

      'Access-Control-Allow-Methods': 'GET, OPTIONS',

    };

    if (request.method === 'OPTIONS') return new Response(null, { headers });

    if (url.pathname === '/calendario') {

      try {

        const cached = await env.CALENDARIO_KV.get('eventos_semana');

        if (cached && cached !== '{}' && cached !== '') {

          // Verificar que el cache es de esta semana

          try {

            const parsed = JSON.parse(cached);

            const generado = new Date(parsed.generado);

            const ahora = new Date();

            const diffHoras = (ahora - generado) / (1000 * 60 * 60);

            // Si tiene menos de 7 días y la semana coincide, devolver cache

            if (diffHoras < 168) return new Response(cached, { headers });

          } catch(e) {

            // Si no se puede parsear, regenerar

          }

        }

        const result = await generarEventos(env);

        const json = JSON.stringify(result);

        await env.CALENDARIO_KV.put('eventos_semana', json, { expirationTtl: 60 * 60 * 24 * 7 });

        return new Response(json, { headers });

      } catch(err) {

        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });

      }

    }

    if (url.pathname === '/calendario/refresh') {

      try {

        const result = await generarEventos(env);

        const json = JSON.stringify(result);

        await env.CALENDARIO_KV.put('eventos_semana', json, { expirationTtl: 60 * 60 * 24 * 7 });

        return new Response(json, { headers });

      } catch(err) {

        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });

      }

    }

    if (url.pathname === '/macro-us') {

      try {

        const cached = await env.CALENDARIO_KV.get('macro_us');

        if (cached) return new Response(cached, { headers });

        const result = await fetchFRED(env);

        const json = JSON.stringify(result);

        await env.CALENDARIO_KV.put('macro_us', json, { expirationTtl: 60 * 60 * 24 });

        return new Response(json, { headers });

      } catch(err) {

        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });

      }

    }

    if (url.pathname === '/commodities') {

      try {

        const cached = await env.CALENDARIO_KV.get('commodities');

        if (cached) return new Response(cached, { headers });

        const result = await fetchCommodities(env);

        const json = JSON.stringify(result);

        await env.CALENDARIO_KV.put('commodities', json, { expirationTtl: 60 * 60 * 6 });

        return new Response(json, { headers });

      } catch(err) {

        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });

      }

    }

    if (url.pathname === '/debug-av') {

      const k = env.COMMODITY_API_KEY || env.ALPHA_VANTAGE_KEY;

      const r = await fetch(`https://www.alphavantage.co/query?function=WTI&interval=daily&apikey=${k}`);

      const keyLen = k ? k.length : 0;

      const t = JSON.stringify({ avResponse: await r.text(), keyLen, hasCommodityKey: !!env.COMMODITY_API_KEY, hasAVKey: !!env.ALPHA_VANTAGE_KEY });

      return new Response(t, { headers });

    }

    return new Response('Manfredi Calendario Worker OK', { headers: { 'Content-Type': 'text/plain' } });

  },

  async scheduled(event, env, ctx) {

    ctx.waitUntil(Promise.all([

      generarYGuardar(env),

      fetchYGuardarFRED(env),

      fetchYGuardarCommodities(env),

    ]));

  }

};

// ── HELPERS DE FECHA ──────────────────────────────────────────────────────────

function getLunes() {

  const hoy = new Date();

  const dow = hoy.getDay();

  const lunes = new Date(hoy);

  lunes.setDate(hoy.getDate() - (dow === 0 ? 6 : dow - 1));

  lunes.setHours(0, 0, 0, 0);

  return lunes;

}

function fmt(d) {

  return d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' });

}

function fmtISO(d) {

  // Devuelve YYYY-MM-DD

  return d.toISOString().split('T')[0];

}

// ── EVENTOS REALES ─────────────────────────────────────────────────────────────

async function generarEventos(env) {

  const hoy = new Date();

  const lunes = getLunes();

  const viernes = new Date(lunes.getTime() + 4 * 86400000);

  const mes = lunes.toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });

  const semana = `${fmt(lunes)} al ${fmt(viernes)} de ${mes}`;

  const fechas = Array.from({ length: 5 }, (_, i) => fmt(new Date(lunes.getTime() + i * 86400000)));

  const fechasISO = Array.from({ length: 5 }, (_, i) => fmtISO(new Date(lunes.getTime() + i * 86400000)));

  // Obtener eventos en paralelo

  const [eventosAR, eventosUS] = await Promise.all([

    fetchEventosINDEC(lunes, viernes, fechasISO),

    fetchEventosForexFactory(fechasISO),

  ]);

  // Construir estructura de días

  const nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

  const dias = nombres.map((nombre, i) => {

    const fechaISO = fechasISO[i];

    const evAR = eventosAR.filter(e => e.fecha === fechaISO).map(e => ({ tipo: 'ar', titulo: e.titulo, descripcion: e.descripcion }));

    const evUS = eventosUS.filter(e => e.fecha === fechaISO).map(e => ({ tipo: 'us', titulo: e.titulo, descripcion: e.descripcion }));

    // Mezclar: máximo 3 eventos por día, priorizando alta relevancia

    const todos = [...evAR, ...evUS].slice(0, 3);

    return { nombre, fecha: fechas[i], eventos: todos };

  });

  return {

    semana,

    generado: hoy.toISOString(),

    fuente: 'INDEC + ForexFactory',

    dias,

  };

}

// ── INDEC ─────────────────────────────────────────────────────────────────────

async function fetchEventosINDEC(lunes, viernes, fechasISO) {

  const eventos = [];

  // Determinar qué PDF usar según el mes

  const mes = lunes.getMonth() + 1; // 1-12

  const anio = lunes.getFullYear();

  const semestre = mes <= 6 ? '1sem' : '2sem';

  const pdfUrl = `https://www.indec.gob.ar/ftp/cuadros/publicaciones/calendario_${semestre}${anio}.pdf`;

  try {

    const resp = await fetch(pdfUrl, {

      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)' },

      signal: AbortSignal.timeout(15000),

    });

    if (!resp.ok) throw new Error(`INDEC PDF status ${resp.status}`);

    const arrayBuffer = await resp.arrayBuffer();

    const text = extractTextFromPDF(arrayBuffer);

    // Parsear los eventos del PDF

    // Formato: "DD AB Nombre del indicador. Período"

    // Ej: "14 MA Índice de precios al consumidor (IPC). Cobertura nacional. Mayo de 2026"

    const lines = text.split('\n');

    const diasSemana = { 'LU': 1, 'MA': 2, 'MI': 3, 'JU': 4, 'VI': 5 };

    const mesesES = { 'enero':0,'febrero':1,'marzo':2,'abril':3,'mayo':4,'junio':5,'julio':6,'agosto':7,'septiembre':8,'octubre':9,'noviembre':10,'diciembre':11 };

    let mesActual = null;

    let anioActual = anio;

    for (const line of lines) {

      const trimmed = line.trim();

      if (!trimmed) continue;

      // Detectar encabezado de mes

      const mesMatch = trimmed.match(/^(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)$/i);

      if (mesMatch) {

        mesActual = mesesES[mesMatch[1].toLowerCase()];

        continue;

      }

      if (mesActual === null) continue;

      // Detectar línea de evento: "DD AB Título..."

      const eventoMatch = trimmed.match(/^(\d{1,2})\s+(LU|MA|MI|JU|VI)\s+(.+)$/);

      if (!eventoMatch) continue;

      const dia = parseInt(eventoMatch[1]);

      const abrevDia = eventoMatch[2];

      const titulo = eventoMatch[3].trim();

      // Construir fecha ISO

      const fechaEvento = new Date(anioActual, mesActual, dia);

      const fechaISO = fmtISO(fechaEvento);

      // ¿Está en la semana actual?

      if (!fechasISO.includes(fechaISO)) continue;

      // Filtrar solo los indicadores relevantes para inversores

      const relevantes = [

        'Índice de precios al consumidor',

        'IPC',

        'Estimador mensual de actividad económica',

        'EMAE',

        'Intercambio comercial argentino',

        'Índice de salarios',

        'Mercado de trabajo',

        'Balanza de pagos',

        'Índice de producción industrial manufacturero',

        'Reservas',

        'Informe de avance del nivel de actividad',

      ];

      const esRelevante = relevantes.some(r => titulo.toLowerCase().includes(r.toLowerCase()));

      if (!esRelevante) continue;

      // Descripción corta

      const descripcion = titulo.length > 80 ? titulo.substring(0, 77) + '...' : titulo;

      eventos.push({

        fecha: fechaISO,

        titulo: titulo.split('.')[0].trim(), // Solo el nombre, sin el período

        descripcion,

      });

    }

  } catch(e) {

    console.error('[INDEC] Error:', e.message);

  }

  return eventos;

}

// Extracción de texto básica de PDF (sin librería externa)

function extractTextFromPDF(arrayBuffer) {

  const bytes = new Uint8Array(arrayBuffer);

  let text = '';

  const decoder = new TextDecoder('latin1');

  const raw = decoder.decode(bytes);

  // Extraer texto entre paréntesis de operadores Tj y TJ (formato PDF)

  const tjMatches = raw.matchAll(/\(([^)]{1,200})\)\s*Tj/g);

  for (const m of tjMatches) {

    text += m[1] + ' ';

  }

  // También buscar streams de texto plano

  const streamMatches = raw.matchAll(/stream\r?\n([\s\S]*?)\r?\nendstream/g);

  for (const m of streamMatches) {

    const chunk = m[1];

    // Solo agregar si parece texto legible

    if (/[a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}/.test(chunk)) {

      text += chunk + '\n';

    }

  }

  // Limpiar caracteres no imprimibles y normalizar espacios

  text = text.replace(/[^\x20-\x7E\xC0-\xFF\n]/g, ' ').replace(/\s+/g, ' ');

  return text;

}

// ── FOREXFACTORY (EEUU) ───────────────────────────────────────────────────────

async function fetchEventosForexFactory(fechasISO) {

  const eventos = [];

  try {

    const resp = await fetch('https://nfs.faireconomy.media/ff_calendar_thisweek.json', {

      headers: {

        'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)',

        'Accept': 'application/json',

      },

      signal: AbortSignal.timeout(10000),

    });

    if (!resp.ok) throw new Error(`ForexFactory status ${resp.status}`);

    const data = await resp.json();

    if (!Array.isArray(data)) throw new Error('Formato inesperado de ForexFactory');

    // Filtrar: solo USD, solo alto impacto

    const eventosAltos = data.filter(e =>

      e.currency === 'USD' &&

      e.impact === 'High'

    );

    // Traducciones de títulos comunes

    const traducciones = {

      'CPI m/m': 'IPC (Inflación) mensual',

      'Core CPI m/m': 'IPC Core mensual',

      'PPI m/m': 'Índice de Precios al Productor',

      'Non-Farm Employment Change': 'Nóminas No Agrícolas',

      'Unemployment Rate': 'Tasa de Desempleo',

      'FOMC Statement': 'Comunicado FOMC (Fed)',

      'Federal Funds Rate': 'Decisión de Tasas Fed',

      'Fed Chair Press Conference': 'Conferencia de Prensa Fed',

      'GDP q/q': 'PBI Trimestral (preliminar)',

      'Retail Sales m/m': 'Ventas Minoristas',

      'ISM Manufacturing PMI': 'PMI Manufacturero ISM',

      'ISM Services PMI': 'PMI Servicios ISM',

      'Initial Jobless Claims': 'Solicitudes de Desempleo',

      'Consumer Confidence': 'Confianza del Consumidor',

      'Trade Balance': 'Balanza Comercial',

      'PCE Price Index m/m': 'PCE (Inflación Fed)',

      'Core PCE Price Index m/m': 'PCE Core (Inflación Fed)',

    };

    for (const ev of eventosAltos) {

      // Parsear fecha del evento (formato: "2026-06-10T12:30:00")

      const fechaISO = ev.date ? ev.date.split('T')[0] : null;

      if (!fechaISO || !fechasISO.includes(fechaISO)) continue;

      const tituloES = traducciones[ev.title] || ev.title;

      const hora = ev.date && ev.date.includes('T') ? ev.date.split('T')[1].substring(0, 5) + ' UTC' : '';

      eventos.push({

        fecha: fechaISO,

        titulo: tituloES,

        descripcion: hora ? `${tituloES}. Publicación: ${hora}` : tituloES,

      });

    }

  } catch(e) {

    console.error('[ForexFactory] Error:', e.message);

  }

  return eventos;

}

async function generarYGuardar(env) {

  const eventos = await generarEventos(env);

  await env.CALENDARIO_KV.put('eventos_semana', JSON.stringify(eventos), { expirationTtl: 60 * 60 * 24 * 7 });

}

// ── FRED ──────────────────────────────────────────────────────────────────────

async function fetchFRED(env) {

  const key = env.FRED_API_KEY;

  const base = 'https://api.stlouisfed.org/fred/series/observations';

  const fetchSeries = async (id, limit) => {

    const fredResp = await fetch(`${base}?series_id=${id}&api_key=${key}&file_type=json&limit=${limit}&sort_order=desc`);

    const fredJson = await fredResp.json();

    return (fredJson.observations || []).filter(o => o.value !== '.' && o.value !== null);

  };

  const [gdpObs, cpiObs, unempObs, t10yObs] = await Promise.all([

    fetchSeries('A191RL1Q225SBEA', 2),

    fetchSeries('CPIAUCSL', 14),

    fetchSeries('UNRATE', 2),

    fetchSeries('DGS10', 2),

  ]);

  const gdpVal = gdpObs.length > 0 ? parseFloat(gdpObs[0].value).toFixed(1) : null;

  let cpiVal = null;

  if (cpiObs.length >= 13) {

    const current = parseFloat(cpiObs[0].value);

    const yearAgo = parseFloat(cpiObs[12].value);

    if (!isNaN(current) && !isNaN(yearAgo) && yearAgo !== 0) {

      cpiVal = ((current - yearAgo) / yearAgo * 100).toFixed(1);

    }

  }

  const unempVal = unempObs.length > 0 ? parseFloat(unempObs[0].value).toFixed(1) : null;

  const t10yVal = t10yObs.length > 0 ? parseFloat(t10yObs[0].value).toFixed(2) : null;

  return { gdp: gdpVal, cpi: cpiVal, unemp: unempVal, treasury: t10yVal, updated: new Date().toISOString() };

}

async function fetchYGuardarFRED(env) {

  const data = await fetchFRED(env);

  await env.CALENDARIO_KV.put('macro_us', JSON.stringify(data), { expirationTtl: 60 * 60 * 24 });

}

// ── COMMODITIES ───────────────────────────────────────────────────────────────

async function fetchCommodities(env) {

  const apiKey = env.COMMODITY_API_KEY || env.ALPHA_VANTAGE_KEY;

  const fmt = (v) => v != null ? parseFloat(v).toFixed(2) : null;

  const calcChange = (cur, prev) => {

    if (cur != null && prev != null && parseFloat(prev) !== 0) {

      return ((parseFloat(cur) - parseFloat(prev)) / Math.abs(parseFloat(prev)) * 100).toFixed(2);

    }

    return null;

  };

  const fetchSeries = async (fn) => {

    const url = `https://www.alphavantage.co/query?function=${fn}&interval=daily&apikey=${apiKey}`;

    const resp = await fetch(url);

    if (!resp.ok) return null;

    const json = await resp.json();

    if (!json.data || json.data.length < 2) return null;

    const cur = json.data[0].value;

    const prev = json.data[1].value;

    return { price: fmt(cur), change: calcChange(cur, prev) };

  };

  const fetchMetal = async (from) => {

    const url = `https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=${from}&to_currency=USD&apikey=${apiKey}`;

    const resp = await fetch(url);

    if (!resp.ok) return null;

    const json = await resp.json();

    const rate = json['Realtime Currency Exchange Rate'];

    if (!rate) return null;

    const cur = rate['5. Exchange Rate'];

    return { price: fmt(cur), change: null };

  };

  const [xau, xag, wti, brent, corn] = await Promise.all([

    fetchMetal('XAU'),

    fetchMetal('XAG'),

    fetchSeries('WTI'),

    fetchSeries('BRENT'),

    fetchSeries('CORN'),

  ]);

  return {

    XAU:   xau   || { price: null, change: null },

    XAG:   xag   || { price: null, change: null },

    WTI:   wti   || { price: null, change: null },

    BRENT: brent || { price: null, change: null },

    CORN:  corn  || { price: null, change: null },

    updated: new Date().toISOString()

  };

}

async function fetchYGuardarCommodities(env) {

  const data = await fetchCommodities(env);

  await env.CALENDARIO_KV.put('commodities', JSON.stringify(data), { expirationTtl: 60 * 60 * 6 });

}
