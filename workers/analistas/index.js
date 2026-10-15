// workers/analistas/index.js — Análisis e informes de autores invitados.
//
// Todo vive en un solo bucket R2 (ANALISTAS): los archivos y también los índices en
// JSON. No usa KV, así no compite con el cupo de escrituras de los otros workers.
//
//   meta/habilitados.json   { "<email>": perfil del autor }         ← lo maneja el creador
//   meta/envios.json        [ resumen de cada envío ]               ← listados sin N lecturas
//   meta/publicados.json    { autores:[...], publicaciones:[...] }   ← lo que lee el sitio
//   envios/<id>/envio.json  el envío completo (incluye el texto si es formato texto)
//   envios/<id>/analisis.pdf · tapa.jpg · revision.json (la escribe la skill revisar-analisis)
//
// Identidad: SIEMPRE del ID token de Firebase (Authorization: Bearer ...). La skill
// entra como creador con X-Admin-Key = ADMIN_KEY (secret). En `wrangler dev` con
// --var DEV:1 se acepta "Bearer dev:<email>" para probar sin Firebase; en producción no.
//
// Estados de un envío: subiendo → recibido → (cambios | rechazado | publicado → retirado)

const CREADORES = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
const SITIO = 'https://manfredinvestment.com';
const CATEGORIAS = ['acciones', 'bonos', 'macro', 'politica', 'trading'];
const MAX_PDF = 20 * 1024 * 1024;
const MAX_TAPA = 600 * 1024;
// versión vigente de los Términos de colaboración (terminos-autores.html). Si cambia, los autores la aceptan de nuevo al enviar.
const TERMINOS = '1.1';
const COLORES = ['#c3a6f2', '#7fd1ae', '#8fb4ff', '#f29e8e', '#e9c46a', '#9fd3e6', '#f2b880'];

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Admin-Key',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
  'Access-Control-Max-Age': '86400'
};
const json = (obj, status = 200, extra = {}) => new Response(JSON.stringify(obj), { status, headers: { ...CORS, 'Content-Type': 'application/json', ...extra } });
const err = (msg, status = 400) => json({ error: msg }, status);

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const url = new URL(request.url), p = url.pathname, m = request.method;
    try {
      // ── público ───────────────────────────────────────────────
      if (m === 'GET' && p === '/publicados') return publicados(env);
      let r = /^\/pub\/([\w-]+)\.(pdf|jpg)$/.exec(p);
      if (m === 'GET' && r) return archivoPublico(env, r[1], r[2]);

      // ── autores ───────────────────────────────────────────────
      if (m === 'GET' && p === '/yo') return yo(request, env);
      if (m === 'POST' && p === '/envios') return crearEnvio(request, env, ctx);
      r = /^\/envios\/([\w-]+)\/pdf$/.exec(p);
      if (m === 'PUT' && r) return subirPdf(request, env, ctx, r[1]);
      r = /^\/envios\/([\w-]+)\/retirar$/.exec(p);
      if (m === 'POST' && r) return pedirRetiro(request, env, ctx, r[1]);
      if (m === 'GET' && p === '/mis-envios') return misEnvios(request, env);
      if (m === 'POST' && p === '/perfil') return guardarPerfil(request, env);

      // ── creador (y la skill con X-Admin-Key) ──────────────────
      if (m === 'GET' && p === '/creador/envios') return creadorEnvios(request, env);
      r = /^\/creador\/envio\/([\w-]+)\/(analisis\.pdf|tapa\.jpg|envio\.json|revision\.json)$/.exec(p);
      if (m === 'GET' && r) return creadorArchivo(request, env, r[1], r[2]);
      if (m === 'POST' && p === '/creador/revision') return creadorRevision(request, env);
      if (m === 'POST' && p === '/creador/decision') return creadorDecision(request, env, ctx);
      if (m === 'GET' && p === '/creador/autores') return creadorAutores(request, env);
      if (m === 'POST' && p === '/creador/habilitar') return creadorHabilitar(request, env, ctx);
      if (m === 'POST' && p === '/creador/deshabilitar') return creadorDeshabilitar(request, env);
    } catch (e) {
      console.error('[analistas]', p, e && e.stack || e);
      return err('Error interno', 500);
    }
    return err('Ruta no encontrada', 404);
  }
};

