/* Panel de creador -- bloque "WhatsApp · Comunidad" (lo carga assets/panel/panel.js).
 * Muestra el resumen de apertura o de cierre que arma el worker manfredi-whatsapp,
 * dibuja la tarjeta-imagen (1080x1350, en el navegador) y lo comparte en 1 toque:
 * en el celular abre el menú de compartir del sistema -> WhatsApp -> la Comunidad.
 */
(function () {
  var C = { bg: '#0b1629', bg2: '#0e1c35', ink: '#f3f6fb', ch: '#e9d3a0', line: 'rgba(233,211,160,.22)', up: '#56c793', dn: '#ef7a6b' };
  var st = { el: null, get: null, base: '', momento: null, datos: {}, cargando: false };

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
  function momentoPorHora() { var h = new Date().getUTCHours() - 3; return h >= 14 || h < 0 ? 'cierre' : 'apertura'; }

  // ---------- estructura ----------
  function esqueleto() {
    st.el.innerHTML =
      '<div class="wa-top">' +
        '<div class="wa-tabs" role="tablist">' +
          '<button type="button" data-m="apertura">Antes de la apertura</button>' +
          '<button type="button" data-m="cierre">Cierre</button>' +
        '</div>' +
        '<span class="wa-estado" id="waEstado"></span>' +
      '</div>' +
      '<div class="wa-grid">' +
        '<div class="wa-col"><div class="wa-sub">Tarjeta</div><canvas class="wa-card" id="waCanvas" width="1080" height="1350" aria-label="Tarjeta del resumen"></canvas></div>' +
        '<div class="wa-col"><div class="wa-sub">Mensaje</div><div class="wa-chat"><div class="wa-bubble" id="waBubble"><div class="pn-loading">Cargando…</div></div></div></div>' +
      '</div>' +
      '<div class="wa-acciones">' +
        '<button type="button" class="wa-btn wa-main" data-a="imagen">1 · Compartir tarjeta</button>' +
        '<button type="button" class="wa-btn wa-main" data-a="texto">2 · Compartir texto</button>' +
        '<button type="button" class="wa-btn" data-a="copiar">Copiar texto</button>' +
        '<button type="button" class="wa-btn" data-a="regenerar">&#8635; Regenerar</button>' +
      '</div>' +
      '<p class="wa-nota">En el celular, cada botón abre el menú de compartir: elegí WhatsApp y después el grupo de avisos de la Comunidad. En la compu, la tarjeta se descarga y el texto abre WhatsApp Web.</p>';
    st.el.addEventListener('click', function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      if (b.dataset.m) mostrar(b.dataset.m, false);
      else if (b.dataset.a === 'imagen') compartirImagen(b);
      else if (b.dataset.a === 'texto') compartirTexto();
      else if (b.dataset.a === 'copiar') copiar(b);
      else if (b.dataset.a === 'regenerar') mostrar(st.momento, true);
    });
  }

  function mostrar(m, regenerar) {
    if (st.cargando) return;
    st.momento = m;
    [].forEach.call(st.el.querySelectorAll('.wa-tabs button'), function (b) { b.setAttribute('aria-selected', b.dataset.m === m ? 'true' : 'false'); });
    if (st.datos[m] && !regenerar) return pintar(st.datos[m]);
    st.cargando = true;
    document.getElementById('waBubble').innerHTML = '<div class="pn-loading">' + (regenerar ? 'Generando con datos de este momento…' : 'Cargando…') + '</div>';
    document.getElementById('waEstado').textContent = '';
    st.get(st.base, '/wa/' + m + (regenerar ? '?regenerar=1' : '')).then(function (d) {
      st.datos[m] = d; pintar(d);
    }).catch(function (e) {
      document.getElementById('waBubble').innerHTML = '<p class="pn-err">No se pudo armar el resumen: ' + esc(e.message) + '</p>';
    }).then(function () { st.cargando = false; });
  }

  function pintar(d) {
    document.getElementById('waBubble').innerHTML = waHtml(d.texto);
    var hora = new Date(d.generado).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    document.getElementById('waEstado').innerHTML = 'Datos de las ' + esc(hora) + ' · ' + (d.ia ? 'redactado con IA' : 'plantilla (la IA no respondió)');
    dibujar(d);
  }

  // ---------- tarjeta 1080x1350 ----------
  var logo = new Image(); logo.src = 'assets/img/icon-192.png';
  function dibujar(d) {
    var cv = document.getElementById('waCanvas'), x = cv.getContext('2d');
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
      st.blob = null; cv.toBlob(function (b) { st.blob = b; }, 'image/png');
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
  function actual() { return st.datos[st.momento]; }
  function nombreArchivo(d) { return 'manfredi-' + d.momento + '-' + d.fecha + '.png'; }
  function compartirImagen(btn) {
    var d = actual(), blob = st.blob; if (!d || !blob) return;
    var file = new File([blob], nombreArchivo(d), { type: 'image/png' });
    if (navigator.canShare && navigator.canShare({ files: [file] }) && /Android|iPhone|iPad/i.test(navigator.userAgent)) {
      navigator.share({ files: [file] }).catch(function () {});
    } else {
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = file.name; a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
      aviso(btn, 'Descargada');
    }
  }
  function compartirTexto() {
    var d = actual(); if (!d) return;
    if (navigator.share && /Android|iPhone|iPad/i.test(navigator.userAgent)) navigator.share({ text: d.texto }).catch(function () {});
    else window.open('https://wa.me/?text=' + encodeURIComponent(d.texto), '_blank', 'noopener');
  }
  function copiar(btn) {
    var d = actual(); if (!d || !navigator.clipboard) return;
    navigator.clipboard.writeText(d.texto).then(function () { aviso(btn, 'Copiado'); });
  }
  function aviso(btn, t) { var o = btn.textContent; btn.textContent = t; setTimeout(function () { btn.textContent = o; }, 1600); }

  // ---------- estilos ----------
  function estilos() {
    if (document.getElementById('waCss')) return;
    var s = document.createElement('style'); s.id = 'waCss';
    s.textContent =
      '.wa-top{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;border-bottom:1px solid rgba(233,211,160,.14);margin-bottom:18px}' +
      '.wa-tabs{display:flex;gap:24px}' +
      '.wa-tabs button{position:relative;border:0;background:none;padding:0 0 11px;cursor:pointer;font:400 14px "IBM Plex Sans",sans-serif;color:#f3f6fb}' +
      '.wa-tabs button::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;background:#e9d3a0;transform:scaleX(0);transition:transform .3s cubic-bezier(.23,1,.32,1)}' +
      '.wa-tabs button[aria-selected="true"]{font-weight:600}.wa-tabs button[aria-selected="true"]::after{transform:scaleX(1)}' +
      '.wa-estado{padding-bottom:11px;font:500 11px "IBM Plex Mono",monospace;letter-spacing:.06em;color:#e9d3a0}' +
      '.wa-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:22px}' +
      '.wa-sub{margin-bottom:8px;font:500 10.5px "IBM Plex Mono",monospace;letter-spacing:.16em;text-transform:uppercase;color:#e9d3a0}' +
      '.wa-card{display:block;width:100%;height:auto;border-radius:10px;border:1px solid rgba(233,211,160,.14)}' +
      '.wa-chat{max-height:560px;overflow:auto;padding:14px;border-radius:10px;background:#0a1220;border:1px solid rgba(233,211,160,.14)}' +
      '.wa-bubble{max-width:520px;padding:10px 12px;border-radius:0 10px 10px 10px;background:#1f2c34;color:#f3f6fb;font:400 13.5px/1.5 "IBM Plex Sans",sans-serif;overflow-wrap:anywhere}' +
      '.wa-acciones{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}' +
      '.wa-btn{padding:9px 16px;border-radius:8px;border:1px solid rgba(233,211,160,.3);background:none;color:#f3f6fb;font:500 13px "IBM Plex Sans",sans-serif;cursor:pointer;transition:border-color .2s,background .2s}' +
      '.wa-btn.wa-main{border-color:#e9d3a0;color:#e9d3a0}' +
      '@media (hover:hover){.wa-btn:hover{background:rgba(233,211,160,.08)}}' +
      '.wa-nota{margin:12px 0 0;font:400 12.5px/1.5 "IBM Plex Sans",sans-serif;color:#f3f6fb}' +
      '@media (max-width:760px){.wa-grid{grid-template-columns:1fr}.wa-btn{flex:1 1 45%}}';
    document.head.appendChild(s);
  }

  window.pnWhatsapp = function (el, get, base) {
    st = { el: el, get: get, base: base, momento: null, datos: {}, cargando: false };
    estilos(); esqueleto(); mostrar(momentoPorHora(), false);
  };
})();
