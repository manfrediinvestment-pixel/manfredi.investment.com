// Efectos de sonido sintetizados (osciladores + ruido), sin bajar nada.
// Genera WAV mono 48 kHz / 16 bit en out/sfx/.
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DIR = path.join(HERE, 'out/sfx');
const SR = 48000;
mkdirSync(DIR, { recursive: true });

// ruido con semilla
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const buf = s => new Float32Array(Math.round(s * SR));
const TAU = Math.PI * 2;

// filtro biquad (RBJ) con frecuencia que puede cambiar muestra a muestra
function biquad(type) {
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  return (x, f, q = 0.9) => {
    const w = TAU * Math.min(f, SR * 0.45) / SR, c = Math.cos(w), a = Math.sin(w) / (2 * q);
    let b0, b1, b2;
    if (type === 'bp') { b0 = a; b1 = 0; b2 = -a; }
    else if (type === 'lp') { b0 = (1 - c) / 2; b1 = 1 - c; b2 = (1 - c) / 2; }
    else { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = (1 + c) / 2; }
    const a0 = 1 + a, a1 = -2 * c, a2 = 1 - a;
    const y = (b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0;
    x2 = x1; x1 = x; y2 = y1; y1 = y; return y;
  };
}

function normalize(b, peak = 0.89) { let m = 0; for (const v of b) m = Math.max(m, Math.abs(v)); if (m) for (let i = 0; i < b.length; i++) b[i] *= peak / m; return b; }

function wav(name, b) {
  const n = b.length, out = Buffer.alloc(44 + n * 2);
  out.write('RIFF', 0); out.writeUInt32LE(36 + n * 2, 4); out.write('WAVE', 8); out.write('fmt ', 12);
  out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(1, 22); out.writeUInt32LE(SR, 24); out.writeUInt32LE(SR * 2, 28); out.writeUInt16LE(2, 32); out.writeUInt16LE(16, 34);
  out.write('data', 36); out.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) out.writeInt16LE(Math.round(Math.max(-1, Math.min(1, b[i])) * 32767), 44 + i * 2);
  writeFileSync(path.join(DIR, name + '.wav'), out);
}

// reverb Schroeder simple (4 combs + 2 allpass)
function reverb(b, tail = 2.4, mix = 0.35) {
  const out = new Float32Array(b.length + Math.round(tail * SR));
  out.set(b);
  const combs = [1557, 1617, 1491, 1422].map(d => ({ d: Math.round(d * SR / 44100), buf: null, i: 0, fb: 0.84 }));
  combs.forEach(c => { c.buf = new Float32Array(c.d); });
  const aps = [225, 556].map(d => ({ d: Math.round(d * SR / 44100), buf: new Float32Array(Math.round(d * SR / 44100)), i: 0 }));
  const wet = new Float32Array(out.length);
  for (let n = 0; n < out.length; n++) {
    const x = n < b.length ? b[n] : 0; let s = 0;
    for (const c of combs) { const y = c.buf[c.i]; c.buf[c.i] = x + y * c.fb; c.i = (c.i + 1) % c.d; s += y; }
    s *= 0.25;
    for (const a of aps) { const y = a.buf[a.i]; const v = s + y * 0.5; a.buf[a.i] = v; a.i = (a.i + 1) % a.d; s = y - v * 0.5; }
    wet[n] = s;
  }
  for (let n = 0; n < out.length; n++) out[n] = out[n] * (1 - mix) + wet[n] * mix * 2.2;
  return out;
}

const env = (t, a, d) => t < a ? t / a : Math.exp(-(t - a) / d);

// whoosh: ruido filtrado con barrido de frecuencia, 0,4 s
{
  const r = mulberry32(1), b = buf(0.4), bp = biquad('bp'), bp2 = biquad('bp');
  for (let i = 0; i < b.length; i++) {
    const t = i / SR, u = t / 0.4, f = 250 * Math.pow(18, Math.sin(u * Math.PI * 0.9));
    const e = Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.05)), 1.6);
    const n = r() * 2 - 1;
    b[i] = (bp(n, f, 1.2) * 0.8 + bp2(n, f * 1.9, 2) * 0.4) * e;
  }
  wav('whoosh', normalize(b));
}