/* ══════════════════════════════ identidad ══════════════════════════════ */
let _jwks = { keys: null, exp: 0 };
async function firebaseKeys() {
  if (_jwks.keys && Date.now() < _jwks.exp) return _jwks.keys;
  const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
  const { keys } = await r.json();
  const mm = /max-age=(\d+)/.exec(r.headers.get('cache-control') || '');
  _jwks = { keys, exp: Date.now() + (mm ? +mm[1] : 3600) * 1000 };
  return keys;
}
function b64urlBytes(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
async function usuario(request, env) {
  const auth = request.headers.get('Authorization') || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : '';
  if (env.DEV === '1' && token.startsWith('dev:')) return { email: token.slice(4).toLowerCase(), nombre: '' };
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  try {
    const header = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[0])));
    const q = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[1])));
    const now = Math.floor(Date.now() / 1000);
    if (header.alg !== 'RS256' || q.aud !== FIREBASE_PROJECT || q.iss !== 'https://securetoken.google.com/' + FIREBASE_PROJECT) return null;
    if (!q.exp || q.exp < now || !q.email || q.email_verified === false) return null;
    const jwk = (await firebaseKeys()).find(k => k.kid === header.kid);
    if (!jwk) return null;
    const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
    return ok ? { email: String(q.email).toLowerCase(), nombre: q.name || '' } : null;
  } catch (e) { return null; }
}
function esAdmin(request, env) {
  const k = request.headers.get('X-Admin-Key') || '';
  return !!env.ADMIN_KEY && k.length >= 16 && k === env.ADMIN_KEY;
}
// creador logueado o la skill con la clave
async function creador(request, env) {
  if (esAdmin(request, env)) return { email: 'skill', skill: true };
  const u = await usuario(request, env);
  return u && CREADORES.includes(u.email) ? u : null;
}
async function autor(request, env) {
  const u = await usuario(request, env);
  if (!u) return { error: err('Iniciá sesión', 401) };
  const hab = await leer(env, 'meta/habilitados.json', {});
  const a = hab[u.email];
  if (!a || a.baja) return { error: err('Tu mail no está habilitado para publicar', 403) };
  return { u, a, hab };
}

/* ══════════════════════════════ R2 ══════════════════════════════ */
async function leer(env, key, def) {
  const o = await env.ANALISTAS.get(key);
  if (!o) return def;
  try { return await o.json(); } catch (e) { return def; }
}
async function escribir(env, key, val) {
  await env.ANALISTAS.put(key, JSON.stringify(val), { httpMetadata: { contentType: 'application/json' } });
}
// lectura-modificación-escritura con control de concurrencia (etag): dos cambios a la
// vez sobre el mismo índice no se pisan.
async function actualizar(env, key, def, fn) {
  for (let i = 0; i < 6; i++) {
    const o = await env.ANALISTAS.get(key);
    const actual = o ? await o.json().catch(() => def) : structuredClone(def);
    const nuevo = await fn(actual);
    const opts = { httpMetadata: { contentType: 'application/json' } };
    if (o) opts.onlyIf = { etagMatches: o.etag };
    const res = await env.ANALISTAS.put(key, JSON.stringify(nuevo), opts);
    if (res) return nuevo;
    await new Promise(r => setTimeout(r, 40 * (i + 1)));
  }
  throw new Error('No se pudo actualizar ' + key);
}
async function guardarEnvio(env, e) {
  await escribir(env, 'envios/' + e.id + '/envio.json', e);
  await actualizar(env, 'meta/envios.json', [], lista => {
    const r = resumen(e), i = lista.findIndex(x => x.id === e.id);
    if (i >= 0) lista[i] = r; else lista.unshift(r);
    return lista;
  });
}
// lo que va al índice: todo menos el cuerpo del texto
function resumen(e) { const { cuerpo, ...r } = e; return r; }

/* ══════════════════════════════ público ══════════════════════════════ */
async function publicados(env) {
  const d = await leer(env, 'meta/publicados.json', { autores: [], publicaciones: [] });
  return json(d, 200, { 'Cache-Control': 'public, max-age=60' });
}
async function archivoPublico(env, id, ext) {
  const d = await leer(env, 'meta/publicados.json', { publicaciones: [] });
  if (!d.publicaciones.some(x => x.id === id)) return err('No encontrado', 404);
  const o = await env.ANALISTAS.get('envios/' + id + '/' + (ext === 'pdf' ? 'analisis.pdf' : 'tapa.jpg'));
  if (!o) return err('No encontrado', 404);
  return new Response(o.body, { headers: { ...CORS, 'Content-Type': ext === 'pdf' ? 'application/pdf' : 'image/jpeg', 'Cache-Control': 'public, max-age=86400', ETag: o.httpEtag } });
}

