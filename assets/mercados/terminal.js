/* Mercados · diseño Terminal
   - window.mktDetail: panel derecho con el gráfico del activo elegido (en el
     celular se abre como hoja desde abajo). Velas o línea + volumen, con
     TradingView Lightweight Charts v5 y temporalidades 1D / 1M / YTD / 1A / 5A
     que salen del endpoint /serie del worker manfredi-mercados.
   - window.mktFci: pestaña "Fondos comunes" con reports/fci.json (CAFCI, lo
     genera scripts/build_fci.py en el workflow diario). */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var SERIE = (LOCAL ? 'http://127.0.0.1:8790' : 'https://manfredi-mercados.nachito2502.workers.dev') + '/serie';
  var TF = [['1D', '1 día'], ['1M', '1 mes'], ['YTD', 'en el año'], ['1A', '1 año'], ['5A', '5 años']];
  var SIN_INTRADIARIO = { arg_bonds: 1, dolares: 1 };
  var CACHE = {};

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pct(v, d) { if (v == null || isNaN(v)) return '—'; d = d == null ? 2 : d; return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%'; }
  function cls(v) { return v > 0 ? 'up' : v < 0 ? 'dn' : ''; }
  function precio(v, usd) { if (v == null) return '—'; var d = Math.abs(v) >= 1000 ? 0 : 2; return (usd ? 'US$ ' : '$ ') + Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function vol(n) { n = Number(n) || 0; if (!n) return '—'; if (n >= 1e12) return (n / 1e12).toFixed(1).replace('.', ',') + ' billones'; if (n >= 1e9) return (n / 1e9).toFixed(1).replace('.', ',') + ' mil M'; if (n >= 1e6) return (n / 1e6).toFixed(1).replace('.', ',') + ' M'; if (n >= 1e3) return (n / 1e3).toFixed(1).replace('.', ',') + ' mil'; return Math.round(n).toLocaleString('es-AR'); }
  function esCel() { return window.matchMedia('(max-width: 1000px)').matches; }
  function conLC(cb) { var t0 = Date.now(); (function w() { if (window.LightweightCharts) return cb(window.LightweightCharts); if (Date.now() - t0 < 10000) setTimeout(w, 100); })(); }

  /* ------------------------------ gráfico ------------------------------ */
  function crearGrafico(el, usd) {
    var LC = window.LightweightCharts;
    var ch = LC.createChart(el, {
      autoSize: true,
      layout: { background: { type: 'solid', color: 'transparent' }, textColor: 'rgba(238,242,248,.78)', fontFamily: "'IBM Plex Sans', system-ui, sans-serif", fontSize: 12, attributionLogo: true,
        panes: { separatorColor: '#1c2b44', separatorHoverColor: 'rgba(242, 201, 76, 0.45)', enableResize: true } },
      grid: { vertLines: { visible: false }, horzLines: { color: 'rgba(238,242,248,.05)' } },
      rightPriceScale: { borderVisible: false, scaleMargins: { top: .1, bottom: .06 } },
      timeScale: { borderVisible: false, timeVisible: true, secondsVisible: false, fixLeftEdge: true, fixRightEdge: true },
      crosshair: { mode: LC.CrosshairMode.Magnet, vertLine: { color: 'rgba(242,201,76,.5)', labelBackgroundColor: '#1d3357', style: 3 }, horzLine: { color: 'rgba(242,201,76,.35)', labelBackgroundColor: '#1d3357', style: 3 } },
      localization: { locale: 'es-AR',
        timeFormatter: function (t) { return new Date(t * 1000).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit' }); } },
      handleScale: { mouseWheel: false, pinch: true }, handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false }
    });
    // formato de precio solo para las series de precio (el volumen usa el suyo)
    var fmt = { type: 'custom', minMove: 0.01, formatter: function (p) { return (usd ? 'US$ ' : '$ ') + Number(p).toLocaleString('es-AR', { maximumFractionDigits: Math.abs(p) >= 1000 ? 0 : 2 }); } };
    // las dos series de precio viven en el panel 0 y se alterna cuál se ve
    var area = ch.addSeries(LC.AreaSeries, { priceFormat: fmt, lineColor: '#f2c94c', lineWidth: 2, topColor: 'rgba(242,201,76,.28)', bottomColor: 'rgba(242,201,76,0)', priceLineColor: 'rgba(242,201,76,.6)', crosshairMarkerBorderColor: '#0b1528', crosshairMarkerBackgroundColor: '#f2c94c', crosshairMarkerRadius: 5 }, 0);
    var velas = ch.addSeries(LC.CandlestickSeries, { priceFormat: fmt, upColor: '#4fc48c', downColor: '#ee7369', borderVisible: false, wickUpColor: '#4fc48c', wickDownColor: '#ee7369', priceLineColor: 'rgba(242,201,76,.6)', visible: false }, 0);
    var volumen = ch.addSeries(LC.HistogramSeries, { priceFormat: { type: 'volume' }, priceLineVisible: false, lastValueVisible: false }, 1);
    // qué paneles se ven: ambos (precio grande, volumen chico), solo precio o
    // solo volumen. Se reparte el alto con stretch factors; el usuario además
    // puede arrastrar la línea divisoria.
    var modo = 'linea', vista = 'ambos', hayVol = true;
    function aplicar() {
      var v = hayVol ? vista : 'precio';
      var p = ch.panes();
      area.applyOptions({ visible: v !== 'volumen' && modo !== 'velas' });
      velas.applyOptions({ visible: v !== 'volumen' && modo === 'velas' });
      volumen.applyOptions({ visible: v !== 'precio' });
      p[0].setStretchFactor(v === 'volumen' ? 0.0001 : v === 'precio' ? 1 : 4);
      p[1].setStretchFactor(v === 'precio' ? 0.0001 : 1);
    }
    aplicar();
    return {
      ch: ch,
      modo: function (m) { modo = m; aplicar(); },
      vista: function (v) { vista = v; aplicar(); },
      datos: function (pts) {
        area.setData(pts.map(function (p) { return { time: p.t, value: p.c }; }));
        velas.setData(pts.map(function (p) { return { time: p.t, open: p.o, high: p.h, low: p.l, close: p.c }; }));
        hayVol = pts.some(function (p) { return p.v > 0; });
        volumen.setData(hayVol ? pts.map(function (p) { return { time: p.t, value: p.v, color: p.c >= p.o ? 'rgba(79,196,140,.45)' : 'rgba(238,115,105,.45)' }; }) : []);
        aplicar();
        ch.timeScale().fitContent();
        return hayVol;
      },
      quitar: function () { ch.remove(); }
    };
  }

  /* ------------------------------ panel ------------------------------ */
  var st = { cur: null, tf: '1A', modo: 'linea', vista: 'ambos', g: null, req: 0 };

  function marcar() {
    var c = st.cur;
    document.querySelectorAll('#mktTableBody .mkt-row, #mktSearchResults .mkt-row').forEach(function (r) {
      r.classList.toggle('mt-sel', !!c && r.getAttribute('data-symbol') === c.item.symbol && r.getAttribute('data-category') === c.category);
    });
  }

  function show(o) {
    var panel = $('mktDetail');
    if (!panel) return;
    st.cur = o;
    if (SIN_INTRADIARIO[o.category] && st.tf === '1D') st.tf = '1M';
    var usd = o.currency === 'USD', item = o.item;
    var nombre = item.name && item.name !== item.symbol ? item.name : item.symbol;
    var hoy = o.change == null ? '' : '<span class="mt-d-hoy ' + cls(o.change) + '">' + pct(o.change) + ' hoy</span>';
    panel.innerHTML =
      '<button type="button" class="mt-d-close" aria-label="Cerrar">&times;</button>' +
      '<div class="mt-d-top"><div class="mt-d-id">' +
      '<div class="mt-d-h">' + o.logoHTML + '<div><h3>' + esc(nombre) + '</h3><small>' + esc(item.symbol) + ' · ' + esc(o.label) + '</small></div></div>' +
      '<div class="mt-d-px"><b>' + o.priceHTML + '</b>' + hoy + '<span class="mt-d-var"><span id="mtVar"></span><small id="mtVarL"></small></span></div></div>' +
      '<div class="mt-d-ctl"><div class="mt-seg" id="mtTf" role="group" aria-label="Temporalidad">' + TF.map(function (t) {
        var off = t[0] === '1D' && SIN_INTRADIARIO[o.category];
        return '<button type="button" data-tf="' + t[0] + '" class="' + (t[0] === st.tf ? 'on' : '') + '"' + (off ? ' disabled title="Sin datos intradiarios"' : '') + '>' + t[0] + '</button>';
      }).join('') + '</div>' +
      '<div class="mt-seg" id="mtModo" role="group" aria-label="Tipo de gráfico"><button type="button" data-m="linea" class="' + (st.modo === 'linea' ? 'on' : '') + '">Línea</button><button type="button" data-m="velas" class="' + (st.modo === 'velas' ? 'on' : '') + '">Velas</button></div>' +
      '<div class="mt-seg" id="mtVista" role="group" aria-label="Qué ver">' + [['ambos', 'Ambos'], ['precio', 'Precio'], ['volumen', 'Volumen']].map(function (v) { return '<button type="button" data-v="' + v[0] + '" class="' + (st.vista === v[0] ? 'on' : '') + '">' + v[1] + '</button>'; }).join('') + '</div></div></div>' +
      '<div class="mt-d-chart"><div class="mt-d-cv" id="mtChart"></div><div class="mt-d-msg" id="mtMsg" hidden></div></div>' +
      '<div class="mt-d-kpis" id="mtKpis"></div>';
    marcar();
    if (esCel()) { panel.classList.add('open'); document.body.classList.add('mt-sheet-open'); }
    else if (o.traer) {
      var r = panel.getBoundingClientRect();
      if (r.top < 70 || r.bottom > innerHeight) panel.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
    }
    panel.querySelector('.mt-d-close').addEventListener('click', cerrar);
    $('mtTf').addEventListener('click', function (e) { var b = e.target.closest('[data-tf]'); if (!b || b.disabled) return; st.tf = b.dataset.tf; [].forEach.call(this.children, function (x) { x.classList.toggle('on', x === b); }); cargar(); });
    $('mtModo').addEventListener('click', function (e) { var b = e.target.closest('[data-m]'); if (!b) return; st.modo = b.dataset.m; [].forEach.call(this.children, function (x) { x.classList.toggle('on', x === b); }); if (st.g) st.g.modo(st.modo); });
    $('mtVista').addEventListener('click', function (e) { var b = e.target.closest('[data-v]'); if (!b || b.disabled) return; st.vista = b.dataset.v; [].forEach.call(this.children, function (x) { x.classList.toggle('on', x === b); }); if (st.g) st.g.vista(st.vista); });
    if (st.g) { st.g.quitar(); st.g = null; }
    conLC(function () {
      if (st.cur !== o) return;
      st.g = crearGrafico($('mtChart'), usd);
      st.g.modo(st.modo);
      st.g.vista(st.vista);
      cargar();
    });
  }

  function cargar() {
    var o = st.cur, tf = st.tf, id = ++st.req;
    var key = o.category + ':' + o.item.symbol + ':' + tf;
    var msg = $('mtMsg');
    msg.hidden = false; msg.textContent = 'Cargando gráfico…'; msg.className = 'mt-d-msg';
    var p = CACHE[key] ? Promise.resolve(CACHE[key]) :
      fetch(SERIE + '?category=' + encodeURIComponent(o.category) + '&symbol=' + encodeURIComponent(o.item.symbol) + '&tf=' + tf, { signal: AbortSignal.timeout(15000) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) { var e = new Error(j && j.error || 'HTTP ' + r.status); e.propio = !!(j && j.error); throw e; } return j; }); });
    p.then(function (j) {
      if (id !== st.req || !st.g) return;
      CACHE[key] = j;
      var pts = j.points || [];
      if (pts.length < 2) throw new Error('Sin datos para esta temporalidad');
      msg.hidden = true;
      var hayVol = st.g.datos(pts);
      [].forEach.call($('mtVista').children, function (x) { if (x.dataset.v !== 'precio') { x.disabled = !hayVol; x.title = hayVol ? '' : 'Este activo no tiene volumen'; } });
      var a = pts[0].o || pts[0].c, z = pts[pts.length - 1].c, v = (z / a - 1) * 100;
      $('mtVar').textContent = pct(v); $('mtVar').className = cls(v);
      $('mtVarL').textContent = 'en ' + TF.find(function (t) { return t[0] === tf; })[1];
      var hi = Math.max.apply(null, pts.map(function (x) { return x.h; })), lo = Math.min.apply(null, pts.map(function (x) { return x.l; }));
      var usd = o.currency === 'USD';
      var k = [['Máximo', precio(hi, usd)], ['Mínimo', precio(lo, usd)]];
      if (hayVol) k.push(['Volumen promedio', vol(pts.reduce(function (t, x) { return t + x.v; }, 0) / pts.length)], ['Volumen hoy', vol(o.volume)]);
      $('mtKpis').innerHTML = k.map(function (x) { return '<div><small>' + x[0] + '</small><b>' + x[1] + '</b></div>'; }).join('');
    }).catch(function (e) {
      if (id !== st.req) return;
      msg.hidden = false; msg.className = 'mt-d-msg err';
      msg.textContent = e && e.propio ? e.message + '.' : 'No pudimos cargar el gráfico. Probá de nuevo en un momento.';
      $('mtVar').textContent = ''; $('mtVarL').textContent = ''; $('mtKpis').innerHTML = '';
    });
  }

  function cerrar() {
    var panel = $('mktDetail');
    if (panel) panel.classList.remove('open');
    document.body.classList.remove('mt-sheet-open');
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && $('mktDetail') && $('mktDetail').classList.contains('open')) cerrar(); });

  window.mktDetail = { show: show, mark: marcar, current: function () { return st.cur; }, close: cerrar };

  /* --------------------------- fondos comunes --------------------------- */
  var F = { data: null, sel: 0, cargando: false };
  function fondos(el) {
    if (!el) return;
    if (!F.data) {
      el.innerHTML = '<div class="mkt-row-msg">Cargando fondos comunes…</div>';
      if (F.cargando) return;
      F.cargando = true;
      fetch('/reports/fci.json?d=' + new Date().toISOString().slice(0, 10)).then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (d) { F.data = d; fondos(el); })
        .catch(function () { el.innerHTML = '<div class="mkt-row-msg">No pudimos cargar los fondos. Probá de nuevo en un rato.</div>'; })
        .then(function () { F.cargando = false; });
      return;
    }
    var d = F.data, c = d.categorias[F.sel];
    var fecha = (d.fecha || '').split('-').reverse().join('/');
    el.innerHTML =
      '<div class="mt-f-h"><h3>Fondos comunes <em>de inversión</em></h3><span class="mt-f-src">CAFCI · ' + esc(fecha) + '</span></div>' +
      '<div class="mt-f-cats" role="tablist">' + d.categorias.map(function (x, i) { return '<button type="button" role="tab" aria-selected="' + (i === F.sel) + '" data-f="' + i + '" class="' + (i === F.sel ? 'on' : '') + '">' + esc(x.label) + '</button>'; }).join('') + '</div>' +
      '<div class="mt-f-t"><div class="mt-f-r mt-f-head"><span></span><span>Fondo</span><span>Hoy</span><span>Mes</span><span>En el año</span><span>12 meses</span><span class="mt-hide-s">Patrimonio</span></div>' +
      c.items.map(function (f, i) {
        return '<div class="mt-f-r"><span class="mt-f-n">' + (i + 1) + '</span><span class="mt-f-name"><b>' + esc(f.nombre) + '</b><small>' + (f.horizonte ? 'Horizonte ' + esc(f.horizonte) + ' · ' : '') + esc(f.moneda) + '</small></span>' +
          '<span class="' + cls(f.dia) + '"><i class="mt-chip ' + cls(f.dia) + '">' + pct(f.dia, 3) + '</i></span><span class="' + cls(f.mes) + '">' + pct(f.mes) + '</span><span class="' + cls(f.ytd) + '">' + pct(f.ytd, 1) + '</span><span class="' + cls(f.anual) + '">' + pct(f.anual, 1) + '</span>' +
          '<span class="mt-hide-s">' + (f.moneda === 'USD' ? 'US$ ' : '$ ') + vol(f.patrimonio) + '</span></div>';
      }).join('') + '</div>' +
      '<p class="mt-f-note">Rendimientos pasados no garantizan rendimientos futuros. Esto no es una recomendación de inversión.</p>';
    el.querySelector('.mt-f-cats').addEventListener('click', function (e) { var b = e.target.closest('[data-f]'); if (b) { F.sel = +b.dataset.f; fondos(el); } });
  }
  window.mktFci = { render: fondos };
})();
