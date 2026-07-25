/*
 * manfredi-mercados
 * Agrega data912 + Finnhub + TwelveData + CoinGecko + dolarapi + Yahoo en un solo
 * payload cacheado en KV (patron cache-on-miss, igual que manfredi-calendario).
 * Objetivo: sacar las API keys del navegador y servir un indice grande de activos
 * (para el buscador de la seccion Mercados) sin que cada visitante dispare llamados
 * directos a las fuentes.
 */

const CACHE_KEY = 'mercados_v1';
const CACHE_TTL_SECONDS = 120;

// Nombres de empresa conocidos - el resto del universo (miles de tickers de
// data912) se muestra solo con el ticker hasta que se amplie este mapa.
const NAME_MAP = {
  // Acciones Argentina
  YPFD: 'YPF', GGAL: 'Grupo Galicia', BMA: 'Banco Macro', PAMP: 'Pampa Energía',
  LOMA: 'Loma Negra', TXAR: 'Ternium Argentina', ALUA: 'Aluar', BYMA: 'BYMA',
  TECO2: 'Telecom Argentina', CEPU: 'Central Puerto', CRES: 'Cresud', COME: 'Comercial del Plata',
  TGSU2: 'Transportadora Gas del Sur', TGNO4: 'Transportadora Gas del Norte',
  EDN: 'Edenor', TRAN: 'Transener', VALO: 'Grupo Financiero Valores', SUPV: 'Banco Supervielle',
  // ADRs
  YPF: 'YPF', PAM: 'Pampa Energía', TEO: 'Telecom Argentina', LOM: 'Loma Negra',
  TX: 'Ternium', IRS: 'IRSA', BIOX: 'Bioceres', DESP: 'Despegar', MELI: 'MercadoLibre',
  GLOB: 'Globant', TS: 'Tenaris', CRESY: 'Cresud',
  // CEDEARs / Acciones USA (mismos tickers, mismo nombre en ambas categorías)
  AAPL: 'Apple', TSLA: 'Tesla', AMZN: 'Amazon', GOOGL: 'Alphabet (Google)', MSFT: 'Microsoft',
  NVDA: 'Nvidia', META: 'Meta Platforms', JPM: 'JPMorgan Chase', KO: 'Coca-Cola', DIS: 'Disney',
  NFLX: 'Netflix', 'BRK.B': 'Berkshire Hathaway', V: 'Visa', MA: 'Mastercard', WMT: 'Walmart',
  PG: 'Procter & Gamble', XOM: 'ExxonMobil', BA: 'Boeing', INTC: 'Intel', AMD: 'AMD',
  // Bonos AR (soberanos en dólares)
  AL30: 'Bonar 2030', GD30: 'Global 2030', AL35: 'Bonar 2035', GD35: 'Global 2035',
  AE38: 'Bonar 2038', GD38: 'Global 2038', AL41: 'Bonar 2041', GD41: 'Global 2041',
  GD46: 'Global 2046', AL29: 'Bonar 2029',
};

function displayName(symbol) {
  return NAME_MAP[symbol] || symbol;
}

// ─── data912 ─────────────────────────────────────────────────────────────
async function fetchD912(endpoint) {
  try {
    const resp = await fetch(`https://data912.com/live/${endpoint}`, { signal: AbortSignal.timeout(10000) });
    if (!resp.ok) throw new Error(`data912 ${endpoint} HTTP ${resp.status}`);
    const rows = await resp.json();
    if (!Array.isArray(rows)) return [];
    return rows;
  } catch (e) {
    console.error(`[mercados] data912/${endpoint}:`, e.message);
    return [];
  }
}

function mapD912Rows(rows, { sortByVolume = true, limit = null } = {}) {
  let items = rows
    .filter(r => r.symbol && r.c != null)
    .map(r => ({
      symbol: r.symbol,
      name: displayName(r.symbol),
      price: r.c,
      change: r.pct_change ?? null,
      volume: r.v ?? 0,
    }));
  if (sortByVolume) items.sort((a, b) => (b.volume || 0) - (a.volume || 0));
  if (limit) items = items.slice(0, limit);
  return items;
}

// ─── Finnhub (server-side, key nunca viaja al navegador) ──────────────────
async function fetchFinnhub(symbol, key) {
  if (!key) return null;
  try {
    const url = `https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(symbol)}&token=${key}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.c == null || data.c === 0) return null;
    const pct = data.pc > 0 ? ((data.c - data.pc) / data.pc * 100) : null;
    return { price: data.c, change: pct };
  } catch (e) {
    console.error(`[mercados] Finnhub/${symbol}:`, e.message);
    return null;
  }
}

// ─── TwelveData (server-side) ──────────────────────────────────────────────
async function fetchTwelveData(symbol, key) {
  if (!key) return null;
  try {
    const url = `https://api.twelvedata.com/quote?symbol=${encodeURIComponent(symbol)}&apikey=${key}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return null;
    const data = await res.json();
    if (!data.close) return null;
    return { price: parseFloat(data.close), change: data.percent_change != null ? parseFloat(data.percent_change) : null };
  } catch (e) {
    console.error(`[mercados] TwelveData/${symbol}:`, e.message);
    return null;
  }
}