/* ══════════════════════════════ autores ══════════════════════════════ */
async function yo(request, env) {
  const u = await usuario(request, env);
  if (!u) return json({ sesion: false });
  const hab = await leer(env, 'meta/habilitados.json', {});
  const a = hab[u.email];
  return json({ sesion: true, email: u.email, creador: CREADORES.includes(u.email), habilitado: !!(a && !a.baja), autor: a && !a.baja ? perfilPublico(a) : null,
    terminos: { vigente: TERMINOS, aceptado: a && a.terminos ? a.terminos.version : null } });
}
function perfilPublico(a) {
  const p = { slug: a.slug, nombre: a.nombre, rol: a.rol || '', corto: a.corto || '', bio: a.bio || '', color: a.color, verificado: true, desde: a.desde, links: a.links || {}, asesor: !!a.registro };
  // matrícula para asesorar: la carga el creador después de ver la constancia (Términos, cl. 5)
  if (a.registro) p.registro = { organismo: a.registro.organismo, categoria: a.registro.categoria, numero: a.registro.numero };
  if (a.negocio) p.negocio = { nombre: a.negocio.nombre, desc: a.negocio.desc || '', url: a.negocio.url || '' };
  return p;
}
function registroDe(r) {
  if (!r || typeof r !== 'object') return null;
  const reg = { organismo: txt(r.organismo, 40), categoria: txt(r.categoria, 80), numero: txt(r.numero, 40) };
  return reg.organismo && reg.numero ? reg : null;
}
const txt = (v, n) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, n);
function nuevoId(slug) {
  const d = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Argentina/Buenos_Aires' }).replace(/-/g, '');
  return d + '-' + slug.slice(0, 24) + '-' + crypto.randomUUID().slice(0, 6);
}
function b64aBytes(s) {
  const m = /^data:image\/jpeg;base64,(.+)$/.exec(s || '');
  return m ? Uint8Array.from(atob(m[1]), c => c.charCodeAt(0)) : null;
}

// POST /envios  — datos del envío (JSON). Si es PDF, después va PUT /envios/<id>/pdf.
async function crearEnvio(request, env, ctx) {
  const { u, a, error } = await autor(request, env);
  if (error) return error;
  const b = await request.json().catch(() => null);
  if (!b) return err('Datos inválidos');
  const formato = b.formato === 'texto' ? 'texto' : 'pdf';
  const e = {
    id: nuevoId(a.slug), email: u.email, autor: a.slug, formato,
    titulo: txt(b.titulo, 90), resumen: txt(b.resumen, 180), categoria: CATEGORIAS.includes(b.categoria) ? b.categoria : '',
    activos: txt(b.activos, 120), posiciones: txt(b.posiciones, 200),
    declaraciones: { autoria: b.autoria === true, sinRecomendaciones: b.reglas === true },
    enviado: new Date().toISOString(), estado: formato === 'pdf' ? 'subiendo' : 'recibido',
    reemplaza: /^[\w-]{6,80}$/.test(b.reemplaza || '') ? b.reemplaza : undefined
  };
  if (!e.titulo || !e.resumen || !e.categoria) return err('Faltan título, resumen o categoría');
  if (!e.declaraciones.autoria || !e.declaraciones.sinRecomendaciones) return err('Faltan las confirmaciones');
  if (b.terminos !== TERMINOS) return err('Tenés que aceptar los Términos de colaboración (versión ' + TERMINOS + ')');
  e.terminos = { version: TERMINOS, aceptado: e.enviado };
  // la aceptación también queda en el autor (la primera vez y con cada versión nueva)
  if (!a.terminos || a.terminos.version !== TERMINOS)
    await actualizar(env, 'meta/habilitados.json', {}, h => { if (h[u.email]) h[u.email].terminos = { version: TERMINOS, fecha: e.enviado }; return h; });
  if (formato === 'texto') {
    const cuerpo = String(b.cuerpo || '').replace(/\r/g, '').slice(0, 60000);
    if (cuerpo.trim().split(/\s+/).length < 150) return err('El texto tiene que tener al menos 150 palabras');
    e.cuerpo = cuerpo;
  } else if (b.tapa) {
    const t = b64aBytes(b.tapa);
    if (t && t.length <= MAX_TAPA) await env.ANALISTAS.put('envios/' + e.id + '/tapa.jpg', t, { httpMetadata: { contentType: 'image/jpeg' } });
  }
  await guardarEnvio(env, e);
  if (e.estado === 'recibido') ctx.waitUntil(avisarRecibido(env, e, a));
  return json({ ok: true, id: e.id, estado: e.estado });
}

