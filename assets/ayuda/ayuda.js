/* Ayuda de Manfredi: preguntas frecuentes con buscador y derivación al mail del equipo.
   Vive en un Shadow DOM (igual que assets/cartel/cartel.js) para no chocar con el CSS global.
   Botón fijo arriba a la derecha, debajo del menú; Warren sigue abajo a la derecha.
   Las preguntas están en assets/ayuda/faq.json y se cargan recién al abrir.
   Lo que no está en las preguntas se manda por mail (mailto) a MAIL_EQUIPO. */
(function () {
  if (window.__miAyuda) return;
  window.__miAyuda = true;

  var FAQ_URL = 'assets/ayuda/faq.json';
  var MAIL_EQUIPO = 'manfredi.investment@gmail.com';

  var CSS = "\
  :host{all:initial;--bg:#0a1322;--raised:#0f1c30;--raised2:#132440;--line:rgba(255,255,255,.09);--line2:rgba(255,255,255,.16);\
    --ink:#eef2f7;--ink2:rgba(238,242,247,.86);--ink3:rgba(238,242,247,.68);--gold:#f2c94c;--gold-ink:#f5d67a;--pos:#5cc08e;--neg:#e8675f;\
    --serif:'DM Serif Display',Georgia,serif;--sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;\
    --ease:cubic-bezier(.23,1,.32,1);--top:68px;--right:max(16px,calc((100vw - 1200px) / 2 + 32px));\
    font-family:var(--sans);color:var(--ink);-webkit-font-smoothing:antialiased}\
  *{box-sizing:border-box}\
  ::selection{background:rgba(242,201,76,.32);color:#fff}\
  button{font:inherit;color:inherit}\
  :focus-visible{outline:2px solid var(--gold);outline-offset:2px}\
  \
  /* ── Botón ── */\
  .trig{position:fixed;z-index:90;top:calc(var(--top) + 12px);right:var(--right);height:40px;padding:0 15px 0 7px;display:flex;align-items:center;gap:9px;\
    border-radius:999px;border:1px solid rgba(242,201,76,.42);background:var(--bg);color:var(--ink);cursor:pointer;\
    box-shadow:0 10px 26px -12px rgba(0,0,0,.65),0 2px 6px rgba(0,0,0,.18);\
    transition:transform .16s var(--ease),border-color .15s ease,background-color .15s ease,padding .28s var(--ease),top .12s linear}\
  .trig:active{transform:scale(.97)}\
  .trig__ic{width:26px;height:26px;border-radius:50%;background:var(--gold);color:#0a0f1e;display:grid;place-items:center;flex:none}\
  .trig__ic svg{width:15px;height:15px}\
  .trig__t{font-size:13.5px;font-weight:600;letter-spacing:.005em;white-space:nowrap;max-width:120px;overflow:hidden;transition:max-width .28s var(--ease),opacity .2s ease}\
  .trig.mini{padding:0 7px}\
  .trig.mini .trig__t{max-width:0;opacity:0}\
  .trig[aria-expanded=true]{border-color:var(--gold);background:var(--raised)}\
  @media (hover:hover) and (pointer:fine){\
    .trig:hover{border-color:var(--gold);background:var(--raised)}\
    .trig.mini:hover{padding:0 15px 0 7px}.trig.mini:hover .trig__t{max-width:120px;opacity:1}\
  }\
  .trig.mini:focus-visible{padding:0 15px 0 7px}.trig.mini:focus-visible .trig__t{max-width:120px;opacity:1}\
  \
  /* ── Panel ── */\
  .pan{position:fixed;z-index:8001;top:calc(var(--top) + 60px);right:var(--right);width:410px;max-height:min(640px,calc(100vh - var(--top) - 76px));\
    display:flex;flex-direction:column;background:var(--bg);border:1px solid rgba(242,201,76,.26);border-radius:14px;overflow:hidden;\
    box-shadow:0 28px 60px -24px rgba(0,0,0,.75),0 8px 18px -8px rgba(0,0,0,.4);\
    transform-origin:calc(100% - 40px) -8px;opacity:0;visibility:hidden;transform:translateY(-6px) scale(.96);filter:blur(3px);\
    transition:opacity .15s ease,transform .15s var(--ease),filter .15s ease,visibility 0s linear .15s}\
  .pan.open{opacity:1;visibility:visible;transform:none;filter:none;transition:opacity .2s ease,transform .24s var(--ease),filter .2s ease,visibility 0s}\
  \
  .hd{padding:18px 18px 14px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,rgba(242,201,76,.07),rgba(242,201,76,0) 90%)}\
  .hd__row{display:flex;align-items:flex-start;gap:12px}\
  .hd h2{margin:0;font:400 24px/1.15 var(--serif);color:#fff;letter-spacing:-.005em;flex:1}\
  .hd p{margin:6px 0 14px;font-size:13.5px;line-height:1.5;color:var(--ink2)}\
  .x{flex:none;width:36px;height:36px;margin:-6px -8px 0 0;border:0;border-radius:8px;background:none;color:var(--ink2);cursor:pointer;display:grid;place-items:center;transition:background-color .15s ease,color .15s ease}\
  .x:hover{background:rgba(255,255,255,.06);color:#fff}\
  .x svg{width:16px;height:16px}\
  .srch{display:flex;align-items:center;gap:10px;height:46px;padding:0 12px 0 14px;border-radius:10px;background:var(--raised);border:1px solid var(--line2);transition:border-color .15s ease,box-shadow .15s ease}\
  .srch:focus-within{border-color:rgba(242,201,76,.7);box-shadow:0 0 0 3px rgba(242,201,76,.12)}\
  .srch svg{width:17px;height:17px;color:var(--ink3);flex:none}\
  .srch input{flex:1;min-width:0;height:100%;border:0;background:none;outline:none;color:#fff;font:15px var(--sans);caret-color:var(--gold)}\
  .srch input::placeholder{color:var(--ink3)}\
  .srch input::-webkit-search-cancel-button{display:none}\
  .clr{border:0;background:none;color:var(--ink3);cursor:pointer;padding:6px;border-radius:6px;display:none}\
  .clr.on{display:grid}.clr:hover{color:#fff}\
  .clr svg{width:14px;height:14px}\
  \
  .bd{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.18) transparent}\
  .bd::-webkit-scrollbar{width:8px}.bd::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:8px;border:2px solid var(--bg)}\
  .v{display:none;padding:14px 18px 18px}\
  .v.on{display:block;animation:vin .22s var(--ease)}\
  @keyframes vin{from{opacity:0;transform:translateY(4px);filter:blur(2px)}to{opacity:1;transform:none;filter:none}}\
  \
  .cats{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}\
  .cat{height:32px;padding:0 12px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.035);color:var(--ink2);font-size:13px;font-weight:500;cursor:pointer;\
    transition:background-color .15s ease,border-color .15s ease,color .15s ease,transform .16s var(--ease)}\
  .cat:hover{border-color:var(--line2);color:#fff}\
  .cat:active{transform:scale(.97)}\
  .cat[aria-pressed=true]{background:var(--gold);border-color:var(--gold);color:#0a0f1e;font-weight:600}\
  .lt{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:0 0 4px}\
  .lt h3{margin:0;font:400 18px/1.2 var(--serif);color:#fff}\
  .lt span{font-size:12.5px;color:var(--ink3);font-variant-numeric:tabular-nums}\
  \
  .ql{list-style:none;margin:0;padding:0}\
  .qi{display:flex;align-items:center;gap:12px;width:100%;min-height:48px;padding:11px 8px 11px 2px;border:0;border-bottom:1px solid var(--line);background:none;cursor:pointer;text-align:left;\
    font-size:14.5px;line-height:1.4;color:var(--ink);border-radius:0;transition:background-color .12s ease}\n  .qi>span{transition:transform .18s var(--ease)}\
  .ql li:last-child .qi{border-bottom:0}\
  .qi svg{width:14px;height:14px;flex:none;margin-left:auto;color:var(--ink3);transition:transform .18s var(--ease),color .15s ease}\
  .qi:hover,.qi.act{background:rgba(242,201,76,.06)}\n  .qi:hover>span,.qi.act>span{transform:translateX(8px)}\
  .qi:hover svg,.qi.act svg{color:var(--gold);transform:translateX(2px)}\
  .qi mark{background:none;color:var(--gold-ink);font-weight:600}\
  .qi small{display:block;margin-top:2px;font-size:12px;color:var(--ink3)}\
  \
  .empty h3{margin:6px 0 6px;font:400 21px/1.2 var(--serif);color:#fff}\
  .empty p{margin:0 0 16px;font-size:14px;line-height:1.55;color:var(--ink2)}\
  .empty q{color:#fff;quotes:'\\201C' '\\201D'}\
  \
  .back{display:inline-flex;align-items:center;gap:6px;height:32px;margin:-4px 0 10px -6px;padding:0 8px;border:0;border-radius:6px;background:none;color:var(--ink2);font-size:13px;font-weight:500;cursor:pointer;transition:background-color .15s ease,color .15s ease}\
  .back:hover{background:rgba(255,255,255,.05);color:#fff}\
  .back svg{width:14px;height:14px}\
  .aq{margin:0 0 12px;font:400 23px/1.2 var(--serif);color:#fff;text-wrap:balance}\
  .aa{font-size:14.5px;line-height:1.62;color:var(--ink2)}\
  .aa p{margin:0 0 10px}\
  .aa b{color:#fff;font-weight:600}\
  .aa ul{margin:0 0 10px;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px}\
  .aa li{position:relative;padding-left:18px}\
  .aa li::before{content:'';position:absolute;left:2px;top:.72em;width:8px;height:1.5px;border-radius:2px;background:var(--gold)}\
  .aa>:last-child{margin-bottom:0}\
  .btn{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 18px;border:0;border-radius:6px;background:var(--gold);color:#0a0f1e;font-size:14px;font-weight:600;cursor:pointer;\
    transition:background-color .15s ease,transform .16s var(--ease)}\
  .btn:hover{background:#f7d96c}\
  .btn:active{transform:scale(.97)}\
  .btn svg{width:15px;height:15px}\
  .btn[disabled]{opacity:.6;cursor:default;transform:none}\
  .btn--ghost{background:transparent;color:var(--ink);border:1px solid var(--line2)}\
  .btn--ghost:hover{background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.3)}\
  .ago{margin-top:16px}\
  .fb{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:18px;padding-top:14px;border-top:1px solid var(--line);font-size:13px;color:var(--ink2)}\
  .fb__b{height:30px;padding:0 13px;border-radius:999px;border:1px solid var(--line2);background:none;cursor:pointer;font-size:13px;font-weight:500;color:var(--ink);transition:border-color .15s ease,background-color .15s ease,transform .16s var(--ease)}\
  .fb__b:hover{border-color:rgba(242,201,76,.6)}\
  .fb__b:active{transform:scale(.97)}\
  .fb__ok{color:var(--pos);font-weight:500}\
  .lnk{border:0;background:none;padding:0;color:var(--gold-ink);font-weight:600;font-size:13px;cursor:pointer;text-decoration:underline;text-underline-offset:3px;text-decoration-color:rgba(245,214,122,.4)}\
  .lnk:hover{text-decoration-color:var(--gold-ink)}\
  .rel{margin-top:20px}\
  .rel h4{margin:0 0 2px;font-size:13px;font-weight:600;color:var(--ink3)}\
  .rel .qi{font-size:14px;min-height:44px}\
  \
  .frm{display:flex;flex-direction:column;gap:12px;margin-top:4px}\
  .fld{display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:500;color:var(--ink2)}\
  .fld input,.fld textarea{width:100%;padding:11px 12px;border-radius:8px;border:1px solid var(--line2);background:var(--raised);color:#fff;font:14.5px/1.45 var(--sans);caret-color:var(--gold);resize:vertical;transition:border-color .15s ease,box-shadow .15s ease}\
  .fld textarea{min-height:92px}\
  .fld input:focus,.fld textarea:focus{outline:none;border-color:rgba(242,201,76,.7);box-shadow:0 0 0 3px rgba(242,201,76,.12)}\
  .fld input[aria-invalid=true]{border-color:var(--neg)}\
  .err{margin:-4px 0 0;font-size:12.5px;color:#f1938d}\
  .note{margin:0;font-size:12.5px;line-height:1.5;color:var(--ink3)}\
  .done{text-align:left;padding-top:6px}\
  .done h3{margin:0 0 6px;font:400 22px/1.2 var(--serif);color:#fff}\
  .done p{margin:0 0 16px;font-size:14px;line-height:1.55;color:var(--ink2)}\
  .mailbox{display:flex;align-items:center;gap:8px;margin:0 0 14px;padding:10px 12px;border-radius:8px;border:1px solid var(--line2);background:var(--raised);font-size:14px;color:#fff;user-select:all}\
  .mailbox span{flex:1;min-width:0;overflow-wrap:anywhere}\
  .mailbox button{flex:none;height:30px;padding:0 10px;border-radius:6px;border:1px solid var(--line2);background:none;color:var(--ink);font-size:12.5px;font-weight:500;cursor:pointer}\
  .sk{height:14px;border-radius:6px;background:linear-gradient(90deg,rgba(255,255,255,.05),rgba(255,255,255,.1),rgba(255,255,255,.05));background-size:200% 100%;animation:sh 1.2s linear infinite;margin:16px 0}\
  @keyframes sh{to{background-position:-200% 0}}\
  \
  .ft{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 18px;border-top:1px solid var(--line);font-size:13px;color:var(--ink2);background:rgba(255,255,255,.015)}\
  .ft .lnk{font-size:13px}\
  \
  @media (max-width:600px){\
    .trig{right:12px;padding:0 7px}.trig .trig__t{max-width:0;opacity:0}\
    .pan{left:10px;right:10px;width:auto;top:calc(var(--top) + 58px);max-height:calc(100dvh - var(--top) - 70px);transform-origin:calc(100% - 30px) -8px}\
    .hd h2{font-size:22px}\
  }\
  @media (prefers-reduced-motion:reduce){\
    .trig,.pan,.pan.open,.qi,.qi svg,.qi>span,.trig__t{transition:none}\
    .v.on,.sk{animation:none}\
  }";

  var I = {
    q: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.2 9.1a2.9 2.9 0 1 1 4.1 2.7c-.8.4-1.3 1-1.3 1.9v.6"/><path d="M12 17.6h.01"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    lupa: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4-4"/></svg>',
    chev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12 20 4l-6 16-3-7-7-1z"/></svg>'
  };

  var HTML = '\
  <button type="button" class="trig" id="trig" aria-expanded="false" aria-controls="pan">\
    <span class="trig__ic">' + I.q + '</span><span class="trig__t">Ayuda</span>\
  </button>\
  <div class="pan" id="pan" role="dialog" aria-labelledby="ttl">\
    <div class="hd">\
      <div class="hd__row"><h2 id="ttl">¿En qué te ayudamos?</h2><button type="button" class="x" id="cls" aria-label="Cerrar la ayuda">' + I.x + '</button></div>\
      <p>Respuestas sobre cómo usar Manfredi. Si tu duda no está, se la pasamos al equipo.</p>\
      <label class="srch">' + I.lupa + '<input id="s" type="search" placeholder="Escribí tu duda, por ejemplo: cómo cancelo" autocomplete="off" spellcheck="false" aria-label="Buscar en la ayuda" aria-controls="bd"><button type="button" class="clr" id="clr" aria-label="Borrar la búsqueda">' + I.x + '</button></label>\
    </div>\
    <div class="bd" id="bd">\
      <section class="v" id="vHome"></section>\
      <section class="v" id="vRes" aria-live="polite"></section>\
      <section class="v" id="vAns"></section>\
      <section class="v" id="vMail"></section>\
    </div>\
    <div class="ft"><span>¿Preguntas sobre el mercado?</span><button type="button" class="lnk" id="toWarren">Hablá con Warren</button></div>\
  </div>';

  // ── Búsqueda ────────────────────────────────────────────────────────────
  var STOP = ' a al algo ante como con cual cuales cuando de del donde el ella en es esa ese esta este esto hay la las le les lo los me mi mis mas muy no o para pero por porque puedo que se si sin sobre su sus te tengo tu tus un una uno unos y ya yo quiero hago hacer seria ';
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/&amp;/g, '&').replace(/[^a-z0-9&]+/g, ' ').trim(); }
  // Cómo suena, para que "cansel", "kancelo" o "vitcoin" encuentren lo mismo que la palabra bien escrita
  function son(t) { return t.replace(/qu/g, 'k').replace(/c([ei])/g, 's$1').replace(/z/g, 's').replace(/v/g, 'b').replace(/ll/g, 'y').replace(/h/g, '').replace(/c/g, 'k'); }
  function toks(s) { return norm(s).split(' ').filter(function (t) { return t && (t.length > 1 || /\d/.test(t)) && STOP.indexOf(' ' + t + ' ') === -1; }); }
  function lev(a, b) {
    if (Math.abs(a.length - b.length) > 2) return 3;
    var p = [], i, j;
    for (j = 0; j <= b.length; j++) p[j] = j;
    for (i = 1; i <= a.length; i++) {
      var prev = p[0]; p[0] = i;
      for (j = 1; j <= b.length; j++) {
        var tmp = p[j];
        p[j] = Math.min(p[j] + 1, p[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
        prev = tmp;
      }
    }
    return p[b.length];
  }
  function tm(q, t) {
    if (q === t) return 1;
    if (q.length >= 4) { var sq = son(q), st = son(t); if (sq === st) return .95; if (st.indexOf(sq) === 0) return .8; }
    if (q.length >= 3 && t.indexOf(q) === 0) return .85;
    if (t.length >= 4 && q.indexOf(t) === 0) return .7;
    if (q.length >= 5 && t.length >= 5) { var d = lev(q, t); if (d === 1) return .75; if (d === 2 && q.length >= 7) return .5; }
    return 0;
  }
  function best(q, arr) { var m = 0; for (var i = 0; i < arr.length && m < 1; i++) { var v = tm(q, arr[i]); if (v > m) m = v; } return m; }

  var DATA = null, BYID = {}, CATS = {};
  function prep(d) {
    d.categorias.forEach(function (c) { CATS[c.id] = c.t; });
    d.preguntas.forEach(function (p) {
      p._q = toks(p.q); p._k = toks(p.k + ' ' + (CATS[p.c] || '')); p._a = toks(p.a.replace(/<[^>]+>/g, ' '));
      BYID[p.id] = p;
    });
    DATA = d;
  }
  function search(text) {
    var qs = toks(text);
    if (!qs.length) return [];
    var out = [];
    DATA.preguntas.forEach(function (p) {
      var score = 0, hit = 0;
      qs.forEach(function (q) {
        var s = Math.max(3 * best(q, p._q), 2.2 * best(q, p._k), .8 * best(q, p._a));
        if (s >= 1.5) hit++;
        score += s;
      });
      if (score >= 2 && hit >= Math.ceil(qs.length / 2)) out.push({ p: p, s: score + hit });
    });
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 8).map(function (o) { return o.p; });
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function hl(text, qs) {
    return text.split(/(\s+)/).map(function (w) {
      if (!w.trim()) return w;
      var n = norm(w); if (!n) return esc(w);
      var on = qs.some(function (q) { return tm(q, n) >= .7; });
      return on ? '<mark>' + esc(w) + '</mark>' : esc(w);
    }).join('');
  }

  // ── Montaje ─────────────────────────────────────────────────────────────
  var host = document.createElement('div');
  host.id = 'miAyuda';
  var root = host.attachShadow({ mode: 'open' });
  root.innerHTML = '<style>' + CSS + '</style>' + HTML;
  document.body.appendChild(host);
  var $ = function (id) { return root.getElementById(id); };
  var trig = $('trig'), pan = $('pan'), inp = $('s'), clr = $('clr'), bd = $('bd');
  var V = { home: $('vHome'), res: $('vRes'), ans: $('vAns'), mail: $('vMail') };
  var state = { cat: null, prev: 'home', act: -1, open: false };

  // Posición: siempre justo debajo del menú, aunque el menú esté pegado arriba o no
  var nav = null, raf = 0;
  function place() {
    raf = 0;
    nav = nav || document.querySelector('.navbar');
    var b = nav ? Math.max(0, Math.round(nav.getBoundingClientRect().bottom)) : 0;
    host.style.setProperty('--top', b + 'px');
    trig.classList.toggle('mini', window.scrollY > 280 && !state.open);
  }
  function schedule() { if (!raf) raf = requestAnimationFrame(place); }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  place();
  if (window.matchMedia('(max-width:600px)').matches) inp.placeholder = 'Escribí tu duda';

  function show(name) {
    Object.keys(V).forEach(function (k) { V[k].classList.toggle('on', k === name); });
    bd.scrollTop = 0;
  }

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (load._p) return load._p;
    load._p = fetch(FAQ_URL, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { prep(d); return d; })
      .catch(function (e) { load._p = null; throw e; });
    return load._p;
  }

  function row(p, qs, sub) {
    return '<li><button type="button" class="qi" data-id="' + p.id + '"><span>' + (qs ? hl(p.q, qs) : esc(p.q)) +
      (sub ? '<small>' + esc(CATS[p.c] || '') + '</small>' : '') + '</span>' + I.chev + '</button></li>';
  }

  function renderHome() {
    if (!DATA) {
      V.home.innerHTML = '<div class="sk" style="width:70%"></div><div class="sk"></div><div class="sk" style="width:85%"></div><div class="sk" style="width:60%"></div>';
      show('home');
      load().then(renderHome).catch(function () {
        V.home.innerHTML = '<div class="empty"><h3>No pudimos cargar la ayuda.</h3><p>Revisá tu conexión y probá de nuevo, o mandanos tu consulta directamente.</p></div>' +
          '<button type="button" class="btn" data-act="retry">Probar de nuevo</button> <button type="button" class="btn btn--ghost" data-act="mail">Escribir al equipo</button>';
      });
      return;
    }
    var cats = '<div class="cats" role="group" aria-label="Temas">' + DATA.categorias.map(function (c) {
      return '<button type="button" class="cat" data-cat="' + c.id + '" aria-pressed="' + (state.cat === c.id) + '">' + esc(c.t) + '</button>';
    }).join('') + '</div>';
    var list, title;
    if (state.cat) {
      list = DATA.preguntas.filter(function (p) { return p.c === state.cat; });
      title = CATS[state.cat];
    } else {
      list = DATA.destacadas.map(function (id) { return BYID[id]; }).filter(Boolean);
      title = 'Lo más preguntado';
    }
    V.home.innerHTML = cats + '<div class="lt"><h3>' + esc(title) + '</h3>' + (state.cat ? '<span>' + list.length + ' preguntas</span>' : '') + '</div>' +
      '<ul class="ql">' + list.map(function (p) { return row(p); }).join('') + '</ul>';
    show('home');
  }

  function renderRes(text) {
    if (!DATA) { load().then(function () { renderRes(inp.value); }); return; }
    var qs = toks(text), res = search(text);
    state.act = -1;
    if (!res.length) {
      V.res.innerHTML = '<div class="empty"><h3>No tenemos esa respuesta cargada.</h3>' +
        '<p>Mandale tu pregunta al equipo y te respondemos por mail. Tu consulta: <q>' + esc(text.trim()) + '</q></p>' +
        '<button type="button" class="btn" data-act="mail">' + I.send + 'Mandar la pregunta al equipo</button></div>';
    } else {
      V.res.innerHTML = '<div class="lt"><h3>Resultados</h3><span>' + res.length + (res.length === 1 ? ' respuesta' : ' respuestas') + '</span></div><ul class="ql" role="listbox" aria-label="Resultados">' +
        res.map(function (p) { return row(p, qs, true); }).join('') + '</ul>' +
        '<div class="fb" style="border:0;margin-top:10px;padding-top:6px">¿No es lo que buscabas? <button type="button" class="lnk" data-act="mail">Mandala al equipo</button></div>';
    }
    show('res');
  }

  function renderAns(id, from) {
    var p = BYID[id]; if (!p) return;
    state.prev = from || 'home';
    var go = '';
    if (p.go) go = '<div class="ago"><button type="button" class="btn" data-go="' + esc(p.go[1]) + '">' + esc(p.go[0]) + I.arrow + '</button></div>';
    var rel = DATA.preguntas.filter(function (x) { return x.c === p.c && x.id !== p.id; }).slice(0, 3);
    V.ans.innerHTML = '<button type="button" class="back" data-act="back">' + I.back + 'Volver</button>' +
      '<h3 class="aq">' + esc(p.q) + '</h3><div class="aa">' + p.a + '</div>' + go +
      '<div class="fb" id="fb">¿Te sirvió? <button type="button" class="fb__b" data-fb="si">Sí</button><button type="button" class="fb__b" data-fb="no">No</button></div>' +
      (rel.length ? '<div class="rel"><h4>Más sobre ' + esc(CATS[p.c]) + '</h4><ul class="ql">' + rel.map(function (x) { return row(x); }).join('') + '</ul></div>' : '');
    V.ans.dataset.q = p.q;
    show('ans');
  }

  function renderMail(pregunta) {
    V.mail.innerHTML = '<button type="button" class="back" data-act="back">' + I.back + 'Volver</button>' +
      '<h3 class="aq">Mandanos tu pregunta</h3><p class="note" style="font-size:14px;color:var(--ink2);margin-bottom:6px">Al tocar Enviar se abre tu app de mail con la pregunta lista para mandar a <b style="color:#fff">' + MAIL_EQUIPO + '</b>. Te respondemos a ese mismo mail.</p>' +
      '<form class="frm" id="frm" novalidate>' +
      '<label class="fld">Tu pregunta<textarea id="fQ" maxlength="1000" required>' + esc(pregunta || '') + '</textarea></label>' +
      '<p class="err" id="eQ" hidden>Contanos tu duda en al menos unas palabras.</p>' +
      '<div><button type="submit" class="btn" id="fBtn">' + I.send + 'Enviar por mail</button></div></form>';
    show('mail');
    var q = V.mail.querySelector('#fQ');
    q.focus(); q.setSelectionRange(q.value.length, q.value.length);
  }

  // Abre la app de mail del visitante con la consulta armada (sin servidor de por medio)
  function sendMail(ev) {
    ev.preventDefault();
    var q = V.mail.querySelector('#fQ'), texto = q.value.trim(), ok = texto.length >= 5;
    q.setAttribute('aria-invalid', !ok); V.mail.querySelector('#eQ').hidden = ok;
    if (!ok) { q.focus(); return; }
    var asunto = 'Consulta desde la web: ' + texto.split('\n')[0].slice(0, 60);
    var cuerpo = texto + '\n\n—\nSección: ' + (location.hash || '#inicio');
    location.href = 'mailto:' + MAIL_EQUIPO + '?subject=' + encodeURIComponent(asunto) + '&body=' + encodeURIComponent(cuerpo);
    V.mail.innerHTML = '<div class="done"><h3>Se abrió tu app de mail.</h3><p>Revisá el mensaje y tocá <b style="color:#fff">Enviar</b> ahí para que nos llegue. Si no se abrió nada, escribinos a este mail con tu pregunta:</p>' +
      '<div class="mailbox"><span>' + MAIL_EQUIPO + '</span><button type="button" data-act="copy">Copiar</button></div>' +
      '<button type="button" class="btn btn--ghost" data-act="home">Volver a la ayuda</button></div>';
    bd.scrollTop = 0;
  }

  function doGo(dest) {
    if (dest === 'contacto') { renderMail(''); return; }
    toggle(false);
    if (dest.charAt(0) === '#') { location.hash = dest.slice(1); return; }
    if (dest === 'warren') { if (typeof window.toggleWarren === 'function') window.toggleWarren(); return; }
    if (dest === 'pagar') { if (typeof window.openPaymentModal === 'function') window.openPaymentModal(); return; }
    if (dest === 'login') { if (window.showLoginOverlay) window.showLoginOverlay(); return; }
    if (dest === 'notify') { if (window.showNotifyOverlay) window.showNotifyOverlay(); return; }
    if (dest.indexOf('fin:') === 0 && window.miOpenFinView) { window.miOpenFinView(dest.slice(4)); }
  }

  function toggle(open) {
    state.open = open;
    pan.classList.toggle('open', open);
    trig.setAttribute('aria-expanded', open);
    trig.setAttribute('aria-label', open ? 'Cerrar la ayuda' : 'Abrir la ayuda');
    if (open) {
      trig.classList.remove('mini');
      if (!inp.value) renderHome();
      setTimeout(function () { inp.focus({ preventScroll: true }); }, 60);
    } else {
      schedule();
    }
  }

  // ── Eventos ─────────────────────────────────────────────────────────────
  trig.setAttribute('aria-label', 'Abrir la ayuda');
  trig.addEventListener('pointerenter', function () { load().catch(function () {}); }, { once: true });
  trig.addEventListener('click', function () { toggle(!state.open); });
  $('cls').addEventListener('click', function () { toggle(false); trig.focus(); });
  $('toWarren').addEventListener('click', function () { doGo('warren'); });

  var tq = 0;
  inp.addEventListener('input', function () {
    clr.classList.toggle('on', !!inp.value);
    clearTimeout(tq);
    tq = setTimeout(function () { if (inp.value.trim()) renderRes(inp.value); else renderHome(); }, 90);
  });
  clr.addEventListener('click', function () { inp.value = ''; clr.classList.remove('on'); renderHome(); inp.focus(); });
  inp.addEventListener('keydown', function (e) {
    if (!V.res.classList.contains('on')) { if (e.key === 'Enter' && inp.value.trim()) { e.preventDefault(); renderRes(inp.value); } return; }
    var items = V.res.querySelectorAll('.qi');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      if (!items.length) return;
      e.preventDefault();
      state.act = (state.act + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach(function (el, i) { el.classList.toggle('act', i === state.act); });
      items[state.act].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (items.length) renderAns(items[Math.max(0, state.act)].dataset.id, 'res');
      else renderMail(inp.value);
    }
  });

  root.addEventListener('click', function (e) {
    var t = e.target.closest('button'); if (!t) return;
    if (t.dataset.cat) { state.cat = state.cat === t.dataset.cat ? null : t.dataset.cat; renderHome(); return; }
    if (t.dataset.id) { renderAns(t.dataset.id, V.res.classList.contains('on') ? 'res' : 'home'); return; }
    if (t.dataset.go) { doGo(t.dataset.go); return; }
    if (t.dataset.fb) {
      var fb = V.ans.querySelector('#fb');
      if (t.dataset.fb === 'si') fb.innerHTML = '<span class="fb__ok">Gracias, nos sirve saberlo.</span>';
      else fb.innerHTML = '¿Qué te faltó? <button type="button" class="lnk" data-act="mail-q">Mandale tu duda al equipo</button>';
      return;
    }
    var a = t.dataset.act;
    if (a === 'back') { if (state.prev === 'res' && inp.value.trim()) renderRes(inp.value); else renderHome(); }
    else if (a === 'home') { inp.value = ''; clr.classList.remove('on'); renderHome(); }
    else if (a === 'mail') renderMail(inp.value.trim());
    else if (a === 'mail-q') renderMail(V.ans.dataset.q + '\n\n');
    else if (a === 'retry') renderHome();
    else if (a === 'copy') {
      var done = function () { t.textContent = 'Copiado'; };
      try { navigator.clipboard.writeText(MAIL_EQUIPO).then(done, function () {}); } catch (err) {}
    }
  });
  root.addEventListener('submit', function (e) { if (e.target.id === 'frm') sendMail(e); });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && state.open) { toggle(false); trig.focus(); } });
  document.addEventListener('pointerdown', function (e) {
    if (state.open && e.composedPath().indexOf(host) === -1) toggle(false);
  });
})();
