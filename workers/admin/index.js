// workers/admin/index.js
// Worker "manfredi-admin": datos de Cloudflare (trafico del sitio + uso y
// errores de los workers) para el Panel de creador. Solo lo pueden leer las
// cuentas de CREADORES, validadas con el ID token de Firebase.
//
// Necesita UN secreto (lo crea Nacho en Cloudflare, solo lectura):
//   npx wrangler secret put CF_API_TOKEN --config workers/admin/wrangler.toml
// Permisos del token: Account > Account Analytics: Read, Account > Workers Scripts: Read,
// Zone > Zone: Read, Zone > Analytics: Read (zona manfredinvestment.com).

const CREADORES = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
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
        const path = new URL(request.url).pathname;
        try {
            const u = await usuarioDelToken(request);
            if (!u) return json({ error: 'No autenticado' }, 401);
            if (!CREADORES.includes(u.email)) return json({ error: 'Solo para creadores' }, 403);
            if (!env.CF_API_TOKEN) return json({ error: 'sin_token', mensaje: 'Falta el secreto CF_API_TOKEN en el worker manfredi-admin' }, 503);

            if (path === '/trafico' && request.method === 'GET') return json(await trafico(env));
            if (path === '/workers' && request.method === 'GET') return json(await workersUso(env));
            return json({ error: 'Ruta no encontrada' }, 404);
        } catch (e) {
            return json({ error: e.message }, 500);
        }
    }
};

// ─── Cloudflare API ──────────────────────────────────────────────────────────
async function cf(env, path) {
    const r = await fetch('https://api.cloudflare.com/client/v4' + path, { headers: { Authorization: 'Bearer ' + env.CF_API_TOKEN } });
    const d = await r.json();
    if (!d.success) throw new Error('Cloudflare ' + path.split('?')[0] + ': ' + ((d.errors && d.errors[0] && d.errors[0].message) || r.status));
    return d.result;
}
async function gql(env, query, variables) {
    const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + env.CF_API_TOKEN, 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, variables })
    });
    const d = await r.json();
    if (d.errors && d.errors.length) throw new Error(d.errors[0].message);
    return d.data;
}
const isoDia = d => d.toISOString().slice(0, 10);