// PUT /envios/<id>/pdf  — el PDF va directo del navegador al bucket (sin parsear: poco CPU)
async function subirPdf(request, env, ctx, id) {
  const { u, a, error } = await autor(request, env);
  if (error) return error;
  const e = await leer(env, 'envios/' + id + '/envio.json', null);
  if (!e || e.email !== u.email) return err('Envío no encontrado', 404);
  if (e.estado !== 'subiendo') return err('Este envío ya tiene su PDF');
  const largo = +request.headers.get('Content-Length') || 0;
  if (!largo || largo > MAX_PDF) return err('El PDF tiene que pesar menos de 20 MB', 413);
  const key = 'envios/' + id + '/analisis.pdf';
  await env.ANALISTAS.put(key, request.body, { httpMetadata: { contentType: 'application/pdf' } });
  // confirmar que de verdad es un PDF (los primeros bytes son "%PDF")
  const cab = await env.ANALISTAS.get(key, { range: { offset: 0, length: 5 } });
  const ini = cab ? new TextDecoder().decode(await cab.arrayBuffer()) : '';
  if (!ini.startsWith('%PDF')) { await env.ANALISTAS.delete(key); return err('El archivo no es un PDF válido'); }
  e.estado = 'recibido'; e.bytes = largo;
  await guardarEnvio(env, e);
  ctx.waitUntil(avisarRecibido(env, e, a));
  return json({ ok: true, id, estado: e.estado });
}

async function misEnvios(request, env) {
  const { u, error } = await autor(request, env);
  if (error) return error;
  const lista = (await leer(env, 'meta/envios.json', [])).filter(x => x.email === u.email && x.estado !== 'subiendo');
  // al autor no le mostramos la revisión interna, solo el mensaje que le mandaste
  return json({ envios: lista.map(({ revision, ...x }) => x) });
}

async function pedirRetiro(request, env, ctx, id) {
  const { u, a, error } = await autor(request, env);
  if (error) return error;
  const e = await leer(env, 'envios/' + id + '/envio.json', null);
  if (!e || e.email !== u.email) return err('Envío no encontrado', 404);
  e.retiroPedido = new Date().toISOString();
  await guardarEnvio(env, e);
  ctx.waitUntil(mail(env, CREADORES, 'Pedido de retiro: ' + e.titulo, plantilla('Pedido de retiro',
    '<p><b>' + esc(a.nombre) + '</b> pidió retirar <b>' + esc(e.titulo) + '</b>.</p><p>Lo podés retirar desde el Panel → Análisis por revisar.</p>', SITIO + '/#panel', 'Abrir el Panel')));
  return json({ ok: true });
}

