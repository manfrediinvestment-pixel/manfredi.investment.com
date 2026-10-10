/* Postularse como analista: antes de abrir el mail, un cartel con los pasos.
   Lo abre cualquier link con [data-postular] (anuncio de la home, cartel de
   Análisis e informes, invitación del costado). Si este archivo no carga, el
   link sigue siendo un mailto común. Estilos en assets/analistas/analistas.css. */
(function () {
  var MAIL = 'manfredi.investment@gmail.com';
  var ASUNTO = 'Quiero publicar en Manfredi';
  var CUERPO = 'Nombre:\nLinkedIn o redes:\nTemas que analizás:\nLink o PDF de un análisis tuyo:\n';
  var HREF = 'mailto:' + MAIL + '?subject=' + encodeURIComponent(ASUNTO) + '&body=' + encodeURIComponent(CUERPO);
  var box = null, antes = null;

  function armar() {
    box = document.createElement('div');
    box.className = 'pst';
    box.hidden = true;
    box.innerHTML =
      '<div class="pst__card" role="dialog" aria-modal="true" aria-labelledby="pstT">' +
        '<div class="pst__in">' +
          '<button type="button" class="pst__x" aria-label="Cerrar">&times;</button>' +
          '<span class="pst__k"><i></i>Postulación</span>' +
          '<h3 class="pst__t" id="pstT">Cómo <em>postularte</em></h3>' +
          '<ol class="pst__pasos">' +
            '<li><b>01</b><span><strong>Escribinos un mail</strong>a <button type="button" class="pst__mail" data-copiar>' + MAIL + '</button></span></li>' +
            '<li><b>02</b><span><strong>Contanos quién sos</strong>Tu nombre, tu LinkedIn o redes y los temas que analizás.</span></li>' +
            '<li><b>03</b><span><strong>Mandanos un análisis tuyo</strong>En PDF o con un link. Puede ser uno que ya hayas publicado.</span></li>' +
          '</ol>' +
          '<div class="pst__acc">' +
            '<a class="pst__gold" href="' + HREF + '">Escribir el mail</a>' +
            '<button type="button" class="pst__copy" data-copiar><span>Copiar la dirección</span></button>' +
          '</div>' +
          '<span class="pst__f">Elegimos entre 5 y 10 analistas para la primera convocatoria</span>' +
        '</div>' +
      '</div>';
    document.body.appendChild(box);
    box.addEventListener('click', function (e) {
      if (e.target === box || e.target.closest('.pst__x')) { cerrar(); return; }
      var c = e.target.closest('[data-copiar]');
      if (c) copiar();
    });
  }
  function copiar() {
    var listo = function () {
      var b = box.querySelector('.pst__copy');
      b.classList.add('ok'); b.firstChild.textContent = 'Dirección copiada';
      setTimeout(function () { b.classList.remove('ok'); b.firstChild.textContent = 'Copiar la dirección'; }, 2200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(MAIL).then(listo, function () { viejo(); listo(); });
    else { viejo(); listo(); }
  }
  function viejo() {
    var t = document.createElement('textarea'); t.value = MAIL; t.style.position = 'fixed'; t.style.opacity = '0';
    document.body.appendChild(t); t.select(); try { document.execCommand('copy'); } catch (e) {} t.remove();
  }
  function abrir() {
    if (!box) armar();
    antes = document.activeElement;
    box.hidden = false;
    requestAnimationFrame(function () { box.classList.add('on'); box.querySelector('.pst__gold').focus({ preventScroll: true }); });
    document.documentElement.style.overflow = 'hidden';
  }
  function cerrar() {
    box.classList.remove('on');
    document.documentElement.style.overflow = '';
    setTimeout(function () { box.hidden = true; }, 220);
    if (antes && antes.focus) antes.focus({ preventScroll: true });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-postular]');
    if (!a) return;
    e.preventDefault();
    abrir();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && box && !box.hidden) cerrar(); });
  window.miPostular = abrir;
})();
