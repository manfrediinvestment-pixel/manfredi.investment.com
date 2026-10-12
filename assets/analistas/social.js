/* Me gusta y comentarios de "Análisis e informes". Lo usa assets/analistas/analistas.js.
   - Se guarda en Firestore (mismo proyecto que el login):
       analisis/{pubId}/likes/{uid}          existe = le gustó
       analisis/{pubId}/comentarios/{auto}   { uid, nombre, foto, texto, creado }
     Los me gusta del usuario también quedan en users/{uid}.meGusta para leerlos en una sola lectura.
     Las reglas de seguridad están en firestore.rules (sección analisis).
   - Solo los registrados pueden dar me gusta o comentar; leer es libre.
   - En localhost con los autores de ejemplo usa datos de prueba en localStorage
     (sesión de prueba iniciada; con ?sesion=0 se ve como alguien sin cuenta). */
(function () {
  var FB = 'https://www.gstatic.com/firebasejs/10.12.0/';
  var CREADOR = 'nachito2502@gmail.com';
  var MAX = 1000;
  var qs = new URLSearchParams(location.search);
  var MOCK = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && qs.get('ejemplos') !== '0';

  var st = { likes: {}, coms: {}, mios: {}, hilos: {}, user: null, abiertos: {} };
  var oyentes = [];

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function nombreDe(u) { return u.displayName || String(u.email || 'Usuario').split('@')[0]; }

  /* ------------------------------ backend: Firestore ------------------------------ */
  var fs = null;
  function firestore() {
    if (fs) return fs;
    fs = Promise.all([import(FB + 'firebase-app.js'), import(FB + 'firebase-auth.js'), import(FB + 'firebase-firestore.js')]).then(function (m) {
      // la app la inicializa index.html; si todavía no está, esperamos un poco
      return new Promise(function (ok, mal) {
        var n = 0;
        (function esperar() {
          if (m[0].getApps().length) return ok({ app: m[0].getApp(), A: m[1], F: m[2] });
          if (++n > 100) return mal(new Error('Firebase no inicializado'));
          setTimeout(esperar, 100);
        })();
      });
    }).then(function (x) {
      var db = x.F.getFirestore(x.app), auth = x.A.getAuth(x.app), F = x.F;
      x.A.onAuthStateChanged(auth, function (u) { setUser(u ? { uid: u.uid, nombre: nombreDe(u), foto: u.photoURL || '', email: u.email || '' } : null); });
      return {
        contar: function (id) {
          var base = F.collection(db, 'analisis', id, 'likes'), cs = F.collection(db, 'analisis', id, 'comentarios');
          return Promise.all([F.getCountFromServer(base), F.getCountFromServer(cs)]).then(function (r) { return { likes: r[0].data().count, coms: r[1].data().count }; });
        },
        mios: function (u) {
          return F.getDoc(F.doc(db, 'users', u.uid)).then(function (s) { var d = s.exists() ? s.data() : {}; return Array.isArray(d.meGusta) ? d.meGusta : []; });
        },
        like: function (id, u, on) {
          var b = F.writeBatch(db), ref = F.doc(db, 'analisis', id, 'likes', u.uid), uref = F.doc(db, 'users', u.uid);
          if (on) { b.set(ref, { creado: F.serverTimestamp() }); b.set(uref, { meGusta: F.arrayUnion(id) }, { merge: true }); }
          else { b.delete(ref); b.set(uref, { meGusta: F.arrayRemove(id) }, { merge: true }); }
          return b.commit();
        },
        hilo: function (id) {
          var q = F.query(F.collection(db, 'analisis', id, 'comentarios'), F.orderBy('creado', 'asc'), F.limit(200));
          return F.getDocs(q).then(function (s) { return s.docs.map(function (d) { var c = d.data(); return { id: d.id, uid: c.uid, nombre: c.nombre, foto: c.foto, texto: c.texto, t: c.creado && c.creado.toMillis ? c.creado.toMillis() : Date.now() }; }); });
        },
        comentar: function (id, u, texto) {
          return F.addDoc(F.collection(db, 'analisis', id, 'comentarios'), { uid: u.uid, nombre: u.nombre, foto: u.foto, texto: texto, creado: F.serverTimestamp() })
            .then(function (r) { return { id: r.id, uid: u.uid, nombre: u.nombre, foto: u.foto, texto: texto, t: Date.now() }; });
        },
        borrar: function (id, cid) { return F.deleteDoc(F.doc(db, 'analisis', id, 'comentarios', cid)); }
      };
    });
    return fs;
  }

  /* ------------------------------ backend: prueba local ------------------------------ */
  function mock() {
    var K = 'an-social-prueba';
    var leer = function () { try { return JSON.parse(localStorage.getItem(K)) || null; } catch (e) { return null; } };
    var db = leer() || { likes: {}, coms: {} };
    var guardar = function () { localStorage.setItem(K, JSON.stringify(db)); };
    var yo = { uid: 'prueba', nombre: 'Vos (prueba)', foto: '', email: '' };
    // números de arranque fijos por publicación para que la lista no se vea vacía
    var semilla = function (id) { var h = 0; for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0; return h; };
    var EJ = [
      { nombre: 'Martina R.', texto: 'Muy claro el planteo de los tres escenarios. ¿Cómo cambia si el BCRA compra en bloque?' },
      { nombre: 'Julián P.', texto: 'Buen trabajo. Me sumo a pedir una actualización cuando salga el dato de reservas del viernes.' }
    ];
    var hilo = function (id) {
      if (!db.coms[id]) db.coms[id] = semilla(id) % 3 === 0 ? EJ.map(function (c, i) { return { id: 'ej' + i, uid: 'ej' + i, nombre: c.nombre, foto: '', texto: c.texto, t: Date.now() - (2 - i) * 36e5 * 5 }; }) : [];
      return db.coms[id];
    };
    setTimeout(function () { setUser(qs.get('sesion') === '0' ? null : yo); }, 0);
    return Promise.resolve({
      contar: function (id) { return Promise.resolve({ likes: semilla(id) % 23 + (db.likes[id] ? 1 : 0), coms: hilo(id).length }); },
      mios: function () { return Promise.resolve(Object.keys(db.likes).filter(function (k) { return db.likes[k]; })); },
      like: function (id, u, on) { db.likes[id] = on; guardar(); return Promise.resolve(); },
      hilo: function (id) { return Promise.resolve(hilo(id).slice()); },
      comentar: function (id, u, texto) { var c = { id: 'c' + Date.now(), uid: u.uid, nombre: u.nombre, foto: '', texto: texto, t: Date.now() }; hilo(id).push(c); guardar(); return Promise.resolve(c); },
      borrar: function (id, cid) { db.coms[id] = hilo(id).filter(function (c) { return c.id !== cid; }); guardar(); return Promise.resolve(); }
    });
  }

  var api = null;
  function back() { return api || (api = MOCK ? mock() : firestore()); }

  /* ------------------------------ estado ------------------------------ */
  function setUser(u) {
    st.user = u;
    st.mios = {};
    var listo = u ? back().then(function (b) { return b.mios(u); }).then(function (ids) { ids.forEach(function (id) { st.mios[id] = true; }); }).catch(function () {}) : Promise.resolve();
    listo.then(function () { pintarTodo(); oyentes.forEach(function (f) { f(u); }); });
  }

  /* ------------------------------ vista ------------------------------ */
  var ICO_LIKE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.3s-7.6-4.6-9.2-9.4C1.7 7.6 3.8 4.5 7.1 4.5c2 0 3.6 1.1 4.9 2.9 1.3-1.8 2.9-2.9 4.9-2.9 3.3 0 5.4 3.1 4.3 6.4-1.6 4.8-9.2 9.4-9.2 9.4z"/></svg>';
  var ICO_COM = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 5.5h15a1 1 0 0 1 1 1v9.2a1 1 0 0 1-1 1H10l-4.4 3.3v-3.3H4.5a1 1 0 0 1-1-1V6.5a1 1 0 0 1 1-1z"/></svg>';

  function n(x) { return x == null ? '' : String(x); }
  // la barra de una publicación; abierta = el hilo se ve siempre (nota completa)
  function barra(id, abierta) {
    return '<div class="an-soc" data-soc="' + esc(id) + '">' +
      '<button type="button" class="an-soc__b an-soc__like" data-like="' + esc(id) + '" aria-pressed="false" aria-label="Me gusta">' + ICO_LIKE + '<span data-n="likes"></span></button>' +
      (abierta ? '<span class="an-soc__b an-soc__com is-static">' + ICO_COM + '<span data-n="coms"></span></span>'
        : '<button type="button" class="an-soc__b an-soc__com" data-com="' + esc(id) + '" aria-expanded="false" aria-label="Comentarios">' + ICO_COM + '<span data-n="coms"></span></button>') +
      '</div>';
  }
  function pintar(id) {
    var l = st.likes[id], c = st.coms[id], mio = !!st.mios[id];
    document.querySelectorAll('[data-soc="' + id + '"]').forEach(function (el) {
      el.classList.add('is-ready');
      el.querySelector('[data-n="likes"]').textContent = l ? n(l) : '';
      el.querySelector('[data-n="coms"]').textContent = c ? n(c) : '';
      var b = el.querySelector('[data-like]');
      b.classList.toggle('on', mio); b.setAttribute('aria-pressed', mio);
      var cb = el.querySelector('[data-com]');
      if (cb) { cb.classList.toggle('on', !!st.abiertos[id]); cb.setAttribute('aria-expanded', !!st.abiertos[id]); }
    });
  }
  function pintarTodo() {
    Object.keys(st.likes).forEach(pintar);
    document.querySelectorAll('[data-hilo]').forEach(function (h) { pintarHilo(h.dataset.hilo); });
  }

  var pedidos = {};
  function cargar(ids) {
    ids = ids.filter(function (id) { return !pedidos[id]; });
    if (!ids.length) { pintarTodo(); return; }
    back().then(function (b) {
      ids.forEach(function (id) {
        pedidos[id] = b.contar(id).then(function (r) { st.likes[id] = r.likes; st.coms[id] = r.coms; pintar(id); })
          .catch(function (e) { delete pedidos[id]; console.warn('[analisis] contadores', e.message); });
      });
    }).catch(function (e) { console.warn('[analisis]', e.message); });
  }

  /* ------------------------------ hilo de comentarios ------------------------------ */
  function hace(t) {
    var s = Math.max(1, Math.round((Date.now() - t) / 1000));
    if (s < 60) return 'recién';
    var m = Math.round(s / 60); if (m < 60) return 'hace ' + m + ' min';
    var h = Math.round(m / 60); if (h < 24) return 'hace ' + h + ' h';
    var d = Math.round(h / 24); if (d < 30) return 'hace ' + d + ' d';
    return new Date(t).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\./g, '');
  }
  function avatar(c) {
    var ini = (String(c.nombre || '?').match(/[A-Za-zÁÉÍÓÚÑáéíóúñ]+/g) || ['?']).map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase();
    return '<span class="an-hilo__av">' + (c.foto ? '<img src="' + esc(c.foto) + '" alt="" referrerpolicy="no-referrer">' : esc(ini)) + '</span>';
  }
  function puedeBorrar(c) { return st.user && (c.uid === st.user.uid || st.user.email === CREADOR); }
  function pintarHilo(id) {
    var box = document.querySelector('[data-hilo="' + id + '"]');
    if (!box) return;
    var lista = st.hilos[id];
    var cuerpo = !lista ? '<p class="an-hilo__vacio">Cargando comentarios…</p>'
      : !lista.length ? '<p class="an-hilo__vacio">Todavía no hay comentarios. Sé el primero.</p>'
      : '<ul class="an-hilo__l">' + lista.map(function (c) {
        return '<li>' + avatar(c) + '<div><div class="an-hilo__m"><b>' + esc(c.nombre) + '</b><time>' + hace(c.t) + '</time>' +
          (puedeBorrar(c) ? '<button type="button" class="an-hilo__x" data-borrar="' + esc(c.id) + '">Eliminar</button>' : '') + '</div>' +
          '<p>' + esc(c.texto) + '</p></div></li>';
      }).join('') + '</ul>';
    var form = st.user
      ? '<form class="an-hilo__f" data-form="' + esc(id) + '">' + avatar(st.user) +
        '<textarea name="t" rows="1" maxlength="' + MAX + '" placeholder="Escribí un comentario…" aria-label="Comentario"></textarea>' +
        '<button type="submit" class="an-hilo__send" disabled>Publicar</button></form>'
      : '<div class="an-hilo__in"><span>Para comentar y dar me gusta necesitás una cuenta.</span><button type="button" class="an-hilo__login" data-login>Ingresar</button></div>';
    // si el usuario estaba escribiendo, no le borramos el texto
    var prev = box.querySelector('textarea'), txt = prev ? prev.value : '';
    box.innerHTML = cuerpo + form;
    var ta = box.querySelector('textarea');
    if (ta && txt) { ta.value = txt; ajustar(ta); }
  }
  function abrirHilo(id) {
    if (!st.hilos[id]) back().then(function (b) { return b.hilo(id); }).then(function (l) { st.hilos[id] = l; st.coms[id] = l.length; pintar(id); pintarHilo(id); })
      .catch(function (e) { st.hilos[id] = []; pintarHilo(id); console.warn('[analisis] comentarios', e.message); });
    pintarHilo(id);
  }
  // hilo debajo de una fila de la lista
  function alternar(id, fila) {
    var abierto = !st.abiertos[id];
    st.abiertos[id] = abierto;
    var sig = fila.nextElementSibling;
    if (!abierto) {
      if (sig && sig.dataset.hilo === id) { sig.classList.remove('on'); setTimeout(function () { sig.remove(); }, 260); }
    } else {
      var box = document.createElement('div');
      box.className = 'an-hilo an-hilo--fila'; box.dataset.hilo = id;
      fila.after(box);
      abrirHilo(id);
      requestAnimationFrame(function () { box.classList.add('on'); });
    }
    pintar(id);
  }
  function ajustar(ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 220) + 'px'; }
  function pedirLogin() { if (typeof window.showLoginOverlay === 'function') window.showLoginOverlay(); }

  /* ------------------------------ eventos ------------------------------ */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-like]');
    if (b) {
      e.preventDefault(); e.stopPropagation();
      var id = b.dataset.like;
      if (!st.user) { pedirLogin(); return; }
      var on = !st.mios[id];
      st.mios[id] = on; st.likes[id] = Math.max(0, (st.likes[id] || 0) + (on ? 1 : -1)); pintar(id);
      if (on) { b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
      back().then(function (x) { return x.like(id, st.user, on); }).catch(function (err) {
        st.mios[id] = !on; st.likes[id] = Math.max(0, (st.likes[id] || 0) + (on ? -1 : 1)); pintar(id);
        console.warn('[analisis] me gusta', err.message);
      });
      return;
    }
    var c = e.target.closest('[data-com]');
    if (c) { e.preventDefault(); e.stopPropagation(); alternar(c.dataset.com, c.closest('.an-row')); return; }
    if (e.target.closest('[data-login]')) { pedirLogin(); return; }
    var x = e.target.closest('[data-borrar]');
    if (x) {
      var hid = x.closest('[data-hilo]').dataset.hilo, cid = x.dataset.borrar;
      x.disabled = true;
      back().then(function (bk) { return bk.borrar(hid, cid); }).then(function () {
        st.hilos[hid] = st.hilos[hid].filter(function (k) { return k.id !== cid; }); st.coms[hid] = st.hilos[hid].length; pintar(hid); pintarHilo(hid);
      }).catch(function (err) { x.disabled = false; console.warn('[analisis] borrar', err.message); });
    }
  }, true);
  document.addEventListener('input', function (e) {
    if (!e.target.matches('.an-hilo__f textarea')) return;
    ajustar(e.target);
    e.target.form.querySelector('.an-hilo__send').disabled = !e.target.value.trim();
  });
  document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + Enter publica
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && e.target.matches('.an-hilo__f textarea')) { e.preventDefault(); e.target.form.requestSubmit(); }
  });
  document.addEventListener('submit', function (e) {
    var f = e.target.closest('[data-form]');
    if (!f) return;
    e.preventDefault();
    var id = f.dataset.form, ta = f.querySelector('textarea'), texto = ta.value.trim().slice(0, MAX), btn = f.querySelector('.an-hilo__send');
    if (!texto || !st.user) return;
    btn.disabled = true; btn.textContent = 'Publicando…';
    back().then(function (b) { return b.comentar(id, st.user, texto); }).then(function (c) {
      (st.hilos[id] = st.hilos[id] || []).push(c); st.coms[id] = st.hilos[id].length;
      ta.value = ''; pintar(id); pintarHilo(id);
    }).catch(function (err) {
      btn.disabled = false; btn.textContent = 'Publicar';
      console.warn('[analisis] comentar', err.message);
    });
  });

  window.AnSocial = {
    barra: barra,
    // contenedor del hilo siempre abierto (nota en texto)
    hilo: function (id) { return '<section class="an-hilo an-hilo--nota on" data-hilo="' + esc(id) + '"></section>'; },
    // después de pintar: pide los números y llena los hilos abiertos
    montar: function (ids) {
      cargar(ids);
      document.querySelectorAll('.an-hilo--nota[data-hilo]').forEach(function (h) { abrirHilo(h.dataset.hilo); });
      // si se repintó la lista, los hilos abiertos se cierran
      Object.keys(st.abiertos).forEach(function (id) { if (!document.querySelector('.an-hilo--fila[data-hilo="' + id + '"]')) st.abiertos[id] = false; });
    },
    alCambiarSesion: function (f) { oyentes.push(f); }
  };
  back();
})();
