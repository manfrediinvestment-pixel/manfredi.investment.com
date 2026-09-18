/* Cartel de membresía de la home (#membresia): carrusel de 3 secciones premium
   (Warren IA · Informes · Portfolio). Se monta en un Shadow DOM para que su CSS
   quede aislado del resto de la página. Las cifras de Warren salen del informe
   de AAPL (Q3 FY2026); las del Portfolio son de ejemplo. Las hojas de
   assets/cartel/pages/ son capturas reales de los informes.
   Test: agregar ?cartel=0|1|2 a la URL fija una sección sin autoplay. */
(function(){
  var host=document.getElementById('mcHost');
  if(!host||!host.attachShadow)return;
  var root=host.attachShadow({mode:'open'});
  var CSS="\n  :host{display:block;color:var(--ink);font-family:var(--sans);\n    --bg:#07101e; --raised:#0c1828; --raised2:#0f1f34;\n    --line:rgba(255,255,255,.09); --line-soft:rgba(255,255,255,.05);\n    --ink:#e8eef6; --ink2:rgba(232,238,246,.64); --ink3:rgba(232,238,246,.38);\n    --amber:#f2c94c; --pos:#10b981; --neg:#ef4444; --data:#5aa9e6;\n    --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;\n    --sans:'IBM Plex Sans',system-ui,sans-serif;\n    --serif:'DM Serif Display',Georgia,serif;\n  }\n  *{box-sizing:border-box}\n\n  /* ===== marco ===== */\n  .frame{max-width:1280px;margin:0 auto;position:relative;height:520px;border:1px solid rgba(242,201,76,.28);\n    background:linear-gradient(135deg,rgba(242,201,76,.08),rgba(242,201,76,0) 58%);display:flex;flex-direction:column;overflow:hidden}\n  .viewport{flex:1;min-height:0;overflow:hidden;position:relative}\n  .track{display:flex;width:300%;height:100%;transition:transform .95s cubic-bezier(.65,0,.25,1)}\n  .slide{width:33.3334%;height:100%;display:grid;grid-template-columns:1fr 1.08fr;gap:36px;padding:24px 36px 8px 44px;align-items:stretch}\n  .copy{display:flex;flex-direction:column;justify-content:center;padding-right:8px}\n  .eyebrow{font:10px var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--amber);margin:0 0 18px;display:flex;gap:12px;align-items:center}\n  .eyebrow i{font-style:normal;color:var(--ink3);letter-spacing:.1em}\n  .copy h3{margin:0 0 14px;font:400 clamp(30px,3.4vw,44px)/1.05 var(--serif);letter-spacing:-.01em}\n  .copy p{margin:0;font-size:14px;line-height:1.6;color:var(--ink2);max-width:40ch}\n  .tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}\n  .tag{font:10px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink2);border:1px solid var(--line);padding:4px 9px}\n  .new{font:700 8.5px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:#07101e;background:var(--amber);padding:2px 6px;margin-left:10px;vertical-align:middle}\n  .vis{min-height:0;position:relative}\n\n  .strip{flex:none;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:0 24px 0 44px;height:64px;border-top:1px solid var(--line-soft)}\n  .tabs{display:flex;gap:26px}\n  .tab{background:none;border:0;padding:0;cursor:pointer;text-align:left;color:var(--ink3);font:10.5px var(--mono);letter-spacing:.1em;text-transform:uppercase;width:132px}\n  .tab span{display:block;margin-bottom:8px;transition:color .3s}\n  .tab .bar{display:block;height:2px;background:var(--line);position:relative;overflow:hidden}\n  .tab .bar b{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--amber)}\n  .tab.on span{color:var(--ink)}\n  .tab.done .bar b{width:100%}\n  .buy{display:flex;align-items:center;gap:14px}\n  .amt{font:600 20px var(--mono);color:var(--amber)}\n  .per{font:11px var(--mono);color:var(--ink3);margin-left:-8px}\n  .btn{font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;padding:11px 20px;background:var(--amber);color:#07101e;border:0;cursor:pointer}\n  .btn:hover{background:#f7dc6f}\n\n  /* ===== 1 · Warren (opción A) ===== */\n  .chat{position:absolute;inset:0 0 14px;border:1px solid var(--line);background:var(--raised);display:flex;flex-direction:column}\n  .chat__bar{display:flex;align-items:center;gap:10px;padding:9px 14px;border-bottom:1px solid var(--line-soft);flex:none}\n  .chat__av{width:24px;height:24px;display:grid;place-items:center;border:1px solid rgba(242,201,76,.4);color:var(--amber);font:13px var(--serif)}\n  .chat__name{font-size:12px;font-weight:600}\n  .chat__name small{margin-left:8px;font:9px var(--mono);letter-spacing:.08em;color:var(--pos);text-transform:uppercase;font-weight:400}\n  .chat__demo{margin-left:auto;font:9px var(--mono);letter-spacing:.08em;color:var(--ink3);text-transform:uppercase}\n  .chat__body{flex:1;min-height:0;padding:10px 14px;display:flex;flex-direction:column;gap:9px;overflow:hidden;scroll-behavior:smooth}\n  .msg{font-size:12.5px;line-height:1.5}\n  .msg--u{align-self:flex-end;max-width:80%;padding:6px 12px;background:rgba(242,201,76,.12);border:1px solid rgba(242,201,76,.3)}\n  .msg--w{align-self:stretch;padding:10px 14px;background:var(--raised2);border:1px solid var(--line);display:flex;flex-direction:column;gap:9px}\n  .msg--w strong{font-weight:600;color:var(--ink)}\n  .verdict{display:flex;align-items:baseline;gap:6px 14px;flex-wrap:wrap}\n  .verdict .tk{font:600 15px var(--mono)}\n  .verdict .px{font:12px var(--mono);color:var(--ink3)}\n  .verdict .fv{font:600 15px var(--mono);color:var(--amber)}\n  .verdict .gap{font:600 12px var(--mono);color:var(--neg)}\n  .verdict .chip{font:9.5px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--amber);border:1px solid rgba(242,201,76,.4);padding:2px 7px}\n  .kpis{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line-soft)}\n  .kpi{padding:6px 10px;border-right:1px solid var(--line-soft)}\n  .kpi:last-child{border-right:0}\n  .kpi small{display:block;font:8.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);margin-bottom:2px}\n  .kpi strong{font:600 13px var(--mono);font-variant-numeric:tabular-nums}\n  .up{color:var(--pos)} .dn{color:var(--neg)}\n  .sec{font:9.5px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--amber);display:flex;align-items:center;gap:8px}\n  .sec::after{content:'';flex:1;height:1px;background:var(--line-soft)}\n  .tbl{width:100%;border-collapse:collapse;font:10.5px var(--mono);font-variant-numeric:tabular-nums}\n  .tbl th{font-weight:400;font-size:8.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);text-align:right;padding:3px 6px;border-bottom:1px solid var(--line)}\n  .tbl th:first-child,.tbl td:first-child{text-align:left;padding-left:0}\n  .tbl td{padding:4px 6px;text-align:right;border-bottom:1px solid var(--line-soft);color:var(--ink)}\n  .tbl td:first-child{color:var(--ink2)}\n  .tbl tr.tot td{font-weight:600;border-bottom:0;color:var(--amber)}\n  .tbl tr.tot td:first-child{color:var(--amber)}\n  .tbl tr{animation:rowin .35s ease both}\n  @keyframes rowin{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}\n  .bars{display:flex;flex-direction:column;gap:5px;position:relative;padding:2px 0}\n  .brow{display:grid;grid-template-columns:118px 1fr 58px;align-items:center;gap:8px;font:10.5px var(--mono)}\n  .brow>span:first-child{color:var(--ink2)}\n  .track2{position:relative;height:9px;background:rgba(255,255,255,.04)}\n  .fill{position:absolute;left:0;top:0;bottom:0;width:0;background:rgba(90,169,230,.65);transition:width .9s cubic-bezier(.2,.8,.2,1)}\n  .brow.hi .fill{background:var(--amber)}\n  .brow em{font-style:normal;text-align:right}\n  .mkt{position:absolute;top:0;bottom:0;width:0;border-left:1.5px dashed var(--neg);opacity:0;transition:opacity .5s}\n  .mkt::after{content:'Mercado $306';position:absolute;top:-12px;left:-38px;font:8.5px var(--mono);color:var(--neg);white-space:nowrap}\n  .txt{font-size:12.5px;line-height:1.55;color:var(--ink2)}\n  .src{align-self:flex-start;font:9.5px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--data);border:1px solid rgba(90,169,230,.35);padding:3px 8px}\n  .hid{opacity:0;transform:translateY(6px)}\n  .hid.on{opacity:1;transform:none;transition:opacity .45s,transform .45s}\n  .dots{display:inline-flex;gap:4px;padding:3px 0}\n  .dots i{width:5px;height:5px;border-radius:50%;background:var(--ink3);animation:blink 1.1s infinite}\n  .dots i:nth-child(2){animation-delay:.15s}.dots i:nth-child(3){animation-delay:.3s}\n  .caret::after{content:'';display:inline-block;width:6px;height:12px;background:var(--amber);margin-left:2px;vertical-align:-1px;animation:blink 1s infinite}\n  @keyframes blink{50%{opacity:.25}}\n  .chat__input{display:flex;gap:8px;padding:9px 12px;border-top:1px solid var(--line-soft);flex:none}\n  .chat__field{flex:1;font-size:11.5px;color:var(--ink3);padding:8px 11px;border:1px solid var(--line);background:rgba(255,255,255,.02)}\n  .chat__send{width:34px;display:grid;place-items:center;background:var(--amber);color:#07101e;font-weight:700}\n\n  /* ===== 2 · Informes (sin cambios) ===== */\n  .deckbox{position:absolute;inset:0 0 14px;border:1px solid var(--line);background:radial-gradient(90% 80% at 32% 30%,#10233d 0%,#08111f 75%);overflow:hidden}\n  .stack{position:absolute;left:50%;top:50%;width:255px;height:332px;margin:-166px 0 0 -190px}\n  .pgc{position:absolute;inset:0;background:#fff;transform-origin:0% 100%;box-shadow:0 14px 30px rgba(0,0,0,.5),0 0 0 1px rgba(0,0,0,.25);\n    transition:transform .8s cubic-bezier(.3,.7,.2,1),opacity .6s,filter .8s}\n  .pgc img{display:block;width:100%;height:100%;object-fit:cover;object-position:top}\n  .pgc.out{transform:translate(-115%,6px) rotate(-9deg)!important;opacity:0!important}\n  .deckcap{position:absolute;left:0;right:0;bottom:14px;display:flex;justify-content:center;gap:14px;font:10px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink3)}\n  .deckcap .now{color:var(--ink);min-width:200px;text-align:left}\n\n  /* ===== 3 · Portfolio: carga de activos + ratios + gráficos ===== */\n  .pf{position:absolute;inset:0 0 14px;border:1px solid var(--line);background:var(--raised);padding:12px 14px;display:flex;flex-direction:column;gap:10px}\n  .pf__top{flex:1;min-height:0;display:grid;grid-template-columns:.92fr 1.08fr;gap:14px}\n  .colt{font:9px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:7px;display:flex;justify-content:space-between;align-items:baseline;gap:8px}\n  .colt b{color:var(--amber);font-weight:500}\n  .colt .k1{color:var(--amber);font-style:normal} .colt .k2{color:var(--data);font-style:normal;margin-left:8px}\n  .colt .k1 b,.colt .k2 b{color:inherit;font-weight:600}\n  .addrow{display:grid;grid-template-columns:1.2fr .8fr auto;gap:6px;margin-bottom:6px}\n  .inp{font:11px var(--mono);padding:6px 9px;border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--ink);min-height:28px;display:flex;align-items:center}\n  .inp.ph{color:var(--ink3)}\n  .inp.focus{border-color:rgba(242,201,76,.6)}\n  .addbtn{font:600 9.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:0 11px;display:grid;place-items:center;background:rgba(242,201,76,.14);color:var(--amber);border:1px solid rgba(242,201,76,.4);transition:all .2s}\n  .addbtn.press{background:var(--amber);color:#07101e}\n  .hold{display:flex;flex-direction:column;gap:3px}\n  .hrow{display:grid;grid-template-columns:44px 1fr 32px;gap:8px;align-items:center;padding:4px 8px;border:1px solid var(--line-soft);background:rgba(255,255,255,.02);font:10.5px var(--mono);animation:rowin .4s ease both;height:25px}\n  .hrow .tk{font-weight:600;color:var(--ink)}\n  .hrow .nm{color:var(--ink3);font-size:9px;display:flex;flex-direction:column;gap:3px}\n  .wbar{height:3px;background:rgba(255,255,255,.06);position:relative}\n  .wbar b{position:absolute;left:0;top:0;bottom:0;background:var(--amber);width:0;transition:width .7s cubic-bezier(.2,.8,.2,1)}\n  .hrow .pc{text-align:right;color:var(--ink2)}\n  .pfchart{display:flex;flex-direction:column;min-height:0;border:1px solid var(--line-soft);padding:8px 10px 8px;background:rgba(255,255,255,.015)}\n  .pfchart svg{flex:1;min-height:0;width:100%;margin:2px 0 6px}\n  .sbar{display:flex;height:7px;background:rgba(255,255,255,.05);overflow:hidden}\n  .sbar span{display:block;height:100%;width:0;transition:width .8s cubic-bezier(.2,.8,.2,1)}\n  .sleg{display:flex;gap:12px;margin-top:5px;font:9px var(--mono);color:var(--ink2);flex-wrap:wrap}\n  .sleg i{display:inline-block;width:7px;height:7px;margin-right:5px}\n  .ratios{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}\n  .rt{border:1px solid var(--line-soft);background:rgba(255,255,255,.02);padding:6px 10px;transition:border-color .4s,background .4s}\n  .rt small{display:block;font:8px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);margin-bottom:2px;white-space:nowrap}\n  .rt strong{font:600 15px var(--mono);font-variant-numeric:tabular-nums;color:var(--ink3);transition:color .4s}\n  .rt em{font:9px var(--mono);font-style:normal;margin-left:6px}\n  .rt.live strong{color:var(--ink)}\n  .rt.flash{border-color:rgba(242,201,76,.7);background:rgba(242,201,76,.07)}\n  .insight{border:1px solid rgba(242,201,76,.3);background:rgba(242,201,76,.06);padding:7px 12px;font-size:11.5px;line-height:1.45;color:var(--ink2);min-height:38px;display:flex;gap:9px;align-items:flex-start}\n  .insight .w{flex:none;width:20px;height:20px;display:grid;place-items:center;border:1px solid rgba(242,201,76,.4);color:var(--amber);font:12px var(--serif)}\n  .insight strong{color:var(--ink)}\n\n  @media (max-width:1040px){\n    .frame{height:auto}\n    .viewport{height:780px;flex:none}\n    .slide{grid-template-columns:1fr;gap:16px;padding:22px 18px 6px;grid-template-rows:auto 1fr}\n    .copy h3{font-size:30px}\n    .copy p{font-size:13px}\n    .copy .tags{display:none}\n    .strip{padding:12px 16px;height:auto;flex-wrap:wrap}\n    .tabs{gap:12px;width:100%}.tab{width:auto;flex:1}\n    .buy{width:100%;justify-content:space-between}\n    .stack{margin-left:-125px}\n    .brow{grid-template-columns:92px 1fr 52px}\n    .pf__top{grid-template-columns:1fr}\n    .ratios{grid-template-columns:repeat(2,1fr)}\n  }\n  @media (prefers-reduced-motion:reduce){.track,.pgc{transition:none}}\n\n  .go{align-self:flex-start;margin-top:18px;font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:rgba(242,201,76,.92);border:1px solid rgba(242,201,76,.38);background:transparent;padding:10px 16px;cursor:pointer;transition:background .18s,border-color .18s}\n  .go:hover,.go:focus-visible{background:rgba(242,201,76,.1);border-color:rgba(242,201,76,.75);outline:0}\n  .vis[data-go]{cursor:pointer}\n  .vis[data-go] .chat,.vis[data-go] .deckbox,.vis[data-go] .pf{transition:border-color .2s}\n  .vis[data-go]:hover .chat,.vis[data-go]:hover .deckbox,.vis[data-go]:hover .pf{border-color:rgba(242,201,76,.45)}\n";
  var HTML="<div class=\"frame\" id=\"frame\">\n    <div class=\"viewport\">\n      <div class=\"track\" id=\"track\">\n\n        <!-- 1 · WARREN IA -->\n        <div class=\"slide\" id=\"s0\">\n          <div class=\"copy\">\n            <div class=\"eyebrow\">Membresía Manfredi Investment <i>01 / 03</i></div>\n            <h3>Warren IA</h3>\n            <p>Tu asesor de inversiones con inteligencia artificial. Le preguntás en criollo por un activo o por tu cartera, y te responde con datos y la fuente.</p>\n            <div class=\"tags\"><span class=\"tag\">100 consultas / mes</span><span class=\"tag\">24/7</span></div><button type=\"button\" class=\"go\" data-go=\"warren\">Hablar con Warren &rarr;</button>\n          </div>\n          <div class=\"vis\" data-go=\"warren\" title=\"Ir a esta secci&oacute;n\">\n            <div class=\"chat\">\n              <div class=\"chat__bar\"><span class=\"chat__av\">W</span><span class=\"chat__name\">Warren · Asesor IA<small>● En línea</small></span><span class=\"chat__demo\">Consulta de ejemplo</span></div>\n              <div class=\"chat__body\"></div>\n              <div class=\"chat__input\"><div class=\"chat__field\">Preguntale sobre un informe, un activo o tu cartera…</div><div class=\"chat__send\">→</div></div>\n            </div>\n          </div>\n        </div>\n\n        <!-- 2 · INFORMES -->\n        <div class=\"slide\" id=\"s1\">\n          <div class=\"copy\">\n            <div class=\"eyebrow\">Membresía Manfredi Investment <i>02 / 03</i></div>\n            <h3>Informes institucionales de acciones</h3>\n            <p>Análisis completo de cada empresa: 14 secciones, cuatro métodos de valuación y un fair value explícito, con la tesis, los riesgos y los catalizadores.</p>\n            <div class=\"tags\"><span class=\"tag\">39 informes</span><span class=\"tag\">DCF · Comparables · Consenso</span></div><button type=\"button\" class=\"go\" data-go=\"informes\">Ver los informes &rarr;</button>\n          </div>\n          <div class=\"vis\" data-go=\"informes\" title=\"Ir a esta secci&oacute;n\">\n            <div class=\"deckbox\">\n              <div class=\"stack\" id=\"stack\"></div>\n              <div class=\"deckcap\"><span class=\"now\" id=\"decknow\">—</span></div>\n            </div>\n          </div>\n        </div>\n\n        <!-- 3 · PORTFOLIO -->\n        <div class=\"slide\" id=\"s2\">\n          <div class=\"copy\">\n            <div class=\"eyebrow\">Membresía Manfredi Investment <i>03 / 03</i></div>\n            <h3>Manfredi Investment Portfolio<span class=\"new\">Nuevo</span></h3>\n            <p>Cargá tus activos y el portfolio calcula solo los ratios de tu cartera: beta, volatilidad, Sharpe, VaR, drawdown y más. Warren te explica cada uno.</p>\n            <div class=\"tags\"><span class=\"tag\">Beta · Sharpe · VaR</span><span class=\"tag\">Drawdown</span><span class=\"tag\">vs. S&amp;P 500</span></div><button type=\"button\" class=\"go\" data-go=\"portfolio\">Armar mi portfolio &rarr;</button>\n          </div>\n          <div class=\"vis\" data-go=\"portfolio\" title=\"Ir a esta secci&oacute;n\">\n            <div class=\"pf\">\n              <div class=\"pf__top\">\n                <div>\n                  <div class=\"colt\"><span>Cargá tus activos</span><b class=\"cnt\">0 activos</b></div>\n                  <div class=\"addrow\"><div class=\"inp ph\" data-f=\"t\">Ticker</div><div class=\"inp ph\" data-f=\"q\">Cantidad</div><div class=\"addbtn\">+ Agregar</div></div>\n                  <div class=\"hold\"></div>\n                </div>\n                <div class=\"pfchart\">\n                  <div class=\"colt\"><span>Rendimiento</span><span><em class=\"k1\">Tu cartera <b class=\"rc\">—</b></em><em class=\"k2\">S&amp;P <b class=\"rs\">—</b></em></span></div>\n                  <svg viewBox=\"0 0 300 110\" preserveAspectRatio=\"none\" aria-hidden=\"true\">\n                    <line x1=\"0\" x2=\"300\" y1=\"28\" y2=\"28\" stroke=\"rgba(255,255,255,.06)\"/><line x1=\"0\" x2=\"300\" y1=\"56\" y2=\"56\" stroke=\"rgba(255,255,255,.06)\"/><line x1=\"0\" x2=\"300\" y1=\"84\" y2=\"84\" stroke=\"rgba(255,255,255,.06)\"/>\n                    <path class=\"area\" d=\"M0 110 L300 110 Z\" fill=\"rgba(242,201,76,.10)\"/>\n                    <path class=\"lsp\" d=\"\" fill=\"none\" stroke=\"#5aa9e6\" stroke-width=\"1.8\" stroke-linejoin=\"round\" vector-effect=\"non-scaling-stroke\"/>\n                    <path class=\"lpf\" d=\"\" fill=\"none\" stroke=\"#f2c94c\" stroke-width=\"2.2\" stroke-linejoin=\"round\" vector-effect=\"non-scaling-stroke\"/>\n                  </svg>\n                  <div class=\"sbar\"><span data-s=\"0\" style=\"background:#f2c94c\"></span><span data-s=\"1\" style=\"background:#5aa9e6\"></span><span data-s=\"2\" style=\"background:#10b981\"></span></div>\n                  <div class=\"sleg\"><span><i style=\"background:#f2c94c\"></i>Tecnología <b class=\"s0\">—</b></span><span><i style=\"background:#5aa9e6\"></i>Financiero <b class=\"s1\">—</b></span><span><i style=\"background:#10b981\"></i>Consumo <b class=\"s2\">—</b></span></div>\n                </div>\n              </div>\n              <div class=\"ratios\"></div>\n              <div class=\"insight\"><span class=\"w\">W</span><span class=\"itxt\" style=\"color:var(--ink3)\">Warren interpreta tus ratios apenas cargás la cartera…</span></div>\n            </div>\n          </div>\n        </div>\n\n      </div>\n    </div>\n\n    <div class=\"strip\">\n      <div class=\"tabs\" id=\"tabs\">\n        <button class=\"tab\" type=\"button\"><span>Warren IA</span><span class=\"bar\"><b></b></span></button>\n        <button class=\"tab\" type=\"button\"><span>Informes</span><span class=\"bar\"><b></b></span></button>\n        <button class=\"tab\" type=\"button\"><span>Portfolio</span><span class=\"bar\"><b></b></span></button>\n      </div>\n      <div class=\"buy\"><span class=\"amt\">USD 15</span><span class=\"per\">/ mes</span><button class=\"btn\" type=\"button\">Suscribirme →</button></div>\n    </div>\n  </div>";
  root.innerHTML='<style>'+CSS+'</style>'+HTML;

var q=new URLSearchParams(location.search), fixed=q.has('cartel'), STATIC=fixed;
if(fixed){var st=document.createElement('style');st.textContent='.track,.fill,.hid.on,.mkt,.pgc,.wbar b,.sbar span,.rt,.rt strong,.addbtn{transition:none!important}.hrow,.tbl tr{animation:none!important}.caret::after{display:none}.chat__body{scroll-behavior:auto!important}';root.appendChild(st);}

function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
function wait(S,t,ms){return new Promise(function(r){setTimeout(function(){r(t===S.v);},ms/(S.k||1));});}
function fmt(n){return String(n).replace('.',',');}

/* ---------- API de chat ---------- */
function Chat(root,S,t){
  var body=root.querySelector('.chat__body');
  function w(ms){return wait(S,t,ms);}
  function bottom(){body.scrollTop=body.scrollHeight;}
  this.reset=function(){body.innerHTML='';};
  this.w=w; this.bottom=bottom;
  this.user=async function(text){
    var u=el('div','msg msg--u caret'); body.appendChild(u); bottom();
    for(var k=1;k<=text.length;k++){u.textContent=text.slice(0,k); if(!await w(STATIC?0:24))return false;}
    u.classList.remove('caret'); return await w(350);
  };
  this.think=async function(){
    var b=el('div','msg msg--w','<span class="dots"><i></i><i></i><i></i></span>'); body.appendChild(b); bottom();
    if(!await w(900))return null; b.innerHTML=''; return b;
  };
  this.type=async function(box,html,speed){
    var c=el('div','txt caret'); box.appendChild(c);
    var parts=html.split(/(<[^>]+>|\s+)/).filter(Boolean), acc='';
    for(var i=0;i<parts.length;i++){acc+=parts[i]; c.innerHTML=acc; bottom(); if(parts[i].trim()&&parts[i][0]!=='<'){if(!await w(STATIC?0:(speed||24)))return false;}}
    c.classList.remove('caret'); return true;
  };
  this.show=async function(box,node,pause){
    node.classList.add('hid'); box.appendChild(node); await w(30); node.classList.add('on'); bottom(); return await w(pause==null?600:pause);
  };
  this.sec=function(txt){return el('div','sec',txt);};
  this.verdict=function(){return el('div','verdict','<span class="tk">AAPL</span><span class="px">mercado $306,07</span><span>Fair value propio <span class="fv">$257,08</span></span><span class="gap">−16,0%</span><span class="chip">Valuación exigente</span>');};
  this.kpis=function(){return el('div','kpis','<div class="kpi"><small>Ingresos TTM</small><strong>$466,8B</strong></div><div class="kpi"><small>Q3 interanual</small><strong class="up">+16%</strong></div><div class="kpi"><small>Margen bruto</small><strong>48,7%</strong></div><div class="kpi"><small>Caja neta</small><strong class="up">+$64,2B</strong></div>');};
  this.table=async function(box,head,rows){
    var tb=el('table','tbl','<tr>'+head.map(function(h){return '<th>'+h+'</th>';}).join('')+'</tr>');
    box.appendChild(tb); bottom();
    for(var i=0;i<rows.length;i++){
      var r=rows[i].slice(), tot=r[0].charAt(0)==='*'; if(tot)r[0]=r[0].slice(1);
      tb.appendChild(el('tr',tot?'tot':'', r.map(function(c){return '<td>'+c+'</td>';}).join(''))); bottom();
      if(!await w(STATIC?0:130))return false;
    }
    return true;
  };
  this.bars=async function(box){
    var M=[['DCF · caso Base',184.58,0],['Comparables P/E',224.11,0],['Reversión 10 años',295.60,0],['Consenso Wall St.',324.01,0],['Blend Manfredi',257.08,1]], MAX=340, MK=306.07;
    var bx=el('div','bars'); M.forEach(function(m){bx.appendChild(el('div','brow'+(m[2]?' hi':''),'<span>'+m[0]+'</span><div class="track2"><div class="fill" data-w="'+(m[1]/MAX*100)+'"></div></div><em>$'+fmt(m[1].toFixed(2))+'</em>'));});
    var mk=el('div','mkt'); bx.appendChild(mk); box.appendChild(bx); bottom(); await w(40);
    var tr=bx.querySelector('.track2'); mk.style.left=(tr.offsetLeft+tr.offsetWidth*(MK/MAX))+'px';
    Array.prototype.forEach.call(bx.querySelectorAll('.fill'),function(f,i){setTimeout(function(){if(t===S.v)f.style.width=f.dataset.w+'%';},i*120);});
    if(!await w(STATIC?100:1000))return false; mk.style.opacity=1; return await w(500);
  };
  this.src=function(txt){return el('div','src',txt);};
}

/* ---------- 1 · WARREN (opción A: análisis largo) ---------- */
var T_RES=[['Ingresos totales','$111,18B','$109,42B','$466,82B'],['Margen bruto','49,3%','50,1%¹','48,7%'],['Margen operativo','32,3%','32,6%','33,2%'],['Utilidad neta','$29,58B','$29,79B','$128,93B'],['EPS diluido','$2,01','$2,02','$8,71']];
var T_BAL=[['Efectivo e inversiones','$146,52B'],['Deuda total','$82,35B'],['*Caja neta','+$64,17B'],['Patrimonio neto','$107,52B'],['Activos totales','$383,27B']];
var T_FCF=[['Flujo de caja libre (TTM)','$136,68B'],['Margen de FCF','29,3%'],['Capex / ingresos','2,2%']];
var WS={v:0,k:2.6};   // k = factor de velocidad: el analisis completo se escribe en ~5 s
async function runWarren(){
  var t=++WS.v, sl=root.getElementById('s0'), c=new Chat(sl,WS,t); c.reset();
  if(!await c.w(700))return;
  if(!await c.user('Analizame la acción de Apple (AAPL)'))return;
  var b=await c.think(); if(!b)return;
  if(!await c.show(b,c.verdict(),700))return;
  if(!await c.show(b,c.kpis(),700))return;
  if(!await c.show(b,c.sec('1 · Resultados'),200))return;
  if(!await c.table(b,['Métrica','Q2 FY26','Q3 FY26','TTM'],T_RES))return;
  if(!await c.type(b,'El trimestre fue récord, pero <strong>~2 pp del margen bruto y $0,11 de EPS</strong> vienen de reembolsos de aranceles no recurrentes: sin eso el margen ronda 48%. Además, I+D acelera <strong>+32% interanual</strong>, la señal contable de la apuesta de Apple en IA.'))return;
  if(!await c.show(b,c.sec('2 · Balance y caja'),200))return;
  if(!await c.table(b,['Al 27 jun 2026','Valor'],T_BAL))return;
  if(!await c.table(b,['Flujo de caja','Valor'],T_FCF))return;
  if(!await c.type(b,'Apalancamiento prácticamente nulo: la deuda equivale a <strong>0,5x el EBITDA</strong>. Con un capex de apenas 2,2% de los ingresos, Apple devuelve casi todo el flujo libre en recompras ($62,1B en nueve meses) y sumó una nueva autorización por $100B.'))return;
  if(!await c.show(b,c.sec('3 · Valuación'),200))return;
  if(!await c.bars(b))return;
  if(!await c.type(b,'El blend queda <strong>16% por debajo del mercado</strong>: a 31,7x P/E forward contra 23,2x de sus pares, el precio ya exige años de crecimiento, justo con una guía de septiembre de solo +9%–11% y el primer relevo de CEO en quince años.'))return;
  await c.show(b,c.src('▤ Informe AAPL · Secciones 05, 06, 07 y 13'),0);
}
function stopWarren(){WS.v++; root.querySelector('#s0 .chat__body').innerHTML='';}

/* ---------- 2 · INFORMES (sin cambios) ---------- */
var PAGES=[
 ['assets/cartel/pages/p01_aapl_portada.jpg','AAPL · Portada y fair value'],['assets/cartel/pages/p02_aapl_segmentos.jpg','AAPL · 03 Segmentos'],
 ['assets/cartel/pages/p03_nvda_portada.jpg','NVDA · Portada y fair value'],['assets/cartel/pages/p04_aapl_football.jpg','AAPL · 13 Cuatro métodos'],
 ['assets/cartel/pages/p05_jpm_portada.jpg','JPM · Portada y fair value'],['assets/cartel/pages/p06_googl_capex.jpg','GOOGL · 07 Flujo de caja'],
 ['assets/cartel/pages/p07_meli_portada.jpg','MELI · Portada y fair value'],['assets/cartel/pages/p08_nvda_estados.jpg','NVDA · 05 Estados financieros'],
 ['assets/cartel/pages/p09_tsla_segmentos.jpg','TSLA · 03 Segmentos'],['assets/cartel/pages/p10_googl_football.jpg','GOOGL · 13 Cinco métodos']
];
var stack=root.getElementById('stack'), now=root.getElementById('decknow');
var cards=PAGES.map(function(p){var c=el('div','pgc','<img alt="" src="'+p[0]+'">'); stack.appendChild(c); return c;});
var head=0, deckTimer=null, N=PAGES.length, VIS=5;
function place(c,pos,instant){
  if(instant){c.style.transition='none';}
  var k=Math.min(pos,VIS-1);
  c.style.transform='translate('+(k*32)+'px,'+(-k*10)+'px) scale('+(1-k*.045)+')';
  c.style.filter='brightness('+(1-k*.13)+')';
  c.style.opacity=pos>=VIS?0:1; c.style.zIndex=50-pos;
  if(instant){void c.offsetWidth; c.style.transition='';}
}
function layout(instant){cards.forEach(function(c,i){ if(c.classList.contains('out'))return; place(c,(i-head+N)%N,instant); }); now.textContent=PAGES[head][1];}
function step(){
  var front=cards[head]; front.classList.add('out'); head=(head+1)%N; layout(false);
  setTimeout(function(){front.style.transition='none'; front.classList.remove('out'); place(front,(cards.indexOf(front)-head+N)%N,true);},820);
}
function deckStart(){head=0; cards.forEach(function(c){c.classList.remove('out');}); layout(true); clearInterval(deckTimer); deckTimer=setInterval(step,2000);}
function deckStop(){clearInterval(deckTimer);}

/* ---------- 3 · PORTFOLIO: activos → ratios + gráficos ---------- */
var ASSETS=[['AAPL','25'],['MSFT','10'],['NVDA','30'],['JPM','12'],['KO','40']];
var WEIGHTS=[[100],[57,43],[33,25,42],[27,22,34,17],[26,21,24,15,14]];
var SECT=[[100,0,0],[100,0,0],[100,0,0],[83,17,0],[71,15,14]];
var RATIOS=[[1.19,27.5,0.74,-2.9,-24.8,31.7,0.4,100],[1.12,24.1,0.92,-2.5,-21.3,30.1,0.6,100],[1.31,28.7,1.06,-3.0,-26.9,33.4,0.4,100],[1.19,24.6,1.02,-2.6,-22.1,27.8,1.0,83],[1.03,20.9,1.08,-2.2,-18.7,26.2,1.5,71]];
var RLAB=[['Beta',function(v){return fmt(v.toFixed(2));}],['Volatilidad anual',function(v){return fmt(v.toFixed(1))+'%';}],['Sharpe',function(v){return fmt(v.toFixed(2));}],['VaR 95% (1 día)',function(v){return '−'+fmt(Math.abs(v).toFixed(1))+'%';}],
 ['Drawdown máx.',function(v){return '−'+fmt(Math.abs(v).toFixed(1))+'%';}],['P/E ponderado',function(v){return fmt(v.toFixed(1))+'x';}],['Dividend yield',function(v){return fmt(v.toFixed(1))+'%';}],['Top 3 posiciones',function(v){return Math.round(v)+'%';}]];
var GOODUP=[0,0,1,0,0,0,1,0], NEUTRAL=[1,0,0,0,0,1,0,1]; // beta, P/E y top3: flecha neutra
var SP=[0,1.2,0.8,2.6,3.7,3.1,4.9,5.8,5.2,7.0,8.1,9.0];
var PFS=[[0,2.1,1.0,3.9,6.0,4.8,7.9,9.2,8.1,10.4,11.6,12.4],[0,1.7,1.1,3.4,5.1,4.4,6.8,8.0,7.3,9.4,10.4,11.1],[0,2.9,1.6,5.2,8.4,6.6,11.3,13.6,11.9,16.2,18.1,19.4],[0,2.4,1.5,4.6,7.2,5.9,9.8,11.7,10.2,13.9,15.6,16.6],[0,2.0,1.3,4.0,6.3,5.3,8.7,10.4,9.2,12.3,13.8,14.5]];
var YMIN=-1, YMAX=21;
function ypx(v){return 104-(v-YMIN)/(YMAX-YMIN)*96;}
function pathOf(a){return a.map(function(v,i){return (i?'L':'M')+(i*300/11).toFixed(1)+' '+ypx(v).toFixed(1);}).join(' ');}
var PS={v:0,k:3.6};   // k = factor de velocidad: la carga de 5 activos + ratios en ~5,5 s
async function runPortfolio(){
  var t=++PS.v, pr=root.getElementById('s2');
  function w(ms){return wait(PS,t,ms);}
  var hold=pr.querySelector('.hold'), rat=pr.querySelector('.ratios'), cnt=pr.querySelector('.cnt'), itxt=pr.querySelector('.itxt');
  var inpT=pr.querySelector('[data-f=t]'), inpQ=pr.querySelector('[data-f=q]'), btn=pr.querySelector('.addbtn');
  var lpf=pr.querySelector('.lpf'), lsp=pr.querySelector('.lsp'), area=pr.querySelector('.area'), rc=pr.querySelector('.rc'), rs=pr.querySelector('.rs');
  var sb=pr.querySelectorAll('.sbar span'), sl=[pr.querySelector('.s0'),pr.querySelector('.s1'),pr.querySelector('.s2')];
  hold.innerHTML=''; rat.innerHTML=''; cnt.textContent='0 activos'; rc.textContent='—'; rs.textContent='—';
  itxt.style.color='var(--ink3)'; itxt.textContent='Warren interpreta tus ratios apenas cargás la cartera…';
  lpf.setAttribute('d',''); lsp.setAttribute('d',''); area.setAttribute('d','M0 110 L300 110 Z');
  Array.prototype.forEach.call(sb,function(s){s.style.width='0';}); sl.forEach(function(s){s.textContent='—';});
  function resetInp(){inpT.textContent='Ticker';inpQ.textContent='Cantidad';inpT.className='inp ph';inpQ.className='inp ph';}
  resetInp();
  var tiles=RLAB.map(function(l){var d=el('div','rt','<small>'+l[0]+'</small><strong>—</strong><em></em>'); rat.appendChild(d); return d;});
  var cur=null, curS=null;
  function anim(cb,dur){var s=Date.now(); return new Promise(function(res){(function f(){ if(t!==PS.v)return res(); var p=(STATIC||!dur)?1:Math.min(1,(Date.now()-s)/dur), e=1-Math.pow(1-p,3); cb(e); if(p<1)requestAnimationFrame(f); else res(); })();});}
  await w(900); if(t!==PS.v)return;
  for(var n=0;n<ASSETS.length;n++){
    var a=ASSETS[n];
    inpT.className='inp focus'; inpT.textContent='';
    for(var k=1;k<=a[0].length;k++){inpT.textContent=a[0].slice(0,k); if(!await w(STATIC?0:90))return;}
    inpT.className='inp'; inpQ.className='inp focus'; inpQ.textContent='';
    for(k=1;k<=a[1].length;k++){inpQ.textContent=a[1].slice(0,k); if(!await w(STATIC?0:90))return;}
    if(!await w(260))return; btn.classList.add('press'); if(!await w(240))return; btn.classList.remove('press'); resetInp();
    hold.appendChild(el('div','hrow','<span class="tk">'+a[0]+'</span><span class="nm"><i style="font-style:normal">× '+a[1]+' acc.</i><span class="wbar"><b></b></span></span><span class="pc">0%</span>'));
    cnt.textContent=(n+1)+(n?' activos':' activo');
    await w(30);
    WEIGHTS[n].forEach(function(p,i){var r=hold.children[i]; r.querySelector('b').style.width=p+'%'; r.querySelector('.pc').textContent=p+'%';});
    // sectores
    Array.prototype.forEach.call(sb,function(s,i){s.style.width=SECT[n][i]+'%';}); sl.forEach(function(s,i){s.textContent=SECT[n][i]?SECT[n][i]+'%':'—';});
    // gráfico + ratios en paralelo
    var toS=PFS[n], fromS=curS||PFS[n].map(function(){return 0;}), to=RATIOS[n], from=cur||to.map(function(v){return v*0.6;});
    tiles.forEach(function(tile,i){
      tile.classList.add('live','flash'); setTimeout(function(){tile.classList.remove('flash');},900);
      var em=tile.querySelector('em');
      if(cur){var d=to[i]-cur[i]; if(Math.abs(d)>0.0001){var up=d>0; em.textContent=up?'▲':'▼'; em.style.color=NEUTRAL[i]?'var(--ink3)':(((GOODUP[i]&&up)||(!GOODUP[i]&&!up))?'var(--pos)':'var(--neg)');}}
    });
    await Promise.all([
      anim(function(e){
        var ser=toS.map(function(v,i){return fromS[i]+(v-fromS[i])*e;}), sp=SP.map(function(v){return v*e;});
        lpf.setAttribute('d',pathOf(ser)); lsp.setAttribute('d',pathOf(sp)); area.setAttribute('d',pathOf(ser)+' L300 110 L0 110 Z');
        rc.textContent='+'+fmt(ser[11].toFixed(1))+'%'; rs.textContent='+'+fmt(sp[11].toFixed(1))+'%';
      },1000/PS.k),
      anim(function(e){tiles.forEach(function(tile,i){tile.querySelector('strong').textContent=RLAB[i][1](from[i]+(to[i]-from[i])*e);});},800/PS.k)
    ]);
    cur=to; curS=toS;
    if(!await w(STATIC?0:1100))return;
  }
  itxt.style.color='var(--ink2)'; itxt.innerHTML='';
  var msg='<strong>Concentración en tecnología del 71%</strong>: alta para un perfil moderado. Con beta 1,03, tu cartera se mueve casi igual que el mercado.';
  var parts=msg.split(/(<[^>]+>|\s+)/).filter(Boolean), acc='';
  for(var i=0;i<parts.length;i++){acc+=parts[i]; itxt.innerHTML=acc; if(parts[i].trim()&&parts[i][0]!=='<'){if(!await w(STATIC?0:30))return;}}
}
function stopPortfolio(){PS.v++;}

/* ---------- carrusel ---------- */
var DUR=8000;   // cada seccion dura 8 s y pasa a la siguiente
var track=root.getElementById('track'), tabs=Array.prototype.slice.call(root.querySelectorAll('.tab'));
var cur=-1, elapsed=0, hover=false, visible=false, last=0;
function go(i){
  if(cur===0)stopWarren(); if(cur===1)deckStop(); if(cur===2)stopPortfolio();
  cur=i; elapsed=0;
  track.style.transform='translateX(-'+(i*33.3334)+'%)';
  tabs.forEach(function(t,j){t.classList.toggle('on',j===i);t.classList.toggle('done',j<i);t.querySelector('b').style.width=j<i?'100%':'0';});
  setTimeout(function(){
    if(cur!==i)return;
    if(i===0)runWarren(); if(i===1)deckStart(); if(i===2)runPortfolio();
  },fixed?100:500);
}
tabs.forEach(function(t,i){t.addEventListener('click',function(){go(i);});});
function tick(ts){
  var dt=last?ts-last:0; last=ts;
  if(!fixed && visible && !hover && cur>=0){
    elapsed+=dt;
    tabs[cur].querySelector('b').style.width=Math.min(100,elapsed/DUR*100)+'%';
    if(elapsed>=DUR) go((cur+1)%3);
  }
  requestAnimationFrame(tick);
}

/* ---------- tocar una seccion = ir a esa seccion del sitio ---------- */
function goTab(tab){ var a=document.querySelector('.nav-link[data-tab-target="'+tab+'"]'); if(a)a.click(); else location.hash='#'+tab; }
var GOTO={
  warren:function(){ var n=document.querySelector('.nav-link[onclick*="toggleWarren"]'); if(n)n.click(); else if(typeof window.toggleWarren==='function')window.toggleWarren(); },
  informes:function(){ goTab('inversiones'); },
  portfolio:function(){ goTab('portfolio'); }
};
Array.prototype.forEach.call(root.querySelectorAll('[data-go]'),function(n){
  n.addEventListener('click',function(){ var f=GOTO[n.getAttribute('data-go')]; if(f)f(); });
});

var frame=root.getElementById('frame');
root.querySelector('.btn').addEventListener('click',function(){ if(typeof window.openPaymentModal==='function') window.openPaymentModal(); });
frame.addEventListener('mouseenter',function(){hover=true;});
frame.addEventListener('mouseleave',function(){hover=false;});
new IntersectionObserver(function(es){es.forEach(function(e){
  var was=visible;
  // visible = se ve una parte relevante: 40% del cartel, o 40% de la pantalla (en celular el cartel es mas alto que la pantalla)
  visible=e.isIntersecting && (e.intersectionRatio>=.4 || e.intersectionRect.height>=window.innerHeight*.4);
  if(visible&&!was&&cur<0) go(fixed?+q.get('cartel'):0);
  if(fixed&&cur<0&&e.isIntersecting) go(+q.get('cartel'));
});},{threshold:[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]}).observe(frame);
requestAnimationFrame(tick);

})();
