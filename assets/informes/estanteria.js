/* Pestaña Informes: arma la estantería a partir de las pick-card ocultas de
   #inversiones (la lista que actualizan las skills de informes: un informe nuevo
   aparece solo, en su sector) y de informes/catalogo.json (trimestre, secciones,
   gráficos, cifras de la tapa y fecha; lo regenera scripts/catalogo-informes.mjs
   todos los días). La ficha de arriba trae el precio del último año del worker
   manfredi-mercados (/serie), que se actualiza solo. */
(function () {
  var root = document.getElementById('est');
  if (!root) return;
  var MERCADOS = 'https://manfredi-mercados.nachito2502.workers.dev/serie?category=usa_stocks&tf=1A&symbol=';
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var ORDEN = ['semis', 'software', 'bigtech', 'bancos', 'defensivos', 'argentina'];
  var NOMBRES = { semis: 'Semiconductores', software: 'Software', bigtech: 'Big Tech', bancos: 'Bancos y pagos', defensivos: 'Defensivos', argentina: 'Argentina' };
  var ACENTO = { semis: '#3fc1c9', software: '#8b7cf6', bigtech: '#5b8def', bancos: '#4fb37f', defensivos: '#e0a24a', argentina: '#74b9e8' };
  var DESTACADOS = [{ t: 'AAPL', b: '#c3cad6' }, { t: 'MSFT', b: '#3b8cf0' }, { t: 'TSLA', b: '#e3343f' }];
  var ETQ = { 'Ingresos TTM': 'Ingresos 12 meses', 'Ingresos FY2026 (TTM)': 'Ingresos 12 meses', 'Var. ingresos (últ. trim.)': 'Crecimiento trim.', 'Margen bruto TTM': 'Margen bruto', 'Margen operativo TTM': 'Margen operativo' };

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function corto(n) { return String(n || '').replace(/,? Inc\.?$|,? Inc\.,? | Corporation$| Incorporated$| plc$| N\.V\.$| S\.A\.$| SE$|,? Co\.$| Company$| Holdings?$/g, '').replace(/^The /, '').trim(); }
  function fmtF(iso) { if (!iso) return ''; var p = iso.split('-'); return +p[2] + ' ' + MES[+p[1] - 1]; }
  function hoyISO() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function nuevo(iso) { return iso && (new Date(hoyISO()) - new Date(iso)) / 864e5 <= 10; }

  // 1) las pick-card: una por empresa, en su sector
  var sectores = [], todos = [];
  document.querySelectorAll('#inversiones .inv-panel[data-sector-panel]').forEach(function (panel) {
    var key = panel.getAttribute('data-sector-panel');
    var tab = document.querySelector('#invTabs [data-sector="' + key + '"]');
    var sec = { key: key, nombre: NOMBRES[key] || (tab ? tab.textContent.trim() : key), libros: [] };
    panel.querySelectorAll('.pick-card').forEach(function (card) {
      var tk = (card.querySelector('.pick-ticker') || {}).textContent || '';
      var btn = card.querySelector('a.pick-btn[href]');
      var href = btn && btn.getAttribute('href');
      var img = card.querySelector('img.pick-logo');
      var it = { t: tk.trim(), n: ((card.querySelector('.pick-name') || {}).textContent || '').trim(), sec: key,
        href: href && href !== '#' ? href : '', logo: img ? img.getAttribute('src') : '', soon: card.classList.contains('pick-card--soon') || !href || href === '#' };
      if (!it.t) return;
      sec.libros.push(it); todos.push(it);
    });
    if (sec.libros.length) sectores.push(sec);
  });
  sectores.sort(function (a, b) { var ia = ORDEN.indexOf(a.key), ib = ORDEN.indexOf(b.key); return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib); });
  var CAT = {};
  var filtro = 'todos';

  function cover(d) {
    var c = CAT[d.t] || {};
    var pie = d.soon ? 'Próximamente' : esc(String(c.q || '').replace(/\s*\(.*$/, ''));
    return '<span class="est-cover" style="--acc:' + (ACENTO[d.sec] || '#5b8def') + '"><span class="est-cover__frame"></span>' +
      '<span class="est-cover__in"><span class="est-cover__top">Equity Research</span>' +
      (d.logo ? '<img class="est-cover__logo" src="' + esc(d.logo) + '" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">' : '<span style="margin-top:auto"></span>') +
      '<span class="est-cover__tk' + (d.t.length > 4 ? ' largo' : '') + '">' + esc(d.t) + '</span><span class="est-cover__name">' + esc(corto(d.n)) + '</span>' +
      '<span class="est-cover__bot"><span>' + pie + '</span>' + (!d.soon && nuevo(c.f) ? '<span class="est-cover__new">Nuevo</span>' : '<i></i>') + '</span></span></span>';
  }
  function libro(d) {
    var c = CAT[d.t] || {};
    if (d.soon) {
      return '<button type="button" class="est-book soon" data-pedir="' + esc(d.t) + '" style="border:0;background:none;padding:0;text-align:left;font:inherit">' + cover(d) +
        '<span class="est-book__meta"><span>' + esc(corto(d.n)) + '</span><span class="est-pill">En preparación</span></span></button>';
    }
    return '<a class="est-book" href="' + esc(d.href) + '" target="_blank" rel="noopener">' + cover(d) +
      '<span class="est-book__meta"><span>' + esc(corto(d.n)) + '</span><time>' + fmtF(c.f) + '</time></span>' +
      (c.secs ? '<span class="est-book__depth">' + c.secs + ' secciones · ' + c.ch + ' gráficos</span>' : '') + '</a>';
  }
  function ordenar(l) {
    return l.slice().sort(function (a, b) {
      if (a.soon !== b.soon) return a.soon ? 1 : -1;
      return String((CAT[b.t] || {}).f || '').localeCompare(String((CAT[a.t] || {}).f || ''));
    });
  }
  var FLECHA = function (d) { return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="' + d + '"/></svg>'; };
  function estante(sec, grilla) {
    return '<section class="est-shelf"><div class="est-shelf__h"><h3>' + esc(sec.nombre) + '</h3>' +
      (grilla ? '' : '<div class="est-arrows"><button type="button" data-dir="-1" aria-label="Anterior">' + FLECHA('m15 18-6-6 6-6') + '</button><button type="button" data-dir="1" aria-label="Siguiente">' + FLECHA('m9 18 6-6-6-6') + '</button></div>') +
      '</div><div class="est-track' + (grilla ? ' g' : '') + '"><div class="est-row' + (grilla ? ' grid' : '') + '">' + ordenar(sec.libros).map(libro).join('') + '</div></div></section>';
  }
  function pintar() {
    var conInforme = todos.filter(function (d) { return !d.soon; }).length;
    document.getElementById('estSecs').innerHTML = [{ key: 'todos', nombre: 'Todos', libros: todos }].concat(sectores).map(function (s) {
      var n = s.libros.filter(function (d) { return !d.soon; }).length;
      var av = s.key === 'todos' ? '<svg class="est-sec__av" aria-hidden="true"><use href="#miMark"/></svg>' : (s.libros[0] && s.libros[0].logo ? '<img class="est-sec__av" src="' + esc(s.libros[0].logo) + '" alt="">' : '');
      return '<button type="button" class="est-sec' + (s.key === filtro ? ' on' : '') + '" data-s="' + s.key + '" aria-pressed="' + (s.key === filtro) + '">' + av + '<span class="est-sec__t">' + esc(s.nombre) + '</span><span class="est-sec__n">' + n + '</span></button>';
    }).join('');
    var lista = filtro === 'todos' ? sectores : sectores.filter(function (s) { return s.key === filtro; });
    var n = filtro === 'todos' ? conInforme : lista[0].libros.filter(function (d) { return !d.soon; }).length;
    document.getElementById('estCnt').innerHTML = '<b>' + n + '</b> ' + (n === 1 ? 'informe' : 'informes');
    document.getElementById('estShelves').innerHTML = lista.map(function (s) { return estante(s, filtro !== 'todos'); }).join('');
    document.querySelectorAll('#estShelves .est-row:not(.grid)').forEach(flechas);
  }
  function flechas(row) {
    var a = row.closest('.est-shelf').querySelectorAll('.est-arrows button');
    if (!a.length) return;
    a[0].disabled = row.scrollLeft < 8;
    a[1].disabled = row.scrollLeft + row.clientWidth >= row.scrollWidth - 8;
  }

  document.getElementById('estSecs').addEventListener('click', function (e) {
    var b = e.target.closest('.est-sec'); if (!b) return;
    filtro = b.getAttribute('data-s'); pintar();
  });
  var shelves = document.getElementById('estShelves');
  shelves.addEventListener('click', function (e) {
    var b = e.target.closest('.est-arrows button');
    if (b) { var row = b.closest('.est-shelf').querySelector('.est-row'); row.scrollBy({ left: +b.getAttribute('data-dir') * row.clientWidth * .8 }); return; }
    var p = e.target.closest('[data-pedir]');
    if (p && typeof miOpenPedirInforme === 'function') miOpenPedirInforme(p.getAttribute('data-pedir'));
  });
  shelves.addEventListener('scroll', function (e) { if (e.target.classList && e.target.classList.contains('est-row')) flechas(e.target); }, true);

  // 2) ficha destacada: Apple, Microsoft y Tesla con el precio del último año
  var fx = document.getElementById('estFicha'), series = {}, cur = 0, W = 700, H = 260;
  function pr(v) { return '$' + v.toFixed(2); }
  function pct(c) { return (c >= 0 ? '+' : '') + c.toFixed(1).replace('.', ',') + '%'; }
  function cambio(s) { return s && s.length > 1 ? (s[s.length - 1][1] / s[0][1] - 1) * 100 : null; }
  function grafico(s, color) {
    var n = s.length, vs = s.map(function (p) { return p[1]; });
    var mn = Math.min.apply(0, vs), mx = Math.max.apply(0, vs), pad = (mx - mn) * .12 || 1;
    mn -= pad; mx += pad;
    var X = function (i) { return i / (n - 1) * W; }, Y = function (v) { return H - (v - mn) / (mx - mn) * H; };
    var d = s.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('');
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="estFg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + color + '" stop-opacity=".26"/><stop offset="1" stop-color="' + color + '" stop-opacity="0"/></linearGradient></defs>' +
      '<line x1="0" x2="' + W + '" y1="' + Y(vs[0]).toFixed(1) + '" y2="' + Y(vs[0]).toFixed(1) + '" stroke="rgba(214,226,244,.28)" stroke-dasharray="3 5" vector-effect="non-scaling-stroke"/>' +
      '<path d="' + d + 'L' + W + ' ' + H + 'L0 ' + H + 'Z" fill="url(#estFg)"/>' +
      '<path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>' +
      '<line class="est-fx__v" x1="0" x2="0" y1="0" y2="' + H + '" stroke="rgba(243,246,251,.4)" vector-effect="non-scaling-stroke" opacity="0"/></svg><span class="est-fx__tip"></span>';
  }
  function eje(s) {
    var out = [];
    for (var k = 0; k < 5; k++) { var p = s[Math.round(k / 4 * (s.length - 1))], d = new Date(p[0] * 1000); out.push('<span>' + MES[d.getMonth()] + ' ' + String(d.getFullYear()).slice(2) + '</span>'); }
    return out.join('');
  }
  function pintarFicha() {
    var lista = DESTACADOS.filter(function (f) { return CAT[f.t] && todos.some(function (d) { return d.t === f.t && !d.soon; }); });
    if (!lista.length) { fx.hidden = true; return; }
    if (cur >= lista.length) cur = 0;
    var f = lista[cur], c = CAT[f.t], d = todos.filter(function (x) { return x.t === f.t; })[0], s = series[f.t];
    var ch = cambio(s), col = ch == null || ch >= 0 ? '#56c793' : '#f07b70';
    fx.hidden = false;
    fx.style.setProperty('--b', f.b);
    var stats = (c.stats || []).slice(0, 3);
    fx.innerHTML = '<div class="est-fx__tabs" role="tablist">' + lista.map(function (g, i) {
      var gd = todos.filter(function (x) { return x.t === g.t; })[0], gs = series[g.t], gc = cambio(gs);
      return '<button type="button" role="tab" aria-selected="' + (i === cur) + '" class="est-fx__tab' + (i === cur ? ' on' : '') + '" data-i="' + i + '"><img src="' + esc(gd.logo) + '" alt=""><span><b>' + esc(corto(gd.n)) + '</b><small>' + g.t + '</small></span>' +
        (gs ? '<span class="px">' + pr(gs[gs.length - 1][1]) + '<span style="color:' + (gc >= 0 ? 'var(--es-up)' : 'var(--es-dn)') + '">' + pct(gc) + '</span></span>' : '') + '</button>';
    }).join('') + '</div>' +
      '<div class="est-fx__body est-fx__sw"><div><div class="est-fx__k">Equity Research · ' + esc(c.q) + '</div><p class="est-fx__tk">' + f.t + '</p><div class="est-fx__name">' + esc(corto(d.n)) + '</div>' +
      (c.tesis ? '<p class="est-fx__h">' + esc(c.tesis) + '</p>' : '') +
      '<div class="est-fx__stats">' + stats.map(function (st) { return '<div><span>' + esc(ETQ[st[0]] || st[0].replace(/\s*TTM$/, '')) + '</span><b class="' + (/^\+/.test(st[1]) ? 'up' : '') + '">' + esc(st[1]) + '</b></div>'; }).join('') + '</div>' +
      '<div class="est-fx__cta"><a class="est-btn" href="' + esc(d.href) + '" target="_blank" rel="noopener">Leer el informe</a><span>' + c.secs + ' secciones · ' + c.ch + ' gráficos</span></div></div>' +
      '<div class="est-fx__chart"><small>Precio · último año</small>' +
      (s ? '<div><span class="est-fx__price">' + pr(s[s.length - 1][1]) + '</span><span class="est-fx__chg ' + (ch >= 0 ? 'up' : 'dn') + '">' + pct(ch) + '</span></div><div class="est-fx__plot">' + grafico(s, col) + '</div><div class="est-fx__x">' + eje(s) + '</div>'
         : '<div class="est-fx__plot"><span class="est-fx__sk">Cargando el precio…</span></div>') + '</div></div>';
    var pl = fx.querySelector('.est-fx__plot');
    if (s && pl) pl.onmousemove = function (e) {
      var r = pl.getBoundingClientRect(), x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), p = s[Math.round(x * (s.length - 1))], dt = new Date(p[0] * 1000);
      var tip = pl.querySelector('.est-fx__tip'); tip.textContent = pr(p[1]) + ' · ' + dt.getDate() + ' ' + MES[dt.getMonth()]; tip.style.left = (x * 100) + '%';
      var v = pl.querySelector('.est-fx__v'); v.setAttribute('x1', x * W); v.setAttribute('x2', x * W); v.setAttribute('opacity', 1);
    };
  }
  fx.addEventListener('click', function (e) { var b = e.target.closest('.est-fx__tab'); if (b) { cur = +b.getAttribute('data-i'); pintarFicha(); } });

  pintar();
  fetch('informes/catalogo.json?d=' + hoyISO(), { signal: AbortSignal.timeout(8000) })
    .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); })
    .then(function (cat) {
      CAT = cat || {};
      pintar(); pintarFicha();
      DESTACADOS.forEach(function (f) {
        fetch(MERCADOS + f.t, { signal: AbortSignal.timeout(8000) })
          .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); })
          .then(function (j) { series[f.t] = (j.points || []).filter(function (p) { return p.c != null; }).map(function (p) { return [p.t, p.c]; }); if (series[f.t].length < 2) delete series[f.t]; pintarFicha(); })
          .catch(function (e) { console.warn('[MI] Informes precio ' + f.t + ':', e.message); });
      });
    })
    .catch(function (e) { console.warn('[MI] Informes catálogo:', e.message); });
})();
