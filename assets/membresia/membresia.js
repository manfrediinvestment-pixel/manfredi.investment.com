/* Membresía: estado de los botones de plan (home + cartel de pago), video de Manfredi Pro
   (se reproduce solo cuando está a la vista) y entrada de la sección #membresia.
   El index dispara 'mi:auth' cada vez que se resuelve el login / la membresía. */
(function () {
  var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  function esSocio() { return window._isMiembro === true; }
  function logueado() { return !!(window._currentUser && window._currentUser.email); }

  function sync() {
    var socio = esSocio(), user = logueado();
    document.querySelectorAll('[data-mb-free]').forEach(function (b) {
      b.classList.remove('is-current'); b.disabled = false;
      if (socio) { b.textContent = 'Incluido en Manfredi Pro'; b.disabled = true; b.classList.add('is-current'); }
      else if (user) { b.textContent = 'Tu plan actual'; b.disabled = true; b.classList.add('is-current'); }
      else { b.textContent = 'Crear cuenta gratis'; }
    });
    document.querySelectorAll('[data-mb-pro]').forEach(function (b) {
      b.innerHTML = (socio ? 'Ir a Manfredi Pro' : (b.getAttribute('data-mb-pro') || 'Suscribirme')) + ' ' + ARROW;
    });
    document.querySelectorAll('[data-mb-tag]').forEach(function (t) {
      t.textContent = socio ? 'Tu plan' : t.getAttribute('data-mb-tag');
    });
  }

  document.addEventListener('click', function (e) {
    // Asesoría: lleva a la sección (cerrando el cartel de pago si estaba abierto)
    var ase = e.target.closest('[data-mb-ase]');
    if (ase) {
      e.preventDefault();
      if (window.closePaymentModal) window.closePaymentModal();
      if (location.hash === '#asesoria') window.dispatchEvent(new HashChangeEvent('hashchange'));
      else location.hash = 'asesoria';
      var top = function () { window.scrollTo({ top: 0, behavior: 'instant' }); };
      top(); setTimeout(top, 60); setTimeout(top, 250);
      return;
    }
    var free = e.target.closest('[data-mb-free]');
    if (free && !free.disabled) {
      e.preventDefault();
      if (window.closePaymentModal) window.closePaymentModal();
      if (window.showLoginOverlay) window.showLoginOverlay();
      return;
    }
    var pro = e.target.closest('[data-mb-pro]');
    if (!pro || pro.disabled) return;
    e.preventDefault();
    if (esSocio()) {
      if (window.closePaymentModal) window.closePaymentModal();
      location.hash = 'pro';
      return;
    }
    if (pro.hasAttribute('data-mb-pay')) { if (window.handlePayment) window.handlePayment('mercadopago'); }
    else if (window.openPaymentModal) window.openPaymentModal();
  });

  document.addEventListener('mi:auth', sync);
  // por si el login se resolvió antes de que cargara este archivo
  var tries = 0, iv = setInterval(function () { sync(); if (window._authChecked || ++tries > 20) clearInterval(iv); }, 500);
  sync();

  var sec = document.querySelector('.mbr');
  if (!sec) return;
  var film = document.getElementById('mbrFilm');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!('IntersectionObserver' in window)) { if (film) film.setAttribute('controls', ''); return; }

  // video: arranca al verlo, se pausa al salir (ahorra datos); con movimiento reducido, con controles
  if (film) {
    if (reduce) film.setAttribute('controls', '');
    else new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting) { var p = film.play(); if (p && p.catch) p.catch(function () { film.setAttribute('controls', ''); }); }
        else film.pause();
      });
    }, { threshold: 0.35 }).observe(film);
  }

  if (reduce) return;
  sec.classList.add('mb-pre');
  var io = new IntersectionObserver(function (ents) {
    ents.forEach(function (en) {
      if (!en.isIntersecting) return;
      io.disconnect();
      sec.classList.add('mb-in');
    });
  }, { threshold: 0.12 });
  io.observe(sec);
})();
