// PNG de tiempos clave para revisar: node snapshot.mjs [t1 t2 ...]
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { openComposition, HERE } from './lib.mjs';

const T = process.argv.slice(2).map(Number);
const times = T.length ? T : [0.3, 1.5, 3.0, 5.5, 9.0, 13.0, 14.5, 16.5, 20.0, 24.5];
const dir = path.join(HERE, 'snapshots'); mkdirSync(dir, { recursive: true });
const { page, close } = await openComposition({ port: 8822 });
try {
  for (const t of times) {
    await page.evaluate(t => window.seek(t), t);
    const f = path.join(dir, `t${t.toFixed(2).padStart(5, '0')}.png`);
    await page.screenshot({ path: f });
    console.log(f);
  }
} finally { await close(); }
