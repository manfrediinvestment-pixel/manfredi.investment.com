/* Panel de creador -- bloque "WhatsApp · Comunidad" (lo carga assets/panel/panel.js).
 * Se ve como el chat de la Comunidad en WhatsApp: los resúmenes del día (antes de la
 * apertura y al cierre) que arma el worker manfredi-whatsapp, cada uno como tarjeta-imagen
 * (1080x1350, dibujada en el navegador) + mensaje de texto, en el orden en que se publican.
 * Debajo de cada uno, compartir en 1 toque: en el celular abre el menú de compartir del
 * sistema -> WhatsApp -> el grupo de avisos.
 */
(function () {
  var C = { bg: '#0b1629', ink: '#f3f6fb', ch: '#e9d3a0', line: 'rgba(233,211,160,.22)', up: '#56c793', dn: '#ef7a6b' };
  var MOMENTOS = [
    { id: 'apertura', hora: '10:15', desde: 10 * 60 + 15 },
    { id: 'cierre', hora: '17:20', desde: 17 * 60 + 20 }
  ];
  var st = { el: null, get: null, base: '', datos: {}, blobs: {}, cargando: {} };

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  // *negrita* y _cursiva_ como las muestra WhatsApp
  function waHtml(t) {
    return esc(t).replace(/\*([^*\n]+)\*/g, '<b>$1</b>').replace(/(^|[\s(])_([^_\n]+)_/g, '$1<i>$2</i>').replace(/\n/g, '<br>');
  }
  function r1(c) { return Math.round(c * 10) / 10; }
  function pct(c) { return (r1(c) > 0 ? '+' : r1(c) < 0 ? '−' : '') + Math.abs(r1(c)).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function num(v, d) { if (d == null) d = Math.abs(v) >= 10000 ? 0 : 2; return v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function precio(f) { return f.u === 'pb' ? num(f.v, 0) + ' pb' : (f.u === '$' ? '$ ' : f.u ? f.u + ' ' : '') + num(f.v); }
  function variacion(f) {
    if (f.d != null) return { t: (f.d > 0 ? '+' : f.d < 0 ? '−' : '') + Math.abs(f.d) + ' pb', s: f.d > 0 ? -1 : f.d < 0 ? 1 : 0 }; // riesgo país: bajar es bueno
    return f.c == null ? { t: '', s: 0 } : { t: pct(f.c), s: r1(f.c) > 0 ? 1 : r1(f.c) < 0 ? -1 : 0 };
  }
  function minutosART() { var d = new Date(); return ((d.getUTCHours() + 21) % 24) * 60 + d.getUTCMinutes(); }
  function hhmm(iso) { return new Date(iso).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }); }
  var TILDES = '<svg class="wa-tick" viewBox="0 0 18 11" width="16" height="10" aria-hidden="true"><path d="M1 5.6l3 3L11 1.5M7.2 8.6L8 9.4 15.5 1.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // ---------- el chat ----------
  function esqueleto() {
    st.el.innerHTML =
      '<div class="wa-app">' +
        '<div class="wa-head">' +
          '<img class="wa-av" src="assets/img/icon-192.png" alt="">' +
          '<div class="wa-who"><b>Manfredi Investment · Mercados</b><span>Avisos · solo administradores</span></div>' +
        '</div>' +
        '<div class="wa-feed" id="waFeed">' +
          '<div class="wa-dia"><span>Hoy</span></div>' +
          MOMENTOS.map(function (m) { return '<div class="wa-msg" id="waMsg-' + m.id + '"></div>'; }).join('') +
        '</div>' +
        '<div class="wa-pie">Solo los administradores pueden enviar mensajes</div>' +
      '</div>' +
      '<p class="wa-nota">Así lo ven en la Comunidad. Debajo de cada resumen: <b>Tarjeta</b> y después <b>Texto</b> abren el menú de compartir del celular (WhatsApp → grupo de avisos). En la compu, la tarjeta se descarga y el texto abre WhatsApp Web.</p>';
    st.el.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-a]'); if (!b) return;
      var m = b.dataset.m;
      if (b.dataset.a === 'imagen') compartirImagen(m, b);
      else if (b.dataset.a === 'texto') compartirTexto(m);
      else if (b.dataset.a === 'copiar') copiar(m, b);
      else if (b.dataset.a === 'armar' || b.dataset.a === 'regenerar') cargar(m, true);
    });
  }

  function cargar(m, regenerar) {
    if (st.cargando[m]) return;
    st.cargando[m] = true;
    var box = document.getElementById('waMsg-' + m);
    box.innerHTML = '<div class="wa-bub wa-escribiendo">' + (regenerar ? 'Armando con los datos de este momento' : 'Cargando') + '<i></i><i></i><i></i></div>';
    st.get(st.base, '/wa/' + m + (regenerar ? '?regenerar=1' : '')).then(function (d) {
      st.datos[m] = d; pintar(m, d);
    }).catch(function (e) {
      box.innerHTML = '<div class="wa-bub"><p class="pn-err">No se pudo armar el resumen: ' + esc(e.message) + '</p></div>' + acciones(m, true);
    }).then(function () { st.cargando[m] = false; });
  }

  // El cierre todavía no pasó: en vez de mensaje, un aviso para armarlo antes si hace falta.
  function pendiente(m) {
    var mo = MOMENTOS.filter(function (x) { return x.id === m; })[0];
    document.getElementById('waMsg-' + m).innerHTML =
      '<div class="wa-aviso">El resumen del cierre se arma a las ' + mo.hora + ' · <button type="button" data-a="armar" data-m="' + m + '">Armarlo ahora</button></div>';
  }

  function pintar(m, d) {
    var hora = hhmm(d.generado);
    document.getElementById('waMsg-' + m).innerHTML =
      '<div class="wa-bub wa-img"><canvas id="waCv-' + m + '" width="1080" height="1350" aria-label="Tarjeta del resumen"></canvas>' +
        '<span class="wa-meta wa-meta-img">' + esc(hora) + TILDES + '</span></div>' +
      '<div class="wa-bub">' + waHtml(d.texto) + '<span class="wa-meta">' + esc(hora) + TILDES + '</span></div>' +
      acciones(m) +
      '<div class="wa-origen">' + (d.ia ? 'Introducción redactada con IA' : 'Introducción con plantilla (la IA no respondió)') + '</div>';
    dibujar(m, d);
    var feed = document.getElementById('waFeed'); if (feed) feed.scrollTop = feed.scrollHeight; // como WhatsApp: abre en lo último
  }

  function acciones(m, soloRegenerar) {
    var b = function (a, t, cls) { return '<button type="button" class="wa-btn' + (cls ? ' ' + cls : '') + '" data-a="' + a + '" data-m="' + m + '">' + t + '</button>'; };
    return '<div class="wa-acc">' + (soloRegenerar ? '' :
      b('imagen', '1 · Tarjeta', 'wa-main') + b('texto', '2 · Texto', 'wa-main') + b('copiar', 'Copiar')) +
      b('regenerar', '&#8635; Regenerar') + '</div>';
  }

  // ---------- tarjeta 1080x1350 ----------
  var logo = new Image(); logo.src = 'assets/img/icon-192.png';
  function dibujar(m, d) {
    var cv = document.getElementById('waCv-' + m); if (!cv) return;
    var x = cv.getContext('2d');
    var fuentes = ['400 64px "DM Serif Display"', '500 24px "IBM Plex Mono"', '400 32px "IBM Plex Sans"', '500 32px "IBM Plex Mono"'];
    Promise.all(fuentes.map(function (f) { return document.fonts ? document.fonts.load(f) : null; })).catch(function () {}).then(function () {
      var W = 1080, H = 1350, L = 84, R = W - 84;
      x.fillStyle = C.bg; x.fillRect(0, 0, W, H);
      var g = x.createRadialGradient(W * 0.85, 0, 0, W * 0.85, 0, 760);
      g.addColorStop(0, 'rgba(233,211,160,.13)'); g.addColorStop(1, 'rgba(233,211,160,0)');
      x.fillStyle = g; x.fillRect(0, 0, W, H);

      // encabezado
      if (logo.complete && logo.naturalWidth) x.drawImage(logo, L, 76, 58, 58);
      x.textBaseline = 'middle';
      x.fillStyle = C.ch; x.font = '500 22px "IBM Plex Mono"';
      spaced(x, 'MANFREDI INVESTMENT', L + 78, 105, 4);
      x.textAlign = 'right'; x.font = '500 22px "IBM Plex Mono"';
      x.fillText(d.fechaLarga.charAt(0).toUpperCase() + d.fechaLarga.slice(1), R, 105);
      x.textAlign = 'left';
      x.fillStyle = C.ink; x.font = '400 70px "DM Serif Display"';
      x.fillText(d.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado', L, 215);
      linea(x, L, R, 278);

      var y = 330;
      y = seccion(x, 'ARGENTINA', d.datos.argentina, L, R, y);
      y = seccion(x, d.momento === 'apertura' ? 'MUNDO · ÚLTIMO CIERRE' : 'MUNDO', d.datos.mundo, L, R, y + 24);

      // cierre: panel líder · apertura: agenda de hoy
      var extra = [];
      var p = d.datos.panel;
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
      // el PNG queda listo de antemano: Safari pide que share() salga directo del toque
      st.blobs[m] = null; cv.toBlob(function (b) { st.blobs[m] = b; }, 'image/png');
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
  var MOVIL = /Android|iPhone|iPad/i.test(navigator.userAgent);
  function compartirImagen(m, btn) {
    var d = st.datos[m], blob = st.blobs[m]; if (!d || !blob) return;
    var file = new File([blob], 'manfredi-' + d.momento + '-' + d.fecha + '.png', { type: 'image/png' });
    if (MOVIL && navigator.canShare && navigator.canShare({ files: [file] })) {
      navigator.share({ files: [file] }).catch(function () {});
    } else {
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = file.name; a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
      aviso(btn, 'Descargada');
    }
  }
  function compartirTexto(m) {
    var d = st.datos[m]; if (!d) return;
    if (MOVIL && navigator.share) navigator.share({ text: d.texto }).catch(function () {});
    else window.open('https://wa.me/?text=' + encodeURIComponent(d.texto), '_blank', 'noopener');
  }
  function copiar(m, btn) {
    var d = st.datos[m]; if (!d || !navigator.clipboard) return;
    navigator.clipboard.writeText(d.texto).then(function () { aviso(btn, 'Copiado'); });
  }
  function aviso(btn, t) { var o = btn.innerHTML; btn.textContent = t; setTimeout(function () { btn.innerHTML = o; }, 1600); }

  // ---------- estilos (colores de WhatsApp en modo oscuro; sin texto gris) ----------
  function estilos() {
    if (document.getElementById('waCss')) return;
    var s = document.createElement('style'); s.id = 'waCss';
    s.textContent =
      '.wa-app{max-width:620px;margin:0 auto;border-radius:12px;overflow:hidden;border:1px solid rgba(233,211,160,.14);background:#0b141a;font-family:"IBM Plex Sans",system-ui,sans-serif;color:#e9edef}' +
      '.wa-head{display:flex;align-items:center;gap:12px;padding:10px 16px;background:#202c33}' +
      '.wa-av{width:40px;height:40px;border-radius:50%;object-fit:cover}' +
      '.wa-who{display:grid;gap:2px;min-width:0}.wa-who b{font-size:15.5px;font-weight:500;color:#e9edef}.wa-who span{font-size:12.5px;color:#e9edef}' +
      '.wa-feed{height:640px;overflow-y:auto;padding:14px 5% 18px;display:flex;flex-direction:column;gap:6px;' +
        'background-color:#0b141a;background-image:radial-gradient(rgba(233,237,239,.035) 1px,transparent 1px);background-size:18px 18px}' +
      '.wa-dia{align-self:center;margin:4px 0 8px}.wa-dia span{display:inline-block;padding:5px 12px;border-radius:8px;background:#182229;font-size:12.5px;color:#e9edef}' +
      '.wa-msg{display:flex;flex-direction:column;align-items:flex-end;gap:4px}.wa-msg:empty{display:none}.wa-msg + .wa-msg{margin-top:14px}' +
      '.wa-bub{position:relative;max-width:88%;padding:7px 9px 8px;border-radius:8px 0 8px 8px;background:#005c4b;font-size:14.2px;line-height:1.45;overflow-wrap:anywhere;box-shadow:0 1px .5px rgba(0,0,0,.13)}' +
      '.wa-bub + .wa-bub{border-radius:8px}' +
      '.wa-bub .wa-meta{float:right;margin:6px 0 -4px 12px;font-size:11px;line-height:15px;color:#e9edef;display:inline-flex;align-items:center;gap:3px}' +
      '.wa-tick{color:#53bdeb}' +
      '.wa-img{padding:3px}.wa-img canvas{display:block;width:300px;max-width:100%;height:auto;border-radius:6px}' +
      '.wa-meta-img{position:absolute;right:10px;bottom:8px;float:none!important;margin:0!important;padding:1px 6px;border-radius:8px;background:rgba(11,20,26,.55)}' +
      '.wa-escribiendo{font-size:13.5px}.wa-escribiendo i{display:inline-block;width:5px;height:5px;margin-left:4px;border-radius:50%;background:#e9edef;animation:waP 1.2s infinite}' +
      '.wa-escribiendo i:nth-child(2){animation-delay:.2s}.wa-escribiendo i:nth-child(3){animation-delay:.4s}' +
      '@keyframes waP{0%,60%,100%{opacity:.25}30%{opacity:1}}' +
      '@media (prefers-reduced-motion:reduce){.wa-escribiendo i{animation:none}}' +
      '.wa-aviso{align-self:center;padding:6px 12px;border-radius:8px;background:#182229;font-size:12.5px;color:#e9edef;text-align:center}' +
      '.wa-aviso button{border:0;background:none;padding:0;color:#e9d3a0;font:inherit;text-decoration:underline;cursor:pointer}' +
      '.wa-acc{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px;margin-top:2px}' +
      '.wa-btn{padding:5px 11px;border-radius:14px;border:1px solid rgba(233,211,160,.3);background:#111b21;color:#e9edef;font:500 12px "IBM Plex Sans",sans-serif;cursor:pointer;transition:background .2s}' +
      '.wa-btn.wa-main{border-color:#e9d3a0;color:#e9d3a0}' +
      '@media (hover:hover){.wa-btn:hover{background:#1c2a32}}' +
      '.wa-origen{font:500 10.5px "IBM Plex Mono",monospace;letter-spacing:.06em;color:#e9d3a0}' +
      '.wa-pie{padding:13px 16px;background:#202c33;text-align:center;font-size:13px;color:#e9edef}' +
      '.wa-nota{max-width:620px;margin:12px auto 0;font:400 12.5px/1.5 "IBM Plex Sans",sans-serif;color:#f3f6fb}' +
      '@media (max-width:640px){.wa-feed{height:560px;padding:12px 3% 16px}.wa-bub{max-width:94%}}';
    document.head.appendChild(s);
  }

  window.pnWhatsapp = function (el, get, base) {
    st = { el: el, get: get, base: base, datos: {}, blobs: {}, cargando: {} };
    estilos(); esqueleto();
    var ahora = minutosART();
    MOMENTOS.forEach(function (m) {
      if (m.id === 'apertura' || ahora >= m.desde) cargar(m.id, false);
      else pendiente(m.id);
    });
  };
})();