async function guardarPerfil(request, env) {
  const { u, error } = await autor(request, env);
  if (error) return error;
  const b = await request.json().catch(() => ({}));
  const url = v => { v = txt(v, 200); return /^https:\/\/[^\s"<>]+$/.test(v) ? v : ''; };
  const hab = await actualizar(env, 'meta/habilitados.json', {}, h => {
    const a = h[u.email];
    a.nombre = txt(b.nombre, 60) || a.nombre;
    a.rol = txt(b.rol, 90); a.corto = txt(b.corto, 40) || a.corto; a.bio = txt(b.bio, 280);
    a.links = { linkedin: url(b.linkedin), instagram: url(b.instagram), x: url(b.x) };
    if (txt(b.trabajo, 80)) a.links.trabajo = { nombre: txt(b.trabajo, 80), url: url(b.trabajoUrl) };
    Object.keys(a.links).forEach(k => { if (!a.links[k]) delete a.links[k]; });
    // su negocio propio (consultora, asesoría, estudio), aunque sea pago: Términos 1.1, cl. 9.3
    if (txt(b.negocio, 60)) a.negocio = { nombre: txt(b.negocio, 60), desc: txt(b.negocioDesc, 120), url: url(b.negocioUrl) };
    else delete a.negocio;
    return h;
  });
  await refrescarAutoresPublicados(env, hab);
  return json({ ok: true, autor: perfilPublico(hab[u.email]) });
}

/* ══════════════════════════════ creador ══════════════════════════════ */
async function creadorEnvios(request, env) {
  if (!(await creador(request, env))) return err('Solo el creador', 403);
  const url = new URL(request.url), solo = url.searchParams.get('estado');
  let lista = (await leer(env, 'meta/envios.json', [])).filter(x => x.estado !== 'subiendo');
  if (solo) lista = lista.filter(x => x.estado === solo);
  const hab = await leer(env, 'meta/habilitados.json', {});
  lista = lista.map(x => ({ ...x, autorPerfil: hab[x.email] ? perfilPublico(hab[x.email]) : null }));
  return json({ envios: lista });
}
async function creadorArchivo(request, env, id, archivo) {
  if (!(await creador(request, env))) return err('Solo el creador', 403);
  const o = await env.ANALISTAS.get('envios/' + id + '/' + archivo);
  if (!o) return err('No encontrado', 404);
  const tipo = archivo.endsWith('.pdf') ? 'application/pdf' : archivo.endsWith('.jpg') ? 'image/jpeg' : 'application/json';
  return new Response(o.body, { headers: { ...CORS, 'Content-Type': tipo, 'Cache-Control': 'private, no-store' } });
}

// POST /creador/revision {id, revision}  — la escribe la skill revisar-analisis
async function creadorRevision(request, env) {
  if (!(await creador(request, env))) return err('Solo el creador', 403);
  const b = await request.json().catch(() => ({}));
  const e = await leer(env, 'envios/' + (b.id || '') + '/envio.json', null);
  if (!e) return err('Envío no encontrado', 404);
  const r = b.revision || {};
  if (!['publicar', 'cambios', 'rechazar'].includes(r.veredicto) || !Array.isArray(r.checks)) return err('Revisión inválida');
  await escribir(env, 'envios/' + e.id + '/revision.json', r);
  e.revision = { veredicto: r.veredicto, puntaje: r.puntaje, resumen: r.resumen, revisadoEn: r.revisadoEn || new Date().toISOString() };
  await guardarEnvio(env, e);
  return json({ ok: true });
}

// POST /creador/decision {id, accion: aprobar|cambios|rechazar|retirar, mensaje}
async function creadorDecision(request, env, ctx) {
  const c = await creador(request, env);
  if (!c || c.skill) return err('Solo el creador', 403); // la skill revisa; decidir es tuyo
  const b = await request.json().catch(() => ({}));
  const e = await leer(env, 'envios/' + (b.id || '') + '/envio.json', null);
  if (!e) return err('Envío no encontrado', 404);
  const hab = await leer(env, 'meta/habilitados.json', {});
  const a = hab[e.email];
  if (!a) return err('El autor ya no está habilitado');
  const ahora = new Date().toISOString(), mensaje = String(b.mensaje || '').slice(0, 5000);

  if (b.accion === 'aprobar') {
    if (!['recibido', 'cambios'].includes(e.estado)) return err('Este envío no está pendiente');
    e.estado = 'publicado'; e.publicado = ahora; e.decision = { accion: 'aprobar', fecha: ahora };
    await guardarEnvio(env, e);
    await actualizar(env, 'meta/publicados.json', { autores: [], publicaciones: [] }, d => {
      // si reemplaza a una versión anterior, sale la vieja
      d.publicaciones = d.publicaciones.filter(x => x.id !== e.id && x.id !== e.reemplaza);
      d.publicaciones.unshift(publicacion(e));
      return conAutores(d, hab);
    });
    ctx.waitUntil(mail(env, [e.email], 'Publicamos tu análisis', plantilla('Ya está publicado',
      '<p>Hola ' + esc(a.nombre.split(' ')[0]) + ', tu análisis <b>' + esc(e.titulo) + '</b> ya está en Manfredi Investment.</p><p>Compartí tu perfil para que llegue a más gente.</p>',
      SITIO + '/#analista-' + a.slug, 'Ver mi perfil')));
    return json({ ok: true, estado: e.estado });
  }
  if (b.accion === 'cambios' || b.accion === 'rechazar') {
    if (!mensaje.trim()) return err('Escribí el mensaje para el autor');
    e.estado = b.accion === 'cambios' ? 'cambios' : 'rechazado';
    e.mensaje = mensaje; e.revisado = ahora; e.decision = { accion: b.accion, fecha: ahora };
    await guardarEnvio(env, e);
    ctx.waitUntil(mail(env, [e.email], b.accion === 'cambios' ? 'Tu análisis: cambios sugeridos' : 'Sobre tu análisis', plantilla(
      b.accion === 'cambios' ? 'Cambios sugeridos' : 'Sobre tu análisis',
      '<p style="white-space:pre-line">' + esc(mensaje) + '</p>', SITIO + '/#autor', 'Ir a Mi espacio de autor')));
    return json({ ok: true, estado: e.estado });
  }
  if (b.accion === 'retirar') {
    e.estado = 'retirado'; e.decision = { accion: 'retirar', fecha: ahora };
    await guardarEnvio(env, e);
    await actualizar(env, 'meta/publicados.json', { autores: [], publicaciones: [] }, d => {
      d.publicaciones = d.publicaciones.filter(x => x.id !== e.id);
      return conAutores(d, hab);
    });
    return json({ ok: true, estado: e.estado });
  }
  return err('Acción inválida');
}
// la publicación tal como la lee el sitio (assets/analistas/analistas.js)
// rutas relativas al worker: el sitio les antepone la URL del worker
function publicacion(e) {
  const p = { id: e.id, autor: e.autor, categoria: e.categoria, titulo: e.titulo, resumen: e.resumen, fecha: e.publicado.slice(0, 10) };
  if (e.posiciones) p.posiciones = e.posiciones; // la declaración del autor se publica junto con la pieza
  if (e.formato === 'pdf') { p.pdf = '/pub/' + e.id + '.pdf'; p.tapa = '/pub/' + e.id + '.jpg'; }
  else p.cuerpo = e.cuerpo; // los textos se leen en la página (#nota-<id>)
  return p;
}
function conAutores(d, hab) {
  const usados = new Set(d.publicaciones.map(x => x.autor));
  d.autores = Object.values(hab).filter(a => usados.has(a.slug) && !a.baja).map(perfilPublico);
  return d;
}
async function refrescarAutoresPublicados(env, hab) {
  await actualizar(env, 'meta/publicados.json', { autores: [], publicaciones: [] }, d => conAutores(d, hab));
}

async function creadorAutores(request, env) {
  if (!(await creador(request, env))) return err('Solo el creador', 403);
  const hab = await leer(env, 'meta/habilitados.json', {});
  const envios = await leer(env, 'meta/envios.json', []);
  return json({ terminosVigentes: TERMINOS, autores: Object.entries(hab).map(([email, a]) => ({ email, ...perfilPublico(a), baja: !!a.baja, habilitadoEn: a.habilitadoEn, terminos: a.terminos || null,
    envios: envios.filter(x => x.email === email && x.estado !== 'subiendo').length, publicados: envios.filter(x => x.email === email && x.estado === 'publicado').length })) });
}
const slugDe = n => n.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);

// POST /creador/habilitar {email, nombre, rol, corto, registro?: {organismo, categoria, numero} | null}
// Con un mail ya habilitado sirve para editar: si viene "registro" (aunque sea null) se actualiza.
async function creadorHabilitar(request, env, ctx) {
  const c = await creador(request, env);
  if (!c || c.skill) return err('Solo el creador', 403);
  const b = await request.json().catch(() => ({}));
  const email = String(b.email || '').trim().toLowerCase();
  const nombre = txt(b.nombre, 60);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 120) return err('Mail inválido');
  if (!nombre) return err('Falta el nombre');
  let nuevo = false;
  const hab = await actualizar(env, 'meta/habilitados.json', {}, h => {
    const usados = new Set(Object.entries(h).filter(([k]) => k !== email).map(([, a]) => a.slug));
    if (h[email]) {
      h[email].baja = false; h[email].nombre = nombre; h[email].rol = txt(b.rol, 90) || h[email].rol;
      if ('registro' in b) { const r = registroDe(b.registro); if (r) h[email].registro = r; else delete h[email].registro; }
      return h;
    }
    nuevo = true;
    let slug = slugDe(nombre) || 'autor', s = slug, i = 2;
    while (usados.has(s) || s === 'manfredi') s = slug + '-' + i++;
    h[email] = { slug: s, nombre, rol: txt(b.rol, 90), corto: txt(b.corto, 40) || txt(b.rol, 40), color: COLORES[Object.keys(h).length % COLORES.length],
      desde: new Date().toISOString().slice(0, 10), habilitadoEn: new Date().toISOString(), links: {} };
    const r = registroDe(b.registro); if (r) h[email].registro = r;
    return h;
  });
  await refrescarAutoresPublicados(env, hab);
  if (nuevo || b.reenviar) ctx.waitUntil(mail(env, [email], 'Ya podés publicar en Manfredi Investment', plantilla('Bienvenido a Análisis e informes',
    '<p>Hola ' + esc(nombre.split(' ')[0]) + ', habilitamos tu mail para publicar en la sección Análisis e informes.</p>' +
    '<p>Iniciá sesión en el sitio con <b>' + esc(email) + '</b> y vas a ver el botón <b>Mi espacio de autor</b> junto a las pestañas de Noticias. Desde ahí subís tus análisis (PDF o texto) y completás tu perfil.</p>',
    SITIO + '/#autor', 'Ir a Mi espacio de autor')));
  return json({ ok: true, autor: { email, ...perfilPublico(hab[email]) } });
}
async function creadorDeshabilitar(request, env) {
  const c = await creador(request, env);
  if (!c || c.skill) return err('Solo el creador', 403);
  const b = await request.json().catch(() => ({}));
  const email = String(b.email || '').trim().toLowerCase();
  const hab = await actualizar(env, 'meta/habilitados.json', {}, h => { if (h[email]) h[email].baja = true; return h; });
  if (!hab[email]) return err('No existe', 404);
  await refrescarAutoresPublicados(env, hab);
  return json({ ok: true });
}

