/* Panel de creador → "Análisis por revisar" + "Autores habilitados".
   - Envíos de los autores invitados con la revisión que dejó la skill revisar-analisis
     (veredicto, puntaje, semáforo, datos verificados, mensaje para el autor). Vos decidís:
     Aprobar y publicar · Pedir cambios · Rechazar · Retirar.
   - Autores habilitados: escribís un mail y a esa persona le aparece "Mi espacio de autor".
   De verdad: con la cuenta creadora, todo contra el worker (assets/analistas/api.js).
   Vista de ejemplo en local, sin worker: http://127.0.0.1:8800/?revision=prueba#panel
   (lee revision/prueba/, las acciones no hacen nada). */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var origen = new URLSearchParams(location.search).get('revision');
  var DEMO = LOCAL && !!origen && /^[\w-]+$/.test(origen);
  var API = window.AnApi;
  var BASE = DEMO ? 'revision/' + origen + '/' : '';

  var CAT = { macro: 'Macro', acciones: 'Acciones', bonos: 'Bonos', politica: 'Política', trading: 'Trading' };
  var VER = { publicar: { t: 'Para publicar', c: 'ok' }, cambios: { t: 'Pide cambios', c: 'ojo' }, rechazar: { t: 'No publicar', c: 'mal' } };
  var ESTADO = { recibido: 'pendiente', publicado: 'aprobado', cambios: 'cambios', rechazado: 'rechazado', retirado: 'aprobado' };
  var ORDEN = { mal: 0, ojo: 1, ok: 2 };
  var st = { envios: [], autores: [], tab: 'pendiente', abierto: null, confirmar: null, ocupado: false, editando: null };
  var box = null, boxAut = null;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function json(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(u + ' HTTP ' + r.status); return r.json(); }); }
  function hace(iso) {
    var m = Math.round((Date.now() - new Date(iso)) / 60000);
    return m < 60 ? 'hace ' + Math.max(1, m) + ' min' : m < 1440 ? 'hace ' + Math.round(m / 60) + ' h' : 'hace ' + Math.round(m / 1440) + ' d';
  }
  function aviso(t) {
    var a = document.createElement('div');
    a.className = 'rv-toast'; a.textContent = t;
    document.body.appendChild(a);
    requestAnimationFrame(function () { a.classList.add('on'); });
    setTimeout(function () { a.classList.remove('on'); setTimeout(function () { a.remove(); }, 300); }, 2800);
  }
  function envio(id) { return st.envios.filter(function (x) { return x.id === id; })[0]; }
  var PESO = { publicar: 0, cambios: 1, rechazar: 2 };
  function ordenar(l) {
    return l.sort(function (a, b) {
      var ra = a.revision || {}, rb = b.revision || {};
      return (PESO[ra.veredicto] == null ? 3 : PESO[ra.veredicto]) - (PESO[rb.veredicto] == null ? 3 : PESO[rb.veredicto]) || (rb.puntaje || 0) - (ra.puntaje || 0);
    });
  }

  /* ------------------------------ datos ------------------------------ */
  function cargarDemo() {
    return json(BASE + 'index.json').then(function (ix) {
      return Promise.all(ix.envios.map(function (id) {
        return Promise.all([json(BASE + id + '/envio.json'), json(BASE + id + '/revision.json').catch(function () { return null; })])
          .then(function (r) { var e = r[0]; e.revision = r[1]; e.estado = 'pendiente'; e.tapaUrl = BASE + id + '/' + (e.tapa || 'tapa.jpg'); e.formato = 'pdf'; return e; });
      }));
    }).then(function (l) { st.envios = ordenar(l); });
  }
  function cargarReal() {
    return API.get('/creador/envios').then(function (d) {
      var viejos = {}; st.envios.forEach(function (e) { viejos[e.id] = e; });
      st.envios = ordenar((d.envios || []).map(function (e) {
        var v = viejos[e.id] || {};
        return { id: e.id, titulo: e.titulo, categoria: e.categoria, enviado: e.enviado, formato: e.formato, estadoReal: e.estado, estado: ESTADO[e.estado] || 'pendiente',
          autor: e.autorPerfil || { nombre: e.email, rol: '' }, email: e.email, retiroPedido: e.retiroPedido, reemplaza: e.reemplaza, mensajeEnviado: e.mensaje,
          resumenRev: e.revision || null, revision: v.revision && e.revision && v.revision.revisadoEn === e.revision.revisadoEn ? v.revision : null,
          tapaUrl: v.tapaUrl || '', cuerpo: v.cuerpo };
      }));
    });
  }
  function cargarAutores() { return API.get('/creador/autores').then(function (d) { st.autores = d.autores || []; }); }
  // lo pesado se pide recién al abrir: la revisión completa, el texto, la tapa
  function completar(e) {
    if (DEMO || !e) return Promise.resolve();
    var p = [];
    if (e.resumenRev && !e.revision) p.push(API.get('/creador/envio/' + e.id + '/revision.json').then(function (r) { e.revision = r; }).catch(function () {}));
    if (e.formato === 'texto' && e.cuerpo == null) p.push(API.get('/creador/envio/' + e.id + '/envio.json').then(function (r) { e.cuerpo = r.cuerpo || ''; }).catch(function () {}));
    return Promise.all(p);
  }
  function tapas() {
    if (DEMO) return;
    st.envios.forEach(function (e) {
      if (e.formato !== 'pdf' || e.tapaUrl) return;
      e.tapaUrl = 'pendiente';
      API.get('/creador/envio/' + e.id + '/tapa.jpg', { blob: true }).then(function (b) {
        e.tapaUrl = URL.createObjectURL(b);
        var img = box && box.querySelector('[data-rv-tapa="' + e.id + '"]');
        if (img) img.src = e.tapaUrl;
      }).catch(function () { e.tapaUrl = 'sin'; });
    });
  }

  /* ------------------------------ vista: envíos ------------------------------ */
  function resumen() {
    var p = st.envios.filter(function (e) { return e.estado === 'pendiente'; });
    var n = function (v) { return p.filter(function (e) { var r = e.revision || e.resumenRev; return r && r.veredicto === v; }).length; };
    return '<div class="rv-sum"><span><b>' + p.length + '</b>por revisar</span><span class="ok"><b>' + n('publicar') + '</b>para publicar</span>' +
      '<span class="ojo"><b>' + n('cambios') + '</b>con cambios</span><span class="mal"><b>' + n('rechazar') + '</b>para rechazar</span></div>';
  }
  function tabs() {
    var c = function (s) { return st.envios.filter(function (e) { return e.estado === s; }).length; };
    return '<div class="rv-tabs" role="tablist">' + [['pendiente', 'Por revisar'], ['aprobado', 'Publicados'], ['cambios', 'Cambios pedidos'], ['rechazado', 'Rechazados']].map(function (t) {
      return '<button type="button" role="tab" data-rv-tab="' + t[0] + '" aria-selected="' + (st.tab === t[0]) + '">' + t[1] + '<i>' + c(t[0]) + '</i></button>';
    }).join('') + '</div>';
  }
  function check(c) {
    return '<li class="rv-ck ' + esc(c.estado) + '"><span class="rv-dot"></span><div><b>' + esc(c.titulo) + '</b>' +
      (c.pagina ? '<em>pág. ' + esc(c.pagina) + '</em>' : '') + (c.detalle ? '<p>' + esc(c.detalle) + '</p>' : '') + '</div></li>';
  }
  function nombre(e) { return esc(String(e.autor.nombre || '').split(' ')[0]); }
  function detalle(e) {
    var r = e.revision;
    var izq = !r ? (e.resumenRev ? '<p class="rv-sin">Cargando la revisión…</p>' : '<p class="rv-sin">Todavía no lo revisó la skill. En Claude Code: "revisá los análisis".</p>')
      : (function () {
        var cks = r.checks.slice().sort(function (a, b) { return ORDEN[a.estado] - ORDEN[b.estado]; });
        var malos = cks.filter(function (c) { return c.estado !== 'ok'; }), buenos = cks.filter(function (c) { return c.estado === 'ok'; });
        return '<h5>Controles</h5><ul class="rv-cks">' + malos.map(check).join('') + '</ul>' +
          (buenos.length ? '<details class="rv-oks"' + (malos.length ? '' : ' open') + '><summary>' + buenos.length + (buenos.length === 1 ? ' control en orden' : ' controles en orden') + '</summary><ul class="rv-cks">' + buenos.map(check).join('') + '</ul></details>' : '');
      })();
    if (e.formato === 'texto') izq += '<h5 class="rv-h5">El texto</h5><div class="rv-texto">' + (e.cuerpo == null ? 'Cargando…' : esc(e.cuerpo)) + '</div>';
    var der = (r && r.datos && r.datos.length ? '<h5>Datos verificados</h5><ul class="rv-datos">' + r.datos.map(function (d) {
      var f = /^https?:/.test(d.fuente || '') ? '<a href="' + esc(d.fuente) + '" target="_blank" rel="noopener">fuente</a>' : esc(d.fuente || '');
      return '<li class="' + esc(d.estado) + '"><span class="rv-dot"></span><div><b>' + esc(d.dato) + '</b><p>' + esc(d.nota || '') + (f ? ' · ' + f : '') + '</p></div></li>';
    }).join('') + '</ul>' : '');
    if (e.estado === 'pendiente') der += '<h5>Mensaje para ' + nombre(e) + ' <small>se manda por mail si pedís cambios o rechazás</small></h5>' +
      '<textarea class="rv-msg" rows="9" data-rv-msg="' + esc(e.id) + '" placeholder="Qué tiene que cambiar y por qué.">' + esc(r && r.mensajeAutor || '') + '</textarea>' +
      '<button type="button" class="rv-link" data-rv-copiar="' + esc(e.id) + '">Copiar mensaje</button>';
    else if (e.mensajeEnviado) der += '<h5>Mensaje que le mandaste</h5><div class="rv-texto">' + esc(e.mensajeEnviado) + '</div>';
    if (e.retiroPedido) der += '<p class="rv-ret">' + nombre(e) + ' pidió retirarlo ' + hace(e.retiroPedido) + '.</p>';
    return '<div class="rv-det"><div class="rv-col">' + izq + '</div><div class="rv-col">' + der + '</div></div>';
  }
  function boton(e, accion, texto, cls) {
    var conf = st.confirmar === e.id + ':' + accion;
    return '<button type="button" class="rv-btn' + (cls ? ' ' + cls : '') + (conf ? ' is-conf' : '') + '" data-rv-accion="' + accion + '" data-id="' + esc(e.id) + '"' + (st.ocupado ? ' disabled' : '') + '>' +
      (conf ? 'Tocá de nuevo para confirmar' : texto) + '</button>';
  }
  function acciones(e) {
    var v = e.revision && e.revision.veredicto || e.resumenRev && e.resumenRev.veredicto;
    var ver = '<button type="button" class="rv-btn" data-rv-pdf="' + esc(e.id) + '">' + (e.formato === 'texto' ? 'Ver en la página' : 'Ver PDF') + '</button>';
    if (e.estado === 'pendiente') return '<div class="rv-acc">' + (e.formato === 'pdf' ? ver : '') +
      boton(e, 'rechazar', 'Rechazar', v === 'rechazar' ? 'is-main-mal' : '') + boton(e, 'cambios', 'Pedir cambios', v === 'cambios' ? 'is-main' : '') +
      boton(e, 'aprobar', 'Aprobar y publicar', v === 'publicar' ? 'is-main' : '') + '</div>';
    if (DEMO) return '<div class="rv-acc"><button type="button" class="rv-btn" data-rv-accion="volver" data-id="' + esc(e.id) + '">Volver a por revisar</button></div>';
    if (e.estadoReal === 'publicado') return '<div class="rv-acc">' + (e.formato === 'pdf' ? ver : '') + '<a class="rv-btn" href="#analista-' + esc(e.autor.slug) + '">Ver en la sección</a>' + boton(e, 'retirar', 'Retirar de la sección', e.retiroPedido ? 'is-main-mal' : '') + '</div>';
    return '<div class="rv-acc">' + (e.formato === 'pdf' ? ver : '') + '</div>';
  }
  function item(e) {
    var r = e.revision || e.resumenRev, v = r ? VER[r.veredicto] : null, ab = st.abierto === e.id;
    var tapa = e.formato === 'texto' ? '<span class="rv-tapa rv-tapa--txt"><img src="assets/img/logo-mark-512.png" alt=""></span>'
      : '<span class="rv-tapa"><img data-rv-tapa="' + esc(e.id) + '" src="' + (e.tapaUrl && !/^(pendiente|sin)$/.test(e.tapaUrl) ? esc(e.tapaUrl) : 'assets/img/logo-mark-512.png') + '" alt="" loading="lazy"></span>';
    var extra = e.estadoReal === 'retirado' ? '<span class="rv-pill">Retirado</span>' : e.retiroPedido && e.estadoReal === 'publicado' ? '<span class="rv-pill mal"><span class="rv-dot"></span>Pide retirarlo</span>' : '';
    return '<article class="rv-item' + (ab ? ' on' : '') + '" data-rv="' + esc(e.id) + '">' +
      '<button type="button" class="rv-head" data-rv-abrir="' + esc(e.id) + '" aria-expanded="' + ab + '">' + tapa +
      '<span class="rv-main"><span class="rv-k">' + esc(CAT[e.categoria] || e.categoria) + '<i></i>' + hace(e.enviado) + '<i></i>' + (e.formato === 'texto' ? 'texto' : e.paginas ? esc(e.paginas) + ' pág.' : 'PDF') + (e.reemplaza ? '<i></i>versión corregida' : '') + '</span>' +
      '<span class="rv-t">' + esc(e.titulo) + '</span>' +
      '<span class="rv-a">' + esc(e.autor.nombre) + (e.autor.rol ? ' · ' + esc(e.autor.rol) : '') + '</span>' +
      (r && r.resumen ? '<span class="rv-r">' + esc(r.resumen) + '</span>' : '') + '</span>' +
      '<span class="rv-v">' + extra + (v ? '<span class="rv-pill ' + v.c + '"><span class="rv-dot"></span>' + v.t + '</span><span class="rv-pts"><b>' + esc(r.puntaje) + '</b>/100</span>' : (e.estado === 'pendiente' ? '<span class="rv-pill">Sin revisar</span>' : '')) +
      '<svg class="rv-chev" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8l5 5 5-5"/></svg></span>' +
      '</button>' + (ab ? detalle(e) + acciones(e) : '') + '</article>';
  }
  function pintar() {
    if (!box) return;
    var l = st.envios.filter(function (e) { return e.estado === st.tab; });
    box.innerHTML = '<section class="rv">' +
      '<header class="rv-top"><div><span class="rv-kick">Analistas invitados</span><h3>Análisis por revisar</h3></div>' + resumen() + '</header>' + tabs() +
      (l.length ? '<div class="rv-list">' + l.map(item).join('') + '</div>' : '<p class="rv-vacio">No hay envíos en esta pestaña.</p>') +
      (DEMO ? '<p class="rv-pie">Vista de ejemplo con <code>' + esc(BASE) + '</code>: las acciones no publican ni mandan nada.</p>' : '<p class="rv-pie">Las revisiones las hace la skill revisar-analisis en Claude Code: "revisá los análisis".</p>') +
      '</section>';
    tapas();
  }

  /* ------------------------------ vista: autores ------------------------------ */
  var ORGANISMOS = ['CNV', 'CNMV', 'CMF', 'SMV', 'SEC'];
  function formAutor() {
    var e = st.editando || {}, r = e.registro || null;
    var org = r ? r.organismo : 'CNV', otro = !!r && ORGANISMOS.indexOf(r.organismo) < 0;
    return '<form class="rv-hab" data-rv-hab>' +
      '<label><span>Mail</span><input name="email" type="email" required placeholder="analista@mail.com" autocomplete="off" value="' + esc(e.email || '') + '"' + (e.email ? ' readonly' : '') + '></label>' +
      '<label><span>Nombre</span><input name="nombre" required placeholder="Nombre y apellido" value="' + esc(e.nombre || '') + '"></label>' +
      '<label><span>Cómo se presenta</span><input name="rol" placeholder="Ej.: Economista (UBA) · Renta fija" value="' + esc(e.rol || '') + '"></label>' +
      '<div class="rv-hab__acc">' + (st.editando ? '<button type="button" class="rv-btn" data-rv-cancelar>Cancelar</button>' : '') +
      '<button type="submit" class="rv-btn is-main"' + (st.ocupado ? ' disabled' : '') + '>' + (st.editando ? 'Guardar' : 'Habilitar') + '</button></div>' +
      '<label class="rv-hab__mat"><input type="checkbox" name="asesor"' + (r ? ' checked' : '') + '> <b>Tiene matrícula para asesorar</b> <small>Viste la constancia. Puede incluir recomendaciones si cumple la cláusula 5 de los Términos.</small></label>' +
      '<div class="rv-hab__reg"' + (r ? '' : ' hidden') + '>' +
      '<label><span>Organismo</span><select name="organismo">' + ORGANISMOS.map(function (o) { return '<option' + (o === org ? ' selected' : '') + '>' + o + '</option>'; }).join('') + '<option value="otro"' + (otro ? ' selected' : '') + '>Otro</option></select></label>' +
      '<label' + (otro ? '' : ' hidden') + ' data-rv-otro><span>Cuál</span><input name="organismoOtro" placeholder="Autoridad de su país" value="' + esc(otro ? org : '') + '"></label>' +
      '<label><span>Categoría</span><input name="categoria" placeholder="Ej.: Agente Productor · Asesor de inversiones" value="' + esc(r ? r.categoria : '') + '"></label>' +
      '<label><span>N.º de registro</span><input name="numero" placeholder="Matrícula" value="' + esc(r ? r.numero : '') + '"></label></div>' +
      '</form>';
  }
  function registroTxt(r) { return r ? 'Asesor registrado · ' + r.organismo + (r.categoria ? ' · ' + r.categoria : '') + ' · N.º ' + r.numero : ''; }
  function pintarAutores() {
    if (!boxAut) return;
    var act = st.autores.filter(function (a) { return !a.baja; }), baja = st.autores.filter(function (a) { return a.baja; });
    boxAut.innerHTML = '<section class="rv rv-aut">' +
      '<header class="rv-top"><div><span class="rv-kick">Analistas invitados</span><h3>Autores habilitados</h3></div>' +
      '<div class="rv-sum"><span><b>' + act.length + '</b>habilitados</span><span class="ok"><b>' + act.reduce(function (s, a) { return s + a.publicados; }, 0) + '</b>publicaciones</span></div></header>' +
      formAutor() +
      '<p class="rv-pie rv-pie--top">' + (st.editando ? 'Editando a ' + esc(st.editando.nombre) + '. Los cambios se ven al toque en su perfil.' : 'Le llega un mail de bienvenida y, cuando inicia sesión con ese mail, le aparece "Mi espacio de autor".') + '</p>' +
      (act.length ? '<ul class="rv-auts">' + act.map(function (a) {
        var conf = st.confirmar === 'baja:' + a.email;
        return '<li><span class="an-av sm" style="--c:' + esc(a.color) + '">' + esc(a.nombre.split(' ').map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase()) + '</span>' +
          '<span class="rv-auts__b"><b>' + esc(a.nombre) + '</b><small>' + esc(a.email) + (a.rol ? ' · ' + esc(a.rol) : '') + '</small>' + (a.registro ? '<em class="rv-reg">' + esc(registroTxt(a.registro)) + '</em>' : '') + '</span>' +
          '<span class="rv-auts__n">' + a.envios + ' envíos · ' + a.publicados + ' publicados</span>' +
          '<span class="rv-auts__acc"><button type="button" class="rv-link" data-rv-editar="' + esc(a.email) + '">Editar</button><button type="button" class="rv-link" data-rv-reenviar="' + esc(a.email) + '">Reenviar mail</button>' +
          '<button type="button" class="rv-link rv-link--mal" data-rv-baja="' + esc(a.email) + '">' + (conf ? 'Confirmar' : 'Deshabilitar') + '</button></span></li>';
      }).join('') + '</ul>' : '<p class="rv-vacio">Todavía no habilitaste a nadie.</p>') +
      (baja.length ? '<details class="rv-oks"><summary>' + baja.length + ' deshabilitados</summary><ul class="rv-auts">' + baja.map(function (a) {
        return '<li><span class="rv-auts__b"><b>' + esc(a.nombre) + '</b><small>' + esc(a.email) + '</small></span><span class="rv-auts__acc"><button type="button" class="rv-link" data-rv-rehab="' + esc(a.email) + '" data-nombre="' + esc(a.nombre) + '">Volver a habilitar</button></span></li>';
      }).join('') + '</ul></details>' : '') +
      '</section>';
  }

  /* ------------------------------ acciones ------------------------------ */
  function decidir(e, accion) {
    if (DEMO) {
      e.estado = accion === 'aprobar' ? 'aprobado' : accion === 'cambios' ? 'cambios' : accion === 'rechazar' ? 'rechazado' : 'pendiente';
      st.abierto = null; pintar();
      aviso({ aprobado: 'Aprobado. En prueba: no se publicó nada.', cambios: 'Cambios pedidos. En prueba: no se mandó el mensaje.', rechazado: 'Rechazado. En prueba: no se mandó nada.', pendiente: 'Volvió a por revisar.' }[e.estado]);
      return;
    }
    var ta = box.querySelector('[data-rv-msg="' + e.id + '"]'), mensaje = ta ? ta.value.trim() : '';
    if ((accion === 'cambios' || accion === 'rechazar') && !mensaje) { aviso('Escribí el mensaje para el autor.'); if (ta) ta.focus(); return; }
    st.ocupado = true; pintar();
    API.post('/creador/decision', { id: e.id, accion: accion, mensaje: mensaje }).then(function () {
      st.ocupado = false; st.abierto = null;
      aviso({ aprobar: 'Publicado. Ya se ve en Análisis e informes.', cambios: 'Listo: le mandamos los cambios por mail.', rechazar: 'Listo: le avisamos por mail.', retirar: 'Retirado de la sección.' }[accion]);
      return Promise.all([cargarReal(), cargarAutores()]);
    }).then(function () { pintar(); pintarAutores(); }).catch(function (er) { st.ocupado = false; pintar(); aviso('No se pudo: ' + er.message); });
  }
  function verPdf(e) {
    if (e.formato === 'texto') { location.hash = 'nota-' + e.id; return; }
    var abrir = function (url) {
      if (typeof window.openPdf === 'function') window.openPdf(url, e.titulo, { etiqueta: e.autor.nombre, tapa: e.tapaUrl && !/^(pendiente|sin)$/.test(e.tapaUrl) ? e.tapaUrl : undefined });
      else window.open(url, '_blank', 'noopener');
    };
    if (DEMO) { abrir(BASE + e.id + '/' + (e.archivo || 'analisis.pdf')); return; }
    if (e.estadoReal === 'publicado') { abrir(API.url('/pub/' + e.id + '.pdf')); return; }
    aviso('Abriendo el PDF…');
    API.get('/creador/envio/' + e.id + '/analisis.pdf', { blob: true }).then(function (b) { abrir(URL.createObjectURL(b)); }).catch(function (er) { aviso('No se pudo abrir: ' + er.message); });
  }
  function habilitar(datos, msj) {
    st.ocupado = true; pintarAutores();
    return API.post('/creador/habilitar', datos).then(function () {
      st.ocupado = false; aviso(msj || 'Habilitado. Le mandamos el mail de bienvenida.');
      return cargarAutores();
    }).then(pintarAutores).catch(function (er) { st.ocupado = false; pintarAutores(); aviso('No se pudo: ' + er.message); });
  }

  function eventos() {
    box.addEventListener('click', function (ev) {
      var t = ev.target.closest('[data-rv-tab],[data-rv-abrir],[data-rv-accion],[data-rv-pdf],[data-rv-copiar]');
      if (!t) return;
      if (t.dataset.rvTab) { st.tab = t.dataset.rvTab; st.confirmar = null; pintar(); return; }
      if (t.dataset.rvAbrir) {
        var id = t.dataset.rvAbrir;
        st.abierto = st.abierto === id ? null : id; st.confirmar = null; pintar();
        if (st.abierto) completar(envio(id)).then(function () { if (st.abierto === id) pintar(); });
        return;
      }
      if (t.dataset.rvPdf) { verPdf(envio(t.dataset.rvPdf)); return; }
      if (t.dataset.rvCopiar) {
        var ta = box.querySelector('[data-rv-msg="' + t.dataset.rvCopiar + '"]');
        (navigator.clipboard ? navigator.clipboard.writeText(ta.value) : Promise.reject()).then(function () { aviso('Mensaje copiado'); }, function () { ta.select(); });
        return;
      }
      var e = envio(t.dataset.id), accion = t.dataset.rvAccion;
      if (accion === 'volver') { decidir(e, 'volver'); return; }
      // publicar, rechazar y retirar se confirman con un segundo toque (sin ventanas del navegador)
      var clave = e.id + ':' + accion;
      if (!DEMO && accion !== 'cambios' && st.confirmar !== clave) {
        st.confirmar = clave; pintar();
        setTimeout(function () { if (st.confirmar === clave) { st.confirmar = null; pintar(); } }, 4000);
        return;
      }
      st.confirmar = null;
      decidir(e, accion);
    });
    if (!boxAut) return;
    boxAut.addEventListener('submit', function (ev) {
      var f = ev.target.closest('[data-rv-hab]');
      if (!f) return;
      ev.preventDefault();
      var org = f.organismo.value === 'otro' ? f.organismoOtro.value.trim() : f.organismo.value;
      var datos = { email: f.email.value, nombre: f.nombre.value, rol: f.rol.value };
      if (f.asesor.checked) {
        if (!org || !f.numero.value.trim()) { aviso('Completá el organismo y el número de registro.'); return; }
        datos.registro = { organismo: org, categoria: f.categoria.value, numero: f.numero.value };
      } else datos.registro = null;
      var editando = !!st.editando;
      habilitar(datos, editando ? 'Cambios guardados.' : null).then(function () { if (editando) { st.editando = null; pintarAutores(); } });
    });
    boxAut.addEventListener('change', function (ev) {
      var f = ev.target.form;
      if (!f || !f.hasAttribute('data-rv-hab')) return;
      if (ev.target.name === 'asesor') f.querySelector('.rv-hab__reg').hidden = !ev.target.checked;
      if (ev.target.name === 'organismo') f.querySelector('[data-rv-otro]').hidden = ev.target.value !== 'otro';
    });
    boxAut.addEventListener('click', function (ev) {
      var t = ev.target.closest('[data-rv-baja],[data-rv-reenviar],[data-rv-rehab],[data-rv-editar],[data-rv-cancelar]');
      if (!t) return;
      if (t.hasAttribute('data-rv-cancelar')) { st.editando = null; pintarAutores(); return; }
      if (t.dataset.rvEditar) {
        st.editando = st.autores.filter(function (x) { return x.email === t.dataset.rvEditar; })[0];
        pintarAutores(); boxAut.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
      var a = function (m) { return st.autores.filter(function (x) { return x.email === m; })[0]; };
      if (t.dataset.rvReenviar) { var x = a(t.dataset.rvReenviar); habilitar({ email: x.email, nombre: x.nombre, rol: x.rol, reenviar: true }, 'Mail reenviado.'); return; }
      if (t.dataset.rvRehab) { habilitar({ email: t.dataset.rvRehab, nombre: t.dataset.nombre }, 'Habilitado de nuevo.'); return; }
      var clave = 'baja:' + t.dataset.rvBaja;
      if (st.confirmar !== clave) { st.confirmar = clave; pintarAutores(); setTimeout(function () { if (st.confirmar === clave) { st.confirmar = null; pintarAutores(); } }, 4000); return; }
      st.confirmar = null;
      API.post('/creador/deshabilitar', { email: t.dataset.rvBaja }).then(function () { aviso('Deshabilitado. Sus publicaciones ya no se muestran.'); return cargarAutores(); })
        .then(pintarAutores).catch(function (er) { aviso('No se pudo: ' + er.message); });
    });
  }

  /* ------------------------------ montaje ------------------------------ */
  // va arriba del Panel, fuera de #panelRoot (panel.js lo reescribe entero)
  function contenedores() {
    var root = document.getElementById('panelRoot');
    if (!root) return false;
    var cont = document.getElementById('rvPanel');
    if (!cont) { cont = document.createElement('div'); cont.id = 'rvPanel'; cont.className = 'rv-panel'; root.parentNode.insertBefore(cont, root); }
    cont.innerHTML = '<div id="rvRoot"></div>' + (DEMO ? '' : '<div id="rvAutores"></div>');
    box = document.getElementById('rvRoot'); boxAut = document.getElementById('rvAutores');
    if (DEMO) root.hidden = true; // en la vista de ejemplo no hay sesión: se oculta el aviso de "solo creador"
    return true;
  }
  function montar() {
    if (DEMO) {
      if (location.hash !== '#panel') location.hash = 'panel';
      if (!contenedores()) return;
      box.innerHTML = '<div class="pn-loading">Cargando envíos…</div>';
      eventos();
      cargarDemo().then(function () { st.abierto = st.envios[0] && st.envios[0].id; pintar(); })
        .catch(function (e) { box.innerHTML = '<p class="rv-vacio">No se pudieron leer los envíos: ' + esc(e.message) + '</p>'; });
      return;
    }
    if (!API) return;
    API.yo().then(function (yo) {
      if (!yo.creador || !contenedores()) return;
      box.innerHTML = '<div class="pn-loading">Cargando envíos…</div>';
      eventos();
      Promise.all([cargarReal(), cargarAutores()]).then(function () {
        var p = st.envios.filter(function (e) { return e.estado === 'pendiente'; })[0];
        st.abierto = p ? p.id : null; pintar(); pintarAutores();
        if (p) completar(p).then(pintar);
      }).catch(function (e) { box.innerHTML = '<p class="rv-vacio">No se pudo conectar con el worker de analistas: ' + esc(e.message) + '</p>'; });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', montar); else montar();
})();
