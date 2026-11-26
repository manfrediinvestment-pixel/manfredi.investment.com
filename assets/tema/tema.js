/* Botón sol / luna: cambia el sitio entre oscuro (el de siempre) y claro, y lo recuerda.
   El atributo se pone antes de pintar con un script chiquito en el <head> (sin parpadeo). */
(function () {
  'use strict';
  var KEY = 'mi_tema', root = document.documentElement;
  function actual() { return root.getAttribute('data-tema') === 'claro' ? 'claro' : 'oscuro'; }
  function poner(t) {
    if (t === 'claro') root.setAttribute('data-tema', 'claro'); else root.removeAttribute('data-tema');
    try { localStorage.setItem(KEY, t); } catch (e) {}
    var b = document.getElementById('miTema');
    if (b) { b.setAttribute('aria-pressed', String(t === 'claro')); b.setAttribute('aria-label', t === 'claro' ? 'Pasar a modo oscuro' : 'Pasar a modo claro'); b.title = t === 'claro' ? 'Modo oscuro' : 'Modo claro'; }
  }
  function montar() {
    var inner = document.querySelector('.navbar .nav-inner'), user = document.getElementById('navUserArea');
    if (!inner || document.getElementById('miTema')) return;
    var b = document.createElement('button');
    b.type = 'button'; b.id = 'miTema'; b.className = 'mi-tema';
    b.innerHTML = '<svg class="luna" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>' +
      '<svg class="sol" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
    b.addEventListener('click', function () { poner(actual() === 'claro' ? 'oscuro' : 'claro'); });
    if (user) inner.insertBefore(b, user); else inner.appendChild(b);
    poner(actual());
  }
  if (document.readyState !== 'loading') montar(); else document.addEventListener('DOMContentLoaded', montar);
})();
