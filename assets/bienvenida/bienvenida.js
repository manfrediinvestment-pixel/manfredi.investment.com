/* Bienvenida (se carga en index.html):
   1) Quien entra por primera vez a la home, sin cuenta y sin un link a una
      sección (#portfolio, #mercados…), va a /bienvenida.html. Una sola vez:
      la bienvenida marca mi_bienvenida_vista y "Explorar la página" vuelve acá.
   2) Los botones de la bienvenida vuelven con ?registro=1, ?ingresar=1,
      ?membresia=1 o ?warren=1: acá se abre el login o el pago y se limpia la URL.
   ?membresia=1&codigo=MANFREDI30 abre el pago con el código ya cargado
   (link del mensaje de FINANZAS en Instagram).
   Test: ?bienvenida=1 fuerza la redirección aunque ya la hayas visto. */
(function () {
  var KEY = 'mi_bienvenida_vista';
  var q = new URLSearchParams(location.search);

  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function cuando(fn, cb, max) {
    var t0 = Date.now();
    (function chk() { if (typeof window[fn] === 'function') return cb(window[fn]); if (Date.now() - t0 < (max || 8000)) setTimeout(chk, 120); })();
  }

  /* ---- 2) acciones que vienen de la bienvenida ---- */
  var accion = q.has('registro') || q.has('ingresar') ? 'login' : q.has('membresia') ? 'pago' : q.has('warren') ? 'warren' : null;
  if (accion) {
    var codigo = (q.get('codigo') || '').replace(/[^A-Za-z0-9]/g, '').slice(0, 30).toUpperCase();
    ls(KEY, 'vista');
    q.delete('registro'); q.delete('ingresar'); q.delete('membresia'); q.delete('warren'); q.delete('codigo');
    var limpia = location.pathname + (q.toString() ? '?' + q.toString() : '') + location.hash;
    try { history.replaceState(null, '', limpia); } catch (e) {}
    if (accion === 'login') cuando('showLoginOverlay', function (f) { setTimeout(function () { if (!window._currentUser) f(); }, 600); });
    if (accion === 'pago') cuando('openPaymentModal', function (f) {
      f();
      if (!codigo) return;
      cuando('toggleDiscountPanel', function (abrir) {
        var panel = document.getElementById('payDiscountPanel');
        var campo = document.getElementById('payDiscountCode');
        if (!panel || !campo) return;
        if (panel.classList.contains('hidden')) abrir();
        campo.value = codigo;
        if (window.updateDiscountPriceDisplay) window.updateDiscountPriceDisplay();
      });
    });
    if (accion === 'warren') cuando('toggleWarren', function (f) { setTimeout(f, 600); });
    return;
  }

  /* ---- 1) primera visita sin cuenta → bienvenida ---- */
  var forzada = q.has('bienvenida');
  if (!forzada) {
    if (ls(KEY) || ls('mi_member_token')) return;
    var h = location.hash.replace('#', '');
    if (h && h !== 'inicio') return;                                    // vino a una sección puntual
    if (/bot|crawl|spider|slurp|lighthouse|headless|preview/i.test(navigator.userAgent)) return;
    if (navigator.webdriver) return;
  }
  function ir() { ls(KEY, 'redirigida'); location.replace('/bienvenida.html'); }
  if (forzada) return ir();

  // ¿hay una sesión de Firebase guardada en este navegador? Entonces esperamos a
  // saber si está logueado antes de mandarlo a ningún lado.
  function puedeHaberSesion() {
    if (!window.indexedDB || !indexedDB.databases) return Promise.resolve(true);
    return indexedDB.databases().then(function (dbs) {
      return dbs.some(function (d) { return d && /firebase/i.test(d.name || ''); });
    }).catch(function () { return true; });
  }
  puedeHaberSesion().then(function (quizas) {
    if (!quizas) return ir();
    var t0 = Date.now();
    (function chk() {
      if (window._currentUser) { ls(KEY, 'registrado'); return; }
      if (window._currentUser === null) return ir();
      if (Date.now() - t0 > 5000) return;                               // no sabemos: no molestar
      setTimeout(chk, 150);
    })();
  });
})();
