/* Pestaña Noticias (menú "Noticias", data-tab="informes")
   - Feed minuto a minuto: /noticias del worker manfredi-mercados (titular +
     bajada de Ámbito, El Cronista, Infobae y Bloomberg Línea, con región y tema).
     Filtros por región y tema; de a 20 con "Ver más noticias".
   - Al costado: cotizaciones (/pulso) con selector Argentina / EE.UU.
   Los informes semanales viven en Análisis e informes → Resúmenes semanales
   (assets/analistas/analistas.js), no acá.
   Formato y dirección del worker: window.MIPulso (assets/pulso/pulso.js). */
(function () {
  var TZ = 'America/Argentina/Buenos_Aires';
  var P = window.MIPulso;
  if (!P || !document.getElementById('ntFeed')) return;
  var POR_PAGINA = 20;
  var st = { items: [], filtro: 'todo', mostrar: POR_PAGINA, region: 'ar', pulso: null };
  var FILTROS = [['todo', 'Todo'], ['ar', 'Argentina'], ['mundo', 'EE.UU. y el mundo'], ['Dólar', 'Dólar'], ['Bonos', 'Bonos'], ['Acciones', 'Acciones'], ['Economía', 'Economía']];

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dia(t) { return new Date(t).toLocaleDateString('es-AR', { timeZone: TZ }); }
  function hhmm(t) { return new Date(t).toLocaleTimeString('es-AR', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false }); }
  function hoyLargo() {
    var f = new Date().toLocaleDateString('es-AR', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });
    return f.charAt(0).toUpperCase() + f.slice(1).replace(',', '');
  }

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
  // se dibujan una vez; al elegir solo cambia la clase y la línea dorada se desliza
  function pintarChips() {
    $('ntChips').innerHTML = FILTROS.map(function (f, i) {
      return (i === 3 ? '<span class="nt-sep" aria-hidden="true"></span>' : '') +
        '<button type="button" data-f="' + f[0] + '">' + f[1] + '</button>';
    }).join('') + '<span class="nt-ind" aria-hidden="true"></span>';
    marcarChip();
  }
  function marcarChip() {
    var on = null;
    $('ntChips').querySelectorAll('[data-f]').forEach(function (b) {
      var si = b.dataset.f === st.filtro;
      b.classList.toggle('on', si); b.setAttribute('aria-pressed', si);
      if (si) on = b;
    });
    var ind = $('ntChips').querySelector('.nt-ind');
    if (!on || !on.offsetWidth) return;
    var pad = parseFloat(getComputedStyle(on).paddingRight) || 0, izq = parseFloat(getComputedStyle(on).paddingLeft) || 0;
    ind.style.transform = 'translateX(' + (on.offsetLeft + izq) + 'px) scaleX(' + (on.offsetWidth - izq - pad) + ')';
    // en el celular, que el elegido quede a la vista
    var box = $('ntChips');
    if (on.offsetLeft < box.scrollLeft || on.offsetLeft + on.offsetWidth > box.scrollLeft + box.clientWidth) box.scrollTo({ left: on.offsetLeft - 24, behavior: 'smooth' });
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
    // el ancho de cada filtro cambia cuando termina de cargar la tipografía
    marcarChip();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(marcarChip);
    cargarNoticias(); cargarCotizaciones();
    setInterval(function () { if (visible()) { cargarNoticias(); cargarCotizaciones(); } }, 5 * 60000);
  }

  $('ntDate').textContent = hoyLargo();
  pintarChips();
  $('ntChips').addEventListener('click', function (e) {
    var b = e.target.closest('[data-f]');
    if (!b || b.dataset.f === st.filtro) return;
    st.filtro = b.dataset.f; st.mostrar = POR_PAGINA;
    marcarChip(); pintarFeed();
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
  window.addEventListener('resize', function () { fijar(); marcarChip(); });
  // la pestaña puede abrirse más tarde: se carga recién cuando se ve
  window.addEventListener('hashchange', function () { setTimeout(function () { iniciar(); marcarChip(); }, 50); });
  document.addEventListener('click', function (e) { if (e.target.closest('[data-tab-target="informes"]')) setTimeout(function () { iniciar(); marcarChip(); }, 50); });
  if (document.readyState === 'complete') iniciar(); else window.addEventListener('load', iniciar);
})();
