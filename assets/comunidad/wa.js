/* Comunidad de WhatsApp.
 * - MI_WA_COMUNIDAD: link de invitación del grupo (https://chat.whatsapp.com/...). Vacío = "Muy pronto".
 *   Es el único lugar donde se carga: lo usan este cuadro y el chat (assets/comunidad/chat.js).
 * - Cuadro de la home (#waCard, en el lugar del Pulso del día): el grupo con el último resumen
 *   real como vista previa (worker manfredi-comunidad, sala "gratis") y el botón para unirse. */
window.MI_WA_COMUNIDAD = '';

(function () {
  'use strict';
  var API = 'https://manfredi-comunidad.nachito2502.workers.dev';
  var IC_WA = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2Zm0 18.15a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.23 8.23 0 1 1 6.98 3.86Zm4.52-6.16c-.25-.12-1.47-.72-1.7-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.16.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28Z"/></svg>';
  var IC_TICKS = '<svg viewBox="0 0 16 11" width="15" height="11" aria-hidden="true"><path d="M1 5.6 4 8.6 10.6 2M6 8.6 7.2 9.8 14.6 2.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function hora(ms) { return new Date(ms).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Argentina/Buenos_Aires' }); }
  function dia(ms) {
    var f = function (d) { return new Date(d).toLocaleDateString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' }); };
    if (f(ms) === f(Date.now())) return 'Hoy';
    if (f(ms) === f(Date.now() - 864e5)) return 'Ayer';
    return new Date(ms).toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', timeZone: 'America/Argentina/Buenos_Aires' });
  }
  // Horarios de hoy (cambian con el horario de verano de Nueva York): los sabe tarjeta.js.
  function horarios() {
    try { var h = window.MiTarjeta && window.MiTarjeta.horarios(new Date()); if (h && h.apertura) return [h.apertura.hora, h.cierre.hora]; } catch (e) {}
    return ['11:00', '18:30'];
  }

  function burbuja(m) {
    if (!m) return '<div class="wa-msg wa-msg--skel" aria-hidden="true"><i></i><i></i><i></i></div>';
    var r = m.datos || {};
    var titulo = r.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado';
    var texto = r.clave || String(r.intro || '').split('. ')[0];
    return '<div class="wa-dia"><span>' + esc(dia(m.creado)) + '</span></div>' +
      '<div class="wa-msg">' +
        '<b class="wa-msg-k">Manfredi · ' + titulo + '</b>' +
        '<p>' + esc(texto) + '</p>' +
        '<span class="wa-msg-t">' + hora(m.creado) + IC_TICKS + '</span>' +
      '</div>';
  }

  function pintar(card, m) {
    var link = window.MI_WA_COMUNIDAD, hs = horarios();
    card.innerHTML =
      '<div class="wa-hd">' +
        '<img class="wa-av" src="assets/img/logo-mark-512.png" alt="" width="44" height="44">' +
        '<div class="wa-hd-t"><b>Comunidad Manfredi</b><span>Grupo de WhatsApp · Gratis</span></div>' +
        '<span class="wa-ic" aria-hidden="true">' + IC_WA + '</span>' +
      '</div>' +
      '<div class="wa-feed">' + burbuja(m) + '</div>' +
      '<ul class="wa-pts">' +
        '<li><time>' + hs[0] + '</time><span>Resumen antes de la apertura</span></li>' +
        '<li><time>' + hs[1] + '</time><span>Resumen del cierre del mercado</span></li>' +
        '<li><time>Sin spam</time><span>Solo los administradores publican</span></li>' +
      '</ul>' +
      (link
        ? '<a class="wa-btn" href="' + esc(link) + '" target="_blank" rel="noopener">' + IC_WA + '<span>Unirme al grupo</span></a>'
        : '<span class="wa-btn wa-btn--pronto" aria-disabled="true">' + IC_WA + '<span>Unirme al grupo · Muy pronto</span></span>');
  }

  function iniciar() {
    var card = document.getElementById('waCard');
    if (!card) return;
    pintar(card, null);
    fetch(API + '/chat/gratis').then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      var lista = (d && d.mensajes) || [], m = null;
      for (var i = lista.length - 1; i >= 0; i--) if (lista[i].tipo === 'resumen' && !lista[i].borrado) { m = lista[i]; break; }
      if (m && typeof m.datos === 'string') { try { m.datos = JSON.parse(m.datos); } catch (e) { m = null; } }
      if (m) pintar(card, m); else card.querySelector('.wa-feed').remove();
    }).catch(function () { var f = card.querySelector('.wa-feed'); if (f) f.remove(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