// impacto: sub de 50 Hz con caída + click
{
  const r = mulberry32(2), b = buf(1.1), lp = biquad('lp');
  let ph = 0;
  for (let i = 0; i < b.length; i++) {
    const t = i / SR, f = 50 + 70 * Math.exp(-t / 0.035);
    ph += TAU * f / SR;
    const sub = Math.sin(ph) * env(t, 0.002, 0.32);
    const click = (r() * 2 - 1) * Math.exp(-t / 0.004) * 0.9 + Math.sin(TAU * 2400 * t) * Math.exp(-t / 0.006) * 0.4;
    const body = lp(r() * 2 - 1, 900, 0.7) * Math.exp(-t / 0.05) * 0.8;
    b[i] = Math.tanh((sub * 1.3 + click + body) * 1.4);
  }
  wav('impact', normalize(b));
}

// riser: ruido + seno subiendo, 1,5 s (corta seco en el golpe)
{
  const r = mulberry32(3), b = buf(1.5), bp = biquad('bp'), hp = biquad('hp');
  let ph = 0, ph2 = 0;
  for (let i = 0; i < b.length; i++) {
    const t = i / SR, u = t / 1.5, f = 180 * Math.pow(8, u * u);
    ph += TAU * f / SR; ph2 += TAU * f * 1.5 / SR;
    const e = Math.pow(u, 2.2) * (u > 0.985 ? (1 - u) / 0.015 : 1);
    const n = bp(hp(r() * 2 - 1, 400), 600 + 7000 * u * u, 0.8);
    b[i] = (n * 1.1 + Math.sin(ph) * 0.35 + Math.sin(ph2) * 0.15) * e;
  }
  wav('riser', normalize(b, 0.85));
}

// chispa eléctrica: ruido con bitcrush + pitidos muy cortos
{
  const r = mulberry32(4), b = buf(0.32), hp = biquad('hp');
  let hold = 0;
  for (let i = 0; i < b.length; i++) {
    const t = i / SR;
    if (i % 9 === 0) hold = r() * 2 - 1;                         // sample & hold ≈ 5 kHz
    const crushed = Math.round(hold * 6) / 6;                     // ~3 bits
    const gate = (Math.sin(TAU * 38 * t) > -0.2 ? 1 : 0.25) * (r() < 0.985 ? 1 : 0);
    const n = hp(crushed, 1800, 0.7) * gate * Math.exp(-t / 0.09);
    let beep = 0;
    [[0, 3900], [0.045, 5200], [0.11, 3300]].forEach(([s, f]) => { if (t >= s && t < s + 0.018) beep += Math.sin(TAU * f * (t - s)) * 0.5; });
    b[i] = n * 0.9 + beep;
  }
  wav('spark', normalize(b, 0.8));
}

// tick suelto y tira de ticks que se acelera (contadores)
function tick(b, at, amp = 1) {
  const s = Math.round(at * SR);
  for (let i = 0; i < 0.03 * SR && s + i < b.length; i++) {
    const t = i / SR;
    b[s + i] += (Math.sin(TAU * 2600 * t) * 0.6 + Math.sin(TAU * 5200 * t) * 0.25) * Math.exp(-t / 0.006) * amp;
  }
}
{
  const b = buf(1.25);
  let t = 0, gap = 0.11;
  while (t < 1.15) { tick(b, t, 0.7 + 0.3 * t); t += gap; gap = Math.max(0.035, gap * 0.86); }
  wav('ticks', normalize(b, 0.8));
}

// golpe final con cola de reverb (marca de agua)
{
  const r = mulberry32(6), dry = buf(1.2);
  let ph = 0;
  for (let i = 0; i < dry.length; i++) {
    const t = i / SR, f = 48 + 60 * Math.exp(-t / 0.04);
    ph += TAU * f / SR;
    const sub = Math.sin(ph) * env(t, 0.002, 0.45);
    const click = (r() * 2 - 1) * Math.exp(-t / 0.005) * 0.6;
    // acorde "champagne": parciales tipo campana
    let bell = 0;
    [[392, 1], [587.3, 0.7], [784, 0.5], [1174.7, 0.3], [1568, 0.18]].forEach(([fq, a], k) => { bell += Math.sin(TAU * fq * t + k) * a * Math.exp(-t / (0.5 + k * 0.08)); });
    dry[i] = Math.tanh(sub * 1.2 + click) * 0.9 + bell * 0.22 * env(t, 0.004, 0.9);
  }
  wav('hit', normalize(reverb(dry, 2.6, 0.4)));
}

console.log('sfx →', DIR);
