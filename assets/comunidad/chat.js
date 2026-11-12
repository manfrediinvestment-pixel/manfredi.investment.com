/* Chats de Manfredi Pro -- pestaña "Chat" (#pro). Backend: worker manfredi-comunidad (D1).
 *
 * - "Mercados" (gratis): lo lee cualquiera, escribe quien inició sesión. Ahí se publican solos
 *   los resúmenes de apertura y cierre: el mismo mensaje que va a la Comunidad de WhatsApp.
 * - Manfredi Pro, dividido en chats como una Comunidad de WhatsApp: Ideas de Ignacio (publica
 *   solo él), Charla de socios y Preguntas a Ignacio. Solo socios (el worker lo valida); al
 *   resto se le muestra la invitación.
 * - Arriba del chat gratis, una guía lleva a los resúmenes de hoy aunque la charla los deje lejos.
 *
 * Mensajes nuevos por consulta cada pocos segundos (solo con la pestaña a la vista).
 * Anti-estafa: los links de los usuarios se muestran como texto; solo los oficiales se tocan.
 * window.ProChat.montar(el) -- lo llama assets/pro/pro.js.
 */
(function () {
  if (window.ProChat) return;
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = LOCAL ? 'http://localhost:8790' : 'https://manfredi-comunidad.nachito2502.workers.dev';
  // Link de invitación de la Comunidad de WhatsApp: vive en assets/comunidad/wa.js (vacío = "Muy pronto").
  var WA_COMUNIDAD = window.MI_WA_COMUNIDAD || '';
  // Los chats de Manfredi Pro todavía no abren: se ven con el cartel "Próximamente".
  var PRO_PRONTO = true;
  var EMOJIS = ['👍', '🔥', '📈', '📉', '🤔'];
  var COLORES = ['#e9d3a0', '#8ec5ff', '#9be3c4', '#f0a8b8', '#c9b6ff', '#ffc58f'];
  var SALAS = {
    gratis: { nombre: 'Mercados', tag: 'Gratis', sub: 'Comunidad abierta · resúmenes antes y después de Wall Street',
      fijado: 'Resúmenes del mercado media hora antes de que abra Wall Street y media hora después del cierre. Las opiniones de los miembros no son recomendaciones de inversión. Nadie del equipo te va a escribir por privado ni a pedirte dinero.' },
    ideas: { nombre: 'Ideas de Ignacio', pro: true, soloCreador: true, sub: 'Publica solo Ignacio · ideas, seguimientos y cierres',
      fijado: 'Las ideas son análisis generales: no consideran tu situación particular. Antes de operar, mirá si encajan con tu perfil.' },
    socios: { nombre: 'Charla de socios', pro: true, sub: 'Solo socios Pro',
      fijado: 'Lo que se comparte acá queda entre socios. Las opiniones de los miembros no son recomendaciones de inversión.' },
    preguntas: { nombre: 'Preguntas a Ignacio', pro: true, sub: 'Ignacio responde citando tu mensaje',
      fijado: 'Una pregunta por mensaje: Ignacio responde citándola, así nada queda sin respuesta.' }
  };
  var PRO = ['ideas', 'socios', 'preguntas'];
  var TODAS = ['gratis'].concat(PRO);
  var IC = {
    send: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 12l16-8-6 16-2.5-6.5z" fill="currentColor"/></svg>',
    back: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    pin: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M9 3h6l-1 6 3 3H7l3-3zM12 12v9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    reply: '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M10 8V5l-6 6 6 6v-3c4 0 7 1 9 4-1-5-4-9-9-10z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    smile: '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8.5 14c1 1.4 2.1 2 3.5 2s2.5-.6 3.5-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="9.3" cy="10" r="1" fill="currentColor"/><circle cx="14.7" cy="10" r="1" fill="currentColor"/></svg>',
    trash: '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M5 7h14M10 7V5h4v2M7 7l1 12h8l1-12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    share: '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M3.5 20.5l1.3-4.2A8.5 8.5 0 1 1 8 19.4z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M9 8.6c0 3.3 2.9 6.4 6.4 6.4l1.1-1.6-2-1-1 1c-1.2-.5-2.2-1.5-2.7-2.7l1-1-1-2z" fill="currentColor"/></svg>',
    check: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M12 2l2.4 2.2 3.2-.4.9 3.1 2.9 1.5-1 3.1 1 3.1-2.9 1.5-.9 3.1-3.2-.4L12 22l-2.4-2.2-3.2.4-.9-3.1-2.9-1.5 1-3.1-1-3.1 2.9-1.5.9-3.1 3.2.4z" fill="currentColor"/><path d="M8.5 12.2l2.3 2.3 4.7-4.8" fill="none" stroke="#0b1629" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    copy: '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><rect x="8.5" y="8.5" width="11" height="11" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M15.5 8.5V6.5a2 2 0 0 0-2-2h-7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    lock: '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 11V8a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    down: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    gente: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="9" cy="8.5" r="3.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 19c.6-3.2 3-5 6-5s5.4 1.8 6 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M15.5 5.6a3 3 0 0 1 0 5.8M17.5 14.3c1.8.7 3 2.300 3.500 4.700" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    foto: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><rect x="3.5" y="5" width="17" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="9" cy="10" r="1.7" fill="currentColor"/><path d="M4.5 17.5l5-5 3.5 3.5 2.5-2.5 4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    x: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    ideas: '<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path d="M4 19l5-6 4 3 7-9" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 7h5v5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    socios: '<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h7A2.5 2.5 0 0 1 16 6.5v4A2.5 2.5 0 0 1 13.5 13H9l-3.5 3v-3H6.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M19 9.5a2 2 0 0 1 1 1.7v3.6a2 2 0 0 1-2 2h-.5V19L15 16.8h-3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    preguntas: '<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path d="M9.2 9a2.9 2.9 0 1 1 4.1 2.6c-.8.4-1.3 1-1.3 1.9v.5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/><circle cx="12" cy="17.6" r="1.15" fill="currentColor"/></svg>',
    clock: '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7.5V12l3 2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
  };
  function avatarSala(k, cls) {
    if (k === 'gratis') return '<span class="ch-av ch-av--sala ' + (cls || '') + '"><img src="assets/img/icon-192.png" alt=""></span>';
    return '<span class="ch-av ch-av--sala ch-av--pro ' + (cls || '') + '">' + IC[k] + '</span>';
  }

  var S = null;
  function nuevaSala() { return { msgs: {}, orden: [], ts: 0, hayMas: false, estado: 'cargando', error: '', hoy: [], vistos: leer('mi-chat-visto', {}) }; }
  function nuevasSalas() { var o = {}; TODAS.forEach(function (k) { o[k] = nuevaSala(); }); return o; }

  // ---------- utilidades ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function leer(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  // El formato de WhatsApp (negrita, cursiva, citas, listas y tablas): el mismo del mensaje que va
  // a la Comunidad. Los links se pueden tocar solo en los mensajes oficiales (anti-estafa).
  function formato(t, oficial) { return tickers(window.MiTarjeta.waHtml(t, oficial)); }

  // ---------- $TICKER en los mensajes: precio en vivo y gráfico (datos de Mercados) ----------
  var MERC = 'https://manfredi-mercados.nachito2502.workers.dev';
  // Si un símbolo está en varias categorías, gana la primera (NVDA = la acción en EE.UU., no el CEDEAR)
  var ORDEN_CAT = ['arg_stocks', 'usa_stocks', 'usa_adrs', 'cripto', 'commodities', 'arg_cedears', 'arg_bonds', 'dolares'];
  var PRECIOS = null, PRECIOS_TS = 0;
  function tickers(html) {
    // $NVDA, $ggal, $BRK.B (el punto final de una oración no es parte del ticker)
    return html.replace(/(^|[\s>(¡¿"])\$([A-Za-z][A-Za-z0-9]{0,7}(?:\.[A-Za-z])?)(?=$|[\s<.,;:!?)"])/g, function (_, antes, s) {
      s = s.toUpperCase();
      return antes + '<button type="button" class="ch-tk" data-a="tk" data-s="' + s + '"><b>$' + s + '</b>' + chipPrecio(s) + '</button>';
    });
  }
  function fmtNum(v) { var d = Math.abs(v) >= 1000 ? 0 : 2; return Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function fmtPct(v) { if (v == null || isNaN(v)) return ''; return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function chipPrecio(s) {
    var p = PRECIOS && PRECIOS[s];
    if (!p || p.price == null) return '<span class="ch-tk-p"></span>';
    return '<span class="ch-tk-p">' + (p.cur === 'USD' ? 'US$ ' : '$ ') + fmtNum(p.price) + (p.change != null ? ' <i class="' + (p.change > 0 ? 'up' : p.change < 0 ? 'dn' : '') + '">' + fmtPct(p.change) + '</i>' : '') + '</span>';
  }
  function cargarPrecios() {
    if (Date.now() - PRECIOS_TS < 110e3) return;
    PRECIOS_TS = Date.now();
    fetch(MERC + '/mercados').then(function (r) { return r.json(); }).then(function (d) {
      var m = {};
      ORDEN_CAT.slice().reverse().forEach(function (k) {
        var c = d.categorias && d.categorias[k]; if (!c) return;
        c.items.forEach(function (it) { m[it.symbol.toUpperCase()] = { cat: k, cur: c.currency, price: it.price, change: it.change, name: it.name, logo: it.logo }; });
      });
      PRECIOS = m;
      S.root.querySelectorAll('.ch-tk').forEach(function (b) { b.querySelector('.ch-tk-p').outerHTML = chipPrecio(b.dataset.s); });
      if (S.ficha) pintarFichaCab();
    }).catch(function () { PRECIOS_TS = 0; });
  }

  // Ficha del activo: precio, gráfico en vivo (1 día se actualiza cada minuto) y "Ver en Mercados".
  var TFS = [['1D', '1 día'], ['1M', '1 mes'], ['1A', '1 año'], ['5A', '5 años']];
  function abrirFicha(s) {
    var p = PRECIOS && PRECIOS[s];
    cerrarFicha();
    S.ficha = { s: s, cat: p ? p.cat : 'usa_stocks', tf: p && (p.cat === 'arg_bonds' || p.cat === 'dolares') ? '1M' : '1D' };
    var el = S.root.querySelector('.ch-ficha');
    el.innerHTML = '<div class="ch-ficha-card" role="dialog" aria-label="Gráfico de ' + esc(s) + '">' +
      '<div class="ch-ficha-cab"></div>' +
      '<div class="ch-ficha-tf" role="group" aria-label="Temporalidad">' + TFS.map(function (t) { return '<button type="button" data-a="tk-tf" data-tf="' + t[0] + '"' + (t[0] === S.ficha.tf ? ' aria-pressed="true"' : '') + '>' + t[1] + '</button>'; }).join('') + '</div>' +
      '<div class="ch-ficha-gr"><div class="ch-ficha-msg">Cargando gráfico…</div></div>' +
      '<div class="ch-ficha-pie"><span class="ch-ficha-vivo"><i></i>En vivo · datos de Mercados</span><button type="button" class="ch-btn ch-btn--gold" data-a="tk-mercados">Ver en Mercados</button></div>' +
      '<button type="button" class="ch-ficha-x" data-a="tk-cerrar" aria-label="Cerrar">' + IC.x + '</button></div>';
    el.hidden = false;
    pintarFichaCab(); serieFicha();
    S.ficha.timer = setInterval(function () { if (S.ficha && S.ficha.tf === '1D' && aLaVista()) { PRECIOS_TS = 0; cargarPrecios(); serieFicha(true); } }, 60e3);
  }
  function pintarFichaCab() {
    var f = S.ficha, cab = f && S.root.querySelector('.ch-ficha-cab'); if (!cab) return;
    var p = PRECIOS && PRECIOS[f.s];
    cab.innerHTML = (p && p.logo ? '<img src="' + esc(p.logo) + '" alt="" class="ch-ficha-logo">' : '<span class="ch-ficha-logo ch-ficha-logo--txt">' + esc(f.s.slice(0, 2)) + '</span>') +
      '<div class="ch-ficha-t"><b>' + esc(f.s) + '</b><span>' + esc(p && p.name && p.name !== f.s ? p.name : '') + '</span></div>' +
      (p && p.price != null ? '<div class="ch-ficha-p"><b>' + (p.cur === 'USD' ? 'US$ ' : '$ ') + fmtNum(p.price) + '</b><i class="' + (p.change > 0 ? 'up' : p.change < 0 ? 'dn' : '') + '">' + fmtPct(p.change) + ' hoy</i></div>' : '');
  }
  function serieFicha(silencio) {
    var f = S.ficha; if (!f) return;
    var gr = S.root.querySelector('.ch-ficha-gr'), tf = f.tf, s = f.s;
    fetch(MERC + '/serie?category=' + f.cat + '&symbol=' + encodeURIComponent(s) + '&tf=' + tf).then(function (r) { return r.json(); }).then(function (d) {
      if (!S.ficha || S.ficha.s !== s || S.ficha.tf !== tf) return;
      if (!d.points || d.points.length < 2) throw new Error(d.error || 'Sin datos');
      conGraficos(function (LC) {
        if (!S.ficha || !gr.isConnected) return;
        if (!f.ch) {
          gr.innerHTML = '';
          f.ch = LC.createChart(gr, {
            autoSize: true,
            layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#e9d3a0', fontFamily: "'IBM Plex Mono', ui-monospace, monospace", fontSize: 11, attributionLogo: false },
            grid: { vertLines: { visible: false }, horzLines: { color: 'rgba(233,211,160,.06)' } },
            rightPriceScale: { borderVisible: false }, timeScale: { borderVisible: false, timeVisible: true, secondsVisible: false },
            handleScale: false, handleScroll: false,
            localization: { locale: 'es-AR', timeFormatter: function (t) { return new Date(t * 1000).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }); } }
          });
          f.serie = f.ch.addSeries(LC.AreaSeries, { lineWidth: 2, priceLineVisible: true });
        }
        // en 1 día el color sigue a la variación del día (contra el cierre anterior), igual que el número de arriba
        var pd = PRECIOS && PRECIOS[s], pts = d.points;
        var sube = tf === '1D' && pd && pd.change != null ? pd.change >= 0 : pts[pts.length - 1].c >= (pts[0].o || pts[0].c), hex = sube ? '#56c793' : '#ef7a6b', rgb = sube ? '86,199,147' : '239,122,107';
        f.serie.applyOptions({ lineColor: hex, topColor: 'rgba(' + rgb + ',.22)', bottomColor: 'rgba(' + rgb + ',0)', priceLineColor: hex });
        f.serie.setData(pts.map(function (p) { return { time: p.t, value: p.c }; }));
        if (!silencio) f.ch.timeScale().fitContent();
      });
    }).catch(function () {
      if (silencio || !S.ficha || S.ficha.s !== s) return;
      if (f.ch) { f.ch.remove(); f.ch = null; }
      gr.innerHTML = '<div class="ch-ficha-msg">No hay gráfico para esta temporalidad. Probá con otra o abrilo en Mercados.</div>';
    });
  }
  function conGraficos(cb) { var t0 = Date.now(); (function w() { if (window.LightweightCharts) return cb(window.LightweightCharts); if (Date.now() - t0 < 10000) setTimeout(w, 100); })(); }
  function cerrarFicha() {
    var f = S.ficha; if (!f) return;
    clearInterval(f.timer); if (f.ch) f.ch.remove(); S.ficha = null;
    var el = S.root.querySelector('.ch-ficha'); if (el) { el.hidden = true; el.innerHTML = ''; }
  }
  function hora(ms) { return new Date(ms).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }); }
  function diaClave(ms) { var d = new Date(ms); return d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate(); }
  function diaTexto(ms) {
    var d = new Date(ms), hoy = new Date(); hoy.setHours(0, 0, 0, 0);
    var x = new Date(d); x.setHours(0, 0, 0, 0);
    var dif = Math.round((hoy - x) / 864e5);
    if (dif === 0) return 'Hoy';
    if (dif === 1) return 'Ayer';
    var t = d.toLocaleDateString('es-AR', dif < 7 ? { weekday: 'long' } : { day: 'numeric', month: 'long' });
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  function color(h) { var n = 0; for (var i = 0; i < (h || '').length; i++) n = (n * 31 + h.charCodeAt(i)) >>> 0; return COLORES[n % COLORES.length]; }
  function iniciales(n) { var p = String(n || '?').trim().split(/\s+/); return ((p[0] || '?')[0] + (p.length > 1 ? p[p.length - 1][0] : '')).toUpperCase(); }
  function avatar(m, cls) {
    if (m.rol === 'oficial') return '<span class="ch-av ' + (cls || '') + ' ch-av--of"><img src="assets/img/icon-192.png" alt=""></span>';
    var c = m.rol === 'creador' ? '#e9d3a0' : color(m.h);
    if (m.foto) return '<span class="ch-av ' + (cls || '') + '"><img src="' + esc(m.foto) + '" alt="" referrerpolicy="no-referrer" loading="lazy"></span>';
    return '<span class="ch-av ' + (cls || '') + '" style="--av:' + c + '">' + esc(iniciales(m.nombre)) + '</span>';
  }
  function chip(m) {
    if (m.rol === 'oficial') return '<span class="ch-ver" title="Cuenta oficial">' + IC.check + '</span>';
    if (m.rol === 'creador') return '<em class="ch-chip ch-chip--cr">Creador</em>';
    if (m.rol === 'socio') return '<em class="ch-chip">Pro</em>';
    return '';
  }
  function usuario() { return window._currentUser || null; }
  function token() { var u = usuario(); return u && u.getIdToken ? u.getIdToken() : Promise.resolve(null); }
  function api(path, opt) {
    opt = opt || {};
    return token().then(function (t) {
      var h = { 'Content-Type': 'application/json' }; if (t) h.Authorization = 'Bearer ' + t;
      return fetch(API + path, { method: opt.method || 'GET', headers: h, body: opt.body ? JSON.stringify(opt.body) : undefined });
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) { var e = new Error(d.error || ('HTTP ' + r.status)); e.status = r.status; e.code = d.error; throw e; }
        return d;
      });
    });
  }

  // ---------- datos ----------
  function aplicar(sala, lista, nuevos) {
    var z = S.salas[sala], cambio = false;
    lista.forEach(function (m) {
      var prev = z.msgs[m.id];
      if (!prev) { z.orden.push(m.id); if (nuevos) S.recien[m.id] = 1; cambio = true; }
      else if (prev.editado === m.editado && !prev.pendiente) return;
      z.msgs[m.id] = m; cambio = true;
    });
    if (cambio) z.orden.sort(function (a, b) { return a - b; });
    return cambio;
  }
  function cargar(sala) {
    var z = S.salas[sala];
    return api('/chat/' + sala).then(function (d) {
      z.msgs = {}; z.orden = []; z.ts = d.ahora; z.hayMas = d.hayMas; z.estado = 'ok'; z.hoy = d.hoy || []; S.yo = d.yo || S.yo;
      aplicar(sala, d.mensajes, false);
    }).catch(function (e) {
      z.estado = e.code === 'solo_socios' || e.code === 'sin_sesion' ? 'bloqueada' : 'error';
      z.motivo = e.code; z.error = e.message;
    }).then(function () { if (sala === S.sala) pintarSala(true); pintarLista(); });
  }
  // Los chats de Pro: sin sesión no hace falta preguntar, quedan con la invitación.
  function cargarTodas() {
    // ?r=<id>: viene del link del epígrafe de WhatsApp -> abre Mercados en ese resumen
    var r = +new URLSearchParams(location.search).get('r');
    cargar('gratis').then(function () {
      if (!r) return;
      if (S.sala === 'gratis') setTimeout(function () { irA(r); }, 300);
      try { var q = new URLSearchParams(location.search); q.delete('r'); history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : '') + location.hash); } catch (e) {}
    });
    PRO.forEach(function (k) {
      if (PRO_PRONTO) S.salas[k].estado = 'pronto';
      else if (usuario()) cargar(k);
      else { S.salas[k].estado = 'bloqueada'; S.salas[k].motivo = 'sin_sesion'; }
    });
    pintarLista();
  }
  function consultar(sala) {
    var z = S.salas[sala];
    if (z.estado !== 'ok' || z.consultando) return Promise.resolve();
    z.consultando = true;
    return api('/chat/' + sala + '?ts=' + z.ts).then(function (d) {
      z.ts = d.ahora;
      var hoyAntes = JSON.stringify(z.hoy || []); z.hoy = d.hoy || [];
      if (sala === S.sala && JSON.stringify(z.hoy) !== hoyAntes) pintarHoy();
      if (aplicar(sala, d.mensajes, true)) { if (sala === S.sala) pintarFeed(false); pintarLista(); }
    }).catch(function () {}).then(function () { z.consultando = false; });
  }
  function anteriores() {
    var z = S.salas[S.sala];
    if (!z.hayMas || z.trayendo || !z.orden.length) return;
    z.trayendo = true;
    var feed = S.root.querySelector('.ch-feed'), alto = feed.scrollHeight;
    api('/chat/' + S.sala + '?antes=' + z.orden[0]).then(function (d) {
      z.hayMas = d.hayMas; aplicar(S.sala, d.mensajes, false);
      pintarFeed(false, true);
      feed.scrollTop += feed.scrollHeight - alto;
    }).catch(function () {}).then(function () { z.trayendo = false; });
  }

  // ---------- tarjeta del resumen (assets/comunidad/tarjeta.js) ----------
  var tarjetas = {};
  function tarjeta(m) {
    var k = m.id + ':' + m.editado;
    if (tarjetas[k]) return tarjetas[k];
    var t = tarjetas[k] = { url: null, blob: null };
    if (!window.MiTarjeta || !m.datos) return t;
    var cv = document.createElement('canvas'); cv.width = 1080; cv.height = 1350;
    window.MiTarjeta.dibujar(cv, m.datos).then(function (b) {
      t.blob = b; t.url = URL.createObjectURL(b);
      var img = S.root.querySelector('[data-card="' + m.id + '"]');
      if (img) { img.src = t.url; img.parentNode.classList.add('on'); }
    });
    return t;
  }

  // ---------- estructura ----------
  function esqueleto() {
    S.root.innerHTML =
      '<div class="ch-app" data-vista="chat">' +
        '<aside class="ch-side">' +
          '<div class="ch-side-h"><h3>Chats</h3></div>' +
          '<ul class="ch-list" role="list"></ul>' +
          '<div class="ch-next" aria-live="off"></div>' +
          '<div class="ch-wa">' +
            '<span class="ch-wa-ic">' + IC.share + '</span>' +
            '<div><b>Canal de WhatsApp</b><span>Los resúmenes del día, en tu celular.</span></div>' +
            (WA_COMUNIDAD ? '<a class="ch-wa-btn" href="' + esc(WA_COMUNIDAD) + '" target="_blank" rel="noopener">Seguir</a>' : '<em class="ch-chip">Muy pronto</em>') +
          '</div>' +
        '</aside>' +
        '<section class="ch-main" aria-label="Conversación"></section>' +
      '</div>' +
      '<div class="ch-lb" hidden><button type="button" class="ch-lb-x" aria-label="Cerrar">' + IC.x + '</button><img alt=""></div>' +
      '<div class="ch-ficha" hidden></div>';
    S.root.addEventListener('click', clic);
    S.root.addEventListener('keydown', tecla);
    S.root.addEventListener('input', function (e) {
      if (e.target.matches('.ch-ta')) ajustar(e.target);
      if (e.target.matches('.ch-adj-zoom') && S.adjunto) { S.adjunto.zoom = +e.target.value; dibujarAdj(); }
    });
    // Encuadre: arrastrar la imagen (mouse o dedo)
    var arr = null;
    S.root.addEventListener('pointerdown', function (e) {
      if (!e.target.matches('.ch-adj-cv')) return;
      arr = { x: e.clientX, y: e.clientY }; e.target.setPointerCapture(e.pointerId); e.preventDefault();
    });
    S.root.addEventListener('pointermove', function (e) {
      if (!arr) return;
      moverAdj(e.clientX - arr.x, e.clientY - arr.y); arr = { x: e.clientX, y: e.clientY };
    });
    ['pointerup', 'pointercancel'].forEach(function (t) { S.root.addEventListener(t, function () { arr = null; }); });
  }

  function itemSala(k) {
    var z = S.salas[k], info = SALAS[k], ult = null;
    for (var i = z.orden.length - 1; i >= 0; i--) { var m = z.msgs[z.orden[i]]; if (m && !m.borrado) { ult = m; break; } }
    var noLeidos = z.estado === 'ok' && k !== S.sala ? z.orden.filter(function (id) { return id < 1e14 && id > (z.vistos[k] || 0) && z.msgs[id].h !== (S.yo && S.yo.h); }).length : 0;
    var prev = z.estado === 'pronto' ? '<em class="ch-chip">Próximamente</em>'
      : z.estado === 'bloqueada' ? '<span class="ch-lock">' + IC.lock + ' Solo socios</span>'
      : ult ? esc((ult.rol === 'oficial' ? '' : ult.nombre.split(' ')[0] + ': ') + (ult.tipo === 'resumen' ? (ult.datos.momento === 'apertura' ? 'Resumen antes de la apertura' : 'Resumen del cierre') : ult.tipo === 'imagen' && !ult.texto ? 'Imagen' : ult.texto.replace(/[*_]/g, '')))
      : z.estado === 'cargando' ? 'Cargando…' : '';
    return '<li><button type="button" class="ch-item' + (info.pro ? ' ch-item--sub' : '') + '" data-ir="' + k + '"' + (k === S.sala ? ' aria-current="true"' : '') + '>' +
      avatarSala(k) +
      '<span class="ch-item-b"><span class="ch-item-t"><b>' + esc(info.nombre) + '</b>' + (info.tag ? '<em class="ch-tag">' + info.tag + '</em>' : '') +
      (ult ? '<time>' + (diaTexto(ult.creado) === 'Hoy' ? hora(ult.creado) : diaTexto(ult.creado)) + '</time>' : '') + '</span>' +
      '<span class="ch-item-p"><span>' + prev + '</span>' + (noLeidos ? '<i class="ch-unread">' + (noLeidos > 99 ? '99+' : noLeidos) + '</i>' : '') + '</span></span>' +
    '</button></li>';
  }
  function pintarLista() {
    var ul = S.root.querySelector('.ch-list'); if (!ul) return;
    ul.innerHTML = itemSala('gratis') +
      '<li class="ch-grupo"><div class="ch-grupo-h"><span class="ch-av ch-av--pro ch-av--grupo"><span>Pro</span></span><b>Manfredi Pro</b><em class="ch-tag ch-tag--pro">Pro</em></div>' +
      '<ul role="list">' + PRO.map(itemSala).join('') + '</ul></li>';
  }

  function pintarSala(alFondo) {
    var main = S.root.querySelector('.ch-main'), k = S.sala, z = S.salas[k], info = SALAS[k];
    var cab = '<header class="ch-head">' +
      '<button type="button" class="ch-back" data-a="lista" aria-label="Volver a los chats">' + IC.back + '</button>' +
      avatarSala(k) +
      '<div class="ch-head-t"><b>' + (info.pro ? '<small>Manfredi Pro</small>' : '') + esc(info.nombre) + '</b><span>' + esc(info.sub) + '</span></div>' +
      (k === 'gratis' ? '<div class="ch-gente"' + (S.gente ? '' : ' hidden') + '>' + IC.gente + '<span><b>' + (S.gente || 0).toLocaleString('es-AR') + '</b> personas en la comunidad</span></div>' : '') +
    '</header>';
    if (z.estado === 'pronto') { main.innerHTML = cab + pronto(); return; }
    if (z.estado === 'bloqueada') { main.innerHTML = cab + bloqueo(); return; }
    main.innerHTML = cab +
      '<button type="button" class="ch-pin" data-a="pin" aria-expanded="false">' + IC.pin + '<span>' + esc(info.fijado) + '</span></button>' +
      (k === 'gratis' ? '<div class="ch-hoy" aria-label="Resúmenes de hoy"></div>' : '') +
      '<div class="ch-feedwrap"><div class="ch-feed" role="log" aria-live="polite" aria-label="Mensajes"><div class="ch-feed-in"></div></div>' +
      '<button type="button" class="ch-nuevos" data-a="bajar" hidden>' + IC.down + '<span>Mensajes nuevos</span></button></div>' +
      compositor();
    var feed = main.querySelector('.ch-feed');
    feed.addEventListener('scroll', function () {
      S.pegado = alFondoDe(feed);
      if (feed.scrollTop < 120) anteriores();
      if (alFondoDe(feed)) { main.querySelector('.ch-nuevos').hidden = true; marcarVisto(); }
    }, { passive: true });
    // Al entrar, el chat queda pegado abajo (en el último mensaje) aunque después cambie el alto:
    // las tarjetas de los resúmenes se dibujan un instante más tarde y el chat puede cargarse
    // cuando todavía no se ve (otra pestaña). Se suelta cuando la persona sube a leer.
    S.pegado = alFondo !== false;
    if (S.ro) S.ro.disconnect();
    if (window.ResizeObserver) {
      S.ro = new ResizeObserver(function () { if (S.pegado) feed.scrollTop = feed.scrollHeight; });
      S.ro.observe(feed); S.ro.observe(feed.querySelector('.ch-feed-in'));
    }
    pintarFeed(alFondo !== false);
    pintarHoy();
    dibujarAdj();
  }

  // Guía a los resúmenes de hoy: siempre a la vista, lleva al mensaje aunque haya quedado lejos.
  var RES = [{ k: 'apertura', t: 'Antes de la apertura' }, { k: 'cierre', t: 'Cierre del mercado' }];
  function pintarHoy() {
    var el = S.root.querySelector('.ch-hoy'); if (!el) return;
    var z = S.salas.gratis, hoy = window.MiTarjeta.horarios(new Date());
    var vistos = leer('mi-res-visto', {});
    if (!hoy.hay && !(z.hoy || []).length) { el.hidden = true; return; }
    el.hidden = false;
    el.innerHTML = '<span class="ch-hoy-k">Resúmenes de hoy</span>' + RES.map(function (r) {
      var m = (z.hoy || []).filter(function (x) { return x.momento === r.k; })[0];
      if (!m) return '<span class="ch-hoy-b pend">' + IC.clock + '<span>' + r.t + '</span><time>' + hoy[r.k].hora + '</time></span>';
      return '<button type="button" class="ch-hoy-b" data-a="ir-res" data-id="' + m.id + '">' + (vistos[m.id] ? '' : '<i class="ch-hoy-dot" aria-label="Nuevo"></i>') +
        '<span>' + r.t + '</span><time>' + hora(m.creado) + '</time>' + IC.down + '</button>';
    }).join('');
  }
  // Mueve solo el chat (no la página) hasta el mensaje y lo destaca un instante.
  function resaltar(o) {
    var feed = S.root.querySelector('.ch-feed');
    S.pegado = false;
    feed.scrollTo({ top: Math.max(0, o.offsetTop - 14), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    o.classList.remove('flash'); void o.offsetWidth; o.classList.add('flash');
  }
  // Lleva a un mensaje: si todavía no está cargado, trae los anteriores hasta encontrarlo.
  function irA(id, intentos) {
    var feed = S.root.querySelector('.ch-feed'), z = S.salas[S.sala];
    var o = S.root.querySelector('.ch-row[data-id="' + id + '"]');
    if (o) { resaltar(o); return; }
    if (!feed || !z.hayMas || (intentos || 0) > 10 || !z.orden.length) return;
    api('/chat/' + S.sala + '?antes=' + z.orden[0]).then(function (d) {
      z.hayMas = d.hayMas; aplicar(S.sala, d.mensajes, false); pintarFeed(false, true);
      irA(id, (intentos || 0) + 1);
    }).catch(function () {});
  }

  function compositor() {
    if (!usuario()) return '<div class="ch-login"><span>Iniciá sesión para escribir en el chat.</span><button type="button" class="ch-btn ch-btn--gold" data-a="login">Iniciar sesión</button></div>';
    if (SALAS[S.sala].soloCreador && !(S.yo && S.yo.rol === 'creador'))
      return '<div class="ch-login"><span>Acá publica solo Ignacio. Para comentar una idea:</span><button type="button" class="ch-btn" data-ir="socios">Ir a Charla de socios</button></div>';
    var r = S.responde, adj = S.adjunto, cr = esCreador();
    return (r ? '<div class="ch-reply"><div><b>' + esc(r.nombre) + '</b><span>' + esc(r.texto) + '</span></div><button type="button" data-a="sin-reply" aria-label="Cancelar respuesta">' + IC.x + '</button></div>' : '') +
      (adj ? editorAdj() : '') +
      '<form class="ch-comp" data-a="enviar">' +
        (cr ? '<label class="ch-clip" title="Adjuntar imagen" aria-label="Adjuntar imagen">' + IC.foto + '<input type="file" accept="image/*" class="ch-file" hidden></label>' : '') +
        '<textarea class="ch-ta" rows="1" maxlength="800" placeholder="' + (adj ? 'Agregá un texto (opcional)' : 'Escribí un mensaje · con $NVDA se ve el gráfico') + '" aria-label="Mensaje">' + esc(S.borrador[S.sala] || '') + '</textarea>' +
        '<button type="submit" class="ch-send" aria-label="Enviar">' + IC.send + '</button>' +
      '</form><div class="ch-toast" role="status"></div>';
  }

  function pronto() {
    var fantasmas = [62, 38, 74, 46, 58, 30, 66].map(function (w, i) {
      return '<div class="ch-fake' + (i % 3 === 1 ? ' mio' : '') + '"><i style="width:' + w + '%"></i><i style="width:' + (w * 0.6) + '%"></i></div>';
    }).join('');
    return '<div class="ch-locked"><div class="ch-locked-bg" aria-hidden="true">' + fantasmas + '</div>' +
      '<div class="ch-locked-card">' +
        '<span class="ch-kick">Manfredi Pro · Próximamente</span>' +
        '<h3>Los chats de los socios</h3>' +
        '<ul><li><b>Ideas de Ignacio</b>Cada análisis, sus seguimientos y sus cierres.</li>' +
        '<li><b>Charla de socios</b>Un espacio para hablar de mercados entre socios.</li>' +
        '<li><b>Preguntas a Ignacio</b>Consultás y te responde Ignacio, no un bot.</li></ul>' +
        '<button type="button" class="ch-btn ch-btn--gold" data-ir="gratis">Ir al chat de Mercados</button>' +
      '</div></div>';
  }

  function bloqueo() {
    var fantasmas = [62, 38, 74, 46, 58, 30, 66].map(function (w, i) {
      return '<div class="ch-fake' + (i % 3 === 1 ? ' mio' : '') + '"><i style="width:' + w + '%"></i><i style="width:' + (w * 0.6) + '%"></i></div>';
    }).join('');
    var logueado = !!usuario();
    return '<div class="ch-locked"><div class="ch-locked-bg" aria-hidden="true">' + fantasmas + '</div>' +
      '<div class="ch-locked-card">' +
        '<span class="ch-kick">Manfredi Pro</span>' +
        '<h3>El chat de los socios</h3>' +
        '<ul><li><b>Ideas de Ignacio</b>Cada análisis, sus seguimientos y sus cierres, primero acá.</li>' +
        '<li><b>Preguntas directas</b>Consultás y te responde Ignacio, no un bot.</li>' +
        '<li><b>Todo Pro</b>Informes completos y Warren IA incluidos.</li></ul>' +
        '<button type="button" class="ch-btn ch-btn--gold" data-a="pagar">Sumarme a Manfredi Pro</button>' +
        (logueado ? '' : '<button type="button" class="ch-btn" data-a="login">Ya soy socio · Iniciar sesión</button>') +
      '</div></div>';
  }

  // ---------- mensajes ----------
  function pintarFeed(alFondo, sinAnim) {
    var feed = S.root.querySelector('.ch-feed'); if (!feed) return;
    var estaba = alFondoDe(feed), z = S.salas[S.sala], html = '', antes = null;
    if (z.estado === 'cargando') html = '<div class="ch-cargando"><i></i><i></i><i></i></div>';
    else if (z.estado === 'error') html = '<div class="ch-dia"><span>No se pudo cargar el chat. Probá de nuevo en un rato.</span></div>';
    if (z.hayMas) html += '<div class="ch-mas-arriba"><span>Cargando anteriores…</span></div>';
    z.orden.forEach(function (id) {
      var m = z.msgs[id];
      if (!antes || diaClave(antes.creado) !== diaClave(m.creado)) { html += '<div class="ch-dia"><span>' + diaTexto(m.creado) + '</span></div>'; antes = null; }
      var cont = antes && antes.h === m.h && !antes.borrado && m.creado - antes.creado < 5 * 60e3 && m.tipo !== 'resumen' && antes.tipo !== 'resumen';
      html += fila(m, cont);
      antes = m;
    });
    feed.querySelector('.ch-feed-in').innerHTML = html;
    cargarImagenes(feed);
    if (sinAnim) S.recien = {};
    if (alFondo || estaba) { feed.scrollTop = feed.scrollHeight; marcarVisto(); }
    else if (Object.keys(S.recien).length) {
      var res = Object.keys(S.recien).map(function (id) { return z.msgs[id]; }).filter(function (m) { return m && m.tipo === 'resumen'; })[0];
      var pill = S.root.querySelector('.ch-nuevos');
      pill.querySelector('span').textContent = res ? 'Nuevo: ' + (res.datos.momento === 'apertura' ? 'resumen antes de la apertura' : 'resumen del cierre') : 'Mensajes nuevos';
      pill.hidden = false;
    }
    S.recien = {};
  }

  function fila(m, cont) {
    var mio = S.yo && m.h === S.yo.h && m.rol !== 'oficial';
    var cls = 'ch-row' + (mio ? ' mio' : '') + (cont ? ' cont' : '') + (S.recien[m.id] ? ' entra' : '') + (m.tipo === 'resumen' ? ' res' : '') + (m.tipo === 'imagen' ? ' img' : '');
    var h = '<div class="' + cls + '" data-id="' + m.id + '">';
    if (!mio) h += cont ? '<span class="ch-av-sp"></span>' : avatar(m, 'sm');
    // Imagen: nunca más alta que ~420 px (una vertical larga queda angosta, no gigante)
    var anchoImg = m.tipo === 'imagen' && m.datos ? Math.round(Math.min(380, 420 * (+m.datos.w || 4) / (+m.datos.h || 5))) : 0;
    h += '<div class="ch-bub' + (m.rol === 'oficial' ? ' of' : '') + (m.borrado ? ' borrado' : '') + '"' + (anchoImg && !m.borrado ? ' style="width:min(' + Math.max(anchoImg, 230) + 'px, 80%)"' : '') + '>';
    if (!mio && !cont) h += '<div class="ch-who"><b style="color:' + (m.rol === 'oficial' || m.rol === 'creador' ? '#e9d3a0' : color(m.h)) + '">' + esc(m.nombre) + '</b>' + chip(m) + '</div>';
    if (m.borrado) {
      h += '<div class="ch-txt"><i>Mensaje eliminado</i><span class="ch-time">' + hora(m.creado) + '</span></div></div></div>';
      return h;
    }
    if (m.cita) h += '<div class="ch-quote" data-a="ir" data-ir-id="' + (m.responde || '') + '"><b>' + esc(m.cita.nombre) + '</b><span>' + esc(m.cita.texto.replace(/[*_]/g, '')) + '</span></div>';
    if (m.tipo === 'resumen' && m.datos) h += resumen(m);
    else if (m.tipo === 'imagen' && m.datos) {
      h += '<button type="button" class="ch-img" data-a="ver-img" aria-label="Ver imagen" style="aspect-ratio:' + (+m.datos.w || 4) + '/' + (+m.datos.h || 5) + '">' +
        '<img alt="" ' + (m.datos.url ? 'src="' + m.datos.url + '"' : 'data-img="' + esc(m.datos.img) + '"') + '>' +
        (m.texto ? '' : '<span class="ch-time">' + (m.pendiente ? 'Enviando' : hora(m.creado)) + '</span>') + '</button>';
      if (m.texto) h += '<div class="ch-txt">' + formato(m.texto, false) + '<span class="ch-time">' + (m.pendiente ? 'Enviando' : hora(m.creado)) + '</span></div>';
      // Pasarla al Canal de WhatsApp: copia la imagen y abre el canal para pegarla; después, el texto.
      // En el celular además está Compartir (imagen + texto juntos, para mandarla a un chat).
      if (esCreador() && !m.pendiente) h += '<div class="ch-res-pie"><span class="ch-res-acc">' +
        '<button type="button" class="ch-share" data-a="copiar-img">' + IC.share + (WA_COMUNIDAD ? 'Copiar y abrir el canal' : 'Copiar imagen') + '</button>' +
        (m.texto ? '<button type="button" class="ch-share" data-a="copiar-txt">' + IC.copy + 'Copiar texto</button>' : '') +
        (window.MiTarjeta.movil ? '<button type="button" class="ch-share" data-a="compartir-img">' + IC.share + 'Compartir</button>' : '') +
        '</span><span></span></div>';
    }
    else h += '<div class="ch-txt">' + formato(m.texto, m.rol === 'oficial') + '<span class="ch-time">' + (m.pendiente ? 'Enviando' : hora(m.creado)) + '</span></div>';
    var re = Object.keys(m.reacciones || {});
    if (re.length) h += '<div class="ch-reacts">' + re.map(function (e) {
      var mia = S.yo && m.reacciones[e].indexOf(S.yo.h) > -1;
      return '<button type="button" class="ch-react' + (mia ? ' mia' : '') + '" data-a="reaccion" data-e="' + e + '">' + e + '<b>' + m.reacciones[e].length + '</b></button>';
    }).join('') + '</div>';
    if (!m.pendiente) h += herramientas(m, mio);
    return h + '</div></div>';
  }

  // Compartir y copiar los resúmenes para el Canal de WhatsApp: solo el creador.
  function esCreador() { return !!(S.yo && S.yo.rol === 'creador'); }

  function resumen(m) {
    var d = m.datos, t = tarjeta(m);
    // el texto completo es el mismo de WhatsApp: arriba la introducción, el resto se despliega
    // el texto completo es el mismo de WhatsApp: arriba la clave y el párrafo, el resto se despliega
    var k = d.texto.indexOf(d.intro), cuerpo = (k > -1 ? d.texto.slice(k + d.intro.length) : d.texto).trim();
    return '<button type="button" class="ch-card' + (t.url ? ' on' : '') + '" data-a="ver" aria-label="Ver la tarjeta en grande">' +
        '<img data-card="' + m.id + '" src="' + (t.url || '') + '" alt="Tarjeta: ' + (d.momento === 'apertura' ? 'antes de la apertura' : 'cierre del mercado') + '"></button>' +
      '<div class="ch-res-k">' + (d.momento === 'apertura' ? 'Antes de la apertura' : 'Cierre del mercado') + '</div>' +
      (d.clave ? '<p class="ch-res-clave">' + esc(d.clave) + '</p>' : '') +
      '<div class="ch-txt">' + formato(d.intro, true) + '</div>' +
      '<details class="ch-det"><summary><span>Ver el resumen completo</span>' + IC.down + '</summary><div class="ch-txt">' + formato(cuerpo, true) + '</div></details>' +
      '<div class="ch-res-pie">' + (esCreador()
        ? '<span class="ch-res-acc"><button type="button" class="ch-share" data-a="copiar-res">' + IC.copy + (WA_COMUNIDAD ? 'Copiar y abrir el canal' : 'Copiar para el canal') + '</button>' +
          '<button type="button" class="ch-share" data-a="compartir">' + IC.share + 'Compartir</button></span>'
        : '<span></span>') + '<span class="ch-time">' + hora(m.creado) + '</span></div>';
  }

  function herramientas(m, mio) {
    var puedeBorrar = S.yo && (mio || S.yo.rol === 'creador');
    if (!usuario() && !puedeBorrar) return '';
    return '<div class="ch-tools" role="toolbar" aria-label="Acciones">' +
      (usuario() ? (SALAS[S.sala].soloCreador && !(S.yo && S.yo.rol === 'creador') ? '' : '<button type="button" data-a="responder" title="Responder" aria-label="Responder">' + IC.reply + '</button>') +
        '<button type="button" data-a="emojis" title="Reaccionar" aria-label="Reaccionar">' + IC.smile + '</button>' : '') +
      (puedeBorrar ? '<button type="button" data-a="borrar" title="Eliminar" aria-label="Eliminar">' + IC.trash + '</button>' : '') +
      '<span class="ch-emojis">' + EMOJIS.map(function (e) { return '<button type="button" data-a="reaccion" data-e="' + e + '">' + e + '</button>'; }).join('') + '</span>' +
    '</div>';
  }

  // ---------- acciones ----------
  function msgDe(el) { var r = el.closest('.ch-row'); return r ? S.salas[S.sala].msgs[r.dataset.id] : null; }
  function clic(e) {
    var b = e.target.closest('[data-a],[data-ir]');
    // en el celular, tocar un mensaje muestra sus acciones
    if (!b) {
      var row = e.target.closest('.ch-row');
      S.root.querySelectorAll('.ch-row.sel').forEach(function (r) { if (r !== row) r.classList.remove('sel', 'emo'); });
      if (row && !e.target.closest('a,summary')) row.classList.toggle('sel');
      return;
    }
    if (b.dataset.ir) { abrir(b.dataset.ir); return; }
    var a = b.dataset.a, m = msgDe(b);
    if (a === 'enviar') return;
    if (a === 'lista') { S.root.querySelector('.ch-app').dataset.vista = 'lista'; return; }
    if (a === 'login') { if (window.showLoginOverlay) window.showLoginOverlay(); return; }
    if (a === 'pagar') { if (typeof window.openPaymentModal === 'function') window.openPaymentModal(); else if (window.showLoginOverlay) window.showLoginOverlay({ motivo: 'pago' }); return; }
    if (a === 'pin') { var x = b.getAttribute('aria-expanded') === 'true'; b.setAttribute('aria-expanded', String(!x)); return; }
    if (a === 'bajar') { var f = S.root.querySelector('.ch-feed'); f.scrollTo({ top: f.scrollHeight, behavior: 'smooth' }); b.hidden = true; return; }
    if (a === 'sin-reply') { S.responde = null; repintarCompositor(); return; }
    if (a === 'tk') { abrirFicha(b.dataset.s); return; }
    if (a === 'tk-cerrar') { cerrarFicha(); return; }
    if (a === 'tk-tf' && S.ficha) {
      S.ficha.tf = b.dataset.tf;
      b.parentNode.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      serieFicha(); return;
    }
    if (a === 'tk-mercados' && S.ficha) {
      var fi = S.ficha; cerrarFicha();
      if (window.mktAbrirActivo) window.mktAbrirActivo(fi.s, fi.cat); else location.hash = 'mercados';
      return;
    }
    if (a === 'sin-adj') { quitarAdjunto(); repintarCompositor(); return; }
    if (a === 'adj-fmt' && S.adjunto) {
      S.adjunto.fmt = b.dataset.f; S.adjunto.ox = S.adjunto.oy = 0.5;
      b.parentNode.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      dibujarAdj(); return;
    }
    if (a === 'ver-img') { var im = b.querySelector('img'); if (!im || !im.src) return; var lb2 = S.root.querySelector('.ch-lb'); lb2.querySelector('img').src = im.src; lb2.hidden = false; return; }
    if ((a === 'copiar-img' || a === 'compartir-img' || a === 'copiar-txt') && m && esCreador()) { pasarAWhatsApp(a, m, b); return; }
    if (a === 'responder' && m) {
      S.responde = { id: m.id, nombre: m.nombre, texto: m.tipo === 'resumen' ? (m.datos.momento === 'apertura' ? 'Resumen antes de la apertura' : 'Resumen del cierre') : m.tipo === 'imagen' && !m.texto ? 'Imagen' : m.texto.replace(/[*_]/g, '').slice(0, 140) };
      repintarCompositor(); var ta = S.root.querySelector('.ch-ta'); if (ta) ta.focus();
      return;
    }
    if (a === 'emojis') { b.closest('.ch-row').classList.toggle('emo'); return; }
    if (a === 'reaccion' && m) { reaccionar(m, b.dataset.e); return; }
    if (a === 'borrar' && m) {
      if (!b.classList.contains('confirmar')) { b.classList.add('confirmar'); b.innerHTML = '¿Eliminar?'; return; }
      api('/chat/' + S.sala + '/' + m.id + '/borrar', { method: 'POST' }).then(function (d) { aplicar(S.sala, [d.mensaje]); pintarFeed(false); pintarLista(); }).catch(function (err) { toast(err.message); });
      return;
    }
    if (a === 'ir-res') {
      var v = leer('mi-res-visto', {}); v[b.dataset.id] = 1; guardar('mi-res-visto', v);
      pintarHoy(); irA(+b.dataset.id); return;
    }
    if (a === 'ir') { var o = S.root.querySelector('.ch-row[data-id="' + b.dataset.irId + '"]'); if (o) resaltar(o); return; }
    if (a === 'ver' && m) { var t = tarjeta(m); if (!t.url) return; var lb = S.root.querySelector('.ch-lb'); lb.querySelector('img').src = t.url; lb.hidden = false; return; }
    if (a === 'copiar-res' && m && esCreador()) {
      // el mensaje entero, igual al de la web (tablas, bonos, agenda y titulares); si faltara, el epígrafe
      var txt = m.datos.texto || window.MiTarjeta.epigrafe(m.datos, m.id);
      (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(function () {
        b.classList.add('ok'); setTimeout(function () { b.classList.remove('ok'); }, 1600);
        toast(abrirCanal() ? 'Copiado. Se abrió el canal: pegalo ahí.' : 'Copiado. Pegalo en el canal de WhatsApp.');
      }, function () { toast('No se pudo copiar. Probá con Compartir.'); });
      return;
    }
    if (a === 'compartir' && m && esCreador()) {
      var tj = tarjeta(m);
      var epi = window.MiTarjeta.epigrafe(m.datos, m.id);
      window.MiTarjeta.compartirImagen(tj.blob, m.datos, epi).then(function (r) {
        if (r === 'descargada') { window.MiTarjeta.compartirTexto(epi); toast('Tarjeta descargada. El texto se abrió en WhatsApp.'); }
      });
    }
  }
  function tecla(e) {
    if (e.target.matches('.ch-ta') && e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); enviar(); }
    if (e.key === 'Escape') { var lb = S.root.querySelector('.ch-lb'); if (!lb.hidden) lb.hidden = true; cerrarFicha(); }
  }
  function abrir(k) {
    S.borrador[S.sala] = (S.root.querySelector('.ch-ta') || {}).value || '';
    S.sala = k; S.responde = null;
    S.root.querySelector('.ch-app').dataset.vista = 'chat';
    pintarLista(); pintarSala(true);
    if (S.salas[k].estado !== 'ok' && S.salas[k].estado !== 'pronto') cargar(k);
  }
  function repintarCompositor() {
    var main = S.root.querySelector('.ch-main');
    S.borrador[S.sala] = (main.querySelector('.ch-ta') || {}).value || S.borrador[S.sala] || '';
    main.querySelectorAll('.ch-reply,.ch-adj,.ch-comp,.ch-login,.ch-toast').forEach(function (n) { n.remove(); });
    main.insertAdjacentHTML('beforeend', compositor());
    var ta = main.querySelector('.ch-ta'); if (ta) ajustar(ta);
    dibujarAdj();
  }
  function ajustar(ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
  function toast(t) {
    var el = S.root.querySelector('.ch-toast'); if (!el) return;
    el.textContent = t; el.classList.add('on'); clearTimeout(S.tt);
    S.tt = setTimeout(function () { el.classList.remove('on'); }, 3200);
  }

  // Cuánta gente hay en la comunidad (registrados en el sitio): arriba del chat de Mercados.
  function cargarGente() {
    fetch('https://log-user.nachito2502.workers.dev/comunidad/cantidad').then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      if (!d || !(d.usuarios > 0)) return;
      S.gente = d.usuarios;
      var el = S.root.querySelector('.ch-gente'); if (!el) return;
      el.querySelector('b').textContent = S.gente.toLocaleString('es-AR'); el.hidden = false;
    }).catch(function () {});
  }

  // ---------- imágenes (solo el creador sube) ----------
  // Se cargan aparte, una vez por sesión: el worker devuelve la data URL y el navegador la arma.
  var IMGS = {};
  function cargarImagenes(feed) {
    feed.querySelectorAll('img[data-img]').forEach(function (el) {
      var k = el.getAttribute('data-img');
      if (!IMGS[k]) IMGS[k] = fetch(API + '/img/' + k).then(function (r) { if (!r.ok) throw new Error(); return r.text(); }).catch(function () { delete IMGS[k]; return ''; });
      IMGS[k].then(function (u) { if (u && el.isConnected) { el.src = u; el.removeAttribute('data-img'); } });
    });
  }
  // La imagen del mensaje en PNG (el portapapeles del navegador solo acepta PNG).
  function imagenPng(el) {
    return new Promise(function (ok, mal) {
      if (!el || !el.src) return mal(new Error('La imagen todavía se está cargando.'));
      var cv = document.createElement('canvas'); cv.width = el.naturalWidth; cv.height = el.naturalHeight;
      cv.getContext('2d').drawImage(el, 0, 0);
      cv.toBlob(function (b) { b ? ok(b) : mal(new Error('No se pudo preparar la imagen.')); }, 'image/png');
    });
  }
  // Abre el Canal de WhatsApp (link de wa.js) en otra pestaña o en la app. Se llama DESPUÉS de copiar:
  // si la página pierde el foco antes, el navegador no deja escribir en el portapapeles.
  function abrirCanal() {
    if (!WA_COMUNIDAD) return false;
    var w = window.open(WA_COMUNIDAD, '_blank');
    if (!w) return false; // el navegador bloqueó la ventana nueva
    try { w.opener = null; } catch (e) {}
    return true;
  }
  function hecho(b, t) { b.classList.add('ok'); setTimeout(function () { b.classList.remove('ok'); }, 1600); toast(t); }
  function pasarAWhatsApp(a, m, b) {
    var texto = m.texto || '';
    if (a === 'copiar-txt') {
      (navigator.clipboard ? navigator.clipboard.writeText(texto) : Promise.reject()).then(function () { hecho(b, 'Texto copiado. Pegalo como epígrafe en WhatsApp.'); }, function () { toast('No se pudo copiar el texto.'); });
      return;
    }
    var el = b.closest('.ch-bub').querySelector('.ch-img img');
    imagenPng(el).then(function (png) {
      if (a === 'compartir-img') {
        var file = new File([png], 'manfredi-' + m.id + '.png', { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          // por si WhatsApp descarta el texto: también queda copiado para pegarlo
          if (texto && navigator.clipboard) navigator.clipboard.writeText(texto).catch(function () {});
          return navigator.share(texto ? { files: [file], text: texto } : { files: [file] }).catch(function () {});
        }
      }
      if (!navigator.clipboard || !window.ClipboardItem) throw new Error('Este navegador no deja copiar imágenes.');
      return navigator.clipboard.write([new ClipboardItem({ 'image/png': png })]).then(function () {
        var abierto = a === 'copiar-img' && abrirCanal();
        hecho(b, (abierto ? 'Imagen copiada y canal abierto: pegala ahí (Ctrl+V)' : 'Imagen copiada. En WhatsApp: Ctrl+V') + (texto ? '. Después tocá Copiar texto para el epígrafe.' : '.'));
      });
    }).catch(function (err) { toast(err.message || 'No se pudo copiar la imagen.'); });
  }

  // ---------- ajustar la imagen antes de mandarla: formato, zoom y encuadre ----------
  var FORMATOS = [{ k: 'orig', t: 'Original' }, { k: '4:5', t: '4:5', r: 4 / 5 }, { k: '1:1', t: '1:1', r: 1 }, { k: '16:9', t: '16:9', r: 16 / 9 }];
  function quitarAdjunto() { if (S.adjunto && S.adjunto.src) URL.revokeObjectURL(S.adjunto.src); S.adjunto = null; }
  function prepararImagen(file) {
    if (!file || !/^image\//.test(file.type)) return;
    var url = URL.createObjectURL(file), img = new Image();
    img.onload = function () {
      quitarAdjunto();
      S.adjunto = { img: img, src: url, nw: img.naturalWidth, nh: img.naturalHeight, fmt: 'orig', zoom: 1, ox: 0.5, oy: 0.5 };
      repintarCompositor();
      var ta = S.root.querySelector('.ch-ta'); if (ta) ta.focus();
    };
    img.onerror = function () { URL.revokeObjectURL(url); toast('No se pudo leer la imagen.'); };
    img.src = url;
  }
  // Dibuja el recorte elegido con el lado más largo en `lado` px.
  function recorte(A, lado) {
    var f = FORMATOS.filter(function (x) { return x.k === A.fmt; })[0];
    var r = f.r || A.nw / A.nh;
    var W = r >= 1 ? lado : Math.round(lado * r), H = Math.round(W / r);
    var s = Math.max(W / A.nw, H / A.nh) * A.zoom, sw = W / s, sh = H / s;
    var cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    var cx = cv.getContext('2d'); cx.fillStyle = '#0b1629'; cx.fillRect(0, 0, W, H);
    cx.drawImage(A.img, (A.nw - sw) * A.ox, (A.nh - sh) * A.oy, sw, sh, 0, 0, W, H);
    return { cv: cv, sw: sw, sh: sh };
  }
  function dibujarAdj() {
    var A = S.adjunto, cv = S.root.querySelector('.ch-adj-cv'); if (!A || !cv) return;
    var r = recorte(A, 520); A._vista = r;
    cv.width = r.cv.width; cv.height = r.cv.height; cv.getContext('2d').drawImage(r.cv, 0, 0);
  }
  // Lo que se sube: lado más largo hasta 1600 px en JPEG; si pesa más de ~900 KB baja la calidad.
  function exportarAdj(A) {
    var cv = recorte(A, Math.min(1600, Math.max(A.nw, A.nh))).cv;
    var q = 0.88, du = cv.toDataURL('image/jpeg', q);
    while (du.length > 1.2e6 && q > 0.45) { q -= 0.1; du = cv.toDataURL('image/jpeg', q); }
    if (du.length > 1.8e6) return null;
    return { url: du, b64: du.split(',')[1], mime: 'image/jpeg', w: cv.width, h: cv.height };
  }
  function editorAdj() {
    var A = S.adjunto;
    return '<div class="ch-adj">' +
      '<div class="ch-adj-marco"><canvas class="ch-adj-cv" title="Arrastrá para encuadrar"></canvas></div>' +
      '<div class="ch-adj-ctl">' +
        '<div class="ch-adj-h"><b>Ajustar imagen</b><button type="button" data-a="sin-adj" aria-label="Quitar imagen">' + IC.x + '</button></div>' +
        '<div class="ch-adj-k">Formato</div>' +
        '<div class="ch-adj-fmt" role="group" aria-label="Formato">' + FORMATOS.map(function (f) {
          return '<button type="button" data-a="adj-fmt" data-f="' + f.k + '"' + (A.fmt === f.k ? ' aria-pressed="true"' : '') + '>' + f.t + '</button>';
        }).join('') + '</div>' +
        '<label class="ch-adj-k" for="ch-adj-zoom">Zoom</label>' +
        '<input id="ch-adj-zoom" class="ch-adj-zoom" type="range" min="1" max="3" step="0.01" value="' + A.zoom + '">' +
        '<p class="ch-adj-ayuda">Arrastrá la imagen para encuadrarla. Abajo podés sumarle un texto.</p>' +
      '</div></div>';
  }
  function moverAdj(dx, dy) {
    var A = S.adjunto, v = A && A._vista, cv = S.root.querySelector('.ch-adj-cv'); if (!v || !cv) return;
    var k = cv.width / cv.getBoundingClientRect().width; // px de pantalla -> px del lienzo
    var fx = A.nw - v.sw, fy = A.nh - v.sh, s = v.cv.width / v.sw;
    if (fx > 0.5) A.ox = Math.min(1, Math.max(0, A.ox - dx * k / s / fx));
    if (fy > 0.5) A.oy = Math.min(1, Math.max(0, A.oy - dy * k / s / fy));
    dibujarAdj();
  }

  function enviar() {
    var ta = S.root.querySelector('.ch-ta'); if (!ta) return;
    var texto = ta.value.trim(); if ((!texto && !S.adjunto) || S.enviando) return;
    var original = S.adjunto, adj = original ? exportarAdj(original) : null;
    if (original && !adj) { toast('La imagen es muy pesada.'); return; }
    var sala = S.sala, z = S.salas[sala], resp = S.responde;
    var tmp = { id: 1e15 + Date.now(), h: S.yo ? S.yo.h : 'yo', nombre: S.yo ? S.yo.nombre : '', rol: S.yo ? S.yo.rol : 'usuario', tipo: adj ? 'imagen' : 'texto', texto: texto,
      datos: adj ? { url: adj.url, w: adj.w, h: adj.h } : null,
      cita: resp ? { nombre: resp.nombre, texto: resp.texto } : null, reacciones: {}, creado: Date.now(), editado: 0, pendiente: true };
    S.enviando = true; ta.value = ''; ajustar(ta); S.borrador[sala] = ''; S.responde = null; S.adjunto = null;
    if (resp || adj) repintarCompositor();
    aplicar(sala, [tmp], true); pintarFeed(true);
    var body = { texto: texto, responde: resp ? resp.id : null };
    if (adj) body.imagen = { mime: adj.mime, b64: adj.b64, w: adj.w, h: adj.h };
    api('/chat/' + sala, { method: 'POST', body: body }).then(function (d) {
      delete z.msgs[tmp.id]; z.orden = z.orden.filter(function (x) { return x !== tmp.id; });
      if (adj && d.mensaje.datos) IMGS[d.mensaje.datos.img] = Promise.resolve(adj.url); // ya la tenemos: no se baja de nuevo
      if (original && S.adjunto !== original) URL.revokeObjectURL(original.src);
      aplicar(sala, [d.mensaje]); pintarFeed(true); pintarLista();
    }).catch(function (err) {
      delete z.msgs[tmp.id]; z.orden = z.orden.filter(function (x) { return x !== tmp.id; });
      pintarFeed(false);
      if (original && !S.adjunto) { S.adjunto = original; repintarCompositor(); }
      var t2 = S.root.querySelector('.ch-ta'); if (t2 && !t2.value) { t2.value = texto; ajustar(t2); }
      toast(err.status === 401 ? 'Tu sesión venció: volvé a iniciar sesión.' : err.message);
    }).then(function () { S.enviando = false; });
  }

  function reaccionar(m, emoji) {
    if (!S.yo) { if (window.showLoginOverlay) window.showLoginOverlay(); return; }
    // optimista: se ve al instante, el servidor confirma
    var re = JSON.parse(JSON.stringify(m.reacciones || {})), yo = S.yo.h;
    var tenia = Object.keys(re).filter(function (e) { return re[e].indexOf(yo) > -1; })[0];
    Object.keys(re).forEach(function (e) { re[e] = re[e].filter(function (x) { return x !== yo; }); if (!re[e].length) delete re[e]; });
    if (tenia !== emoji) (re[emoji] = re[emoji] || []).push(yo);
    var copia = Object.assign({}, m, { reacciones: re, editado: -1 });
    aplicar(S.sala, [copia]); pintarFeed(false);
    api('/chat/' + S.sala + '/' + m.id + '/reaccion', { method: 'POST', body: { emoji: emoji } }).then(function (d) {
      aplicar(S.sala, [d.mensaje]); pintarFeed(false);
    }).catch(function (err) { aplicar(S.sala, [m]); pintarFeed(false); toast(err.message); });
  }

  function alFondoDe(feed) { return feed.scrollHeight - feed.scrollTop - feed.clientHeight < 80; }
  function marcarVisto() {
    var z = S.salas[S.sala], ult = z.orden[z.orden.length - 1];
    if (!ult || ult > 1e14) return;
    if ((z.vistos[S.sala] || 0) < ult) { z.vistos[S.sala] = ult; var v = leer('mi-chat-visto', {}); v[S.sala] = ult; guardar('mi-chat-visto', v); }
  }

  // Próximo resumen (horario de Wall Street en hora argentina) con cuenta regresiva.
  function pintarProximo() {
    var el = S.root.querySelector('.ch-next'); if (!el) return;
    var ahora = Date.now(), artMin = Math.floor(((ahora - 3 * 3600e3) % 864e5) / 6e4), prox = null;
    for (var d = 0; d < 10 && !prox; d++) {
      var h = window.MiTarjeta.horarios(new Date(ahora + d * 864e5));
      if (!h.hay) continue;
      [['apertura', 'Antes de la apertura'], ['cierre', 'Cierre del mercado']].some(function (x) {
        if (d === 0 && h[x[0]].min <= artMin) return false;
        prox = { d: d, t: x[1], hora: h[x[0]].hora, min: h[x[0]].min, iso: h.iso }; return true;
      });
    }
    if (!prox) { el.innerHTML = ''; return; }
    var falta = prox.d * 1440 + prox.min - artMin, hh = Math.floor(falta / 60), mm = falta % 60;
    var nombre = new Date(prox.iso + 'T12:00:00Z').toLocaleDateString('es-AR', { weekday: 'long', timeZone: 'UTC' });
    var cuando = prox.d === 0 ? 'Hoy' : prox.d === 1 ? 'Mañana' : nombre.charAt(0).toUpperCase() + nombre.slice(1);
    el.innerHTML = '<span class="ch-kick">Próximo resumen</span>' +
      '<b>' + prox.t + '</b>' +
      '<span class="ch-next-t"><time>' + cuando + ' · ' + prox.hora + '</time><em>' + (hh >= 24 ? Math.round(hh / 24) + ' d' : (hh ? hh + ' h ' : '') + mm + ' min') + '</em></span>';
  }

  // ---------- alto: el chat ocupa la pantalla, como WhatsApp Web ----------
  // Debajo del menú fijo y de las pestañas de Pro, hasta el borde de abajo de la ventana.
  function menuFijo() {
    var n = document.querySelector('.navbar');
    return n && getComputedStyle(n).position === 'sticky' ? n.offsetHeight : 0;
  }
  function medir() {
    var app = S && S.root.querySelector('.ch-app'); if (!app || app.offsetParent === null) return;
    var top = document.querySelector('#inversiones .pro-top');
    var arriba = menuFijo() + (top ? top.offsetHeight + 14 : 0) + 12;
    app.style.setProperty('--ch-h', Math.max(520, window.innerHeight - arriba - 12) + 'px');
  }
  // Lleva la página hasta las pestañas de Pro, así se ven enteros el chat y la barra para escribir.
  function encuadrar() {
    medir();
    var top = document.querySelector('#inversiones .pro-top'); if (!top || S.root.offsetParent === null) return;
    var y = top.getBoundingClientRect().top + window.scrollY - menuFijo() - 12;
    window.scrollTo({ top: Math.max(0, y), behavior: 'auto' });
  }

  // ---------- ciclo ----------
  function aLaVista() { return S && S.root.offsetParent !== null && !document.hidden; }
  function tic() {
    if (!aLaVista()) return;
    consultar(S.sala);
    // las demás, de a una por vuelta (cada ~15 s alguna)
    var otras = TODAS.filter(function (k) { return k !== S.sala; });
    if (++S.vuelta % 3 === 0) consultar(otras[(S.vuelta / 3) % otras.length]);
  }
  function sesion() { var u = usuario(); return u ? (u.email || u.uid) : ''; }
  function reiniciar() {
    S.yo = null; S.salas = nuevasSalas();
    pintarLista(); pintarSala(true);
    cargarTodas();
  }

  window.ProChat = {
    encuadrar: function () { if (S) encuadrar(); },
    montar: function (el) {
      if (S && S.root === el) {
        // pro.js vuelve a llamar cuando cambia la sesión o la membresía
        if (sesion() !== S.sesion) { S.sesion = sesion(); reiniciar(); }
        return;
      }
      S = { root: el, sala: 'gratis', salas: nuevasSalas(), yo: null, responde: null, borrador: {}, recien: {}, vuelta: 0, sesion: sesion() };
      esqueleto(); pintarLista(); pintarSala(true); pintarProximo();
      cargarTodas();
      cargarGente();
      cargarPrecios();
      setInterval(function () { if (aLaVista()) cargarPrecios(); }, 30e3);
      S.root.querySelector('.ch-ficha').addEventListener('click', function (e) { if (e.target === e.currentTarget) cerrarFicha(); });
      setInterval(tic, 5000);
      setInterval(pintarProximo, 30000);
      setInterval(function () { if (sesion() !== S.sesion) { S.sesion = sesion(); reiniciar(); } }, 1500);
      document.addEventListener('visibilitychange', function () { if (!document.hidden) tic(); });
      window.addEventListener('resize', medir);
      requestAnimationFrame(encuadrar);
      // en la web real el sitio puede volver a subir la página después (router, fuentes, avisos):
      // se encuadra otra vez cuando terminó de cargar, salvo que la persona ya se haya movido
      var y0 = null;
      var otraVez = function () { if (y0 === null || Math.abs(window.scrollY - y0) < 5) { encuadrar(); y0 = window.scrollY; } };
      setTimeout(function () { y0 = window.scrollY; otraVez(); }, 700);
      window.addEventListener('load', function () { setTimeout(otraVez, 200); }, { once: true });
      S.root.querySelector('.ch-lb').addEventListener('click', function (e) { if (e.target === e.currentTarget || e.target.closest('.ch-lb-x')) e.currentTarget.hidden = true; });
      S.root.addEventListener('submit', function (e) { if (e.target.matches('.ch-comp')) { e.preventDefault(); enviar(); } });
      // Imagen: con el botón o pegándola (Ctrl+V) en la caja de texto. Solo el creador.
      S.root.addEventListener('change', function (e) { if (e.target.matches('.ch-file') && esCreador()) { prepararImagen(e.target.files[0]); e.target.value = ''; } });
      S.root.addEventListener('paste', function (e) {
        if (!e.target.matches('.ch-ta') || !esCreador() || !e.clipboardData) return;
        var f = Array.prototype.filter.call(e.clipboardData.items || [], function (it) { return it.kind === 'file' && /^image\//.test(it.type); })[0];
        if (f) { e.preventDefault(); prepararImagen(f.getAsFile()); }
      });
    }
  };
})();
