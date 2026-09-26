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

// GET /trafico -- 30 dias de Web Analytics: solo navegadores reales (sin bots).
// Filtra por dominio en vez de listar sitios, asi alcanza con el permiso Account Analytics: Read.
// Web Analytics MUESTREA si se le pide un rango largo de una (da 100, 200...): por eso se pide
// un alias por dia para la serie y tramos de 6 dias para los rankings, y se suman aca.
// Ojo: no usa cookies, asi que da VISITAS (entradas al sitio) y paginas vistas, no personas distintas.
async function trafico(env) {
    const DIA = 86400e3, hoy = new Date(), hoy0 = Date.UTC(hoy.getUTCFullYear(), hoy.getUTCMonth(), hoy.getUTCDate());
    const desde = new Date(hoy0 - 29 * DIA);
    const out = { desde: isoDia(desde), hasta: isoDia(hoy), web: null, errores: {} };
    const rango = (a, b) => `requestHost_in:$h, datetime_geq:"${new Date(a).toISOString()}", datetime_leq:"${new Date(Math.min(b, Date.now())).toISOString()}"`;
    const consulta = partes => gql(env, `query($a:String!,$h:[String!]){viewer{accounts(filter:{accountTag:$a}){${partes.join('\n')}}}}`,
        { a: env.CF_ACCOUNT_ID, h: [env.SITE_HOST, 'www.' + env.SITE_HOST] }).then(d => d.viewer.accounts[0]);
    try {
        const dias = [];
        for (let t = +desde; t <= hoy0; t += DIA) dias.push(t);
        const s = await consulta(dias.map((t, i) => `d${i}: rumPageloadEventsAdaptiveGroups(limit:1, filter:{${rango(t, t + DIA - 1)}}){ count sum{visits} }`));
        const serie = dias.map((t, i) => { const g = s['d' + i][0]; return { fecha: isoDia(new Date(t)), vistas: g ? g.count : 0, visitas: g ? g.sum.visits : 0 }; });

        const DIMS = { paginas: ['requestPath', 12], origen: ['refererHost', 10], paises: ['countryName', 10], dispositivos: ['deviceType', 5] };
        const tramos = [];
        for (let t = +desde; t <= hoy0; t += 6 * DIA) tramos.push([t, t + 6 * DIA - 1]);
        const partes = [];
        Object.entries(DIMS).forEach(([k, [dim]]) => tramos.forEach(([a, b], i) =>
            partes.push(`${k}${i}: rumPageloadEventsAdaptiveGroups(limit:50, filter:{${rango(a, b)}}, orderBy:[count_DESC]){ count sum{visits} dimensions{${dim}} }`)));
        const r = await consulta(partes);
        const rank = k => {
            const [dim, top] = DIMS[k], acc = {};
            tramos.forEach((_, i) => (r[k + i] || []).forEach(g => {
                const n = g.dimensions[dim] || '(directo)', e = acc[n] || (acc[n] = { nombre: n, vistas: 0, visitas: 0 });
                e.vistas += g.count; e.visitas += g.sum.visits;
            }));
            return Object.values(acc).sort((x, y) => y.vistas - x.vistas).slice(0, top);
        };
        out.web = {
            sitio: env.SITE_HOST, serie,
            paginas: rank('paginas').map(e => ({ ruta: e.nombre, vistas: e.vistas, visitas: e.visitas })),
            // origen: solo llegadas desde afuera (la navegacion interna trae visitas = 0)
            origen: rank('origen').filter(e => e.visitas > 0).sort((x, y) => y.visitas - x.visitas).map(e => ({ origen: e.nombre, vistas: e.vistas, visitas: e.visitas })),
            paises: rank('paises').map(e => ({ pais: e.nombre, vistas: e.vistas, visitas: e.visitas })),
            dispositivos: rank('dispositivos').map(e => ({ tipo: e.nombre, vistas: e.vistas, visitas: e.visitas }))
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