/* ══════════════════════════════ mails ══════════════════════════════ */
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
async function mail(env, to, subject, html) {
  if (!env.RESEND_API_KEY) { console.log('[analistas] (sin RESEND_API_KEY) mail no enviado:', to.join(','), '·', subject); return; }
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST', headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: 'Manfredi Investment <hola@manfredinvestment.com>', to, subject, html })
    });
    if (!r.ok) console.error('[analistas] Resend', r.status, await r.text());
  } catch (e) { console.error('[analistas] mail', e.message); }
}
// mismo look que la campaña: fondo azul, título dorado, texto azul claro
function plantilla(titulo, cuerpo, link, boton) {
  return '<div style="background:#0a1528;padding:32px 16px;font-family:Arial,Helvetica,sans-serif"><div style="max-width:560px;margin:0 auto;background:#0e1c35;border:1px solid #2b3a55;border-radius:16px;padding:32px 28px">' +
    '<div style="font:600 11px Arial;letter-spacing:3px;text-transform:uppercase;color:#e9d3a0">Manfredi Investment</div>' +
    '<h1 style="margin:12px 0 18px;font:400 26px Georgia,serif;color:#f3e3bd">' + esc(titulo) + '</h1>' +
    '<div style="font:15px/1.6 Arial;color:#dbe6f7">' + cuerpo + '</div>' +
    (link ? '<p style="margin:26px 0 0"><a href="' + link + '" style="display:inline-block;padding:12px 22px;border-radius:10px;background:#d4b067;color:#1d1606;font:600 14px Arial;text-decoration:none">' + esc(boton) + '</a></p>' : '') +
    '</div></div>';
}
async function avisarRecibido(env, e, a) {
  await mail(env, [e.email], 'Recibimos tu análisis', plantilla('Recibimos tu análisis',
    '<p>Hola ' + esc(a.nombre.split(' ')[0]) + ', recibimos <b>' + esc(e.titulo) + '</b>. Lo revisamos y te avisamos por mail cuando esté publicado o si hace falta algún cambio.</p>', SITIO + '/#autor', 'Ver mis envíos'));
  await mail(env, CREADORES, 'Nuevo análisis para revisar: ' + e.titulo, plantilla('Nuevo análisis para revisar',
    '<p><b>' + esc(a.nombre) + '</b> mandó <b>' + esc(e.titulo) + '</b> (' + esc(e.categoria) + ', ' + (e.formato === 'pdf' ? 'PDF' : 'texto') + ').</p><p>En Claude Code: "revisá los análisis".</p>', SITIO + '/#panel', 'Abrir el Panel'));
}
