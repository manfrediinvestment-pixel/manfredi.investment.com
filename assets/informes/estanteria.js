/* Pestaña Informes: "el atril y la colección".
   Arriba, el atril: un libro en 3D (tapa Monocromo, lomo del color de su serie, canto de
   páginas) con el nombre, la tesis y tres cifras del informe. Abajo, la colección: todos
   los informes como lomos en un estante, agrupados por sector, cada sector con su color
   de serie. El grosor de cada lomo es el largo real del informe (palabras del catálogo) y
   la altura, la cantidad de gráficos. Tocar un lomo lo lleva al atril.
   Lee las pick-card ocultas de #inversiones (la lista que actualizan las skills de
   informes: un informe nuevo aparece solo, en su sector) e informes/catalogo.json
   (trimestre, secciones, gráficos, palabras, cifras, tesis y fecha; lo regenera
   scripts/catalogo-informes.mjs). */
(function () {
  var root = document.getElementById('est');
  if (!root) return;
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var ORDEN = ['semis', 'software', 'bigtech', 'bancos', 'defensivos', 'argentina'];
  var NOMBRES = { semis: 'Semiconductores', software: 'Software', bigtech: 'Big Tech', bancos: 'Bancos y pagos', defensivos: 'Defensivos', argentina: 'Argentina' };
  // cada sector es una serie de la colección, siempre con colores de la página (escalera de
  // navys, dorado #F2C94C, oro viejo, champagne y el verde #10B981): semis = azul acero;
  // software = azul real; big tech = medianoche; bancos y pagos = verde; defensivos = oro
  // viejo; Argentina = champagne claro (la única serie clara, con letra marino: CLARO).
  // TINTA = el color vivo (puntos, etiquetas); FONDO = el tono del lomo y de la tapa.
  var TINTA = { semis: '#a9c3e6', software: '#7fa6e8', bigtech: '#e6cf96', bancos: '#34d399', defensivos: '#f2c94c', argentina: '#f7dc6f' };
  var FONDO = { semis: '#1a2f4a', software: '#14295e', bigtech: '#0a1222', bancos: '#0c3a2b', defensivos: '#4a3810', argentina: '#d8c493' };
  var CLARO = { argentina: true };
  // informes abiertos a todos (sin _preview-gate.js): llevan el sello verde "Gratis".
  // El primero es el que recibe a la gente en el atril.
  var GRATIS = ['MSFT'];
  var PALABRAS_POR_PAGINA = 450;
  var CORTO_SEC = { semis: 'Semis', software: 'Software', bigtech: 'Big Tech', bancos: 'Bancos', defensivos: 'Defensivos', argentina: 'Argentina' };
  var ETQ = { 'Ingresos TTM': 'Ingresos 12 meses', 'Ingresos FY2026 (TTM)': 'Ingresos 12 meses', 'Var. ingresos (últ. trim.)': 'Crecimiento trim.', 'Margen bruto TTM': 'Margen bruto', 'Margen operativo TTM': 'Margen operativo' };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function corto(n) { return String(n || '').replace(/,? Inc\.?$|,? Inc\.,? | Corporation$| Incorporated$| plc$| N\.V\.$| S\.A\.$| SE$|,? &? ?Co\.?$| Company$| Holdings?$/g, '').replace(/\s*&\s*$/, '').replace(/^The /, '').trim(); }
  // los informes escriben el trimestre de mil formas ("Q3 FY2026", "3Q/FY2026", "2T2026",
  // "3T fiscal 2026", "Q2 y H1 2026"): acá siempre "3T 2026" (o "Año 2026")
  function trimestre(q) {
    q = String(q || '');
    var a = q.match(/20\d\d/), n = q.match(/\b[QT]\s*([1-4])\b|\b([1-4])\s*[QT]/i);
    if (!a) return q.trim();
    return n ? (n[1] || n[2]) + 'T ' + a[0] : 'Año ' + a[0];
  }
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
  var CAT = {}, NUM = {}, sel = null, W = [2000, 14000];

  function numerar() {
    NUM = {};
    var pub = todos.filter(function (d) { return !d.soon && CAT[d.t] && CAT[d.t].f; });
    pub.sort(function (a, b) { return String(CAT[a.t].f).localeCompare(String(CAT[b.t].f)) || a.t.localeCompare(b.t); })
      .forEach(function (d, i) { NUM[d.t] = String(i + 1).padStart(2, '0'); });
    var ws = pub.map(function (d) { return +CAT[d.t].w || 0; }).filter(Boolean);
    if (ws.length) W = [Math.min.apply(0, ws), Math.max.apply(0, ws)];
  }
  function mono(d) { return d.logo ? d.logo.replace(/assets\/logos\/([^\/]+)$/, 'assets/logos/mono/$1') : ''; }
  function vars(d) { return '--acc:' + (TINTA[d.sec] || '#e6cf96') + ';--deep:' + (FONDO[d.sec] || '#0d1a35'); }
  function claro(d) { return CLARO[d.sec] ? ' claro' : ''; }
  function gratis(d) { return GRATIS.indexOf(d.t) >= 0; }
  // largo en páginas, redondeado para abajo de a 5 ("+20 páginas")
  function paginas(w) { var p = Math.round((+w || 0) / PALABRAS_POR_PAGINA); if (!p) return ''; return (p >= 10 ? '+' + Math.floor(p / 5) * 5 : p) + ' páginas'; }
  // medidas del lomo: grosor = largo del informe; altura = cantidad de gráficos
  function grosor(d) { var w = +(CAT[d.t] || {}).w; if (d.soon || !w) return 25; return Math.round(27 + (w - W[0]) / Math.max(1, W[1] - W[0]) * 16); }
  function alto(d) { var ch = +(CAT[d.t] || {}).ch; return d.soon || !ch ? 228 : 236 + Math.min(16, ch) * 3; }

  // tapa "Monocromo": logo en blanco (assets/logos/mono, lo genera scripts/logos-mono.py)
  function cover(d) {
    var c = CAT[d.t] || {};
    var q = d.soon ? 'Próximamente' : esc(trimestre(c.q));
    var der = !d.soon && nuevo(c.f) ? '<em class="est-cover__new">Nuevo</em>' : (NUM[d.t] ? '<span>N° ' + NUM[d.t] + '</span>' : '');
    var m = mono(d);
    return '<span class="est-cover' + claro(d) + '" style="' + vars(d) + '"><i class="est-cover__frame"></i><i class="est-cover__sheen"></i>' +
      '<span class="est-cover__in"><span class="est-cover__top"><span>Manfredi Research</span>' + der + '</span>' +
      '<span class="est-cover__mark">' + (m ? '<img class="est-cover__logo" src="' + esc(m) + '" alt="" onerror="this.style.visibility=\'hidden\'">' : '') + '</span>' +
      '<i class="est-cover__rule"></i><span class="est-cover__tk' + (d.t.length > 4 ? ' largo' : '') + '">' + esc(d.t) + '</span><span class="est-cover__name">' + esc(corto(d.n)) + '</span>' +
      '<span class="est-cover__bot"><b>' + q + '</b><span class="est-cover__sec">' + esc(CORTO_SEC[d.sec] || '') + '</span></span></span></span>';
  }
  // el lomo: mismo dibujo en el estante y en el libro del atril
  function lomoIn(d) {
    var m = mono(d);
    return '<span class="spn__cap">' + (m ? '<img src="' + esc(m) + '" alt="" loading="lazy" onerror="this.remove()">' : '') + '</span>' +
      '<i class="spn__gilt"></i><span class="spn__tk">' + esc(d.t) + '</span><i class="spn__gilt"></i>' +
      '<span class="spn__no">' + (NUM[d.t] || '··') + '</span>';
  }
  function lomo(d, i) {
    var est = 'style="' + vars(d) + ';--w:' + grosor(d) + 'px;--h:' + alto(d) + 'px;--i:' + i + '"';
    var lbl = esc(corto(d.n)) + (d.soon ? ', en preparación: pedilo' : ', ' + esc(trimestre((CAT[d.t] || {}).q)));
    return '<button type="button" class="spn' + claro(d) + (gratis(d) ? ' gratis' : '') + (d.soon ? ' soon' : '') + (sel && sel.t === d.t ? ' on' : '') + (!d.soon && nuevo((CAT[d.t] || {}).f) ? ' nuevo' : '') + '" ' + est + ' data-t="' + esc(d.t) + '"' + (d.soon ? ' data-pedir="' + esc(d.t) + '"' : '') + ' aria-label="' + lbl + '" aria-pressed="' + !!(sel && sel.t === d.t) + '">' + lomoIn(d) + '</button>';
  }
  function ordenar(l) {
    return l.slice().sort(function (a, b) {
      if (a.soon !== b.soon) return a.soon ? 1 : -1;
      return String((CAT[a.t] || {}).f || '').localeCompare(String((CAT[b.t] || {}).f || ''));
    });
  }
  function pintarColeccion() {
    var pub = todos.filter(function (d) { return !d.soon; }).length, i = 0;
    document.getElementById('estCnt').innerHTML = '<b>' + pub + '</b> informes. Cada lomo es uno; el grosor es su largo real.';
    shelves.innerHTML = sectores.map(function (s) {
      var l = ordenar(s.libros), n = l.filter(function (d) { return !d.soon; }).length;
      return '<div class="col-grp" style="--acc:' + (TINTA[s.key] || '#e6cf96') + '"><div class="col-books">' + l.map(function (d) { return lomo(d, i++); }).join('') + '</div>' +
        '<div class="col-lbl"><i></i>' + esc(s.nombre) + '<b>' + n + '</b></div></div>';
    }).join('');
  }

  // 2) el atril
  var lec = document.getElementById('estLec');
  function libro3d(d) {
    return '<div class="bk3" style="' + vars(d) + ';--d:' + Math.round(grosor(d) * 2.3) + 'px">' +
      '<div class="bk3__f">' + cover(d) + '</div>' +
      '<div class="bk3__s spn' + claro(d) + '" style="' + vars(d) + '">' + lomoIn(d) + '</div>' +
      '<div class="bk3__p"></div><div class="bk3__t"></div></div>';
  }
  function pintarAtril(d) {
    var c = CAT[d.t] || {};
    var stats = (c.stats || []).slice(0, 3);
    var meta = [esc(d.t), esc(trimestre(c.q)), NUM[d.t] ? 'N° ' + NUM[d.t] : ''].filter(Boolean).join('<i>·</i>');
    lec.style.cssText = vars(d);
    lec.innerHTML =
      '<div class="lec__stage"><div class="lec__light"></div>' + libro3d(d) + '<div class="lec__floor"></div></div>' +
      '<div class="lec__txt">' +
        '<h2 class="lec__name">' + esc(corto(d.n)) + '</h2>' +
        (gratis(d) ? '<a class="lec__gratis" href="' + esc(d.href) + '" target="_blank" rel="noopener"><i></i>Gratis<span>Leelo completo, sin ser socio</span></a>' : '') +
        '<p class="lec__meta"><span class="lec__sec"><i></i>' + esc(NOMBRES[d.sec] || '') + '</span>' + meta + '</p>' +
        (c.tesis ? '<p class="lec__tesis">' + esc(c.tesis) + '</p>' : '') +
        (stats.length ? '<dl class="lec__stats">' + stats.map(function (st) {
          return '<div><dt>' + esc(ETQ[st[0]] || st[0].replace(/\s*TTM$/, '')) + '</dt><dd class="' + (/^\+/.test(st[1]) ? 'up' : '') + '">' + esc(st[1]) + '</dd></div>';
        }).join('') + '</dl>' : '') +
        '<div class="lec__cta"><a class="lec__btn" href="' + esc(d.href) + '" target="_blank" rel="noopener">' + (gratis(d) ? 'Leer gratis' : 'Leer el informe') + '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>' +
        '<span>' + [c.secs ? c.secs + ' secciones' : '', c.ch ? c.ch + ' gráficos' : '', paginas(c.w), fmtF(c.f)].filter(Boolean).join(' · ') + '</span></div>' +
      '</div>';
  }
  var cambiando = null;
  function elegir(t, scroll) {
    var d = todos.filter(function (x) { return x.t === t && !x.soon; })[0];
    if (!d || (sel && sel.t === t)) return;
    sel = d;
    shelves.querySelectorAll('.spn').forEach(function (b) { var on = b.getAttribute('data-t') === t; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); });
    if (scroll && lec.getBoundingClientRect().top < -80) lec.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    if (reduce || !lec.firstChild) { pintarAtril(d); return; }
    clearTimeout(cambiando);
    lec.classList.add('sale');
    cambiando = setTimeout(function () {
      pintarAtril(d); lec.classList.remove('sale'); lec.classList.add('entra');
      requestAnimationFrame(function () { requestAnimationFrame(function () { lec.classList.remove('entra'); }); });
    }, 380);
  }

  var shelves = document.getElementById('estShelves');
  shelves.addEventListener('click', function (e) {
    var b = e.target.closest('.spn'); if (!b) return;
    if (b.hasAttribute('data-pedir')) { if (typeof miOpenPedirInforme === 'function') miOpenPedirInforme(b.getAttribute('data-pedir')); return; }
    elegir(b.getAttribute('data-t'), true);
  });

  function arrancar() {
    numerar(); var prev = sel; sel = null; pintarColeccion();
    var pub = todos.filter(function (d) { return !d.soon; });
    var ultimo = prev || pub.filter(gratis)[0] || pub.slice().sort(function (a, b) { return String((CAT[b.t] || {}).f || '').localeCompare(String((CAT[a.t] || {}).f || '')); })[0];
    if (ultimo) { sel = ultimo; pintarAtril(ultimo); shelves.querySelectorAll('.spn').forEach(function (b) { var on = b.getAttribute('data-t') === ultimo.t; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); }); }
  }
  arrancar();
  fetch('informes/catalogo.json?d=' + hoyISO(), { signal: AbortSignal.timeout(8000) })
    .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); })
    .then(function (cat) { CAT = cat || {}; sel = null; arrancar(); })
    .catch(function (e) { console.warn('[MI] Informes catálogo:', e.message); });
})();
