// Banda sonora del reel, sintetizada por código (sin samples ni licencias) y
// atada a la línea de tiempo: lee window.CUES de video.html, así cada sonido cae
// en el cuadro exacto de su movimiento. Mismo resultado en cada corrida (ruido con semilla).
//   node audio.mjs → output/audio.wav (48 kHz, estéreo)
//
// Idea musical (80 BPM, Re mayor):
//  - Cada escena llega en un pulso y CAMBIA EL ACORDE: la armonía marca la estructura.
//  - Gancho: colchón que crece + tecleo de la itálica + "ping" cuando la curva llega a la punta.
//  - Quién/credenciales: aparece el pulso (arpegio suave); cada sello es una campana que sube.
//  - Cómo trabajamos: un acorde por paso, en subida (Mi m → Fa# m → Sol → La sus), con
//    hi-hat suave en contratiempo: es la escena de "proceso", la que empuja.
//  - Mi cartera: el pulso se calla y la curva REAL suena (sonificación cuantizada a la
//    escala); la del S&P 500, una octava abajo y más baja. Los números llegan en el pulso.
//  - Cierre: La sus queda en suspenso y resuelve a Re mayor justo cuando aparece la web.
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
const mtof = m => 440 * 2 ** ((m - 69) / 12);
let seed = 20260522;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

// escribe una voz mono con paneo y envío a reverb
function voice(t0, dur, gain, pan, send, fn) {
  const i0 = Math.max(0, Math.round(t0 * SR)), n = Math.min(N - i0, Math.round(dur * SR));
  const gl = gain * Math.cos((pan + 1) * Math.PI / 4), gr = gain * Math.sin((pan + 1) * Math.PI / 4);
  for (let k = 0; k < n; k++) {
    const x = fn(k / SR, k);
    L[i0 + k] += x * gl; R[i0 + k] += x * gr; SEND[i0 + k] += x * gain * send;
  }
}
const TAU = Math.PI * 2;

