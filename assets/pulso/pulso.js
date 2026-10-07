/* Pulso del día (home)
   - Cartel chico a la derecha del hero (#plsCard): 6 cotizaciones de Argentina,
     6 de EE.UU. y el mundo, y los dos titulares más nuevos. Se refresca solo.
   - "Ampliar" baja una cortina desde arriba con las 12 cotizaciones en una
     franja y las noticias de cada lado (titular + bajada del diario + link).
   - Gráfico del S&P 500 debajo del título (#htxSpx), 1D / 1M / 1A, con
     TradingView Lightweight Charts (ya cargado por la home).
   Datos: endpoint /pulso y /serie del worker manfredi-mercados. */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  // En local, ?api=http://127.0.0.1:PUERTO apunta a un wrangler dev distinto; se
  // recuerda para que no se pierda al pasar por /bienvenida u otra página.
  var API = 'https://manfredi-mercados.nachito2502.workers.dev';
  if (LOCAL) {
    var q = new URLSearchParams(location.search).get('api');
    try { if (q) localStorage.setItem('pls_api', q); q = q || localStorage.getItem('pls_api'); } catch (e) {}
    API = q || 'http://127.0.0.1:8790';
  }
  var TZ = 'America/Argentina/Buenos_Aires';
  var DATA = null, last = {}, reintento = false;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n(v, d) { return Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }

  // la moneda va chica y apagada para que se lea primero el número
  function valor(q) {
    if (q.price == null) return '—';
    if (q.unit === 'pb') return Math.round(q.price) + '<small style="margin:0 0 0 4px">pb</small>';
    var d = q.unit === '$' ? (Number.isInteger(q.price) ? 0 : 2) : (Math.abs(q.price) >= 10000 ? 0 : 2);
    return (q.unit ? '<small>' + q.unit + '</small>' : '') + n(q.price, d);
  }
  function signo(q) {
    var v = q.unit === 'pb' ? q.delta : q.change;
    if (v == null || isNaN(v)) return 0;
    if (Math.abs(v) < 0.005) return 0;
    return (v > 0 ? 1 : -1) * (q.inverso ? -1 : 1);
  }
  function cambio(q) {
    var v = q.unit === 'pb' ? q.delta : q.change;
    if (v == null || isNaN(v)) return '—';
    if (q.unit === 'pb') return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(Math.round(v)) + ' pb';
    if (Math.abs(v) < 0.005) return '0,00%';
    return (v > 0 ? '+' : '−') + n(Math.abs(v), 2) + '%';
  }
  function cls(q) { var s = signo(q); return s > 0 ? 'up' : s < 0 ? 'dn' : 'fl'; }
  function fechaLarga(iso) {
    var d = iso ? new Date(iso) : new Date();
    var f = d.toLocaleDateString('es-AR', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });
    return f.charAt(0).toUpperCase() + f.slice(1).replace(',', '') + ' · ' + d.toLocaleTimeString('es-AR', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false });
  }
  function hora(iso) {
    if (!iso) return '';
    var d = new Date(iso), dia = function (x) { return x.toLocaleDateString('es-AR', { timeZone: TZ }); };
    var hh = d.toLocaleTimeString('es-AR', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false });
    var hoy = new Date(), ayer = new Date(Date.now() - 864e5);
    if (dia(d) === dia(hoy)) return hh;
    if (dia(d) === dia(ayer)) return 'Ayer ' + hh;
    return d.toLocaleDateString('es-AR', { timeZone: TZ, day: 'numeric', month: 'short' });
  }
  function link(x) { return ' href="' + esc(x.link) + '" target="_blank" rel="noopener"'; }
  function fuente(x) { return '<div class="pls-src">' + esc(x.fuente) + (x.fecha ? '<time datetime="' + esc(x.fecha) + '">' + hora(x.fecha) + '</time>' : '') + '</div>'; }

  // destello cuando un valor cambia entre refrescos
  function flash(root) {
    root.querySelectorAll('[data-q]').forEach(function (el) {
      var k = el.getAttribute('data-q'), v = parseFloat(el.getAttribute('data-p'));
      if (last[k] != null && !isNaN(v) && v !== last[k]) {
        el.classList.remove('pls-flash-up', 'pls-flash-dn'); void el.offsetWidth;
        el.classList.add(v > last[k] ? 'pls-flash-up' : 'pls-flash-dn');
      }
    });
  }
  function recordar() {
    if (!DATA) return;
    DATA.argentina.cotizaciones.concat(DATA.mundo.cotizaciones).forEach(function (q) { last[q.id] = q.price; });
  }

  /* ------------------------------ cartel chico ------------------------------ */
  var ICON_OPEN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>';
  var ICON_DOWN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';

  function grupo(titulo, arr) {
    return '<div class="pls__grp"><h3 class="pls__gt">' + titulo + '</h3><div class="pls__q">' + arr.map(function (q) {
      return '<div class="pls__qi" data-q="' + q.id + '" data-p="' + q.price + '"><div class="pls__qn">' + esc(q.name) + '</div><div class="pls__qv">' + valor(q) + '</div><div class="pls__qc ' + cls(q) + '">' + cambio(q) + '</div></div>';
    }).join('') + '</div></div>';
  }

  function pintarCard() {
    var card = $('plsCard');
    if (!card) return;
    var head = '<div class="pls__hd"><h2 class="pls__t">Pulso del día</h2><span class="pls-live">' + (DATA ? fechaLarga(DATA.updated).split(' · ')[1] : '') + '</span>' +
      '<button type="button" class="pls__open" data-pls-open aria-label="Ampliar el pulso del día">' + ICON_OPEN + '</button></div>';
    if (!DATA) {
      card.innerHTML = head + '<div class="pls__body">' + [1, 2].map(function () {
        return '<div class="pls__grp"><span class="pls-skel" style="width:90px;height:9px;margin-bottom:12px"></span><div class="pls__q">' +
          [1, 2, 3, 4, 5, 6].map(function () { return '<div><span class="pls-skel" style="width:70%;height:9px"></span><span class="pls-skel" style="width:85%;margin-top:6px"></span></div>'; }).join('') + '</div></div>';
      }).join('') + '</div>';
      return;
    }
    var tit = [DATA.argentina.noticias[0], DATA.mundo.noticias[0]].filter(Boolean);
    card.innerHTML = head + '<div class="pls__body">' +
      grupo('Argentina', DATA.argentina.cotizaciones) + grupo('EE.UU. y el mundo', DATA.mundo.cotizaciones) +
      (tit.length ? '<ul class="pls__news">' + tit.map(function (x) {
        return '<li><a' + link(x) + '>' + fuente(x) + '<div class="t">' + esc(x.titulo) + '</div></a></li>';
      }).join('') + '</ul>' : '') +
      '</div><button type="button" class="pls__more" data-pls-open>Ver el pulso completo ' + ICON_DOWN + '</button>';
    flash(card);
  }

  /* ------------------------------ cortina ------------------------------ */
  var sheet = null, scrim = null, prevFocus = null;

  function celdas(arr) {
    return arr.map(function (q) {
      return '<div class="pls-cell" data-q="' + q.id + '" data-p="' + q.price + '"><div class="n">' + esc(q.name) + '</div><div class="v">' + valor(q) + '</div><div class="c ' + cls(q) + '">' + cambio(q) + '</div></div>';
    }).join('');
  }
  function columna(titulo, nw) {
    var t = '<h3 class="pls-col__t">' + titulo + '</h3>';
    if (!nw.length) return '<div class="pls-col">' + t + '<p class="pls-empty">No hay noticias nuevas por ahora.</p></div>';
    var lead = nw.filter(function (x) { return x.imagen; })[0] || nw[0];
    var resto = nw.filter(function (x) { return x !== lead; }).slice(0, 3);
    return '<div class="pls-col">' + t +
      '<a class="pls-lead' + (lead.imagen ? '' : ' sin-img') + '"' + link(lead) + '><div>' + fuente(lead) + '<h3>' + esc(lead.titulo) + '</h3>' + (lead.resumen ? '<p>' + esc(lead.resumen) + '</p>' : '') + '</div>' +
      (lead.imagen ? '<img src="' + esc(lead.imagen) + '" alt="" loading="lazy" onerror="this.remove();this.parentNode&&this.parentNode.classList.add(\'sin-img\')">' : '') + '</a>' +
      '<ul class="pls-small">' + resto.map(function (x) {
        return '<li><a' + link(x) + '>' + fuente(x) + '<h4>' + esc(x.titulo) + '</h4>' + (x.resumen ? '<p>' + esc(x.resumen) + '</p>' : '') + '</a></li>';
      }).join('') + '</ul></div>';
  }
  function pintarSheet() {
    if (!sheet || !DATA) return;
    sheet.querySelector('.pls-sheet__in').innerHTML =
      '<header class="pls-mast"><h2 id="plsSheetT">Pulso del día</h2><div class="pls-live">' + fechaLarga(DATA.updated) + '</div><div class="pls-mast__rule"><i></i></div>' +
      '<button type="button" class="pls-x" data-pls-close aria-label="Cerrar"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg></button></header>' +
      '<div class="pls-band"><div class="pls-band__g"><span class="pls-band__l">Argentina</span>' + celdas(DATA.argentina.cotizaciones) + '</div>' +
      '<div class="pls-band__g"><span class="pls-band__l">EE.UU.</span>' + celdas(DATA.mundo.cotizaciones) + '</div></div>' +
      '<div class="pls-cols">' + columna('Argentina', DATA.argentina.noticias) + columna('EE.UU. y el mundo', DATA.mundo.noticias) + '</div>';
    flash(sheet);
  }
  function abrir() {
    if (sheet) return;
    prevFocus = document.activeElement;
    scrim = document.createElement('div'); scrim.className = 'pls-scrim';
    sheet = document.createElement('section');
    sheet.className = 'pls-sheet';
    sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-modal', 'true'); sheet.setAttribute('aria-labelledby', 'plsSheetT');
    sheet.innerHTML = '<div class="pls-sheet__in"></div>';
    var wrap = document.createElement('div'); wrap.className = 'pls-wrap';
    wrap.appendChild(scrim); wrap.appendChild(sheet);
    document.body.appendChild(wrap);
    document.body.classList.add('pls-lock');
    pintarSheet();
    scrim.addEventListener('click', cerrar);
    sheet.addEventListener('click', function (e) { if (e.target.closest('[data-pls-close]')) cerrar(); });
    document.addEventListener('keydown', teclas);
    requestAnimationFrame(function () { requestAnimationFrame(function () { wrap.classList.add('pls-open', 'pls-entering'); setTimeout(function () { wrap.classList.remove('pls-entering'); }, 900); var x = sheet.querySelector('.pls-x'); if (x) x.focus({ preventScroll: true }); }); });
  }
  function cerrar() {
    if (!sheet) return;
    var wrap = sheet.parentNode, s = sheet;
    sheet = null; scrim = null;
    wrap.classList.remove('pls-open');
    document.body.classList.remove('pls-lock');
    document.removeEventListener('keydown', teclas);
    var fin = function () { if (wrap.parentNode) wrap.parentNode.removeChild(wrap); };
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) fin();
    else { s.addEventListener('transitionend', fin, { once: true }); setTimeout(fin, 700); }
    if (prevFocus && prevFocus.focus) prevFocus.focus({ preventScroll: true });
  }
  function teclas(e) {
    if (e.key === 'Escape') { cerrar(); return; }
    if (e.key === 'Tab' && sheet) { // el foco no se escapa de la cortina
      var f = sheet.querySelectorAll('a[href], button');
      if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    }
  }
  document.addEventListener('click', function (e) { if (e.target.closest('[data-pls-open]')) abrir(); });

  /* ------------------------------ datos ------------------------------ */
  function cargar() {
    return fetch(API + '/pulso', { signal: AbortSignal.timeout(15000) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) {
        if (!d || !d.argentina) throw new Error('sin datos');
        DATA = d;
        pintarCard(); pintarSheet(); pintarSpxHead(); recordar();
      })
      .catch(function (e) {
        console.warn('[pulso]', e.message);
        var card = $('plsCard');
        if (card && !DATA) card.innerHTML = '<div class="pls__hd"><h2 class="pls__t">Pulso del día</h2></div><div class="pls__body"><p class="pls-empty">No pudimos cargar las cotizaciones. Probá de nuevo en un rato.</p></div>';
        // primer intento fallido (ej. el worker tardó): se reintenta enseguida, no al minuto
        if (!DATA && !reintento) { reintento = true; setTimeout(cargar, 4000); }
      });
  }

  /* ------------------------------ S&P 500 ------------------------------ */
  var spx = { tf: '1M', ch: null, serie: null, req: 0, cache: {} };
  var TF_TXT = { '1D': 'hoy', '1M': 'en 1 mes', '1A': 'en 1 año' };

  function montarSpx() {
    var box = $('htxSpx');
    if (!box) return;
    box.innerHTML =
      '<div class="htx-spx__top"><div><div class="htx-spx__k">S&amp;P 500 <span class="pls-live" id="htxSpxLive"></span></div>' +
      '<div class="htx-spx__px"><span class="htx-spx__v" id="htxSpxV">—</span><span class="htx-spx__c" id="htxSpxC"></span><span class="htx-spx__p" id="htxSpxP"></span></div></div>' +
      '<div class="pls-seg" id="htxSpxTf" role="group" aria-label="Período">' + ['1D', '1M', '1A'].map(function (t) { return '<button type="button" data-tf="' + t + '" class="' + (t === spx.tf ? 'on' : '') + '">' + t + '</button>'; }).join('') + '</div></div>' +
      '<div class="htx-spx__chart"><div id="htxSpxChart" style="position:absolute;inset:0"></div><div class="htx-spx__msg" id="htxSpxMsg" hidden></div></div>';
    $('htxSpxTf').addEventListener('click', function (e) {
      var b = e.target.closest('[data-tf]');
      if (!b || b.dataset.tf === spx.tf) return;
      spx.tf = b.dataset.tf;
      [].forEach.call(this.children, function (x) { x.classList.toggle('on', x === b); });
      serieSpx();
    });
    (function esperar(t0) {
      if (window.LightweightCharts) return graficoSpx();
      if (Date.now() - t0 < 10000) setTimeout(function () { esperar(t0); }, 100);
    })(Date.now());
  }
  function graficoSpx() {
    var LC = window.LightweightCharts, el = $('htxSpxChart');
    spx.ch = LC.createChart(el, {
      autoSize: true,
      layout: { background: { type: 'solid', color: 'transparent' }, textColor: 'rgba(238,242,248,.62)', fontFamily: "'IBM Plex Sans', system-ui, sans-serif", fontSize: 11.5, attributionLogo: false },
      grid: { vertLines: { visible: false }, horzLines: { color: 'rgba(238,242,248,.045)' } },
      rightPriceScale: { borderVisible: false, scaleMargins: { top: .12, bottom: .04 } },
      timeScale: { borderVisible: false, timeVisible: true, secondsVisible: false, fixLeftEdge: true, fixRightEdge: true },
      crosshair: { mode: LC.CrosshairMode.Magnet, vertLine: { color: 'rgba(242,201,76,.45)', labelBackgroundColor: '#1d3357', style: 3 }, horzLine: { color: 'rgba(242,201,76,.3)', labelBackgroundColor: '#1d3357', style: 3 } },
      localization: { locale: 'es-AR', priceFormatter: function (p) { return n(p, 0); },
        timeFormatter: function (t) { return new Date(t * 1000).toLocaleString('es-AR', spx.tf === '1D' ? { timeZone: TZ, hour: '2-digit', minute: '2-digit' } : { timeZone: TZ, day: '2-digit', month: 'short', year: '2-digit' }); } },
      handleScale: false, handleScroll: false
    });
    spx.serie = spx.ch.addSeries(LC.AreaSeries, { lineColor: '#f2c94c', lineWidth: 2, topColor: 'rgba(242,201,76,.26)', bottomColor: 'rgba(242,201,76,0)', priceLineVisible: false, lastValueVisible: true, crosshairMarkerBorderColor: '#0b1528', crosshairMarkerBackgroundColor: '#f2c94c', crosshairMarkerRadius: 5 });
    serieSpx();
  }
  function serieSpx() {
    if (!spx.serie) return;
    var tf = spx.tf, id = ++spx.req, msg = $('htxSpxMsg');
    var poner = function (pts) {
      if (id !== spx.req) return;
      msg.hidden = true;
      spx.serie.setData(pts.map(function (p) { return { time: p.t, value: p.c }; }));
      spx.ch.timeScale().fitContent();
      var a = pts[0].c, z = pts[pts.length - 1].c, v = (z - a) / a * 100;
      var p = $('htxSpxP');
      p.innerHTML = tf === '1D' ? '' : '<b class="' + (v > 0 ? 'up' : v < 0 ? 'dn' : '') + '">' + (v > 0 ? '+' : v < 0 ? '−' : '') + n(Math.abs(v), 2) + '%</b> ' + TF_TXT[tf];
    };
    if (spx.cache[tf]) return poner(spx.cache[tf]);
    fetch(API + '/serie?category=indices&symbol=SP500&tf=' + tf, { signal: AbortSignal.timeout(12000) })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.points || d.points.length < 2) throw new Error(d.error || 'sin datos');
        spx.cache[tf] = d.points; poner(d.points);
      })
      .catch(function () { if (id === spx.req) { msg.hidden = false; msg.textContent = 'No pudimos cargar el gráfico.'; } });
  }
  function pintarSpxHead() {
    var q = DATA && DATA.mundo.cotizaciones.filter(function (x) { return x.id === 'sp500'; })[0];
    if (!q || !$('htxSpxV')) return;
    var v = $('htxSpxV'), prev = parseFloat(v.getAttribute('data-p'));
    v.textContent = n(q.price, 2);
    v.setAttribute('data-p', q.price);
    if (!isNaN(prev) && prev !== q.price) { v.classList.remove('pls-flash-up', 'pls-flash-dn'); void v.offsetWidth; v.classList.add(q.price > prev ? 'pls-flash-up' : 'pls-flash-dn'); }
    var c = $('htxSpxC');
    c.textContent = cambio(q) + ' hoy';
    c.className = 'htx-spx__c ' + cls(q);
    $('htxSpxLive').textContent = fechaLarga(DATA.updated).split(' · ')[1];
    if (spx.tf === '1D') { delete spx.cache['1D']; serieSpx(); }
  }

  function iniciar() {
    if (!$('plsCard') && !$('htxSpx')) return;
    pintarCard();
    montarSpx();
    cargar();
    setInterval(function () { if (!document.hidden) cargar(); }, 60000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
