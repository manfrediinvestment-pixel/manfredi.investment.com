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
// Cierres historicos diarios: cambian a lo sumo una vez por dia, asi que
// cachear unas horas reduce muchisimo la carga sobre Yahoo/D912/Kraken
// cuando muchos usuarios calculan metricas de cartera (beta, volatilidad,
// etc.) al mismo tiempo y varios comparten los mismos tickers populares.
const HISTORICO_CACHE_TTL_SECONDS = 21600; // 6h
const HISTORICO_MAX_N = 180;

// Nombres de empresa conocidos - el resto del universo (miles de tickers de
// data912) se muestra solo con el ticker hasta que se amplie este mapa.
const NAME_MAP = {
  // Acciones Argentina
  YPFD: 'YPF', GGAL: 'Grupo Galicia', BMA: 'Banco Macro', PAMP: 'Pampa Energía',
  LOMA: 'Loma Negra', TXAR: 'Ternium Argentina', ALUA: 'Aluar', BYMA: 'BYMA',
  TECO2: 'Telecom Argentina', CEPU: 'Central Puerto', CRES: 'Cresud', COME: 'Comercial del Plata',
  TGSU2: 'Transportadora Gas del Sur', TGNO4: 'Transportadora Gas del Norte',
  EDN: 'Edenor', TRAN: 'Transener', VALO: 'Grupo Financiero Valores', SUPV: 'Banco Supervielle',
  BBAR: 'BBVA Argentina', IRSA: 'IRSA', CVH: 'Cablevisión Holding',
  // ADRs
  YPF: 'YPF', PAM: 'Pampa Energía', TEO: 'Telecom Argentina', LOM: 'Loma Negra',
  TX: 'Ternium', IRS: 'IRSA', BIOX: 'Bioceres', DESP: 'Despegar', MELI: 'MercadoLibre',
  GLOB: 'Globant', TS: 'Tenaris', CRESY: 'Cresud',
  // CEDEARs / Acciones USA (mismos tickers, mismo nombre en ambas categorías)
  AAPL: 'Apple', TSLA: 'Tesla', AMZN: 'Amazon', GOOGL: 'Alphabet (Google)', MSFT: 'Microsoft',
  NVDA: 'Nvidia', META: 'Meta Platforms', JPM: 'JPMorgan Chase', KO: 'Coca-Cola', DIS: 'Disney',
  NFLX: 'Netflix', 'BRK.B': 'Berkshire Hathaway', V: 'Visa', MA: 'Mastercard', WMT: 'Walmart',
  PG: 'Procter & Gamble', XOM: 'ExxonMobil', BA: 'Boeing', INTC: 'Intel', AMD: 'AMD',
  AIG: 'American International Group',
  // Bonos AR (soberanos en dólares)
  AL30: 'Bonar 2030', GD30: 'Global 2030', AL35: 'Bonar 2035', GD35: 'Global 2035',
  AE38: 'Bonar 2038', GD38: 'Global 2038', AL41: 'Bonar 2041', GD41: 'Global 2041',
  GD46: 'Global 2046', AL29: 'Bonar 2029',
};

function displayName(symbol) {
  return NAME_MAP[symbol] || symbol;
}

