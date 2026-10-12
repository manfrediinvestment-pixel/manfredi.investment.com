/* Noticias → Análisis e informes → "Mi espacio de autor" (#autor).
   Solo para autores habilitados: el creador habilita su mail y, cuando inician sesión,
   les aparece el botón "Mi espacio de autor" junto a las sub-pestañas.
   Tres partes: Subir análisis (PDF o texto) · Mis envíos (estado de cada uno) · Mi perfil.
   - De verdad: la habilitación, los envíos y el perfil salen del worker (assets/analistas/api.js).
   - Vista de ejemplo en local, sin worker: http://127.0.0.1:8800/?autor=martin-bustos#autor
     (usa data/analistas-ejemplo.json y no envía nada). */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var qs = new URLSearchParams(location.search);
  var slug = qs.get('autor');
  var DEMO = LOCAL && !!slug && /^[\w-]+$/.test(slug);
  var API = window.AnApi;
  if (!DEMO && !API) return;

  var CATS = [['acciones', 'Acciones'], ['bonos', 'Bonos'], ['macro', 'Macro'], ['politica', 'Política'], ['trading', 'Trading']];
  var CATN = {}; CATS.forEach(function (c) { CATN[c[0]] = c[1]; });
  var MAX_MB = 20, MAX_RES = 180, MAX_TIT = 90;
  var st = { autor: null, envios: [], tab: 'subir', formato: 'pdf', archivo: null, tapa: '', paginas: 0, abierto: null, reemplaza: null, enviando: false };

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function json(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(u + ' HTTP ' + r.status); return r.json(); }); }
  function fecha(iso) { return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short' }).replace(/\./g, '').replace(/ de /g, ' '); }
  function iniciales(n) { return n.split(' ').map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase(); }
  function aviso(t) {
    var a = document.createElement('div');
    a.className = 'rv-toast'; a.textContent = t;
    document.body.appendChild(a);
    requestAnimationFrame(function () { a.classList.add('on'); });
    setTimeout(function () { a.classList.remove('on'); setTimeout(function () { a.remove(); }, 300); }, 2800);
  }

  /* ------------------------------ datos ------------------------------ */
  function cargar() { return DEMO ? cargarDemo() : cargarReal(); }
  function cargarReal() {
    return API.yo().then(function (yo) {
      if (!yo.habilitado) throw new Error('no habilitado');
      st.autor = yo.autor;
      return cargarEnvios();
    });
  }
  function cargarEnvios() {
    if (DEMO) return Promise.resolve();
    return API.get('/mis-envios').then(function (d) {
      st.envios = (d.envios || []).map(function (e) {
        return { id: e.id, titulo: e.titulo, categoria: e.categoria, estado: e.estado, enviado: e.enviado, revisado: e.revisado, publicado: e.publicado,
          mensaje: e.mensaje, retiroPedido: e.retiroPedido, formato: e.formato, tapa: e.estado === 'publicado' && e.formato === 'pdf' ? API.url('/pub/' + e.id + '.jpg') : '' };
      });
      if (!st.abierto && st.envios[0]) st.abierto = st.envios[0].id;
    });
  }
  function cargarDemo() {
    return Promise.all([
      json('data/analistas-ejemplo.json'),
      json('revision/prueba/prueba-bustos-ggal/revision.json').catch(function () { return null; })
    ]).then(function (r) {
      var d = r[0], rev = r[1];
      st.autor = (d.autores || []).filter(function (a) { return a.slug === slug; })[0];
      if (!st.autor) throw new Error('No hay un autor de ejemplo "' + slug + '"');
      // lo que ya tiene publicado
      st.envios = (d.publicaciones || []).filter(function (p) { return p.autor === slug; }).map(function (p) {
        return { id: p.id, titulo: p.titulo, categoria: p.categoria, estado: 'publicado', enviado: p.fecha, publicado: p.fecha, tapa: p.tapa || '', lecturas: p.lecturas || 0, texto: !!p.cuerpo };
      });
      // y un envío con cambios pedidos (sale de la revisión de prueba de la skill)
      if (rev && rev.mensajeAutor) st.envios.unshift({
        id: 'prueba-bustos-ggal', titulo: 'GGAL: vuelve el crédito, vuelve la mora', categoria: 'acciones', estado: 'cambios',
        enviado: '2026-10-11T18:40:00-03:00', revisado: rev.revisadoEn, tapa: 'revision/prueba/prueba-bustos-ggal/tapa.jpg', mensaje: rev.mensajeAutor
      });
      st.abierto = st.envios[0] && st.envios[0].id;
    });
  }

  /* ------------------------------ vista ------------------------------ */
  function av(a, cls) {
    return '<span class="an-av' + (cls ? ' ' + cls : '') + '" style="--c:' + esc(a.color) + '">' + (a.foto ? '<img src="' + esc(a.foto) + '" alt="">' : esc(iniciales(a.nombre))) + '</span>';
  }
  function cabeza() {
    var a = st.autor, pend = st.envios.filter(function (e) { return e.estado === 'cambios'; }).length;
    var nPub = st.envios.filter(function (e) { return e.estado === 'publicado'; }).length;
    return '<a class="an-back" href="#analisis">← Análisis e informes</a>' +
      '<header class="au-head">' + av(a, 'lg') +
      '<div><span class="au-k">Mi espacio de autor</span><h3 class="au-t">Hola, ' + esc(a.nombre.split(' ')[0]) + '.</h3>' +
      '<p class="au-s">' + esc(a.rol || '') + '<i></i><a href="#analista-' + esc(a.slug) + '">Ver mi perfil público</a></p></div>' +
      '<div class="au-stats"><span><strong>' + nPub + '</strong>' + (nPub === 1 ? 'publicado' : 'publicados') + '</span>' +
      '<span><strong>' + st.envios.filter(function (e) { return e.estado !== 'publicado'; }).length + '</strong>en curso</span></div></header>' +
      '<div class="au-tabs" role="tablist">' + [['subir', 'Subir análisis', ''], ['envios', 'Mis envíos', pend ? '<i class="au-badge">' + pend + '</i>' : ''], ['perfil', 'Mi perfil', '']].map(function (t) {
        return '<button type="button" role="tab" data-au-tab="' + t[0] + '" aria-selected="' + (st.tab === t[0]) + '">' + t[1] + t[2] + '</button>';
      }).join('') + '</div>';
  }

  // ---------- subir ----------
  function subir() {
    var pdf = st.formato === 'pdf';
    var corr = st.reemplaza && st.envios.filter(function (x) { return x.id === st.reemplaza; })[0];
    return '<form class="au-up" id="auForm" novalidate>' +
      '<div class="au-main">' +
      (corr ? '<p class="au-corr">Versión corregida de <b>' + esc(corr.titulo) + '</b> <button type="button" class="au-link" data-au-nocorr>No es una corrección</button></p>' : '') +
      '<div class="au-seg" role="radiogroup" aria-label="Formato">' +
      '<button type="button" role="radio" data-au-fmt="pdf" aria-checked="' + pdf + '">PDF</button>' +
      '<button type="button" role="radio" data-au-fmt="texto" aria-checked="' + !pdf + '">Texto</button></div>' +
      (pdf ? zona() : '<div class="au-field"><label for="auCuerpo">Texto del análisis</label>' +
        '<textarea id="auCuerpo" name="cuerpo" rows="14" placeholder="Escribí o pegá tu análisis.&#10;&#10;## Para un subtítulo&#10;- Para una lista&#10;**Para negrita**"></textarea>' +
        '<small class="au-help" id="auPalabras">Párrafos separados por una línea en blanco · "## " subtítulo · "- " lista · **negrita**</small></div>') +
      '<div class="au-field"><label for="auTit">Título</label><input id="auTit" name="titulo" maxlength="' + MAX_TIT + '" placeholder="Ej.: AL30 vs GD30: cuánto se paga hoy por la ley Nueva York" required></div>' +
      '<div class="au-field"><label for="auRes">Resumen <small>se ve debajo del título en la lista</small></label><textarea id="auRes" name="resumen" rows="2" maxlength="' + MAX_RES + '" placeholder="Dos líneas: de qué trata y a qué conclusión llegás." required></textarea><small class="au-help au-count" id="auResN">0 / ' + MAX_RES + '</small></div>' +
      '<div class="au-two"><div class="au-field"><label for="auCat">Categoría</label><select id="auCat" name="categoria" required><option value="">Elegí una</option>' + CATS.map(function (c) { return '<option value="' + c[0] + '">' + c[1] + '</option>'; }).join('') + '</select></div>' +
      '<div class="au-field"><label for="auAct">Activos que mencionás <small>opcional</small></label><input id="auAct" name="activos" placeholder="AL30, GD30, GGAL"></div></div>' +
      '<div class="au-field"><label for="auPos">Tus posiciones en esos activos</label><input id="auPos" name="posiciones" placeholder="Ej.: Tengo GD30 · No tengo posiciones"><small class="au-help">Se aclara al pie del análisis.</small></div>' +
      '<label class="au-check"><input type="checkbox" name="autoria" required><span>Soy el autor del contenido y tengo derecho a publicarlo.</span></label>' +
      '<label class="au-check"><input type="checkbox" name="reglas" required><span>No incluye recomendaciones de compra o venta, promesas de rentabilidad ni promoción de servicios pagos.</span></label>' +
      '<div class="au-send"><button type="submit" class="an-gold au-btn" id="auEnviar" disabled>Enviar a revisión</button><span class="au-help" id="auFalta">Completá los campos para enviar.</span></div>' +
      '</div>' +
      '<aside class="au-side">' +
      '<div class="au-card"><h5>Antes de enviar</h5><ul class="au-rules">' +
      '<li><b>Análisis, no órdenes.</b> Contá qué ves y por qué; evitá "comprá" o "conviene vender".</li>' +
      '<li><b>Datos con fecha y fuente.</b> Los verificamos antes de publicar.</li>' +
      '<li><b>Sin promociones.</b> Nada de cursos, grupos pagos ni links de referido.</li>' +
      '<li><b>Tus links van en tu perfil:</b> LinkedIn, redes y el lugar donde trabajás.</li></ul></div>' +
      '<div class="au-card"><h5>Qué pasa después</h5><ol class="au-steps">' +
      '<li><span>1</span>Recibido</li><li><span>2</span>Revisión editorial</li><li><span>3</span>Publicado o con cambios sugeridos</li></ol>' +
      '<p class="au-note">Te avisamos por mail en cada paso. El contenido sigue siendo tuyo: podés publicarlo en tus canales y pedir que lo retiremos cuando quieras.</p></div>' +
      '</aside></form>';
  }
  function zona() {
    if (st.archivo) {
      return '<div class="au-file">' + (st.tapa ? '<img src="' + st.tapa + '" alt="Página 1">' : '<span class="au-file__ph"></span>') +
        '<div><b>' + esc(st.archivo.name) + '</b><small>' + (st.archivo.size / 1048576).toFixed(1).replace('.', ',') + ' MB' + (st.paginas ? ' · ' + st.paginas + ' páginas' : '') + '</small>' +
        '<small class="au-ok">La página 1 va a ser la tapa en la lista.</small>' +
        '<button type="button" class="au-link" data-au-quitar>Cambiar archivo</button></div></div>';
    }
    return '<label class="au-drop" id="auDrop"><input type="file" accept="application/pdf" id="auPdf" hidden>' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/></svg>' +
      '<b>Arrastrá tu PDF o hacé click</b><small>Hasta ' + MAX_MB + ' MB · la página 1 es la tapa</small></label>';
  }

  // ---------- mis envíos ----------
  var PASOS = ['Recibido', 'Revisión editorial', 'Publicado'];
  function pasos(e) {
    var i = { recibido: 0, revision: 1, cambios: 1, rechazado: 1, publicado: 2, retirado: 2 }[e.estado];
    return '<ol class="au-track">' + PASOS.map(function (p, k) {
      var cls = k < i || e.estado === 'publicado' ? 'ok' : k === i ? (e.estado === 'cambios' || e.estado === 'rechazado' ? 'ojo' : 'now') : '';
      var txt = k === 1 && e.estado === 'cambios' ? 'Cambios sugeridos' : k === 1 && e.estado === 'rechazado' ? 'No publicado' : k === 2 && e.estado === 'retirado' ? 'Retirado' : p;
      var cuando = k === 0 ? fecha(e.enviado) : k === 1 && e.revisado ? fecha(e.revisado) : k === 2 && e.publicado ? fecha(e.publicado) : '';
      return '<li class="' + cls + '"><span class="au-track__d"></span><b>' + txt + '</b><em>' + cuando + '</em></li>';
    }).join('') + '</ol>';
  }
  var ESTADO = { recibido: ['En revisión', ''], revision: ['En revisión', ''], cambios: ['Cambios sugeridos', 'ojo'], publicado: ['Publicado', 'ok'], rechazado: ['No publicado', 'mal'], retirado: ['Retirado', ''] };
  function envios() {
    if (!st.envios.length) return '<p class="au-vacio">Todavía no enviaste nada. <button type="button" class="au-link" data-au-tab="subir">Subí tu primer análisis</button></p>';
    return '<div class="au-list">' + st.envios.map(function (e) {
      var ab = st.abierto === e.id, es = ESTADO[e.estado];
      return '<article class="au-env' + (ab ? ' on' : '') + '">' +
        '<button type="button" class="au-env__h" data-au-abrir="' + esc(e.id) + '" aria-expanded="' + ab + '">' +
        '<span class="au-env__cv">' + (e.tapa ? '<img src="' + esc(e.tapa) + '" alt="" loading="lazy">' : '<img class="logo" src="assets/img/logo-mark-512.png" alt="">') + '</span>' +
        '<span class="au-env__b"><span class="au-k">' + esc(CATN[e.categoria] || '') + '<i></i>enviado ' + fecha(e.enviado) + '</span><span class="au-env__t">' + esc(e.titulo) + '</span></span>' +
        '<span class="rv-pill ' + es[1] + '"><span class="rv-dot"></span>' + es[0] + '</span></button>' +
        (ab ? '<div class="au-env__d">' + pasos(e) +
          (e.estado === 'cambios' || e.estado === 'rechazado' ? '<div class="au-msg"><span class="au-k">Mensaje de Ignacio · ' + fecha(e.revisado) + '</span><p>' + esc(e.mensaje).replace(/\n/g, '<br>') + '</p>' +
            '<div class="au-msg__acc">' + (e.estado === 'cambios' ? '<button type="button" class="an-gold au-btn" data-au-corregir="' + esc(e.id) + '">Subir versión corregida</button>' : '') + '<a class="au-link" href="mailto:manfredi.investment@gmail.com?subject=' + encodeURIComponent('Sobre mi análisis: ' + e.titulo) + '">Responder por mail</a></div></div>' : '') +
          (e.estado === 'publicado' ? '<div class="au-pub"><span><strong>' + (e.lecturas ? e.lecturas.toLocaleString('es-AR') : '—') + '</strong>lecturas</span>' +
            '<a class="au-link" href="#analisis">Verlo en la sección</a>' + (e.retiroPedido ? '<span class="au-help">Pediste retirarlo el ' + fecha(e.retiroPedido) + '</span>' : '<button type="button" class="au-link" data-au-retirar="' + esc(e.id) + '">Pedir que lo retiren</button>') + '</div>' : '') +
          (e.estado === 'recibido' ? '<p class="au-note">Lo estamos revisando. Te avisamos por mail.</p>' : '') +
          '</div>' : '') + '</article>';
    }).join('') + '</div>';
  }

  // ---------- perfil ----------
  function perfil() {
    var a = st.autor, l = a.links || {}, t = l.trabajo || {};
    return '<form class="au-up" id="auPerfil">' +
      '<div class="au-main">' +
      '<div class="au-foto">' + av(a, 'lg') + '<div><b>Foto de perfil</b><small class="au-help">Cuadrada, mínimo 400 px.</small><label class="au-link">Cambiar foto<input type="file" accept="image/*" hidden></label></div></div>' +
      '<div class="au-two"><div class="au-field"><label>Nombre</label><input name="nombre" value="' + esc(a.nombre) + '"></div>' +
      '<div class="au-field"><label>Cómo te presentás</label><input name="rol" value="' + esc(a.rol || '') + '" placeholder="Ej.: Economista (UNR) · Analista macro"></div></div>' +
      '<div class="au-field"><label>Bio corta <small>opcional</small></label><textarea name="bio" rows="3" maxlength="280" placeholder="Dos o tres líneas sobre tu formación y lo que analizás.">' + esc(a.bio || '') + '</textarea></div>' +
      '<h5 class="au-h5">Tus links</h5>' +
      '<div class="au-two"><div class="au-field"><label>LinkedIn</label><input name="linkedin" value="' + esc(l.linkedin || '') + '" placeholder="https://www.linkedin.com/in/…"></div>' +
      '<div class="au-field"><label>Instagram</label><input name="instagram" value="' + esc(l.instagram || '') + '" placeholder="https://www.instagram.com/…"></div></div>' +
      '<div class="au-two"><div class="au-field"><label>X</label><input name="x" value="' + esc(l.x || '') + '" placeholder="https://x.com/…"></div>' +
      '<div class="au-field"><label>Dónde trabajás</label><input name="trabajo" value="' + esc(t.nombre || '') + '" placeholder="Nombre de la empresa o facultad"></div></div>' +
      '<div class="au-send"><button type="submit" class="an-gold au-btn">Guardar cambios</button></div>' +
      '</div>' +
      '<aside class="au-side"><div class="au-card"><h5>Así te ven los lectores</h5>' +
      '<div class="au-prev">' + av(a) + '<div><b>' + esc(a.nombre) + (a.verificado ? '<span class="an-verif">✓</span>' : '') + '</b><small>' + esc(a.rol || '') + '</small></div></div>' +
      '<p class="au-note">Tu perfil muestra tus publicaciones, tus links y desde cuándo publicás en Manfredi. Es tu página para compartir.</p>' +
      '<a class="au-link" href="#analista-' + esc(a.slug) + '">Abrir mi perfil público</a></div></aside></form>';
  }

  function pintar() {
    var box = $('anAutor');
    if (!st.autor) return;
    box.innerHTML = '<div class="au">' + cabeza() + '<div class="au-body">' + (st.tab === 'subir' ? subir() : st.tab === 'envios' ? envios() : perfil()) + '</div>' +
      (DEMO ? '<p class="rv-pie">Vista previa en local: nada se envía ni se guarda.</p>' : '') + '</div>';
    if (st.tab === 'subir') validar();
  }

  /* ------------------------------ formulario ------------------------------ */
  function validar() {
    var f = $('auForm'); if (!f) return;
    var falta = [];
    if (st.formato === 'pdf' && !st.archivo) falta.push('el PDF');
    if (st.formato === 'texto' && f.cuerpo.value.trim().split(/\s+/).length < 150) falta.push('el texto (mínimo 150 palabras)');
    if (!f.titulo.value.trim()) falta.push('el título');
    if (!f.resumen.value.trim()) falta.push('el resumen');
    if (!f.categoria.value) falta.push('la categoría');
    if (!f.autoria.checked || !f.reglas.checked) falta.push('las dos confirmaciones');
    $('auEnviar').disabled = !!falta.length || st.enviando;
    $('auFalta').textContent = falta.length ? 'Te falta completar: ' + falta.join(', ') + '.' : 'Listo para enviar.';
    $('auFalta').classList.toggle('au-ok', !falta.length);
    $('auResN').textContent = f.resumen.value.length + ' / ' + MAX_RES;
    var pal = $('auPalabras');
    if (pal) { var n = f.cuerpo.value.trim() ? f.cuerpo.value.trim().split(/\s+/).length : 0; pal.textContent = n ? n + ' palabras · ' + Math.max(1, Math.round(n / 200)) + ' min de lectura' : pal.textContent; }
  }
  function leerPdf(file) {
    if (!file) return;
    if (file.type !== 'application/pdf') { aviso('Tiene que ser un PDF.'); return; }
    if (file.size > MAX_MB * 1048576) { aviso('El PDF supera los ' + MAX_MB + ' MB.'); return; }
    st.archivo = file; st.tapa = ''; st.paginas = 0;
    var guardado = guardarForm();
    pintar(); restaurarForm(guardado);
    // la tapa = página 1, igual que en la lista
    if (!window.pdfjsLib) return;
    file.arrayBuffer().then(function (buf) { return window.pdfjsLib.getDocument({ data: buf }).promise; }).then(function (pdf) {
      st.paginas = pdf.numPages;
      return pdf.getPage(1).then(function (pg) {
        var v = pg.getViewport({ scale: 1 }), sc = 320 / v.width, vp = pg.getViewport({ scale: sc });
        var c = document.createElement('canvas'); c.width = vp.width; c.height = vp.height;
        return pg.render({ canvasContext: c.getContext('2d'), viewport: vp }).promise.then(function () { st.tapa = c.toDataURL('image/jpeg', .85); });
      });
    }).then(function () { var g = guardarForm(); pintar(); restaurarForm(g); }).catch(function (e) { console.warn('[autor] pdf', e.message); });
  }
  function guardarForm() {
    var f = $('auForm'); if (!f) return null;
    var d = {}; Array.prototype.forEach.call(f.elements, function (el) { if (el.name) d[el.name] = el.type === 'checkbox' ? el.checked : el.value; });
    return d;
  }
  function restaurarForm(d) {
    var f = $('auForm'); if (!f || !d) return;
    Object.keys(d).forEach(function (k) { var el = f.elements[k]; if (!el) return; if (el.type === 'checkbox') el.checked = d[k]; else el.value = d[k]; });
    validar();
  }

  /* ------------------------------ eventos ------------------------------ */
  function montarEventos() {
    var box = $('anAutor');
    box.addEventListener('click', function (e) {
      var t = e.target.closest('[data-au-tab],[data-au-fmt],[data-au-abrir],[data-au-quitar],[data-au-retirar],[data-au-corregir],[data-au-nocorr]');
      if (!t) return;
      if (t.dataset.auCorregir) {
        var v = st.envios.filter(function (x) { return x.id === t.dataset.auCorregir; })[0];
        st.reemplaza = v.id; st.tab = 'subir'; st.formato = v.formato || 'pdf'; pintar(); window.scrollTo({ top: 0 });
        var f0 = $('auForm'); if (f0) { f0.titulo.value = v.titulo; f0.categoria.value = v.categoria; validar(); }
        return;
      }
      if (t.hasAttribute('data-au-nocorr')) { var g0 = guardarForm(); st.reemplaza = null; pintar(); restaurarForm(g0); return; }
      if (t.dataset.auTab) { st.tab = t.dataset.auTab; pintar(); window.scrollTo({ top: 0 }); return; }
      if (t.dataset.auFmt) { var g = guardarForm(); st.formato = t.dataset.auFmt; pintar(); restaurarForm(g); return; }
      if (t.dataset.auAbrir) { st.abierto = st.abierto === t.dataset.auAbrir ? null : t.dataset.auAbrir; pintar(); return; }
      if (t.hasAttribute('data-au-quitar')) { var g2 = guardarForm(); st.archivo = null; st.tapa = ''; pintar(); restaurarForm(g2); return; }
      if (t.dataset.auRetirar) {
        if (DEMO) { aviso('Vista previa: acá se manda el pedido para retirarlo.'); return; }
        API.post('/envios/' + t.dataset.auRetirar + '/retirar').then(cargarEnvios).then(function () { pintar(); aviso('Listo: le avisamos a Ignacio para que lo retire.'); })
          .catch(function (er) { aviso(er.message); });
      }
    });
    box.addEventListener('change', function (e) {
      if (e.target.id === 'auPdf') leerPdf(e.target.files[0]);
      else validar();
    });
    box.addEventListener('input', validar);
    box.addEventListener('dragover', function (e) { var d = e.target.closest('#auDrop'); if (d) { e.preventDefault(); d.classList.add('on'); } });
    box.addEventListener('dragleave', function (e) { var d = e.target.closest('#auDrop'); if (d) d.classList.remove('on'); });
    box.addEventListener('drop', function (e) { var d = e.target.closest('#auDrop'); if (d) { e.preventDefault(); leerPdf(e.dataTransfer.files[0]); } });
    box.addEventListener('submit', function (e) {
      e.preventDefault();
      if (e.target.id === 'auPerfil') { guardarPerfil(e.target); return; }
      var f = e.target;
      if (DEMO) {
        st.envios.unshift({ id: 'nuevo-' + Date.now(), titulo: f.titulo.value.trim(), categoria: f.categoria.value, estado: 'recibido', enviado: new Date().toISOString(), tapa: st.formato === 'pdf' ? st.tapa : '' });
        st.abierto = st.envios[0].id; st.archivo = null; st.tapa = ''; st.tab = 'envios';
        pintar(); window.scrollTo({ top: 0 });
        aviso('Recibido. Te avisamos por mail cuando esté revisado.');
        return;
      }
      enviar(f);
    });
  }

  /* ------------------------------ envío real ------------------------------ */
  function enviar(f) {
    var btn = $('auEnviar');
    st.enviando = true; btn.disabled = true; btn.textContent = st.formato === 'pdf' ? 'Subiendo el PDF…' : 'Enviando…';
    var datos = { formato: st.formato, titulo: f.titulo.value, resumen: f.resumen.value, categoria: f.categoria.value, activos: f.activos.value, posiciones: f.posiciones.value,
      autoria: f.autoria.checked, reglas: f.reglas.checked, reemplaza: st.reemplaza || undefined };
    if (st.formato === 'texto') datos.cuerpo = f.cuerpo.value; else if (st.tapa) datos.tapa = st.tapa;
    API.post('/envios', datos).then(function (r) {
      if (st.formato !== 'pdf') return r;
      // el PDF va aparte, directo al bucket
      return API.put('/envios/' + r.id + '/pdf', new Blob([st.archivo], { type: 'application/pdf' }));
    }).then(function (r) {
      st.enviando = false; st.archivo = null; st.tapa = ''; st.reemplaza = null; st.tab = 'envios'; st.abierto = r.id;
      return cargarEnvios();
    }).then(function () {
      pintar(); window.scrollTo({ top: 0 });
      aviso('Recibido. Te avisamos por mail cuando esté revisado.');
    }).catch(function (er) {
      st.enviando = false; btn.textContent = 'Enviar a revisión'; validar();
      aviso('No se pudo enviar: ' + er.message);
    });
  }
  function guardarPerfil(f) {
    if (DEMO) { aviso('Vista previa: acá se guardaría tu perfil.'); return; }
    var d = {}; ['nombre', 'rol', 'bio', 'linkedin', 'instagram', 'x', 'trabajo'].forEach(function (k) { d[k] = f.elements[k] ? f.elements[k].value : ''; });
    API.post('/perfil', d).then(function (r) { st.autor = r.autor; pintar(); aviso('Perfil guardado.'); }).catch(function (er) { aviso('No se pudo guardar: ' + er.message); });
  }

  window.AnAutor = {
    habilitado: false,
    mostrar: function () {
      if (st.autor) { cargarEnvios().then(pintar, pintar); return; }
      var box = $('anAutor');
      if (box) box.innerHTML = '<a class="an-back" href="#analisis">← Análisis e informes</a><p class="nt-empty">Esta sección es para autores habilitados. Iniciá sesión con el mail que te habilitamos.</p>';
    }
  };
  function iniciar() {
    var btn = $('anMio');
    cargar().then(function () {
      window.AnAutor.habilitado = true;
      if (btn) btn.hidden = false;
      montarEventos();
      if (location.hash === '#autor') pintar();
    }).catch(function (e) { console.warn('[autor]', e.message); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
