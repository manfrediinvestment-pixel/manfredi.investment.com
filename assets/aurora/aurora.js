/* Título de la home: cada palabra entra con un desenfoque que se aclara,
   escalonadas, y después se dibuja la línea dorada bajo "en un solo lugar."
   Una sola vez por sesión (las siguientes visitas lo muestran quieto). */
(function () {
  var h = document.querySelector('.htx-h1');
  if (!h) return;
  var primera = true;
  try { primera = !sessionStorage.getItem('aur_intro'); sessionStorage.setItem('aur_intro', '1'); } catch (e) {}
  if (!primera) return;
  var i = 0;
  (function partir(nodo) {
    [].slice.call(nodo.childNodes).forEach(function (n) {
      if (n.nodeType === 1) return partir(n);
      if (n.nodeType !== 3) return;
      var frag = document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach(function (t) {
        if (!t) return;
        if (/^\s+$/.test(t)) return frag.appendChild(document.createTextNode(t));
        var s = document.createElement('span');
        s.className = 'w'; s.textContent = t; s.style.animationDelay = (120 + i++ * 85) + 'ms';
        frag.appendChild(s);
      });
      nodo.replaceChild(frag, n);
    });
  })(h);
  document.documentElement.classList.add('aur-in');
})();
