/* Asesoría 1 a 1 (#asesoria).
   - Entrada con GSAP + ScrollTrigger (se bajan solo la primera vez que se abre
     la pestaña) y respeta prefers-reduced-motion.
   - Gráfico de fondo del hero y panel "Mi cartera, a la vista": curva real de
     la Cartera Manfredi vs S&P 500 en 2026, con la misma cuenta que Portfolio
     (mfBuildPerformanceSeries). Se usa el retorno real acumulado de la curva,
     no el YTD "proyectado" de Portfolio.
   - Formulario → worker log-user POST /asesoria-consulta (hoja "Asesoria" +
     mail a Ignacio + confirmación al cliente). */
(function () {
  var ENDPOINT = 'https://log-user.nachito2502.workers.dev/asesoria-consulta';
  var GSAP = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js';
  var STJS = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js';
  var MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var NS = 'http://www.w3.org/2000/svg';

  var sec = document.getElementById('asesoria');
  if (!sec) return;
  var $ = function (s, r) { return (r || sec).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || sec).querySelectorAll(s)); };
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Estado "antes de la entrada": se oculta solo si va a haber animación, y si
  // GSAP no llega en 3 s se muestra todo igual.
  if (!calm) {
    sec.classList.add('as-pre');
    setTimeout(function () { if (!window.gsap) sec.classList.remove('as-pre'); }, 3000);
  }

  function load(src) {
    return new Promise(function (ok, ko) { var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
  }
  function fmt(v, d) { return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(d == null ? 1 : d).replace('.', ',') + '%'; }
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function fecha(d) { return d.getDate() + ' ' + MESES[d.getMonth()] + ' 2026'; }

  // Curva suave (Catmull-Rom → Bézier) para el gráfico decorativo del hero.
  function smooth(pts) {
    if (pts.length < 2) return '';
    var d = 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1);
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      d += ' C' + (p1[0] + (p2[0] - p0[0]) / 6).toFixed(1) + ' ' + (p1[1] + (p2[1] - p0[1]) / 6).toFixed(1) + ' ' +
        (p2[0] - (p3[0] - p1[0]) / 6).toFixed(1) + ' ' + (p2[1] - (p3[1] - p1[1]) / 6).toFixed(1) + ' ' + p2[0].toFixed(1) + ' ' + p2[1].toFixed(1);
    }
    return d;
  }

  // ── datos reales: cartera vs S&P 500 desde el inicio de la cartera ──
  var DATA = null, dataP = null, dataDone = false;
  function getData() {
    if (dataP) return dataP;
    dataP = (async function () {
      if (typeof mfBuildPerformanceSeries !== 'function') return null;
      try {
        var n = (typeof mfBizDaysBetween === 'function' && typeof MF_INCEPTION_DATE !== 'undefined') ? Math.max(5, mfBizDaysBetween(MF_INCEPTION_DATE, new Date())) : 100;
        var m = await mfBuildPerformanceSeries(n, n, 'month');
        if (!m || m.dataUnavailable) return null;
        var s = m.portfolioPct.findIndex(function (v) { return v != null; });
        var mine = m.portfolioPct.slice(s), bench = m.benchPct.slice(s), dates = m.dates.slice(s);
        var b0 = bench[0] == null ? 0 : bench[0];
        bench = bench.map(function (v) { return v == null ? null : ((1 + v / 100) / (1 + b0 / 100) - 1) * 100; });
        var rows = [];
        for (var i = 0; i < mine.length; i++) if (mine[i] != null && bench[i] != null && dates[i] instanceof Date) rows.push({ d: dates[i], m: mine[i], s: bench[i] });
        if (rows.length < 5) return null;
        DATA = { rows: rows, mine: rows[rows.length - 1].m, spx: rows[rows.length - 1].s };
        return DATA;
      } catch (e) { console.warn('[asesoria] cartera:', e); return null; }
    })();
    dataP.then(function () { dataDone = true; });
    return dataP;
  }

  // ── gráfico de fondo del hero ──────────────────────────
  var hero = $('.as-hero__chart svg');
  function drawHero(data) {
    var box = hero.getBoundingClientRect(), W = Math.round(box.width), H = Math.round(box.height);
    if (!W || !H) return;
    hero.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    hero.innerHTML = '';
    var small = W < 1000;
    // si todavía no hay datos, una forma neutra que sube
    var vals = data ? data.rows.map(function (r) { return r.m; }) : [0, 1.2, .6, 2.4, 1.8, 3.6, 3.1, 5.2, 4.4, 6.8, 6.1, 8.4, 7.6, 10.2, 9.4, 12.1, 11.8, 14.3];
    // promedio por tramos: ~26 puntos para una línea limpia
    var N = Math.min(26, vals.length), pts = [];
    for (var k = 0; k < N; k++) {
      var a = Math.floor(k * vals.length / N), b = Math.max(a + 1, Math.floor((k + 1) * vals.length / N)), sum = 0;
      for (var j = a; j < b; j++) sum += vals[j];
      pts.push(sum / (b - a));
    }
    pts[pts.length - 1] = vals[vals.length - 1];
    var lo = Math.min.apply(null, pts.concat([0])), hi = Math.max.apply(null, pts);
    // en celular la foto va arriba: el gráfico queda detrás de la foto, lejos del texto
    var x0 = W * (small ? .02 : .43), x1 = W * (small ? .92 : .88), yTop = H * (small ? .07 : .26), yBot = H * (small ? .4 : .84);
    var X = function (i) { return x0 + (x1 - x0) * i / (pts.length - 1); };
    var Y = function (v) { return yBot - (yBot - yTop) * (v - lo) / ((hi - lo) || 1); };
    var P = pts.map(function (v, i) { return [X(i), Y(v)]; });
    var d = smooth(P);

    var defs = el('defs', {}, hero);
    var gs = el('linearGradient', { id: 'hcStroke', x1: '0', y1: '0', x2: '1', y2: '0' }, defs);
    el('stop', { offset: '0', 'stop-color': '#e9d3a0', 'stop-opacity': '0' }, gs);
    el('stop', { offset: '.35', 'stop-color': '#cfae6c', 'stop-opacity': '.55' }, gs);
    el('stop', { offset: '.8', 'stop-color': '#e9d3a0', 'stop-opacity': '1' }, gs);
    el('stop', { offset: '1', 'stop-color': '#fff6de', 'stop-opacity': '1' }, gs);
    var ga = el('linearGradient', { id: 'hcArea', x1: '0', y1: '0', x2: '0', y2: '1' }, defs);
    el('stop', { offset: '0', 'stop-color': '#e9d3a0', 'stop-opacity': '.2' }, ga);
    el('stop', { offset: '1', 'stop-color': '#e9d3a0', 'stop-opacity': '0' }, ga);
    var gm = el('linearGradient', { id: 'hcFadeG', x1: '0', y1: '0', x2: '1', y2: '0' }, defs);
    el('stop', { offset: '0', 'stop-color': '#fff', 'stop-opacity': '0' }, gm);
    el('stop', { offset: '.3', 'stop-color': '#fff', 'stop-opacity': '0' }, gm);
    el('stop', { offset: '.5', 'stop-color': '#fff', 'stop-opacity': '.7' }, gm);
    el('stop', { offset: '1', 'stop-color': '#fff', 'stop-opacity': '1' }, gm);
    var mk = el('mask', { id: 'hcFade' }, defs);
    el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#hcFadeG)' }, mk);
    // el relleno se desvanece en los dos extremos de la curva (sin bordes duros)
    var gA = el('linearGradient', { id: 'hcAreaFadeG', gradientUnits: 'userSpaceOnUse', x1: x0, y1: 0, x2: x1, y2: 0 }, defs);
    el('stop', { offset: '0', 'stop-color': '#fff', 'stop-opacity': '0' }, gA);
    el('stop', { offset: '.35', 'stop-color': '#fff', 'stop-opacity': '1' }, gA);
    el('stop', { offset: '.88', 'stop-color': '#fff', 'stop-opacity': '1' }, gA);
    el('stop', { offset: '1', 'stop-color': '#fff', 'stop-opacity': '0' }, gA);
    var mA = el('mask', { id: 'hcAreaFade' }, defs);
    el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#hcAreaFadeG)' }, mA);

    // grilla con escala real a la derecha y meses abajo
    var g = el('g', { class: 'as-hc-grid', mask: 'url(#hcFade)' }, hero);
    var step = (hi - lo) > 12 ? 5 : (hi - lo) > 5 ? 2.5 : 1;
    for (var t = Math.ceil(lo / step) * step; t <= hi + .001; t += step) {
      var yy = Y(t);
      el('line', { x1: small ? 0 : x0 - 80, x2: W, y1: yy, y2: yy }, g);
      if (!small) el('text', { x: W - 28, y: yy - 6, 'text-anchor': 'end' }, g).textContent = fmt(t, 0);
    }
    if (data && !small) {
      var rows = data.rows, last = -1;
      rows.forEach(function (r, i) {
        if (r.d.getMonth() === last) return; last = r.d.getMonth();
        var xi = x0 + (x1 - x0) * i / (rows.length - 1);
        el('line', { class: 'as-hc-tick', x1: xi, x2: xi, y1: yBot + 18, y2: yBot + 24 }, hero);
        el('text', { x: xi + 6, y: yBot + 25 }, g).textContent = MESES[r.d.getMonth()].toUpperCase();
      });
    }

    el('path', { class: 'as-hc-area', d: d + ' L' + x1.toFixed(1) + ' ' + H + ' L' + x0.toFixed(1) + ' ' + H + ' Z', fill: 'url(#hcArea)', mask: 'url(#hcAreaFade)' }, hero);
    el('path', { class: 'as-hc-line', d: d, stroke: 'url(#hcStroke)', pathLength: 1 }, hero);
    if (!calm) el('path', { class: 'as-hc-glint', d: d, pathLength: 1 }, hero);
    var e = P[P.length - 1], end = el('g', { class: 'as-hc-end' }, hero);
    el('circle', { class: 'as-hc-ring', cx: e[0], cy: e[1], r: 6 }, end);
    el('circle', { class: 'as-hc-ring r2', cx: e[0], cy: e[1], r: 6 }, end);
    el('circle', { class: 'as-hc-dot', cx: e[0], cy: e[1], r: 4.5 }, end);
    if (data && !small) {
      var tag = el('g', { class: 'as-hc-tag', transform: 'translate(' + (e[0] - 58) + ' ' + (e[1] - 46) + ')' }, end);
      el('rect', { width: 116, height: 26, rx: 13 }, tag);
      el('text', { x: 58, y: 17, 'text-anchor': 'middle' }, tag).textContent = '2026 ' + fmt(data.mine);
    }
  }

  // ── panel "Mi cartera, a la vista" ─────────────────────
  var panel = $('[data-as="chart"]'), plot = $('.as-plot svg', panel), tip = $('.as-tip', panel), geo = null;
  function drawPanel(data) {
    // sin datos todavía: solo se marca vacío cuando la carga terminó sin resultado
    if (!data) { if (dataDone) panel.classList.add('is-empty'); return; }
    panel.classList.remove('is-empty');
    var box = plot.getBoundingClientRect(), W = Math.round(box.width), H = Math.round(box.height);
    if (!W || !H) return;
    plot.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    plot.innerHTML = '';
    var rows = data.rows, L = W < 560 ? 44 : 58, R = 16, T = 18, B = 34;
    var d0 = new Date(2026, 0, 1).getTime(), d1 = rows[rows.length - 1].d.getTime();
    var X = function (d) { return L + (W - L - R) * (d - d0) / (d1 - d0); };
    var all = []; rows.forEach(function (r) { all.push(r.m, r.s); }); all.push(0);
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all), span = hi - lo || 1;
    var step = [1, 2, 2.5, 5, 10, 20].find(function (s) { return span / s <= 6; }) || 20;
    lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step;
    var Y = function (v) { return T + (H - T - B) * (hi - v) / (hi - lo); };

    var defs = el('defs', {}, plot);
    var pat = el('pattern', { id: 'asHatch', width: 7, height: 7, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
    el('line', { x1: 0, y1: 0, x2: 0, y2: 7, stroke: 'rgba(233,211,160,.10)', 'stroke-width': 1 }, pat);
    var ga = el('linearGradient', { id: 'asArea', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    el('stop', { offset: 0, 'stop-color': '#e9d3a0', 'stop-opacity': .22 }, ga);
    el('stop', { offset: 1, 'stop-color': '#e9d3a0', 'stop-opacity': 0 }, ga);

    var g = el('g', { class: 'as-pg' }, plot);
    for (var v = lo; v <= hi + .001; v += step) {
      el('line', { class: Math.abs(v) < .001 ? 'z' : '', x1: L, x2: W - R, y1: Y(v), y2: Y(v) }, g);
      el('text', { x: L - 10, y: Y(v) + 4, 'text-anchor': 'end' }, g).textContent = fmt(v, step < 1 ? 1 : 0).replace('+0%', '0%');
    }
    for (var mo = 0; mo <= rows[rows.length - 1].d.getMonth(); mo++) {
      var xm = X(new Date(2026, mo, 1).getTime());
      el('line', { x1: xm, x2: xm, y1: H - B, y2: H - B + 5 }, g);
      if (W >= 560 || mo % 2 === 0) el('text', { class: 'x', x: xm + 4, y: H - 10 }, g).textContent = MESES[mo].toUpperCase();
    }
    // antes del inicio de la cartera: zona rayada y marca
    var xs = X(rows[0].d.getTime());
    el('rect', { x: L, y: T, width: Math.max(0, xs - L), height: H - T - B, fill: 'url(#asHatch)' }, plot);
    var st = el('g', { class: 'as-start' }, plot);
    el('line', { x1: xs, x2: xs, y1: T, y2: H - B }, st);
    if (xs - L > 170) el('text', { x: xs - 8, y: T + 14, 'text-anchor': 'end' }, st).textContent = 'INICIO DE LA CARTERA';

    var path = function (key) { return rows.map(function (r, i) { return (i ? 'L' : 'M') + X(r.d.getTime()).toFixed(1) + ' ' + Y(r[key]).toFixed(1); }).join(' '); };
    var pm = path('m');
    el('path', { d: pm + ' L' + X(d1).toFixed(1) + ' ' + Y(lo).toFixed(1) + ' L' + xs.toFixed(1) + ' ' + Y(lo).toFixed(1) + ' Z', fill: 'url(#asArea)' }, plot);
    el('path', { class: 'as-pl-spx', d: path('s') }, plot);
    el('path', { class: 'as-pl-mine', d: pm }, plot);
    var last = rows[rows.length - 1];
    el('circle', { class: 'as-pl-end', cx: X(d1), cy: Y(last.s), r: 4, fill: '#8fb0e6' }, plot);
    el('circle', { class: 'as-pl-end', cx: X(d1), cy: Y(last.m), r: 5, fill: '#f3e3bd' }, plot);
    var cross = el('g', { class: 'as-cross', visibility: 'hidden' }, plot);
    el('line', { x1: 0, x2: 0, y1: T, y2: H - B }, cross);
    el('circle', { r: 4.5, fill: '#f3e3bd', stroke: '#0a0f1e', 'stroke-width': 2 }, cross);
    el('circle', { r: 4, fill: '#8fb0e6', stroke: '#0a0f1e', 'stroke-width': 2 }, cross);
    geo = { X: X, Y: Y, rows: rows, cross: cross, W: W };
  }
  // tooltip al recorrer la curva
  function hover(ev) {
    if (!geo) return;
    var r = plot.getBoundingClientRect(), x = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left, best = 0, bd = 1e9;
    geo.rows.forEach(function (row, i) { var dx = Math.abs(geo.X(row.d.getTime()) - x); if (dx < bd) { bd = dx; best = i; } });
    var row = geo.rows[best], px = geo.X(row.d.getTime()), c = geo.cross.childNodes;
    geo.cross.setAttribute('visibility', 'visible');
    c[0].setAttribute('x1', px); c[0].setAttribute('x2', px);
    c[1].setAttribute('cx', px); c[1].setAttribute('cy', geo.Y(row.m));
    c[2].setAttribute('cx', px); c[2].setAttribute('cy', geo.Y(row.s));
    tip.hidden = false;
    var half = (tip.offsetWidth || 180) / 2 + 4;
    tip.style.left = Math.min(Math.max(px, half), geo.W - half) + 'px';
    $('[data-tip="d"]', tip).textContent = fecha(row.d);
    $('[data-tip="m"]', tip).textContent = fmt(row.m);
    $('[data-tip="s"]', tip).textContent = fmt(row.s);
  }
  function out() { if (geo) geo.cross.setAttribute('visibility', 'hidden'); tip.hidden = true; }
  var plotBox = $('.as-plot', panel);
  plotBox.addEventListener('pointermove', hover);
  plotBox.addEventListener('pointerleave', out);
  plotBox.addEventListener('pointercancel', out);
  window.addEventListener('scroll', function () { if (!tip.hidden) out(); }, { passive: true });

  function setNums(d, animate) {
    [['mine', d.mine], ['spx', d.spx]].forEach(function (p) {
      $$('[data-as-l="' + p[0] + '"]').forEach(function (e) { e.textContent = fmt(p[1]); });
      var e = $('[data-as-n="' + p[0] + '"]');
      if (!e) return;
      if (!animate || !window.gsap) { e.textContent = fmt(p[1]); return; }
      var o = { v: 0 };
      gsap.to(o, { v: p[1], duration: 1.6, ease: 'expo.out', onUpdate: function () { e.textContent = fmt(o.v); } });
    });
  }

  // ── pasos: el activo se elige con el scroll ─────────────
  var steps = $$('.as-step');
  function setStep(i) { steps.forEach(function (s, k) { s.classList.toggle('is-on', k === i); }); }

  // ── movimiento ─────────────────────────────────────────
  function motion() {
    var gsap = window.gsap, ST = window.ScrollTrigger, ease = 'expo.out';
    gsap.registerPlugin(ST);

    var tl = gsap.timeline({ defaults: { ease: ease } });
    tl.eventCallback('onStart', function () { sec.classList.remove('as-pre'); });
    tl.fromTo('#asesoria .as-hero__chart', { opacity: 0 }, { opacity: 1, duration: 1.2 }, 0)
      .fromTo('#asesoria .as-hc-line', { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 2.6, ease: 'power3.inOut' }, .1)
      .fromTo('#asesoria .as-hc-area', { opacity: 0 }, { opacity: 1, duration: 1.6 }, 1.2)
      .fromTo('#asesoria .as-hc-end', { opacity: 0, scale: .4, transformOrigin: 'center', transformBox: 'fill-box' }, { opacity: 1, scale: 1, duration: .9 }, 2.4)
      .fromTo('#asesoria .as-who__img', { clipPath: 'inset(100% 0 0 0)', scale: 1.06, filter: 'blur(10px)' }, { clipPath: 'inset(0% 0 0 0)', scale: 1, filter: 'blur(0px)', duration: 1.6 }, .1)
      .fromTo('#asesoria .as-who__light', { opacity: 0, scale: .8 }, { opacity: 1, scale: 1, duration: 2 }, .3)
      .fromTo('#asesoria .as-who__ring circle', { strokeDasharray: 1240, strokeDashoffset: 1240 }, { strokeDashoffset: 0, duration: 2.2, ease: 'power3.inOut' }, .2)
      .fromTo('#asesoria .as-ln > span', { y: 0, yPercent: 110 }, { y: 0, yPercent: 0, duration: 1.2, stagger: .12 }, .25)
      .fromTo('#asesoria .as-lead', { opacity: 0, y: 18, filter: 'blur(6px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.1 }, .75)
      .fromTo('#asesoria .as-pts li', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .8, stagger: .08 }, .9)
      .fromTo('#asesoria .as-pts', { opacity: 0 }, { opacity: 1, duration: .01 }, .9)
      .fromTo('#asesoria .as-cta', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 1 }, 1.05)
      .fromTo('#asesoria .as-who__cap', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 1 }, 1.1);

    gsap.to('#asesoria .as-who', { yPercent: -10, ease: 'none', scrollTrigger: { trigger: '#asesoria .as-hero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('#asesoria .as-hero__chart', { yPercent: 12, ease: 'none', scrollTrigger: { trigger: '#asesoria .as-hero', start: 'top top', end: 'bottom top', scrub: true } });

    // cartera: aparece entera de una vez (sin dibujarse con el scroll) y los números cuentan
    gsap.from('#asesoria .as-port .as-h3, #asesoria .as-say', { y: 30, opacity: 0, filter: 'blur(8px)', duration: 1.1, ease: ease, stagger: .1,
      scrollTrigger: { trigger: '#asesoria .as-port', start: 'top 75%' } });
    gsap.from('#asesoria .as-panel', { y: 40, opacity: 0, duration: 1.1, ease: ease, scrollTrigger: { trigger: '#asesoria .as-panel', start: 'top 85%' } });
    ST.create({ trigger: '#asesoria .as-port', start: 'top 70%', once: true, onEnter: function () { getData().then(function (d) { if (d) setNums(d, true); }); } });

    var mm = gsap.matchMedia();
    mm.add('(min-width: 1001px)', function () {
      ST.create({ trigger: '#asesoria .as-proc', start: 'top top', end: '+=' + Math.round(window.innerHeight * 2.4), pin: true, anticipatePin: 1,
        onUpdate: function (self) { setStep(Math.min(3, Math.floor(self.progress * 4))); } });
    });
    mm.add('(max-width: 1000px)', function () {
      steps.forEach(function (s) { s.classList.add('is-on'); gsap.from(s, { y: 40, opacity: 0, duration: 1, ease: ease, scrollTrigger: { trigger: s, start: 'top 85%' } }); });
    });

    gsap.from('#asesoria .as-end__grid > *', { y: 40, opacity: 0, duration: 1.2, ease: ease, stagger: .15, scrollTrigger: { trigger: '#asesoria .as-end', start: 'top 75%' } });
  }

  function staticMode() {
    sec.classList.remove('as-pre');
    if (window.innerWidth > 1000) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) setStep(steps.indexOf(e.target.closest('.as-step'))); });
      }, { rootMargin: '-45% 0px -45% 0px' });
      $$('.as-step__txt').forEach(function (t) { io.observe(t); });
    } else steps.forEach(function (s) { s.classList.add('is-on'); });
    getData().then(function (d) { if (d) setNums(d, false); });
  }

  var started = false;
  function enter() {
    if (sec.classList.contains('tab-hidden')) return;
    if (started) { drawHero(DATA); drawPanel(DATA); if (window.ScrollTrigger) ScrollTrigger.refresh(); return; }
    started = true;
    drawHero(null);
    getData().then(function (d) {
      drawHero(d); drawPanel(d);
      if (d && (calm || !window.gsap)) setNums(d, false);
      if (d && window.gsap && !calm) gsap.fromTo('#asesoria .as-hc-line', { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.8, ease: 'power3.inOut' });
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    });
    if (calm) return staticMode();
    load(GSAP).then(function () { return load(STJS); }).then(motion).catch(staticMode);
  }
  var rT;
  window.addEventListener('resize', function () { clearTimeout(rT); rT = setTimeout(function () { if (started && !sec.classList.contains('tab-hidden')) { drawHero(DATA); drawPanel(DATA); } }, 150); });
  window.addEventListener('hashchange', function () { setTimeout(enter, 30); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { setTimeout(enter, 30); });
  else setTimeout(enter, 30);

  // ── formulario ─────────────────────────────────────────
  var box = $('.as-form'), form = box && box.querySelector('form');
  if (!form) return;
  var msg = box.querySelector('.as-msg'), btn = form.querySelector('button[type="submit"]'), btnTxt = btn.querySelector('span');

  // Si el usuario ya inició sesión, completar nombre y mail.
  form.addEventListener('focusin', function () {
    var u = window._currentUser;
    if (!u) return;
    if (u.displayName && !form.nombre.value) form.nombre.value = u.displayName;
    if (u.email && !form.email.value) form.email.value = u.email;
  }, { once: true });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    msg.textContent = ''; msg.classList.remove('is-err');
    var d = {
      nombre: form.nombre.value.trim(), email: form.email.value.trim(), whatsapp: form.whatsapp.value.trim(),
      experiencia: form.experiencia.value, monto: form.monto.value, objetivo: form.objetivo.value.trim(),
      web: form.web.value // trampa para bots, tiene que llegar vacío
    };
    if (!d.nombre || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email) || !form.ok.checked) {
      msg.textContent = 'Completá tu nombre, un mail válido y aceptá que te contactemos.'; msg.classList.add('is-err'); return;
    }
    btn.disabled = true; btnTxt.textContent = 'Enviando…';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || r.status); }); })
      .then(function () {
        box.classList.add('is-sent');
        var n = box.querySelector('[data-as="nombre"]'); if (n) n.textContent = d.nombre.split(' ')[0];
      })
      .catch(function () {
        msg.textContent = 'No se pudo enviar. Probá de nuevo o escribime a manfredi.investment@gmail.com.'; msg.classList.add('is-err');
      })
      .then(function () { btn.disabled = false; btnTxt.textContent = 'Enviar consulta'; });
  });
})();
