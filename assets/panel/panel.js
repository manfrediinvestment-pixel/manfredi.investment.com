/* Panel de creador -- manfredinvestment.com
 * Se carga SOLO para cuentas creadoras (ver index.html, window.miEsCreador).
 * Junta datos de: worker memberships (/creador/resumen), log-user (/creador/usuarios),
 * manfredi-admin (/trafico, /workers: Cloudflare) y los endpoints publicos de datos.
 * Cada worker vuelve a validar el rol con el ID token de Firebase.
 */
(function () {
  var LOCAL = location.hostname === 'localhost';
  var API = {
    memb: LOCAL ? 'http://localhost:8787' : 'https://manfredi-memberships.nachito2502.workers.dev',
    users: LOCAL ? 'http://localhost:8788' : 'https://log-user.nachito2502.workers.dev',
    admin: LOCAL ? 'http://localhost:8789' : 'https://manfredi-admin.nachito2502.workers.dev'
  };
  var SALUD = [
    { nombre: 'Cotizaciones (Mercados)', url: 'https://manfredi-mercados.nachito2502.workers.dev/mercados', campo: 'updated', maxHoras: 2 },
    { nombre: 'Noticias', url: 'https://manfredi-noticias.nachito2502.workers.dev/noticias', campo: 'updated', maxHoras: 6 },
    { nombre: 'Calendario', url: 'https://manfredi-calendario.nachito2502.workers.dev/calendario', campo: 'updated', maxHoras: 48 }
  ];

  var root = document.getElementById('panelRoot');
  if (!root) return;

  // ---------- utilidades ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var nf = new Intl.NumberFormat('es-AR');
  function num(n) { return n == null || isNaN(n) ? '—' : nf.format(Math.round(n)); }
  function compact(n) { return n >= 1e6 ? (n / 1e6).toFixed(1).replace('.', ',') + ' M' : n >= 1e4 ? Math.round(n / 1e3) + ' mil' : num(n); }
  function ars(n) { return '$ ' + num(n); }
  function dia(d) { return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short' }).replace('.', ''); }
  function fechaHora(iso) { return iso ? new Date(iso).toLocaleString('es-AR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }) : '—'; }
  function hace(iso) {
    var m = Math.round((Date.now() - new Date(iso)) / 60000);
    if (isNaN(m)) return '—';
    return m < 1 ? 'recién' : m < 60 ? 'hace ' + m + ' min' : m < 1440 ? 'hace ' + Math.round(m / 60) + ' h' : 'hace ' + Math.round(m / 1440) + ' d';
  }
  // Fechas de Google Sheets: "22/9/2026, 20:10:05" o "22/9/2026 20:10" (es-AR)
  function parseAR(s) {
    var m = /(\d{1,2})\/(\d{1,2})\/(\d{2,4})(?:[ ,]+(\d{1,2}):(\d{2}))?/.exec(s || '');
    if (!m) { var d = new Date(s); return isNaN(d) ? null : d; }
    var y = +m[3] < 100 ? 2000 + +m[3] : +m[3];
    return new Date(y, +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0));
  }
  function inicioSemana(d) { var x = new Date(d); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; }
  function claveMes(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }
  function nombreMes(k) { var p = k.split('-'); return new Date(+p[0], +p[1] - 1, 1).toLocaleDateString('es-AR', { month: 'short' }).replace('.', ''); }

  function get(base, path) {
    var u = window._currentUser;
    if (!u || !u.getIdToken) return Promise.reject(new Error('Sin sesión'));
    return u.getIdToken().then(function (t) {
      return fetch(base + path, { headers: { Authorization: 'Bearer ' + t } });
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) { var e = new Error(d.mensaje || d.error || ('HTTP ' + r.status)); e.code = d.error; e.status = r.status; throw e; }
        return d;
      });
    });
  }

  // ---------- graficos (SVG, una serie, tooltip propio por marca via data-tip) ----------
  // barras verticales: data = [{ label, value, tip }]
  function barras(data, opt) {
    opt = opt || {};
    var W = opt.w || 460, H = opt.h || 180, L = 44, R = 8, T = 12, B = 26;
    var max = Math.max.apply(null, data.map(function (d) { return d.value; }).concat([1]));
    var paso = niceMax(max), iw = W - L - R, ih = H - T - B, bw = iw / data.length, gap = Math.min(6, bw * .25);
    var cada = Math.ceil(data.length / (opt.labels || 8));
    var s = '<svg class="pn-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(opt.aria || '') + '">';
    [0, .5, 1].forEach(function (f) {
      var y = T + ih - ih * f;
      s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '" class="pn-grid"/>' +
        '<text x="' + (L - 8) + '" y="' + (y + 3.5) + '" class="pn-axis" text-anchor="end">' + esc(opt.fmt ? opt.fmt(paso * f) : compact(paso * f)) + '</text>';
    });
    data.forEach(function (d, i) {
      var h = d.value > 0 ? Math.max(2, ih * d.value / paso) : 0, x = L + i * bw + gap / 2, w = bw - gap, y = T + ih - h;
      var r = Math.min(4, w / 2, h);
      s += '<g class="pn-mark" data-tip="' + esc(d.tip || (d.label + ': ' + num(d.value))) + '"><rect x="' + (L + i * bw) + '" y="' + T + '" width="' + bw + '" height="' + ih + '" fill="transparent"/>' +
        (h ? '<path d="M' + x + ',' + (T + ih) + 'V' + (y + r) + 'Q' + x + ',' + y + ' ' + (x + r) + ',' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (T + ih) + 'Z" class="pn-bar"/>' : '') +
        '</g>';
      if ((i % cada === 0 && data.length - 1 - i >= cada / 2) || i === data.length - 1) s += '<text x="' + (L + i * bw + bw / 2) + '" y="' + (H - 8) + '" class="pn-axis" text-anchor="middle">' + esc(d.label) + '</text>';
    });
    return s + '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + (T + ih) + '" y2="' + (T + ih) + '" class="pn-base"/></svg>';
  }
  // area + linea: data = [{ label, value, tip }]
  function area(data, opt) {
    opt = opt || {};
    var W = opt.w || 460, H = opt.h || 180, L = 44, R = 12, T = 12, B = 26;
    var max = Math.max.apply(null, data.map(function (d) { return d.value; }).concat([1]));
    var paso = niceMax(max), iw = W - L - R, ih = H - T - B;
    var X = function (i) { return L + (data.length < 2 ? iw / 2 : iw * i / (data.length - 1)); };
    var Y = function (v) { return T + ih - ih * v / paso; };
    var pts = data.map(function (d, i) { return X(i).toFixed(1) + ',' + Y(d.value).toFixed(1); });
    var cada = Math.ceil(data.length / (opt.labels || 6));
    var s = '<svg class="pn-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(opt.aria || '') + '">' +
      '<defs><linearGradient id="pnFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#F2C94C" stop-opacity=".28"/><stop offset="1" stop-color="#F2C94C" stop-opacity="0"/></linearGradient></defs>';
    [0, .5, 1].forEach(function (f) {
      var y = T + ih - ih * f;
      s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '" class="pn-grid"/><text x="' + (L - 8) + '" y="' + (y + 3.5) + '" class="pn-axis" text-anchor="end">' + compact(paso * f) + '</text>';
    });
    if (data.length) {
      s += '<path d="M' + X(0) + ',' + (T + ih) + 'L' + pts.join('L') + 'L' + X(data.length - 1) + ',' + (T + ih) + 'Z" fill="url(#pnFill)"/>' +
        '<polyline points="' + pts.join(' ') + '" class="pn-line"/>';
      var last = data.length - 1;
      s += '<circle cx="' + X(last) + '" cy="' + Y(data[last].value) + '" r="4.5" class="pn-dot"/>';
      data.forEach(function (d, i) {
        var bw = iw / Math.max(1, data.length - 1);
        s += '<g class="pn-hit" data-tip="' + esc(d.tip || (d.label + ': ' + num(d.value))) + '"><rect x="' + (X(i) - bw / 2) + '" y="' + T + '" width="' + bw + '" height="' + ih + '" fill="transparent"/><line x1="' + X(i) + '" x2="' + X(i) + '" y1="' + T + '" y2="' + (T + ih) + '" class="pn-cross"/><circle cx="' + X(i) + '" cy="' + Y(d.value) + '" r="4" class="pn-dot"/></g>';
        if (i % cada === 0 || i === last) s += '<text x="' + X(i) + '" y="' + (H - 8) + '" class="pn-axis" text-anchor="' + (i === 0 ? 'start' : i === last ? 'end' : 'middle') + '">' + esc(d.label) + '</text>';
      });
    }
    return s + '</svg>';
  }
  function niceMax(v) { var p = Math.pow(10, Math.floor(Math.log10(v || 1))), n = v / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * p; }
  // ranking horizontal (texto + barra proporcional)
  function ranking(rows, opt) {
    opt = opt || {};
    if (!rows.length) return '<p class="pn-empty">' + esc(opt.vacio || 'Sin datos todavía.') + '</p>';
    var max = Math.max.apply(null, rows.map(function (r) { return r.value; }).concat([1]));
    return '<ul class="pn-rank">' + rows.map(function (r) {
      return '<li title="' + esc(r.label + ': ' + num(r.value)) + '"><span class="pn-rank-l">' + esc(r.label) + '</span><span class="pn-rank-v">' + (opt.fmt ? opt.fmt(r.value) : num(r.value)) + '</span><span class="pn-rank-b"><i style="width:' + (100 * r.value / max).toFixed(1) + '%"></i></span></li>';
    }).join('') + '</ul>';
  }
  function tabla(cols, rows, vacio) {
    if (!rows.length) return '<p class="pn-empty">' + esc(vacio || 'Sin datos todavía.') + '</p>';
    return '<div class="pn-table-wrap"><table class="pn-table"><thead><tr>' + cols.map(function (c) { return '<th' + (c.num ? ' class="n"' : '') + '>' + esc(c.t) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr>' + cols.map(function (c) { return '<td' + (c.num ? ' class="n"' : '') + '>' + (c.html ? c.html(r) : esc(c.v(r))) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function kpi(label, valor, sub, estado) {
    return '<div class="pn-kpi' + (estado ? ' ' + estado : '') + '"><span class="pn-kpi-l">' + esc(label) + '</span><span class="pn-kpi-v">' + valor + '</span><span class="pn-kpi-s">' + (sub || '&nbsp;') + '</span></div>';
  }
  function bloque(id, titulo, fuente, ancho) {
    return '<section class="pn-card' + (ancho ? ' pn-wide' : '') + '" id="pn-' + id + '"><header><h3>' + esc(titulo) + '</h3><span class="pn-src">' + esc(fuente) + '</span></header><div class="pn-body"><div class="pn-loading">Cargando…</div></div></section>';
  }
  function set(id, html) { var el = document.querySelector('#pn-' + id + ' .pn-body'); if (el) el.innerHTML = html; }
  function error(id, e) { set(id, '<p class="pn-err">No se pudo cargar: ' + esc(e && e.message || e) + '</p>'); }
  function chip(txt, cls) { return '<span class="pn-chip ' + (cls || '') + '">' + esc(txt) + '</span>'; }

  // ---------- estructura ----------
  function esqueleto() {
    root.innerHTML =
      '<div class="pn-kpis" id="pnKpis"></div>' +
      '<div class="pn-grid">' +
        bloque('trafico', 'Tráfico del sitio · 30 días', 'Cloudflare', true) +
        bloque('ingresos', 'Ingresos', 'Mercado Pago') +
        bloque('socios', 'Socios', 'Membresías + Mercado Pago') +
        bloque('usuarios', 'Usuarios registrados', 'Google Sheets · hoja Usuarios') +
        bloque('pedidos', 'Pedidos de informes', 'Panel de creador') +
        bloque('warren', 'Uso de Warren IA · este mes', 'Membresías') +
        bloque('contenido', 'Informes publicados', 'Sitio') +
        bloque('salud', 'Estado técnico', 'Workers + Cloudflare', true) +
      '</div>';
  }

  var K = {};  // valores para la fila de KPIs
  function pintarKpis() {
    var el = document.getElementById('pnKpis'); if (!el) return;
    el.innerHTML =
      kpi('Socios activos', K.socios == null ? '…' : num(K.socios), K.sociosSub) +
      kpi('Ingresos 30 días', K.ingresos == null ? '…' : ars(K.ingresos), K.ingresosSub) +
      kpi('Usuarios registrados', K.usuarios == null ? '…' : num(K.usuarios), K.usuariosSub) +
      kpi(K.visitasLabel || 'Visitas 30 días', K.visitas == null ? '—' : compact(K.visitas), K.visitasSub || 'Requiere token de Cloudflare') +
      kpi('Pedidos abiertos', K.pedidos == null ? '…' : num(K.pedidos), K.pedidosSub, K.pedidosVencidos ? 'warn' : '') +
      kpi('Consultas a Warren', K.warren == null ? '…' : num(K.warren), 'en el mes');
  }

  // ---------- carga ----------
  function cargarTodo() {
    esqueleto(); K = {}; pintarKpis();
    var sello = document.getElementById('panelUpdated');
    if (sello) sello.textContent = 'Actualizado ' + new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });

    // 1) Membresias: socios, pagos, suscripciones, warren, pedidos
    get(API.memb, '/creador/resumen').then(function (d) {
      renderIngresos(d); renderSocios(d); renderWarren(d); renderPedidos(d);
    }).catch(function (e) { ['ingresos', 'socios', 'warren', 'pedidos'].forEach(function (b) { error(b, e); }); K.socios = K.ingresos = K.pedidos = K.warren = NaN; pintarKpis(); });

    // 2) Usuarios (Sheets)
    get(API.users, '/creador/usuarios').then(renderUsuarios).catch(function (e) { error('usuarios', e); K.usuarios = NaN; pintarKpis(); });

    // 3) Cloudflare
    get(API.admin, '/trafico').then(renderTrafico).catch(function (e) {
      if (e.code === 'sin_token' || e.status === 503 || e.message === 'Failed to fetch') set('trafico', setupCloudflare(e));
      else error('trafico', e);
    });

    renderContenido();
    renderSalud();
  }

  function setupCloudflare(e) {
    return '<div class="pn-setup"><p><b>Falta conectar Cloudflare.</b> Con eso ves visitas por día, páginas más vistas, de dónde llega la gente, países y dispositivos.</p><ol>' +
      '<li>Cloudflare → <b>Workers &amp; Pages</b> → tu proyecto del sitio → <b>Metrics</b> → activá <b>Web Analytics</b> (gratis).</li>' +
      '<li>Cloudflare → <b>My Profile → API Tokens → Create Token → Custom</b>, solo lectura: <i>Account Analytics: Read</i>, <i>Workers Scripts: Read</i>, <i>Zone: Read</i> y <i>Analytics: Read</i> de la zona manfredinvestment.com.</li>' +
      '<li>En la terminal: <code>npx wrangler secret put CF_API_TOKEN --config workers/admin/wrangler.toml</code> y pegá el token.</li>' +
      '<li>Deploy: <code>npx wrangler deploy --config workers/admin/wrangler.toml</code></li></ol>' +
      '<p class="pn-muted">Detalle: ' + esc(e && e.message) + '</p></div>';
  }

  function renderTrafico(d) {
    var html = '';
    if (d.web && d.web.serie.length) {
      var tot = d.web.serie.reduce(function (a, g) { return a + g.visitas; }, 0), vistas = d.web.serie.reduce(function (a, g) { return a + g.vistas; }, 0);
      K.visitas = tot; K.visitasSub = num(vistas) + ' páginas vistas · sin bots'; pintarKpis();
      html += '<div class="pn-sub">Visitas por día <span class="pn-muted">(personas reales en el navegador, sin bots · pasá el mouse por una barra)</span></div>' +
        barras(d.web.serie.map(function (g) { var f = new Date(g.fecha + 'T12:00:00'); return { label: dia(f), value: g.visitas, tip: dia(f) + ' · ' + num(g.visitas) + ' visitas · ' + num(g.vistas) + ' páginas vistas' }; }), { aria: 'Visitas por día', w: 900, h: 220, labels: 8 }) +
        '<div class="pn-cols3"><div><div class="pn-sub">Páginas más vistas</div>' + ranking(d.web.paginas.map(function (p) { return { label: p.ruta, value: p.vistas }; })) + '</div>' +
        '<div><div class="pn-sub">De dónde llegan</div>' + ranking(d.web.origen.map(function (p) { return { label: p.origen, value: p.visitas }; })) + '</div>' +
        '<div><div class="pn-sub">Países</div>' + ranking(d.web.paises.map(function (p) { return { label: p.pais, value: p.visitas }; })) +
        '<div class="pn-sub" style="margin-top:14px">Dispositivos</div>' + ranking(d.web.dispositivos.map(function (p) { return { label: p.tipo, value: p.visitas }; })) + '</div></div>';
    }
    var errs = Object.keys(d.errores || {}).map(function (k) { return 'Web Analytics: ' + d.errores[k]; });
    if (errs.length) html += '<p class="pn-muted" style="margin-top:12px">' + esc(errs.join(' · ')) + '</p>';
    set('trafico', html || '<p class="pn-empty">Cloudflare respondió sin datos todavía.</p>');
  }

  function renderIngresos(d) {
    var ok = (d.pagos || []).filter(function (p) { return p.estado === 'approved'; });
    var hace30 = Date.now() - 30 * 86400e3;
    var ars30 = ok.filter(function (p) { return new Date(p.fecha) >= hace30 && p.moneda === 'ARS'; }).reduce(function (a, p) { return a + (p.monto || 0); }, 0);
    K.ingresos = d.errores && d.errores.pagos ? NaN : ars30;
    K.ingresosSub = ok.filter(function (p) { return new Date(p.fecha) >= hace30; }).length + ' pagos aprobados';
    pintarKpis();
    if (d.errores && d.errores.pagos) { error('ingresos', d.errores.pagos); return; }
    var meses = {}, hoy = new Date();
    for (var i = 5; i >= 0; i--) meses[claveMes(new Date(hoy.getFullYear(), hoy.getMonth() - i, 1))] = 0;
    ok.forEach(function (p) { var k = claveMes(new Date(p.fecha)); if (k in meses && p.moneda === 'ARS') meses[k] += p.monto || 0; });
    var codigos = {};
    ok.forEach(function (p) { if (p.codigo) codigos[p.codigo] = (codigos[p.codigo] || 0) + 1; });
    var rech = (d.pagos || []).filter(function (p) { return p.estado === 'rejected'; }).length;
    set('ingresos',
      '<div class="pn-sub">Ingresos por mes (ARS aprobados)</div>' +
      barras(Object.keys(meses).map(function (k) { return { label: nombreMes(k), value: meses[k], tip: nombreMes(k) + ': ' + ars(meses[k]) }; }), { fmt: compact, aria: 'Ingresos por mes' }) +
      '<div class="pn-chips">' + chip(ok.length + ' aprobados (180 d)', 'ok') + (rech ? chip(rech + ' rechazados', 'bad') : '') +
        Object.keys(codigos).map(function (c) { return chip(c + ': ' + codigos[c] + ' usos', 'gold'); }).join('') + '</div>' +
      '<div class="pn-sub">Últimos pagos</div>' +
      tabla([
        { t: 'Fecha', v: function (p) { return new Date(p.fecha).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' }); } },
        { t: 'Socio', v: function (p) { return p.email || '—'; } },
        { t: 'Plan', v: function (p) { return p.meses ? p.meses + (p.meses == 1 ? ' mes' : ' meses') : (p.concepto || '').slice(0, 24); } },
        { t: 'Monto', num: true, v: function (p) { return (p.moneda === 'ARS' ? '$ ' : p.moneda + ' ') + num(p.monto); } },
        { t: 'Estado', html: function (p) { return chip({ approved: 'Aprobado', rejected: 'Rechazado', pending: 'Pendiente', in_process: 'En proceso', refunded: 'Devuelto', cancelled: 'Cancelado' }[p.estado] || p.estado, p.estado === 'approved' ? 'ok' : p.estado === 'rejected' ? 'bad' : ''); } }
      ], (d.pagos || []).slice(0, 8), 'Todavía no hay pagos en los últimos 180 días.'));
  }

  function renderSocios(d) {
    var socios = (d.socios || []).slice().sort(function (a, b) { return (a.vence || '').localeCompare(b.vence || ''); });
    var en7 = socios.filter(function (s) { return s.vence && new Date(s.vence) - Date.now() < 7 * 86400e3; }).length;
    var subs = d.suscripciones || [], est = {};
    subs.forEach(function (s) { est[s.estado] = (est[s.estado] || 0) + 1; });
    K.socios = socios.length;
    K.sociosSub = socios.filter(function (s) { return s.recurrente; }).length + ' con débito automático' + (en7 ? ' · ' + en7 + ' vencen en 7 d' : '');
    pintarKpis();
    var nombres = { authorized: 'Activas', paused: 'Pausadas', cancelled: 'Canceladas', pending: 'Pendientes' };
    set('socios',
      '<div class="pn-chips">' + (subs.length ? Object.keys(est).map(function (k) { return chip((nombres[k] || k) + ': ' + est[k], k === 'authorized' ? 'ok' : k === 'cancelled' ? 'bad' : ''); }).join('') : chip(d.errores && d.errores.suscripciones ? 'Suscripciones MP: ' + d.errores.suscripciones : 'Sin suscripciones recurrentes', '')) + '</div>' +
      tabla([
        { t: 'Socio', v: function (s) { return s.email; } },
        { t: 'Vence', html: function (s) { var dias = s.vence ? Math.round((new Date(s.vence) - Date.now()) / 86400e3) : null; return s.vence ? esc(new Date(s.vence).toLocaleDateString('es-AR')) + ' <span class="pn-muted">(' + dias + ' d)</span>' : '—'; } },
        { t: 'Pago', html: function (s) { return s.recurrente ? chip('Débito automático', 'ok') : chip('Prepago', ''); } }
      ], socios.slice(0, 10), 'Todavía no hay socios activos.') +
      (socios.length > 10 ? '<p class="pn-muted" style="margin:8px 0 0">y ' + (socios.length - 10) + ' socios más</p>' : ''));
  }

  function renderWarren(d) {
    var w = d.warren || [], tot = w.reduce(function (a, x) { return a + x.usadas; }, 0);
    K.warren = tot; pintarKpis();
    set('warren', '<div class="pn-chips">' + chip(w.length + (w.length === 1 ? ' persona lo usó' : ' personas lo usaron'), 'gold') + chip(num(tot) + ' consultas', '') + '</div>' +
      ranking(w.slice(0, 10).map(function (x) { return { label: x.email, value: x.usadas }; }), { vacio: 'Nadie usó Warren este mes todavía.', fmt: function (v) { return num(v) + ' / 100'; } }));
  }

  function renderPedidos(d) {
    var p = d.pedidos || [], ab = p.filter(function (x) { return x.estado === 'pendiente' || x.estado === 'en_proceso'; });
    var venc = ab.filter(function (x) { return new Date(x.vence) < Date.now(); }).length;
    var hechos = p.filter(function (x) { return x.estado === 'hecho' && x.hecho; });
    var prom = hechos.length ? hechos.reduce(function (a, x) { return a + (new Date(x.hecho) - new Date(x.creado)); }, 0) / hechos.length / 3600e3 : null;
    var aTiempo = hechos.filter(function (x) { return new Date(x.hecho) <= new Date(x.vence); }).length;
    K.pedidos = ab.length; K.pedidosVencidos = venc; K.pedidosSub = venc ? venc + ' fuera de plazo' : 'plazo 48 hs'; pintarKpis();
    var tks = {};
    p.forEach(function (x) { tks[x.ticker] = (tks[x.ticker] || 0) + 1; });
    set('pedidos',
      '<div class="pn-chips">' + chip(ab.length + ' abiertos', ab.length ? 'gold' : '') + (venc ? chip(venc + ' vencidos', 'bad') : '') + chip(hechos.length + ' publicados', 'ok') +
        (prom != null ? chip('Entrega promedio: ' + prom.toFixed(1).replace('.', ',') + ' h', '') : '') + (hechos.length ? chip(Math.round(100 * aTiempo / hechos.length) + '% a tiempo', aTiempo === hechos.length ? 'ok' : 'bad') : '') + '</div>' +
      '<div class="pn-sub">Lo más pedido</div>' +
      ranking(Object.keys(tks).map(function (k) { return { label: k, value: tks[k] }; }).sort(function (a, b) { return b.value - a.value; }).slice(0, 8), { vacio: 'Todavía no hay pedidos.' }) +
      '<p style="margin:12px 0 0"><a class="pn-link" href="#inversiones" data-tab-target="inversiones">Gestionar pedidos en Informes →</a></p>');
  }

  function renderUsuarios(d) {
    var u = (d.usuarios || []).map(function (x) { x._f = parseAR(x.fecha); return x; });
    var reales = u.filter(function (x) { return !/notificaciones/i.test(x.fuente); }), avisos = u.length - reales.length;
    var hace7 = Date.now() - 7 * 86400e3, n7 = reales.filter(function (x) { return x._f && x._f >= hace7; }).length;
    K.usuarios = reales.length; K.usuariosSub = '+' + n7 + ' en 7 días' + (avisos ? ' · ' + avisos + ' solo avisos' : ''); pintarKpis();
    var semanas = {}, hoy = inicioSemana(new Date());
    for (var i = 11; i >= 0; i--) { var s = new Date(hoy); s.setDate(s.getDate() - 7 * i); semanas[s.getTime()] = 0; }
    reales.forEach(function (x) { if (!x._f) return; var k = inicioSemana(x._f).getTime(); if (k in semanas) semanas[k]++; });
    var socios = reales.filter(function (x) { return x.miembro; }).length;
    set('usuarios',
      '<div class="pn-sub">Registros por semana · últimas 12</div>' +
      barras(Object.keys(semanas).map(function (k) { var f = new Date(+k); return { label: dia(f), value: semanas[k], tip: 'Semana del ' + dia(f) + ': ' + semanas[k] + ' registros' }; }), { aria: 'Registros por semana', labels: 6 }) +
      '<div class="pn-chips">' + chip(reales.length ? Math.round(100 * socios / reales.length) + '% son socios' : '0% socios', 'gold') + chip((d.miembros || []).length + ' en hoja Miembros', '') + '</div>' +
      '<div class="pn-sub">Últimos registrados</div>' +
      tabla([
        { t: 'Fecha', v: function (x) { return x.fecha.split(',')[0]; } },
        { t: 'Nombre', v: function (x) { return x.nombre || '—'; } },
        { t: 'Email', v: function (x) { return x.email; } },
        { t: '', html: function (x) { return x.miembro ? chip('Socio', 'ok') : ''; } }
      ], reales.slice().sort(function (a, b) { return (b._f || 0) - (a._f || 0); }).slice(0, 8)));
  }

  function renderContenido() {
    var por = {}, total = 0, prox = 0, nombres = {};
    document.querySelectorAll('#invTabs .mkt-tab').forEach(function (b) { nombres[b.getAttribute('data-sector')] = b.textContent.trim(); });
    document.querySelectorAll('#inversiones .inv-panel').forEach(function (panel) {
      var s = panel.getAttribute('data-sector-panel'), n = panel.querySelectorAll('.pick-card a.pick-btn').length;
      por[s] = n; total += n; prox += panel.querySelectorAll('.pick-card').length - n;
    });
    set('contenido', '<div class="pn-chips">' + chip(total + ' publicados', 'ok') + chip(prox + ' próximamente', '') + '</div>' +
      ranking(Object.keys(por).map(function (k) { return { label: nombres[k] || k, value: por[k] }; }).sort(function (a, b) { return b.value - a.value; })));
  }

  function renderSalud() {
    set('salud', '<div class="pn-health" id="pnHealth"></div><div class="pn-sub" style="margin-top:18px">Workers · últimos 7 días</div><div id="pnWorkers"><div class="pn-loading">Cargando…</div></div>');
    var box = document.getElementById('pnHealth');
    box.innerHTML = SALUD.map(function (s, i) { return '<div class="pn-hc" id="pnHc' + i + '"><span class="pn-hc-dot"></span><div><b>' + esc(s.nombre) + '</b><span>Chequeando…</span></div></div>'; }).join('');
    SALUD.forEach(function (s, i) {
      var t0 = performance.now();
      fetch(s.url, { cache: 'no-store' }).then(function (r) { return r.json().then(function (d) { return { r: r, d: d }; }); }).then(function (x) {
        var ms = Math.round(performance.now() - t0), upd = x.d && (x.d[s.campo] || x.d.actualizado || x.d.fecha);
        var viejo = upd && !isNaN(new Date(upd)) && (Date.now() - new Date(upd)) / 3600e3 > s.maxHoras;
        var el = document.getElementById('pnHc' + i);
        el.className = 'pn-hc ' + (!x.r.ok ? 'bad' : viejo ? 'warn' : 'ok');
        el.querySelector('span:last-child').textContent = (x.r.ok ? (viejo ? 'Desactualizado · ' : 'Funcionando · ') : 'Error ' + x.r.status + ' · ') + (upd && !isNaN(new Date(upd)) ? 'datos ' + hace(upd) : 'responde') + ' · ' + ms + ' ms';
      }).catch(function (e) {
        var el = document.getElementById('pnHc' + i); el.className = 'pn-hc bad';
        el.querySelector('span:last-child').textContent = 'No responde (' + e.message + ')';
      });
    });
    get(API.admin, '/workers').then(function (d) {
      document.getElementById('pnWorkers').innerHTML = tabla([
        { t: 'Worker', v: function (w) { return w.worker; } },
        { t: 'Pedidos', num: true, v: function (w) { return num(w.requests); } },
        { t: 'Errores', num: true, html: function (w) { var pct = w.requests ? 100 * w.errores / w.requests : 0; return num(w.errores) + (w.errores ? ' <span class="' + (pct > 2 ? 'pn-bad' : 'pn-muted') + '">(' + pct.toFixed(1).replace('.', ',') + '%)</span>' : ''); } },
        { t: 'CPU p50', num: true, v: function (w) { return (w.cpuP50 / 1000).toFixed(1).replace('.', ',') + ' ms'; } }
      ], d.workers || []);
    }).catch(function (e) {
      document.getElementById('pnWorkers').innerHTML = '<p class="pn-muted">' + (e.code === 'sin_token' || e.status === 503 || e.message === 'Failed to fetch' ? 'Se activa al conectar Cloudflare (ver arriba).' : 'No se pudo cargar: ' + esc(e.message)) + '</p>';
    });
  }

  // ---------- tooltip de los graficos: aparece al instante sobre la marca (mouse o toque) ----------
  var tip = document.createElement('div');
  tip.className = 'pn-tooltip';
  tip.setAttribute('role', 'status');
  document.body.appendChild(tip);
  function mostrarTip(e) {
    var g = e.target.closest && e.target.closest('.pn-chart [data-tip]');
    if (!g) { tip.classList.remove('on'); return; }
    tip.textContent = g.getAttribute('data-tip');
    var r = (g.querySelector('.pn-bar, .pn-dot') || g).getBoundingClientRect();
    tip.classList.add('on');
    var x = Math.min(Math.max(8, r.left + r.width / 2 - tip.offsetWidth / 2), window.innerWidth - tip.offsetWidth - 8);
    tip.style.left = x + 'px';
    tip.style.top = Math.max(8, r.top - tip.offsetHeight - 8) + 'px';
  }
  document.addEventListener('mouseover', mostrarTip);
  document.addEventListener('click', mostrarTip);
  window.addEventListener('scroll', function () { tip.classList.remove('on'); }, { passive: true });

  // ---------- arranque ----------
  var btn = document.getElementById('panelRefresh');
  if (btn) btn.addEventListener('click', cargarTodo);
  window.miPanelCargar = cargarTodo;
  cargarTodo();
})();
