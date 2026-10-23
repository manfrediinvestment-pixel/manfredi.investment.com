// Render: Playwright → seek(t) cuadro a cuadro (60 fps internos) → ffmpeg (tmix 2 → 30 fps).
// Audio: efectos de sfx.mjs mezclados con adelay + amix en los tiempos de config.mjs,
// loudnorm a −14 LUFS (dos pasadas) y medición final con ebur128.
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import path from 'node:path';
import { openComposition, HERE } from './lib.mjs';
import { DURATION, RENDER_FPS, FPS, STARTS, SNAP, timeline } from './config.mjs';

let FFMPEG = 'ffmpeg';
try { const s = (await import('ffmpeg-static')).default; if (s && existsSync(s)) FFMPEG = s; } catch {}
const OUT = path.join(HERE, 'out');
const MUSIC = path.join(HERE, 'audio/musica.mp3');
mkdirSync(OUT, { recursive: true });
const o = f => path.join(OUT, f);
const run = (args, opts = {}) => { const r = spawnSync(FFMPEG, ['-hide_banner', '-y', ...args], { encoding: 'utf8', maxBuffer: 1 << 28, ...opts }); if (r.status !== 0) { console.error(r.stderr.slice(-3000)); throw new Error('ffmpeg falló'); } return r; };

// ── 1 · efectos ──
await import('./sfx.mjs');

// ── 2 · música: golpes (onsets) por energía y cortes al golpe más cercano ──
let cuts = {};
const hasMusic = existsSync(MUSIC);
if (hasMusic) {
  const SR = 11025, HOP = 110; // ~10 ms
  const r = spawnSync(FFMPEG, ['-hide_banner', '-i', MUSIC, '-ac', '1', '-ar', String(SR), '-f', 'f32le', '-'], { maxBuffer: 1 << 30 });
  const pcm = new Float32Array(r.stdout.buffer, r.stdout.byteOffset, Math.floor(r.stdout.length / 4));
  const E = [];
  for (let i = 0; i + HOP <= pcm.length; i += HOP) { let s = 0; for (let j = 0; j < HOP; j++) s += pcm[i + j] * pcm[i + j]; E.push(Math.log10(1e-9 + s / HOP)); }
  const flux = E.map((v, i) => Math.max(0, v - (E[i - 1] ?? v)));
  const mean = flux.reduce((a, b) => a + b, 0) / flux.length, sd = Math.sqrt(flux.reduce((a, b) => a + (b - mean) ** 2, 0) / flux.length);
  const onsets = [];
  flux.forEach((v, i) => { if (v > mean + 1.5 * sd && v >= (flux[i - 1] ?? 0) && v >= (flux[i + 1] ?? 0)) { const t = i * HOP / SR; if (!onsets.length || t - onsets.at(-1) > 0.12) onsets.push(t); } });
  for (const k of SNAP) {
    const near = onsets.filter(t => Math.abs(t - STARTS[k]) <= 0.35).sort((a, b) => Math.abs(a - STARTS[k]) - Math.abs(b - STARTS[k]))[0];
    if (near != null) cuts[k] = +near.toFixed(3);
  }
  console.log('música: golpes detectados', onsets.length, '· cortes ajustados', cuts);
}
const { sfx } = timeline(cuts);

// ── 3 · video ──
const { page, close } = await openComposition({ port: 8823, cuts: hasMusic ? cuts : null });
const VIDEO = o('_video.mp4');
const N = Math.round(DURATION * RENDER_FPS);
const ff = spawn(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(RENDER_FPS), '-i', '-',
  '-vf', `tmix=frames=2,fps=${FPS},format=yuv420p`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-movflags', '+faststart', VIDEO], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise((ok, ko) => ff.on('close', c => c === 0 ? ok() : ko(new Error('ffmpeg video ' + c))));
const cdp = await page.context().newCDPSession(page);
const t0 = Date.now();
try {
  for (let f = 0; f < N; f++) {
    await page.evaluate(t => window.seek(t), f / RENDER_FPS);
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 96, optimizeForSpeed: false, captureBeyondViewport: false });
    if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 120 === 0) process.stdout.write(`\r  cuadro ${f}/${N} · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end(); await done;
  // último cuadro (marca de agua quieta), para el loop
  await page.evaluate(t => window.seek(t), DURATION - 0.001);
  await page.screenshot({ path: o('cuadro-final.png') });
} finally { await close(); }
// portada diseñada aparte (portada.html)
await import('./portada.mjs');
console.log(`\n  video listo en ${((Date.now() - t0) / 1000).toFixed(0)} s`);

// ── 4 · audio ──
const ins = [], fl = [];
sfx.forEach((e, i) => {
  ins.push('-i', path.join(OUT, 'sfx', e.f + '.wav'));
  const ms = Math.round(e.t * 1000);
  fl.push(`[${i}:a]aformat=sample_rates=48000:channel_layouts=mono,adelay=${ms}:all=1,volume=${e.g}dB[s${i}]`);
});
fl.push(sfx.map((_, i) => `[s${i}]`).join('') + `amix=inputs=${sfx.length}:normalize=0:duration=longest,apad,atrim=0:${DURATION},afade=t=out:st=${DURATION - 0.6}:d=0.6[fx]`);
let mixOut = '[fx]';
if (hasMusic) {
  ins.push('-i', MUSIC);
  fl.push(`[${sfx.length}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:${DURATION},afade=t=in:d=0.2,afade=t=out:st=${DURATION - 1.5}:d=1.5[mu]`);
  fl.push(`[fx]volume=-6dB,aformat=channel_layouts=stereo[fx2];[mu][fx2]amix=inputs=2:normalize=0:duration=first[mix]`);
  mixOut = '[mix]';
}
const RAW = o('_mix.wav');
run([...ins, '-filter_complex', fl.join(';'), '-map', mixOut, '-ar', '48000', '-ac', '2', RAW]);
// loudnorm en dos pasadas (medir → aplicar lineal)
const p1 = run(['-i', RAW, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-']);
const m = JSON.parse(p1.stderr.slice(p1.stderr.lastIndexOf('{'), p1.stderr.lastIndexOf('}') + 1));
const NORM = o('_mix_norm.wav');
run(['-i', RAW, '-af', `loudnorm=I=-14:TP=-1:LRA=11:measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}:linear=true`, '-ar', '48000', NORM]);

// ── 5 · mux ──
const MAIN = o('reel.mp4');
run(['-i', VIDEO, '-i', NORM, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', MAIN]);
if (!hasMusic) run(['-i', VIDEO, '-map', '0:v', '-c:v', 'copy', '-an', '-movflags', '+faststart', o('reel-mudo.mp4')]);

// ── 6 · medición final ──
const eb = run(['-nostats', '-i', MAIN, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr;
const sum = eb.slice(eb.lastIndexOf('Summary:'));
const I = (sum.match(/I:\s+(-?[\d.]+) LUFS/) || [])[1], LRA = (sum.match(/LRA:\s+(-?[\d.]+) LU/) || [])[1], TP = (sum.match(/Peak:\s+(-?[\d.]+) dBFS/) || [])[1];
const report = `Medición ebur128 de out/reel.mp4 (${hasMusic ? 'música + efectos' : 'solo efectos'})\nIntegrado: ${I} LUFS\nLRA: ${LRA} LU\nPico real: ${TP} dBFS\nObjetivo: loudnorm I=-14 TP=-1 LRA=11\n`;
writeFileSync(o('loudness.txt'), report);
console.log(report);
for (const f of ['_mix.wav', '_mix_norm.wav']) rmSync(o(f), { force: true });
