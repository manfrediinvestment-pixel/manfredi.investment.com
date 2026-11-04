/* Respuesta de Warren (modo PROFUNDA, workers/warren/prompt.js) armada con los datos del
   informe Manfredi de GOOGL (informes/googl.html, publicado 2-nov-2026). La usan las escenas
   "respuesta" y "contraste". Secciones de alto fijo: la cámara se mueve a posiciones exactas. */
(function () {
  const S = { head: 0, fv: 210, caja: 540, met: 990, ff: 1580, esc: 2060, src: 2480, end: 2830, total: 2960 };
  const met = [
    ["DCF (caso base)", "210,03", "7,5%"],
    ["Suma de las partes", "316,22", "7,5%"],
    ["Comparables (P/E)", "369,36", "25%"],
    ["Reversión histórica", "280,43", "35%"],
    ["Consenso Wall Street", "401,29", "25%"],
  ];
  const ff = [ // rango bajo/alto de cada método (football field del informe)
    ["DCF", 67.21, 486.12], ["Comparables", 265.11, 504.42], ["Suma de partes", 316.22, 346.01],
    ["Reversión", 272.65, 288.20], ["Consenso", 300.00, 490.00],
  ];
  const esc = [["Bajista", "67,21", 25, "#EF4444"], ["Base", "210,03", 45, "#f2c94c"], ["Alcista", "486,12", 30, "#10B981"]];
  const FFX = (v) => 210 + (v / 520) * 690; // escala del football field: US$ 0-520 en 690 px

  function html() {
    return `
<div class="wd" style="height:${S.total}px">
  <section class="wd-s" id="wd-head" style="top:${S.head}px;height:200px">
    <div class="wd-k">INFORME · EMPRESA</div>
    <h1>Alphabet Inc. <em>(GOOGL)</em></h1>
    <div class="wd-pos"><i></i>POSTURA: NEUTRAL · SESGO CONSTRUCTIVO</div>
  </section>
  <section class="wd-s" id="wd-fv" style="top:${S.fv}px;height:300px">
    <div class="wd-fvrow">
      <div><div class="wd-k">VALOR JUSTO · BLEND</div><div class="wd-big odo" id="wd-fvn" data-layout-ignore></div></div>
      <div class="wd-vs">vs.</div>
      <div><div class="wd-k">PRECIO · CIERRE 30-OCT</div><div class="wd-px odo" id="wd-pxn" data-layout-ignore></div></div>
    </div>
    <div class="wd-up" id="wd-up">+18,0% de diferencia</div>
  </section>
  <section class="wd-s" id="wd-caja" style="top:${S.caja}px;height:420px">
    <h2>La caja del 3T26</h2>
    <div class="wd-bar"><span>Flujo operativo</span><div class="wd-tr"><i class="g" id="wd-b1"></i></div><b>US$ 42,29 B</b></div>
    <div class="wd-bar"><span>Capex</span><div class="wd-tr"><i class="r" id="wd-b2"></i></div><b>US$ 51,36 B</b></div>
    <div class="wd-fcf" id="wd-fcf">Flujo libre: <b>−US$ 9,07 B</b></div>
    <div class="wd-cloud" id="wd-cloud">Google Cloud <b>+103%</b> · US$ 30,71 B</div>
  </section>
  <section class="wd-s" id="wd-met" style="top:${S.met}px;height:560px">
    <h2>Valuación: cinco métodos</h2>
    <table class="wd-t"><thead><tr><th>Método</th><th>US$</th><th>Peso</th></tr></thead><tbody>
      ${met.map((r) => `<tr class="wd-mr"><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join("")}
      <tr class="wd-mr wd-tot"><td>Blend ponderado</td><td>330,28</td><td>100%</td></tr>
    </tbody></table>
  </section>
  <section class="wd-s" id="wd-ff" style="top:${S.ff}px;height:460px">
    <h2>Football field de valuación</h2>
    <svg class="wd-ffsvg" width="940" height="360" viewBox="0 0 940 360">
      ${ff.map((r, i) => `<text x="0" y="${42 + i * 62}" class="wd-ffl">${r[0]}</text>
        <rect class="wd-ffb" data-x="${FFX(r[1]).toFixed(1)}" data-w="${(FFX(r[2]) - FFX(r[1])).toFixed(1)}" x="${FFX(r[1]).toFixed(1)}" y="${18 + i * 62}" width="0" height="32" rx="8"/>`).join("")}
      <line class="wd-ffp" x1="${FFX(279.84)}" x2="${FFX(279.84)}" y1="4" y2="320" />
      <line class="wd-ffv" x1="${FFX(330.28)}" x2="${FFX(330.28)}" y1="4" y2="320" />
      <text class="wd-ffpt" x="${FFX(279.84) - 8}" y="350" text-anchor="end">Precio 280</text>
      <text class="wd-ffvt" x="${FFX(330.28) + 8}" y="350">Blend 330</text>
    </svg>
  </section>
  <section class="wd-s" id="wd-esc" style="top:${S.esc}px;height:400px">
    <h2>Escenarios (DCF)</h2>
    ${esc.map((r) => `<div class="wd-er"><span>${r[0]}</span><b>US$ ${r[1]}</b><div class="wd-tr"><i style="background:${r[3]}" data-p="${r[2]}"></i></div><em>${r[2]}%</em></div>`).join("")}
    <div class="wd-ev" id="wd-ev">Valor esperado ponderado: <b>US$ 257,15</b></div>
  </section>
  <section class="wd-s" id="wd-src" style="top:${S.src}px;height:330px">
    <h2>Fuentes</h2>
    <ul class="wd-ul">
      <li>Precio: cierre del 30-oct-2026, Nasdaq</li>
      <li>Resultados 3T26: 8-K en la SEC, 28-oct-2026</li>
      <li>Valuación: informe Manfredi GOOGL, 2-nov-2026</li>
      <li>Consenso: TipRanks, posterior al reporte</li>
    </ul>
  </section>
  <section class="wd-s" id="wd-end" style="top:${S.end}px;height:110px">
    <p class="wd-disc">Análisis educativo de Manfredi Investment. No constituye asesoramiento financiero regulado.</p>
  </section>
</div>`;
  }
  window.WDOC = { S, html, FFX };
})();
