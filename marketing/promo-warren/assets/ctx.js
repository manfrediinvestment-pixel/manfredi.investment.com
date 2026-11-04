/* Los 4 casilleros de contexto (escenas "contexto" y "revelacion"). */
(function () {
  const ic = (p) => `<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#f2c94c" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
  const ITEMS = [
    ["Tu cartera", ic('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>')],
    ["Tu perfil de riesgo", ic('<path d="M4 17a8 8 0 1 1 16 0"/><path d="M12 17l4-5"/><circle cx="12" cy="17" r="1.4" fill="#f2c94c"/>')],
    ["Informes propios", ic('<path d="M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h10M9 8h5"/>')],
    ["Precio de hoy", ic('<path d="M3 17l5-5 4 3 8-8"/><path d="M15 7h5v5"/>')],
  ];
  const X = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  const OK = '<svg viewBox="0 0 24 24" fill="none" stroke="#0a1322" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  function card(i, id, both) {
    const [lab, svg] = ITEMS[i];
    const marks = `<div class="mk x">${X}</div>` + (both ? `<div class="mk ok">${OK}</div>` : "");
    return `<div class="ctx glass" id="${id}">${svg}<b>${lab}</b>${marks}</div>`;
  }
  window.CTX = { ITEMS, card };
})();