// GET /trafico -- 30 dias. Dos fuentes, cada una opcional:
//  - zona (todo pedido que pasa por Cloudflare: requests, visitantes unicos, paises)
//  - Web Analytics (visitas reales de navegador: paginas, de donde vienen, dispositivos)
async function trafico(env) {
    const hasta = new Date(), desde = new Date(Date.now() - 29 * 86400e3);
    const out = { desde: isoDia(desde), hasta: isoDia(hasta), zona: null, web: null, errores: {} };

    try {
        const zonas = await cf(env, '/zones?name=' + encodeURIComponent(env.SITE_HOST));
        if (!zonas.length) throw new Error('No encontré la zona ' + env.SITE_HOST);
        const d = await gql(env, `query($z:String!,$a:Date!,$b:Date!){viewer{zones(filter:{zoneTag:$z}){
            httpRequests1dGroups(limit:31,filter:{date_geq:$a,date_leq:$b},orderBy:[date_ASC]){
              dimensions{date} sum{requests pageViews bytes threats countryMap{clientCountryName requests}} uniq{uniques}}}}}`,
            { z: zonas[0].id, a: out.desde, b: out.hasta });
        const dias = d.viewer.zones[0].httpRequests1dGroups;
        const paises = {};
        dias.forEach(g => (g.sum.countryMap || []).forEach(c => { paises[c.clientCountryName] = (paises[c.clientCountryName] || 0) + c.requests; }));
        out.zona = {
            dias: dias.map(g => ({ fecha: g.dimensions.date, requests: g.sum.requests, paginas: g.sum.pageViews, unicos: g.uniq.uniques, bytes: g.sum.bytes, amenazas: g.sum.threats })),
            paises: Object.entries(paises).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([pais, requests]) => ({ pais, requests }))
        };
    } catch (e) { out.errores.zona = e.message; }

    try {
        const sitios = await cf(env, `/accounts/${env.CF_ACCOUNT_ID}/rum/site_info/list?per_page=50`);
        const sitio = (sitios || []).find(s => (s.ruleset && s.ruleset.zone_name === env.SITE_HOST) || s.host === env.SITE_HOST || (s.host || '').endsWith('.pages.dev')) || (sitios || [])[0];
        if (!sitio) throw new Error('Web Analytics no está activado');
        const v = { a: env.CF_ACCOUNT_ID, s: sitio.site_tag, d1: desde.toISOString(), d2: hasta.toISOString() };
        const grupo = (alias, dim, limit, order) => `${alias}: rumPageloadEventsAdaptiveGroups(limit:${limit}, filter:{siteTag:$s, datetime_geq:$d1, datetime_leq:$d2}, orderBy:[${order}]){ count sum{visits} dimensions{${dim}} }`;
        const d = await gql(env, `query($a:String!,$s:String!,$d1:Time!,$d2:Time!){viewer{accounts(filter:{accountTag:$a}){
            ${grupo('serie', 'date', 31, 'date_ASC')}
            ${grupo('paginas', 'requestPath', 12, 'count_DESC')}
            ${grupo('origen', 'refererHost', 10, 'count_DESC')}
            ${grupo('paises', 'countryName', 10, 'count_DESC')}
            ${grupo('dispositivos', 'deviceType', 5, 'count_DESC')}
          }}}`, v);
        const a = d.viewer.accounts[0];
        const map = (arr, k) => arr.map(g => ({ [k]: g.dimensions[k === 'fecha' ? 'date' : k], vistas: g.count, visitas: g.sum.visits }));
        out.web = {
            sitio: sitio.host || sitio.site_tag,
            serie: map(a.serie, 'fecha'),
            paginas: a.paginas.map(g => ({ ruta: g.dimensions.requestPath, vistas: g.count, visitas: g.sum.visits })),
            origen: a.origen.map(g => ({ origen: g.dimensions.refererHost || '(directo)', vistas: g.count, visitas: g.sum.visits })),
            paises: a.paises.map(g => ({ pais: g.dimensions.countryName, vistas: g.count, visitas: g.sum.visits })),
            dispositivos: a.dispositivos.map(g => ({ tipo: g.dimensions.deviceType, vistas: g.count, visitas: g.sum.visits }))
        };
    } catch (e) { out.errores.web = e.message; }

    return out;
}

// GET /workers -- ultimos 7 dias por worker: pedidos, errores, CPU
async function workersUso(env) {
    const hasta = new Date(), desde = new Date(Date.now() - 7 * 86400e3);
    const d = await gql(env, `query($a:String!,$d1:Time!,$d2:Time!){viewer{accounts(filter:{accountTag:$a}){
        workersInvocationsAdaptive(limit:200, filter:{datetime_geq:$d1, datetime_leq:$d2}){
          sum{requests errors subrequests} quantiles{cpuTimeP50 cpuTimeP99} dimensions{scriptName}}}}}`,
        { a: env.CF_ACCOUNT_ID, d1: desde.toISOString(), d2: hasta.toISOString() });
    const por = {};
    d.viewer.accounts[0].workersInvocationsAdaptive.forEach(g => {
        const n = g.dimensions.scriptName;
        const w = por[n] || (por[n] = { worker: n, requests: 0, errores: 0, subrequests: 0, cpuP50: 0, cpuP99: 0 });
        w.requests += g.sum.requests; w.errores += g.sum.errors; w.subrequests += g.sum.subrequests;
        w.cpuP50 = Math.max(w.cpuP50, g.quantiles.cpuTimeP50); w.cpuP99 = Math.max(w.cpuP99, g.quantiles.cpuTimeP99);
    });
    return { desde: desde.toISOString(), workers: Object.values(por).sort((a, b) => b.requests - a.requests) };
}

// ─── ID token de Firebase (misma verificacion que workers/memberships) ───────
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
