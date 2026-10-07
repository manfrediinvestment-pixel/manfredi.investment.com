/* Pestaña Noticias (menú "Noticias", data-tab="informes")
   - Feed minuto a minuto: /noticias del worker manfredi-mercados (titular +
     bajada de Ámbito, El Cronista, Infobae y Bloomberg Línea, con región y tema).
     Filtros por región y tema; de a 20 con "Ver más noticias".
   - Informe semanal destacado arriba (papers/manifest.json, el más nuevo); la
     etiqueta "Nuevo" solo durante la semana del informe. Abre el visor de PDF.
   - Al costado: cotizaciones (/pulso) con selector Argentina / EE.UU. y los
     informes anteriores, 3 a la vista y una flecha para ver más.
   Formato y dirección del worker: window.MIPulso (assets/pulso/pulso.js). */
(function () {
  var TZ = 'America/Argentina/Buenos_Aires';
  var P = window.MIPulso;
  if (!P || !document.getElementById('ntFeed')) return;
  var POR_PAGINA = 20;
  var st = { items: [], filtro: 'todo', mostrar: POR_PAGINA, region: 'ar', pulso: null, papers: [], pag: 0 };
  var FILTROS = [['todo', 'Todo'], ['ar', 'Argentina'], ['mundo', 'EE.UU. y el mundo'], ['Dólar', 'Dólar'], ['Bonos', 'Bonos'], ['Acciones', 'Acciones'], ['Economía', 'Economía']];

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dia(t) { return new Date(t).toLocaleDateString('es-AR', { timeZone: TZ }); }
  function hhmm(t) { return new Date(t).toLocaleTimeString('es-AR', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false }); }
  function hoyLargo() {
    var f = new Date().toLocaleDateString('es-AR', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });
    return f.charAt(0).toUpperCase() + f.slice(1).replace(',', '');
  }
  function pdf(p) { return 'papers/' + encodeURIComponent(p.file); }
  function tapa(p) { return p.cover || 'papers/covers/' + p.num + '.jpg'; }
  function abrir(p) { if (typeof window.openPdf === 'function') window.openPdf(pdf(p), p.title); else window.open(pdf(p), '_blank', 'noopener'); }

  /* ------------------------------ feed ------------------------------ */
  function grupo(x) {
    var h = (Date.now() - Date.parse(x.fecha)) / 36e5;
    if (dia(x.fecha) === dia(Date.now())) return h < 2 ? 'Última hora' : 'Hoy, más temprano';
    if (dia(x.fecha) === dia(Date.now() - 864e5)) return 'Ayer';
    return 'Días anteriores';
  }
  function filtrar() {
    var f = st.filtro;
    return st.items.filter(function (x) { return f === 'todo' || x.region === f || x.tema === f; });
  }
  function pintarFeed() {
    var box = $('ntFeed'), lista = filtrar(), html = '', ult = '';
    if (!st.items.length) return;
    if (!lista.length) { box.innerHTML = '<p class="nt-empty">No hay noticias de este tema en las últimas horas.</p>'; $('ntMore').hidden = true; return; }
    lista.slice(0, st.mostrar).forEach(function (x) {
      var g = grupo(x);
      if (g !== ult) { html += '<h3 class="nt-day">' + g + '</h3>'; ult = g; }
      var hora = g === 'Días anteriores' ? new Date(x.fecha).toLocaleDateString('es-AR', { timeZone: TZ, day: 'numeric', month: 'short' }) : hhmm(x.fecha);
      html += '<a class="nt-it' + (x.imagen ? '' : ' sin-img') + '" href="' + esc(x.link) + '" target="_blank" rel="noopener">' +
        '<time class="nt-it__h" datetime="' + esc(x.fecha) + '">' + hora + '</time>' +
        '<div class="nt-it__b"><div class="nt-src"><span class="tag">' + esc(x.tema) + '</span><i></i>' + esc(x.fuente) + '</div>' +
        '<div class="nt-it__t">' + esc(x.titulo) + '</div>' + (x.resumen ? '<p class="nt-it__s">' + esc(x.resumen) + '</p>' : '') + '</div>' +
        (x.imagen ? '<img class="nt-it__img" src="' + esc(x.imagen) + '" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.parentNode.classList.add(\'sin-img\');this.remove()">' : '') + '</a>';
    });
    box.innerHTML = html;
    var resto = lista.length - st.mostrar;
    $('ntMore').hidden = resto <= 0;
  }
  function pintarChips() {
    $('ntChips').innerHTML = FILTROS.map(function (f) {
      return '<button type="button" data-f="' + f[0] + '" class="' + (f[0] === st.filtro ? 'on' : '') + '" aria-pressed="' + (f[0] === st.filtro) + '">' + f[1] + '</button>';
    }).join('');
  }
  function cargarNoticias() {
    return fetch(P.api + '/noticias', { signal: AbortSignal.timeout(15000) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) { if (d && d.items && d.items.length) { st.items = d.items; pintarFeed(); } else throw new Error('sin notas'); })
      .catch(function (e) {
        console.warn('[noticias]', e.message);
        if (!st.items.length) $('ntFeed').innerHTML = '<p class="nt-empty">No pudimos cargar las noticias. Probá de nuevo en un rato.</p>';
      });
  }

  /* ------------------------------ informe semanal ------------------------------ */
  var ICON_CAL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>';
  var ICON_DOWN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
  function pintarInforme() {
    var p = st.papers[0], box = $('ntInforme');
    if (!p) { box.hidden = true; return; }
    var pub = p.publishedAt ? Date.parse(p.publishedAt + 'T12:00:00-03:00') : NaN;
    var nuevo = !isNaN(pub) && Date.now() - pub < 7 * 864e5;
    var resumen = String(p.abstract || '').split(' · ').slice(0, 3).join(' · ');
    box.innerHTML = '<button type="button" class="nt-inf" aria-label="Leer el informe semanal: ' + esc(p.title) + '">' +
      '<span class="nt-inf__cover"><img src="' + esc(tapa(p)) + '" alt="" loading="lazy"></span>' +
      '<span><span class="nt-inf__top"><span class="nt-inf__tag' + (nuevo ? '' : ' viejo') + '">' + (nuevo ? 'Nuevo · Informe semanal' : 'Informe semanal') + '</span>' +
      '<span class="nt-inf__when">' + ICON_CAL + esc(p.date) + '</span></span>' +
      '<span class="nt-inf__t">' + esc(p.title) + '</span>' +
      (resumen ? '<span class="nt-inf__s">' + esc(resumen) + '</span>' : '') +
      '<span class="nt-inf__row"><span class="nt-btn">Leer el informe</span><small>PDF</small></span></span></button>';
    box.firstChild.addEventListener('click', function () { abrir(p); });
  }
  function pintarAnteriores() {
    var prev = st.papers.slice(1), card = $('ntPrevs');
    if (!prev.length) { card.hidden = true; return; }
    card.innerHTML = '<h3 class="nt-card__h">Informes anteriores</h3><div class="nt-prevs-win" id="ntPrevsWin"><div class="nt-prevs-list" id="ntPrevsList">' +
      prev.map(function (p, i) {
        return '<button type="button" class="nt-prev" data-i="' + (i + 1) + '"><img src="' + esc(tapa(p)) + '" alt="" loading="lazy"><span><b>' + esc(p.title) + '</b><span>' + esc(p.date) + '</span></span></button>';
      }).join('') + '</div></div>' +
      (prev.length > 3 ? '<button type="button" class="nt-prevs-more" id="ntPrevsMore"><span>Ver más</span>' + ICON_DOWN + '</button>' : '');
    card.addEventListener('click', function (e) {
      var b = e.target.closest('.nt-prev');
      if (b) abrir(st.papers[+b.dataset.i]);
      if (e.target.closest('#ntPrevsMore')) { st.pag = st.pag >= paginas() - 1 ? 0 : st.pag + 1; acomodar(); }
    });
    acomodar();
    // las tapas cargan después y cambian el alto de cada fila
    card.querySelectorAll('img').forEach(function (im) { im.addEventListener('load', acomodar); });
  }
  function paginas() { return Math.ceil((st.papers.length - 1) / 3); }
  function acomodar() {
    var win = $('ntPrevsWin'), list = $('ntPrevsList');
    if (!win || !win.offsetParent) return;
    var rows = [].slice.call(list.children), a = st.pag * 3;
    var alto = function (desde, hasta) { return rows.slice(desde, hasta).reduce(function (s, r) { return s + r.offsetHeight; }, 0); };
    win.style.height = alto(a, a + 3) + 'px';
    list.style.transform = 'translateY(' + -alto(0, a) + 'px)';
    rows.forEach(function (r, i) { r.tabIndex = i >= a && i < a + 3 ? 0 : -1; });
    var more = $('ntPrevsMore');
    if (more) {
      var fin = st.pag === paginas() - 1;
      more.classList.toggle('up', fin);
      more.firstChild.textContent = fin ? 'Volver' : 'Ver más';
    }
  }
  function cargarInformes() {
    return fetch('papers/manifest.json').then(function (r) { return r.json(); }).then(function (list) {
      st.papers = Array.isArray(list) ? list : [];
      pintarInforme(); pintarAnteriores();
    }).catch(function (e) { console.warn('[noticias] informes:', e.message); $('ntInforme').hidden = true; $('ntPrevs').hidden = true; });
  }

  /* ------------------------------ cotizaciones ------------------------------ */
  function pintarCotizaciones() {
    var d = st.pulso, box = $('ntQuotes');
    if (!d) return;
    var arr = st.region === 'ar' ? d.argentina.cotizaciones : d.mundo.cotizaciones;
    box.innerHTML = '<h3 class="nt-card__h">Cotizaciones<span class="nt-date">' + hhmm(d.updated) + '</span></h3>' +
      '<div class="nt-seg" role="group" aria-label="Región"><button type="button" data-r="ar" class="' + (st.region === 'ar' ? 'on' : '') + '">Argentina</button><button type="button" data-r="mundo" class="' + (st.region === 'mundo' ? 'on' : '') + '">EE.UU. y el mundo</button></div>' +
      '<ul class="nt-qs">' + arr.map(function (q) {
        return '<li><span class="n">' + esc(q.name) + '</span><span class="v">' + P.valor(q) + '</span><span class="c ' + P.cls(q) + '">' + P.cambio(q) + '</span></li>';
      }).join('') + '</ul><a class="nt-card__link" href="#mercados" data-tab-target="mercados">Ver todos los mercados →</a>';
  }
  function cargarCotizaciones() {
    return fetch(P.api + '/pulso', { signal: AbortSignal.timeout(15000) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) { if (d && d.argentina) { st.pulso = d; pintarCotizaciones(); } })
      .catch(function (e) { console.warn('[noticias] cotizaciones:', e.message); if (!st.pulso) $('ntQuotes').hidden = true; });
  }

  /* ------------------------------ arranque ------------------------------ */
  function visible() { var s = document.querySelector('section[data-tab="informes"]'); return s && !s.classList.contains('tab-hidden') && !document.hidden; }
  function fijar() {
    var nav = document.querySelector('.navbar');
    var pos = nav ? getComputedStyle(nav).position : '';
    document.querySelector('.nt').style.setProperty('--nt-sticky', (pos === 'sticky' || pos === 'fixed') ? nav.offsetHeight + 'px' : '0px');
  }
  var iniciado = false;
  function iniciar() {
    if (iniciado || !visible()) return;
    iniciado = true;
    fijar();
    cargarNoticias(); cargarInformes(); cargarCotizaciones();
    setInterval(function () { if (visible()) { cargarNoticias(); cargarCotizaciones(); } }, 5 * 60000);
  }

  $('ntDate').textContent = hoyLargo();
  pintarChips();
  $('ntChips').addEventListener('click', function (e) {
    var b = e.target.closest('[data-f]');
    if (!b || b.dataset.f === st.filtro) return;
    st.filtro = b.dataset.f; st.mostrar = POR_PAGINA;
    pintarChips(); pintarFeed();
    // si ya se había bajado, se vuelve al principio de la lista (la barra queda fija arriba)
    var off = (parseInt(getComputedStyle(document.querySelector('.nt')).getPropertyValue('--nt-sticky'), 10) || 0) + $('ntBar').offsetHeight;
    var top = $('ntFeed').getBoundingClientRect().top;
    if (top < off) window.scrollBy(0, top - off - 4);
  });
  $('ntMore').addEventListener('click', function () { st.mostrar += POR_PAGINA; pintarFeed(); });
  $('ntQuotes').addEventListener('click', function (e) {
    var b = e.target.closest('[data-r]');
    if (b && b.dataset.r !== st.region) { st.region = b.dataset.r; pintarCotizaciones(); }
  });
  window.addEventListener('resize', function () { fijar(); acomodar(); });
  // la pestaña puede abrirse más tarde: se carga recién cuando se ve
  window.addEventListener('hashchange', function () { setTimeout(function () { iniciar(); acomodar(); }, 50); });
  document.addEventListener('click', function (e) { if (e.target.closest('[data-tab-target="informes"]')) setTimeout(function () { iniciar(); acomodar(); }, 50); });
  if (document.readyState === 'complete') iniciar(); else window.addEventListener('load', iniciar);
})();