// ── instrumentos ─────────────────────────────────────────
// colchón: parciales suaves, 3 voces desafinadas apenas (coro), ataque y relajación lentos
function pad(notes, t0, t1, gain = .028) {
  const att = .9, rel = 1.3, dur = t1 - t0 + rel;
  notes.forEach((m, j) => {
    const f = mtof(m), pan = (j % 2 ? 1 : -1) * (.15 + .1 * j / notes.length);
    [-5, 0, 5].forEach(c => {
      const fc = f * 2 ** (c / 1200);
      voice(t0, dur, gain / 3, pan, .55, t => {
        const env = Math.min(1, t / att) * (t > t1 - t0 ? Math.max(0, 1 - (t - (t1 - t0)) / rel) : 1);
        const p = TAU * fc * t;
        return env * (Math.sin(p) + .3 * Math.sin(2 * p) + .1 * Math.sin(3 * p) + .04 * Math.sin(4 * p));
      });
    });
  });
}
// pulso tipo piano apagado
function pluck(m, t0, vel = 1, pan = 0, gain = .07) {
  const f = mtof(m);
  voice(t0, 1.6, gain * vel, pan, .35, t => {
    const a = Math.min(1, t / .004), p = TAU * f * t;
    return a * (Math.sin(p) * Math.exp(-t / .9) + .45 * Math.sin(2 * p) * Math.exp(-t / .35) + .18 * Math.sin(3 * p) * Math.exp(-t / .18));
  });
}
// campana FM (sellos, ping, resolución)
function bell(m, t0, gain = .08, pan = 0, dur = 3) {
  const f = mtof(m);
  voice(t0, dur, gain, pan, .7, t => {
    const a = Math.min(1, t / .002), I = 1.8 * Math.exp(-t / .3);
    return a * Math.exp(-t / 1.4) * Math.sin(TAU * f * t + I * Math.sin(TAU * 2 * f * t)) + .25 * a * Math.exp(-t / .25) * Math.sin(TAU * 4.2 * f * t);
  });
}
// golpe grave suave en cada llegada de escena
// (con 2.º y 3.er armónico para que se perciba también en el parlante del celular)
function sub(t0, gain = .16) {
  voice(t0, .9, gain, 0, .05, t => {
    const a = Math.min(1, t / .002), p = TAU * (42 * t + 40 * .06 * (1 - Math.exp(-t / .06)));
    return a * Math.exp(-t / .38) * (Math.sin(p) + .45 * Math.sin(2 * p) * Math.exp(-t / .15) + .2 * Math.sin(3 * p) * Math.exp(-t / .08));
  });
}
// filtro de estado variable (Chamberlin) para ruidos
function svf() { let lo = 0, bp = 0; return (x, fc, q) => { const f = 2 * Math.sin(Math.PI * Math.min(fc, SR / 6) / SR); const hi = x - lo - q * bp; bp += f * hi; lo += f * bp; return { lo, bp, hi }; }; }
// empuje entre escenas: aire que sube hasta el pulso y se va
function whoosh(tc, gain = .2, len = 1.05, peak = .62) {
  const f = svf(), t0 = tc - peak;
  voice(t0, len, gain, 0, .4, t => {
    const u = t / len, x = rnd() * 2 - 1;
    const env = t < peak ? (t / peak) ** 2.2 : Math.exp(-(t - peak) / .16);
    const fc = t < peak ? 350 + 2300 * (t / peak) ** 2 : 2650 * Math.exp(-(t - peak) / .25) + 500;
    return env * f(x, fc, .9).bp * 1.6 * (.6 + .4 * Math.sin(TAU * 3 * u));
  });
}
// tecleo: clic corto y agudo, con algo de variación determinística
function tick(t0, gain = .05) {
  const f = svf(), pitch = 2600 * (0.92 + .16 * rnd()), pan = -.25 + .5 * rnd();
  voice(t0, .05, gain, pan, .12, t => {
    const x = rnd() * 2 - 1;
    return Math.exp(-t / .006) * (f(x, 5200, .5).hi * .8 + .5 * Math.sin(TAU * pitch * t));
  });
}
// clic de botón / selección
function click(t0, gain = .12) {
  voice(t0, .25, gain, 0, .2, t => Math.exp(-t / .03) * Math.sin(TAU * 1250 * t) * .6 + Math.exp(-t / .07) * Math.sin(TAU * 190 * t));
}
// hi-hat suave
function hat(t0, gain = .025) {
  const f = svf();
  voice(t0, .08, gain, .3, .1, t => Math.exp(-t / .02) * f(rnd() * 2 - 1, 9000, .7).hi);
}
// deslizamiento del medidor de perfil (sigue la misma curva power3.out del video)
function glide(t0, dur, m0, m1, gain = .05) {
  let ph = 0;
  voice(t0, dur + .4, gain, .1, .5, t => {
    const u = Math.min(1, t / dur), e = 1 - (1 - u) ** 3;
    ph += TAU * mtof(m0 + (m1 - m0) * e) / SR;
    const env = Math.min(1, t / .05) * (t > dur ? Math.exp(-(t - dur) / .12) : 1);
    return env * (Math.sin(ph) + .2 * Math.sin(2 * ph));
  });
}
// subida de aire suave (el gancho)
function swell(t0, dur, gain = .06) {
  const f = svf();
  voice(t0, dur + .3, gain, 0, .6, t => {
    const u = Math.min(1, t / dur), env = u ** 2 * (t > dur ? Math.exp(-(t - dur) / .08) : 1);
    return env * f(rnd() * 2 - 1, 600 + 5000 * u * u, .6).bp;
  });
}

// ── armonía (MIDI) ───────────────────────────────────────
const CH = {
  Dmaj9: [50, 57, 61, 64, 66], Bm11: [47, 54, 57, 62, 64], Gmaj9: [43, 55, 59, 62, 66],
  Em9: [40, 52, 55, 59, 62, 66], Fsm7: [42, 54, 57, 61, 64], A7sus: [45, 57, 62, 64, 67],
  Bm9: [47, 54, 57, 61, 62], Gadd9: [43, 55, 57, 59, 62], Dfin: [38, 50, 57, 61, 64, 66, 69],
};
const [, A2, A3, A4, A5, A6] = C.arrive, B = C.beat, END = C.end;
const S = C.steps, LAND = C.chart[0] + C.chart[1];
const PLAN = [
  [0, A2, 'Dmaj9'], [A2, A3, 'Bm11'], [A3, A4, 'Gmaj9'],
  [A4, S[1], 'Em9'], [S[1], S[2], 'Fsm7'], [S[2], S[3], 'Gmaj9'], [S[3], A5, 'A7sus'],
  [A5, LAND, 'Bm9'], [LAND, A6, 'Gadd9'], [A6, C.url, 'A7sus'], [C.url, END, 'Dfin'],
];
PLAN.forEach(([a, b, c]) => pad(CH[c], a, b, .028));
const chordAt = t => CH[PLAN.find(([a, b]) => t >= a && t < b)?.[2] || 'Dfin'];

