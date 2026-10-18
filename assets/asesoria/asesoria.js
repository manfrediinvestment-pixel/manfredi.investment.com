/* Asesoría 1 a 1 (#asesoria).
   - Entrada con GSAP + ScrollTrigger (se bajan solo la primera vez que se abre
     la pestaña) y respeta prefers-reduced-motion.
   - "Mi cartera, a la vista": curva real de la Cartera Manfredi vs S&P 500
     desde el 22-may, con la misma cuenta que Portfolio (mfBuildPerformanceSeries).
   - Formulario → worker log-user POST /asesoria-consulta (hoja "Asesoria" +
     mail a Ignacio + confirmación al cliente). */
(function () {
  var ENDPOINT = 'https://log-user.nachito2502.workers.dev/asesoria-consulta';
  var GSAP = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js';
  var ST = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js';

  var sec = document.getElementById('asesoria');
  if (!sec) return;
  var $ = function (s, r) { return (r || sec).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || sec).querySelectorAll(s)); };
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wide = function () { return window.innerWidth > 1000; };

  // Estado "antes de la entrada": se oculta solo si va a haber animación, y si
  // GSAP no llega en 3 s se muestra todo igual.
  if (!calm) {
    sec.classList.add('as-pre');
    setTimeout(function () { if (!window.gsap) sec.classList.remove('as-pre'); }, 3000);
  }

  function load(src) {
    return new Promise(function (ok, ko) {
      var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.head.appendChild(s);
    });
  }
  function fmt(v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1).replace('.', ',') + '%'; }

  // ── pasos: el activo se elige con el scroll ─────────────
  var steps = $$('.as-step');
  function setStep(i) { steps.forEach(function (s, k) { s.classList.toggle('is-on', k === i); }); }

  // ── cartera: datos reales ───────────────────────────────
  var chart = $('[data-as="chart"]'), chartData = null;
  async function buildChart() {
    if (typeof mfBuildPerformanceSeries !== 'function') { chart.classList.add('is-empty'); return null; }
    try {
      var n = (typeof mfBizDaysBetween === 'function' && typeof MF_INCEPTION_DATE !== 'undefined') ? Math.max(5, mfBizDaysBetween(MF_INCEPTION_DATE, new Date())) : 100;
      var m = await mfBuildPerformanceSeries(n, n, 'month');
      if (!m || m.dataUnavailable) throw new Error('sin datos');
      var start = m.portfolioPct.findIndex(function (v) { return v != null; });
      var mine = m.portfolioPct.slice(start), bench = m.benchPct.slice(start);
      var b0 = bench[0] == null ? 0 : bench[0];
      bench = bench.map(function (v) { return v == null ? null : ((1 + v / 100) / (1 + b0 / 100) - 1) * 100; });
      var all = mine.concat(bench).filter(function (v) { return v != null; }).concat([0]);
      var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all), pad = (hi - lo) * .12 || 1;
      lo -= pad; hi += pad;
      var W = 1000, H = 380, N = mine.length - 1 || 1;
      var X = function (i) { return (i / N) * W; }, Y = function (v) { return H - ((v - lo) / (hi - lo)) * H; };
      var line = function (arr) {
        var d = '', on = false;
        arr.forEach(function (v, i) { if (v == null) { on = false; return; } d += (on ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1) + ' '; on = true; });
        return d.trim();
      };
      $('.as-chart__mine', chart).setAttribute('d', line(mine));
      $('.as-chart__spx', chart).setAttribute('d', line(bench));
      $('.as-chart__area', chart).setAttribute('d', line(mine) + ' L' + W + ' ' + H + ' L0 ' + H + ' Z');
      var g = $('.as-chart__grid', chart), step = (hi - lo) / 4, html = '';
      for (var k = 1; k < 4; k++) { var yy = Y(lo + step * k).toFixed(1); html += '<line x1="0" x2="' + W + '" y1="' + yy + '" y2="' + yy + '"/>'; }
      html += '<line class="is-zero" x1="0" x2="' + W + '" y1="' + Y(0).toFixed(1) + '" y2="' + Y(0).toFixed(1) + '"/>';
      g.innerHTML = html;
      var lastB = bench.filter(function (v) { return v != null; }).pop() || 0;
      var mineEnd = typeof m.totalReturn === 'number' ? m.totalReturn : mine[mine.length - 1];
      var tm = $('[data-as-tag="mine"]', chart), tb = $('[data-as-tag="spx"]', chart);
      tm.style.top = (Y(mine[mine.length - 1]) / H * 100) + '%';
      tb.style.top = (Y(lastB) / H * 100) + '%';
      // si las etiquetas se pisan, se separan
      var dy = parseFloat(tb.style.top) - parseFloat(tm.style.top);
      if (Math.abs(dy) < 9) { var mid = (parseFloat(tb.style.top) + parseFloat(tm.style.top)) / 2, s = dy >= 0 ? 1 : -1; tm.style.top = (mid - 5 * s) + '%'; tb.style.top = (mid + 5 * s) + '%'; }
      tm.textContent = 'Mi cartera ' + fmt(mineEnd);
      tb.textContent = 'S&P 500 ' + fmt(lastB);
      var d0 = m.dates && m.dates[start];
      if (d0 instanceof Date && typeof MF_MONTHS !== 'undefined') $('[data-as="d0"]', chart).textContent = d0.getDate() + ' ' + MF_MONTHS[d0.getMonth()];
      return { mine: mineEnd, spx: lastB };
    } catch (e) {
      console.warn('[asesoria] cartera:', e);
      chart.classList.add('is-empty');
      return null;
    }
  }
  function setNums(d, animate) {
    [['mine', d.mine], ['spx', d.spx]].forEach(function (p) {
      var el = $('[data-as-n="' + p[0] + '"]');
      if (!el) return;
      if (!animate || !window.gsap) { el.textContent = fmt(p[1]); return; }
      var o = { v: 0 };
      gsap.to(o, { v: p[1], duration: 1.8, ease: 'expo.out', onUpdate: function () { el.textContent = fmt(o.v); } });
    });
  }

  // ── movimiento ─────────────────────────────────────────
  function motion() {
    var gsap = window.gsap, ST = window.ScrollTrigger;
    gsap.registerPlugin(ST);
    var ease = 'expo.out';

    // entrada del hero: foto que sube desde abajo, título línea por línea
    var tl = gsap.timeline({ defaults: { ease: ease } });
    tl.fromTo('#asesoria .as-hero__trace', { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: 2.6, ease: 'power2.inOut' }, 0)
      .fromTo('#asesoria .as-who__img', { clipPath: 'inset(100% 0 0 0)', scale: 1.06, filter: 'blur(10px)' }, { clipPath: 'inset(0% 0 0 0)', scale: 1, filter: 'blur(0px)', duration: 1.6 }, .1)
      .fromTo('#asesoria .as-who__light', { opacity: 0, scale: .8 }, { opacity: 1, scale: 1, duration: 2 }, .3)
      .fromTo('#asesoria .as-who__ring circle', { strokeDasharray: 1240, strokeDashoffset: 1240 }, { strokeDashoffset: 0, duration: 2.2, ease: 'power3.inOut' }, .2)
      .fromTo('#asesoria .as-ln > span', { y: 0, yPercent: 110 }, { y: 0, yPercent: 0, duration: 1.2, stagger: .12 }, .25)
      .fromTo('#asesoria .as-lead', { opacity: 0, y: 18, filter: 'blur(6px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.1 }, .75)
      .fromTo('#asesoria .as-cta', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 1 }, .95)
      .fromTo('#asesoria .as-who__cap', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 1 }, 1.1);
    tl.eventCallback('onStart', function () { sec.classList.remove('as-pre'); });

    // el hero se va con un leve parallax
    gsap.to('#asesoria .as-who', { yPercent: -10, ease: 'none', scrollTrigger: { trigger: '#asesoria .as-hero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('#asesoria .as-hero__copy', { yPercent: -16, opacity: .2, ease: 'none', scrollTrigger: { trigger: '#asesoria .as-hero', start: 'top top', end: 'bottom top', scrub: true } });

    // cartera: el título entra, la curva se dibuja con el scroll y los números cuentan
    gsap.from('#asesoria .as-port .as-h3, #asesoria .as-say', { y: 30, opacity: 0, filter: 'blur(8px)', duration: 1.2, ease: ease, stagger: .12,
      scrollTrigger: { trigger: '#asesoria .as-port', start: 'top 75%' } });
    gsap.fromTo('#asesoria .as-chart svg', { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', ease: 'none',
      scrollTrigger: { trigger: '#asesoria .as-chart', start: 'top 80%', end: 'bottom 55%', scrub: .6 } });
    gsap.from('#asesoria .as-tag', { opacity: 0, x: -10, duration: .8, ease: ease, stagger: .1,
      scrollTrigger: { trigger: '#asesoria .as-chart', start: 'bottom 60%' } });
    ST.create({ trigger: '#asesoria .as-port', start: 'top 60%', once: true, onEnter: function () {
      (chartData ? Promise.resolve(chartData) : buildChart()).then(function (d) { if (d) setNums(d, true); });
    } });

    // cómo trabajamos: en escritorio la sección queda fija y los pasos avanzan
    var mm = gsap.matchMedia();
    mm.add('(min-width: 1001px)', function () {
        ST.create({ trigger: '#asesoria .as-proc', start: 'top top', end: '+=' + Math.round(window.innerHeight * 2.4), pin: true, anticipatePin: 1,
          onUpdate: function (self) { setStep(Math.min(3, Math.floor(self.progress * 4))); } });
    });
    mm.add('(max-width: 1000px)', function () {
        steps.forEach(function (s) {
          gsap.from(s, { y: 40, opacity: 0, duration: 1, ease: ease, scrollTrigger: { trigger: s, start: 'top 85%' } });
        });
        setStep(-1); steps.forEach(function (s) { s.classList.add('is-on'); });
    });

    // cierre
    gsap.from('#asesoria .as-end__grid > *', { y: 40, opacity: 0, duration: 1.2, ease: ease, stagger: .15,
      scrollTrigger: { trigger: '#asesoria .as-end', start: 'top 75%' } });
  }

  function staticMode() {
    sec.classList.remove('as-pre');
    if (wide()) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) setStep(steps.indexOf(e.target.closest('.as-step'))); });
      }, { rootMargin: '-45% 0px -45% 0px' });
      $$('.as-step__txt').forEach(function (t) { io.observe(t); });
    } else steps.forEach(function (s) { s.classList.add('is-on'); });
    buildChart().then(function (d) { if (d) setNums(d, false); });
  }

  var started = false;
  function enter() {
    if (sec.classList.contains('tab-hidden')) return;
    if (started) { if (window.ScrollTrigger) ScrollTrigger.refresh(); return; }
    started = true;
    buildChart().then(function (d) { chartData = d; if (d && (calm || !window.gsap)) setNums(d, false); if (window.ScrollTrigger) ScrollTrigger.refresh(); });
    if (calm) return staticMode();
    load(GSAP).then(function () { return load(ST); }).then(motion).catch(staticMode);
  }
  window.addEventListener('hashchange', function () { setTimeout(enter, 30); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { setTimeout(enter, 30); });
  else setTimeout(enter, 30);

  // ── formulario ─────────────────────────────────────────
  var box = $('.as-form'), form = box && box.querySelector('form');
  if (!form) return;
  var msg = box.querySelector('.as-msg'), btn = form.querySelector('button[type="submit"]');

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
    if (!d.nombre || !d.email || !form.ok.checked) {
      msg.textContent = 'Completá nombre, mail y aceptá que te contactemos.'; msg.classList.add('is-err'); return;
    }
    btn.disabled = true; btn.textContent = 'Enviando…';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || r.status); }); })
      .then(function () {
        box.classList.add('is-sent');
        var n = box.querySelector('[data-as="nombre"]'); if (n) n.textContent = d.nombre.split(' ')[0];
      })
      .catch(function () {
        msg.textContent = 'No se pudo enviar. Probá de nuevo o escribime a manfredi.investment@gmail.com.'; msg.classList.add('is-err');
      })
      .then(function () { btn.disabled = false; btn.textContent = 'Enviar consulta'; });
  });
})();
