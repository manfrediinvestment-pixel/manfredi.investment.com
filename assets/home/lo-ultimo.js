/* Primera vista de la home: "Lo último" (#luFront) + extras del lado izquierdo (#luLeft).
   Estilos en assets/home/lo-ultimo.css.

   Estilo "Portada" (tapa de diario, como FT / Bloomberg): a la izquierda la fecha con el estado del mercado,
   la frase, la franja "Mercado ahora" y el S&P 500; a la derecha tres secciones con nombre
   (Noticias, Informes, Análisis) y el canal de WhatsApp en una línea.

   Datos (todos reales):
   - Noticias: worker manfredi-noticias (con foto).
   - Análisis de invitados: worker manfredi-analistas (/publicados).
   - Informes: INFORMES_RECIENTES (abajo). Al actualizar o publicar un informe, sumarlo ARRIBA.
   - Mercado: worker manfredi-mercados (/pulso).
   - Canal de WhatsApp: último resumen del worker manfredi-comunidad. */
(function () {
  'use strict';

  var INFORMES_RECIENTES = [
    { t: 'ANT',  nombre: 'Anthropic', fecha: '2026-11-19', nota: 'Informe nuevo',          titulo: 'Anthropic tras su salida a bolsa: ingresos +1.127% y un run-rate de $81 mil millones' },
    { t: 'NVDA', nombre: 'NVIDIA',    fecha: '2026-11-18', nota: 'Actualizado al 3T FY27', titulo: 'NVIDIA: ingresos +103% en el primer trimestre sin Jensen Huang' },
    { t: 'UBER', nombre: 'Uber',      fecha: '2026-11-17', nota: 'Actualizado al 3T26',    titulo: 'Uber: Gross Bookings +20% y una oferta de US$14.800 millones por Delivery Hero' }
  ];

  var NOTICIAS = 'https://manfredi-noticias.nachito2502.workers.dev/noticias';
  var ANALISTAS = 'https://manfredi-analistas.nachito2502.workers.dev';
  var COMUNIDAD = 'https://manfredi-comunidad.nachito2502.workers.dev';
  var MERCADOS = 'https://manfredi-mercados.nachito2502.workers.dev';
  var TZ = 'America/Argentina/Buenos_Aires';
  var REDUCIR = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  var IC_WA = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2Zm4.52 11.99c-.25-.12-1.47-.72-1.7-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.16.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28Z"/></svg>';
  var FLECHA = '<svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>';

  /* ------------------------------ utilidades ------------------------------ */
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function json(u) { return fetch(u, { cache: 'no-cache', signal: AbortSignal.timeout(10000) }).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); }); }
  function diaAR(d) { return d.toLocaleDateString('es-AR', { timeZone: TZ }); }
  function hace(iso) {
    if (!iso) return '';
    var soloDia = /^\d{4}-\d{2}-\d{2}$/.test(iso);
    var t = soloDia ? new Date(iso + 'T12:00:00-03:00') : new Date(iso);
    var m = Math.round((Date.now() - t) / 6e4);
    if (isNaN(m)) return '';
    if (soloDia) {
      if (diaAR(t) === diaAR(new Date())) return 'hoy';
      if (diaAR(t) === diaAR(new Date(Date.now() - 864e5))) return 'ayer';
    } else {
      if (m < 1) return 'recién';
      if (m < 60) return 'hace ' + m + ' min';
      if (m < 24 * 60) return 'hace ' + Math.round(m / 60) + ' h';
      if (diaAR(t) === diaAR(new Date(Date.now() - 864e5))) return 'ayer';
    }
    return t.toLocaleDateString('es-AR', { day: 'numeric', month: 'short', timeZone: TZ }).replace('.', '');
  }
  function num(v, d) { return Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function pct(c) { return (c > 0 ? '+' : c < 0 ? '−' : '') + num(Math.abs(c), 2) + '%'; }
  function cls(c) { return c > 0.005 ? 'up' : c < -0.005 ? 'dn' : ''; }

  // estado del mercado de EE.UU. en hora argentina (11:30 a 18:00, lunes a viernes)
  function estadoMercado() {
    var p = new Intl.DateTimeFormat('es-AR', { timeZone: TZ, weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var g = function (k) { return (p.filter(function (x) { return x.type === k; })[0] || {}).value; };
    var wd = String(g('weekday')).toLowerCase(), min = (+g('hour')) * 60 + (+g('minute'));
    var finde = /^s[áa]b|^dom/.test(wd);
    if (finde) return { abierto: false, txt: 'Mercado cerrado · fin de semana' };
    if (min < 690) return { abierto: false, txt: 'Abre a las 11:30' };
    if (min >= 1080) return { abierto: false, txt: 'Mercado cerrado' };
    return { abierto: true, txt: 'Mercado abierto' };
  }
  function fechaLarga() {
    var s = new Date().toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long', timeZone: TZ });
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  /* --------------------------------- datos --------------------------------- */
  var st = { noticias: null, analisis: null, autores: {}, wa: null, mkt: null };

  function cargarNoticias() {
    var marcar = function (l, o) { return (l || []).map(function (n) { var x = {}; for (var k in n) x[k] = n[k]; x._o = o; return x; }); };
    var orden = function (d) { return marcar(d.argentina || d.noticias, 'ar').concat(marcar(d.wallstreet, 'us')).sort(function (a, b) { return new Date(b.fecha || 0) - new Date(a.fecha || 0); }); };
    return json(NOTICIAS).then(orden).catch(function () {
      return Promise.all([json('reports/argentina.json'), json('reports/wallstreet.json')]).then(function (r) { return orden({ argentina: r[0].noticias, wallstreet: r[1].noticias }); });
    });
  }
  function cargarAnalisis() {
    return json(ANALISTAS + '/publicados').then(function (d) {
      (d.autores || []).forEach(function (a) { st.autores[a.slug] = a; });
      return (d.publicaciones || []).filter(function (p) { return st.autores[p.autor]; })
        .sort(function (a, b) { return String(b.fecha).localeCompare(String(a.fecha)); })
        .slice(0, 4).map(function (p) {
          if (p.tapa && p.tapa[0] === '/') p.tapa = ANALISTAS + p.tapa;
          if (p.pdf && p.pdf[0] === '/') p.pdf = ANALISTAS + p.pdf;
          return p;
        });
    });
  }
  function cargarWa() {
    return json(COMUNIDAD + '/chat/gratis').then(function (d) {
      var m = ((d && d.mensajes) || []).filter(function (x) { return x.tipo === 'resumen' && !x.borrado; }).slice(-1)[0];
      if (m && typeof m.datos === 'string') { try { m.datos = JSON.parse(m.datos); } catch (e) { m.datos = {}; } }
      return m || null;
    });
  }
  function cargarMercado() {
    return json(MERCADOS + '/pulso').then(function (d) {
      var todo = ((d.argentina || {}).cotizaciones || []).concat((d.mundo || {}).cotizaciones || []);
      var de = function (id) { return todo.filter(function (q) { return q.id === id; })[0] || {}; };
      return {
        sp500: de('sp500'), nasdaq: de('nasdaq'), btc: de('btc'), mep: de('bolsa'), riesgo: de('riesgo'), oro: de('oro')
      };
    });
  }

  /* ------------------------- piezas compartidas ------------------------- */
  function noticiasOrden() {
    var ns = st.noticias || [];
    var conFoto = ns.filter(function (n) { return n.imagen; });
    var principal = conFoto.filter(function (n) { return n._o === 'ar'; })[0] || conFoto[0] || ns[0] || null;
    var otras = ns.filter(function (n) { return n !== principal; });
    var us = otras.filter(function (n) { return n._o === 'us'; }), ar = otras.filter(function (n) { return n._o === 'ar'; });
    var resto = [];
    for (var i = 0; i < 4; i++) { if (us[i]) resto.push(us[i]); if (ar[i]) resto.push(ar[i]); }
    return { principal: principal, resto: resto };
  }
  function origen(n, corto) {
    var ar = n._o === 'ar', nom = ar ? 'Argentina' : 'Wall Street';
    return '<span class="' + (ar ? 'ar' : 'us') + '"' + (corto ? ' title="' + nom + '" aria-label="' + nom + '">' : '>' + nom) + '</span>';
  }
  function kNoticia(n, corto) {
    return '<span class="lu-k">' + origen(n, corto) + (n.fuente ? '<b>' + esc(n.fuente) + '</b>' : '') + '<i>' + esc(hace(n.fecha)) + '</i></span>';
  }
  function linkNoticia(n) { return 'href="' + esc(n.link) + '" target="_blank" rel="noopener noreferrer"'; }
  function linkInforme(i) { return 'href="informes/' + i.t.toLowerCase() + '.html" target="_blank" rel="noopener"'; }
  function logo(i, c) { return '<img class="' + (c || 'lu-th lu-th--logo') + '" src="assets/logos/' + i.t.toLowerCase() + '.png" alt="" loading="lazy">'; }
  function autor(p) {
    var a = st.autores[p.autor] || {};
    return '<span class="lu-by">' + (a.foto ? '<img src="' + esc(a.foto) + '" alt="" loading="lazy">' : '') + esc(a.nombre || '') + '</span>';
  }
  function sk(h, w) { return '<div class="lu-sk" style="height:' + h + 'px' + (w ? ';width:' + w : '') + '"></div>'; }

  // encabezado de sección con nombre: NOTICIAS · INFORMES · ANÁLISIS
  function secHd(nombre, href, extra) {
    return '<div class="lu-sec__hd"><h3>' + nombre + '</h3>' + (extra || '') +
      '<a class="lu-sec__more" href="' + href + '"' + (href.charAt(0) === '#' ? '' : ' target="_blank" rel="noopener"') + '>Ver todo' + FLECHA + '</a></div>';
  }

  function itNoticia(n) {
    return '<a class="lu-it" ' + linkNoticia(n) + '><div>' + kNoticia(n, true) + '<h4>' + esc(n.titulo) + '</h4></div>' +
      (n.imagen ? '<img class="lu-th" src="' + esc(n.imagen) + '" alt="" loading="lazy">' : '') + '</a>';
  }
  function itInforme(i) {
    return '<a class="lu-it" ' + linkInforme(i) + '><div>' +
      '<span class="lu-k"><b>' + esc(i.t) + '</b><i>' + esc(i.nombre) + ' · ' + esc(hace(i.fecha)) + '</i></span>' +
      '<h4>' + esc(i.titulo) + '</h4><span class="lu-sello">' + esc(i.nota) + '</span></div>' + logo(i) + '</a>';
  }
  function itAnalisis(p) {
    return '<a class="lu-it" href="#analista-' + esc(p.autor) + '" data-lu-pdf="' + esc(p.id) + '"><div>' +
      '<span class="lu-k"><i>' + esc(hace(p.fecha)) + '</i></span><h4>' + esc(p.titulo) + '</h4>' + autor(p) + '</div>' +
      (p.tapa ? '<img class="lu-th lu-th--tapa" src="' + esc(p.tapa) + '" alt="" loading="lazy">' : '') + '</a>';
  }
  function waLinea() {
    var link = window.MI_WA_COMUNIDAD || 'https://whatsapp.com/channel/0029Vb8rDVHB4hdUO5L2Lx17';
    var m = st.wa, txt;
    if (m) {
      var r = m.datos || {};
      txt = '<b>' + (r.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado') + ':</b> ' + esc(r.clave || String(r.intro || '').split('. ')[0]);
    } else txt = 'Un <b>resumen antes de la apertura</b> y otro <b>al cierre</b>, todos los días hábiles.';
    return '<div class="lu-wa lu-rv">' +
      '<span class="lu-wa__ic">' + IC_WA + '</span>' +
      '<div class="lu-wa__t"><span class="lu-k"><b>Canal de WhatsApp</b><i>Gratis' + (m ? ' · ' + esc(hace(new Date(m.creado).toISOString())) : '') + '</i></span><p>' + txt + '</p></div>' +
      '<a class="lu-wa__btn" href="' + esc(link) + '" target="_blank" rel="noopener">' + IC_WA + 'Seguir el canal</a></div>';
  }

  // cifras que cuentan hasta su valor al entrar
  function cifra(v, d, pre, suf) {
    return '<span class="lu-n" data-to="' + v + '" data-d="' + d + '" data-pre="' + esc(pre || '') + '" data-suf="' + esc(suf || '') + '">' + esc(pre || '') + num(v, d) + esc(suf || '') + '</span>';
  }
  function contar(root) {
    root.querySelectorAll('.lu-n:not(.lu-n--ok)').forEach(function (el) {
      el.classList.add('lu-n--ok');
      if (REDUCIR) return;
      var to = +el.dataset.to, d = +el.dataset.d, pre = el.dataset.pre, suf = el.dataset.suf, t0 = null, dur = 1100;
      var paso = function (t) {
        if (!t0) t0 = t;
        var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        el.textContent = pre + num(to * e, d) + suf;
        if (k < 1) requestAnimationFrame(paso);
      };
      requestAnimationFrame(paso);
    });
  }

  // franja de mercado: S&P 500, Nasdaq, MEP, riesgo país
  function mercado(clase) {
    var m = st.mkt;
    var celdas = [
      ['Nasdaq 100', m && m.nasdaq, 0, ''], ['Dólar MEP', m && m.mep, 0, '$'], ['Riesgo país', m && m.riesgo, 0, ''], ['Bitcoin', m && m.btc, 0, 'US$ ']
    ];
    return '<div class="' + clase + '">' + celdas.map(function (c, i) {
      var q = c[1] || {};
      var val = q.price == null ? '<span class="lu-sk" style="display:inline-block;height:18px;width:70px"></span>'
        : (c[0] === 'Riesgo país' ? cifra(Math.round(q.price), 0, '', ' pb') : cifra(q.price, c[2], c[3], ''));
      var ch = q.change != null ? '<em class="' + cls(q.change) + '">' + pct(q.change) + '</em>'
        : (q.delta != null ? '<em class="' + cls(-q.delta) + '">' + (q.delta > 0 ? '+' : '−') + Math.abs(q.delta) + ' pb</em>' : '');
      return '<div class="lu-q lu-rv" style="--d:' + (i * 70) + 'ms"><span>' + c[0] + '</span><b>' + val + '</b>' + ch + '</div>';
    }).join('') + '</div>';
  }

  /* ================================ ESTILO A ================================ */
  // Portada: tres secciones con nombre. Noticias (foto grande + 2) | Informes (2) y Análisis (2).
  function izqA(left) {
    var e = estadoMercado();
    left.innerHTML =
      '<p class="lu-date lu-rv"><span class="lu-dot' + (e.abierto ? ' on' : '') + '"></span>' + esc(fechaLarga()) + '<i>·</i>' + esc(e.txt) + '</p>' +
      mercado('lu-mkt');
  }
  function derA() {
    var o = noticiasOrden(), p = o.principal;
    var lead = p ? '<a class="lu-lead lu-rv" ' + linkNoticia(p) + '>' +
        '<div class="lu-ph lu-ph--rv">' + (p.imagen ? '<img src="' + esc(p.imagen) + '" alt="">' : '') + '</div>' +
        kNoticia(p) + '<h4 class="lu-lead__t">' + esc(p.titulo) + '</h4>' + (p.resumen ? '<p>' + esc(p.resumen) + '</p>' : '') + '</a>'
      : '<div class="lu-lead"><div class="lu-ph lu-sk"></div>' + sk(12, '40%') + sk(52) + '</div>';
    var an = st.analisis;
    return '<div class="lu-hd lu-rv"><h2>Lo último</h2><span class="lu-live">En vivo</span></div>' +
      '<div class="lu-a">' +
        '<section class="lu-sec lu-sec--n">' + secHd('Noticias', '#reportes') + lead +
          '<div class="lu-a__more">' + o.resto.slice(0, 2).map(function (n, i) { return '<div class="lu-rv" style="--d:' + (200 + i * 80) + 'ms">' + itNoticia(n) + '</div>'; }).join('') + '</div></section>' +
        '<div class="lu-a__col">' +
          '<section class="lu-sec lu-rv" style="--d:120ms">' + secHd('Informes', '#inversiones') + INFORMES_RECIENTES.slice(0, 2).map(itInforme).join('') + '</section>' +
          '<section class="lu-sec lu-rv" style="--d:220ms">' + secHd('Análisis', '#analisis', '<span class="lu-sec__sub">de inversores invitados</span>') +
            (an ? an.slice(0, 2).map(itAnalisis).join('') : sk(60)) + '</section>' +
        '</div>' +
      '</div>' + waLinea();
  }

  /* ------------------------------- montaje ------------------------------- */
  function fotos(root) { root.querySelectorAll('img').forEach(function (img) { img.addEventListener('error', function () { img.remove(); }, { once: true }); }); }
  function entrar(root) {
    // dos cuadros: primero se pinta oculto, después entra (así la animación corre siempre)
    requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.add('is-in'); contar(root); }); });
  }

  function pintar() {
    var box = document.getElementById('luFront'), left = document.getElementById('luLeft');
    if (!box) return;
    var yaEntro = box.classList.contains('is-in');
    box.innerHTML = derA();
    fotos(box);
    if (left && !left.dataset.ok) { izqA(left); left.dataset.ok = '1'; entrar(left); }
    else if (left && st.mkt) { var mk = left.querySelector('.lu-mkt'); if (mk && !mk.dataset.ok) { mk.outerHTML = mercado('lu-mkt'); left.querySelector('.lu-mkt').dataset.ok = '1'; contar(left); } }
    if (yaEntro) { box.classList.add('is-in'); contar(box); }
    else if (st.noticias !== null || pintar.tarde) entrar(box); // entra cuando ya está la noticia principal
  }

  // La membresía (lo de abajo de la home) también entra al hacer scroll.
  function revelarAbajo() {
    if (REDUCIR || !('IntersectionObserver' in window)) return;
    var sel = '.htx-member .mbr__head, .htx-member .mbr__film, .htx-member .mbr__pay';
    var els = Array.prototype.slice.call(document.querySelectorAll(sel));
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('lu-up--in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    var grupo = new Map();
    els.forEach(function (el) {
      var n = grupo.get(el.parentNode) || 0; grupo.set(el.parentNode, n + 1);
      el.style.setProperty('--d', Math.min(n, 6) * 70 + 'ms');
      el.classList.add('lu-up'); io.observe(el);
    });
  }

  function iniciar() {
    var box = document.getElementById('luFront');
    if (!box) return;
    var hero = document.querySelector('.htx-hero');
    if (hero) hero.setAttribute('data-lu', 'a');
    pintar();
    box.addEventListener('click', function (e) {
      var a = e.target.closest('[data-lu-pdf]');
      if (!a || typeof window.openPdf !== 'function') return;
      var p = (st.analisis || []).filter(function (x) { return x.id === a.dataset.luPdf; })[0];
      if (!p || !p.pdf) return;
      e.preventDefault();
      window.openPdf(p.pdf, p.titulo, { tapa: p.tapa, etiqueta: (st.autores[p.autor] || {}).nombre || '' });
    });
    var listo = function (k) { return function (v) { st[k] = v; pintar(); }; };
    setTimeout(function () { pintar.tarde = true; if (!box.classList.contains('is-in')) entrar(box); }, 2500);
    cargarNoticias().then(listo('noticias')).catch(function () { st.noticias = []; pintar(); });
    cargarAnalisis().then(listo('analisis')).catch(function () {});
    cargarWa().then(listo('wa')).catch(function () {});
    cargarMercado().then(listo('mkt')).catch(function () {});
    revelarAbajo();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
