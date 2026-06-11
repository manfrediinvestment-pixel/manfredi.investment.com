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

            // Si tiene menos de 7 dÃÂ­as y la semana coincide, devolver cache

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

  if (url.pathname === '/debug-ff') {
    try {
      const resp = await fetch('https://nfs.faireconomy.media/ff_calendar_thisweek.json', {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)', 'Accept': 'application/json' },
      });
      const text = await resp.text();
      return new Response(JSON.stringify({ status: resp.status, body: text.substring(0, 2000) }), { headers });
    } catch(e) {
      return new Response(JSON.stringify({ error: e.message }), { headers });
    }
  }

  if (url.pathname === '/debug-indec') {
    try {
      const resp = await fetch('https://www.indec.gob.ar/ftp/cuadros/publicaciones/calendario_1sem2026.pdf', {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)' },
      });
      const buf = await resp.arrayBuffer();
      const text = extractTextFromPDF(buf);
      return new Response(JSON.stringify({ status: resp.status, bytes: buf.byteLength, textSample: text.substring(0, 2000) }), { headers });
    } catch(e) {
      return new Response(JSON.stringify({ error: e.message }), { headers });
    }
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

// Ã¢ÂÂÃ¢ÂÂ HELPERS DE FECHA Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

// Ã¢ÂÂÃ¢ÂÂ EVENTOS REALES Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

  // Construir estructura de dÃÂ­as

  const nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

  const dias = nombres.map((nombre, i) => {

    const fechaISO = fechasISO[i];

    const evAR = eventosAR.filter(e => e.fecha === fechaISO).map(e => ({ tipo: 'ar', titulo: e.titulo, descripcion: e.descripcion }));

    const evUS = eventosUS.filter(e => e.fecha === fechaISO).map(e => ({ tipo: 'us', titulo: e.titulo, descripcion: e.descripcion }));

    // Mezclar: mÃÂ¡ximo 3 eventos por dÃÂ­a, priorizando alta relevancia

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

// Ã¢ÂÂÃ¢ÂÂ INDEC Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

async function fetchEventosINDEC(lunes, viernes, fechasISO) {

  const eventos = [];

  // El INDEC publica sus indicadores en fechas predecibles cada mes.

  const anio = lunes.getFullYear();

  const mesLunes = lunes.getMonth(); // 0-indexed

  // Iterar sobre los meses que pueden solapar con la semana

  const mesesARevisar = [...new Set([mesLunes, viernes.getMonth()])];

  for (const mes of mesesARevisar) {

    const mesNombre = new Date(anio, mes, 1).toLocaleDateString('es-AR', { month: 'long' });

    const mesNombreCap = mesNombre.charAt(0).toUpperCase() + mesNombre.slice(1);

    // IPC: sale entre el 10 y el 15 de cada mes (usualmente el dÃ­a 12-13)

    const diaIPC = getDiaHabil(anio, mes, 12);

    const fechaIPC = fmtISO(new Date(anio, mes, diaIPC));

    if (fechasISO.includes(fechaIPC)) {

      eventos.push({

        fecha: fechaIPC,

        const mesAnterior = new Date(anio, mes - 1, 1).toLocaleDateString('es-AR', { month: 'long' });

        const mesAnteriorCap = mesAnterior.charAt(0).toUpperCase() + mesAnterior.slice(1);

        titulo: `IPC ${mesAnteriorCap} ${anio}`,

        descripcion: `INDEC publica el Índice de Precios al Consumidor de ${mesAnteriorCap}. Dato clave para política monetaria del BCRA.`,

      });

    }

    // EMAE: sale entre el 20 y el 25 de cada mes (con 2 meses de rezago)

    const diaEMAE = getDiaHabil(anio, mes, 22);

    const fechaEMAE = fmtISO(new Date(anio, mes, diaEMAE));

    if (fechasISO.includes(fechaEMAE)) {

      const mesRezago = new Date(anio, mes - 2, 1).toLocaleDateString('es-AR', { month: 'long' });

      eventos.push({

        fecha: fechaEMAE,

        titulo: `EMAE ${mesRezago.charAt(0).toUpperCase() + mesRezago.slice(1)} ${anio}`,

        descripcion: `INDEC publica el Estimador Mensual de Actividad EconÃ³mica. Indicador adelantado del PBI.`,

      });

    }

    // Intercambio Comercial: sale entre el 20 y 25 de cada mes

    const diaICA = getDiaHabil(anio, mes, 24);

    const fechaICA = fmtISO(new Date(anio, mes, diaICA));

    if (fechasISO.includes(fechaICA)) {

      eventos.push({

        fecha: fechaICA,

        titulo: `Intercambio Comercial ${mesNombreCap}`,

        descripcion: `INDEC publica exportaciones, importaciones y balanza comercial de Argentina.`,

      });

    }

    // Mercado de trabajo (EPH): sale trimestral

    const trimestresEPH = [

      { mes: 5, dia: 24, label: 'Q1 2026' },

      { mes: 8, dia: 24, label: 'Q2 2026' },

      { mes: 11, dia: 19, label: 'Q3 2026' },

      { mes: 2, dia: 24, label: 'Q4 2025' },

    ];

    for (const eph of trimestresEPH) {

      if (eph.mes === mes) {

        const diaEPH = getDiaHabil(anio, mes, eph.dia);

        const fechaEPH = fmtISO(new Date(anio, mes, diaEPH));

        if (fechasISO.includes(fechaEPH)) {

          eventos.push({

            fecha: fechaEPH,

            titulo: `Desempleo ${eph.label} (EPH)`,

            descripcion: `INDEC publica la Encuesta Permanente de Hogares con datos de empleo y desempleo.`,

          });

        }

      }

    }

  }

  return eventos;

}

function extractTextFromPDF(arrayBuffer) {

  const bytes = new Uint8Array(arrayBuffer);

  let text = '';

  const decoder = new TextDecoder('latin1');

  const raw = decoder.decode(bytes);

  // Extraer texto entre parÃÂ©ntesis de operadores Tj y TJ (formato PDF)

  const tjMatches = raw.matchAll(/\(([^)]{1,200})\)\s*Tj/g);

  for (const m of tjMatches) {

    text += m[1] + ' ';

  }

  // TambiÃÂ©n buscar streams de texto plano

  const streamMatches = raw.matchAll(/stream\r?\n([\s\S]*?)\r?\nendstream/g);

  for (const m of streamMatches) {

    const chunk = m[1];

    // Solo agregar si parece texto legible

    if (/[a-zÃÂ¡ÃÂ©ÃÂ­ÃÂ³ÃÂºÃÂ±A-ZÃÂÃÂÃÂÃÂÃÂÃÂ]{3,}/.test(chunk)) {

      text += chunk + '\n';

    }

  }

  // Limpiar caracteres no imprimibles y normalizar espacios

  text = text.replace(/[^\x20-\x7E\xC0-\xFF\n]/g, ' ').replace(/\s+/g, ' ');

  return text;

}

// Ã¢ÂÂÃ¢ÂÂ FOREXFACTORY (EEUU) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

    // FIX: el campo es "country" no "currency", e "impact" puede ser "High"

    const eventosAltos = data.filter(e =>

      e.country === 'USD' &&

      e.impact === 'High'

    );

    const traducciones = {

      'CPI m/m': 'IPC (InflaciÃ³n) mensual',

      'Core CPI m/m': 'IPC Core mensual',

      'PPI m/m': 'Ãndice de Precios al Productor',

      'Non-Farm Employment Change': 'NÃ³minas No AgrÃ­colas',

      'Unemployment Rate': 'Tasa de Desempleo',

      'FOMC Statement': 'Comunicado FOMC (Fed)',

      'Federal Funds Rate': 'DecisiÃ³n de Tasas Fed',

      'Fed Chair Press Conference': 'Conferencia de Prensa Fed',

      'GDP q/q': 'PBI Trimestral',

      'Prelim GDP q/q': 'PBI Trimestral (preliminar)',

      'Retail Sales m/m': 'Ventas Minoristas',

      'ISM Manufacturing PMI': 'PMI Manufacturero ISM',

      'ISM Services PMI': 'PMI Servicios ISM',

      'Initial Jobless Claims': 'Solicitudes de Desempleo',

      'Consumer Confidence': 'Confianza del Consumidor',

      'Trade Balance': 'Balanza Comercial',

      'PCE Price Index m/m': 'PCE (InflaciÃ³n Fed)',

      'Core PCE Price Index m/m': 'PCE Core (InflaciÃ³n Fed)',

      'ADP Non-Farm Employment Change': 'Empleo ADP (privado)',

      'Average Hourly Earnings m/m': 'Salarios por hora',

      'CB Consumer Confidence': 'Confianza del Consumidor CB',

      'Empire State Manufacturing Index': 'Ãndice Manufacturero NY',

      'Existing Home Sales': 'Ventas de Viviendas Existentes',

      'New Home Sales': 'Ventas de Viviendas Nuevas',

      'Durable Goods Orders m/m': 'Pedidos de Bienes Duraderos',

    };

    for (const ev of eventosAltos) {

      const fechaISO = ev.date ? ev.date.split('T')[0] : null;

      if (!fechaISO || !fechasISO.includes(fechaISO)) continue;

      const tituloES = traducciones[ev.title] || ev.title;

      // Extraer hora UTC del date string

      let horaStr = '';

      try {

        const d = new Date(ev.date);

        const hh = String(d.getUTCHours()).padStart(2, '0');

        const mm = String(d.getUTCMinutes()).padStart(2, '0');

        horaStr = `${hh}:${mm} UTC`;

      } catch(e) {}

      eventos.push({

        fecha: fechaISO,

        titulo: tituloES,

        descripcion: horaStr ? `${tituloES} â ${horaStr}` : tituloES,

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

// Ã¢ÂÂÃ¢ÂÂ FRED Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

// Ã¢ÂÂÃ¢ÂÂ COMMODITIES Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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

// Devuelve el dÃ­a hÃ¡bil mÃ¡s cercano a "dia" en el mes dado (evita sÃ¡bado y domingo)

function getDiaHabil(anio, mes, dia) {

  const d = new Date(anio, mes, dia);

  const dow = d.getDay();

  if (dow === 6) return dia - 1; // sÃ¡bado â viernes

  if (dow === 0) return dia + 1; // domingo â lunes

  return dia;

}
