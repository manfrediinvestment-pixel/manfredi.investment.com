/* Anuncio grande de la promo de Warren (33% OFF hasta el 31-oct-2026).
   Aparece en el centro de la pantalla en cada visita nueva (una vez por
   sesión del navegador), con cuenta regresiva en vivo. No se muestra a socios.
   Test: ?promo=1 lo fuerza aunque ya se haya visto en la sesión. */
(function () {
  var P = window.MI_PROMO;
  var FIN = Date.parse('2026-11-01T03:00:00Z');
  var KEY = 'mi_promo_wall_sesion';
  var forzar = /[?&]promo=1/.test(location.search);
  if (!P || !P.on || Date.now() >= FIN) return;

  function visto() { try { return sessionStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function marcar() { try { sessionStorage.setItem(KEY, '1'); } catch (e) {} }
  function esSocio() {
    try { if (localStorage.getItem('mi_member_token')) return true; } catch (e) {}
    return window._isMiembro === true;
  }
  if (!forzar && visto()) return;

  var CSS = '\
.pw{position:fixed;inset:0;z-index:100000;display:flex;align-items:center;justify-content:center;padding:20px;\
  background:radial-gradient(60% 50% at 50% 40%,rgba(242,201,76,.10),transparent 70%),rgba(3,8,17,.82);\
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);opacity:0;transition:opacity .35s ease}\
.pw.on{opacity:1}\
.pw__card{position:relative;width:min(980px,100%);max-height:calc(100vh - 40px);overflow:auto;border-radius:26px;padding:2px;\
  background:linear-gradient(135deg,rgba(247,220,111,.95),rgba(242,201,76,.25) 30%,rgba(90,140,230,.25) 65%,rgba(247,220,111,.85));\
  box-shadow:0 40px 120px -20px rgba(0,0,0,.9),0 0 80px rgba(242,201,76,.18);transform:translateY(14px) scale(.98);transition:transform .45s cubic-bezier(.2,.8,.2,1)}\
.pw.on .pw__card{transform:none}\
.pw__in{position:relative;overflow:hidden;border-radius:24px;display:grid;grid-template-columns:1.05fr 1fr;gap:8px;\
  background:radial-gradient(55% 45% at 0% 0%,rgba(242,201,76,.16),transparent 70%),radial-gradient(60% 55% at 100% 100%,rgba(64,128,232,.24),transparent 70%),linear-gradient(180deg,#0c1a33,#070f20);\
  color:#f3f6fb;font-family:"IBM Plex Sans",system-ui,sans-serif}\
.pw__in::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.5;\
  background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 34px),repeating-linear-gradient(90deg,rgba(255,255,255,.018) 0 1px,transparent 1px 34px)}\
.pw__in::after{content:"";position:absolute;top:-40%;bottom:-40%;left:-30%;width:18%;pointer-events:none;transform:rotate(18deg);\
  background:linear-gradient(90deg,transparent,rgba(255,240,190,.10),transparent);animation:pwSweep 6s ease-in-out infinite}\
@keyframes pwSweep{0%,60%{left:-30%}100%{left:130%}}\
.pw__x{position:absolute;top:14px;right:14px;z-index:3;width:38px;height:38px;border-radius:50%;border:1px solid rgba(255,255,255,.16);\
  background:rgba(7,15,32,.7);color:#f3f6fb;font-size:20px;line-height:1;cursor:pointer}\
.pw__x:hover{color:#fff;border-color:rgba(242,201,76,.6)}\
.pw__copy{position:relative;z-index:1;padding:40px 8px 34px 42px}\
.pw__kick{display:inline-flex;align-items:center;gap:8px;font:600 12px/1 "IBM Plex Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:#f6d77e}\
.pw__kick i{width:7px;height:7px;border-radius:50%;background:#56c793;box-shadow:0 0 0 4px rgba(86,199,147,.18)}\
.pw h2{margin:16px 0 0;font:400 46px/1.02 "DM Serif Display",Georgia,serif;letter-spacing:-.015em;color:#f3f6fb}\
.pw h2 em{font-style:italic;color:#f6d77e}\
.pw__deal{display:flex;align-items:center;gap:18px;margin-top:24px;flex-wrap:wrap}\
.pw__off{position:relative;overflow:hidden;isolation:isolate;display:inline-flex;align-items:baseline;gap:8px;white-space:nowrap;\
  font:800 30px/1 "IBM Plex Sans",system-ui,sans-serif;color:#0a1322;padding:14px 22px;border-radius:999px;\
  background:linear-gradient(135deg,#fbe7a0 0%,#f2c94c 42%,#d9a92e 100%);\
  box-shadow:0 0 0 2px rgba(255,240,190,.7) inset,0 0 30px rgba(242,201,76,.6),0 0 80px rgba(242,201,76,.28);animation:pwGlow 2.4s ease-in-out infinite}\
.pw__off b{font-size:1.3em;letter-spacing:-.02em}\
.pw__off::after{content:"";position:absolute;top:-30%;bottom:-30%;left:-60%;width:30%;z-index:-1;transform:skewX(-20deg);\
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.9),transparent);animation:pwShine 2.8s ease-in-out infinite}\
@keyframes pwShine{0%,50%{left:-60%}100%{left:140%}}\
@keyframes pwGlow{0%,100%{box-shadow:0 0 0 2px rgba(255,240,190,.6) inset,0 0 24px rgba(242,201,76,.5),0 0 60px rgba(242,201,76,.2)}\
  50%{box-shadow:0 0 0 2px rgba(255,240,190,.85) inset,0 0 40px rgba(242,201,76,.8),0 0 100px rgba(242,201,76,.38)}}\
.pw__price{display:flex;align-items:baseline;gap:10px;white-space:nowrap}\
.pw__price s{font:400 24px/1 "DM Serif Display",serif;color:#f3f6fb;text-decoration-color:#f07b70;text-decoration-thickness:2px}\
.pw__price strong{font:400 52px/1 "DM Serif Display",serif;color:#f6d77e}\
.pw__price span{font:500 15px "IBM Plex Sans",sans-serif;color:#f3f6fb}\
.pw__list{list-style:none;margin:24px 0 0;padding:0;display:flex;flex-direction:column;gap:11px}\
.pw__list li{display:flex;gap:12px;align-items:flex-start;font:500 15.5px/1.4 "IBM Plex Sans",sans-serif;color:#f3f6fb}\
.pw__list li::before{content:"";flex:none;width:9px;height:9px;margin-top:6px;border-radius:50%;background:#f2c94c;box-shadow:0 0 0 4px rgba(242,201,76,.16)}\
.pw__list b{color:#f6d77e;font-weight:600}\
.pw__cd{margin-top:26px}\
.pw__cdh{font:600 11.5px/1 "IBM Plex Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:#f6d77e;margin-bottom:10px}\
.pw__cdg{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;max-width:400px}\
.pw__cdg div{border:1px solid rgba(242,201,76,.32);border-radius:12px;padding:11px 4px 9px;text-align:center;\
  background:linear-gradient(180deg,rgba(242,201,76,.10),rgba(242,201,76,.02))}\
.pw__cdg b{display:block;font:600 30px/1 "IBM Plex Mono",monospace;color:#fff;font-variant-numeric:tabular-nums;text-shadow:0 0 18px rgba(242,201,76,.35)}\
.pw__cdg span{display:block;margin-top:6px;font:600 10.5px/1 "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:#f3f6fb}\
.pw__cta{display:flex;align-items:center;gap:18px;margin-top:26px;flex-wrap:wrap}\
.pw__btn{position:relative;overflow:hidden;border:0;cursor:pointer;border-radius:14px;padding:16px 26px;\
  font:700 16px/1 "IBM Plex Sans",sans-serif;color:#0a1322;background:linear-gradient(135deg,#f7dc6f,#f2c94c 50%,#e2b23a);\
  box-shadow:0 14px 34px -12px rgba(242,201,76,.7)}\
.pw__btn:hover{filter:brightness(1.06)}\
.pw__no{border:0;background:none;cursor:pointer;font:500 14px "IBM Plex Sans",sans-serif;color:#f3f6fb;text-decoration:underline;text-underline-offset:3px}\
.pw__mp{margin-top:16px;font:500 13px "IBM Plex Sans",sans-serif;color:#f3f6fb}\
.pw__mp b{color:#fff;font-weight:600}\
.pw__vis{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;padding:30px 26px 30px 0}\
.pw__vis::before{content:"";position:absolute;width:70%;height:60%;border-radius:50%;background:rgba(242,201,76,.16);filter:blur(70px)}\
.pw__vis{min-height:520px}\
.pw__phone{position:absolute;left:4%;top:50%;width:54%;transform:translateY(-66%) rotate(-3deg);border-radius:26px;overflow:hidden;\
  border:1px solid rgba(214,226,244,.2);box-shadow:0 40px 80px -24px rgba(0,0,0,.9)}\
.pw__chart{position:absolute;right:0;top:50%;width:70%;transform:translateY(34%) rotate(2deg);border-radius:18px;overflow:hidden;background:#0f1a2d;\
  border:1px solid rgba(242,201,76,.35);box-shadow:0 40px 80px -24px rgba(0,0,0,.95),0 0 40px rgba(242,201,76,.12)}\
.pw__phone img,.pw__chart img{display:block;width:100%;height:auto}\
.pw__charth{display:flex;align-items:center;gap:10px;padding:11px 14px;border-bottom:1px solid rgba(214,226,244,.12);font:400 17px "DM Serif Display",serif;color:#f3f6fb}\
.pw__charth i{width:26px;height:26px;border-radius:50%;border:1.5px solid #f2c94c;display:grid;place-items:center;font:400 13px "DM Serif Display",serif;font-style:normal;color:#f2c94c}\
.pw__charth em{margin-left:auto;font:600 10.5px "IBM Plex Mono",monospace;font-style:normal;letter-spacing:.08em;color:#f6d77e;border:1px solid rgba(242,201,76,.5);border-radius:999px;padding:4px 8px}\
.pw__spark{position:absolute;z-index:2;width:18px;height:18px;background:#fff6d4;pointer-events:none;\
  clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);filter:drop-shadow(0 0 6px rgba(255,236,170,.95));animation:pwTw 2.2s ease-in-out infinite}\
@keyframes pwTw{0%,100%{transform:scale(.6);opacity:.5}50%{transform:scale(1.1);opacity:1}}\
@media (max-width:820px){\
  .pw{padding:12px;align-items:flex-end}\
  .pw__card{max-height:calc(100vh - 24px)}\
  .pw__in{grid-template-columns:1fr;gap:0}\
  .pw__vis{order:-1;min-height:0;height:190px;padding:0;overflow:hidden}\
  .pw__phone{left:5%;top:16px;width:40%;transform:rotate(-3deg);border-radius:18px}\
  .pw__chart{right:4%;top:44px;width:62%;transform:rotate(2deg)}\
  .pw__charth{font-size:12px;padding:7px 10px}.pw__charth i{width:18px;height:18px;font-size:10px}.pw__charth em{font-size:8px;padding:3px 6px}\
  .pw__copy{padding:16px 20px 20px}\
  .pw h2{font-size:29px;margin-top:10px}\
  .pw__list li:nth-child(3){display:none}\
  .pw__deal{margin-top:16px;gap:14px}\
  .pw__off{font-size:20px;padding:10px 15px}\
  .pw__price strong{font-size:36px}\
  .pw__price s{font-size:19px}\
  .pw__list{margin-top:16px;gap:8px}\
  .pw__list li{font-size:14px}\
  .pw__cd{margin-top:18px}\
  .pw__cdg div{padding:8px 4px 7px}\
  .pw__cdg b{font-size:22px}\
  .pw__cta{margin-top:16px;gap:10px}\
  .pw__btn{padding:14px 20px}\
  .pw__mp{margin-top:10px;font-size:12px}\
  .pw__btn{flex:1 1 100%;text-align:center}\
  .pw__no{margin:0 auto}\
  .pw__mp{text-align:center}\
}\
@media (prefers-reduced-motion:reduce){.pw,.pw__card{transition:none}.pw__off,.pw__off::after,.pw__in::after,.pw__spark{animation:none}.pw__off::after,.pw__in::after{display:none}}';

  var HTML = '\
<div class="pw__card" role="dialog" aria-modal="true" aria-labelledby="pwTitle"><div class="pw__in">\
  <button type="button" class="pw__x" aria-label="Cerrar">&times;</button>\
  <div class="pw__copy">\
    <span class="pw__kick"><i></i>Lanzamiento · Warren nuevo</span>\
    <h2 id="pwTitle">Mejoramos Warren.<br><em>Y bajamos el precio.</em></h2>\
    <div class="pw__deal">\
      <span class="pw__off"><b>' + P.off + '%</b> OFF</span>\
      <span class="pw__price"><s>USD ' + P.antes + '</s><strong>USD ' + P.usd + '</strong><span>/ mes</span></span>\
    </div>\
    <ul class="pw__list">\
      <li><span><b>Warren</b> te arma informes completos: DCF, escenarios, catalizadores y fuentes.</span></li>\
      <li><span><b>Portfolio</b> con informes de tu cartera: riesgo, beta, correlaciones y peor mes.</span></li>\
      <li><span><b>48 informes</b> de research con fair value, todos incluidos.</span></li>\
    </ul>\
    <div class="pw__cd">\
      <div class="pw__cdh">El 33% OFF termina el 31 de octubre</div>\
      <div class="pw__cdg">\
        <div><b data-pw="d">00</b><span>Días</span></div>\
        <div><b data-pw="h">00</b><span>Horas</span></div>\
        <div><b data-pw="m">00</b><span>Min</span></div>\
        <div><b data-pw="s">00</b><span>Seg</span></div>\
      </div>\
    </div>\
    <div class="pw__cta">\
      <button type="button" class="pw__btn">Quiero el ' + P.off + '% OFF &rarr;</button>\
      <button type="button" class="pw__no">Ahora no</button>\
    </div>\
    <div class="pw__mp">Pagás con <b>Mercado Pago</b>, en pesos · cancelás cuando quieras</div>\
  </div>\
  <div class="pw__vis">\
    <div class="pw__phone"><img src="assets/promo/warren-chat.webp" alt="Chat de Warren: Analizá NVDA y la respuesta con el informe" width="582" height="710"></div>\
    <div class="pw__chart"><div class="pw__charth"><i>W</i>NVIDIA Corporation<em>NEUTRAL</em></div><img src="assets/promo/warren-grafico.webp" alt="Gráfico de ingresos trimestrales de NVIDIA del informe de Warren" width="1048" height="465"></div>\
    <i class="pw__spark" style="top:12%;left:4%"></i><i class="pw__spark" style="bottom:12%;right:6%;animation-delay:.8s"></i><i class="pw__spark" style="top:6%;right:24%;width:12px;height:12px;animation-delay:1.4s"></i>\
  </div>\
</div></div>';

  var root, timer;
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function tick() {
    var ms = Math.max(0, FIN - Date.now());
    var t = Math.floor(ms / 1000);
    var v = { d: Math.floor(t / 86400), h: Math.floor(t % 86400 / 3600), m: Math.floor(t % 3600 / 60), s: t % 60 };
    for (var k in v) { var el = root.querySelector('[data-pw="' + k + '"]'); if (el) el.textContent = pad(v[k]); }
    if (ms <= 0) cerrar();
  }
  function cerrar() {
    if (!root) return;
    clearInterval(timer);
    document.removeEventListener('keydown', onKey);
    root.classList.remove('on');
    var r = root; root = null;
    setTimeout(function () { r.remove(); document.documentElement.style.overflow = ''; }, 350);
  }
  function onKey(e) { if (e.key === 'Escape') cerrar(); }

  function abrir() {
    if (root || (!forzar && esSocio())) return;
    marcar();
    var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    root = document.createElement('div'); root.className = 'pw'; root.innerHTML = HTML;
    document.body.appendChild(root);
    document.documentElement.style.overflow = 'hidden';
    tick(); timer = setInterval(tick, 1000);
    root.addEventListener('click', function (e) { if (e.target === root) cerrar(); });
    root.querySelector('.pw__x').onclick = cerrar;
    root.querySelector('.pw__no').onclick = cerrar;
    root.querySelector('.pw__btn').onclick = function () { cerrar(); if (window.openPaymentModal) window.openPaymentModal(); };
    document.addEventListener('keydown', onKey);
    // el anuncio chico de la esquina sobra si ya se vio este
    var fb = document.getElementById('featureBanner'); if (fb) fb.style.display = 'none';
    requestAnimationFrame(function () { requestAnimationFrame(function () { root && root.classList.add('on'); }); });
    // si al terminar de cargar la sesión resulta socio, se cierra solo
    var chequeos = 0, iv = setInterval(function () { if (!root || ++chequeos > 20) return clearInterval(iv); if (!forzar && esSocio()) cerrar(); }, 500);
  }
  function arrancar() { setTimeout(abrir, 1200); }
  if (document.readyState === 'complete') arrancar(); else window.addEventListener('load', arrancar);
})();
