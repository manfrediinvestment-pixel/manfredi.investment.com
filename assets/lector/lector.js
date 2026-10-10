/* Lector de informes en PDF: window.openPdf(url, título, info?) en todo el sitio.
   - info (opcional): { fecha, tapa } para el encabezado.
   - Barra de progreso mientras baja el PDF; después se arman las páginas con su
     tamaño y se dibujan (nítidas, según la densidad de la pantalla) a medida que
     se acercan a la vista. Página actual, zoom en escritorio, descarga.
   - Esc o la X cierran; el foco vuelve a donde estaba.
   Usa pdf.js (window.pdfjsLib), que ya carga la página. */
(function () {
  var lx = null, doc = null, tarea = null, obsDibujo = null, obsActual = null;
  var st = { zoom: 1, base: 0, paginas: [], foco: null, info: null };
  var ZOOMS = [0.75, 1, 1.25, 1.5, 2];

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function q(sel) { return lx && lx.querySelector(sel); }
  var ICON = {
    menos: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/></svg>',
    mas: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    bajar: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
    cerrar: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>'
  };

  function pdfjs() {
    return new Promise(function (ok, mal) {
      var t0 = Date.now();
      (function esperar() {
        if (window.pdfjsLib) {
          if (!window.pdfjsLib.GlobalWorkerOptions.workerSrc) window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
          return ok(window.pdfjsLib);
        }
        if (Date.now() - t0 > 12000) return mal(new Error('No cargó el lector de PDF'));
        setTimeout(esperar, 100);
      })();
    });
  }

  function abrir(url, titulo, info) {
    if (lx) cerrar(true);
    st = { zoom: 1, base: 0, paginas: [], foco: document.activeElement, info: info || {} };
    var meta = [st.info.etiqueta || 'Informe semanal', st.info.fecha].filter(Boolean).join(' · ');
    lx = document.createElement('div');
    lx.className = 'lx';
    lx.setAttribute('role', 'dialog'); lx.setAttribute('aria-modal', 'true'); lx.setAttribute('aria-labelledby', 'lxT');
    lx.innerHTML = '<div class="lx-scrim" data-cerrar></div><div class="lx-panel">' +
      '<header class="lx-top">' +
        (st.info.tapa ? '<span class="lx-thumb"><img src="' + esc(st.info.tapa) + '" alt=""></span>' : '') +
        '<div class="lx-id"><h2 class="lx-t" id="lxT">' + esc(titulo) + '</h2><div class="lx-m" id="lxM">' + esc(meta) + '</div></div>' +
        '<div class="lx-tools"><span class="lx-pg" id="lxPg" aria-live="polite"></span>' +
          '<div class="lx-zoom" role="group" aria-label="Zoom"><button type="button" data-z="-1" aria-label="Alejar">' + ICON.menos + '</button><span id="lxZ">100%</span><button type="button" data-z="1" aria-label="Acercar">' + ICON.mas + '</button></div>' +
          '<a class="lx-btn lx-dl" href="' + esc(url) + '" download aria-label="Descargar el PDF">' + ICON.bajar + '<span>Descargar</span></a>' +
          '<button type="button" class="lx-btn lx-x" data-cerrar aria-label="Cerrar">' + ICON.cerrar + '</button></div>' +
      '</header><div class="lx-bar"><i id="lxBar"></i></div><div class="lx-body" id="lxBody"><div class="lx-pages" id="lxPages"></div></div></div>';
    document.body.appendChild(lx);
    document.documentElement.style.overflow = 'hidden';
    lx.addEventListener('click', function (e) {
      if (e.target.closest('[data-cerrar]')) cerrar();
      var z = e.target.closest('[data-z]');
      if (z) zoom(+z.dataset.z);
    });
    document.addEventListener('keydown', teclas);
    requestAnimationFrame(function () { requestAnimationFrame(function () { if (lx) { lx.classList.add('on'); q('.lx-x').focus({ preventScroll: true }); } }); });
    pintarZoom();
    // páginas fantasma mientras baja el PDF
    q('#lxPages').innerHTML = [1, 2].map(function () { return '<div class="lx-page" style="max-width:860px;aspect-ratio:210/297"></div>'; }).join('');
    cargar(url);
  }

  function cargar(url) {
    var yo = lx;
    pdfjs().then(function (lib) {
      if (yo !== lx) return;
      tarea = lib.getDocument(url);
      tarea.onProgress = function (p) { if (p.total && q('#lxBar')) q('#lxBar').style.transform = 'scaleX(' + Math.min(1, p.loaded / p.total) + ')'; };
      return tarea.promise;
    }).then(function (d) {
      if (!d || yo !== lx) return;
      doc = d;
      var bar = q('#lxBar'); bar.style.transform = 'scaleX(1)'; bar.style.opacity = '0';
      var m = q('#lxM'); m.textContent = (m.textContent ? m.textContent + ' · ' : '') + d.numPages + (d.numPages === 1 ? ' página' : ' páginas');
      return d.getPage(1).then(function (p1) {
        var v = p1.getViewport({ scale: 1 });
        st.base = v.width;
        armar(v.width / v.height);
      });
    }).catch(function (e) {
      if (yo !== lx) return;
      console.warn('[lector]', e && e.message);
      q('#lxBody').innerHTML = '<div class="lx-msg">No pudimos mostrar el informe acá.<br><a href="' + esc(url) + '" target="_blank" rel="noopener">Abrir el PDF en otra pestaña →</a></div>';
      q('#lxBar').style.opacity = '0';
    });
  }

  function anchoPagina() {
    var body = q('#lxBody');
    var cs = getComputedStyle(body);
    var disp = body.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    return Math.round(Math.min(disp, 860) * st.zoom);
  }

  function armar(prop) {
    var cont = q('#lxPages'), w = anchoPagina(), html = '';
    for (var i = 1; i <= doc.numPages; i++) html += '<div class="lx-page" data-p="' + i + '" style="width:' + w + 'px;aspect-ratio:' + prop + '"><canvas></canvas><span class="num">' + i + '</span></div>';
    cont.innerHTML = html;
    st.paginas = [].slice.call(cont.children);
    var body = q('#lxBody');
    obsDibujo = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) dibujar(en.target); });
    }, { root: body, rootMargin: '900px 0px' });
    obsActual = new IntersectionObserver(function () { actual(); }, { root: body, threshold: [0, .25, .5, .75, 1] });
    st.paginas.forEach(function (el) { obsDibujo.observe(el); obsActual.observe(el); });
    body.addEventListener('scroll', actual, { passive: true });
    actual();
  }

  function dibujar(el) {
    if (!doc || el.dataset.w === String(el.offsetWidth)) return;
    var w = el.offsetWidth; el.dataset.w = String(w);
    var n = +el.dataset.p, yo = lx;
    doc.getPage(n).then(function (pg) {
      if (yo !== lx) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2.5);
      var v = pg.getViewport({ scale: (w / pg.getViewport({ scale: 1 }).width) * dpr });
      var c = document.createElement('canvas');
      c.width = Math.floor(v.width); c.height = Math.floor(v.height);
      el.style.aspectRatio = v.width + '/' + v.height;
      return pg.render({ canvasContext: c.getContext('2d'), viewport: v }).promise.then(function () {
        if (yo !== lx || el.dataset.w !== String(w)) return;
        var viejo = el.querySelector('canvas');
        el.replaceChild(c, viejo);
        requestAnimationFrame(function () { el.classList.add('ok'); });
      });
    }).catch(function (e) { console.warn('[lector] página ' + n + ':', e && e.message); el.dataset.w = ''; });
  }

  // la página que más se ve
  function actual() {
    if (!doc || !lx) return;
    var body = q('#lxBody'), top = body.getBoundingClientRect().top, alto = body.clientHeight, mejor = 1, max = -1;
    st.paginas.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var vis = Math.min(r.bottom, top + alto) - Math.max(r.top, top);
      if (vis > max) { max = vis; mejor = +el.dataset.p; }
    });
    q('#lxPg').innerHTML = '<span class="w">Página </span><b>' + mejor + '</b><span class="w"> de </span><span class="s"> / </span>' + doc.numPages;
  }

  function pintarZoom() {
    var i = ZOOMS.indexOf(st.zoom);
    q('#lxZ').textContent = Math.round(st.zoom * 100) + '%';
    q('[data-z="-1"]').disabled = i <= 0;
    q('[data-z="1"]').disabled = i >= ZOOMS.length - 1;
  }
  function zoom(dir) {
    var i = ZOOMS.indexOf(st.zoom) + dir;
    if (i < 0 || i >= ZOOMS.length) return;
    var body = q('#lxBody'), rel = body.scrollTop / Math.max(1, body.scrollHeight);
    st.zoom = ZOOMS[i]; pintarZoom();
    if (!doc) return;
    redimensionar();
    body.scrollTop = rel * body.scrollHeight;
  }
  function redimensionar() {
    if (!doc || !lx) return;
    var w = anchoPagina();
    st.paginas.forEach(function (el) { el.style.width = w + 'px'; el.classList.remove('ok'); });
    // se vuelven a dibujar las que están cerca de la vista
    st.paginas.forEach(function (el) { obsDibujo.unobserve(el); obsDibujo.observe(el); });
  }
  var tRes = 0;
  window.addEventListener('resize', function () { clearTimeout(tRes); tRes = setTimeout(redimensionar, 180); });

  function teclas(e) {
    if (!lx) return;
    if (e.key === 'Escape') { e.preventDefault(); cerrar(); return; }
    if ((e.key === '+' || e.key === '=') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); zoom(1); }
    if (e.key === '-' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); zoom(-1); }
    if (e.key === 'Tab') { // el foco no sale del lector
      var f = lx.querySelectorAll('a[href], button:not(:disabled)');
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    }
  }

  function cerrar(ya) {
    if (!lx) return;
    var el = lx, foco = st.foco;
    lx = null;
    if (obsDibujo) obsDibujo.disconnect(); if (obsActual) obsActual.disconnect();
    if (tarea && tarea.destroy) { try { tarea.destroy(); } catch (e) {} }
    tarea = null; doc = null;
    document.removeEventListener('keydown', teclas);
    document.documentElement.style.overflow = '';
    var fin = function () { if (el.parentNode) el.parentNode.removeChild(el); };
    if (ya || matchMedia('(prefers-reduced-motion: reduce)').matches) fin();
    else { el.classList.add('off'); el.classList.remove('on'); setTimeout(fin, 200); }
    if (foco && foco.focus) foco.focus({ preventScroll: true });
  }

  window.openPdf = abrir;
  window.closePdf = function () { cerrar(); };
})();