// pulso: arpegio en la octava de arriba. Densidad según la escena
const PAT = [0, 2, 1, 3, 2, 4, 1, 3];
for (let k = 0, t = A2; t < C.url - .01; k++, t = A2 + k * B / 2) {
  const inChart = t >= A5 - .01 && t < LAND + B;           // la curva real toma la melodía
  const quarter = (t < A3) || (t >= A5) || (t >= A6);       // escenas más calmas: negras
  if (inChart || (quarter && k % 2)) continue;
  const ch = chordAt(t).slice(1), m = ch[PAT[k % 8] % ch.length] + 12;
  pluck(m, t, k % 2 ? .55 : .9, (k % 4 - 1.5) * .15, t >= A4 && t < A5 ? .075 : .06);
}
// hi-hat a contratiempo en "Cómo trabajamos"
for (let t = A4 + B / 2; t < A5 - .2; t += B) hat(t);

// llegadas de escena: aire + golpe grave en el pulso
[A2, A3, A4, A5, A6].forEach(t => { whoosh(t); sub(t); });
// pasos: un aire más corto cuando cada tarjeta se asienta
S.forEach(t => whoosh(t, .09, .6, .38));

// gancho: aire que crece mientras se dibuja la curva + ping en la punta
swell(C.curve[0], C.curve[1] - .05);
bell(81, C.dot, .07, .35);          // La5
bell(88, C.dot + .02, .025, .35);   // Mi6, brillo
C.ticks.forEach(t => tick(t));

// quién: el cartel de Balanz entra con un clic suave
click(C.badge, .07);
// credenciales: una campana por sello, subiendo por el acorde de Sol
[71, 74, 78, 81].forEach((m, i) => bell(m, C.seals[i], .075, -.3 + .2 * i));
// cómo trabajamos: elegir horario, medidor, tecleo de "Vos", dona
click(C.slot, .1);
glide(C.gauge[0], C.gauge[1], 69, 76);
C.donut.forEach((t, i) => pluck([69, 72, 74, 76, 79][i] + 12, t, .7, -.3 + .15 * i, .05));

// mi cartera: la curva real suena. Se recorre igual que el video (power2.inOut) y en
// cada semicorchea se toca la nota de la escala que corresponde al valor del día.
const PENTA = [0, 2, 4, 7, 9];                               // Re mayor pentatónica
const toScale = (v, lo, hi, base, span) => {
  const steps = Math.round((v - lo) / ((hi - lo) || 1) * span);
  return base + 12 * Math.floor(steps / 5) + PENTA[((steps % 5) + 5) % 5];
};
const rows = DATA.rows, mins = rows.map(r => r[1]), spxs = rows.map(r => r[2]);
const lo = Math.min(...mins, ...spxs), hi = Math.max(...mins, ...spxs);
const ease = u => u < .5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
let lastM = -1, lastS = -1;
for (let k = 0; k <= 12; k++) {
  const t = C.chart[0] + k * C.chart[1] / 12, i = Math.min(rows.length - 1, Math.round(ease(k / 12) * (rows.length - 1)));
  const mm = toScale(mins[i], lo, hi, 74, 9), ms = toScale(spxs[i], lo, hi, 62, 9);
  if (k < 12) {
    if (mm !== lastM) pluck(mm, t, .8, .25, .07); lastM = mm;
    if (k % 2 === 0 && ms !== lastS) pluck(ms, t + .01, .6, -.3, .04); lastS = ms;
  }
}
// los números llegan: acorde de campanas en el pulso
[[74, .06], [78, .045], [81, .05], [86, .035]].forEach(([m, g], i) => bell(m, LAND + i * .015, g, -.2 + .13 * i));

// cierre: cada línea del título con una nota del La sus; la web resuelve a Re
[64, 67, 69].forEach((m, i) => pluck(m + 12, A6 + i * .375, .7, -.2 + .2 * i, .055));
click(C.url, .09);
sub(C.url, .14);
[[74, .07], [78, .05], [81, .06], [86, .045], [90, .03]].forEach(([m, g], i) => bell(m, C.url + i * .02, g, -.3 + .15 * i, 3.5));

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
      for (const c of combs) { const o = c.b[c.i]; c.f = o * .7 + c.f * .3; c.b[c.i] = x + c.f * .86; c.i = (c.i + 1) % c.b.length; y += o; }
      for (const a of aps) { const o = a.b[a.i]; const z = -y + o; a.b[a.i] = y + o * .5; a.i = (a.i + 1) % a.b.length; y = z; }
      out[n] = y;
    }
    return out;
  };
  return [chan(0), chan(23)];
}
const [RL, RR] = reverb();
const WET = 1.1;
let peak = 0;
for (let n = 0; n < N; n++) {
  L[n] += RL[n] * WET; R[n] += RR[n] * WET;
  peak = Math.max(peak, Math.abs(L[n]), Math.abs(R[n]));
}
// normaliza a -1 dBFS y funde los últimos 0,6 s
const g = .89 / peak, fadeFrom = (END - .6) * SR;
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
console.log(`${out} · ${(N / SR).toFixed(2)} s · llegadas ${C.arrive.join(', ')}`);
