/* Pestaña Noticias → sub-pestaña "Análisis e informes" (analistas invitados).
   - Arriba de Noticias: [Noticias | Análisis e informes]. El hash manda:
     #analisis abre la grilla, #analista-<slug> abre el perfil de un autor.
   - Los informes semanales (papers/manifest.json) entran como un autor más,
     "Manfredi Investment". Los autores invitados salen de data/analistas.json.
   - La imagen de cada tarjeta es SIEMPRE la página 1 del PDF (campo tapa).
   - En localhost se suman los autores ficticios de data/analistas-ejemplo.json
     para ver la sección con contenido; en el sitio en vivo no se cargan.
   Abre los PDF con el lector del sitio (window.openPdf, assets/lector/lector.js). */
(function () {
  var root = document.getElementById('anPanel');
  if (!root) return;
  var TZ = 'America/Argentina/Buenos_Aires';
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var CATS = [['acciones', 'Acciones', '#8fb4ff'], ['bonos', 'Bonos', '#7fd1ae'], ['macro', 'Macro', '#e9c46a'], ['politica', 'Política', '#c3a6f2'], ['trading', 'Trading', '#f29e8e']];
  var CAT = {}; CATS.forEach(function (c) { CAT[c[0]] = { n: c[1], c: c[2] }; });
  var MANFREDI = {
    slug: 'manfredi', nombre: 'Manfredi Investment', rol: 'Research & Markets · Informes semanales y especiales', corto: 'Macro · Mercados',
    color: '#e9c46a', logo: 'assets/img/logo-mark-512.png', verificado: true, desde: '2026-05-18',
    links: { instagram: 'https://www.instagram.com/manfredinvestment', x: 'https://x.com/ManfredInvest', linkedin: 'https://www.linkedin.com/in/ignacio-manfredi-816468250/' }
  };
  var st = { autores: {}, orden: [], pubs: [], cat: 'todo', autor: 'todos', listo: false };

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fecha(iso, largo) {
    var d = new Date(iso + 'T12:00:00-03:00');
    return d.toLocaleDateString('es-AR', largo ? { timeZone: TZ, day: '2-digit', month: 'short', year: 'numeric' } : { timeZone: TZ, day: '2-digit', month: 'short' }).replace(/\./g, '').replace(/ de /g, ' ');
  }
  function miles(n) { return Number(n).toLocaleString('es-AR'); }
  function iniciales(n) { return n.split(' ').map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase(); }
  function av(a, cls) {
    return '<span class="an-av' + (cls ? ' ' + cls : '') + '" style="--c:' + esc(a.color) + '">' +
      (a.logo || a.foto ? '<img src="' + esc(a.logo || a.foto) + '" alt="">' : esc(iniciales(a.nombre))) + '</span>';
  }
  var FLECHA = '<svg class="an-arr" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>';
  var TILDE = '<span class="an-verif" title="Autor verificado">✓</span>';

  /* ------------------------------ datos ------------------------------ */
  function json(url) { return fetch(url, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(url + ' HTTP ' + r.status); return r.json(); }); }
  function sumar(d) {
    (d.autores || []).forEach(function (a) { if (!st.autores[a.slug]) { st.autores[a.slug] = a; st.orden.push(a.slug); } });
    (d.publicaciones || []).forEach(function (p) { if (st.autores[p.autor] && CAT[p.categoria]) st.pubs.push(p); });
  }
  function cargar() {
    var semanales = json('papers/manifest.json').then(function (list) {
      return {
        autores: [MANFREDI],
        publicaciones: (Array.isArray(list) ? list : []).map(function (p) {
          return {
            id: 'manfredi-' + p.num, autor: 'manfredi', categoria: 'macro', etiqueta: p.tag, titulo: p.title,
            fecha: p.publishedAt || '', fechaTexto: p.date, pdf: 'papers/' + encodeURIComponent(p.file), tapa: p.cover || 'papers/covers/' + p.num + '.jpg'
          };
        })
      };
    });
    var fuentes = [semanales, json('data/analistas.json')];
    if (LOCAL) fuentes.push(json('data/analistas-ejemplo.json'));
    return Promise.all(fuentes.map(function (f) { return f.catch(function (e) { console.warn('[analistas]', e.message); return {}; }); }))
      .then(function (ds) {
        ds.forEach(sumar);
        // sin fecha exacta (semanales viejos) se ordenan por la fecha escrita
        st.pubs.forEach(function (p) { p._t = p.fecha ? Date.parse(p.fecha) : Date.parse(fechaDeTexto(p.fechaTexto)) || 0; });
        st.pubs.sort(function (a, b) { return b._t - a._t; });
        st.listo = true;
      });
  }
  var MESES = { enero: 0, febrero: 1, marzo: 2, abril: 3, mayo: 4, junio: 5, julio: 6, agosto: 7, septiembre: 8, octubre: 9, noviembre: 10, diciembre: 11 };
  function fechaDeTexto(t) {
    var m = /(\d{1,2}) de (\w+) de (\d{4})/.exec(t || '');
    if (!m || MESES[m[2]] == null) return '';
    var d = new Date(Date.UTC(+m[3], MESES[m[2]], +m[1], 15));
    return d.toISOString().slice(0, 10);
  }
  function cuando(p, largo) { return p.fecha ? fecha(p.fecha, largo) : (p._t ? fecha(new Date(p._t).toISOString().slice(0, 10), largo) : esc(p.fechaTexto || '')); }
  function etiqueta(p) { return p.etiqueta || CAT[p.categoria].n; }
  function deAutor(slug) { return st.pubs.filter(function (p) { return p.autor === slug; }); }

  /* ------------------------------ grilla ------------------------------ */
  function filtradas() {
    return st.pubs.filter(function (p) {
      return (st.cat === 'todo' || p.categoria === st.cat) && (st.autor === 'todos' || p.autor === st.autor);
    });
  }
  function tarjeta(p) {
    var a = st.autores[p.autor];
    return '<button type="button" class="an-it" data-id="' + esc(p.id) + '" style="--c:' + CAT[p.categoria].c + '">' +
      '<span class="an-cv"><img src="' + esc(p.tapa) + '" alt="" loading="lazy"></span>' +
      '<span class="an-tag">' + esc(etiqueta(p)) + '</span>' +
      '<span class="an-it__t">' + esc(p.titulo) + '</span>' +
      '<span class="an-by">' + av(a, 'sm') + '<b>' + esc(a.nombre) + '</b><small>' + cuando(p) + '</small></span></button>';
  }
  function destacado(p) {
    var a = st.autores[p.autor];
    var nuevo = p._t && Date.now() - p._t < 7 * 864e5;
    return '<button type="button" class="an-hero" data-id="' + esc(p.id) + '" style="--c:' + CAT[p.categoria].c + '">' +
      '<span class="an-cv"><img src="' + esc(p.tapa) + '" alt=""></span>' +
      '<span class="an-hero__b"><span class="an-tag">' + (nuevo ? 'Nuevo · ' : '') + esc(etiqueta(p)) + '</span>' +
      '<span class="an-hero__t">' + esc(p.titulo) + '</span>' +
      '<span class="an-by an-by--lg">' + av(a) + '<span><b>' + esc(a.nombre) + (a.verificado ? TILDE : '') + '</b><small>' + cuando(p, true) +
      (p.paginas ? ' · ' + p.paginas + ' pág.' : '') + '</small></span></span>' +
      '<span class="an-cta">Leer informe' + FLECHA + '</span></span></button>';
  }
  function pintarGrilla() {
    var lista = filtradas(), box = $('anList');
    if (!lista.length) { box.innerHTML = '<p class="nt-empty">Todavía no hay publicaciones en esta categoría.</p>'; return; }
    var conHero = st.cat === 'todo' && st.autor === 'todos';
    box.innerHTML = (conHero ? destacado(lista[0]) : '') + '<div class="an-shelf">' + lista.slice(conHero ? 1 : 0).map(tarjeta).join('') + '</div>';
  }
  function pintarBarra() {
    var n = function (c) { return st.pubs.filter(function (p) { return c === 'todo' || p.categoria === c; }).length; };
    $('anChips').innerHTML = [['todo', 'Todo', '#f3f6fb']].concat(CATS).map(function (c) {
      var on = st.cat === c[0];
      return '<button type="button" class="an-cat' + (on ? ' on' : '') + '" data-cat="' + c[0] + '" aria-pressed="' + on + '" style="--c:' + c[2] + '">' +
        '<span class="an-cat__n"><i></i>' + c[1] + '</span><span class="an-cat__c">' + String(n(c[0])).padStart(2, '0') + '</span></button>';
    }).join('');
  }
  function pintarRail() {
    var orden = st.orden.slice().sort(function (a, b) { return deAutor(b).length - deAutor(a).length; });
    $('anAutores').innerHTML = '<div class="an-panel__h"><span class="an-k">Columnistas</span><span class="an-panel__n">' + String(orden.length).padStart(2, '0') + '</span></div>' +
      '<ul class="an-auths">' + orden.map(function (s) {
        var a = st.autores[s];
        return '<li><a class="an-auth" href="#analista-' + esc(s) + '" style="--c:' + esc(a.color) + '">' + av(a, 'ring') +
          '<span class="an-auth__b"><b>' + esc(a.nombre) + (a.verificado ? TILDE : '') + '</b><small>' + esc(a.corto || '') + '</small></span>' +
          '<span class="an-auth__n">' + deAutor(s).length + '</span>' + FLECHA + '</a></li>';
      }).join('') + '</ul>';
  }
  function pintarCuenta() { var c = $('anCount'); if (c) c.textContent = st.pubs.length ? String(st.pubs.length).padStart(2, '0') : ''; marcarSub(); }
  function marcarSub() {
    var on = document.querySelector('[data-nt-sub].on'), ind = document.querySelector('.nt-switch__ind');
    if (!on || !ind || !on.offsetWidth) return;
    // la línea va solo bajo la palabra, no bajo el contador
    var sup = on.querySelector('sup'), w = on.offsetWidth - (sup ? sup.offsetWidth + 6 : 0);
    ind.style.left = on.offsetLeft + 'px'; ind.style.width = w + 'px';
  }

  /* ------------------------------ perfil ------------------------------ */
  var ICONOS = {
    linkedin: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.06c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.77 2.65 4.77 6.1V21h-4v-5.1c0-1.22-.02-2.78-1.7-2.78-1.7 0-1.96 1.32-1.96 2.69V21h-4z"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.9 2H22l-7.2 8.2L23 22h-6.6l-5.2-6.8L5.3 22H2.2l7.7-8.8L1.6 2h6.8l4.7 6.2zm-1.1 18h1.7L7.3 3.9H5.5z"/></svg>',
    trabajo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6"/></svg>'
  };
  var NOMBRES = { linkedin: 'LinkedIn', instagram: 'Instagram', x: 'X' };
  function links(a) {
    var l = a.links || {};
    return ['linkedin', 'instagram', 'x', 'trabajo'].filter(function (k) { return l[k]; }).map(function (k) {
      var url = k === 'trabajo' ? l[k].url : l[k], txt = k === 'trabajo' ? l[k].nombre : NOMBRES[k];
      return '<a href="' + esc(url) + '" target="_blank" rel="noopener nofollow">' + ICONOS[k] + esc(txt) + '</a>';
    }).join('');
  }
  function pintarPerfil(slug) {
    var a = st.autores[slug], box = $('anPerfil');
    if (!a) { box.innerHTML = '<a class="an-back" href="#analisis">← Análisis e informes</a><p class="nt-empty">No encontramos a este autor.</p>'; return; }
    var pubs = deAutor(slug), lect = pubs.reduce(function (s, p) { return s + (p.lecturas || 0); }, 0);
    var cats = pubs.map(function (p) { return p.categoria; }).filter(function (c, i, arr) { return arr.indexOf(c) === i; });
    var desde = a.desde ? new Date(a.desde + 'T12:00:00-03:00').toLocaleDateString('es-AR', { timeZone: TZ, month: 'short', year: 'numeric' }).replace('.', '').replace(' de ', ' ') : '';
    box.innerHTML = '<a class="an-back" href="#analisis">← Análisis e informes</a>' +
      '<section class="an-prof" style="--c:' + esc(a.color) + '">' + av(a, 'lg') +
      '<div><span class="an-tag">' + cats.map(function (c) { return CAT[c].n; }).join(' · ') + '</span>' +
      '<h3 class="an-prof__n">' + esc(a.nombre) + (a.verificado ? TILDE : '') + '</h3>' +
      '<div class="an-prof__r">' + esc(a.rol || '') + '</div><div class="an-links">' + links(a) + '</div></div>' +
      '<div class="an-pstats"><span><strong>' + pubs.length + '</strong>publicaciones</span>' +
      (lect ? '<span><strong>' + miles(lect) + '</strong>lecturas</span>' : '') +
      (desde ? '<span><strong>' + esc(desde) + '</strong>desde</span>' : '') + '</div></section>' +
      '<div class="an-shelf">' + pubs.map(tarjeta).join('') + '</div>' +
      (slug === 'manfredi' ? '' : '<p class="an-disc">Contenido de autoría de ' + esc(a.nombre) + '. Las opiniones son del autor y no constituyen recomendación de inversión ni reflejan la posición de Manfredi Investment.</p>');
  }

  /* ------------------------------ sub-pestañas ------------------------------ */
  function vista() {
    var h = (location.hash || '').replace('#', '');
    if (h === 'analisis') return { v: 'analisis' };
    if (h.indexOf('analista-') === 0) return { v: 'perfil', slug: h.slice(9) };
    return { v: 'noticias' };
  }
  function mostrar() {
    var w = vista(), an = w.v !== 'noticias';
    document.querySelectorAll('[data-nt-sub]').forEach(function (b) {
      var on = b.dataset.ntSub === (an ? 'analisis' : 'noticias');
      b.classList.toggle('on', on); b.setAttribute('aria-selected', on);
    });
    $('ntPanel').hidden = an; root.hidden = !an;
    $('ntDate').hidden = an;
    marcarSub();
    if (!an) { window.dispatchEvent(new Event('resize')); return; }
    $('anGrid').hidden = w.v !== 'analisis'; $('anPerfil').hidden = w.v !== 'perfil';
    if (!st.listo) return;
    if (w.v === 'perfil') { pintarPerfil(w.slug); window.scrollTo(0, 0); }
  }

  document.querySelectorAll('[data-nt-sub]').forEach(function (b) {
    b.addEventListener('click', function () {
      var h = b.dataset.ntSub === 'analisis' ? '#analisis' : '#informes';
      if (location.hash !== h) history.replaceState(null, '', h);
      mostrar();
    });
  });
  root.addEventListener('click', function (e) {
    var it = e.target.closest('[data-id]');
    if (it) {
      var p = st.pubs.filter(function (x) { return x.id === it.dataset.id; })[0];
      if (!p) return;
      if (typeof window.openPdf === 'function') window.openPdf(p.pdf, p.titulo, { fecha: cuando(p, true), tapa: p.tapa, etiqueta: p.autor === 'manfredi' ? etiqueta(p) : st.autores[p.autor].nombre });
      else window.open(p.pdf, '_blank', 'noopener');
      return;
    }
    var c = e.target.closest('[data-cat]');
    if (c && c.dataset.cat !== st.cat) { st.cat = c.dataset.cat; pintarBarra(); pintarGrilla(); }
  });
  window.addEventListener('resize', marcarSub);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(marcarSub);
  window.addEventListener('hashchange', mostrar);

  mostrar();
  cargar().then(function () { pintarCuenta(); pintarBarra(); pintarGrilla(); pintarRail(); mostrar(); });
})();
