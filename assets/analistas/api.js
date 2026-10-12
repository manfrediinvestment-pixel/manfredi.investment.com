/* Cliente del worker manfredi-analistas (workers/analistas). Lo usan analistas.js,
   autor.js y revision.js.
   - En producción: https://manfredi-analistas.nachito2502.workers.dev con el ID token de Firebase.
   - En local: el worker en wrangler dev (http://127.0.0.1:8791) y, para probar sin
     Firebase, ?dev=<mail> manda "Bearer dev:<mail>" (el worker solo lo acepta con DEV=1). */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var qs = new URLSearchParams(location.search);
  var BASE = qs.get('anapi') && LOCAL ? qs.get('anapi') : LOCAL ? 'http://127.0.0.1:8791' : 'https://manfredi-analistas.nachito2502.workers.dev';
  var DEV = LOCAL ? (qs.get('dev') || '').toLowerCase() : '';

  // espera a que Firebase diga si hay sesión (máx. ~8 s)
  function sesion() {
    if (DEV) return Promise.resolve({ email: DEV });
    return new Promise(function (ok) {
      var n = 0;
      (function mirar() {
        if (window._currentUser || window._authChecked || ++n > 80) return ok(window._currentUser || null);
        setTimeout(mirar, 100);
      })();
    });
  }
  function token() {
    if (DEV) return Promise.resolve('dev:' + DEV);
    var u = window._currentUser;
    return u && u.getIdToken ? u.getIdToken() : Promise.resolve(null);
  }
  function pedir(metodo, ruta, cuerpo, opts) {
    opts = opts || {};
    return token().then(function (t) {
      var h = {};
      if (t) h.Authorization = 'Bearer ' + t;
      var body = cuerpo;
      if (cuerpo != null && !(cuerpo instanceof Blob)) { h['Content-Type'] = 'application/json'; body = JSON.stringify(cuerpo); }
      if (cuerpo instanceof Blob) h['Content-Type'] = cuerpo.type || 'application/octet-stream';
      return fetch(BASE + ruta, { method: metodo, headers: h, body: body, cache: 'no-cache' });
    }).then(function (r) {
      if (opts.blob) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.blob(); }
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) { var e = new Error(d.error || ('HTTP ' + r.status)); e.status = r.status; throw e; }
        return d;
      });
    });
  }
  window.AnApi = {
    base: BASE, local: LOCAL, dev: DEV,
    url: function (rel) { return /^https?:/.test(rel || '') ? rel : BASE + rel; },
    sesion: sesion,
    get: function (r, o) { return pedir('GET', r, null, o); },
    post: function (r, b) { return pedir('POST', r, b || {}); },
    put: function (r, blob) { return pedir('PUT', r, blob); },
    // /yo, una sola vez por carga (lo comparten el espacio del autor y el Panel)
    yo: (function () { var p = null; return function () { return p || (p = sesion().then(function (u) { return u ? pedir('GET', '/yo') : { sesion: false }; }).catch(function () { return { sesion: false }; })); }; })()
  };
})();
