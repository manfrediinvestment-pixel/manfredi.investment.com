// Banda sonora del reel, sintetizada por código (sin samples ni licencias) y atada a la
// línea de tiempo: lee window.CUES de video.html, así cada sonido cae en el cuadro exacto
// de su movimiento. Mismo resultado en cada corrida (ruido con semilla).
//   node audio.mjs → output/audio.wav (48 kHz, estéreo)
//
// House melódico a 120 BPM (pulso 0,5 s; compás de 2 s que arranca en t = 1 s), Si menor / Re mayor:
//  - Gancho: intro filtrada + subida (riser) mientras se escribe la pregunta.
//  - 1.ª transición = el "drop": IMPACTO y entra el bombo.
//  - Bombo en cada pulso, palmas en 2 y 4, hi-hat en contratiempo, bajo saltando en
//    corcheas a contratiempo; colchón, bajo y arpegio "respiran" con el bombo (sidechain).
//  - Transiciones del medio: barrido tonal afinado al acorde que llega.
//  - Cómo trabajamos: la parte más cargada (arpegio en semicorcheas, hi-hat cerrado).
//  - Mi cartera: se va el bombo y la curva REAL suena; los números llegan en el compás y
//    el bombo vuelve justo ahí.
//  - Última transición: brillo ascendente de campanas. La web resuelve a Re mayor.
import { writeFile, readFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { HERE, openVideo } from './lib.mjs';

const SR = 48000;
const v = await openVideo();
const C = await v.page.evaluate(() => window.CUES);
await v.close();
const DATA = JSON.parse(await readFile(join(HERE, 'data.json'), 'utf8'));

const N = Math.ceil((C.end + .05) * SR);
const L = new Float32Array(N), R = new Float32Array(N), SEND = new Float32Array(N);
// bus que "respira" con el bombo (sidechain)
const PL = new Float32Array(N), PR = new Float32Array(N);
const mtof = m => 440 * 2 ** ((m - 69) / 12);
let seed = 20260522;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const TAU = Math.PI * 2;

// escribe una voz mono con paneo (fijo o en función del tiempo) y envío a reverb
function voice(t0, dur, gain, pan, send, fn, pumped = false) {
  const i0 = Math.max(0, Math.round(t0 * SR)), n = Math.min(N - i0, Math.round(dur * SR));
  const BL = pumped ? PL : L, BR = pumped ? PR : R;
  for (let k = 0; k < n; k++) {
    const t = k / SR, x = fn(t, k), p = typeof pan === 'function' ? pan(t) : pan;
    BL[i0 + k] += x * gain * Math.cos((p + 1) * Math.PI / 4);
    BR[i0 + k] += x * gain * Math.sin((p + 1) * Math.PI / 4);
    SEND[i0 + k] += x * gain * send;
  }
}
// filtro de estado variable (Chamberlin)
function svf() { let lo = 0, bp = 0; return (x, fc, q) => { const f = 2 * Math.sin(Math.PI * Math.min(fc, SR / 6) / SR); const hi = x - lo - q * bp; bp += f * hi; lo += f * bp; return { lo, bp, hi }; }; }
const saw = (p, n, bright = 1) => { let s = 0; for (let h = 1; h <= n; h++) s += Math.sin(h * p) / h * Math.exp(-(h - 1) * (1 - bright) * .6); return s; };

// ── batería ──────────────────────────────────────────────
function kick(t0, gain = .55) {
  voice(t0, .5, gain, 0, .02, t => {
    const p = TAU * (48 * t + 110 * .04 * (1 - Math.exp(-t / .04)));
    const body = Math.sin(p) + .35 * Math.sin(2 * p) * Math.exp(-t / .06);   // armónico: se oye en el celular
    return Math.min(1, t / .001) * Math.exp(-t / .22) * body + (t < .004 ? (rnd() * 2 - 1) * .4 * (1 - t / .004) : 0);
  });
}
function clap(t0, gain = .13) {
  const f = svf();
  voice(t0, .3, gain, .05, .35, t => {
    const x = rnd() * 2 - 1;
    const env = [0, .009, .018].reduce((a, d) => a + (t >= d ? Math.exp(-(t - d) / .006) : 0), 0) * .6 + (t > .018 ? Math.exp(-(t - .018) / .09) : 0);
    return env * f(x, 1300, .7).bp * 2.2;
  });
}
function hat(t0, open = false, gain = open ? .05 : .028) {
  const f = svf();
  voice(t0, open ? .18 : .06, gain, open ? .25 : -.2, .08, t => Math.exp(-t / (open ? .055 : .016)) * f(rnd() * 2 - 1, 8500, .6).hi);
}

// ── instrumentos ─────────────────────────────────────────
function pad(notes, t0, t1, gain = .022, bright = .5) {
  const att = .25, rel = .5, dur = t1 - t0 + rel;
  notes.forEach((m, j) => {
    const f = mtof(m), pan = (j % 2 ? 1 : -1) * (.2 + .15 * j / notes.length);
    [-7, 0, 7].forEach(c => {
      const fc = f * 2 ** (c / 1200), ph = rnd() * TAU;
      voice(t0, dur, gain / 3, pan, .45, t => {
        const env = Math.min(1, t / att) * (t > t1 - t0 ? Math.max(0, 1 - (t - (t1 - t0)) / rel) : 1);
        return env * saw(TAU * fc * t + ph, 6, bright);
      }, true);
    });
  });
}
function bass(m, t0, len = .22, gain = .16) {
  const f = mtof(m);
  voice(t0, len + .05, gain, 0, 0, t => {
    const env = Math.min(1, t / .004) * (t < len ? 1 : Math.max(0, 1 - (t - len) / .05));
    const p = TAU * f * t, k = Math.exp(-t / .07);                        // filtro que se cierra: "pluck" de bajo
    return env * (Math.sin(p) + .5 * Math.sin(2 * p) * (.3 + .7 * k) + .25 * Math.sin(3 * p) * k + .12 * Math.sin(4 * p) * k);
  }, true);
}
function arp(m, t0, gain = .045, pan = 0) {
  const f = mtof(m);
  voice(t0, .35, gain, pan, .4, t => Math.min(1, t / .003) * Math.exp(-t / .11) * saw(TAU * f * t, 7, .55), true);
}
function pluck(m, t0, vel = 1, pan = 0, gain = .07) {
  const f = mtof(m);
  voice(t0, 1.2, gain * vel, pan, .4, t => {
    const a = Math.min(1, t / .003), p = TAU * f * t;
    return a * (Math.sin(p) * Math.exp(-t / .6) + .45 * Math.sin(2 * p) * Math.exp(-t / .25) + .18 * Math.sin(3 * p) * Math.exp(-t / .12));
  });
}
function bell(m, t0, gain = .08, pan = 0, dur = 2.5) {
  const f = mtof(m);
  voice(t0, dur, gain, pan, .7, t => {
    const a = Math.min(1, t / .002), I = 1.8 * Math.exp(-t / .3);
    return a * Math.exp(-t / 1.1) * Math.sin(TAU * f * t + I * Math.sin(TAU * 2 * f * t)) + .25 * a * Math.exp(-t / .2) * Math.sin(TAU * 4.2 * f * t);
  });
}
function tick(t0, gain = .07) {
  const f = svf(), pitch = 2600 * (0.92 + .16 * rnd()), pan = -.25 + .5 * rnd();
  voice(t0, .05, gain, pan, .12, t => Math.exp(-t / .006) * (f(rnd() * 2 - 1, 5200, .5).hi * .8 + .5 * Math.sin(TAU * pitch * t)));
}
function click(t0, gain = .1) {
  voice(t0, .25, gain, 0, .2, t => Math.exp(-t / .03) * Math.sin(TAU * 1250 * t) * .6 + Math.exp(-t / .07) * Math.sin(TAU * 190 * t));
}
function glide(t0, dur, m0, m1, gain = .045) {
  let ph = 0;
  voice(t0, dur + .3, gain, .1, .5, t => {
    const u = Math.min(1, t / dur), e = 1 - (1 - u) ** 3;
    ph += TAU * mtof(m0 + (m1 - m0) * e) / SR;
    return Math.min(1, t / .04) * (t > dur ? Math.exp(-(t - dur) / .1) : 1) * (Math.sin(ph) + .2 * Math.sin(2 * ph));
  });
}

// ── transiciones (tres sonidos distintos) ────────────────
// riser del gancho: ruido que se abre + tono que sube, corta seco en el drop
function riser(t0, t1, gain = .16) {
  const f = svf(); let ph = 0; const d = t1 - t0;
  voice(t0, d, gain, t => -.5 + t / d, .5, t => {
    const u = t / d;
    ph += TAU * (180 * 2 ** (u * 2.2)) / SR;
    return u ** 2.4 * (f(rnd() * 2 - 1, 400 + 7000 * u * u, .5).bp * 1.4 + .25 * Math.sin(ph) * u);
  });
}
// 1.ª: IMPACTO (boom grave + platillo filtrado con cola larga)
function impact(t) {
  voice(t, 1.6, .28, 0, .1, u => {
    const p = TAU * (36 * u + 30 * .08 * (1 - Math.exp(-u / .08)));
    return Math.min(1, u / .002) * Math.exp(-u / .5) * (Math.sin(p) + .4 * Math.sin(2 * p) * Math.exp(-u / .2));
  });
  const f = svf();
  voice(t, 2.2, .09, 0, .8, u => Math.exp(-u / .55) * f(rnd() * 2 - 1, 6500, .4).hi);
}
// del medio: barrido de aire que pasa por resonancias afinadas al acorde que llega
function tonalSwoosh(tc, notes, gain = .14) {
  const len = .8, peak = .38, fs = notes.map(svf), fa = svf();
  voice(tc - peak, len, gain, t => -.7 + 1.4 * t / len, .55, t => {
    const x = rnd() * 2 - 1;
    const env = t < peak ? (t / peak) ** 2.5 : Math.exp(-(t - peak) / .14);
    let y = 0;
    notes.forEach((m, i) => { y += fs[i](x, mtof(m), .035).bp; });
    return env * (y * .55 + fa(x, 900 + 5000 * Math.min(1, t / peak), .7).bp * .9);
  });
}
// última: brillo ascendente (campanas en fusas por el acorde) que llega al pulso
function shimmer(tc, notes) {
  const seq = [];
  for (let o = 0; seq.length < 12; o += 12) notes.forEach(m => seq.length < 12 && seq.push(m + o));
  seq.forEach((m, i) => bell(m, tc - (12 - i) * .0625, .018 + .004 * i, .6 - .1 * i, 1.6));
  const f = svf();
  voice(tc - .75, 1.1, .05, 0, .7, t => (t < .75 ? (t / .75) ** 2 : Math.exp(-(t - .75) / .12)) * f(rnd() * 2 - 1, 9000, .5).hi);
}
// paso a paso: barrido cortito y agudo
function stepSwish(tc) {
  const f = svf();
  voice(tc - .18, .35, .06, t => .5 - 2.6 * t, .3, t => (t < .18 ? (t / .18) ** 2 : Math.exp(-(t - .18) / .06)) * f(rnd() * 2 - 1, 2500 + 4000 * t, .6).bp);
}

// ── estructura ───────────────────────────────────────────
const [, A2, A3, A4, A5, A6] = C.arrive, B = C.beat, END = C.end;
const LAND = C.chart[0] + C.chart[1];
const CH = {
  Bm9: [47, 54, 57, 61, 62], Gmaj9: [43, 55, 59, 62, 66], Dadd9: [50, 57, 62, 64, 66], Asus: [45, 57, 62, 64, 69],
  Bm: [47, 54, 59, 62, 66], G: [43, 55, 59, 62, 67], D: [50, 57, 62, 66, 69], A: [45, 57, 61, 64, 69],
  Gadd9: [43, 55, 57, 59, 62], A7sus: [45, 57, 62, 64, 67], Dmaj9: [38, 50, 57, 61, 64, 66],
};
// acordes: cambian en cada llegada de escena y por compás en "Cómo trabajamos"
const PLAN = [
  [0, A2, 'Bm9'], [A2, A3, 'Gmaj9'], [A3, A4, 'Dadd9'],
  [A4, A4 + 2, 'Bm'], [A4 + 2, A4 + 4, 'G'], [A4 + 4, A4 + 6, 'D'], [A4 + 6, A5, 'A'],
  [A5, LAND, 'Bm9'], [LAND, A6, 'Gadd9'], [A6, C.url, 'A7sus'], [C.url, END, 'Dmaj9'],
];
PLAN.forEach(([a, b, c]) => pad(CH[c], a, b, a < A2 ? .05 : .022, a < A2 ? .4 : .5));
const chordAt = t => CH[PLAN.find(([a, b]) => t >= a - 1e-6 && t < b - 1e-6)?.[2] || 'Dmaj9'];

// batería y bajo, desde el drop
const KICKS = [];
const breakdown = t => t >= A5 - 1e-6 && t < LAND - 1e-6;
for (let t = A2; t < END - .25; t += B) {
  if (breakdown(t)) continue;
  kick(t); KICKS.push(t);
  hat(t + B / 2, true);
  if (t >= A3 && Math.round((t - 1) / B) % 2 === 1) clap(t);          // 2 y 4 (compás arranca en t = 1)
  const root = chordAt(t)[0] % 12 + 36;                                // Si1…La1
  bass(root, t + B / 2); bass(root + 12, t + B * .75, .1, .08);
}
// en el gráfico: bajo sostenido (sin bombo) para que la curva quede al frente
bass(CH.Bm9[0] % 12 + 36, A5, LAND - A5 - .05, .12);
// hi-hat cerrado en semicorcheas: "Cómo trabajamos" y el final
for (let t = A4; t < END - .25; t += B / 4) if ((t < A5 || t >= A6) && Math.round(t / (B / 4)) % 2) hat(t);
// arpegio: corcheas en quién/credenciales, semicorcheas en "Cómo trabajamos" y el cierre
const PAT = [0, 2, 1, 3, 2, 4, 1, 3];
for (let k = 0, t = A2; t < END - .3; k++, t = A2 + k * B / 4) {
  if (breakdown(t) || (t >= LAND && t < A6)) continue;
  const dense = (t >= A4 && t < A5) || t >= C.url;
  if (!dense && k % 2) continue;
  const ch = chordAt(t).slice(1), m = ch[PAT[k % 8] % ch.length] + 12;
  arp(m, t, k % 4 === 0 ? .05 : .035, (k % 4 - 1.5) * .2);
}

// sidechain: el bus de colchón/bajo/arpegio baja con cada bombo y vuelve
{
  let ki = 0;
  for (let n = 0; n < N; n++) {
    const t = n / SR;
    while (ki + 1 < KICKS.length && KICKS[ki + 1] <= t) ki++;
    const dt = KICKS.length && KICKS[ki] <= t ? t - KICKS[ki] : 9;
    const g = 1 - .6 * Math.exp(-dt / .09);
    L[n] += PL[n] * g; R[n] += PR[n] * g;
  }
}

// transiciones
riser(.4, A2);
impact(A2);
[A3, A4, A5].forEach(t => tonalSwoosh(t, chordAt(t + .01).slice(1).map(m => m + 24)));
shimmer(A6, CH.A7sus.slice(1).map(m => m + 12));
C.steps.slice(1).forEach(stepSwish);

// gancho: ping cuando la curva llega a la punta + tecleo de la pregunta
bell(78, C.dot, .06, .35);           // Fa#5
bell(85, C.dot + .02, .02, .35);     // Do#6, brillo
C.ticks.forEach(t => tick(t));
// quién: el cartel entra con un clic suave
click(C.badge, .06);
// credenciales: una campana por sello, subiendo por el acorde de Re
[74, 78, 81, 86].forEach((m, i) => bell(m, C.seals[i], .06, -.3 + .2 * i));
// cómo trabajamos: elegir horario, medidor, dona
click(C.slot, .09);
glide(C.gauge[0], C.gauge[1], 69, 76);
C.donut.forEach((t, i) => pluck([69, 73, 76, 78, 81][i] + 12, t, .7, -.3 + .15 * i, .04));

// mi cartera: la curva real suena. Se recorre igual que el video (power2.inOut) y en cada
// semicorchea suena la nota de la escala que corresponde al valor de ese día.
const PENTA = [0, 2, 4, 7, 9];
const toScale = (v, lo, hi, base, span) => { const s = Math.round((v - lo) / ((hi - lo) || 1) * span); return base + 12 * Math.floor(s / 5) + PENTA[((s % 5) + 5) % 5]; };
const rows = DATA.rows, mins = rows.map(r => r[1]), spxs = rows.map(r => r[2]);
const lo = Math.min(...mins, ...spxs), hi = Math.max(...mins, ...spxs);
const ease = u => u < .5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
const STEPS = Math.round(C.chart[1] / (B / 4));
let lastM = -1, lastS = -1;
for (let k = 0; k < STEPS; k++) {
  const t = C.chart[0] + k * B / 4, i = Math.min(rows.length - 1, Math.round(ease(k / STEPS) * (rows.length - 1)));
  const mm = toScale(mins[i], lo, hi, 74, 9), ms = toScale(spxs[i], lo, hi, 62, 9);
  if (mm !== lastM) pluck(mm, t, .9, .25, .075); lastM = mm;
  if (k % 2 === 0 && ms !== lastS) pluck(ms, t + .01, .6, -.3, .04); lastS = ms;
}
// los números llegan: vuelve el bombo + acorde de campanas
[[74, .05], [78, .04], [81, .045], [86, .03]].forEach(([m, g], i) => bell(m, LAND + i * .012, g, -.2 + .13 * i));
impact(LAND);

// cierre: la web resuelve a Re mayor
click(C.url, .08);
[[74, .06], [78, .045], [81, .05], [86, .04], [90, .025]].forEach(([m, g], i) => bell(m, C.url + i * .02, g, -.3 + .15 * i, 3));

// ── reverb (Freeverb simplificado) ───────────────────────
function reverb() {
  const k = SR / 44100, COMBS = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617], APS = [556, 441, 341, 225];
  const chan = spread => {
    const out = new Float32Array(N);
    const combs = COMBS.map(d => ({ b: new Float32Array(Math.round((d + spread) * k)), i: 0, f: 0 }));
    const aps = APS.map(d => ({ b: new Float32Array(Math.round((d + spread) * k)), i: 0 }));
    for (let n = 0; n < N; n++) {
      const x = SEND[n] * .015;
      let y = 0;
      for (const c of combs) { const o = c.b[c.i]; c.f = o * .7 + c.f * .3; c.b[c.i] = x + c.f * .84; c.i = (c.i + 1) % c.b.length; y += o; }
      for (const a of aps) { const o = a.b[a.i]; const z = -y + o; a.b[a.i] = y + o * .5; a.i = (a.i + 1) % a.b.length; y = z; }
      out[n] = y;
    }
    return out;
  };
  return [chan(0), chan(23)];
}
const [RL, RR] = reverb();
let peak = 0;
for (let n = 0; n < N; n++) {
  // saturación suave en el master: pega la mezcla como en un tema electrónico
  L[n] = Math.tanh((L[n] + RL[n]) * 1.6) / 1.6; R[n] = Math.tanh((R[n] + RR[n]) * 1.6) / 1.6;
  peak = Math.max(peak, Math.abs(L[n]), Math.abs(R[n]));
}
// normaliza (≈ -14 LUFS, el nivel de Instagram) y funde los últimos 0,6 s
const g = .72 / peak, fadeFrom = (END - .6) * SR;
const pcm = Buffer.alloc(N * 4);
for (let n = 0; n < N; n++) {
  const f = n > fadeFrom ? Math.max(0, 1 - (n - fadeFrom) / (.6 * SR)) : 1;
  pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[n] * g * f)) * 32767), n * 4);
  pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[n] * g * f)) * 32767), n * 4 + 2);
}
const hdr = Buffer.alloc(44);
hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + pcm.length, 4); hdr.write('WAVE', 8); hdr.write('fmt ', 12);
hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(2, 22); hdr.writeUInt32LE(SR, 24);
hdr.writeUInt32LE(SR * 4, 28); hdr.writeUInt16LE(4, 32); hdr.writeUInt16LE(16, 34); hdr.write('data', 36); hdr.writeUInt32LE(pcm.length, 40);
await mkdir(join(HERE, 'output'), { recursive: true });
const out = join(HERE, 'output', 'audio.wav');
await writeFile(out, Buffer.concat([hdr, pcm]));
console.log(`${out} · ${(N / SR).toFixed(2)} s · ${KICKS.length} bombos · llegadas ${C.arrive.join(', ')}`);
