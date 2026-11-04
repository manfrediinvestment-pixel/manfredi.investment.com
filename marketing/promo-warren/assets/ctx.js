/* Los 4 casilleros (escenas "contexto" y "revelacion"). Cada uno son dos mitades con borde dentado
   (.half-l / .half-r de brand.css) para que se pueda agrietar, romper y volver a armar. */
(function () {
  const ic = (p) => `<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#f2c94c" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
  const ITEMS = [
    ["CONTEXTO", ic('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>'), "No sabe nada de vos ni de tu cartera.", "Lee tu cartera y tu perfil"],
    ["FUENTES", ic('<path d="M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h10M9 8h5"/>'), "No leyó ningún informe.", "Lee nuestros informes"],
    ["PROMPT", ic('<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>'), "Tenés que saber qué preguntarle.", "Ya sabe qué buscar"],
    ["PRECIO", ic('<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.4" fill="#f2c94c"/>'), "USD 20 por mes.", "Incluido en la membresía"],
  ];
  const X = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  const OK = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  function card(i, id) {
    const [k, svg, bad, good] = ITEMS[i];
    const inner = `${svg}<div class="kk">${k}</div><p class="bad">${bad}</p><p class="good">${good}</p><div class="mk x">${X}</div><div class="mk ok">${OK}</div>`;
    return `<div class="cw" id="${id}"><div class="ctx glass half-l">${inner}</div><div class="ctx glass half-r">${inner}</div>` +
      `<svg class="crk" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M53 0 L47 21 L56 39 L45 57 L54 76 L47 100" /><path d="M56 39 L70 46 M45 57 L30 66 M47 21 L36 14" /></svg></div>`;
  }
  window.CTX = { ITEMS, card };
})();
