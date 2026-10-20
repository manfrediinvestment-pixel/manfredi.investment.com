// Render completo: seek cuadro por cuadro a 30 fps y PNG por stdin a ffmpeg (image2pipe).
//   node render.mjs [--out output/reel-asesoria-v2.mp4] [--frames]   (--frames guarda además los PNG en frames/)
// Si existe output/audio.wav (node audio.mjs), se le suma como pista AAC.
import { spawn } from 'node:child_process';
import { access, mkdir, rename, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { FPS, HERE, openVideo } from './lib.mjs';

const arg = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const out = join(HERE, arg('--out') || 'output/reel-asesoria-v2.mp4');
const wav = join(HERE, 'output', 'audio.wav');
const hasAudio = await access(wav).then(() => true, () => false);
const silent = hasAudio ? out.replace(/\.mp4$/, '.sin-audio.mp4') : out;
const keepFrames = process.argv.includes('--frames');
// ffmpeg: FFMPEG=ruta/al/ffmpeg si no está en el PATH (en Windows, la carpeta bin de Gyan.FFmpeg)
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
await mkdir(join(HERE, 'output'), { recursive: true });
if (keepFrames) await mkdir(join(HERE, 'frames'), { recursive: true });

const v = await openVideo();
const total = Math.round(v.duration * FPS);
const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-r', String(FPS), '-movflags', '+faststart', silent],
  { stdio: ['pipe', 'ignore', 'inherit'] });
const done = new Promise((ok, ko) => ff.on('close', c => c === 0 ? ok() : ko(new Error('ffmpeg salió con ' + c))));

for (let i = 0; i <= total; i++) {
  const png = await v.shot(i / FPS);
  if (keepFrames) await writeFile(join(HERE, 'frames', String(i).padStart(6, '0') + '.png'), png);
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r${i}/${total} cuadros`);
}
ff.stdin.end();
await v.close();
await done;
if (hasAudio) {
  const mux = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], { stdio: 'inherit' });
  await new Promise((ok, ko) => mux.on('close', c => c === 0 ? ok() : ko(new Error('ffmpeg (audio) salió con ' + c))));
  await rm(silent);
}
console.log(`\nListo: ${out} (${total + 1} cuadros, ${(total / FPS).toFixed(2)} s)`);
