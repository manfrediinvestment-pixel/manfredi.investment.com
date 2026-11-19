/* "Lo último" — primera vista de la home (#luFront, estilos en lo-ultimo.css).
   Junta en una portada de diario lo más nuevo del sitio:
   - Noticias: worker manfredi-noticias (con foto). La más nueva con foto va grande.
   - Análisis de invitados: worker manfredi-analistas (/publicados), el más reciente.
   - Informes: INFORMES_RECIENTES (abajo). Al actualizar o publicar un informe, sumarlo ARRIBA.
   - Canal de WhatsApp: el último resumen del worker manfredi-comunidad, en una línea.
   Reemplaza al cuadro grande del canal (#waCard, assets/comunidad/wa.js), que ya no está en la home. */
(function () {
  'use strict';

  // Lo último en informes: el primero se muestra. Fecha = día que se publicó/actualizó.
  var INFORMES_RECIENTES = [
    { t: 'ANT',  nombre: 'Anthropic',  fecha: '2026-11-19', nota: 'Informe nuevo', titulo: 'Anthropic tras su salida a bolsa: ingresos +1.127% y un run-rate de $81 mil millones' },
    { t: 'NVDA', nombre: 'NVIDIA',     fecha: '2026-11-18', nota: 'Actualizado al 3T FY27', titulo: 'NVIDIA: ingresos +103% en el primer trimestre sin Jensen Huang' },
    { t: 'UBER', nombre: 'Uber',       fecha: '2026-11-17', nota: 'Actualizado al 3T26', titulo: 'Uber: Gross Bookings +20% y una oferta de US$14.800 millones por Delivery Hero' }
  ];

  var NOTICIAS = 'https://manfredi-noticias.nachito2502.workers.dev/noticias';
  var ANALISTAS = 'https://manfredi-analistas.nachito2502.workers.dev';
  var COMUNIDAD = 'https://manfredi-comunidad.nachito2502.workers.dev';
  var IC_WA = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2Zm4.52 11.99c-.25-.12-1.47-.72-1.7-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.16.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28Z"/></svg>';

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function json(u) { return fetch(u, { cache: 'no-cache', signal: AbortSignal.timeout(10000) }).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); }); }
  // "hace 12 min", "hace 3 h", "ayer", "14 nov"
  function hace(iso) {
    if (!iso) return '';
    var t = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? new Date(iso + 'T12:00:00-03:00') : new Date(iso);
    var m = Math.round((Date.now() - t) / 6e4);
    if (isNaN(m)) return '';
    var f = function (d) { return d.toLocaleDateString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' }); };
    if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) {
      if (f(t) === f(new Date())) return 'hoy';
      if (f(t) === f(new Date(Date.now() - 864e5))) return 'ayer';
    } else {
      if (m < 1) return 'recién';
      if (m < 60) return 'hace ' + m + ' min';
      if (m < 24 * 60) return 'hace ' + Math.round(m / 60) + ' h';
      if (f(t) === f(new Date(Date.now() - 864e5))) return 'ayer';
    }
    return t.toLocaleDateString('es-AR', { day: 'numeric', month: 'short', timeZone: 'America/Argentina/Buenos_Aires' }).replace('.', '');
  }
  function sinFoto(img) { img.addEventListener('error', function () { img.remove(); }, { once: true }); }

  var st = { noticias: null, analisis: null, autores: {}, wa: null };

  /* ------------------------------ piezas ------------------------------ */
  // corto = solo el punto de color (en las filas chicas no entra el nombre)
  function origen(n, corto) {
    var ar = n._o === 'ar', nom = ar ? 'Argentina' : 'Wall Street';
    return '<span class="' + (ar ? 'ar' : 'us') + '"' + (corto ? ' title="' + nom + '" aria-label="' + nom + '">' : '>' + nom) + '</span>';
  }

  function lead(n) {
    if (!n) return '<div class="lu-lead"><div class="lu-ph lu-sk"></div><div class="lu-sk" style="height:12px;width:40%"></div><div class="lu-sk" style="height:52px"></div></div>';
    return '<a class="lu-lead" href="' + esc(n.link) + '" target="_blank" rel="noopener noreferrer">' +
      '<div class="lu-ph">' + (n.imagen ? '<img src="' + esc(n.imagen) + '" alt="" loading="eager" decoding="async">' : '') + '</div>' +
      '<span class="lu-k">' + origen(n) + (n.fuente ? '<b>' + esc(n.fuente) + '</b>' : '') + '<i>' + esc(hace(n.fecha)) + '</i></span>' +
      '<h3>' + esc(n.titulo) + '</h3>' +
      (n.resumen ? '<p>' + esc(n.resumen) + '</p>' : '') +
    '</a>';
  }

  function itNoticia(n) {
    return '<a class="lu-it" href="' + esc(n.link) + '" target="_blank" rel="noopener noreferrer"><div>' +
      '<span class="lu-k">' + origen(n, true) + (n.fuente ? '<b>' + esc(n.fuente) + '</b>' : '') + '<i>' + esc(hace(n.fecha)) + '</i></span>' +
      '<h4>' + esc(n.titulo) + '</h4></div>' +
      (n.imagen ? '<img class="lu-th" src="' + esc(n.imagen) + '" alt="" loading="lazy">' : '') +
    '</a>';
  }

  function itAnalisis(p) {
    var a = st.autores[p.autor] || {};
    return '<a class="lu-it" href="#analista-' + esc(p.autor) + '" data-lu-pdf="' + esc(p.id) + '"><div>' +
      '<span class="lu-k"><b>Análisis</b><i>' + esc(hace(p.fecha)) + '</i></span>' +
      '<h4>' + esc(p.titulo) + '</h4>' +
      '<span class="lu-by">' + (a.foto ? '<img src="' + esc(a.foto) + '" alt="" loading="lazy">' : '') + esc(a.nombre || '') + '</span></div>' +
      (p.tapa ? '<img class="lu-th lu-th--tapa" src="' + esc(p.tapa) + '" alt="" loading="lazy">' : '') +
    '</a>';
  }

  function itInforme(i) {
    return '<a class="lu-it" href="informes/' + i.t.toLowerCase() + '.html" target="_blank" rel="noopener"><div>' +
      '<span class="lu-k"><b>Informe · ' + esc(i.t) + '</b><i>' + esc(hace(i.fecha)) + '</i></span>' +
      '<h4>' + esc(i.titulo) + '</h4>' +
      '<span class="lu-by"><span class="lu-sello">' + esc(i.nota) + '</span></span></div>' +
      '<img class="lu-th lu-th--logo" src="assets/logos/' + i.t.toLowerCase() + '.png" alt="" loading="lazy">' +
    '</a>';
  }

  function wa() {
    var link = window.MI_WA_COMUNIDAD || 'https://whatsapp.com/channel/0029Vb8rDVHB4hdUO5L2Lx17';
    var m = st.wa, txt;
    if (m) {
      var r = m.datos || {};
      txt = '<b>' + (r.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado') + ':</b> ' + esc(r.clave || String(r.intro || '').split('. ')[0]);
    } else {
      txt = 'Un <b>resumen antes de la apertura</b> y otro <b>al cierre</b>, todos los días hábiles.';
    }
    return '<div class="lu-wa">' +
      '<span class="lu-wa__ic">' + IC_WA + '</span>' +
      '<div class="lu-wa__t"><span class="lu-k"><b>Canal de WhatsApp</b><i>Gratis' + (m ? ' · ' + esc(hace(new Date(m.creado).toISOString())) : '') + '</i></span><p>' + txt + '</p></div>' +
      '<a class="lu-wa__btn" href="' + esc(link) + '" target="_blank" rel="noopener">' + IC_WA + 'Seguir el canal</a>' +
    '</div>';
  }

  function pintar(box) {
    var ns = st.noticias || [];
    // la grande: la más nueva de Argentina con foto (en castellano); si no hay, cualquiera con foto
    var conFoto = ns.filter(function (n) { return n.imagen; });
    var principal = conFoto.filter(function (n) { return n._o === 'ar'; })[0] || conFoto[0] || ns[0] || null;
    // al costado: la más nueva de Wall Street y la siguiente de Argentina
    var otras = ns.filter(function (n) { return n !== principal; });
    var resto = [otras.filter(function (n) { return n._o === 'us'; })[0], otras.filter(function (n) { return n._o === 'ar'; })[0]].filter(Boolean);
    var lado = [];
    if (st.analisis) lado.push(itAnalisis(st.analisis));
    lado.push(itInforme(INFORMES_RECIENTES[0]));
    resto.forEach(function (n) { lado.push(itNoticia(n)); });
    if (!st.noticias) lado.push('<div class="lu-it"><div><div class="lu-sk" style="height:10px;width:50%"></div><div class="lu-sk" style="height:38px"></div></div></div>');

    box.innerHTML =
      '<div class="lu-hd"><h2>Lo último</h2><span class="lu-live">En vivo</span>' +
        '<a class="lu-all" href="#reportes" data-tab-target="informes">Todas las noticias</a></div>' +
      '<div class="lu-grid">' + lead(principal) + '<div class="lu-side">' + lado.join('') + '</div></div>' +
      wa();
    box.querySelectorAll('img').forEach(sinFoto);
  }

  /* ------------------------------ datos ------------------------------ */
  function cargarNoticias() {
    var marcar = function (l, o) { return (l || []).map(function (n) { var x = {}; for (var k in n) x[k] = n[k]; x._o = o; return x; }); };
    var orden = function (d) { return marcar(d.argentina || d.noticias, 'ar').concat(marcar(d.wallstreet, 'us')).sort(function (a, b) { return new Date(b.fecha || 0) - new Date(a.fecha || 0); }); };
    return json(NOTICIAS).then(orden).catch(function () {
      return Promise.all([json('reports/argentina.json'), json('reports/wallstreet.json')]).then(function (r) {
        return orden({ argentina: r[0].noticias, wallstreet: r[1].noticias });
      });
    });
  }
  function cargarAnalisis() {
    return json(ANALISTAS + '/publicados').then(function (d) {
      (d.autores || []).forEach(function (a) { st.autores[a.slug] = a; });
      var ps = (d.publicaciones || []).filter(function (p) { return st.autores[p.autor]; })
        .sort(function (a, b) { return String(b.fecha).localeCompare(String(a.fecha)); });
      var p = ps[0];
      if (p) { if (p.tapa && p.tapa[0] === '/') p.tapa = ANALISTAS + p.tapa; if (p.pdf && p.pdf[0] === '/') p.pdf = ANALISTAS + p.pdf; }
      return p || null;
    });
  }
  function cargarWa() {
    return json(COMUNIDAD + '/chat/gratis').then(function (d) {
      var m = ((d && d.mensajes) || []).filter(function (x) { return x.tipo === 'resumen' && !x.borrado; }).slice(-1)[0];
      if (m && typeof m.datos === 'string') { try { m.datos = JSON.parse(m.datos); } catch (e) { m.datos = {}; } }
      return m || null;
    });
  }

  function iniciar() {
    var box = document.getElementById('luFront');
    if (!box) return;
    pintar(box);
    // el análisis se abre en el lector de PDF del sitio, como en la pestaña Noticias
    box.addEventListener('click', function (e) {
      var a = e.target.closest('[data-lu-pdf]');
      if (!a || !st.analisis || typeof window.openPdf !== 'function' || !st.analisis.pdf) return;
      e.preventDefault();
      var p = st.analisis, au = st.autores[p.autor] || {};
      window.openPdf(p.pdf, p.titulo, { tapa: p.tapa, etiqueta: au.nombre || '' });
    });
    var listo = function (k) { return function (v) { st[k] = v; pintar(box); }; };
    cargarNoticias().then(listo('noticias')).catch(function () { st.noticias = []; pintar(box); });
    cargarAnalisis().then(listo('analisis')).catch(function () {});
    cargarWa().then(listo('wa')).catch(function () {});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
