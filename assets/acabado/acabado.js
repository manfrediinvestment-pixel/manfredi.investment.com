/* Acabado (fix/carga-movil-bienvenida): la terminación de la bienvenida en todo el sitio.
   1) Gráficos (LightweightCharts): sin cuadrícula vertical, línea horizontal apenas visible, sin bordes,
      números en Plex Mono chico, cruz de lectura fina en dorado. Va justo después de tema.js.
   2) Letra: las etiquetas cortas en mayúscula que venían en letra de máquina pasan a Instrument Sans
      espaciada (.ac-k) y los títulos en serif se ajustan (.ac-sf). Se mira solo la sección visible.
   3) Movimiento: cada sección entra de borroso a nítido, en escalera (.ac-entra, ver acabado.css). */
(function () {
  'use strict';
  /* ---------- 1) gráficos ---------- */
  var LW = window.LightweightCharts;
  if (LW && typeof LW.createChart === 'function' && !LW.__acabado) {
    var crear = LW.createChart, copia = {};
    for (var k in LW) copia[k] = LW[k];
    copia.__acabado = true;
    copia.createChart = function (el, op) {
      var ch = crear.apply(this, arguments);
      try {
        var claro = document.documentElement.getAttribute('data-tema') === 'claro';
        ch.applyOptions({
          layout: { fontFamily: "'IBM Plex Mono', ui-monospace, monospace", fontSize: 11, attributionLogo: false },
          grid: { vertLines: { visible: false }, horzLines: { color: claro ? 'rgba(11,21,38,.07)' : 'rgba(214,226,244,.06)' } },
          rightPriceScale: { borderVisible: false }, leftPriceScale: { borderVisible: false },
          timeScale: { borderVisible: false },
          crosshair: {
            vertLine: { color: 'rgba(242,201,76,.45)', width: 1, style: 3, labelBackgroundColor: claro ? '#0b1526' : '#13243b' },
            horzLine: { color: 'rgba(242,201,76,.45)', width: 1, style: 3, labelBackgroundColor: claro ? '#0b1526' : '#13243b' }
          }
        });
      } catch (e) {}
      return ch;
    };
    try { window.LightweightCharts = copia; } catch (e) {}
  }

  /* ---------- 2) letra ---------- */
  var visto = typeof WeakSet === 'function' ? new WeakSet() : null, timer = 0;
  function afinar() {
    timer = 0;
    if (!visto) return;
    var raiz = document.querySelector('section[data-tab]:not(.tab-hidden)') || document.body;
    var els = raiz.querySelectorAll('span, b, strong, small, div, h2, h3, h4, h5, h6, p, th, label, a, button, em, i');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (visto.has(el)) continue;
      if (el.childElementCount > 1) { visto.add(el); continue; }
      var t = (el.textContent || '').trim();
      if (!t) continue; // puede llenarse después
      visto.add(el);
      var cs = getComputedStyle(el), ff = cs.fontFamily;
      var letras = (t.match(/[A-Za-zÁÉÍÓÚÑáéíóúñ]/g) || []).length, dig = (t.match(/\d/g) || []).length;
      if (/Plex Mono/i.test(ff) && cs.textTransform === 'uppercase' && t.length <= 42 && letras >= 3 && dig < letras) el.classList.add('ac-k');
      else if (/Instrument Serif|DM Serif/i.test(ff) && parseFloat(cs.fontSize) >= 20) el.classList.add('ac-sf');
    }
  }
  function pedir() { if (!timer) timer = setTimeout(function () { (window.requestIdleCallback || setTimeout)(afinar); }, 350); }

  /* ---------- 3) movimiento ---------- */
  var RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches, ult = null;
  function entrar() {
    var sec = document.querySelector('section[data-tab]:not(.tab-hidden)');
    if (!sec || sec === ult) return; ult = sec;
    if (RM) return;
    sec.classList.remove('ac-entra'); void sec.offsetWidth; sec.classList.add('ac-entra');
    setTimeout(function () { sec.classList.remove('ac-entra'); }, 1200);
  }

  window.addEventListener('mi:tab', function () { entrar(); pedir(); });
  function arrancar() {
    pedir();
    new MutationObserver(pedir).observe(document.body, { childList: true, subtree: true });
    pie();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar); else arrancar();

  /* ---------- pie del sitio: el link de Warren abre el chat ---------- */
  function pie() {
    var f = document.querySelector('footer.ac-foot'); if (!f) return;
    f.addEventListener('click', function (e) { if (e.target.closest('[data-ac-warren]')) { e.preventDefault(); if (typeof window.toggleWarren === 'function') window.toggleWarren(); } });
  }
})();
