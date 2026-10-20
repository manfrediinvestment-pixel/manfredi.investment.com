// Portada del Reel (1080x1920 PNG) → output/portada-reel-asesoria.png
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { HERE, openVideo } from './lib.mjs';

await mkdir(join(HERE, 'output'), { recursive: true });
const v = await openVideo('cover.html');
const file = join(HERE, 'output', 'portada-reel-asesoria.png');
await writeFile(file, await v.shot(0));
await v.close();
console.log(file);
