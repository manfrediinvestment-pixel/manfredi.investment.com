/* Ayudantes compartidos por todas las escenas (deterministas: todo depende del tiempo del timeline). */
(function () {
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const eOut4 = (x) => 1 - Math.pow(1 - x, 4);
  const eInOut3 = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const ACC = { red: "#EF4444", green: "#10B981", gold: "#f2c94c" };
  const G_SVG = '<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>';

  /* Placa del chip de Nvidia: ticker en el verde de la marca (sin reproducir el logo). */
  const N_SVG = '<svg viewBox="0 0 160 70"><text x="80" y="50" text-anchor="middle" font-family="Plex Sans" font-weight="700" font-size="44" letter-spacing="1" fill="#5A8F00">NVDA</text></svg>';

  /* Odómetro: parts = ["−", 10, 1, ",", 0.1, 0.01, "%"]. Números = valor de la columna;
     "." se oculta debajo de 1.000; "~M" = unidad chica. Devuelve set(v). */
  function odo(el, parts) {
    const cols = [], seps = [];
    parts.forEach((p) => {
      if (typeof p === "string") {
        const s = document.createElement("span");
        s.className = p.startsWith("~") ? "odo-fix unit" : "odo-fix";
        s.textContent = p.replace("~", "");
        el.appendChild(s);
        if (p === ".") seps.push(s);
        return;
      }
      const c = document.createElement("span"); c.className = "odo-col";
      const st = document.createElement("span"); st.className = "odo-strip";
      for (let k = 0; k <= 10; k++) { const d = document.createElement("span"); d.textContent = k % 10; st.appendChild(d); }
      c.appendChild(st); el.appendChild(c); cols.push({ c, st, place: p });
    });
    const lowest = Math.min(...cols.map((c) => c.place));
    const minInt = Math.min(...cols.filter((c) => c.place >= 1).map((c) => c.place));
    return function set(v) {
      v = Math.abs(Math.round(v * 1e6) / 1e6);
      for (const { c, st, place } of cols) {
        const q = v / place, base = Math.floor(q + 1e-9);
        const pos = place === lowest ? q % 10 : (base % 10) + Math.max(0, (q - base) * 10 - 9);
        st.style.transform = `translateY(${-pos}em)`;
        c.style.width = (place > minInt ? clamp((v - place * 0.94) / (place * 0.06), 0, 1) : 1) * 0.6 + "em";
      }
      for (const s of seps) { const k = clamp((v - 940) / 60, 0, 1); s.style.width = k * 0.6 + "em"; s.style.opacity = k; s.style.overflow = "hidden"; }
    };
  }

  /* Subtítulo karaoke: cada palabra pasa de champagne apagado a blanco (o a su color de acento). */
  function karaoke(tl, R, sel, tIn, tOut, step, instant) {
    const box = R.querySelector(sel);
    const words = box.querySelectorAll(".w");
    tl.fromTo(box, { opacity: instant ? 1 : 0, filter: instant ? "blur(0px)" : "blur(10px)" },
      { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power3.out" }, tIn);
    words.forEach((w, i) => {
      const col = ACC[w.dataset.acc] || "#f6f8fc";
      tl.fromTo(w, { color: "#B8943F", opacity: 0.9 }, { color: col, opacity: 1, duration: 0.09, ease: "none" }, tIn + 0.04 + i * step);
    });
    if (tOut != null) tl.to(box, { opacity: 0, filter: "blur(8px)", duration: 0.12, ease: "power3.in" }, tOut);
  }

  /* Varias frases seguidas: lines = [[sel, tIn, tOut]], el paso por palabra se reparte en la ventana. */
  function captions(tl, R, lines) {
    lines.forEach(([sel, tIn, tEnd], i) => {
      const n = R.querySelector(sel).querySelectorAll(".w").length;
      const span = (tEnd - tIn) * 0.72;
      const last = i === lines.length - 1;
      karaoke(tl, R, sel, tIn, last ? null : tEnd - 0.06, Math.max(0.08, span / Math.max(1, n)), i === 0 && tIn <= 0);
    });
  }

  /* Reloj determinista: render(t) en cada cuadro. */
  function clock(tl, dur, render) {
    tl.to({}, { duration: dur, ease: "none", onUpdate() { render(this.time()); } }, 0);
    render(0);
  }

  /* Temblor de cámara (6 golpes de ~2 cuadros). */
  function shake(tl, sel, at, amp) {
    const a = amp || 14;
    [[1, -0.7], [-0.85, 0.6], [0.6, -0.45], [-0.35, 0.3], [0.15, -0.1], [0, 0]].forEach(([x, y], i) =>
      tl.to(sel, { x: x * a, y: y * a, duration: 0.032, ease: "none" }, at + i * 0.032));
  }

  function flash(tl, sel, at) {
    tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05, ease: "none" }, at);
    tl.to(sel, { opacity: 0, duration: 0.6, ease: "power2.out" }, at + 0.07);
  }

  window.MF = { clamp, eOut4, eInOut3, odo, karaoke, captions, clock, shake, flash, G_SVG, N_SVG };
})();
