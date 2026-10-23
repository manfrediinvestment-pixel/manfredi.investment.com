// Portada del reel (portada.html) → out/portada.png, 1080×1920.
import path from 'node:path';
import { openComposition, HERE } from './lib.mjs';

const { page, close } = await openComposition({ port: 8824, file: 'portada.html' });
try { await page.screenshot({ path: path.join(HERE, 'out/portada.png') }); console.log('portada → out/portada.png'); }
finally { await close(); }
