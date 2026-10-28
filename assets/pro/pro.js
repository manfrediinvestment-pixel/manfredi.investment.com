/* Manfredi Pro (pestaña "inversiones", hash #pro / #inversiones).
   Dos vistas dentro de la misma sección:
   - La mesa (#pro): las ideas de Ignacio con entrada, objetivo, invalidación y perfil,
     seguimientos, cierres con resultado, encuesta semanal y preguntas de los socios.
     Socios: el feed completo. Visitantes: historial público (sin activos) + vista borrosa.
   - Informes (#inversiones): la estantería de informes de siempre.
   Por ahora la mesa se ve solo en local con datos de ejemplo (data/pro-ejemplo.json):
     http://127.0.0.1:8800/#pro            → como visitante
     http://127.0.0.1:8800/?pro=socio#pro  → como socio
   Los precios actuales salen en vivo del worker de Mercados. */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var qs = new URLSearchParams(location.search);
  var MERCADOS = 'https://manfredi-mercados.nachito2502.workers.dev/mercados';
  var PERFILES = ['Conservador', 'Moderado-Conservador', 'Moderado', 'Moderado-Agresivo', 'Agresivo'];
  var sec = document.getElementById('inversiones'), root = document.getElementById('proMesa');
  if (!sec || !root) return;

  var st = { data: null, precios: {}, seguidas: leer('pro-seguidas', {}), voto: leer('pro-voto', null), abiertos: {} };

  function leer(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function socio() { return (LOCAL && qs.get('pro') === 'socio') || !!(window._miIsMember && window._miIsMember()); }
  function fecha(iso, largo) {
    var d = new Date(iso.length === 10 ? iso + 'T12:00:00-03:00' : iso);
    return d.toLocaleDateString('es-AR', largo ? { day: 'numeric', month: 'long' } : { day: '2-digit', month: 'short' }).replace(/\./g, '').replace(/ de /g, ' ');
  }
  function dias(a, b) { return Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 864e5); }
  function precio(v, m) {
    var ars = m === 'ARS';
    return (ars ? '$ ' : 'US$ ') + v.toLocaleString('es-AR', { minimumFractionDigits: ars || v >= 1000 ? 0 : 2, maximumFractionDigits: ars || v >= 1000 ? 0 : 2 });
  }
  function pct(x, signo) { return (signo && x > 0 ? '+' : '') + x.toFixed(1).replace('.', ',') + '%'; }
  function idea(id) { return st.data.ideas.filter(function (i) { return i.id === id; })[0]; }
  function actual(i) { var p = st.precios[i.cat + ':' + i.symbol]; return p != null ? p : null; }
  function resultado(i) {
    if (i.cierre) return (i.cierre.precio / i.entrada - 1) * 100;
    var a = actual(i); return a == null ? null : (a / i.entrada - 1) * 100;
  }
  function aviso(t) {
    var a = document.createElement('div'); a.className = 'rv-toast'; a.textContent = t; document.body.appendChild(a);
    requestAnimationFrame(function () { a.classList.add('on'); });
    setTimeout(function () { a.classList.remove('on'); setTimeout(function () { a.remove(); }, 300); }, 2600);
  }

  /* ------------------------------ datos ------------------------------ */
  function cargar() {
    if (!LOCAL) return Promise.resolve(null); // la mesa real llega con el alta en la CNV
    return fetch('data/pro-ejemplo.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      st.data = d;
      if (!d) return;
      return fetch(MERCADOS).then(function (r) { return r.json(); }).then(function (m) {
        Object.keys(m.categorias || {}).forEach(function (c) { (m.categorias[c].items || []).forEach(function (it) { st.precios[c + ':' + it.symbol] = it.price; }); });
      }).catch(function () {});
    });
  }
  function historial() {
    var cerradas = st.data.ideas.filter(function (i) { return i.cierre; });
    var r = cerradas.map(resultado), gan = r.filter(function (x) { return x > 0; }).length;
    var prom = r.length ? r.reduce(function (s, x) { return s + x; }, 0) / r.length : 0;
    var vsRef = cerradas.length ? cerradas.reduce(function (s, i) { return s + (resultado(i) - i.cierre.ref.v); }, 0) / cerradas.length : 0;
    return { total: st.data.ideas.length, abiertas: st.data.ideas.length - cerradas.length, cerradas: cerradas.length, aciertos: cerradas.length ? gan / cerradas.length * 100 : 0, prom: prom, vsRef: vsRef };
  }

  /* ------------------------------ piezas ------------------------------ */
  function perfilUsuario() { var p = window._qzLastProfile; return p && p.tier != null ? +p.tier : null; }
  function encaje(i) {
    var u = perfilUsuario();
    if (u == null) return '<span class="pro-fit"><button type="button" class="pro-a" onclick="openQuiz()">Hacé el test</button> para ver si encaja con tu perfil</span>';
    if (i.perfil > u) return '<span class="pro-fit ojo"><i></i>Más riesgo que tu perfil (' + esc(PERFILES[u]) + ')</span>';
    return '<span class="pro-fit ok"><i></i>Encaja con tu perfil (' + esc(PERFILES[u]) + ')</span>';
  }
  // barra: invalidación ── entrada ── objetivo, con el precio de hoy
  function recorrido(i) {
    var a = i.cierre ? i.cierre.precio : actual(i), lo = Math.min(i.invalidacion, a == null ? i.invalidacion : a), hi = Math.max(i.objetivo, a == null ? i.objetivo : a);
    var X = function (v) { return ((v - lo) / (hi - lo || 1) * 100).toFixed(1) + '%'; };
    var r = resultado(i), cls = r == null ? '' : r >= 0 ? 'up' : 'dn';
    return '<div class="pro-run">' +
      '<div class="pro-run__bar"><i class="pro-run__fill ' + cls + '" style="left:' + X(Math.min(i.entrada, a == null ? i.entrada : a)) + ';right:calc(100% - ' + X(Math.max(i.entrada, a == null ? i.entrada : a)) + ')"></i>' +
      '<b class="pro-run__m stop" style="left:' + X(i.invalidacion) + '"></b><b class="pro-run__m in" style="left:' + X(i.entrada) + '"></b><b class="pro-run__m obj" style="left:' + X(i.objetivo) + '"></b>' +
      (a != null ? '<em class="pro-run__now ' + cls + '" style="left:' + X(a) + '"><span>' + (i.cierre ? 'Cierre' : 'Hoy') + ' ' + precio(a, i.moneda) + '</span></em>' : '') + '</div>' +
      '<div class="pro-run__l"><span>Invalidación<b>' + precio(i.invalidacion, i.moneda) + '</b></span>' +
      '<span class="pro-run__in" style="left:' + Math.min(80, Math.max(20, parseFloat(X(i.entrada)))).toFixed(1) + '%">Entrada<b>' + precio(i.entrada, i.moneda) + '</b></span>' +
      '<span>Objetivo<b>' + precio(i.objetivo, i.moneda) + '</b></span></div></div>';
  }
  function cabezaIdea(i) {
    var r = resultado(i);
    return '<div class="pro-idea__h"><span class="pro-tk">' + esc(i.symbol.replace(/C$|D$/, '')) + '</span><div><b>' + esc(i.nombre) + '</b><small>' + esc(i.horizonte) + ' · perfil ' + esc(PERFILES[i.perfil]) + '</small></div>' +
      (r != null ? '<span class="pro-res ' + (r >= 0 ? 'up' : 'dn') + '">' + pct(r, true) + '<small>' + (i.cierre ? 'resultado' : 'desde la entrada') + '</small></span>' : '') + '</div>';
  }
  function cuerpo(t) { return String(t || '').split(/\n{2,}/).map(function (p) { return '<p>' + esc(p) + '</p>'; }).join(''); }
  function seguir(i) {
    var on = !!st.seguidas[i.id];
    return '<button type="button" class="pro-seg' + (on ? ' on' : '') + '" data-pro-seguir="' + esc(i.id) + '" aria-pressed="' + on + '">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0"/></svg>' + (on ? 'Siguiendo' : 'Seguir idea') + '</button>';
  }
  var TIPO = { idea: 'Idea nueva', seguimiento: 'Seguimiento', cierre: 'Cierre', nota: 'Nota' };
  function post(p) {
    var i = p.idea ? idea(p.idea) : null, r = i ? resultado(i) : null;
    var k = '<span class="pro-k pro-k--' + p.tipo + '"><i></i>' + TIPO[p.tipo] + '<em>' + fecha(p.fecha) + '</em></span>';
    var h = '<article class="pro-post pro-post--' + p.tipo + '" id="' + esc(p.id) + '">' + k;
    if (p.tipo === 'idea') h += '<h3 class="pro-t">' + esc(i.titulo) + '</h3>' + cabezaIdea(i) + recorrido(i) + '<div class="pro-body">' + cuerpo(p.cuerpo) + '</div>' + '<div class="pro-meta">' + encaje(i) + '</div>';
    else if (p.tipo === 'cierre') h += '<h3 class="pro-t">' + esc(p.titulo) + '</h3>' +
      '<div class="pro-close"><span class="pro-res big ' + (r >= 0 ? 'up' : 'dn') + '">' + pct(r, true) + '</span><span>' + esc(i.nombre) + '<small>' + esc(i.cierre.motivo) + ' · ' + dias(i.fecha, i.cierre.fecha) + ' días</small></span>' +
      '<span class="pro-close__ref">' + esc(i.cierre.ref.nombre) + ' en el mismo período<b>' + pct(i.cierre.ref.v, true) + '</b></span></div>' + '<div class="pro-body">' + cuerpo(p.cuerpo) + '</div>';
    else if (p.tipo === 'seguimiento') h += '<h3 class="pro-t">' + esc(p.titulo) + '</h3><a class="pro-ref" href="#post-idea-' + esc(i.id) + '" data-pro-ir="' + esc(i.id) + '">' + esc(i.nombre) + ' · ' + (r != null ? pct(r, true) + ' desde la entrada' : '') + '</a>' + '<div class="pro-body">' + cuerpo(p.cuerpo) + '</div>';
    else h += '<h3 class="pro-t">' + esc(p.titulo) + '</h3><div class="pro-body">' + cuerpo(p.cuerpo) + '</div>';
    h += '<div class="pro-acc">' + (window.AnSocial ? window.AnSocial.barra('pro-' + p.id) : '') + (i && !i.cierre ? seguir(i) : '') + '</div>';
    return h + '</article>';
  }

  /* ------------------------------ columna derecha ------------------------------ */
  function railAbiertas() {
    var ab = st.data.ideas.filter(function (i) { return !i.cierre; });
    return '<div class="pro-card"><h4>Ideas abiertas</h4><ul class="pro-open">' + ab.map(function (i) {
      var r = resultado(i), a = actual(i), falta = a != null ? (i.objetivo / a - 1) * 100 : null;
      return '<li><button type="button" data-pro-ir="' + esc(i.id) + '"><span class="pro-tk sm">' + esc(i.symbol.replace(/C$|D$/, '')) + '</span>' +
        '<span><b>' + esc(i.nombre) + '</b><small>' + (falta != null ? pct(falta) + ' al objetivo' : '') + '</small></span>' +
        '<em class="' + (r >= 0 ? 'up' : 'dn') + '">' + (r != null ? pct(r, true) : '—') + '</em></button></li>';
    }).join('') + '</ul></div>';
  }
  function railHistorial(h) {
    return '<div class="pro-card"><h4>Historial</h4><div class="pro-stats">' +
      '<span><b>' + h.cerradas + '</b>ideas cerradas</span><span><b>' + Math.round(h.aciertos) + '%</b>con ganancia</span>' +
      '<span><b class="' + (h.prom >= 0 ? 'up' : 'dn') + '">' + pct(h.prom, true) + '</b>resultado promedio</span><span><b class="' + (h.vsRef >= 0 ? 'up' : 'dn') + '">' + pct(h.vsRef, true) + '</b>contra su índice</span></div></div>';
  }
  function railEncuesta() {
    var e = st.data.encuesta, tot = e.opciones.reduce(function (s, o) { return s + o.v; }, 0) + (st.voto != null ? 1 : 0);
    return '<div class="pro-card"><h4>Encuesta de la semana</h4><p class="pro-q">' + esc(e.pregunta) + '</p><div class="pro-poll' + (st.voto != null ? ' votada' : '') + '">' + e.opciones.map(function (o, k) {
      var v = o.v + (st.voto === k ? 1 : 0), w = (v / tot * 100);
      return '<button type="button" data-pro-voto="' + k + '"' + (st.voto != null ? ' disabled' : '') + ' class="' + (st.voto === k ? 'mio' : '') + '"><i style="width:' + (st.voto != null ? w.toFixed(1) : 0) + '%"></i><span>' + esc(o.t) + '</span>' + (st.voto != null ? '<b>' + Math.round(w) + '%</b>' : '') + '</button>';
    }).join('') + '</div><small class="pro-help">' + (st.voto != null ? tot + ' votos · cierra el viernes' : 'Elegí una: el más votado es el informe de la semana') + '</small></div>';
  }
  function railPreguntas() {
    return '<div class="pro-card"><h4>Preguntale a Ignacio</h4>' +
      '<form class="pro-ask" data-pro-preguntar><textarea rows="2" maxlength="400" placeholder="Tu pregunta sobre las ideas o el mercado" aria-label="Tu pregunta"></textarea><button type="submit" class="pro-btn">Enviar</button></form>' +
      '<ul class="pro-qa">' + st.data.preguntas.map(function (x) { return '<li><b>' + esc(x.q) + '</b><p>' + esc(x.a) + '</p><small>Respondida el ' + fecha(x.fecha) + '</small></li>'; }).join('') + '</ul></div>';
  }

  /* ------------------------------ vistas ------------------------------ */
  function cabeza(h) {
    var a = st.data.autor;
    return '<header class="pro-hero"><img src="' + esc(a.foto) + '" alt="" class="pro-av"><div><span class="pro-kick">Manfredi Pro · La mesa</span>' +
      '<h2 class="pro-h">Mis ideas de inversión, con entrada, objetivo y salida.</h2><p class="pro-by">' + esc(a.nombre) + ' · ' + esc(a.titulo) + '</p></div>' +
      '<div class="pro-hstats"><span><b>' + h.abiertas + '</b>abiertas</span><span><b>' + h.cerradas + '</b>cerradas</span><span><b class="' + (h.vsRef >= 0 ? 'up' : 'dn') + '">' + pct(h.vsRef, true) + '</b>vs su índice</span></div></header>';
  }
  function vistaSocio() {
    var h = historial();
    return cabeza(h) + '<div class="pro-grid"><div class="pro-feed">' + st.data.posts.map(post).join('') +
      '<p class="pro-disc">Las ideas son informes generales de análisis: no consideran tu situación particular. Cada una indica el perfil para el que fue pensada; antes de operar, mirá si encaja con el tuyo.</p></div>' +
      '<aside class="pro-rail">' + railAbiertas() + railHistorial(h) + railEncuesta() + railPreguntas() + '</aside></div>';
  }
  function vistaVisitante() {
    var h = historial();
    var muestra = st.data.posts.slice(0, 3).map(post).join('');
    return '<section class="pro-land">' + cabeza(h) +
      '<div class="pro-land__grid">' +
      '<div class="pro-land__lock"><div class="pro-land__bg" aria-hidden="true">' + muestra + '</div>' +
      '<div class="pro-land__card"><span class="pro-kick">Solo socios Pro</span><h3>Cada idea, con su plan completo.</h3>' +
      '<ul class="pro-inc"><li><b>La mesa</b>Ideas con entrada, objetivo, invalidación y el perfil para el que fueron pensadas. Seguimientos y cierres con resultado.</li>' +
      '<li><b>Avisos</b>Te llega un mail cuando hay una idea nueva o cambia algo de las que seguís.</li>' +
      '<li><b>Informes</b>El research completo de cada empresa, con valuación y escenarios.</li>' +
      '<li><b>Warren</b>Tu analista con IA, para preguntar lo que quieras.</li></ul>' +
      '<button type="button" class="an-gold pro-cta" onclick="if(typeof openPaymentModal===\'function\')openPaymentModal()">Sumarme a Manfredi Pro</button>' +
      '<small class="pro-help">USD 10 por mes hasta el 31 de octubre · cancelás cuando quieras</small></div></div>' +
      '<aside class="pro-rail">' + railHistorial(h) + '<div class="pro-card"><h4>Cómo se arma una idea</h4><ol class="pro-how"><li><b>Tesis</b>Por qué, en dos párrafos.</li><li><b>Niveles</b>Entrada, objetivo e invalidación.</li><li><b>Perfil</b>Para quién es y para quién no.</li><li><b>Cierre</b>Con resultado, gane o pierda.</li></ol></div></aside>' +
      '</div></section>';
  }
  function vistaPronto() {
    return '<section class="pro-soon"><span class="pro-kick">Manfredi Pro · La mesa</span><h2 class="pro-h">Muy pronto.</h2><p class="pro-by">Mis ideas de inversión con entrada, objetivo y salida, para socios Pro.</p>' +
      '<a class="pro-a" href="#inversiones">Mientras tanto, mirá los informes</a></section>';
  }
  function pintar() {
    // La pestaña es el Chat (assets/comunidad/chat.js): Mercados gratis + Manfredi Pro.
    if (window.ProChat) return window.ProChat.montar(root);
    root.innerHTML = !st.data ? vistaPronto() : socio() ? vistaSocio() : vistaVisitante();
    if (window.AnSocial && st.data && socio()) window.AnSocial.montar(st.data.posts.map(function (p) { return 'pro-' + p.id; }));
  }

  /* ------------------------------ sub-pestañas ------------------------------ */
  var nav = document.getElementById('proNav');
  var HASH = { mesa: '#pro', informes: '#inversiones', warren: '#pro-warren' };
  function vista() { var h = (location.hash || '').replace('#', ''); return h === 'pro' ? 'mesa' : h === 'pro-warren' ? 'warren' : 'informes'; }

  // Warren en grande: el mismo panel del chat flotante se muda adentro de la sección
  // (conserva conversación e historial) y vuelve a su lugar al salir.
  var wHogar = null;
  function warrenAdentro(on) {
    var panel = document.getElementById('warrenPanel'), caja = document.getElementById('proWarren');
    if (!panel || !caja) return;
    document.body.classList.toggle('pro-warren-on', on);
    if (on) {
      if (!wHogar) wHogar = { padre: panel.parentNode, sig: panel.nextSibling };
      if (panel.parentNode !== caja) caja.appendChild(panel);
      panel.classList.add('is-embedded');
      if (typeof warrenOpen !== 'undefined' && !warrenOpen && typeof window.toggleWarren === 'function') window.toggleWarren();
    } else if (wHogar && panel.parentNode === caja) {
      panel.classList.remove('is-embedded');
      if (typeof window.closeWarren === 'function') window.closeWarren();
      wHogar.padre.insertBefore(panel, wHogar.sig);
    }
  }
  function mostrar() {
    var v = vista(), enPro = !sec.classList.contains('tab-hidden');
    sec.classList.toggle('pro-v-mesa', v === 'mesa');
    sec.classList.toggle('pro-v-informes', v === 'informes');
    sec.classList.toggle('pro-v-warren', v === 'warren');
    warrenAdentro(v === 'warren' && enPro);
    if (nav) nav.querySelectorAll('[data-pro-tab]').forEach(function (b) { b.setAttribute('aria-selected', b.dataset.proTab === v); });
  }
  if (nav) nav.addEventListener('click', function (e) {
    var b = e.target.closest('[data-pro-tab]');
    if (!b) return;
    var h = HASH[b.dataset.proTab];
    if (location.hash !== h) history.replaceState(null, '', h);
    mostrar(); window.scrollTo({ top: 0 });
  });
  // el router del sitio cambia de pestaña después del hashchange: esperamos un cuadro
  window.addEventListener('hashchange', function () { requestAnimationFrame(mostrar); });

  root.addEventListener('click', function (e) {
    var t = e.target.closest('[data-pro-seguir],[data-pro-voto],[data-pro-ir]');
    if (!t) return;
    if (t.dataset.proSeguir) {
      var id = t.dataset.proSeguir, i = idea(id);
      st.seguidas[id] = !st.seguidas[id]; guardar('pro-seguidas', st.seguidas); pintar();
      aviso(st.seguidas[id] ? 'Te avisamos por mail cuando haya novedades de ' + i.nombre + '.' : 'Dejaste de seguir ' + i.nombre + '.');
      return;
    }
    if (t.dataset.proVoto != null) { st.voto = +t.dataset.proVoto; guardar('pro-voto', st.voto); pintar(); aviso('Voto registrado.'); return; }
    if (t.dataset.proIr) {
      e.preventDefault();
      var p = st.data.posts.filter(function (x) { return x.tipo === 'idea' && x.idea === t.dataset.proIr; })[0];
      var el = p && document.getElementById(p.id);
      if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash'); }
    }
  });
  root.addEventListener('submit', function (e) {
    var f = e.target.closest('[data-pro-preguntar]');
    if (!f) return;
    e.preventDefault();
    var ta = f.querySelector('textarea');
    if (!ta.value.trim()) return;
    ta.value = ''; aviso('Pregunta enviada. Las respuestas salen los viernes.');
  });

  mostrar();
  cargar().then(pintar).catch(function (e) { console.warn('[pro]', e.message); pintar(); });
  // si cambia la sesión (o la membresía) se vuelve a pintar
  var ultimo = null;
  setInterval(function () { var s = socio(); if (s !== ultimo) { ultimo = s; pintar(); } }, 1500);
})();