// ─── Yahoo Finance (para commodities, sin key) ────────────────────────────
async function fetchYahoo(symbol) {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=5d`;
    const resp = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(8000) });
    if (!resp.ok) return null;
    const json = await resp.json();
    const chart = json?.chart?.result?.[0];
    const closes = chart?.indicators?.quote?.[0]?.close;
    if (!closes) return null;
    const valid = closes.filter(v => v != null);
    if (!valid.length) return null;
    const cur = valid[valid.length - 1];
    const prev = valid.length > 1 ? valid[valid.length - 2] : null;
    const change = prev ? ((cur - prev) / prev * 100) : null;
    return { price: cur, change };
  } catch (e) {
    console.error(`[mercados] Yahoo/${symbol}:`, e.message);
    return null;
  }
}

// ─── dolarapi.com ──────────────────────────────────────────────────────────
async function fetchDolares() {
  try {
    const resp = await fetch('https://dolarapi.com/v1/dolares', { signal: AbortSignal.timeout(8000) });
    if (!resp.ok) return [];
    const rows = await resp.json();
    if (!Array.isArray(rows)) return [];
    const LABELS = {
      oficial: 'Dólar Oficial', blue: 'Dólar Blue', bolsa: 'Dólar MEP',
      contadoconliqui: 'Dólar CCL', mayorista: 'Dólar Mayorista',
      cripto: 'Dólar Cripto', tarjeta: 'Dólar Tarjeta',
    };
    return rows.map(r => ({
      symbol: (r.casa || '').toUpperCase(),
      name: LABELS[r.casa] || r.nombre || r.casa,
      price: r.venta,
      compra: r.compra,
      change: null,
      volume: 0,
    }));
  } catch (e) {
    console.error('[mercados] dolarapi:', e.message);
    return [];
  }
}

async function fetchDivisas() {
  try {
    const resp = await fetch('https://open.er-api.com/v6/latest/USD', { signal: AbortSignal.timeout(8000) });
    if (!resp.ok) return [];
    const data = await resp.json();
    const rates = data.rates || {};
    const FX = [
      { code: 'EUR', name: 'Euro' }, { code: 'BRL', name: 'Real brasileño' },
      { code: 'CNY', name: 'Yuan chino' }, { code: 'GBP', name: 'Libra esterlina' },
      { code: 'CHF', name: 'Franco suizo' }, { code: 'JPY', name: 'Yen japonés' },
    ];
    return FX.filter(f => rates[f.code]).map(f => ({
      symbol: f.code, name: f.name, price: rates[f.code], change: null, volume: 0, isRateVsUSD: true,
    }));
  } catch (e) {
    console.error('[mercados] divisas:', e.message);
    return [];
  }
}

// ─── CoinGecko ──────────────────────────────────────────────────────────
async function fetchCripto() {
  try {
    const url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=150&page=1&sparkline=false&price_change_percentage=24h';
    const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (!resp.ok) return [];
    const rows = await resp.json();
    if (!Array.isArray(rows)) return [];
    return rows.map(c => ({
      symbol: (c.symbol || '').toUpperCase(),
      name: c.name,
      price: c.current_price,
      change: c.price_change_percentage_24h,
      volume: c.total_volume || 0,
    }));
  } catch (e) {
    console.error('[mercados] coingecko:', e.message);
    return [];
  }
}

// ─── Merval: ArgentinaDatos → Finnhub → Yahoo ─────────────────────────────
async function fetchMerval(finnhubKey) {
  try {
    const res = await fetch('https://api.argentinadatos.com/v1/cotizaciones/indices/merval', { signal: AbortSignal.timeout(8000) });
    if (res.ok) {
      const data = await res.json();
      const last = Array.isArray(data) ? data[data.length - 1] : null;
      if (last?.valor) {
        const prev = data.length > 1 ? data[data.length - 2]?.valor : null;
        const change = prev > 0 ? ((last.valor - prev) / prev * 100) : null;
        return { price: last.valor, change };
      }
    }
  } catch (e) { console.error('[mercados] Merval/ArgentinaDatos:', e.message); }
  const viaFinnhub = await fetchFinnhub('BYMA:MERVAL', finnhubKey);
  if (viaFinnhub) return viaFinnhub;
  return await fetchYahoo('^MERV');
}

// ─── Commodities (Yahoo futures) ──────────────────────────────────────────
async function fetchCommodities() {
  const specs = [
    { symbol: 'GC=F', id: 'XAU', name: 'Oro' },
    { symbol: 'SI=F', id: 'XAG', name: 'Plata' },
    { symbol: 'CL=F', id: 'WTI', name: 'Petróleo WTI' },
    { symbol: 'BZ=F', id: 'BRENT', name: 'Petróleo Brent' },
    { symbol: 'ZC=F', id: 'CORN', name: 'Maíz' },
    { symbol: 'NG=F', id: 'NATGAS', name: 'Gas Natural' },
    { symbol: 'HG=F', id: 'COPPER', name: 'Cobre' },
  ];
  const results = await Promise.all(specs.map(async s => {
    const r = await fetchYahoo(s.symbol);
    return { symbol: s.id, name: s.name, price: r?.price ?? null, change: r?.change ?? null, volume: 0 };
  }));
  return results;
}

// ─── Agregación completa ──────────────────────────────────────────────────
async function buildPayload(env) {
  const finnhubKey = env.FINNHUB_KEY;
  const twelveDataKey = env.TWELVEDATA_KEY;

  const [
    argStocksRaw, argCedearsRaw, usaStocksRaw, usaAdrsRaw, argBondsRaw,
    cripto, commodities, dolares, divisas,
    oro, spx, ndx, merval,
  ] = await Promise.all([
    fetchD912('arg_stocks'),
    fetchD912('arg_cedears'),
    fetchD912('usa_stocks'),
    fetchD912('usa_adrs'),
    fetchD912('arg_bonds'),
    fetchCripto(),
    fetchCommodities(),
    fetchDolares(),
    fetchDivisas(),
    fetchTwelveData('XAU/USD', twelveDataKey),
    fetchFinnhub('SPY', finnhubKey),
    fetchFinnhub('QQQ', finnhubKey),
    fetchMerval(finnhubKey),
  ]);

  const wti = commodities.find(c => c.symbol === 'WTI');
  const btc = cripto.find(r => r.symbol === 'BTC') || null;

  const featured = [
    { id: 'oro', flag: '🥇', name: 'Oro', unit: 'US$', price: oro?.price ?? null, change: oro?.change ?? null },
    { id: 'merval', flag: '🇦🇷', name: 'Merval', unit: '', price: merval?.price ?? null, change: merval?.change ?? null },
    { id: 'sp500', flag: '🇺🇸', name: 'S&P 500', unit: 'US$', price: spx?.price ?? null, change: spx?.change ?? null },
    { id: 'nasdaq', flag: '🇺🇸', name: 'Nasdaq 100', unit: 'US$', price: ndx?.price ?? null, change: ndx?.change ?? null },
    { id: 'btc', flag: '₿', name: 'Bitcoin', unit: 'US$', price: btc?.price ?? null, change: btc?.change ?? null },
    { id: 'ccl', flag: '🇦🇷', name: 'Dólar CCL', unit: '$', price: dolares.find(d => d.symbol === 'CONTADOCONLIQUI')?.price ?? null, change: null },
    { id: 'wti', flag: '🛢️', name: 'Petróleo WTI', unit: 'US$', price: wti?.price ?? null, change: wti?.change ?? null },
  ];

  const categorias = {
    arg_stocks:  { currency: 'ARS', total: argStocksRaw.length,  items: mapD912Rows(argStocksRaw) },
    arg_cedears: { currency: 'ARS', total: argCedearsRaw.length, items: mapD912Rows(argCedearsRaw, { limit: 400 }) },
    usa_stocks:  { currency: 'USD', total: usaStocksRaw.length,  items: mapD912Rows(usaStocksRaw, { limit: 500 }) },
    usa_adrs:    { currency: 'USD', total: usaAdrsRaw.length,    items: mapD912Rows(usaAdrsRaw) },
    arg_bonds:   { currency: 'ARS', total: argBondsRaw.length,   items: mapD912Rows(argBondsRaw) },
    cripto:      { currency: 'USD', total: cripto.length,        items: cripto },
    commodities: { currency: 'USD', total: commodities.length,   items: commodities },
    dolares:     { currency: 'ARS', total: dolares.length + divisas.length, items: [...dolares, ...divisas] },
  };

  return { updated: new Date().toISOString(), featured, categorias };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
    };
    if (request.method === 'OPTIONS') return new Response(null, { headers });

    if (url.pathname === '/mercados') {
      try {
        const forceRefresh = url.searchParams.get('refresh') === '1';
        if (!forceRefresh) {
          const cached = await env.MERCADOS_KV.get(CACHE_KEY);
          if (cached) return new Response(cached, { headers });
        }
        const payload = await buildPayload(env);
        const json = JSON.stringify(payload);
        await env.MERCADOS_KV.put(CACHE_KEY, json, { expirationTtl: CACHE_TTL_SECONDS });
        return new Response(json, { headers });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
      }
    }

    return new Response('Manfredi Mercados Worker OK', { headers: { 'Content-Type': 'text/plain' } });
  },
};
