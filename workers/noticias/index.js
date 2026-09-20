// workers/noticias/index.js
// Worker de Cloudflare para noticias de mercado (Argentina + Wall Street).
// Mismo patrón cache-aside que manfredi-calendario: KV + cron de pre-calentado.

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

const KV_KEY = 'noticias';
const KV_TTL = 60 * 45; // 45 min — dentro del rango 30-60 pedido; el cron de 30 min lo mantiene tibio.

// Ámbito/Cronista/Bloomberg Línea confirmados estables desde el Worker.
// Infobae devuelve 0 items de forma consistente al pedirse desde IPs de
// Cloudflare Workers (probable bloqueo anti-bot del lado del sitio, el mismo
// feed funciona perfecto pedido desde fuera) -- se deja con max bajo como
// bonus best-effort, pero el resto de las fuentes ya suma 10 por su cuenta
// para no depender de que Infobae responda.
const FUENTES_ARG = [
  { fuente: 'Ámbito',         url: 'https://www.ambito.com/rss/economia.xml',                                          max: 4 },
  { fuente: 'Infobae',        url: 'https://www.infobae.com/arc/outboundfeeds/rss/category/economia/',                 max: 2 },
  { fuente: 'El Cronista',    url: 'https://www.cronista.com/arc/outboundfeeds/rss/category/economia-politica/',       max: 4 },
  { fuente: 'Bloomberg Línea', url: 'https://www.bloomberglinea.com/arc/outboundfeeds/rss/latinoamerica/argentina.xml', max: 2 },
];

const FUENTES_US = [
  { fuente: 'Yahoo Finance',  url: 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US', max: 3 },
  { fuente: 'Investing.com',  url: 'https://www.investing.com/rss/news_25.rss',                                       max: 3 },
  { fuente: 'Seeking Alpha',  url: 'https://seekingalpha.com/market_currents.xml',                                    max: 2 },
  { fuente: 'The Economist',  url: 'https://www.economist.com/finance-and-economics/rss.xml',                          max: 2 },
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS_HEADERS });

    if (url.pathname === '/noticias') {
      try {
        const cached = await env.NOTICIAS_KV.get(KV_KEY);
        if (cached) return new Response(cached, { headers: CORS_HEADERS });

        const result = await generarNoticias();
        const json = JSON.stringify(result);
        await env.NOTICIAS_KV.put(KV_KEY, json, { expirationTtl: KV_TTL });
        return new Response(json, { headers: CORS_HEADERS });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS_HEADERS });
      }
    }

    if (url.pathname === '/noticias/refresh') {
      try {
        const result = await generarNoticias();
        const json = JSON.stringify(result);
        await env.NOTICIAS_KV.put(KV_KEY, json, { expirationTtl: KV_TTL });
        return new Response(json, { headers: CORS_HEADERS });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS_HEADERS });
      }
    }

    return new Response('Manfredi Noticias Worker OK', { headers: { 'Content-Type': 'text/plain' } });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil((async () => {
      const result = await generarNoticias();
      await env.NOTICIAS_KV.put(KV_KEY, JSON.stringify(result), { expirationTtl: KV_TTL });
    })());
  },
};

async function generarNoticias() {
  const [argentina, wallstreet] = await Promise.all([
    fetchGrupo(FUENTES_ARG),
    fetchGrupo(FUENTES_US),
  ]);
  return { argentina, wallstreet, updated: new Date().toISOString() };
}

async function fetchGrupo(fuentes) {
  const resultados = await Promise.all(fuentes.map(f => fetchFeed(f.url, f.max, f.fuente)));
  return resultados.flat();
}

async function fetchFeed(url, max, fuente) {
  try {
    const resp = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)', 'Accept': 'application/rss+xml, application/xml, text/xml' },
      signal: AbortSignal.timeout(10000),
    });
    if (!resp.ok) return [];
    const xml = await resp.text();
    const items = parseRSS(xml, max).map(item => ({ ...item, fuente }));
    // Las notas cuyo RSS no trae imagen la toman del og:image de la página.
    await Promise.all(items.map(async item => {
      if (!item.imagen && item.link) item.imagen = await fetchOgImage(item.link);
    }));
    return items;
  } catch (e) {
    console.warn(`[noticias] ${fuente}:`, e.message);
    return [];
  }
}

// Parser RSS liviano por regex (sin DOMParser disponible en Workers).
function parseRSS(xml, maxItems) {
  const items = [];
  const itemBlocks = xml.match(/<item[\s\S]*?<\/item>/g) || [];
  for (const block of itemBlocks.slice(0, maxItems)) {
    const titulo = extractTag(block, 'title');
    const link = extractTag(block, 'link');
    let resumen = extractTag(block, 'description');
    if (!titulo) continue;
    resumen = resumen.replace(/<[^>]+>/g, '').trim().slice(0, 250);
    const pubDateRaw = extractTag(block, 'pubDate') || extractTag(block, 'dc:date') || extractTag(block, 'published');
    const parsed = pubDateRaw ? new Date(pubDateRaw) : null;
    const fecha = parsed && !isNaN(parsed.getTime()) ? parsed.toISOString() : null;
    items.push({ titulo: titulo.trim(), link: link.trim(), resumen, fecha, imagen: extractImage(block) });
  }
  return items;
}

function extractTag(block, tag) {
  const cdataMatch = block.match(new RegExp(`<${tag}[^>]*>\\s*<!\\[CDATA\\[([\\s\\S]*?)\\]\\]>\\s*<\\/${tag}>`, 'i'));
  if (cdataMatch) return cdataMatch[1];
  const plainMatch = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i'));
  return plainMatch ? plainMatch[1] : '';
}

// Imagen de la nota: media:content / media:thumbnail / enclosure de imagen, o la
// primera <img> embebida en description/content:encoded. Devuelve '' si no hay.
function extractImage(block) {
  const patterns = [
    /<media:content[^>]*?url=["']([^"']+)["'][^>]*>/i,
    /<media:thumbnail[^>]*?url=["']([^"']+)["'][^>]*>/i,
    /<enclosure[^>]*?url=["']([^"']+)["'][^>]*?type=["']image\/[^"']*["']/i,
    /<enclosure[^>]*?type=["']image\/[^"']*["'][^>]*?url=["']([^"']+)["']/i,
    /<img[^>]*?src=["']([^"']+)["']/i,
  ];
  for (const re of patterns) {
    const m = block.match(re);
    if (!m) continue;
    const url = m[1].replace(/&amp;/g, '&').trim();
    if (/^https?:\/\//i.test(url) && !/\.(mp4|mov|webm)(\?|$)/i.test(url)) return url;
  }
  return '';
}

// og:image de la nota (best-effort, 5 s). Se descartan las imágenes genéricas del
// sitio (logo compartido por todas las notas), que no aportan nada como portada.
async function fetchOgImage(link) {
  try {
    const resp = await fetch(link, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ManfrediInvestment/1.0)', 'Accept': 'text/html' },
      signal: AbortSignal.timeout(5000),
    });
    if (!resp.ok) return '';
    const html = (await resp.text()).slice(0, 200000);
    const m = html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i)
           || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);
    const url = m ? m[1].replace(/&amp;/g, '&').trim() : '';
    if (!/^https?:\/\//i.test(url) || /og_image|default[-_]?share|logo/i.test(url)) return '';
    return url;
  } catch (e) {
    return '';
  }
}
