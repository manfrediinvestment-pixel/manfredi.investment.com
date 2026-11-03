/* Pestaña Informes: "biblioteca por sector". Una fila por sector con sus tapas en
   abanico; al tocarla se despliega el estante. Debajo de los libros no hay texto:
   un único renglón muestra el informe que estás mirando (nombre, trimestre y tesis).
   Lee las pick-card ocultas de #inversiones (la lista que actualizan las skills de
   informes: un informe nuevo aparece solo, en su sector) e informes/catalogo.json
   (trimestre, secciones, gráficos, tesis y fecha; lo regenera scripts/catalogo-informes.mjs). */
(function () {
  var root = document.getElementById('est');
  if (!root) return;
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var ORDEN = ['semis', 'software', 'bigtech', 'bancos', 'defensivos', 'argentina'];
  var NOMBRES = { semis: 'Semiconductores', software: 'Software', bigtech: 'Big Tech', bancos: 'Bancos y pagos', defensivos: 'Defensivos', argentina: 'Argentina' };
  // color de cada sector según cómo lo "ve" el mercado: semis = cian eléctrico (silicio);
  // software = violeta (nube, SaaS); big tech = azul (blue chips); bancos y pagos = verde
  // dólar; defensivos = ámbar/oro (refugio, dividendos); Argentina = celeste de la bandera.
  var SECTOR_TINTA = { semis: '#6fd6df', software: '#ad9ff7', bigtech: '#86aef7', bancos: '#78cf9e', defensivos: '#e9b56c', argentina: '#9fd0f2' };
  var CORTO_SEC = { semis: 'Semis', software: 'Software', bigtech: 'Big Tech', bancos: 'Bancos', defensivos: 'Defensivos', argentina: 'Argentina' };
  var ABANICO = 5;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function corto(n) { return String(n || '').replace(/,? Inc\.?$|,? Inc\.,? | Corporation$| Incorporated$| plc$| N\.V\.$| S\.A\.$| SE$|,? Co\.$| Company$| Holdings?$/g, '').replace(/^The /, '').trim(); }
  // los informes escriben el trimestre de mil formas ("Q3 FY2026", "3Q/FY2026", "2T2026",
  // "3T fiscal 2026", "Q2 y H1 2026"): en la estantería siempre "3T 2026" (o "Año 2026")
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
  var CAT = {}, NUM = {}, abierto = null;

  // N° de la colección: orden en que se publicó cada informe (fecha del catálogo)
  function numerar() {
    NUM = {};
    todos.filter(function (d) { return !d.soon && CAT[d.t] && CAT[d.t].f; })
      .sort(function (a, b) { return String(CAT[a.t].f).localeCompare(String(CAT[b.t].f)) || a.t.localeCompare(b.t); })
      .forEach(function (d, i) { NUM[d.t] = String(i + 1).padStart(2, '0'); });
  }
  function mono(d) { return d.logo ? d.logo.replace(/assets\/logos\/([^\/]+)$/, 'assets/logos/mono/$1') : ''; }
  // tapa "Monocromo": logo en blanco (assets/logos/mono, lo genera scripts/logos-mono.py)
  function cover(d) {
    var c = CAT[d.t] || {};
    var q = d.soon ? 'Próximamente' : esc(trimestre(c.q));
    var der = !d.soon && nuevo(c.f) ? '<em class="est-cover__new">Nuevo</em>' : (NUM[d.t] ? '<span>N° ' + NUM[d.t] + '</span>' : '');
    var m = mono(d);
    return '<span class="est-cover" style="--acc:' + (SECTOR_TINTA[d.sec] || '#e6cf96') + '"><i class="est-cover__frame"></i><i class="est-cover__sheen"></i>' +
      '<span class="est-cover__in"><span class="est-cover__top"><span>Manfredi Research</span>' + der + '</span>' +
      '<span class="est-cover__mark">' + (m ? '<img class="est-cover__logo" src="' + esc(m) + '" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">' : '') + '</span>' +
      '<i class="est-cover__rule"></i><span class="est-cover__tk' + (d.t.length > 4 ? ' largo' : '') + '">' + esc(d.t) + '</span><span class="est-cover__name">' + esc(corto(d.n)) + '</span>' +
      '<span class="est-cover__bot"><b>' + q + '</b><span class="est-cover__sec">' + esc(CORTO_SEC[d.sec] || '') + '</span></span></span></span>';
  }
  // tapa en miniatura para el abanico: solo el azul, el filete y el logo
  function mini(d, i) {
    var m = mono(d);
    return '<span class="lib-mini' + (d.soon ? ' soon' : '') + '" style="--i:' + i + '">' + (m ? '<img src="' + esc(m) + '" alt="" loading="lazy" onerror="this.remove()">' : '') + '</span>';
  }
  function ordenar(l) {
    return l.slice().sort(function (a, b) {
      if (a.soon !== b.soon) return a.soon ? 1 : -1;
      return String((CAT[b.t] || {}).f || '').localeCompare(String((CAT[a.t] || {}).f || ''));
    });
  }
  function libro(d, i) {
    var lbl = esc(corto(d.n)) + (d.soon ? ', en preparación' : ', informe ' + esc(trimestre((CAT[d.t] || {}).q)));
    if (d.soon) {
      return '<button type="button" class="lib-book soon" style="--i:' + i + '" data-t="' + esc(d.t) + '" data-pedir="' + esc(d.t) + '" aria-label="' + lbl + '">' + cover(d) + '</button>';
    }
    return '<a class="lib-book" style="--i:' + i + '" data-t="' + esc(d.t) + '" href="' + esc(d.href) + '" target="_blank" rel="noopener" aria-label="' + lbl + '">' + cover(d) + '</a>';
  }
  var FLECHA = function (d) { return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + d + '"/></svg>'; };

  function fila(sec) {
    var l = ordenar(sec.libros), pub = l.filter(function (d) { return !d.soon; }), prep = l.length - pub.length;
    var nuevos = pub.filter(function (d) { return nuevo((CAT[d.t] || {}).f); }).length;
    var id = 'lib-' + sec.key, on = abierto === sec.key;
    return '<section class="lib-row' + (on ? ' on' : '') + '" data-s="' + sec.key + '" style="--acc:' + (SECTOR_TINTA[sec.key] || '#e6cf96') + '">' +
      '<button type="button" class="lib-row__h" aria-expanded="' + on + '" aria-controls="' + id + '">' +
        '<span class="lib-row__name"><i class="lib-dot"></i>' + esc(sec.nombre) + (nuevos ? '<em class="lib-new">' + (nuevos === 1 ? 'Nuevo' : nuevos + ' nuevos') + '</em>' : '') + '</span>' +
        '<span class="lib-fan" aria-hidden="true">' + l.slice(0, ABANICO).map(mini).join('') + '</span>' +
        '<span class="lib-row__n"><b>' + pub.length + '</b> ' + (pub.length === 1 ? 'informe' : 'informes') + (prep ? '<small>+ ' + prep + ' en preparación</small>' : '') + '</span>' +
        '<span class="lib-row__ic" aria-hidden="true">' + FLECHA('M12 5v14M5 12h14') + '</span>' +
      '</button>' +
      '<div class="lib-drawer" id="' + id + '" role="region" aria-label="' + esc(sec.nombre) + '"><div class="lib-drawer__in">' +
        '<div class="lib-shelf"><div class="lib-track">' + l.map(libro).join('') + '</div></div>' +
        '<div class="lib-cap">' +
          '<div class="lib-cap__txt" aria-live="polite"></div>' +
          '<div class="lib-arrows"><button type="button" data-dir="-1" aria-label="Anteriores">' + FLECHA('m15 18-6-6 6-6') + '</button><button type="button" data-dir="1" aria-label="Siguientes">' + FLECHA('m9 18 6-6-6-6') + '</button></div>' +
        '</div>' +
      '</div></div></section>';
  }
  // el único renglón de texto del estante: el informe que estás mirando
  function leyenda(row, t) {
    var d = todos.filter(function (x) { return x.t === t; })[0]; if (!d) return;
    var c = CAT[d.t] || {}, cap = row.querySelector('.lib-cap__txt');
    var meta = d.soon ? 'En preparación · pedilo y lo priorizamos' : [trimestre(c.q), c.secs ? c.secs + ' secciones' : '', c.ch ? c.ch + ' gráficos' : '', fmtF(c.f)].filter(Boolean).join(' · ');
    cap.innerHTML = '<p class="lib-cap__n"><b>' + esc(corto(d.n)) + '</b><span>' + esc(meta) + '</span></p>' +
      (c.tesis && !d.soon ? '<p class="lib-cap__t">' + esc(c.tesis) + '</p>' : '');
    row.querySelectorAll('.lib-book').forEach(function (b) { b.classList.toggle('foco', b.getAttribute('data-t') === t); });
  }
  function flechas(row) {
    var tr = row.querySelector('.lib-track'), a = row.querySelectorAll('.lib-arrows button');
    if (!tr || !a.length) return;
    a[0].disabled = tr.scrollLeft < 8;
    a[1].disabled = tr.scrollLeft + tr.clientWidth >= tr.scrollWidth - 8;
    row.querySelector('.lib-arrows').hidden = tr.scrollWidth <= tr.clientWidth + 8;
  }
  function pintar() {
    var pub = todos.filter(function (d) { return !d.soon; }).length;
    document.getElementById('estCnt').innerHTML = '<b>' + pub + '</b> informes de equity research, cada uno con su valuación propia.';
    shelves.innerHTML = sectores.map(fila).join('');
    shelves.querySelectorAll('.lib-row').forEach(function (row) {
      var first = row.querySelector('.lib-book'); if (first) leyenda(row, first.getAttribute('data-t'));
    });
  }
  function abrir(key) {
    abierto = abierto === key ? null : key;
    shelves.querySelectorAll('.lib-row').forEach(function (row) {
      var on = row.getAttribute('data-s') === abierto;
      row.classList.toggle('on', on);
      row.querySelector('.lib-row__h').setAttribute('aria-expanded', on);
      if (on) { var tr = row.querySelector('.lib-track'); tr.scrollLeft = 0; requestAnimationFrame(function () { flechas(row); }); }
    });
  }

  var shelves = document.getElementById('estShelves');
  shelves.addEventListener('click', function (e) {
    var h = e.target.closest('.lib-row__h');
    if (h) { abrir(h.closest('.lib-row').getAttribute('data-s')); return; }
    var b = e.target.closest('.lib-arrows button');
    if (b) { var tr = b.closest('.lib-row').querySelector('.lib-track'); tr.scrollBy({ left: +b.getAttribute('data-dir') * tr.clientWidth * .8 }); return; }
    var p = e.target.closest('[data-pedir]');
    if (p && typeof miOpenPedirInforme === 'function') miOpenPedirInforme(p.getAttribute('data-pedir'));
  });
  function mirar(e) { var b = e.target.closest && e.target.closest('.lib-book'); if (b) leyenda(b.closest('.lib-row'), b.getAttribute('data-t')); }
  shelves.addEventListener('mouseover', mirar);
  shelves.addEventListener('focusin', mirar);
  shelves.addEventListener('scroll', function (e) { if (e.target.classList && e.target.classList.contains('lib-track')) flechas(e.target.closest('.lib-row')); }, true);
  window.addEventListener('resize', function () { var r = shelves.querySelector('.lib-row.on'); if (r) flechas(r); });

  pintar();
  fetch('informes/catalogo.json?d=' + hoyISO(), { signal: AbortSignal.timeout(8000) })
    .then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); })
    .then(function (cat) { CAT = cat || {}; numerar(); pintar(); var r = shelves.querySelector('.lib-row.on'); if (r) flechas(r); })
    .catch(function (e) { console.warn('[MI] Informes catálogo:', e.message); });
})();
