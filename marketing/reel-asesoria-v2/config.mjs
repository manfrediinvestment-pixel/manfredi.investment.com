// Fuente única de tiempos: la usan index.html (imagen), sfx/render (sonido).
// Todo está expresado relativo al arranque de cada escena, así si hay música
// y se corren los cortes al golpe más cercano, todo lo demás se mueve con ellos.

export const W = 1080;
export const H = 1920;
export const FPS = 30;          // salida
export const RENDER_FPS = 60;   // cuadros internos (se mezclan de a 2 → desenfoque de movimiento)
export const DURATION = 25;
export const STILL = 1.2;       // últimos segundos quietos (portada / loop)

// Arranque de cada escena (s). Las que se pueden ajustar al golpe de la música: SNAP.
export const STARTS = { hook: 0, yosi: 2.6, me: 3.8, chart: 7.5, cards: 11.5, nums: 15.0, cta: 18.5, brand: 21.5 };
export const SNAP = ['yosi', 'chart', 'cta', 'brand'];
export const ORDER = ['hook', 'yosi', 'me', 'chart', 'cards', 'nums', 'cta', 'brand'];

export function timeline(cuts = {}) {
  const S = { ...STARTS, ...cuts };
  const C = {
    S,
    hookWords: S.hook + 0.0,      // primera palabra pega en el cuadro 1
    hookStep: 0.17,
    hookSweep: S.hook + 1.45,
    riser: S.yosi - 1.5,
    photoIn: S.me + 0.02,
    nameIn: S.me + 0.7,
    seals: [S.me + 1.35, S.me + 2.0, S.me + 2.65],
    chartIn: S.chart,
    drawStart: S.chart + 0.75,
    drawDur: 2.0,
    chartCount: S.chart + 2.8,
    chartCountDur: 0.95,
    cards: [S.cards + 0.35, S.cards + 0.7, S.cards + 1.05],
    cardCountDur: 0.9,
    plusIn: S.cards + 1.75,
    numsIn: S.nums,
    count1: S.nums + 0.3,
    count2: S.nums + 0.55,
    countDur: 1.35,
    diffIn: S.nums + 2.05,
    ctaIn: S.cta,
    brandIn: S.brand,
    still: DURATION - STILL,
  };

  // Efectos de sonido: [tiempo, archivo, ganancia dB]
  const sfx = [];
  const add = (t, f, g = 0) => sfx.push({ t: +t.toFixed(3), f, g });
  add(0.0, 'impact', -4);
  add(0.0, 'whoosh', -6);
  for (let i = 0; i < 8; i += 2) add(C.hookWords + i * C.hookStep + 0.05, 'whoosh', -16);
  add(C.hookSweep, 'spark', -14);
  add(C.riser, 'riser', -3);
  add(S.yosi, 'impact', 0);
  add(S.me - 0.05, 'whoosh', -4);
  C.seals.forEach(t => { add(t, 'spark', -7); add(t, 'impact', -14); });
  add(S.chart - 0.05, 'whoosh', -5);
  add(C.drawStart, 'spark', -9);
  add(C.drawStart + C.drawDur * 0.5, 'spark', -12);
  add(C.drawStart + C.drawDur - 0.05, 'spark', -8);
  add(C.chartCount, 'ticks', -9);
  add(S.cards - 0.08, 'whoosh', -5);
  C.cards.forEach(t => { add(t, 'spark', -8); add(t, 'impact', -12); add(t + 0.2, 'ticks', -13); });
  add(C.plusIn, 'whoosh', -10);
  add(S.nums - 0.12, 'whoosh', -3);
  add(S.nums, 'impact', -5);
  add(C.count1, 'ticks', -8);
  add(C.count1 + C.countDur, 'spark', -9);
  add(C.diffIn, 'impact', -10);
  add(S.cta, 'impact', -3);
  add(S.cta, 'whoosh', -8);
  add(S.brand - 0.1, 'whoosh', -6);
  add(S.brand + 0.25, 'hit', 0);
  return { C, sfx };
}
