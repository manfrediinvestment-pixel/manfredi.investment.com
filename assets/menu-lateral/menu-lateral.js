/* Menú lateral de todo el sitio (feat/menu-lateral) — "app shell".
   Barra izquierda a toda la altura: logo arriba (con botón para achicarla a solo íconos),
   grupos con ícono y flecha, opciones con su ícono, separadores entre bloques. Arriba a la
   derecha queda una barra con dónde estás + la cuenta. Las opciones de cada grupo se leen de las
   pestañas internas que ya existen (Mercados, Calendario, Portfolio, Pro): al tocar una opción se
   "aprieta" esa pestaña, así no se duplica lógica. Solo en pantallas ≥1100px; en celular sigue el ☰. */
(function () {
  'use strict';
  var MQ = window.matchMedia('(min-width: 1100px)');
  var K_AB = 'mi_menu_lateral_abiertos', K_MINI = 'mi_menu_lateral_mini';

  // Íconos de trazo (24×24), mismo grosor en todos.
  var IC = {
    inicio: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    mercados: '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    datos: '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-8"/><path d="M22 20H2"/>',
    noticias: '<rect x="3" y="4" width="14" height="16" rx="2"/><path d="M17 8h3a1 1 0 0 1 1 1v9a2 2 0 0 1-2 2"/><path d="M7 8h6M7 12h6M7 16h4"/>',
    calendario: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    portfolio: '<path d="M21 12A9 9 0 1 1 12 3v9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
    pro: '<path d="m3 8 4 4 5-7 5 7 4-4-2 11H5z"/>',
    herramientas: '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    star: '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    linea: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    globo: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    bono: '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    torta: '<path d="M21 12A9 9 0 1 1 12 3v9z"/>',
    moneda: '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .8-3 2s1.3 1.7 3 2 3 .8 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6v2M12 16v2"/>',
    gota: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    cripto: '<path d="M12 2 21 7v10l-9 5-9-5V7z"/><path d="M12 22V12M21 7l-9 5-9-5"/>',
    lista: '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/>',
    bandera: '<path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/>',
    barras: '<path d="M6 20V12M12 20V6M18 20v-4"/>',
    resumen: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
    escudo: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/>',
    porc: '<path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
    chispa: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.5 7.2L4 21l1.8-5.5A8 8 0 1 1 21 12z"/>',
    libro: '<path d="M4 4h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v15h-6a2 2 0 0 0-2 2 2 2 0 0 0-2-2H4z"/><path d="M12 5v16"/>',
    billetera: '<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M16 13h2M3 10h18M6 6l9-3 1 3"/>',
    calc: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>',
    birrete: '<path d="m2 9 10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5M22 9v6"/>',
    persona: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    lupa: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    tablero: '<rect x="3" y="3" width="8" height="10" rx="1.5"/><rect x="13" y="3" width="8" height="6" rx="1.5"/><rect x="13" y="11" width="8" height="10" rx="1.5"/><rect x="3" y="15" width="8" height="6" rx="1.5"/>',
    nota: '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    ayuda: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01"/>',
    punto: '<circle cx="12" cy="12" r="3"/>'
  };
  function svg(k, cls) { return '<svg class="' + (cls || 'ml-ic') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (IC[k] || IC.punto) + '</svg>'; }
  // ícono de cada opción según su nombre
  var POR_NOMBRE = [
    [/favorit/i, 'star'], [/mapa/i, 'grid'], [/acciones|adr/i, 'linea'], [/cedear/i, 'globo'], [/bono/i, 'bono'],
    [/fondo/i, 'torta'], [/cripto/i, 'cripto'], [/commod/i, 'gota'], [/d[oó]lar/i, 'moneda'],
    [/^todo/i, 'lista'], [/argentina|ee\.?uu/i, 'bandera'], [/resultado/i, 'barras'], [/dividend/i, 'moneda'],
    [/resumen/i, 'resumen'], [/rendimiento/i, 'linea'], [/riesgo/i, 'escudo'], [/diversif/i, 'torta'], [/ratio/i, 'porc'],
    [/warren/i, 'chispa'], [/chat/i, 'chat'], [/informe/i, 'libro'], [/gasto/i, 'billetera'], [/calculadora/i, 'calc'],
    [/university/i, 'birrete'], [/asesor/i, 'persona'], [/tablero/i, 'tablero'], [/inflaci/i, 'porc'],
    [/explorador/i, 'lupa'], [/calendario/i, 'calendario'], [/an[aá]lisis/i, 'nota'], [/noticia/i, 'noticias']
  ];
  function icono(n) { for (var i = 0; i < POR_NOMBRE.length; i++) if (POR_NOMBRE[i][0].test(n)) return POR_NOMBRE[i][1]; return 'punto'; }

  // Bloques separados por una línea; cada grupo lee sus opciones de la pestaña interna (src) o de una lista fija.
  var BLOQUES = [
    [{ id: 'inicio', n: 'Inicio', ic: 'inicio', hash: '' }],
    [
      { id: 'mercados', n: 'Mercados', ic: 'mercados', tab: 'mercados', hash: 'mercados', src: '#mktTabs .mkt-tab' },
      { id: 'datos', n: 'Argentina en datos', ic: 'datos', hash: 'datos', items: [
        { n: 'Tablero', hash: 'datos' }, { n: 'Inflación', hash: 'datos-inflacion' },
        { n: 'Explorador de series', hash: 'datos-explorador' }, { n: 'Calendario INDEC', hash: 'datos-calendario' }] },
      { id: 'noticias', n: 'Noticias', ic: 'noticias', hash: 'reportes', items: [
        { n: 'Noticias', hash: 'reportes', sub: 'noticias' }, { n: 'Análisis e informes', hash: 'analisis' }] },
      { id: 'calendario', n: 'Calendario', ic: 'calendario', tab: 'calendario', hash: 'calendario', src: '#calTabs button' }
    ],
    [
      { id: 'portfolio', n: 'Portfolio', ic: 'portfolio', tab: 'portfolio', hash: 'portfolio', src: '#pfSecNav .pf-sec-tab' },
      { id: 'pro', n: 'Manfredi Pro', ic: 'pro', hash: 'pro', pro: true, src: '#proNav [data-pro-tab]' }
    ],
    [
      { id: 'herramientas', n: 'Herramientas', ic: 'herramientas', hash: 'herramientas', items: [
        { n: 'Warren IA', fn: function () { if (typeof window.toggleWarren === 'function') window.toggleWarren(); } },
        { n: 'Gastos del mes', finview: 'gastos', fn: function () { window.miOpenFinView && window.miOpenFinView('gastos'); } },
        { n: 'Calculadora de objetivos', finview: 'calculadora', fn: function () { window.miOpenFinView && window.miOpenFinView('calculadora'); } },
        { n: 'University', hash: 'university' }, { n: 'Asesoría personalizada', hash: 'asesoria' }] }
    ]
  ];
  var GRUPOS = [].concat.apply([], BLOQUES);
  function grupo(id) { return GRUPOS.filter(function (g) { return g.id === id; })[0]; }

  function hashActual() { return (location.hash || '').replace('#', ''); }
  function grupoActivo() {
    var h = hashActual();
    if (!h) return 'inicio';
    if (h === 'datos' || h.indexOf('datos-') === 0) return 'datos';
    if (h === 'reportes' || h === 'analisis' || h.indexOf('analista-') === 0 || h.indexOf('nota-') === 0 || h === 'autor') return 'noticias';
    if (h === 'pro' || h === 'pro-warren' || h === 'inversiones') return 'pro';
    if (h === 'finanzas' || h === 'herramientas' || h === 'university' || h === 'asesoria' || h.indexOf('asesoria-') === 0) return 'herramientas';
    var g = GRUPOS.filter(function (x) { return x.hash === h || x.tab === h; })[0];
    return g ? g.id : 'inicio';
  }
  function texto(b) {
    var c = b.cloneNode(true);
    c.querySelectorAll('svg, span, i, b, small, em, sup').forEach(function (x) { x.remove(); });
    return (c.textContent || '').replace(/\s+/g, ' ').trim() || (b.textContent || '').replace(/\s+/g, ' ').trim();
  }
  function prendido(b) { return b.classList.contains('active') || b.classList.contains('on') || b.getAttribute('aria-selected') === 'true'; }
  function leer(k, def) { try { var v = localStorage.getItem(k); return v == null ? def : JSON.parse(v); } catch (e) { return def; } }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  var abiertos = leer(K_AB, {}) || {}, mini = !!leer(K_MINI, false), side, lista, crumb, pend = 0;

  function opciones(g) {
    if (g.src) {
      return Array.prototype.map.call(document.querySelectorAll(g.src), function (b, i) {
        var n = texto(b), resto = (b.textContent || '').replace(/\s+/g, '').replace(n.replace(/\s+/g, ''), '').replace(/Nuevo/i, '');
        return { n: n, i: i, on: prendido(b), nuevo: !!b.querySelector('.mt-new'), cant: /^\d+$/.test(resto) ? resto : '' };
      }).filter(function (o) { return o.n; });
    }
    var h = hashActual(), act = grupoActivo() === g.id;
    return (g.items || []).map(function (it, i) {
      var on = false;
      if (act && it.hash) on = it.hash === h;
      if (act && it.finview) { var fb = document.querySelector('#finViewTabs [data-finview="' + it.finview + '"]'); on = !!(fb && prendido(fb)) && (h === 'herramientas' || h === 'finanzas'); }
      return { n: it.n, i: i, on: on };
    });
  }

  function dibujar() {
    pend = 0;
    if (!lista) return;
    var act = grupoActivo(), h = '', subAct = '';
    BLOQUES.forEach(function (bl, bi) {
      if (bi) h += '<hr class="ml-sep">';
      bl.forEach(function (g) {
        var esAct = act === g.id, tiene = !!(g.src || g.items), ab = tiene && !mini && (abiertos[g.id] != null ? abiertos[g.id] : esAct);
        if (esAct && tiene && !mini && abiertos[g.id] == null) ab = true;
        h += '<div class="ml-g' + (esAct ? ' act' : '') + (ab ? ' open' : '') + '">' +
          '<div class="ml-gh"><button type="button" class="ml-gl" data-ml-go="' + g.id + '" title="' + g.n + '"' + (esAct ? ' aria-current="page"' : '') + '>' + svg(g.ic) +
          '<span class="ml-t">' + g.n + (g.pro ? '<b class="ml-pro">PRO</b>' : '') + '</span></button>' +
          (tiene ? '<button type="button" class="ml-chev" data-ml-tg="' + g.id + '" aria-label="' + (ab ? 'Cerrar ' : 'Abrir ') + g.n + '" aria-expanded="' + ab + '">' + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>' : '') +
          '</div>';
        if (ab) {
          var ops = opciones(g);
          h += '<div class="ml-gb">';
          if (!ops.length) h += '<span class="ml-vacio">Cargando…</span>';
          ops.forEach(function (o) {
            var on = esAct && o.on; if (on) subAct = o.n;
            h += '<button type="button" class="ml-item' + (on ? ' on' : '') + '" data-ml-g="' + g.id + '" data-ml-i="' + o.i + '">' +
              '<span class="ml-t">' + o.n + '</span>' + (o.nuevo ? '<b class="ml-new">Nuevo</b>' : '') + (o.cant ? '<span class="ml-cant">' + o.cant + '</span>' : '') + '</button>';
          });
          h += '</div>';
        } else if (esAct && tiene) {
          var o2 = opciones(g).filter(function (o) { return o.on; })[0]; if (o2) subAct = o2.n;
        }
        h += '</div>';
      });
    });
    if (h !== dibujar._h) { dibujar._h = h; lista.innerHTML = h; }
    cabecera();
    if (crumb) {
      var g = grupo(act);
      var ch = g ? ('<span class="ml-cr-ic">' + svg(g.ic, '') + '</span><span class="ml-cr-g">' + g.n + '</span>' + (subAct && subAct !== g.n ? '<span class="ml-cr-s" aria-hidden="true"></span><span class="ml-cr-o">' + subAct + '</span>' : '')) : '';
      if (ch !== dibujar._c) { dibujar._c = ch; crumb.innerHTML = ch; }
    }
  }
  function pedirDibujo() { if (!pend) pend = requestAnimationFrame(dibujar); }

  // ---------- Encabezado parejo para todas las secciones: mismo lugar, misma letra, sin movimiento ----------
  var DESC = {
    mercados: 'Acciones, CEDEARs, bonos, cripto y dólares, con precios en tiempo real.',
    datos: 'Los números oficiales de la economía argentina, directo del INDEC.',
    noticias: 'Lo que mueve a los mercados hoy y el análisis de nuestros invitados.',
    calendario: 'Los datos económicos, resultados y dividendos de la semana.',
    portfolio: 'Tus inversiones, cuánto rinden y cuánto riesgo tienen, en un solo lugar.',
    pro: 'Informes de research, el chat de socios y Warren IA.',
    herramientas: 'Warren IA, tus gastos y la calculadora de objetivos.',
    university: 'Cursos para aprender a invertir desde cero.'
  };
  function cabecera() {
    var act = grupoActivo(); if (act === 'inicio') return;
    var h = hashActual(), sec = document.querySelector('section[data-tab]:not(.tab-hidden)');
    if (!sec || sec.getAttribute('data-tab') === 'inicio' || sec.getAttribute('data-tab') === 'asesoria') return;
    var g = grupo(act), titulo = g ? g.n : '', d = DESC[act] || '';
    if (sec.getAttribute('data-tab') === 'university') { titulo = 'University'; d = DESC.university; }
    var ph = sec.querySelector(':scope > .ml-ph');
    if (!ph) { ph = document.createElement('header'); ph.className = 'ml-ph'; sec.insertBefore(ph, sec.firstChild); }
    var html = '<div class="ml-ph-in"><h1 class="ml-ph-t">' + titulo + '</h1>' + (d ? '<p class="ml-ph-d">' + d + '</p>' : '') + '</div>' +
      (act === 'mercados' ? '<span class="ml-ph-live"><i></i>En vivo</span>' : act === 'datos' ? '<span class="ml-ph-live"><i></i>Fuente: INDEC</span>' : '');
    if (ph._h !== html) { ph._h = html; ph.innerHTML = html; }
    if (act === 'mercados') {
      var bar = sec.querySelector('.mt-bar'), strip = sec.querySelector('.mt-strip');
      if (bar && strip && bar.nextElementSibling !== strip) strip.parentNode.insertBefore(bar, strip);
    }
    indicador();
  }
  function indicador() {
    var tabs = document.getElementById('mktTabs'); if (!tabs || !tabs.offsetParent) return;
    var ind = tabs.querySelector('.ml-tab-ind');
    if (!ind) { ind = document.createElement('i'); ind.className = 'ml-tab-ind'; ind.setAttribute('aria-hidden', 'true'); tabs.appendChild(ind); }
    var on = tabs.querySelector('.mkt-tab.active'); if (!on) { ind.style.width = '0'; return; }
    ind.style.width = on.offsetWidth + 'px';
    ind.style.transform = 'translateX(' + on.offsetLeft + 'px)';
  }

  function irGrupo(g) {
    if (g.id === 'inicio') { if (location.hash) location.hash = ''; window.scrollTo(0, 0); return; }
    if (hashActual() === g.hash) { window.scrollTo(0, 0); return; }
    location.hash = g.hash;
    if (g.id === 'noticias') setTimeout(function () { var b = document.querySelector('[data-nt-sub="noticias"]'); if (b && !b.classList.contains('on')) b.click(); }, 80);
  }
  function irA(g, i) {
    if (g.src) {
      var ejecutar = function () { var bs = document.querySelectorAll(g.src); if (bs[i]) bs[i].click(); window.scrollTo(0, 0); };
      if (grupoActivo() !== g.id) { location.hash = g.hash; setTimeout(ejecutar, 80); } else ejecutar();
      return;
    }
    var it = g.items[i];
    if (it.fn) { it.fn(); setTimeout(pedirDibujo, 120); return; }
    if (it.hash) {
      if (location.hash === '#' + it.hash) window.scrollTo(0, 0); else location.hash = it.hash;
      if (it.sub) setTimeout(function () { var b = document.querySelector('[data-nt-sub="' + it.sub + '"]'); if (b && !b.classList.contains('on')) b.click(); }, 80);
    }
  }

  function ponerMini(v) {
    mini = v; guardar(K_MINI, v);
    document.documentElement.classList.toggle('ml-mini', v);
    var t = side && side.querySelector('.ml-col');
    if (t) { t.setAttribute('aria-label', v ? 'Expandir menú' : 'Achicar menú'); t.setAttribute('aria-expanded', String(!v)); }
    dibujar();
  }

  function montar() {
    if (side) return;
    side = document.createElement('aside');
    side.className = 'ml-side'; side.id = 'mlSide';
    side.innerHTML =
      '<div class="ml-top"><a href="#" class="ml-logo" data-ml-go="inicio" aria-label="Manfredi Investment, inicio">' +
        '<span class="ml-mark"><svg class="mi-mark"><use href="#miMark"/></svg></span>' +
        '<span class="ml-brand"><b>Manfredi</b><small>Investment</small></span></a>' +
        '<button type="button" class="ml-col" aria-label="Achicar menú" aria-expanded="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg></button></div>' +
      '<nav class="ml-list" aria-label="Secciones del sitio"></nav>' +
      '<div class="ml-foot"><button type="button" class="ml-gl ml-ayuda" title="Ayuda">' + svg('ayuda') + '<span class="ml-t">Ayuda</span></button></div>';
    document.body.appendChild(side);
    lista = side.querySelector('.ml-list');

    // barra de arriba: dónde estás (a la izquierda) + la cuenta (lo que ya tenía el navbar, a la derecha)
    var inner = document.querySelector('.navbar .nav-inner');
    if (inner && !inner.querySelector('.ml-crumb')) { crumb = document.createElement('div'); crumb.className = 'ml-crumb'; inner.insertBefore(crumb, inner.firstChild); }
    // la cinta de cotizaciones pasa debajo de la barra de arriba
    var tk = document.querySelector('.ticker-bar'), nb = document.querySelector('.navbar');
    if (tk && nb && nb.nextElementSibling !== tk) nb.parentNode.insertBefore(tk, nb.nextSibling);

    side.addEventListener('click', function (e) {
      var col = e.target.closest('.ml-col'); if (col) { ponerMini(!mini); return; }
      if (e.target.closest('.ml-ayuda')) { var hst = document.getElementById('miAyuda'), t = hst && hst.shadowRoot && hst.shadowRoot.getElementById('trig'); if (t) t.click(); return; }
      var go = e.target.closest('[data-ml-go]');
      if (go) { e.preventDefault(); var g = grupo(go.dataset.mlGo); if (g) { if (mini && (g.src || g.items) && grupoActivo() === g.id) { ponerMini(false); return; } irGrupo(g); } return; }
      var tg = e.target.closest('[data-ml-tg]');
      if (tg) { var id = tg.dataset.mlTg, ab = tg.getAttribute('aria-expanded') === 'true'; abiertos[id] = !ab; guardar(K_AB, abiertos); dibujar(); return; }
      var it = e.target.closest('.ml-item[data-ml-i]');
      if (it) { var g2 = grupo(it.dataset.mlG); if (g2) irA(g2, +it.dataset.mlI); }
    });
    new MutationObserver(function (ms) {
      for (var k = 0; k < ms.length; k++) { var tg = ms[k].target; if (side.contains(tg) || (crumb && crumb.contains(tg)) || (tg.classList && tg.classList.contains('ml-tab-ind'))) continue; if (ms[k].type === 'childList' && ms[k].addedNodes.length === 1 && ms[k].addedNodes[0].className === 'ml-tab-ind') continue; pedirDibujo(); return; }
    }).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'aria-selected'] });
    window.addEventListener('hashchange', function () {
      // al cambiar de sección, la que se abre arranca desplegada y la anterior vuelve a su estado guardado
      var a = grupoActivo(); if (abiertos[a] === false) { delete abiertos[a]; guardar(K_AB, abiertos); }
      pedirDibujo();
    });
    window.addEventListener('resize', function () { requestAnimationFrame(indicador); });
    ponerMini(mini);
  }
  // el botón flotante de Ayuda pasa al pie del menú (está en un shadow DOM: se le inyecta un estilo)
  function ayudaFlotante(on) {
    var hst = document.getElementById('miAyuda');
    if (!hst || !hst.shadowRoot) { if (on) setTimeout(function () { ayudaFlotante(MQ.matches); }, 400); return; }
    var st = hst.shadowRoot.getElementById('mlHide');
    if (!st) { st = document.createElement('style'); st.id = 'mlHide'; st.textContent = '.trig{display:none!important}'; hst.shadowRoot.appendChild(st); }
    st.disabled = !on;
  }
  function aplicar() {
    var on = MQ.matches;
    ayudaFlotante(on);
    document.documentElement.classList.toggle('ml-on', on);
    document.documentElement.classList.toggle('ml-mini', on && mini);
    if (on) montar();
  }
  if (document.readyState !== 'loading') aplicar(); else document.addEventListener('DOMContentLoaded', aplicar);
  if (MQ.addEventListener) MQ.addEventListener('change', aplicar); else MQ.addListener(aplicar);
})();
