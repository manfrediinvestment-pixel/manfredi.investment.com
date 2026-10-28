/* Tarjeta del resumen del día (1080x1350) -- la misma en el chat de Manfredi Pro
 * (assets/comunidad/chat.js), en el Panel de creador (assets/panel/whatsapp.js) y en WhatsApp.
 * Se dibuja en el navegador con los datos que arma el worker manfredi-comunidad.
 *
 * window.MiTarjeta.dibujar(canvas, resumen) -> Promise<Blob PNG>
 * window.MiTarjeta.compartirImagen(blob, resumen, texto?) / .compartirTexto(texto)
 * window.MiTarjeta.waHtml(texto, conLinks)  -> el formato de WhatsApp en HTML
 * window.MiTarjeta.epigrafe(resumen, id)     -> lo que acompaña a la tarjeta en WhatsApp
 * window.MiTarjeta.horarios(fecha)          -> a qué hora (Argentina) sale cada resumen ese día
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
    document.fonts ? Promise.all(['400 64px "DM Serif Display"', '600 24px "IBM Plex Mono"', '500 32px "IBM Plex Sans"', '600 32px "IBM Plex Mono"'].map(function (f) { return document.fonts.load(f); })) : null,
    new Promise(function (ok) { if (logo.complete) ok(); else { logo.onload = logo.onerror = ok; } })
  ]).catch(function () {});

  // ---------- formato de WhatsApp en HTML ----------
  // *negrita*, _cursiva_, > cita, - lista y ```bloque de ancho fijo``` (las tablas de cotizaciones).
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function enLinea(t, links) {
    var h = esc(t).replace(/\*([^*\n]+)\*/g, '<b>$1</b>').replace(/(^|[\s(])_([^_\n]+)_/g, '$1<i>$2</i>');
    if (links) h = h.replace(/(https?:\/\/[^\s<]+|\bmanfredinvestment\.com\b)/g, function (u) {
      return '<a href="' + (/^http/.test(u) ? u : 'https://' + u) + '" target="_blank" rel="noopener">' + u + '</a>';
    });
    return h;
  }
  function waHtml(texto, links) {
    var partes = String(texto || '').split('```'), html = '';
    partes.forEach(function (parte, i) {
      if (i % 2) { html += '<pre class="wa-mono">' + esc(parte.replace(/^\n|\n$/g, '')) + '</pre>'; return; }
      var lineas = parte.split('\n'), lista = false;
      lineas.forEach(function (l, j) {
        var esLista = /^- /.test(l);
        if (esLista && !lista) { html += '<ul class="wa-lista">'; lista = true; }
        if (!esLista && lista) { html += '</ul>'; lista = false; }
        if (esLista) html += '<li>' + enLinea(l.slice(2), links) + '</li>';
        else if (/^> /.test(l)) html += '<blockquote class="wa-cita">' + enLinea(l.slice(2), links) + '</blockquote>';
        else if (l.trim()) html += enLinea(l, links) + ((lineas[j + 1] || '').trim() && !/^(- |> )/.test(lineas[j + 1]) ? '<br>' : '');
        else if (j > 0 && j < lineas.length - 1) html += '<span class="wa-sep"></span>';
      });
      if (lista) html += '</ul>';
    });
    return html;
  }

  // ---------- horario de los resúmenes (el de Wall Street, en hora argentina) ----------
  // 30 min antes de la apertura (9:00 NY) y 30 min después del cierre (16:30 NY; 13:30 los días
  // de cierre temprano). Mismas fechas que workers/comunidad (NYSE_FERIADOS / NYSE_MEDIO_DIA).
  var FERIADOS = ['2026-11-26', '2026-12-25', '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24'];
  var MEDIO_DIA = ['2026-11-27', '2026-12-24', '2027-11-26'];
  function horarios(fecha) {
    var iso = new Date(fecha.getTime() - 3 * 3600e3).toISOString().slice(0, 10);
    var dia = new Date(iso + 'T15:00:00Z');
    var nyHora = +new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', hourCycle: 'h23' }).format(dia);
    var dif = 12 - nyHora;                       // 15:00 UTC = 12:00 en Argentina: horas que va adelantada a NY (1 o 2)
    var wd = dia.getUTCDay(), cierreNY = MEDIO_DIA.indexOf(iso) > -1 ? 13 * 60 + 30 : 16 * 60 + 30;
    var hm = function (m) { return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); };
    var ap = 9 * 60 + dif * 60, ci = cierreNY + dif * 60;
    return { iso: iso, hay: wd !== 0 && wd !== 6 && FERIADOS.indexOf(iso) < 0,
      apertura: { min: ap, hora: hm(ap) }, cierre: { min: ci, hora: hm(ci) } };
  }

  // ---------- epígrafe ----------
  // En WhatsApp va un solo mensaje, como se ve en la página: la tarjeta y, abajo, el título, la
  // clave y el párrafo. El link abre el chat de la página justo en este resumen (tablas, bonos,
  // agenda y titulares completos).
  function epigrafe(d, id) {
    var fecha = d.fechaLarga.charAt(0).toUpperCase() + d.fechaLarga.slice(1);
    var out = ['*MANFREDI · ' + (d.momento === 'apertura' ? 'ANTES DE LA APERTURA' : 'CIERRE DEL MERCADO') + '*', '_' + fecha + '_', ''];
    if (d.clave) out.push('> *' + d.clave + '*', '');
    out.push(d.intro, '', 'El resumen completo, con bonos, agenda y titulares:', 'manfredinvestment.com/' + (id ? '?r=' + id : '') + '#pro');
    return out.join('\n');
  }

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
      x.fillStyle = C.ch; x.font = '600 24px "IBM Plex Mono"';
      spaced(x, 'MANFREDI INVESTMENT', L + 78, 105, 4);
      x.textAlign = 'right';
      x.fillText(d.fechaLarga.charAt(0).toUpperCase() + d.fechaLarga.slice(1), R, 105);
      x.textAlign = 'left';
      x.fillStyle = C.ink; x.font = '400 70px "DM Serif Display"';
      x.fillText(d.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado', L, 215);
      var y = 278;
      if (d.clave) {
        // la clave del día, en hasta 2 líneas
        x.font = '500 32px "IBM Plex Sans"'; x.fillStyle = C.ch;
        var lineas = partir(x, d.clave, R - L).slice(0, 2);
        lineas.forEach(function (t, i) { x.fillText(t, L, 282 + i * 42); });
        y = 282 + lineas.length * 42 + 8;
      }
      linea(x, L, R, y);

      y += 52;
      y = seccion(x, d.momento === 'apertura' ? 'ARGENTINA · ÚLTIMO CIERRE' : 'ARGENTINA', d.datos.argentina, L, R, y);
      y = seccion(x, d.momento === 'apertura' ? 'MUNDO · ÚLTIMO CIERRE' : 'MUNDO', d.datos.mundo, L, R, y + 20);

      // cierre: panel líder · apertura: agenda de hoy
      var extra = [], p = d.datos.panel;
      if (p) {
        if (p.suben.length) extra.push({ k: 'SUBEN', v: p.suben.map(function (a) { return a.n + ' ' + pct(a.c); }).join('   '), c: C.up });
        if (p.bajan.length) extra.push({ k: 'BAJAN', v: p.bajan.map(function (a) { return a.n + ' ' + pct(a.c); }).join('   '), c: C.dn });
      } else if (d.datos.agenda.eventos.length) {
        d.datos.agenda.eventos.slice(0, 2).forEach(function (e, i) { extra.push({ k: i ? '' : 'HOY', v: cortar(x, e.t, R - L - 150, '500 28px "IBM Plex Sans"'), c: C.ink, sans: true }); });
      }
      if (extra.length) {
        y += 18; linea(x, L, R, y); y += 46;
        extra.forEach(function (e) {
          x.fillStyle = C.ch; x.font = '600 23px "IBM Plex Mono"'; spaced(x, e.k, L, y, 3);
          x.fillStyle = e.c; x.font = e.sans ? '500 28px "IBM Plex Sans"' : '600 29px "IBM Plex Mono"'; x.fillText(e.v, L + 150, y);
          y += 50;
        });
      }

      // pie
      linea(x, L, R, H - 112);
      x.fillStyle = C.ch; x.font = '600 24px "IBM Plex Mono"'; spaced(x, 'MANFREDINVESTMENT.COM', L, H - 70, 3);
      x.textAlign = 'right'; x.fillStyle = C.ink; x.font = '500 24px "IBM Plex Sans"';
      x.fillText('Cotizaciones en vivo · Comunidad gratis', R, H - 70);
      x.textAlign = 'left';
      return new Promise(function (ok) { cv.toBlob(ok, 'image/png'); });
    });
  }
  function seccion(x, titulo, filas, L, R, y) {
    x.fillStyle = C.ch; x.font = '600 23px "IBM Plex Mono"'; spaced(x, titulo, L, y, 3);
    y += 50;
    filas.forEach(function (f) {
      var v = variacion(f);
      x.fillStyle = C.ink; x.font = '500 34px "IBM Plex Sans"'; x.textAlign = 'left'; x.fillText(f.n, L, y);
      x.font = '600 33px "IBM Plex Mono"'; x.textAlign = 'right'; x.fillText(precio(f), R - 200, y);
      x.fillStyle = v.s > 0 ? C.up : v.s < 0 ? C.dn : C.ink; x.fillText(v.t, R, y);
      x.textAlign = 'left';
      y += 50;
    });
    return y;
  }
  function linea(x, L, R, y) { x.strokeStyle = C.line; x.lineWidth = 1.5; x.beginPath(); x.moveTo(L, y); x.lineTo(R, y); x.stroke(); }
  function spaced(x, t, px, py, sp) { for (var i = 0; i < t.length; i++) { x.fillText(t[i], px, py); px += x.measureText(t[i]).width + sp; } }
  function partir(x, t, max) {
    var out = [], l = '';
    t.split(' ').forEach(function (w) { var p = l ? l + ' ' + w : w; if (x.measureText(p).width > max && l) { out.push(l); l = w; } else l = p; });
    if (l) out.push(l);
    return out;
  }
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
    if (texto && navigator.clipboard) navigator.clipboard.writeText(texto).catch(function () {});
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

  window.MiTarjeta = { dibujar: dibujar, compartirImagen: compartirImagen, compartirTexto: compartirTexto, waHtml: waHtml, horarios: horarios, epigrafe: epigrafe, movil: MOVIL };
})();
