/* Panel de creador → "Análisis por revisar".
   Muestra cada envío de un autor invitado con la revisión que dejó la skill
   revisar-analisis (.claude/skills/revisar-analisis): veredicto, puntaje, semáforo de
   controles, datos verificados y el mensaje listo para el autor. El creador solo decide.
   - Por ahora funciona en local: http://127.0.0.1:8800/?revision=prueba#panel lee
     revision/prueba/index.json (sin iniciar sesión). Las acciones no publican nada.
   - Cuando exista el portal de carga (worker + R2) los envíos van a venir del worker. */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var origen = new URLSearchParams(location.search).get('revision');
  if (!LOCAL || !origen || !/^[\w-]+$/.test(origen)) return;
  var BASE = 'revision/' + origen + '/';

  var CAT = { macro: 'Macro', acciones: 'Acciones', bonos: 'Bonos', politica: 'Política', trading: 'Trading' };
  var VER = {
    publicar: { t: 'Para publicar', c: 'ok' },
    cambios: { t: 'Pide cambios', c: 'ojo' },
    rechazar: { t: 'No publicar', c: 'mal' }
  };
  var ORDEN = { mal: 0, ojo: 1, ok: 2 };
  var st = { envios: [], tab: 'pendiente', abierto: null };

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function json(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(u + ' HTTP ' + r.status); return r.json(); }); }
  function hace(iso) {
    var m = Math.round((Date.now() - new Date(iso)) / 60000);
    return m < 60 ? 'hace ' + Math.max(1, m) + ' min' : m < 1440 ? 'hace ' + Math.round(m / 60) + ' h' : 'hace ' + Math.round(m / 1440) + ' d';
  }
  function cargar() {
    return json(BASE + 'index.json').then(function (ix) {
      return Promise.all(ix.envios.map(function (id) {
        return Promise.all([json(BASE + id + '/envio.json'), json(BASE + id + '/revision.json').catch(function () { return null; })])
          .then(function (r) { var e = r[0]; e.revision = r[1]; e.estado = 'pendiente'; return e; });
      }));
    }).then(function (l) {
      // primero lo que está para publicar, después cambios, al final rechazos; dentro, por puntaje
      var peso = { publicar: 0, cambios: 1, rechazar: 2 };
      l.sort(function (a, b) {
        var ra = a.revision || {}, rb = b.revision || {};
        return (peso[ra.veredicto] == null ? 3 : peso[ra.veredicto]) - (peso[rb.veredicto] == null ? 3 : peso[rb.veredicto]) || (rb.puntaje || 0) - (ra.puntaje || 0);
      });
      st.envios = l;
    });
  }

  /* ------------------------------ vista ------------------------------ */
  function resumen() {
    var p = st.envios.filter(function (e) { return e.estado === 'pendiente'; });
    var n = function (v) { return p.filter(function (e) { return e.revision && e.revision.veredicto === v; }).length; };
    return '<div class="rv-sum">' +
      '<span><b>' + p.length + '</b>por revisar</span>' +
      '<span class="ok"><b>' + n('publicar') + '</b>para publicar</span>' +
      '<span class="ojo"><b>' + n('cambios') + '</b>con cambios</span>' +
      '<span class="mal"><b>' + n('rechazar') + '</b>para rechazar</span></div>';
  }
  function tabs() {
    var c = function (s) { return st.envios.filter(function (e) { return e.estado === s; }).length; };
    return '<div class="rv-tabs" role="tablist">' + [['pendiente', 'Por revisar'], ['aprobado', 'Aprobados'], ['cambios', 'Cambios pedidos'], ['rechazado', 'Rechazados']].map(function (t) {
      return '<button type="button" role="tab" data-rv-tab="' + t[0] + '" aria-selected="' + (st.tab === t[0]) + '">' + t[1] + '<i>' + c(t[0]) + '</i></button>';
    }).join('') + '</div>';
  }
  function check(c) {
    return '<li class="rv-ck ' + esc(c.estado) + '"><span class="rv-dot"></span><div><b>' + esc(c.titulo) + '</b>' +
      (c.pagina ? '<em>pág. ' + esc(c.pagina) + '</em>' : '') + (c.detalle ? '<p>' + esc(c.detalle) + '</p>' : '') + '</div></li>';
  }
  function detalle(e) {
    var r = e.revision;
    if (!r) return '<div class="rv-det"><p class="rv-sin">Todavía no lo revisó la skill. En Claude Code: "revisá los análisis".</p></div>';
    var cks = r.checks.slice().sort(function (a, b) { return ORDEN[a.estado] - ORDEN[b.estado]; });
    var malos = cks.filter(function (c) { return c.estado !== 'ok'; }), buenos = cks.filter(function (c) { return c.estado === 'ok'; });
    return '<div class="rv-det">' +
      '<div class="rv-col"><h5>Controles</h5><ul class="rv-cks">' + malos.map(check).join('') + '</ul>' +
      (buenos.length ? '<details class="rv-oks"' + (malos.length ? '' : ' open') + '><summary>' + buenos.length + (buenos.length === 1 ? ' control en orden' : ' controles en orden') + '</summary><ul class="rv-cks">' + buenos.map(check).join('') + '</ul></details>' : '') + '</div>' +
      '<div class="rv-col">' +
      (r.datos && r.datos.length ? '<h5>Datos verificados</h5><ul class="rv-datos">' + r.datos.map(function (d) {
        var f = /^https?:/.test(d.fuente || '') ? '<a href="' + esc(d.fuente) + '" target="_blank" rel="noopener">fuente</a>' : esc(d.fuente || '');
        return '<li class="' + esc(d.estado) + '"><span class="rv-dot"></span><div><b>' + esc(d.dato) + '</b><p>' + esc(d.nota || '') + (f ? ' · ' + f : '') + '</p></div></li>';
      }).join('') + '</ul>' : '') +
      (r.mensajeAutor ? '<h5>Mensaje para ' + esc(e.autor.nombre.split(' ')[0]) + '</h5><textarea class="rv-msg" rows="9" data-rv-msg="' + esc(e.id) + '">' + esc(r.mensajeAutor) + '</textarea>' +
        '<button type="button" class="rv-link" data-rv-copiar="' + esc(e.id) + '">Copiar mensaje</button>' : '') +
      '</div></div>';
  }
  function acciones(e) {
    var v = e.revision && e.revision.veredicto;
    if (e.estado !== 'pendiente') return '<div class="rv-acc"><button type="button" class="rv-btn" data-rv-accion="pendiente" data-id="' + esc(e.id) + '">Volver a por revisar</button></div>';
    return '<div class="rv-acc">' +
      '<button type="button" class="rv-btn" data-rv-pdf="' + esc(e.id) + '">Ver PDF</button>' +
      '<button type="button" class="rv-btn' + (v === 'rechazar' ? ' is-main-mal' : '') + '" data-rv-accion="rechazado" data-id="' + esc(e.id) + '">Rechazar</button>' +
      '<button type="button" class="rv-btn' + (v === 'cambios' ? ' is-main' : '') + '" data-rv-accion="cambios" data-id="' + esc(e.id) + '">Pedir cambios</button>' +
      '<button type="button" class="rv-btn' + (v === 'publicar' ? ' is-main' : '') + '" data-rv-accion="aprobado" data-id="' + esc(e.id) + '">Aprobar y publicar</button></div>';
  }
  function item(e) {
    var r = e.revision, v = r ? VER[r.veredicto] : null, ab = st.abierto === e.id;
    return '<article class="rv-item' + (ab ? ' on' : '') + '" data-rv="' + esc(e.id) + '">' +
      '<button type="button" class="rv-head" data-rv-abrir="' + esc(e.id) + '" aria-expanded="' + ab + '">' +
      '<span class="rv-tapa"><img src="' + esc(BASE + e.id + '/' + (e.tapa || 'tapa.jpg')) + '" alt="" loading="lazy"></span>' +
      '<span class="rv-main"><span class="rv-k">' + esc(CAT[e.categoria] || e.categoria) + '<i></i>' + hace(e.enviado) + '<i></i>' + esc(e.paginas || '') + ' pág.</span>' +
      '<span class="rv-t">' + esc(e.titulo) + '</span>' +
      '<span class="rv-a">' + esc(e.autor.nombre) + ' · ' + esc(e.autor.rol || '') + '</span>' +
      (r ? '<span class="rv-r">' + esc(r.resumen) + '</span>' : '') + '</span>' +
      '<span class="rv-v">' + (v ? '<span class="rv-pill ' + v.c + '"><span class="rv-dot"></span>' + v.t + '</span><span class="rv-pts"><b>' + esc(r.puntaje) + '</b>/100</span>' : '<span class="rv-pill">Sin revisar</span>') +
      '<svg class="rv-chev" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8l5 5 5-5"/></svg></span>' +
      '</button>' +
      (ab ? detalle(e) + acciones(e) : '') + '</article>';
  }
  function pintar(box) {
    var l = st.envios.filter(function (e) { return e.estado === st.tab; });
    box.innerHTML = '<section class="rv">' +
      '<header class="rv-top"><div><span class="rv-kick">Analistas invitados</span><h3>Análisis por revisar</h3></div>' + resumen() + '</header>' +
      tabs() +
      (l.length ? '<div class="rv-list">' + l.map(item).join('') + '</div>' : '<p class="rv-vacio">No hay envíos en esta pestaña.</p>') +
      '<p class="rv-pie">Revisión hecha por la skill revisar-analisis · vista de prueba con <code>' + esc(BASE) + '</code>: las acciones no publican ni mandan nada.</p>' +
      '</section>';
  }
  function aviso(t) {
    var a = document.createElement('div');
    a.className = 'rv-toast'; a.textContent = t;
    document.body.appendChild(a);
    requestAnimationFrame(function () { a.classList.add('on'); });
    setTimeout(function () { a.classList.remove('on'); setTimeout(function () { a.remove(); }, 300); }, 2600);
  }

  /* ------------------------------ montaje ------------------------------ */
  function montar() {
    var root = document.getElementById('panelRoot');
    if (!root) return;
    if (location.hash !== '#panel') location.hash = 'panel';
    var box = document.createElement('div');
    box.id = 'rvRoot';
    root.innerHTML = '';
    root.appendChild(box);
    box.innerHTML = '<div class="pn-loading">Cargando envíos…</div>';
    cargar().then(function () { st.abierto = st.envios[0] && st.envios[0].id; pintar(box); })
      .catch(function (e) { box.innerHTML = '<p class="rv-vacio">No se pudieron leer los envíos: ' + esc(e.message) + '</p>'; });

    box.addEventListener('click', function (ev) {
      var t = ev.target.closest('[data-rv-tab],[data-rv-abrir],[data-rv-accion],[data-rv-pdf],[data-rv-copiar]');
      if (!t) return;
      if (t.dataset.rvTab) { st.tab = t.dataset.rvTab; pintar(box); return; }
      if (t.dataset.rvAbrir) { st.abierto = st.abierto === t.dataset.rvAbrir ? null : t.dataset.rvAbrir; pintar(box); return; }
      if (t.dataset.rvPdf) {
        var e = st.envios.filter(function (x) { return x.id === t.dataset.rvPdf; })[0], url = BASE + e.id + '/' + (e.archivo || 'analisis.pdf');
        if (typeof window.openPdf === 'function') window.openPdf(url, e.titulo, { etiqueta: e.autor.nombre, tapa: BASE + e.id + '/' + (e.tapa || 'tapa.jpg') });
        else window.open(url, '_blank', 'noopener');
        return;
      }
      if (t.dataset.rvCopiar) {
        var ta = box.querySelector('[data-rv-msg="' + t.dataset.rvCopiar + '"]');
        (navigator.clipboard ? navigator.clipboard.writeText(ta.value) : Promise.reject()).then(function () { aviso('Mensaje copiado'); }, function () { ta.select(); });
        return;
      }
      var en = st.envios.filter(function (x) { return x.id === t.dataset.id; })[0];
      en.estado = t.dataset.rvAccion;
      st.abierto = null;
      pintar(box);
      aviso({ aprobado: 'Aprobado. En prueba: no se publicó nada.', cambios: 'Cambios pedidos. En prueba: no se mandó el mensaje.', rechazado: 'Rechazado. En prueba: no se mandó nada.', pendiente: 'Volvió a por revisar.' }[en.estado]);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', montar); else montar();
})();
