/* Bienvenida: presentación de la página para quien entra por primera vez y no
   está registrado. Se monta en un Shadow DOM (igual que cartel y ayuda) para
   que su CSS quede aislado. Usa datos reales de los workers de mercados,
   noticias y calendario; la cartera y la charla con Warren son de ejemplo y lo
   dicen en pantalla.
   Dos formatos para elegir:  A = recorrido por pasos · B = una sola pantalla.
   Test: ?bienvenida=a o ?bienvenida=b la abre siempre (aunque estés logueado). */
(function () {
  var VARIANTE_POR_DEFECTO = 'a';
  var KEY_VISTA = 'mi_bienvenida_vista';
  var API = {
    mercados: 'https://manfredi-mercados.nachito2502.workers.dev/mercados',
    noticias: 'https://manfredi-noticias.nachito2502.workers.dev/noticias',
    calendario: 'https://manfredi-calendario.nachito2502.workers.dev/calendario'
  };
  var INFORMES = ['nvda','aapl','msft','googl','amzn','meta','tsla','avgo','tsm','amd','meli','jpm','ko','brk-b','lly','v','ma','nflx','orcl','pltr','wmt','pg','unh','dis','shop','crwd','asml','mu','gs','jnj'];

  var q = new URLSearchParams(location.search);
  var forzada = (q.get('bienvenida') || '').toLowerCase();
  var variante = forzada === 'b' ? 'b' : forzada === 'a' ? 'a' : VARIANTE_POR_DEFECTO;
  var RM = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- ¿mostrarla? ---------- */
  function esperarAuth() {
    return new Promise(function (res) {
      var t0 = Date.now();
      (function chk() {
        if (window._currentUser) return res('user');
        if (window._currentUser === null) return res('anon');
        if (Date.now() - t0 > 4500) return res('anon');
        setTimeout(chk, 150);
      })();
    });
  }

  function arrancar() {
    if (forzada === 'a' || forzada === 'b') return abrir();
    if (ls(KEY_VISTA) || ls('mi_member_token')) return;
    esperarAuth().then(function (estado) {
      if (estado === 'user') { ls(KEY_VISTA, 'registrado'); return; }
      if (ls(KEY_VISTA) || ls('mi_member_token')) return;
      abrir();
    });
  }

  /* ---------- datos ---------- */
  function getJSON(url) {
    var ctl = window.AbortController ? new AbortController() : null;
    if (ctl) setTimeout(function () { ctl.abort(); }, 8000);
    return fetch(url, ctl ? { signal: ctl.signal } : {}).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  var datos = Promise.all([getJSON(API.mercados), getJSON(API.noticias), getJSON(API.calendario)]).then(function (r) {
    return armarDatos(r[0], r[1], r[2]);
  });

  function armarDatos(m, n, c) {
    var D = { ok: !!m, dolares: [], indices: [], movers: [], total: 0, noticias: [], agenda: null, hora: '' };
    if (m && m.categorias) {
      var cat = m.categorias;
      var dol = (cat.dolares && cat.dolares.items) || [];
      [['OFICIAL', 'Oficial'], ['BOLSA', 'MEP'], ['CONTADOCONLIQUI', 'CCL'], ['BLUE', 'Blue']].forEach(function (p) {
        var it = dol.filter(function (x) { return x.symbol === p[0]; })[0];
        if (it) D.dolares.push({ n: p[1], v: it.price });
      });
      var fe = m.featured || [];
      [['merval', 'Merval'], ['sp500', 'S&P 500'], ['nasdaq', 'Nasdaq 100'], ['btc', 'Bitcoin'], ['oro', 'Oro']].forEach(function (p) {
        var it = fe.filter(function (x) { return x.id === p[0]; })[0];
        if (it && it.change != null) D.indices.push({ n: p[1], c: it.change, v: it.price, id: p[0] });
      });
      var ced = ((cat.arg_cedears && cat.arg_cedears.items) || []).concat((cat.arg_stocks && cat.arg_stocks.items) || []);
      var vistos = {};
      D.movers = ced.filter(function (x) { return x.change != null && x.volume > 0; })
        .sort(function (a, b) { return Math.abs(b.change) - Math.abs(a.change); })
        .filter(function (x) {
          var base = /^[A-Z]{2,5}[DC]$/.test(x.symbol) && ced.some(function (y) { return y.symbol === x.symbol.slice(0, -1); }) ? x.symbol.slice(0, -1) : x.symbol;
          if (vistos[base]) return false; vistos[base] = 1; return true;
        }).slice(0, 4)
        .map(function (x) { return { s: x.symbol, n: x.name && x.name !== x.symbol ? x.name : 'CEDEAR', c: x.change }; });
      Object.keys(cat).forEach(function (k) { D.total += (cat[k].items || []).length; });
      if (m.updated) { var d = new Date(m.updated); D.hora = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }); }
    }
    if (n) {
      var MERCADO = /d[oó]lar|deuda|bono|fmi|bcra|merval|acci[oó]n|inflaci|tasa|caputo|milei|mercado|riesgo pa|fed\b|wall street|ypf|reservas|emisi[oó]n|privatiz|tarifa|impuesto|exporta|importa|super[aá]vit|d[eé]ficit|inversi|banco|petr[oó]leo|cedear|licitaci|econom/i;
      var lista = (n.argentina || []).map(function (x) {
        var dom = x.fuente || ''; if (!dom) { try { dom = new URL(x.link).hostname.replace(/^www\./, '').split('.')[0]; } catch (e) {} }
        return { t: x.titulo, f: x.fecha, src: dom, m: MERCADO.test(x.titulo + ' ' + (x.resumen || '')) };
      });
      var top = lista.filter(function (x) { return x.m; });
      D.noticias = (top.length >= 2 ? top : lista).slice(0, 4);
    }
    if (c && c.dias && c.dias.length) {
      var hoy = new Date(), hd = hoy.getDate(), hm = hoy.getMonth() + 1, pick = null;
      c.dias.forEach(function (d) {
        var p = String(d.fecha || '').split('/'); var dd = +p[0], mm = +p[1];
        if (!pick && (mm > hm || (mm === hm && dd >= hd)) && d.eventos && d.eventos.length) pick = d;
      });
      if (!pick) pick = c.dias.filter(function (d) { return d.eventos && d.eventos.length; }).slice(-1)[0];
      if (pick) {
        var esHoy = pick.fecha === hd + '/' + hm;
        D.agenda = { titulo: esHoy ? 'Hoy, ' + pick.nombre.toLowerCase() + ' ' + pick.fecha : pick.nombre + ' ' + pick.fecha, ev: pick.eventos.slice(0, 4).map(function (e) { return { tipo: e.tipo, t: e.titulo }; }) };
      }
    }
    return D;
  }

  /* ---------- formato ---------- */
  function ars(v) { return '$' + Math.round(v).toLocaleString('es-AR'); }
  function pct(v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }
  function cls(v) { return v > 0 ? 'up' : v < 0 ? 'dn' : ''; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function hace(iso) {
    var ms = Date.now() - new Date(iso).getTime(); if (!(ms > 0)) return '';
    var m = Math.round(ms / 60000); if (m < 60) return 'hace ' + Math.max(m, 1) + ' min';
    var h = Math.round(m / 60); if (h < 24) return 'hace ' + h + ' h';
    return 'hace ' + Math.round(h / 24) + ' d';
  }
  function contar(el, to, fmt, ms) {
    if (RM || !el) { if (el) el.textContent = fmt(to); return; }
    var t0 = performance.now(), from = to * 0.82; ms = ms || 1100;
    (function f(t) {
      var k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(2, -10 * k);
      el.textContent = fmt(from + (to - from) * (k === 1 ? 1 : e));
      if (k < 1) requestAnimationFrame(f);
    })(t0);
  }

  /* ---------- íconos (trazo 1.6, misma familia) ---------- */
  var IC = {
    mercados: '<path d="M3 17l5-5 4 3 8-8"/><path d="M15 7h5v5"/>',
    noticias: '<rect x="3.5" y="4.5" width="13" height="15" rx="1.5"/><path d="M16.5 8.5h3v9.5a1.5 1.5 0 0 1-3 0"/><path d="M7 8.5h6M7 12h6M7 15.5h4"/>',
    calendario: '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    portfolio: '<path d="M12 3.5a8.5 8.5 0 1 0 8.5 8.5H12z"/><path d="M15 3.8A8.5 8.5 0 0 1 20.2 9H15z"/>',
    informes: '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4M9 12h6M9 15.5h6"/>',
    warren: '<path d="M4.5 5.5h15v10h-8l-4 3.5v-3.5h-3z"/><path d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01"/>',
    university: '<path d="M2.5 9L12 4.5 21.5 9 12 13.5z"/><path d="M6.5 11v4.5c1.5 1.4 3.4 2 5.5 2s4-.6 5.5-2V11"/>',
    flecha: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    cerrar: '<path d="M6 6l12 12M18 6L6 18"/>',
    atras: '<path d="M19 12H5M11 6l-6 6 6 6"/>'
  };
  function ic(n, s) { return '<svg class="ic" width="' + (s || 18) + '" height="' + (s || 18) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + IC[n] + '</svg>'; }
  var LOGO = '<img class="logo" src="/assets/img/favicon.svg" alt="" width="30" height="30">';

  /* ---------- curva de ejemplo (determinística) ---------- */
  function serie(seed, drift, vol, n) {
    var x = seed, v = 0, out = [0];
    for (var i = 1; i < n; i++) { x = (x * 9301 + 49297) % 233280; v += drift + (x / 233280 - 0.5) * vol; out.push(v); }
    return out;
  }
  var EJ_CARTERA = serie(7, 0.205, 2.1, 64), EJ_SP = serie(23, 0.13, 1.5, 64);
  function pathDe(arr, w, h, min, max) {
    return arr.map(function (v, i) { return (i ? 'L' : 'M') + (i / (arr.length - 1) * w).toFixed(1) + ' ' + (h - (v - min) / (max - min) * h).toFixed(1); }).join(' ');
  }
  function graficoSVG(w, h) {
    var all = EJ_CARTERA.concat(EJ_SP), min = Math.min.apply(0, all) - 1, max = Math.max.apply(0, all) + 1;
    var pc = pathDe(EJ_CARTERA, w, h, min, max), ps = pathDe(EJ_SP, w, h, min, max);
    var y0 = h - (0 - min) / (max - min) * h;
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<line x1="0" x2="' + w + '" y1="' + y0.toFixed(1) + '" y2="' + y0.toFixed(1) + '" class="g0"/>' +
      '<path d="' + pc + ' L' + w + ' ' + h + ' L0 ' + h + 'Z" class="area"/>' +
      '<path d="' + ps + '" class="lsp"/>' +
      '<path d="' + pc + '" class="lpf"/></svg>';
  }
  var FIN_C = EJ_CARTERA[EJ_CARTERA.length - 1], FIN_S = EJ_SP[EJ_SP.length - 1];

  /* =====================================================================
     CSS
     ===================================================================== */
  var CSS = [
    ':host{all:initial;position:fixed;inset:0;z-index:2147483000;display:block;',
    '--bg:#07101e;--raised:#0c1828;--raised2:#11223a;--line:rgba(232,238,246,.11);--line-soft:rgba(232,238,246,.06);',
    '--ink:#eef2f7;--ink2:rgba(238,242,247,.80);--ink3:rgba(238,242,247,.60);--amber:#f2c94c;--amber-ink:#f5d67a;',
    '--pos:#5cc08e;--neg:#ec7a72;--data:#7ab8ec;--r:8px;--ease:cubic-bezier(.23,1,.32,1);--expo:cubic-bezier(.16,1,.3,1);',
    "--serif:'DM Serif Display',Georgia,serif;--sans:'IBM Plex Sans',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;",
    'font-family:var(--sans);color:var(--ink);-webkit-font-smoothing:antialiased}',
    '*{box-sizing:border-box;margin:0;padding:0}',
    '.wrap{outline:0}',
    '::selection{background:rgba(242,201,76,.32);color:#fff}',
    'button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}',
    ':focus-visible{outline:2px solid var(--amber);outline-offset:3px;border-radius:4px}',
    '.ic{flex:none;display:block}',
    '.num{font-family:var(--mono);font-variant-numeric:tabular-nums;letter-spacing:-.01em}',
    '.up{color:var(--pos)}.dn{color:var(--neg)}',
    /* escena */
    '.scrim{position:absolute;inset:0;background:radial-gradient(120% 90% at 12% 0%,#13284a 0%,#0a1629 42%,#07101e 78%);opacity:0;transition:opacity .5s var(--ease)}',
    '.open .scrim{opacity:1}',
    '.shell{position:absolute;inset:0;display:flex;flex-direction:column;opacity:0;transform:translateY(14px);transition:opacity .6s var(--expo),transform .8s var(--expo)}',
    '.open .shell{opacity:1;transform:none}',
    '.closing .shell{opacity:0;transform:translateY(-8px) scale(.99);transition-duration:.32s}',
    '.closing .scrim{opacity:0;transition-duration:.38s}',
    '.top{flex:none;display:flex;align-items:center;justify-content:space-between;padding:20px clamp(16px,4vw,48px)}',
    '.brand{display:flex;align-items:center;gap:11px;font-weight:600;font-size:15px;letter-spacing:.01em}',
    '.logo{width:30px;height:30px;display:block}',
    '.skip{display:flex;align-items:center;gap:8px;color:var(--ink3);font-size:14px;padding:8px 10px;border-radius:6px;transition:color .15s,background-color .15s}',
    '.skip:hover{color:var(--ink);background:rgba(238,242,247,.06)}',
    /* botones */
    '.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;font-weight:600;font-size:15.5px;padding:14px 22px;border-radius:var(--r);background:var(--amber);color:#07101e;transition:background-color .15s,transform .16s var(--ease);box-shadow:0 10px 28px -12px rgba(242,201,76,.55)}',
    '.btn:hover{background:#f7d96c}.btn:active{transform:scale(.97)}',
    '.btn2{display:inline-flex;align-items:center;gap:8px;font-weight:500;font-size:15px;padding:13px 18px;border-radius:var(--r);color:var(--ink2);border:1px solid var(--line);transition:border-color .15s,color .15s,transform .16s var(--ease)}',
    '.btn2:hover{color:var(--ink);border-color:rgba(238,242,247,.28)}.btn2:active{transform:scale(.97)}',
    '.lnk{display:inline-flex;align-items:center;gap:7px;color:var(--amber-ink);font-weight:500;font-size:14.5px;padding:4px 0;text-underline-offset:4px}',
    '.lnk:hover{text-decoration:underline}',
    '.tag{font-size:11.5px;font-weight:600;padding:3px 8px;border-radius:999px;white-space:nowrap}',
    '.tag--free{color:var(--pos);background:rgba(92,192,142,.12)}',
    '.tag--pro{color:var(--amber);background:rgba(242,201,76,.12)}',
    '.demo{font-size:12px;color:var(--ink3);font-style:italic}',
    '.live{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink3)}',
    '.live i{width:7px;height:7px;border-radius:50%;background:var(--pos);box-shadow:0 0 0 0 rgba(92,192,142,.6);animation:pulse 2s infinite}',
    '@keyframes pulse{70%{box-shadow:0 0 0 7px rgba(92,192,142,0)}100%{box-shadow:0 0 0 0 rgba(92,192,142,0)}}',

    /* ================= A · RECORRIDO ================= */
    '.A .stage{flex:1;min-height:0;position:relative}',
    '.step{position:absolute;inset:0;display:grid;grid-template-columns:minmax(0,.86fr) minmax(0,1.14fr);gap:clamp(28px,5vw,80px);align-items:center;padding:0 clamp(16px,5vw,72px) 8px;visibility:hidden}',
    '.step.on{visibility:visible}',
    '.copy{max-width:470px}',
    '.copy h2{font:400 clamp(34px,4.1vw,58px)/1.04 var(--serif);letter-spacing:-.012em;text-wrap:balance;margin-bottom:20px}',
    '.copy h2 em{font-style:italic;color:var(--amber)}',
    '.copy p{font-size:17px;line-height:1.6;color:var(--ink2);max-width:42ch;text-wrap:pretty}',
    '.copy .lnk{margin-top:22px}',
    '.copy .note{margin-top:14px;font-size:13.5px;color:var(--ink3)}',
    '.vis{position:relative;height:min(520px,100%);min-height:0;display:flex;align-items:center}',
    /* entrada de cada paso: el texto sube, la visual se destapa */
    '.step .copy>*{opacity:0;transform:translateY(16px);filter:blur(4px)}',
    '.step.on .copy>*{opacity:1;transform:none;filter:none;transition:opacity .7s var(--expo),transform .9s var(--expo),filter .7s var(--expo)}',
    '.step.on .copy>*:nth-child(2){transition-delay:.07s}.step.on .copy>*:nth-child(3){transition-delay:.14s}.step.on .copy>*:nth-child(4){transition-delay:.2s}',
    '.step .vis>*{opacity:0;clip-path:inset(0 0 12% 0 round 14px);transform:translateY(10px)}',
    '.step.on .vis>*{opacity:1;clip-path:inset(0 0 0 0 round 14px);transform:none;transition:opacity .6s var(--expo) .12s,clip-path 1s var(--expo) .12s,transform 1s var(--expo) .12s}',
    '.step.out-l .copy>*{opacity:0;transform:translateY(-10px);transition:opacity .25s,transform .3s}',
    '.panel{width:100%;background:linear-gradient(180deg,var(--raised2),var(--raised) 46%);border:1px solid var(--line);border-radius:14px;box-shadow:0 30px 60px -28px rgba(0,0,0,.75),0 2px 0 rgba(255,255,255,.03) inset;overflow:hidden}',
    '.ph{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;border-bottom:1px solid var(--line-soft);font-size:13.5px;font-weight:600;color:var(--ink2)}',
    '.ph span{display:flex;align-items:center;gap:9px}',
    '.ph .ic{color:var(--amber)}',
    /* paso 1: pestañas */
    '.win{width:100%;border-radius:14px;border:1px solid var(--line);background:var(--raised);overflow:hidden;box-shadow:0 30px 60px -28px rgba(0,0,0,.8)}',
    '.tabs{display:flex;align-items:flex-end;gap:2px;padding:10px 10px 0;background:#091321;height:46px;border-bottom:1px solid var(--line-soft)}',
    '.tb{flex:1 1 0;min-width:0;max-width:190px;height:34px;display:flex;align-items:center;gap:8px;padding:0 10px;border-radius:9px 9px 0 0;background:rgba(238,242,247,.05);color:var(--ink3);font-size:12.5px;white-space:nowrap;overflow:hidden;',
    'transition:max-width .55s var(--expo),flex-grow .55s var(--expo),opacity .35s,transform .45s var(--expo),padding .45s,background-color .4s,color .4s;animation:tbin .45s var(--expo) backwards}',
    '.tb b{width:12px;height:12px;border-radius:3px;flex:none;background:var(--c,#5b6b80)}',
    '.tb span{overflow:hidden;text-overflow:ellipsis}',
    '@keyframes tbin{from{opacity:0;transform:translateY(10px)}}',
    '.tabs.fold .tb:not(.keep){max-width:0;flex-grow:0;padding:0;opacity:0;transform:translateX(-30px)}',
    '.tabs.fold .tb.keep{max-width:260px;flex-grow:0;flex-basis:260px;background:var(--raised);color:var(--ink);box-shadow:inset 0 -2px 0 var(--amber)}',
    '.tb.keep img{width:14px;height:14px;display:none}',
    '.tabs.fold .tb.keep img{display:block}.tabs.fold .tb.keep b{display:none}',
    '.wbody{position:relative;height:300px}',
    '.mess,.calm{position:absolute;inset:0;padding:22px;transition:opacity .6s var(--ease),filter .6s}',
    '.mess{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}',
    '.mess i{display:block;border-radius:6px;background:rgba(238,242,247,.05)}',
    '.mess i:nth-child(1){grid-column:span 2}.mess i:nth-child(4){grid-row:span 2}.mess i:nth-child(6){grid-column:span 2}',
    '.calm{opacity:0;display:flex;flex-direction:column;gap:14px}',
    '.fold~.wbody .mess{opacity:0;filter:blur(6px)}.fold~.wbody .calm{opacity:1;transition-delay:.35s}',
    '.calm .row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}',
    '.kp{padding:14px 16px;border-radius:10px;background:rgba(238,242,247,.035);border:1px solid var(--line-soft)}',
    '.kp small{display:block;font-size:12.5px;color:var(--ink3);margin-bottom:6px}',
    '.kp strong{font-size:22px;font-weight:500}',
    '.kp em{font-style:normal;font-size:12.5px;margin-left:6px}',
    '.calm .hl{font-size:14.5px;line-height:1.45;color:var(--ink2);padding:12px 16px;border-radius:10px;border:1px solid var(--line-soft)}',
    '.calm .hl b{color:var(--ink3);font-weight:500;font-size:12px;display:block;margin-bottom:3px}.calm .hl .src{text-transform:capitalize}',
    /* paso 2: cotizaciones */
    '.dol{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--line-soft)}',
    '.dol div{padding:18px 18px 20px;border-right:1px solid var(--line-soft)}.dol div:last-child{border-right:0}',
    '.dol small{display:block;font-size:13px;color:var(--ink3);margin-bottom:8px}',
    '.dol strong{font-size:clamp(20px,2vw,28px);font-weight:500}',
    '.idx{display:grid;grid-template-columns:1fr 1fr;gap:0}',
    '.idx>div{padding:6px 18px 14px}',
    '.idx h4,.ag h4,.nw h4{font-size:12.5px;font-weight:500;color:var(--ink3);margin:12px 0 8px}',
    '.li{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--line-soft);font-size:14.5px}',
    '.li:last-child{border-bottom:0}',
    '.li .num{font-size:14px}',
    '.li .nm{color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.li .tk{font-family:var(--mono);font-weight:600;font-size:13.5px;margin-right:8px;color:var(--ink)}',
    '.foot{display:flex;justify-content:space-between;align-items:center;padding:12px 18px;border-top:1px solid var(--line-soft);font-size:12.5px;color:var(--ink3)}',
    /* paso 3: noticias + agenda */
    '.nwag{display:grid;grid-template-columns:1.25fr 1fr}',
    '.nw{padding:4px 18px 16px;border-right:1px solid var(--line-soft)}',
    '.ag{padding:4px 18px 16px}',
    '.news{display:block;padding:11px 0;border-bottom:1px solid var(--line-soft)}',
    '.news:last-child{border-bottom:0}',
    '.news p{font-size:14.5px;line-height:1.42;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}',
    '.news small{display:block;margin-top:4px;font-size:12px;color:var(--ink3)}.news .src{text-transform:capitalize}',
    '.ev{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;padding:9px 0;border-bottom:1px solid var(--line-soft);font-size:13.5px;line-height:1.4;color:var(--ink2)}',
    '.ev:last-child{border-bottom:0}',
    '.flag{font-size:10.5px;font-weight:700;padding:2px 6px;border-radius:4px;margin-top:1px;letter-spacing:.02em}',
    '.flag--ar{color:#9fd1f5;background:rgba(122,184,236,.14)}.flag--us{color:#f5d67a;background:rgba(242,201,76,.12)}.flag--x{color:var(--ink2);background:rgba(238,242,247,.08)}',
    /* paso 4: cartera */
    '.pfv{padding:16px 18px 6px}',
    '.leg{display:flex;gap:22px;align-items:baseline;flex-wrap:wrap}',
    '.leg div small{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink3);margin-bottom:3px}',
    '.leg div small i{width:10px;height:3px;border-radius:2px}',
    '.leg strong{font-size:26px;font-weight:500}',
    '.chart{height:200px;margin:12px 0 4px}',
    '.chart svg{width:100%;height:100%;display:block;overflow:visible}',
    '.g0{stroke:rgba(238,242,247,.12);stroke-dasharray:3 4}',
    '.lpf{fill:none;stroke:var(--amber);stroke-width:2.4;stroke-linejoin:round;vector-effect:non-scaling-stroke}',
    '.lsp{fill:none;stroke:var(--data);stroke-width:1.8;stroke-linejoin:round;vector-effect:non-scaling-stroke;opacity:.9}',
    '.area{fill:rgba(242,201,76,.08)}',
    '.chart svg{clip-path:inset(0 100% 0 0)}',
    '.draw svg{clip-path:inset(0 0 0 0);transition:clip-path 1.8s cubic-bezier(.45,0,.2,1) .35s}',
    '.cap{font-size:13.5px;color:var(--ink2);padding:6px 0 14px}',
    '.brk{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:14px 18px;border-top:1px solid var(--line-soft);font-size:13px;color:var(--ink3)}',
    '.brk span.b{color:var(--ink2);font-weight:500;padding:4px 10px;border-radius:999px;background:rgba(238,242,247,.06)}',
    /* paso 5: informes + warren */
    '.duo{display:grid;grid-template-rows:auto auto;gap:14px;width:100%}',
    '.wall{display:grid;grid-template-columns:repeat(10,1fr);gap:8px;padding:16px 18px}',
    '.wall img{width:100%;aspect-ratio:1;border-radius:9px;background:#fff;object-fit:contain;padding:5px;opacity:0;transform:scale(.85)}',
    '.on .wall img{opacity:1;transform:none;transition:opacity .5s var(--expo),transform .6s var(--expo)}',
    '.chat{padding:14px 18px 16px;display:flex;flex-direction:column;gap:10px}',
    '.msg{font-size:14px;line-height:1.5;max-width:88%}',
    '.msg--u{align-self:flex-end;padding:9px 13px;border-radius:12px 12px 3px 12px;background:rgba(242,201,76,.13);border:1px solid rgba(242,201,76,.28)}',
    '.msg--w{align-self:flex-start;padding:11px 14px;border-radius:12px 12px 12px 3px;background:rgba(238,242,247,.05);border:1px solid var(--line-soft);color:var(--ink2);min-height:44px}',
    '.msg--w b{color:var(--ink);font-weight:600}',
    '.caret::after{content:"";display:inline-block;width:7px;height:14px;background:var(--amber);margin-left:2px;vertical-align:-2px;animation:blink 1s steps(2) infinite}',
    '@keyframes blink{50%{opacity:0}}',
    /* paso 6: cierre */
    '.ctas{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}',
    '.idxl{width:100%}',
    '.it{display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:center;width:100%;text-align:left;padding:15px 18px;border-bottom:1px solid var(--line-soft);transition:background-color .15s}',
    '.it:last-child{border-bottom:0}',
    '.it:hover{background:rgba(238,242,247,.035)}',
    '.it .ic{color:var(--amber)}',
    '.it strong{display:block;font-size:15px;font-weight:600}',
    '.it small{display:block;font-size:13px;color:var(--ink3);margin-top:2px}',
    /* navegación inferior */
    '.nav{flex:none;display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px clamp(16px,5vw,72px) 22px}',
    '.prog{display:flex;gap:6px;flex:1;max-width:420px}',
    '.prog button{flex:1;height:22px;position:relative}',
    '.prog button::before{content:"";position:absolute;left:0;right:0;top:10px;height:3px;border-radius:2px;background:rgba(238,242,247,.12);transition:background-color .3s}',
    '.prog button.done::before,.prog button.cur::before{background:var(--amber)}',
    '.prog button.cur::before{background:linear-gradient(90deg,var(--amber),var(--amber-ink))}',
    '.navb{display:flex;align-items:center;gap:10px}',
    '.back{width:46px;height:46px;display:grid;place-items:center;border-radius:var(--r);border:1px solid var(--line);color:var(--ink2);transition:opacity .2s,border-color .15s}',
    '.back:hover{border-color:rgba(238,242,247,.28);color:var(--ink)}',
    '.back[disabled]{opacity:0;pointer-events:none}',
    '.count{font-size:13px;color:var(--ink3);min-width:44px;text-align:right}',

    /* ================= B · UNA PANTALLA ================= */
    '.B .main{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(28px,4vw,64px);align-items:center;padding:0 clamp(16px,4.5vw,64px) 28px}',
    '.B .copy{max-width:500px}',
    '.B .copy h2{font-size:clamp(38px,4.4vw,64px)}',
    '.B .copy>*{opacity:0;transform:translateY(16px);filter:blur(4px)}',
    '.B.go .copy>*{opacity:1;transform:none;filter:none;transition:opacity .8s var(--expo),transform 1s var(--expo),filter .8s var(--expo)}',
    '.B.go .copy>*:nth-child(2){transition-delay:.08s}.B.go .copy>*:nth-child(3){transition-delay:.16s}.B.go .copy>*:nth-child(4){transition-delay:.24s}',
    '.inc{list-style:none;margin-top:26px;display:grid;grid-template-columns:1fr 1fr;gap:10px 20px}',
    '.inc li{display:flex;align-items:center;gap:10px;font-size:14.5px;color:var(--ink2)}',
    '.inc .ic{color:var(--amber)}',
    '.board{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:auto;gap:10px;max-height:100%;min-height:0}',
    '.mod{position:relative;display:flex;flex-direction:column;justify-content:flex-start;background:linear-gradient(180deg,var(--raised2),var(--raised) 60%);border:1px solid var(--line);border-radius:12px;overflow:hidden;text-align:left;width:100%;',
    'clip-path:inset(0 100% 0 0 round 12px);transition:border-color .2s}',
    '.mod::after{content:"";position:absolute;top:0;bottom:0;left:0;width:2px;background:var(--amber);box-shadow:0 0 18px 2px rgba(242,201,76,.5);opacity:0}',
    '.mod.in{clip-path:inset(0 0 0 0 round 12px);transition:clip-path .9s var(--expo),border-color .2s}',
    '.mod.in::after{animation:scan .9s var(--expo) forwards}',
    '@keyframes scan{0%{left:0;opacity:1}85%{opacity:1}100%{left:100%;opacity:0}}',
    '.mod:hover{border-color:rgba(242,201,76,.38)}',
    '.mh{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 14px 0;font-size:12.5px;font-weight:600;color:var(--ink3)}',
    '.mh span{display:flex;align-items:center;gap:7px}.mh .ic{color:var(--amber)}',
    '.mh .go{color:var(--ink3);opacity:0;transform:translateX(-4px);transition:opacity .2s,transform .2s var(--ease)}',
    '.mod:hover .mh .go{opacity:1;transform:none;color:var(--amber)}',
    '.m-dol{grid-column:span 6}.m-idx{grid-column:span 3}.m-ag{grid-column:span 3}.m-nw{grid-column:span 3}.m-pf{grid-column:span 3}.m-wr{grid-column:span 6}',
    '.m-dol .dol{border:0}.m-dol .dol div{padding:8px 14px 14px}',
    '.m-dol .dol strong{font-size:clamp(18px,1.7vw,24px)}',
    '.mb{padding:4px 14px 10px}',
    '.mb .li{padding:6px 0;font-size:13.5px}',
    '.mb .ev{padding:7px 0;font-size:13px}',
    '.mb .news{padding:8px 0}.mb .news p{font-size:13.5px}',
    '.m-pf .chart{height:96px;margin:6px 0 0}',
    '.m-pf .leg strong{font-size:18px}',
    '.wr{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center;padding:8px 14px 12px}',
    '.wr .msg--w{max-width:none;min-height:0;font-size:13.5px}',
    '.logos{display:flex;gap:6px}',
    '.logos img{width:30px;height:30px;border-radius:7px;background:#fff;object-fit:contain;padding:3px}',
    '.B .ctas{margin-top:30px}',

    /* ================= responsive ================= */
    '@media (max-width:900px){',
    '.top{padding:14px 16px}',
    '.step{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr);align-items:start;gap:20px;padding:6px 16px 0;overflow:hidden}',
    '.copy h2{font-size:clamp(30px,8.4vw,40px);margin-bottom:12px}',
    '.copy p{font-size:15.5px}',
    '.copy .lnk{margin-top:12px}',
    '.vis{height:100%;align-items:flex-start}',
    '.wbody{height:230px}',
    '.tabs{height:40px}.tb{height:30px;font-size:11.5px;padding:0 8px}',
    '.calm .row{grid-template-columns:1fr 1fr}.calm .row .kp:nth-child(3){display:none}',
    '.dol{grid-template-columns:1fr 1fr}.dol div:nth-child(2){border-right:0}.dol div:nth-child(-n+2){border-bottom:1px solid var(--line-soft)}',
    '.dol div{padding:12px 14px}',
    '.idx{grid-template-columns:1fr}.idx>div:last-child{display:none}',
    '.nwag{grid-template-columns:1fr}.nw{border-right:0;border-bottom:1px solid var(--line-soft)}.nw .news:nth-child(n+4){display:none}',
    '.chart{height:150px}',
    '.wall{grid-template-columns:repeat(6,1fr);gap:6px;padding:12px 14px}.wall img:nth-child(n+13){display:none}',
    '.chat{padding:10px 14px 12px}.msg{font-size:13.5px}',
    '.nw .news:nth-child(n+3){display:none}',
    '.it{padding:12px 14px}',
    '.nav{padding:12px 16px calc(14px + env(safe-area-inset-bottom))}',
    '.ctas{margin-top:18px}.ctas .btn,.ctas .btn2{flex:1 1 100%}',
    '.B .main{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr);align-items:start;gap:18px;padding:4px 16px 0;overflow:hidden}',
    '.B .copy h2{font-size:clamp(32px,9vw,42px)}',
    '.inc{display:none}',
    '.B .ctas{position:fixed;left:0;right:0;bottom:0;margin:0;padding:12px 16px calc(14px + env(safe-area-inset-bottom));background:linear-gradient(180deg,rgba(7,16,30,0),#07101e 32%);z-index:2}',
    '.B .ctas .btn2{display:none}',
    '.board{grid-template-columns:1fr 1fr;padding-bottom:96px;overflow:hidden}',
    '.m-dol,.m-wr,.m-ag,.m-idx{grid-column:span 2}.m-nw,.m-pf,.m-wr{display:none}',
    '.m-idx .mb{display:grid;grid-template-columns:1fr 1fr;column-gap:18px}',
    '.m-ag .ev:nth-child(n+3){display:none}',
    '.wr{grid-template-columns:1fr}.logos{display:none}',
    '}',
    '@media (max-width:900px) and (max-height:700px){.wbody{height:180px}.chart{height:110px}.m-wr{display:none}}',
    '@media (min-width:901px) and (max-height:760px){.copy h2{font-size:clamp(32px,3.4vw,46px)}.wbody{height:250px}.chart{height:150px}.vis{height:100%}}',
    '@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}.mod{clip-path:none}}'
  ].join('\n');

  /* =====================================================================
     montaje común
     ===================================================================== */
  var host, root, lastFocus;
  function abrir() {
    if (host) return;
    lastFocus = document.activeElement;
    host = document.createElement('div');
    host.id = 'miBienvenida';
    document.body.appendChild(host);
    root = host.attachShadow({ mode: 'open' });
    document.documentElement.setAttribute('data-bienvenida', '');
    document.documentElement.style.overflow = 'hidden';
    var wrap = document.createElement('div');
    wrap.className = 'wrap ' + variante.toUpperCase();
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-modal', 'true');
    wrap.setAttribute('aria-label', 'Bienvenida a Manfredi Investment');
    wrap.tabIndex = -1;
    wrap.innerHTML = '<div class="scrim"></div><div class="shell"></div>';
    root.innerHTML = '<style>' + CSS + '</style>';
    root.appendChild(wrap);
    var shell = wrap.querySelector('.shell');
    (variante === 'b' ? montarB : montarA)(shell, wrap);
    requestAnimationFrame(function () { requestAnimationFrame(function () { wrap.classList.add('open'); wrap.focus({ preventScroll: true }); }); });
    root.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); cerrar(); }
      if (e.key === 'Tab') trampa(e);
    });
    root.addEventListener('click', function (e) {
      var a = e.target.closest('[data-ir]'); if (a) { e.preventDefault(); cerrar(a.getAttribute('data-ir')); return; }
      if (e.target.closest('[data-registro]')) { cerrar(null, true); return; }
      if (e.target.closest('[data-cerrar]')) cerrar();
    });
  }
  function trampa(e) {
    var f = Array.prototype.filter.call(root.querySelectorAll('button,a[href]'), function (x) { return x.offsetParent !== null && !x.disabled; });
    if (!f.length) return;
    var a = root.activeElement;
    if (e.shiftKey && a === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && a === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  }
  function cerrar(tab, registro) {
    if (!host) return;
    if (!forzada) ls(KEY_VISTA, registro ? 'registro' : tab ? 'ir:' + tab : 'cerrada');
    var wrap = root.querySelector('.wrap');
    wrap.classList.add('closing');
    setTimeout(function () {
      host.remove(); host = null;
      document.documentElement.removeAttribute('data-bienvenida');
      document.documentElement.style.overflow = '';
      if (tab) { location.hash = tab; window.scrollTo(0, 0); }
      if (registro && window.showLoginOverlay) window.showLoginOverlay();
      else if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) {} }
    }, RM ? 0 : 340);
  }
  function top() {
    return '<header class="top"><div class="brand">' + LOGO + 'Manfredi Investment</div>' +
      '<button class="skip" data-cerrar>Saltar' + ic('cerrar', 16) + '</button></header>';
  }

  /* bloques de datos que comparten A y B */
  function htmlDolares(D) {
    if (!D.dolares.length) return '<div class="dol"><div><small>Dólar</small><strong class="num">—</strong></div></div>';
    return '<div class="dol">' + D.dolares.map(function (d) {
      return '<div><small>Dólar ' + esc(d.n) + '</small><strong class="num" data-ars="' + d.v + '">' + ars(d.v) + '</strong></div>';
    }).join('') + '</div>';
  }
  function htmlIndices(D, n) {
    return D.indices.slice(0, n || 5).map(function (x) {
      return '<div class="li"><span class="nm">' + esc(x.n) + '</span><span class="num ' + cls(x.c) + '">' + pct(x.c) + '</span></div>';
    }).join('') || '<div class="li"><span class="nm">Cargando…</span></div>';
  }
  function htmlMovers(D) {
    return D.movers.map(function (x) {
      return '<div class="li"><span class="nm"><span class="tk">' + esc(x.s) + '</span>' + esc(x.n) + '</span><span class="num ' + cls(x.c) + '">' + pct(x.c) + '</span></div>';
    }).join('');
  }
  function htmlNoticias(D, n) {
    if (!D.noticias.length) return '<div class="news"><p>Las noticias se actualizan cada media hora.</p></div>';
    return D.noticias.slice(0, n || 4).map(function (x) {
      return '<div class="news"><p>' + esc(x.t) + '</p><small><span class="src">' + esc(x.src) + '</span>' + (x.f ? ' · ' + hace(x.f) : '') + '</small></div>';
    }).join('');
  }
  function htmlAgenda(D, n) {
    if (!D.agenda) return '<div class="ev"><span class="flag flag--x">—</span><span>La agenda de la semana se publica los domingos.</span></div>';
    return D.agenda.ev.slice(0, n || 4).map(function (e) {
      var f = e.tipo === 'ar' ? ['ar', 'AR'] : e.tipo === 'us' ? ['us', 'EE.UU.'] : ['x', 'Emp.'];
      return '<div class="ev"><span class="flag flag--' + f[0] + '">' + f[1] + '</span><span>' + esc(e.t) + '</span></div>';
    }).join('');
  }
  function animarDolares(scope) {
    Array.prototype.forEach.call(scope.querySelectorAll('[data-ars]'), function (el, i) {
      setTimeout(function () { contar(el, +el.getAttribute('data-ars'), ars, 1200); }, i * 90);
    });
  }
  function logosHTML(n) {
    return INFORMES.slice(0, n).map(function (t, i) {
      return '<img src="/assets/logos/' + t + '.png" alt="' + t.toUpperCase() + '" loading="lazy" style="transition-delay:' + (0.2 + i * 0.025).toFixed(3) + 's" onerror="this.style.visibility=\'hidden\'">';
    }).join('');
  }
  var WARREN_Q = '¿Mi cartera está muy concentrada?';
  var WARREN_A = 'Un poco: el <b>58%</b> está en tecnología y tus 3 posiciones más grandes suman el <b>61%</b>. Si cae el Nasdaq, tu cartera cae más que el mercado. Sumar algo de consumo o salud bajaría ese riesgo.';
  function tipear(el, html, cb) {
    if (RM) { el.innerHTML = html; if (cb) cb(); return; }
    var parts = html.split(/(<[^>]+>|\s+)/).filter(Boolean), i = 0, acc = '';
    el.classList.add('caret');
    (function paso() {
      if (!host) return;
      if (i >= parts.length) { el.classList.remove('caret'); if (cb) cb(); return; }
      acc += parts[i++]; el.innerHTML = acc;
      setTimeout(paso, /^\s+$/.test(parts[i - 1]) ? 10 : 42);
    })();
  }

  /* =====================================================================
     A · RECORRIDO POR PASOS
     ===================================================================== */
  var PESTANAS = [
    ['Diario económico', '#4c6a92'], ['Cotizaciones', '#5c8f75'], ['Calendario INDEC', '#8a6fb0'], ['App del broker', '#b4744c'],
    ['Excel de la cartera', '#3f8a5a'], ['Twitter financiero', '#5a7fa8'], ['Investing', '#a8584f'], ['Informe de un banco', '#6b7a8f'],
    ['Grupo de WhatsApp', '#4f9a6c'], ['YouTube', '#a84f4f']
  ];

  function montarA(shell, wrap) {
    var pasos = [
      { id: 'todo', html: function () {
        return '<div class="copy"><h2>Lo que mirás en <em>diez pestañas</em>, en una sola.</h2>' +
          '<p>Cotizaciones, noticias, el calendario económico, informes de empresas y tu cartera, pensado para el inversor argentino. Lo principal es gratis.</p></div>' +
          '<div class="vis"><div class="win"><div class="tabs" id="tabsA"></div><div class="wbody">' +
          '<div class="mess"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>' +
          '<div class="calm"><div class="row" id="calmKp"></div><div class="hl" id="calmHl"></div></div></div></div></div>';
      } },
      { id: 'mercados', html: function () {
        return '<div class="copy"><h2>El mercado, <em>en vivo</em>.</h2>' +
          '<p>Todos los dólares, el Merval, Wall Street, bonos, CEDEARs y cripto' + '<span id="totA"></span>. Con lo que más se movió hoy, sin abrir otra página.</p>' +
          '<button class="lnk" data-ir="mercados">Ir a Mercados' + ic('flecha', 16) + '</button></div>' +
          '<div class="vis"><div class="panel"><div class="ph"><span>' + ic('mercados') + 'Mercados</span><span class="live" id="liveA"><i></i>En vivo</span></div>' +
          '<div id="dolA"></div><div class="idx"><div><h4>Índices hoy</h4><div id="idxA"></div></div><div><h4>Lo que más se movió</h4><div id="movA"></div></div></div></div></div>';
      } },
      { id: 'noticias', html: function () {
        return '<div class="copy"><h2>Lo que pasa hoy y <em>lo que viene</em>.</h2>' +
          '<p>Las noticias de Argentina y Wall Street que importan, y la agenda de la semana: datos del INDEC, la Fed, balances y dividendos de las empresas que seguimos.</p>' +
          '<button class="lnk" data-ir="calendario">Ver el calendario' + ic('flecha', 16) + '</button></div>' +
          '<div class="vis"><div class="panel"><div class="nwag"><div class="nw"><h4>Últimas noticias</h4><div id="nwA"></div></div>' +
          '<div class="ag"><h4 id="agT">Agenda</h4><div id="agA"></div></div></div></div></div>';
      } },
      { id: 'cartera', html: function () {
        return '<div class="copy"><h2>¿Le estás <em>ganando</em> al mercado?</h2>' +
          '<p>Cargá tu cartera a mano o importá el PDF de tu broker. Te mostramos tu rendimiento real, descontando lo que fuiste aportando, al lado del S&amp;P 500.</p>' +
          '<button class="lnk" data-ir="portfolio">Armar mi cartera gratis' + ic('flecha', 16) + '</button></div>' +
          '<div class="vis"><div class="panel"><div class="ph"><span>' + ic('portfolio') + 'Tu portafolio</span><span class="demo">Cartera de ejemplo</span></div>' +
          '<div class="pfv"><div class="leg"><div><small><i style="background:var(--amber)"></i>Tu cartera</small><strong class="num" style="color:var(--amber)" id="pfC">+0,0%</strong></div>' +
          '<div><small><i style="background:var(--data)"></i>S&amp;P 500</small><strong class="num" style="color:var(--data)" id="pfS">+0,0%</strong></div></div>' +
          '<div class="chart" id="chA">' + graficoSVG(600, 200) + '</div><p class="cap">Ganó plata, pero menos que el mercado. Eso tu broker no te lo muestra.</p></div>' +
          '<div class="brk">Importá el PDF de <span class="b">IOL</span><span class="b">Balanz</span><span class="b">Cocos</span><span class="b">PPI</span><span class="b">Bull Market</span></div></div></div>';
      } },
      { id: 'informes', html: function () {
        return '<div class="copy"><h2>Informes en serio y <em>un asesor con IA</em>.</h2>' +
          '<p>Más de 45 empresas analizadas a fondo, con valuación y un precio justo explícito. Y Warren, una IA que conoce tu cartera y te responde en criollo.</p>' +
          '<p class="note"><span class="tag tag--pro">Membresía</span>&nbsp; USD 15 por mes</p>' +
          '<button class="lnk" data-ir="informes">Ver los informes' + ic('flecha', 16) + '</button></div>' +
          '<div class="vis"><div class="duo"><div class="panel"><div class="ph"><span>' + ic('informes') + 'Informes publicados</span><span class="demo">Algunas de las empresas</span></div><div class="wall">' + logosHTML(30) + '</div></div>' +
          '<div class="panel"><div class="ph"><span>' + ic('warren') + 'Warren IA</span><span class="demo">Conversación de ejemplo</span></div>' +
          '<div class="chat"><div class="msg msg--u">' + WARREN_Q + '</div><div class="msg msg--w" id="wA"></div></div></div></div></div>';
      } },
      { id: 'fin', html: function () {
        var secciones = [
          ['mercados', 'Mercados', 'Dólares, acciones, bonos, CEDEARs y cripto', 'free'],
          ['noticias', 'Noticias y reportes', 'Argentina y Wall Street, todos los días', 'free', 'inicio'],
          ['calendario', 'Calendario', 'Datos económicos, balances y dividendos', 'free'],
          ['portfolio', 'Portfolio', 'Tu cartera contra el mercado', 'free'],
          ['university', 'University', 'Cursos para aprender a invertir', 'free'],
          ['informes', 'Informes y Warren IA', 'Valuaciones y tu asesor con IA', 'pro']
        ];
        return '<div class="copy"><h2>Tu mañana de mercado, <em>en un solo lugar</em>.</h2>' +
          '<p>Creá tu cuenta gratis con Google o con tu mail, cargá tu cartera y empezá a mirar todo desde acá.</p>' +
          '<div class="ctas"><button class="btn" data-registro>Crear cuenta gratis' + ic('flecha', 18) + '</button><button class="btn2" data-cerrar>Explorar la página</button></div></div>' +
          '<div class="vis"><div class="panel idxl">' + secciones.map(function (s) {
            return '<button class="it" data-ir="' + (s[4] || s[0]) + '">' + ic(s[0] === 'noticias' ? 'noticias' : s[0] === 'informes' ? 'informes' : s[0], 22) +
              '<span><strong>' + s[1] + '</strong><small>' + s[2] + '</small></span><span class="tag tag--' + s[3] + '">' + (s[3] === 'free' ? 'Gratis' : 'Membresía') + '</span></button>';
          }).join('') + '</div></div>';
      } }
    ];

    shell.innerHTML = top() + '<main class="stage">' + pasos.map(function (p, i) {
      return '<section class="step" data-i="' + i + '" aria-hidden="true">' + p.html() + '</section>';
    }).join('') + '</main>' +
      '<nav class="nav" aria-label="Pasos"><div class="prog">' + pasos.map(function (p, i) {
        return '<button aria-label="Paso ' + (i + 1) + ' de ' + pasos.length + '" data-paso="' + i + '"></button>';
      }).join('') + '</div><div class="navb"><span class="count num" id="cnt"></span><button class="back" id="prev" aria-label="Paso anterior">' + ic('atras') + '</button>' +
      '<button class="btn" id="next">Siguiente' + ic('flecha', 18) + '</button></div></nav>';

    var steps = shell.querySelectorAll('.step'), cur = -1, hechos = {};
    var next = shell.querySelector('#next'), prev = shell.querySelector('#prev');

    function ir(i) {
      if (i < 0 || i >= steps.length || i === cur) return;
      if (cur >= 0) { steps[cur].classList.remove('on'); steps[cur].setAttribute('aria-hidden', 'true'); }
      cur = i;
      steps[i].classList.add('on'); steps[i].setAttribute('aria-hidden', 'false');
      Array.prototype.forEach.call(shell.querySelectorAll('.prog button'), function (b, k) {
        b.classList.toggle('done', k < i); b.classList.toggle('cur', k === i);
        if (k === i) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
      });
      shell.querySelector('#cnt').textContent = (i + 1) + ' / ' + steps.length;
      prev.disabled = i === 0;
      var ult = i === steps.length - 1;
      next.style.display = ult ? 'none' : '';
      entrar(i);
    }
    shell.querySelector('.prog').addEventListener('click', function (e) { var b = e.target.closest('[data-paso]'); if (b) ir(+b.getAttribute('data-paso')); });
    next.addEventListener('click', function () { ir(cur + 1); });
    prev.addEventListener('click', function () { ir(cur - 1); });
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') ir(cur + 1);
      if (e.key === 'ArrowLeft') ir(cur - 1);
    });
    var tx = null, ty = 0;
    shell.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
    shell.addEventListener('touchend', function (e) {
      if (tx == null) return;
      var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty; tx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) ir(cur + (dx < 0 ? 1 : -1));
    }, { passive: true });

    function entrar(i) {
      var s = steps[i];
      if (i === 0) pestanas(s);
      if (i === 1) datos.then(function (D) {
        s.querySelector('#dolA').innerHTML = htmlDolares(D);
        s.querySelector('#idxA').innerHTML = htmlIndices(D, 4);
        s.querySelector('#movA').innerHTML = htmlMovers(D);
        if (D.total) s.querySelector('#totA').textContent = ': más de ' + (Math.floor(D.total / 100) * 100).toLocaleString('es-AR') + ' cotizaciones';
        if (D.hora) s.querySelector('#liveA').innerHTML = '<i></i>Actualizado ' + D.hora;
        animarDolares(s);
      });
      if (i === 2) datos.then(function (D) {
        s.querySelector('#nwA').innerHTML = htmlNoticias(D, 4);
        s.querySelector('#agA').innerHTML = htmlAgenda(D, 4);
        if (D.agenda) s.querySelector('#agT').textContent = 'Agenda · ' + D.agenda.titulo;
      });
      if (i === 3) {
        var ch = s.querySelector('#chA'); ch.classList.remove('draw'); void ch.offsetWidth; ch.classList.add('draw');
        setTimeout(function () { contar(s.querySelector('#pfC'), FIN_C, pct, 1700); contar(s.querySelector('#pfS'), FIN_S, pct, 1700); }, 350);
      }
      if (i === 4 && !hechos[4]) { hechos[4] = 1; setTimeout(function () { tipear(s.querySelector('#wA'), WARREN_A); }, 700); }
      if (i === steps.length - 1 && root.activeElement === next) setTimeout(function () { var b = s.querySelector('.btn'); if (b) b.focus({ preventScroll: true }); }, 60);
    }

    function pestanas(s) {
      var bar = s.querySelector('#tabsA');
      bar.classList.remove('fold'); bar.innerHTML = '';
      datos.then(function (D) {
        var kp = D.dolares.filter(function (d) { return d.n === 'MEP'; })[0];
        var mv = D.indices.filter(function (x) { return x.id === 'merval'; })[0];
        var sp = D.indices.filter(function (x) { return x.id === 'sp500'; })[0];
        s.querySelector('#calmKp').innerHTML =
          '<div class="kp"><small>Dólar MEP</small><strong class="num">' + (kp ? ars(kp.v) : '—') + '</strong></div>' +
          '<div class="kp"><small>Merval</small><strong class="num ' + (mv ? cls(mv.c) : '') + '">' + (mv ? pct(mv.c) : '—') + '</strong></div>' +
          '<div class="kp"><small>S&amp;P 500</small><strong class="num ' + (sp ? cls(sp.c) : '') + '">' + (sp ? pct(sp.c) : '—') + '</strong></div>';
        var n = D.noticias[0];
        s.querySelector('#calmHl').innerHTML = n ? '<b>Última noticia · <span class="src">' + esc(n.src) + '</span></b>' + esc(n.t) : '<b>Noticias</b>Argentina y Wall Street, actualizadas todo el día.';
      });
      PESTANAS.forEach(function (p, k) {
        setTimeout(function () {
          if (!host) return;
          var t = document.createElement('div'); t.className = 'tb' + (k === 0 ? ' keep' : '');
          t.innerHTML = '<b style="--c:' + p[1] + '"></b><img src="/assets/img/favicon.svg" alt=""><span>' + p[0] + '</span>';
          bar.appendChild(t);
        }, RM ? 0 : 250 + k * 120);
      });
      setTimeout(function () {
        if (!host) return;
        bar.classList.add('fold');
        var k = bar.querySelector('.keep span'); if (k) k.textContent = 'Manfredi Investment';
      }, RM ? 0 : 250 + PESTANAS.length * 120 + 900);
    }

    ir(0);
  }

  /* =====================================================================
     B · UNA SOLA PANTALLA
     ===================================================================== */
  function montarB(shell, wrap) {
    shell.innerHTML = top() +
      '<main class="main"><div class="copy">' +
      '<h2>Cerrá las diez pestañas. <em>Abrí una</em>.</h2>' +
      '<p>Lo que hoy mirás en diez pestañas: cotizaciones, noticias, el calendario, informes de empresas y tu cartera contra el mercado. Pensado para el inversor argentino, y lo principal es gratis.</p>' +
      '<ul class="inc">' +
      '<li>' + ic('mercados') + 'Mercados en vivo</li><li>' + ic('noticias') + 'Noticias y reportes</li>' +
      '<li>' + ic('calendario') + 'Calendario económico</li><li>' + ic('portfolio') + 'Tu cartera vs. el S&amp;P</li>' +
      '<li>' + ic('informes') + 'Informes con valuación</li><li>' + ic('warren') + 'Warren, asesor con IA</li></ul>' +
      '<div class="ctas"><button class="btn" data-registro>Crear cuenta gratis' + ic('flecha', 18) + '</button><button class="btn2" data-cerrar>Explorar la página</button></div>' +
      '</div>' +
      '<div class="board">' +
      '<button class="mod m-dol" data-ir="mercados"><div class="mh"><span>' + ic('mercados', 15) + 'Dólares</span><span class="live" id="liveB"><i></i>En vivo</span></div><div id="dolB">' + htmlDolares({ dolares: [] }) + '</div></button>' +
      '<button class="mod m-idx" data-ir="mercados"><div class="mh"><span>' + ic('mercados', 15) + 'Índices hoy</span><span class="go">' + ic('flecha', 15) + '</span></div><div class="mb" id="idxB"></div></button>' +
      '<button class="mod m-ag" data-ir="calendario"><div class="mh"><span>' + ic('calendario', 15) + '<span id="agTB">Agenda</span></span><span class="go">' + ic('flecha', 15) + '</span></div><div class="mb" id="agB"></div></button>' +
      '<button class="mod m-nw" data-ir="inicio"><div class="mh"><span>' + ic('noticias', 15) + 'Noticias</span><span class="go">' + ic('flecha', 15) + '</span></div><div class="mb" id="nwB"></div></button>' +
      '<button class="mod m-pf" data-ir="portfolio"><div class="mh"><span>' + ic('portfolio', 15) + 'Tu cartera</span><span class="demo">Ejemplo</span></div><div class="mb">' +
      '<div class="leg"><div><small><i style="background:var(--amber)"></i>Tu cartera</small><strong class="num" style="color:var(--amber)" id="pfCB">+0,0%</strong></div><div><small><i style="background:var(--data)"></i>S&amp;P 500</small><strong class="num" style="color:var(--data)" id="pfSB">+0,0%</strong></div></div>' +
      '<div class="chart" id="chB">' + graficoSVG(400, 96) + '</div></div></button>' +
      '<button class="mod m-wr" data-ir="informes"><div class="mh"><span>' + ic('warren', 15) + 'Warren IA e informes</span><span class="demo">Conversación de ejemplo</span></div>' +
      '<div class="wr"><div class="msg msg--w" id="wB"></div><div class="logos">' + logosHTML(6) + '</div></div></button>' +
      '</div></main>';

    wrap.classList.add('go');
    var mods = shell.querySelectorAll('.mod');
    datos.then(function (D) {
      shell.querySelector('#dolB').innerHTML = htmlDolares(D);
      shell.querySelector('#idxB').innerHTML = htmlIndices(D, 4);
      shell.querySelector('#agB').innerHTML = htmlAgenda(D, 3);
      shell.querySelector('#nwB').innerHTML = htmlNoticias(D, 2);
      if (D.agenda) shell.querySelector('#agTB').textContent = D.agenda.titulo.replace(/^Hoy, /, 'Hoy · ');
      if (D.hora) shell.querySelector('#liveB').innerHTML = '<i></i>Actualizado ' + D.hora;
      Array.prototype.forEach.call(mods, function (m, i) {
        setTimeout(function () {
          if (!host) return;
          m.classList.add('in');
          if (m.classList.contains('m-dol')) animarDolares(m);
          if (m.classList.contains('m-pf')) { m.querySelector('.chart').classList.add('draw'); setTimeout(function () { contar(shell.querySelector('#pfCB'), FIN_C, pct, 1700); contar(shell.querySelector('#pfSB'), FIN_S, pct, 1700); }, 350); }
          if (m.classList.contains('m-wr')) setTimeout(function () { tipear(shell.querySelector('#wB'), '<b>' + WARREN_Q + '</b> ' + WARREN_A); }, 500);
        }, RM ? 0 : 300 + i * 170);
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar);
  else arrancar();
})();
