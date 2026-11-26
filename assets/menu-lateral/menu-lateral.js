/* Menú lateral de todo el sitio (feat/menu-lateral).
   Capa encima de la navegación existente: arma la barra izquierda con cada sección y sus
   opciones, y al tocar una opción "aprieta" la pestaña interna que ya existe en la página
   (Mercados, Calendario, Portfolio, Pro, Noticias, Argentina en datos). Así no se duplica lógica:
   si una sección agrega una pestaña, aparece sola en el menú. Solo en pantallas anchas (≥1100px);
   en celular sigue el menú ☰ de siempre. */
(function () {
  'use strict';
  var MQ = window.matchMedia('(min-width: 1100px)');
  var KEY = 'mi_menu_lateral_abiertos';

  // Cada grupo: de dónde salen sus opciones (src = botones de la pestaña interna) o una lista fija.
  var GRUPOS = [
    { id: 'mercados', n: 'Mercados', tab: 'mercados', hash: 'mercados', src: '#mktTabs .mkt-tab' },
    { id: 'datos', n: 'Argentina en datos', tab: 'informes', hash: 'datos', items: [
      { n: 'Tablero', hash: 'datos' }, { n: 'Inflación', hash: 'datos-inflacion' },
      { n: 'Explorador de series', hash: 'datos-explorador' }, { n: 'Calendario INDEC', hash: 'datos-calendario' }] },
    { id: 'noticias', n: 'Noticias', tab: 'informes', hash: 'reportes', items: [
      { n: 'Noticias', hash: 'reportes', sub: 'noticias' }, { n: 'Análisis e informes', hash: 'analisis' }] },
    { id: 'calendario', n: 'Calendario', tab: 'calendario', hash: 'calendario', src: '#calTabs button' },
    { id: 'portfolio', n: 'Portfolio', tab: 'portfolio', hash: 'portfolio', src: '#pfSecNav .pf-sec-tab' },
    { id: 'pro', n: 'Manfredi Pro', tab: 'inversiones', hash: 'pro', pro: true, src: '#proNav [data-pro-tab]' },
    { id: 'herramientas', n: 'Herramientas', tab: 'herramientas', hash: 'herramientas', items: [
      { n: 'Warren IA', fn: function () { if (typeof window.toggleWarren === 'function') window.toggleWarren(); } },
      { n: 'Gastos del mes', fn: function () { window.miOpenFinView && window.miOpenFinView('gastos'); }, finview: 'gastos' },
      { n: 'Calculadora de objetivos', fn: function () { window.miOpenFinView && window.miOpenFinView('calculadora'); }, finview: 'calculadora' },
      { n: 'University', hash: 'university' }, { n: 'Asesoría personalizada', hash: 'asesoria' }] }
  ];

  function hashActual() { return (location.hash || '').replace('#', ''); }
  function grupoActivo() {
    var h = hashActual();
    if (!h) return 'inicio';
    if (h === 'datos' || h.indexOf('datos-') === 0) return 'datos';
    if (h === 'reportes' || h === 'analisis' || h.indexOf('analista-') === 0 || h.indexOf('nota-') === 0 || h === 'autor') return 'noticias';
    if (h === 'pro' || h === 'pro-warren' || h === 'inversiones') return 'pro';
    if (h === 'finanzas' || h === 'herramientas' || h === 'university' || h === 'asesoria' || h.indexOf('asesoria-') === 0) return 'herramientas';
    for (var i = 0; i < GRUPOS.length; i++) if (GRUPOS[i].hash === h || GRUPOS[i].tab === h) return GRUPOS[i].id;
    return 'inicio';
  }
  function texto(b) {
    var c = b.cloneNode(true);
    c.querySelectorAll('svg, span, i, b, small, em, sup').forEach(function (x) { x.remove(); });
    var t = (c.textContent || '').replace(/\s+/g, ' ').trim();
    return t || (b.textContent || '').replace(/\s+/g, ' ').trim();
  }
  function prendido(b) {
    return b.classList.contains('active') || b.classList.contains('on') || b.getAttribute('aria-selected') === 'true';
  }
  function leerAbiertos() { try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; } }
  function guardarAbiertos(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }

  var abiertos = leerAbiertos(), side, pend = 0;

  function opciones(g) {
    if (g.src) {
      return Array.prototype.map.call(document.querySelectorAll(g.src), function (b, i) {
        var n = texto(b), resto = (b.textContent || '').replace(/\s+/g, '').replace(n.replace(/\s+/g, ''), '').replace(/Nuevo/i, ''), cant = /^\d+$/.test(resto) ? resto : '';
        return { n: n, i: i, on: prendido(b), nuevo: !!b.querySelector('.mt-new'), cant: cant };
      }).filter(function (o) { return o.n; });
    }
    var h = hashActual(), act = grupoActivo() === g.id;
    return g.items.map(function (it, i) {
      var on = false;
      if (act && it.hash) on = it.hash === h || (it.hash === 'reportes' && h === 'reportes');
      if (act && it.finview) { var fb = document.querySelector('#finViewTabs [data-finview="' + it.finview + '"]'); on = !!(fb && prendido(fb)) && (h === 'herramientas' || h === 'finanzas'); }
      return { n: it.n, i: i, on: on };
    });
  }

  function dibujar() {
    pend = 0;
    if (!side) return;
    var act = grupoActivo(), h = '';
    h += '<a class="ml-item ml-inicio' + (act === 'inicio' ? ' on' : '') + '" href="#" data-ml-inicio>Inicio</a>';
    GRUPOS.forEach(function (g) {
      var esAct = act === g.id, ab = esAct || !!abiertos[g.id];
      var ops = ab ? opciones(g) : [];
      h += '<div class="ml-g' + (esAct ? ' act' : '') + '">' +
        '<button type="button" class="ml-gh" data-ml-g="' + g.id + '" aria-expanded="' + ab + '"><span>' + g.n + (g.pro ? ' <b class="ml-pro">PRO</b>' : '') + '</span><i aria-hidden="true">' + (ab ? '−' : '+') + '</i></button>';
      if (ab) {
        h += '<div class="ml-gb">';
        if (!ops.length) h += '<span class="ml-vacio">Cargando…</span>';
        ops.forEach(function (o) {
          h += '<button type="button" class="ml-item' + (esAct && o.on ? ' on' : '') + '" data-ml-g="' + g.id + '" data-ml-i="' + o.i + '">' + o.n + (o.nuevo ? '<b class="ml-new">Nuevo</b>' : '') + (o.cant ? '<span class="ml-cant">' + o.cant + '</span>' : '') + '</button>';
        });
        h += '</div>';
      }
      h += '</div>';
    });
    side.innerHTML = h;
  }
  function pedirDibujo() { if (!pend) pend = requestAnimationFrame(dibujar); }

  function irA(g, i) {
    var esAct = grupoActivo() === g.id;
    if (g.src) {
      var ejecutar = function () {
        var bs = document.querySelectorAll(g.src);
        if (bs[i]) bs[i].click();
        window.scrollTo(0, 0);
      };
      if (!esAct) { location.hash = g.hash; setTimeout(ejecutar, 80); } else ejecutar();
      return;
    }
    var it = g.items[i];
    if (it.fn) { it.fn(); setTimeout(pedirDibujo, 120); return; }
    if (it.hash) {
      if (location.hash === '#' + it.hash) { window.scrollTo(0, 0); }
      else location.hash = it.hash;
      if (it.sub) setTimeout(function () { var b = document.querySelector('[data-nt-sub="' + it.sub + '"]'); if (b && !b.classList.contains('on')) b.click(); }, 80);
    }
  }

  function montar() {
    if (side) return;
    side = document.createElement('nav');
    side.className = 'ml-side';
    side.id = 'mlSide';
    side.setAttribute('aria-label', 'Secciones del sitio');
    document.body.appendChild(side);
    side.addEventListener('click', function (e) {
      var ini = e.target.closest('[data-ml-inicio]');
      if (ini) { e.preventDefault(); if (location.hash) location.hash = ''; window.scrollTo(0, 0); return; }
      var it = e.target.closest('.ml-item[data-ml-i]');
      if (it) { var g = GRUPOS.filter(function (x) { return x.id === it.dataset.mlG; })[0]; if (g) irA(g, +it.dataset.mlI); return; }
      var gh = e.target.closest('.ml-gh');
      if (gh) {
        var id = gh.dataset.mlG, esAct = grupoActivo() === id;
        if (esAct) { // el grupo activo no se cierra: tocar el título lleva a su primera opción
          window.scrollTo(0, 0); return;
        }
        abiertos[id] = !abiertos[id]; guardarAbiertos(abiertos); dibujar();
      }
    });
    // las pestañas internas cambian solas (datos que cargan, clics dentro de la página): seguirlas
    new MutationObserver(function (ms) {
      for (var k = 0; k < ms.length; k++) if (!side.contains(ms[k].target)) { pedirDibujo(); return; }
    }).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'aria-selected'] , characterData: false });
    window.addEventListener('hashchange', pedirDibujo);
    ubicar();
    window.addEventListener('scroll', ubicar, { passive: true });
    window.addEventListener('resize', ubicar);
    dibujar();
  }
  // la barra arranca justo debajo del navbar (que es sticky y puede tener la cinta de precios arriba)
  function ubicar() {
    if (!side) return;
    var nb = document.querySelector('.navbar');
    var top = nb ? Math.max(0, nb.getBoundingClientRect().bottom) : 0;
    side.style.top = top + 'px';
  }
  function aplicar() {
    var on = MQ.matches;
    document.documentElement.classList.toggle('ml-on', on);
    if (on) montar();
  }
  // evitar que el observer se dispare por nuestros propios cambios en bucle: el dibujo solo toca #mlSide,
  // y rAF agrupa todo en un cuadro.
  if (document.readyState !== 'loading') aplicar(); else document.addEventListener('DOMContentLoaded', aplicar);
  if (MQ.addEventListener) MQ.addEventListener('change', aplicar); else MQ.addListener(aplicar);
})();
