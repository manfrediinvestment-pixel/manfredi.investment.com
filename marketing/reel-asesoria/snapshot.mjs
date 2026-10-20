// Cuadros sueltos para revisar antes del render completo.
//   node snapshot.mjs --at 1,4,7,11,17,21,23
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { HERE, openVideo } from './lib.mjs';

const i = process.argv.indexOf('--at');
const times = (i > 0 ? process.argv[i + 1] : '1,4,7,11,17,21,23').split(',').map(Number);
const dir = join(HERE, 'snapshots');
await mkdir(dir, { recursive: true });
const v = await openVideo();
for (const t of times) {
  const file = join(dir, `t${t.toFixed(2).replace('.', '_')}.png`);
  await writeFile(file, await v.shot(t));
  console.log(file);
}
await v.close();
