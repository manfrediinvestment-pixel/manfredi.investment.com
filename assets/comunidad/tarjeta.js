/* Tarjeta del resumen del día (1080x1350) -- la misma en el chat de Manfredi Pro
 * (assets/comunidad/chat.js), en el Panel de creador (assets/panel/whatsapp.js) y en WhatsApp.
 * Se dibuja en el navegador con los datos que arma el worker manfredi-comunidad.
 *
 * window.MiTarjeta.dibujar(canvas, resumen) -> Promise<Blob PNG>
 * window.MiTarjeta.compartirImagen(blob, resumen, texto?) / .compartirTexto(texto)
 */
(function () {
  if (window.MiTarjeta) return;
  var C = { bg: '#0b1629', ink: '#f3f6fb', ch: '#e9d3a0', line: 'rgba(233,211,160,.22)', up: '#56c793', dn: '#ef7a6b' };
  var MOVIL = /Android|iPhone|iPad/i.test(navigator.userAgent);

  function r1(c) { return Math.round(c * 10) / 10; }
  function pct(c) { return (r1(c) > 0 ? '+' : r1(c) < 0 ? '−' : '') + Math.abs(r1(c)).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function num(v, d) { if (d == null) d = Math.abs(v) >= 10000 ? 0 : 2; return v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function precio(f) { return f.u === 'pb' ? num(f.v, 0) + ' pb' : (f.u === '$' ? '$ ' : f.u ? f.u + ' ' : '') + num(f.v); }
  function variacion(f) {
    if (f.d != null) return { t: (f.d > 0 ? '+' : f.d < 0 ? '−' : '') + Math.abs(f.d) + ' pb', s: f.d > 0 ? -1 : f.d < 0 ? 1 : 0 }; // riesgo país: bajar es bueno
    return f.c == null ? { t: '', s: 0 } : { t: pct(f.c), s: r1(f.c) > 0 ? 1 : r1(f.c) < 0 ? -1 : 0 };
  }

  var logo = new Image(); logo.src = 'assets/img/icon-192.png';
  var listo = Promise.all([
    document.fonts ? Promise.all(['400 64px "DM Serif Display"', '500 24px "IBM Plex Mono"', '400 32px "IBM Plex Sans"', '500 32px "IBM Plex Mono"'].map(function (f) { return document.fonts.load(f); })) : null,
    new Promise(function (ok) { if (logo.complete) ok(); else { logo.onload = logo.onerror = ok; } })
  ]).catch(function () {});

  function dibujar(cv, d) {
    return listo.then(function () {
      var x = cv.getContext('2d'), W = 1080, H = 1350, L = 84, R = W - 84;
      x.fillStyle = C.bg; x.fillRect(0, 0, W, H);
      var g = x.createRadialGradient(W * 0.85, 0, 0, W * 0.85, 0, 760);
      g.addColorStop(0, 'rgba(233,211,160,.13)'); g.addColorStop(1, 'rgba(233,211,160,0)');
      x.fillStyle = g; x.fillRect(0, 0, W, H);

      // encabezado
      if (logo.naturalWidth) x.drawImage(logo, L, 76, 58, 58);
      x.textBaseline = 'middle'; x.textAlign = 'left';
      x.fillStyle = C.ch; x.font = '500 22px "IBM Plex Mono"';
      spaced(x, 'MANFREDI INVESTMENT', L + 78, 105, 4);
      x.textAlign = 'right';
      x.fillText(d.fechaLarga.charAt(0).toUpperCase() + d.fechaLarga.slice(1), R, 105);
      x.textAlign = 'left';
      x.fillStyle = C.ink; x.font = '400 70px "DM Serif Display"';
      x.fillText(d.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado', L, 215);
      linea(x, L, R, 278);

      var y = 330;
      y = seccion(x, 'ARGENTINA', d.datos.argentina, L, R, y);
      y = seccion(x, d.momento === 'apertura' ? 'MUNDO · ÚLTIMO CIERRE' : 'MUNDO', d.datos.mundo, L, R, y + 24);

      // cierre: panel líder · apertura: agenda de hoy
      var extra = [], p = d.datos.panel;
      if (p) {
        if (p.suben.length) extra.push({ k: 'SUBEN', v: p.suben.map(function (a) { return a.n + ' ' + pct(a.c); }).join('   '), c: C.up });
        if (p.bajan.length) extra.push({ k: 'BAJAN', v: p.bajan.map(function (a) { return a.n + ' ' + pct(a.c); }).join('   '), c: C.dn });
      } else if (d.datos.agenda.eventos.length) {
        d.datos.agenda.eventos.slice(0, 2).forEach(function (e, i) { extra.push({ k: i ? '' : 'HOY', v: cortar(x, e.t, R - L - 150, '400 26px "IBM Plex Sans"'), c: C.ink, sans: true }); });
      }
      if (extra.length) {
        y += 18; linea(x, L, R, y); y += 46;
        extra.forEach(function (e) {
          x.fillStyle = C.ch; x.font = '500 20px "IBM Plex Mono"'; spaced(x, e.k, L, y, 3);
          x.fillStyle = e.c; x.font = e.sans ? '400 26px "IBM Plex Sans"' : '500 27px "IBM Plex Mono"'; x.fillText(e.v, L + 150, y);
          y += 50;
        });
      }

      // pie
      linea(x, L, R, H - 112);
      x.fillStyle = C.ch; x.font = '500 22px "IBM Plex Mono"'; spaced(x, 'MANFREDINVESTMENT.COM', L, H - 70, 3);
      x.textAlign = 'right'; x.fillStyle = C.ink; x.font = '400 22px "IBM Plex Sans"';
      x.fillText('Cotizaciones en vivo · Comunidad gratis', R, H - 70);
      x.textAlign = 'left';
      return new Promise(function (ok) { cv.toBlob(ok, 'image/png'); });
    });
  }
  function seccion(x, titulo, filas, L, R, y) {
    x.fillStyle = C.ch; x.font = '500 20px "IBM Plex Mono"'; spaced(x, titulo, L, y, 3);
    y += 50;
    filas.forEach(function (f) {
      var v = variacion(f);
      x.fillStyle = C.ink; x.font = '400 31px "IBM Plex Sans"'; x.textAlign = 'left'; x.fillText(f.n, L, y);
      x.font = '500 31px "IBM Plex Mono"'; x.textAlign = 'right'; x.fillText(precio(f), R - 190, y);
      x.fillStyle = v.s > 0 ? C.up : v.s < 0 ? C.dn : C.ink; x.fillText(v.t, R, y);
      x.textAlign = 'left';
      y += 54;
    });
    return y;
  }
  function linea(x, L, R, y) { x.strokeStyle = C.line; x.lineWidth = 1.5; x.beginPath(); x.moveTo(L, y); x.lineTo(R, y); x.stroke(); }
  function spaced(x, t, px, py, sp) { for (var i = 0; i < t.length; i++) { x.fillText(t[i], px, py); px += x.measureText(t[i]).width + sp; } }
  function cortar(x, t, max, font) {
    x.font = font; if (x.measureText(t).width <= max) return t;
    while (t.length && x.measureText(t + '…').width > max) t = t.slice(0, -1);
    return t.trim() + '…';
  }

  // ---------- compartir ----------
  // En el celular abre el menú del sistema (WhatsApp, Instagram…); en la compu descarga la
  // tarjeta. El blob tiene que estar listo antes del toque: Safari pide que share() salga directo.
  function compartirImagen(blob, d, texto) {
    if (!blob) return Promise.resolve('sin');
    var file = new File([blob], 'manfredi-' + d.momento + '-' + d.fecha + '.png', { type: 'image/png' });
    if (MOVIL && navigator.canShare && navigator.canShare({ files: [file] })) {
      return navigator.share(texto ? { files: [file], text: texto } : { files: [file] }).then(function () { return 'ok'; }, function () { return 'cancelado'; });
    }
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = file.name; a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    return Promise.resolve('descargada');
  }
  function compartirTexto(texto) {
    if (MOVIL && navigator.share) return navigator.share({ text: texto }).catch(function () {});
    window.open('https://wa.me/?text=' + encodeURIComponent(texto), '_blank', 'noopener');
  }

  window.MiTarjeta = { dibujar: dibujar, compartirImagen: compartirImagen, compartirTexto: compartirTexto, movil: MOVIL };
})();
