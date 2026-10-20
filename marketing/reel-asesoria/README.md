# Reel · Asesoría 1 a 1 · Próximamente

Video vertical 1080x1920 a 30 fps hecho con Node + Playwright + GSAP + ffmpeg (sin Remotion ni HyperFrames).

| Archivo | Qué hace |
|---|---|
| `data.mjs` | Lee del sitio el rendimiento **real** desde el 22/05/2026 de la cartera y del S&P 500 en la misma ventana → `data.json`. Correrlo el día del render. |
| `video.html` | El video: escenas `<section>` y **una sola** línea de tiempo GSAP en pausa (`window.seek`, `window.DURATION`). |
| `snapshot.mjs` | Cuadros sueltos para revisar: `node snapshot.mjs --at 1,4,7,11,17,21,23` → `snapshots/` |
| `audio.mjs` | Música y efectos sintetizados por código, atados a `window.CUES` del video (80 BPM: cada escena llega en un pulso y cambia el acorde) → `output/audio.wav`. |
| `render.mjs` | Render completo → `output/reel-asesoria-v2.mp4`, con el audio si existe `output/audio.wav` (`--frames` guarda además los PNG en `frames/`). |
| `cover.html` / `cover.mjs` | Portada → `output/portada-reel-asesoria.png` |
| `copy.md` | Texto del posteo. |

```bash
npm install                # Playwright local; Chromium: npx playwright install chromium
node data.mjs              # (--live para leer de manfredinvestment.com en vez del repo local)
node snapshot.mjs
node audio.mjs              # siempre antes de render si cambió la línea de tiempo
node render.mjs            # ffmpeg fuera del PATH: FFMPEG="C:/…/ffmpeg-9.0-full_build/bin/ffmpeg.exe" node render.mjs
node cover.mjs
```

Para ver el video en tiempo real: servir la carpeta y abrir `video.html?play`.