// Devuelve el primer valor numerico valido de una lista de candidatos --
// usado para tolerar que Finnhub exponga distintos alias del mismo campo
// segun el ticker/plan.
function firstNumber(...candidates) {
  for (const c of candidates) {
    if (typeof c === 'number' && !Number.isNaN(c)) return c;
  }
  return null;
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

// El "volumen" que reporta data912 para usa_stocks resulto ser una metrica
// local (probado con datos reales: AAPL rankea #2190 de 3158, MSFT #1991,
// GOOGL #3132 -- muy por debajo del limite de 500), no el volumen real de
// NYSE/NASDAQ -- mismo patron que ya vimos con Acciones AR. Sin este pin,
// las empresas mas grandes y reconocidas de EE.UU. quedaban afuera del
// treemap de "Acciones de Estados Unidos" antes de siquiera llegar a
// pedirle el market cap a Finnhub. Cubre S&P 500 top ~80 aprox.
// GOOG (Class C) se excluye a proposito -- es la misma empresa que GOOGL
// (Class A), duplicarla en el treemap cuenta a Alphabet dos veces.
const USA_MEGA_CAP_PINS = [
  'AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','BRK.B','JPM',
  'JNJ','V','PG','UNH','HD','MA','XOM','CVX','ABBV','PFE','KO','PEP','WMT',
  'DIS','NFLX','ADBE','CRM','ORCL','CSCO','INTC','AMD','QCOM','TXN','IBM',
  'GS','MS','BAC','WFC','C','SPGI','BLK','SCHW','AXP','LOW','NKE','MCD',
  'SBUX','COST','TGT','LMT','RTX','BA','CAT','DE','HON','UPS','UNP','GE',
  'MMM','T','VZ','CMCSA','ABT','TMO','DHR','LLY','MRK','BMY','GILD','AMGN',
  'ISRG','NOW','INTU','PYPL','UBER','SHOP','PLTR','AVGO','LIN','ACN','PM',
  'SPCX',
];
// Simbolos que representan la MISMA empresa que otro ya en la lista (otra
// clase de acciones) -- se excluyen aunque el volumen local los meta solos
// en el top 500, para no duplicar la misma compañia en el treemap.
const USA_DUPLICATE_CLASS_EXCLUDE = ['GOOG'];

// pin: simbolos que siempre tienen que quedar en la lista aunque el limite por
// volumen los deje afuera -- para activos reales de la cartera con poco volumen
// de CEDEAR (ej. AIG), sin los cuales el buscador de Mercados y el pricing en
// vivo del Portafolio de Manfredi los tratan como inexistentes.
function mapD912Rows(rows, { sortByVolume = true, limit = null, pin = [] } = {}) {
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
  if (limit && items.length > limit) {
    const kept = items.slice(0, limit);
    const keptSymbols = new Set(kept.map(it => it.symbol));
    const missingPins = pin
      .map(sym => items.find(it => it.symbol === sym))
      .filter(it => it && !keptSymbols.has(it.symbol));
    items = kept.concat(missingPins);
  }
  return items;
}

// ─── Logo + market cap (Finnhub /stock/profile2, misma respuesta para las dos) ─
// Guardados en UN SOLO blob de KV (no una key por simbolo) -- version previa
// de esto usaba `env.MERCADOS_KV.get()` por cada uno de los ~1.200 simbolos
// (Acciones AR + CEDEARs + Acciones USA + ADRs) en cada build, y cada
// lectura de KV cuenta como un subrequest para Cloudflare Workers igual que
// un fetch(): tumbo el endpoint entero con "Too many API requests by single
// Worker invocation" (buildPayload ya gasta ~25 subrequests en precios antes
// de llegar aca). Con el blob, el costo es 1 lectura + a lo sumo 1 escritura
// por build, sin importar cuantos simbolos haya.
// v3: el mismo pedido a /stock/profile2 que ya haciamos para el logo tambien
// trae marketCapitalization (en millones de USD) -- se pide gratis en la
// misma respuesta, sin sumar ningun fetch nuevo.
// v4: Acciones AR ahora solo enriquece simbolos en NAME_MAP (ver comentario
// en buildPayload) -- bump para descartar entradas viejas de simbolos como
// GGAL que quedaron con logo cacheado (fresco por 30 dias, no se reintenta)
// pero marketCap null por el choque de simbolo detectado con INTR/Finnhub.
// v5: se saco el techo especial mas estricto para Acciones AR. Probando con
// datos reales, Finnhub devuelve el market cap de las empresas argentinas
// (GGAL, BMA, SUPV, LOMA, CEPU, EDN, YPF, PAM, TEO, CRESY, IRS -- todas con
// country:"AR" en la respuesta) consistentemente ~1000x mas grande que el
// valor real (ej. GGAL da $10,6 billones en vez de ~$10 mil millones). Es
// un desvio de escala uniforme para TODO el mercado argentino -- no importa
// para este feature porque el treemap de Acciones AR nunca se compara al
// lado del de CEDEARs/Acciones USA, solo mide tamaño relativo DENTRO de la
// misma seccion, y ese orden relativo se mantiene igual de correcto este
// desviado o no. Bump para reintentar los simbolos que el techo anterior
// habia descartado.
const LOGO_BLOB_KEY = 'logos_v5';
const LOGO_POSITIVE_MS = 30 * 24 * 60 * 60 * 1000; // 30 dias -- no cambian de un dia para el otro
const LOGO_NEGATIVE_MS = 3 * 24 * 60 * 60 * 1000;  // 3 dias -- reintentar simbolos sin datos

async function loadLogoBlob(env) {
  if (!env.MERCADOS_KV) return {};
  try {
    const raw = await env.MERCADOS_KV.get(LOGO_BLOB_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.error('[mercados] logo blob parse:', e.message);
    return {};
  }
}

async function saveLogoBlob(env, blob) {
  if (!env.MERCADOS_KV) return;
  try {
    await env.MERCADOS_KV.put(LOGO_BLOB_KEY, JSON.stringify(blob));
  } catch (e) {
    console.error('[mercados] logo blob put:', e.message);
  }
}

// querySymbol vs symbol: para algunos tickers locales de Acciones AR
// (YPFD, PAMP, TECO2, CRES, IRSA), el ticker de BYMA no resuelve nada en
// Finnhub -- solo devuelve datos si se pide el ticker del ADR equivalente
// (YPF, PAM, TEO, CRESY, IRS respectivamente, ver AR_LOCAL_TO_ADR_SYMBOL).
async function fetchProfile(querySymbol, finnhubKey) {
  if (!finnhubKey) return { logo: null, marketCap: null, country: null };
  try {
    const url = `https://finnhub.io/api/v1/stock/profile2?symbol=${encodeURIComponent(querySymbol)}&token=${finnhubKey}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return { logo: null, marketCap: null, country: null };
    const data = await res.json();
    return {
      logo: (data && data.logo) || null,
      marketCap: (data && typeof data.marketCapitalization === 'number') ? data.marketCapitalization : null,
      country: (data && data.country) || null,
    };
  } catch (e) {
    console.error(`[mercados] profile/${querySymbol}:`, e.message);
    return { logo: null, marketCap: null, country: null };
  }
}

// Concurrencia acotada para las llamadas a Finnhub (no para KV, que ahora es
// una sola lectura/escritura fuera de este loop).
async function mapWithConcurrency(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}

// Techo de sanity para CEDEARs/Acciones USA/ADRs -- generoso, headroom
// arriba de la compañia mas grande del mundo hoy. Acciones AR NO usa este
// techo (ver maxMarketCapM=Infinity en el call site): el desvio de escala
// ~1000x que devuelve Finnhub para empresas argentinas (ver comentario de
// logos_v5 mas arriba) hace que justo las dos mas grandes -- GGAL (~USD
// 10,6 billones inflado) e YPF (~USD 32 billones inflado) -- superen
// incluso este techo generoso y quedarian nulificadas, cuando son
// exactamente las que mas se necesitan en el treemap. El desvio es uniforme
// para todo el mercado AR asi que no afecta el tamaño relativo entre
// activos de esa misma seccion (que es lo unico que le importa al treemap).
const MAX_MARKETCAP_M = 10000000; // USD 10 billones -- CEDEARs/USA/ADRs

// Para estos tickers locales de Acciones AR, el ticker de BYMA no resuelve
// nada en Finnhub -- solo el ticker del ADR equivalente trae datos (ver
// comentario en fetchProfile). El resultado se sigue guardando/mostrando
// bajo el ticker LOCAL (ej. "YPFD"), el alias solo se usa para el pedido.
const AR_LOCAL_TO_ADR_SYMBOL = { YPFD: 'YPF', PAMP: 'PAM', TECO2: 'TEO', CRES: 'CRESY', IRSA: 'IRS' };

// Acciones en circulacion (numero TOTAL de la compañia, no unidades ADR)
// para las empresas argentinas mas grandes de Acciones AR. Investigado a
// mano (SEC 20-F para las que tienen ADR en EE.UU., stockanalysis.com para
// el resto -- agosto 2026) porque NINGUNA fuente gratis (Finnhub, Yahoo
// Finance, data912, BYMA oficial, CNV) tiene market cap por ticker para el
// mercado local completo: Finnhub solo cubria los ~12 tickers con ADR en
// EE.UU., y encima con un desvio de escala ~1000x (ver comentario de
// logos_v5 mas arriba). Con esto calculamos el market cap nosotros mismos
// (acciones x precio en vivo, que ya tenemos de data912) -- el numero de
// acciones es lo unico que hay que actualizar a mano, y cambia rarisima vez
// (splits/emisiones), asi que alcanza con revisarlo cada tanto (mensual).
// YPFD: usar el TOTAL de la compañia (3.930M), no las 393,31M que reportan
// las fuentes centradas en el ADR (ratio ADR 1:10) -- confundir esto
// hubiera subvaluado YPF 10x contra el resto.
const AR_SHARES_OUTSTANDING = {
  GGAL: 1606253729, YPFD: 3930000000, BMA: 639413408, PAMP: 1340000000,
  BBAR: 612710000, CEPU: 1500000000, LOMA: 583483151, IRSA: 834570000,
  EDN: 875680000, TECO2: 2150000000, SUPV: 437730000, CRES: 709250000,
  BYMA: 7620000000, TXAR: 4520000000, ALUA: 2800000000, COME: 7000000000,
  TGSU2: 752760000, TGNO4: 439370000, TRAN: 444670000, VALO: 1150000000,
  CVH: 180640000,
};

// expectedCountry (opcional): valida el campo "country" que devuelve
// Finnhub contra el pais esperado antes de aceptar el logo/marketCap --
// reemplaza la lista curada fija que se usaba antes para Acciones AR.
// Encontrado con datos reales: el ticker local "INTR" (papel chico de BYMA)
// matcheaba por simbolo con Banco Inter (Brasil, country:"BR" en la
// respuesta) en vez de con la empresa argentina real. Chequear el pais en
// vivo deja pasar CUALQUIER empresa argentina real sin necesidad de una
// lista fija, y rechaza automaticamente los choques de simbolo con
// empresas de otros paises -- mas robusto y no requiere mantenimiento.
async function enrichWithLogos(items, finnhubKey, blob, budget, maxMarketCapM = MAX_MARKETCAP_M, expectedCountry = null) {
  if (!finnhubKey) return items;
  const now = Date.now();
  const sane = (mc) => (typeof mc === 'number' && mc > 0 && mc <= maxMarketCapM) ? mc : null;
  return mapWithConcurrency(items, 20, async (item) => {
    const entry = blob[item.symbol];
    if (entry && (now - entry.ts) < (entry.logo ? LOGO_POSITIVE_MS : LOGO_NEGATIVE_MS)) {
      return { ...item, logo: entry.logo, marketCap: sane(entry.marketCap) };
    }
    if (budget.remaining <= 0) {
      return { ...item, logo: entry ? entry.logo : null, marketCap: entry ? sane(entry.marketCap) : null };
    }
    budget.remaining--;
    const querySymbol = AR_LOCAL_TO_ADR_SYMBOL[item.symbol] || item.symbol;
    let { logo, marketCap, country } = await fetchProfile(querySymbol, finnhubKey);
    if (expectedCountry && country !== expectedCountry) { logo = null; marketCap = null; }
    blob[item.symbol] = { logo, marketCap, ts: now };
    budget.dirty = true;
    return { ...item, logo, marketCap: sane(marketCap) };
  });
}

// ─── Cripto: CDN estatico por simbolo (spothq/cryptocurrency-icons via
// jsdelivr, gratis, sin key, sin KV) -- funciona igual sea que el precio
// haya salido de CoinGecko o del fallback de Kraken (CoinGecko bloquea
// seguido las IPs de Cloudflare Workers). Sin verificacion de si el icono
// existe: el <img onerror> del frontend cae solo al circulo con la inicial.
function cryptoIconUrl(symbol) {
  return `https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/128/color/${symbol.toLowerCase()}.png`;
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

// ─── Cripto: CoinGecko → Binance ────────────────────────────────────────
// CoinGecko bloquea bastante seguido las IPs de salida de Cloudflare Workers
// (403), así que si falla o viene vacío caemos a la API pública de Binance.
async function fetchCriptoCoinGecko() {
  const url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=150&page=1&sparkline=false&price_change_percentage=24h';
  const resp = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
    signal: AbortSignal.timeout(10000),
  });
  if (!resp.ok) throw new Error(`CoinGecko HTTP ${resp.status}`);
  const rows = await resp.json();
  if (!Array.isArray(rows) || !rows.length) throw new Error('CoinGecko: respuesta vacía');
  return rows.map(c => ({
    symbol: (c.symbol || '').toUpperCase(),
    name: c.name,
    price: c.current_price,
    change: c.price_change_percentage_24h,
    volume: c.total_volume || 0,
    marketCap: (typeof c.market_cap === 'number' && c.market_cap > 0) ? c.market_cap : null,
  }));
}

// Kraken funciona bien desde IPs de Cloudflare Workers (Binance las bloquea
// con 403). /Ticker sin parámetro "pair" devuelve TODOS los pares — filtramos
// los cotizados en USD. Ordenamos por volumen EN USD (precio × volumen en el
// activo base), no por volumen crudo: si no, monedas tipo SHIB/PEPE con
// billones de tokens circulando le ganan a BTC en la comparación.
// Kraken nombra sus 10 pares originales con prefijo legacy X+código+Z (ej.
// XXBTZUSD), pero esa misma terminación "ZUSD" también aparece en tickers
// modernos que legítimamente terminan en Z (AI16ZUSD = AI16Z, XTZUSD = XTZ).
// No hay forma genérica de distinguirlos, así que los 10 legacy van a mano.
const KRAKEN_LEGACY_SYMBOLS = {
  XETCZUSD: 'ETC', XETHZUSD: 'ETH', XLTCZUSD: 'LTC', XMLNZUSD: 'MLN',
  XREPZUSD: 'REP', XXBTZUSD: 'BTC', XXLMZUSD: 'XLM', XXMRZUSD: 'XMR',
  XXRPZUSD: 'XRP', XZECZUSD: 'ZEC',
};

async function fetchCriptoKraken() {
  const resp = await fetch('https://api.kraken.com/0/public/Ticker', { signal: AbortSignal.timeout(10000) });
  if (!resp.ok) throw new Error(`Kraken HTTP ${resp.status}`);
  const json = await resp.json();
  const result = json.result;
  if (!result) throw new Error('Kraken: respuesta vacía');
  return Object.entries(result)
    .filter(([pair]) => pair.endsWith('USD'))
    .map(([pair, t]) => {
      const symbol = KRAKEN_LEGACY_SYMBOLS[pair] || pair.slice(0, -3);
      const last = parseFloat(t.c?.[0]);
      const open = parseFloat(t.o);
      const change = open > 0 ? ((last - open) / open * 100) : null;
      const baseVolume = parseFloat(t.v?.[1]) || 0;
      return { symbol, name: symbol, price: last, change, volume: last * baseVolume };
    })
    .filter(r => r.symbol && r.price > 0)
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 200);
}

// CoinGecko bloquea/limita seguido las IPs compartidas de Cloudflare Workers
// (confirmado: desde una IP normal responde 200 siempre, desde el worker
// falla ~1 de cada 2-3 pedidos) -- es el unico que trae market_cap gratis
// (Kraken, el fallback, no lo tiene), asi que vale la pena un par de
// reintentos cortos antes de resignarse al fallback sin market cap.
async function fetchCripto() {
  let items;
  for (let attempt = 0; attempt < 3 && !items; attempt++) {
    if (attempt > 0) await new Promise(r => setTimeout(r, 400));
    try {
      items = await fetchCriptoCoinGecko();
    } catch (e) {
      console.error(`[mercados] coingecko (intento ${attempt + 1}):`, e.message);
    }
  }
  if (!items) {
    try {
      items = await fetchCriptoKraken();
    } catch (e) {
      console.error('[mercados] kraken:', e.message);
      items = [];
    }
  }
  return items.map(c => ({ ...c, logo: cryptoIconUrl(c.symbol) }));
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
        const spark = data.slice(-30).map(d => d.valor).filter(v => v != null);
        return { price: last.valor, change, spark };
      }
    }
  } catch (e) { console.error('[mercados] Merval/ArgentinaDatos:', e.message); }
  const viaFinnhub = await fetchFinnhub('BYMA:MERVAL', finnhubKey);
  if (viaFinnhub) return viaFinnhub;
  return await fetchYahoo('^MERV');
}

// ─── Commodities (Yahoo futures) ──────────────────────────────────────────
const COMMODITY_YAHOO_MAP = {
  XAU: 'GC=F', XAG: 'SI=F', WTI: 'CL=F', BRENT: 'BZ=F', CORN: 'ZC=F', NATGAS: 'NG=F', COPPER: 'HG=F',
};
const COMMODITY_NAMES = {
  XAU: 'Oro', XAG: 'Plata', WTI: 'Petróleo WTI', BRENT: 'Petróleo Brent',
  CORN: 'Maíz', NATGAS: 'Gas Natural', COPPER: 'Cobre',
};

async function fetchCommodities() {
  const results = await Promise.all(Object.entries(COMMODITY_YAHOO_MAP).map(async ([id, ySymbol]) => {
    const r = await fetchYahoo(ySymbol);
    return { symbol: id, name: COMMODITY_NAMES[id], price: r?.price ?? null, change: r?.change ?? null, volume: 0 };
  }));
  return results;
}

// ─── Histórico bajo demanda (para el gráfico del modal de detalle) ────────
// A diferencia del resto de este worker, esto NO se cachea en KV: solo se
// pide cuando alguien hace click en un activo puntual, así que el volumen
// de pedidos es bajo y no vale la pena gastar el cupo de escrituras de KV.
function closesFromD912History(rows, n) {
  if (!Array.isArray(rows) || !rows.length) return [];
  return rows.filter(r => r.c != null).slice(-n).map(r => r.c);
}

async function fetchD912Closes(endpoint, symbol, n = 30) {
  const resp = await fetch(`https://data912.com/historical/${endpoint}/${encodeURIComponent(symbol)}`, { signal: AbortSignal.timeout(10000) });
  if (!resp.ok) throw new Error(`data912 historical HTTP ${resp.status}`);
  const rows = await resp.json();
  return closesFromD912History(rows, n);
}

async function fetchYahooCloses(symbol, n = 30) {
  // "range" tiene que cubrir al menos n dias habiles, si no Yahoo devuelve
  // menos velas de las pedidas y closes.slice(-n) queda corto en silencio.
  const range = n <= 63 ? '3mo' : (n <= 126 ? '6mo' : '1y');
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=${range}`;
  const resp = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(10000) });
  if (!resp.ok) throw new Error(`Yahoo HTTP ${resp.status}`);
  const json = await resp.json();
  const closes = json?.chart?.result?.[0]?.indicators?.quote?.[0]?.close;
  if (!Array.isArray(closes)) throw new Error('Yahoo: sin datos');
  return closes.filter(v => v != null).slice(-n);
}

// Reverso de KRAKEN_LEGACY_SYMBOLS: "BTC" -> "XXBTZUSD", etc.
const KRAKEN_SYMBOL_TO_PAIR = Object.fromEntries(
  Object.entries(KRAKEN_LEGACY_SYMBOLS).map(([pair, symbol]) => [symbol, pair])
);

async function fetchKrakenCloses(symbol, n = 30) {
  const pair = KRAKEN_SYMBOL_TO_PAIR[symbol] || `${symbol}USD`;
  const url = `https://api.kraken.com/0/public/OHLC?pair=${encodeURIComponent(pair)}&interval=1440`;
  const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
  if (!resp.ok) throw new Error(`Kraken HTTP ${resp.status}`);
  const json = await resp.json();
  const series = json.result && Object.values(json.result)[0];
  if (!Array.isArray(series) || !series.length) throw new Error('Kraken: sin datos');
  return series.slice(-n).map(row => parseFloat(row[4]));
}

async function fetchDolarCloses(casa, n = 30) {
  const url = `https://api.argentinadatos.com/v1/cotizaciones/dolares/${encodeURIComponent(casa)}`;
  const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
  if (!resp.ok) throw new Error(`ArgentinaDatos HTTP ${resp.status}`);
  const rows = await resp.json();
  if (!Array.isArray(rows) || !rows.length) throw new Error('ArgentinaDatos: sin datos');
  return rows.slice(-n).map(r => r.venta);
}

async function fetchHistoricalCloses(category, symbol, n = 30) {
  if (category === 'arg_stocks') return fetchD912Closes('stocks', symbol, n);
  if (category === 'arg_cedears') return fetchD912Closes('cedears', symbol, n);
  if (category === 'arg_bonds') return fetchD912Closes('bonds', symbol, n);
  if (category === 'usa_stocks' || category === 'usa_adrs') return fetchYahooCloses(symbol, n);
  if (category === 'commodities') {
    const ySymbol = COMMODITY_YAHOO_MAP[symbol];
    if (!ySymbol) throw new Error('Commodity desconocida');
    return fetchYahooCloses(ySymbol, n);
  }
  if (category === 'cripto') return fetchKrakenCloses(symbol, n);
  if (category === 'dolares') return fetchDolarCloses(symbol.toLowerCase(), n);
  throw new Error('Categoría desconocida');
}

// ─── Sparks de los carteles fijos (columna izquierda) ─────────────────────
// Llamados extra solo para dibujar la líneita de tendencia — si alguno falla
// no rompe nada, esa card queda sin gráfico pero con precio/variación igual.
async function fetchFeaturedSparks() {
  const safe = async (fn) => { try { return await fn(); } catch (e) { return []; } };
  const [oro, wti, spx, ndx, btc, ccl] = await Promise.all([
    safe(() => fetchYahooCloses('GC=F', 20)),
    safe(() => fetchYahooCloses('CL=F', 20)),
    safe(() => fetchYahooCloses('SPY', 20)),
    safe(() => fetchYahooCloses('QQQ', 20)),
    safe(() => fetchKrakenCloses('BTC', 20)),
    safe(() => fetchDolarCloses('contadoconliqui', 20)),
  ]);
  return { oro, wti, spx, ndx, btc, ccl };
}

// ─── Agregación completa ──────────────────────────────────────────────────
async function buildPayload(env) {
  const finnhubKey = env.FINNHUB_KEY;
  const twelveDataKey = env.TWELVEDATA_KEY;

  const [
    argStocksRaw, argCedearsRaw, usaStocksRaw, usaAdrsRaw, argBondsRaw,
    cripto, commodities, dolares, divisas,
    oro, spx, ndx, merval, sparks,
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
    fetchFeaturedSparks(),
  ]);

  const wti = commodities.find(c => c.symbol === 'WTI');
  const btc = cripto.find(r => r.symbol === 'BTC') || null;

  const featured = [
    { id: 'oro', flag: '🥇', name: 'Oro', unit: 'US$', price: oro?.price ?? null, change: oro?.change ?? null, spark: sparks.oro },
    { id: 'merval', flag: '🇦🇷', name: 'Merval', unit: '', price: merval?.price ?? null, change: merval?.change ?? null, spark: merval?.spark ?? [] },
    { id: 'sp500', flag: '🇺🇸', name: 'S&P 500', unit: 'US$', price: spx?.price ?? null, change: spx?.change ?? null, spark: sparks.spx },
    { id: 'nasdaq', flag: '🇺🇸', name: 'Nasdaq 100', unit: 'US$', price: ndx?.price ?? null, change: ndx?.change ?? null, spark: sparks.ndx },
    { id: 'btc', flag: '₿', name: 'Bitcoin', unit: 'US$', price: btc?.price ?? null, change: btc?.change ?? null, spark: sparks.btc },
    { id: 'ccl', flag: '🇦🇷', name: 'Dólar CCL', unit: '$', price: dolares.find(d => d.symbol === 'CONTADOCONLIQUI')?.price ?? null, change: null, spark: sparks.ccl },
    { id: 'wti', flag: '🛢️', name: 'Petróleo WTI', unit: 'US$', price: wti?.price ?? null, change: wti?.change ?? null, spark: sparks.wti },
  ];

  // Logos via Finnhub -- Acciones AR, CEDEARs, Acciones USA y ADRs. Un solo
  // blob de KV para las 4 (ver comentario en enrichWithLogos): se carga una
  // vez, se comparte, y se guarda una vez al final si hubo simbolos nuevos.
  //
  // Acciones AR va PRIMERO y awaited por separado, no en el mismo Promise.all
  // que las otras 3 -- si las 4 corren concurrentes compitiendo por el mismo
  // cupo compartido, CEDEARs/Acciones USA (cientos de simbolos, arrancan con
  // mas "workers" en paralelo dentro de si mismas) le ganan la carrera casi
  // siempre, dejando a Acciones AR (solo 95 simbolos en total) practicamente
  // sin turno build tras build (confirmado con datos reales: 6/95 despues de
  // muchos ciclos, mientras las otras ya estaban en 200-460 de cobertura).
  // Dandole prioridad, se completa sola en ~5 builds (95/20) y despues el
  // cupo entero queda libre para las demas -- mismo total de 20 por build,
  // solo cambia el orden de reparto.
  //
  // Ademas, para Acciones AR se valida el "country" que devuelve Finnhub
  // contra 'AR' antes de aceptar el LOGO (ver comentario en enrichWithLogos)
  // -- reemplaza la lista curada fija que se usaba antes: ahora TODOS los
  // ~95 simbolos son candidatos, no solo los ~20 conocidos de antemano, y
  // el choque de simbolo tipo INTR (matcheaba con Banco Inter de Brasil,
  // country:"BR") se descarta solo por el chequeo de pais.
  //
  // El market cap que devuelve Finnhub para Acciones AR se descarta y se
  // reemplaza por AR_SHARES_OUTSTANDING x precio en vivo -- Finnhub solo
  // cubre los ~12 tickers con ADR en EE.UU. (dejando afuera BYMA, TXAR,
  // ALUA, COME, TGSU2, TGNO4, TRAN, VALO, CVH, que tambien queremos en el
  // treemap), y ademas todo lo que SI cubre viene con el mismo desvio de
  // escala ~1000x -- mezclar ambas fuentes (Finnhub para 12, calculo propio
  // para el resto) haria que el tamaño relativo entre las dos mitades del
  // treemap fuera incoherente entre si.
  const logoBlob = await loadLogoBlob(env);
  const logoBudget = { remaining: 20, dirty: false };
  const argStocksItems = (await enrichWithLogos(mapD912Rows(argStocksRaw), finnhubKey, logoBlob, logoBudget, Infinity, 'AR'))
    .map(it => {
      const shares = AR_SHARES_OUTSTANDING[it.symbol];
      const marketCap = (shares && typeof it.price === 'number') ? (shares * it.price / 1e6) : null;
      return { ...it, marketCap };
    });
  const [argCedearsItems, usaStocksItems, usaAdrsItems] = await Promise.all([
    enrichWithLogos(mapD912Rows(argCedearsRaw, { limit: 400, pin: ['AIG'] }), finnhubKey, logoBlob, logoBudget),
    enrichWithLogos(mapD912Rows(usaStocksRaw.filter(r => !USA_DUPLICATE_CLASS_EXCLUDE.includes(r.symbol)), { limit: 500, pin: USA_MEGA_CAP_PINS }), finnhubKey, logoBlob, logoBudget),
    enrichWithLogos(mapD912Rows(usaAdrsRaw), finnhubKey, logoBlob, logoBudget),
  ]);
  if (logoBudget.dirty) await saveLogoBlob(env, logoBlob);

  const categorias = {
    arg_stocks:  { currency: 'ARS', total: argStocksRaw.length,  items: argStocksItems },
    arg_cedears: { currency: 'ARS', total: argCedearsRaw.length, items: argCedearsItems },
    usa_stocks:  { currency: 'USD', total: usaStocksRaw.length,  items: usaStocksItems },
    usa_adrs:    { currency: 'USD', total: usaAdrsRaw.length,    items: usaAdrsItems },
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

    if (url.pathname === '/historico') {
      const category = url.searchParams.get('category') || '';
      const symbol = url.searchParams.get('symbol') || '';
      const n = Math.min(HISTORICO_MAX_N, Math.max(1, parseInt(url.searchParams.get('n'), 10) || 30));
      if (!category || !symbol) {
        return new Response(JSON.stringify({ error: 'Faltan category y symbol' }), { status: 400, headers });
      }
      const cacheKey = `historico_v1:${category}:${symbol}:${n}`;
      const forceRefresh = url.searchParams.get('refresh') === '1';
      try {
        if (!forceRefresh) {
          const cached = await env.MERCADOS_KV.get(cacheKey);
          if (cached) return new Response(cached, { headers });
        }
        const closes = await fetchHistoricalCloses(category, symbol, n);
        if (!closes.length) throw new Error('Sin datos históricos');
        const json = JSON.stringify({
          symbol, category, closes,
          min: Math.min(...closes), max: Math.max(...closes),
        });
        await env.MERCADOS_KV.put(cacheKey, json, { expirationTtl: HISTORICO_CACHE_TTL_SECONDS });
        return new Response(json, { headers });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 404, headers });
      }
    }

    // GET /fundamentals?symbol=AAPL -- ROE / P/E / dividend yield ponderados para
    // "Tu Portafolio". Reusa la FINNHUB_KEY que ya esta configurada (misma que
    // usa buildPayload() para SPY/QQQ/Merval) -- ninguna cuenta ni key nueva.
    // Cache largo (24h) porque estos datos fundamentales cambian a lo sumo una
    // vez por trimestre, no vale la pena pedirlos seguido.
    if (url.pathname === '/fundamentals') {
      const symbol = url.searchParams.get('symbol') || '';
      if (!symbol) {
        return new Response(JSON.stringify({ error: 'Falta symbol' }), { status: 400, headers });
      }
      const cacheKey = `fundamentals_v1:${symbol.toUpperCase()}`;
      const forceRefresh = url.searchParams.get('refresh') === '1';
      try {
        if (!forceRefresh) {
          const cached = await env.MERCADOS_KV.get(cacheKey);
          if (cached) return new Response(cached, { headers });
        }
        const finnhubKey = env.FINNHUB_KEY;
        if (!finnhubKey) throw new Error('FINNHUB_KEY no configurada');
        const [metricResp, profileResp] = await Promise.all([
          fetch(
            `https://finnhub.io/api/v1/stock/metric?symbol=${encodeURIComponent(symbol)}&metric=all&token=${finnhubKey}`,
            { signal: AbortSignal.timeout(10000) }
          ),
          // /stock/profile2 -- sector (finnhubIndustry) y pais de la empresa, para
          // "Concentracion sectorial"/"Concentracion geografica" en Tu Portafolio.
          // Free tier de Finnhub la cubre igual que /stock/metric, sin key nueva.
          fetch(
            `https://finnhub.io/api/v1/stock/profile2?symbol=${encodeURIComponent(symbol)}&token=${finnhubKey}`,
            { signal: AbortSignal.timeout(10000) }
          )
        ]);
        if (!metricResp.ok) throw new Error(`Finnhub HTTP ${metricResp.status}`);
        const data = await metricResp.json();
        const m = data && data.metric;
        if (!m) throw new Error('Finnhub: sin datos de metric');
        // Nombres de campo defensivos: Finnhub no siempre expone el mismo alias
        // para todos los tickers/planes, probamos varias variantes conocidas.
        const roe = firstNumber(m.roeTTM, m.roeRfy, m.roeAnnual);
        const pe = firstNumber(m.peBasicExclExtraTTM, m.peTTM, m.peExclExtraTTM, m.peAnnual);
        const divYield = firstNumber(m.currentDividendYieldTTM, m.dividendYieldIndicatedAnnual, m.dividendYield5Y);
        let sector = null, country = null, marketCap = null;
        if (profileResp.ok) {
          const profile = await profileResp.json();
          sector = (profile && profile.finnhubIndustry) || null;
          country = (profile && profile.country) || null;
          marketCap = (profile && typeof profile.marketCapitalization === 'number') ? profile.marketCapitalization : null;
        }
        const json = JSON.stringify({ symbol: symbol.toUpperCase(), roe, pe, divYield, sector, country, marketCap });
        await env.MERCADOS_KV.put(cacheKey, json, { expirationTtl: 86400 });
        return new Response(json, { headers });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 404, headers });
      }
    }

    // GET /admin/enrich?token=...&symbols=AAPL,MSFT,...&ar=1
    // Recarga a demanda logos/market cap de un lote chico de simbolos contra
    // Finnhub y los persiste en el mismo blob de KV que usa buildPayload()
    // (logos_v5) -- pensado para disparar manualmente en tandas (no expuesto
    // en el sitio, no llamado por buildPayload) cuando se quiere refrescar
    // CEDEARs/Acciones USA/ADRs "de una", sin esperar el trickle de 20 por
    // ciclo de 2 min. Tope duro de 25 simbolos por pedido para no acercarse
    // al limite de subrequests por invocacion de Cloudflare Workers (mismo
    // problema que rompio produccion la primera vez, ver comentario de
    // logos_v2/v3 mas arriba) -- para recargar todo el universo (~1.100
    // simbolos entre CEDEARs/Acciones USA/ADRs) hay que llamarlo en un loop
    // externo, ~45-55 pedidos de a 20-25 simbolos.
    if (url.pathname === '/admin/enrich') {
      const token = url.searchParams.get('token') || '';
      if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
        return new Response(JSON.stringify({ error: 'unauthorized' }), { status: 401, headers });
      }
      const finnhubKey = env.FINNHUB_KEY;
      if (!finnhubKey) {
        return new Response(JSON.stringify({ error: 'FINNHUB_KEY no configurada' }), { status: 500, headers });
      }
      const isAR = url.searchParams.get('ar') === '1';
      const symbols = (url.searchParams.get('symbols') || '')
        .split(',').map(s => s.trim().toUpperCase()).filter(Boolean).slice(0, 25);
      if (!symbols.length) {
        return new Response(JSON.stringify({ error: 'Falta symbols (separados por coma, maximo 25)' }), { status: 400, headers });
      }
      const blob = await loadLogoBlob(env);
      const now = Date.now();
      const results = await mapWithConcurrency(symbols, 20, async (symbol) => {
        const querySymbol = AR_LOCAL_TO_ADR_SYMBOL[symbol] || symbol;
        let { logo, marketCap, country } = await fetchProfile(querySymbol, finnhubKey);
        if (isAR && country !== 'AR') { logo = null; marketCap = null; }
        blob[symbol] = { logo, marketCap, ts: now };
        return { symbol, logo: !!logo, marketCap };
      });
      await saveLogoBlob(env, blob);
      return new Response(JSON.stringify({ processed: results.length, results }), { headers });
    }

    if (url.pathname === '/debug-cripto') {
      const attempts = {};
      const tryOne = async (name, fn) => {
        try {
          const rows = await fn();
          attempts[name] = { ok: true, count: rows.length, sample: rows[0] };
        } catch (e) {
          attempts[name] = { ok: false, error: e.message };
        }
      };
      await tryOne('coingecko', fetchCriptoCoinGecko);
      await tryOne('kraken', fetchCriptoKraken);
      return new Response(JSON.stringify(attempts, null, 2), { headers });
    }

    return new Response('Manfredi Mercados Worker OK', { headers: { 'Content-Type': 'text/plain' } });
  },
};
