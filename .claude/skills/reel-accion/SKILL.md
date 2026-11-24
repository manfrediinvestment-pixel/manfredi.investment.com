---
name: reel-accion
description: "Use when the user asks for a 'reel de acción' / 'reel de accion [ticker]' / 'video a cámara de [ticker]' — the talking-head format (sin IA) for manfredinvestment.com: the user records himself speaking to camera (vertical) and above his head goes a HORIZONTAL 16:9 clip. Delivers, for one ticker that already has `informes/<ticker>.html`: (1) a ≤5 s hook clip that connects everyday life with a verified financial fact, (2) three analysis sections taken from the report, each with a two-phase animated chart, (3) the generic 'Comentá INFORME' closing clip (48 logos + a real report turning pages), (4) the full script of what to say, (5) a local preview page and copies on the Desktop. Trigger with just 'reel de acción NFLX', 'reel accion de KO', 'hacé el video a cámara de AAPL' — no more context is needed. NOT the old AI vertical reel (that is skill reel-informe)."
metadata:
  version: 1.0.0
  piloto: NFLX 16-nov-2026 (marketing/video-camara-nflx, rama feat/video-camara-nflx)
---

# Reel de acción (video a cámara)

**Por qué existe:** los reels hechos con IA no funcionaron ("a la gente no le gusta ver videos creados con IA").
Ahora el user habla a cámara mirando a lente, y arriba de su cabeza va un clip horizontal 16:9 (ancho completo, tercio
superior del cuadro vertical). Todo tiene que ser muy profesional y con detalle. El piloto es NFLX: el user lo aprobó
("está realmente perfecto"), así que **NFLX es la vara**. Copiá su estructura, no la reinventes.

## Qué se entrega

| Pieza | Archivo | Duración |
|---|---|---|
| Gancho | `salida/gancho.mp4` | 5 s exactos |
| Sección 1, 2, 3 | `salida/seccion-N.mp4` | 10 s cada una, 2 gráficos (cambia en el seg. 4,9) |
| Cierre (el mismo para todos) | `salida/cierre.mp4` | 7 s |
| Guion | `GUION.md` | ~65–75 s hablados |
| Vista previa | `salida/index.html` servido en http://localhost:8765/ | — |

Y una copia de los mp4, los png de cada gráfico y el guion en `C:\Users\Equipo\Desktop\Video reels\<TICKER> a camara\`.

## Flujo

### 0 · Rama y carpeta
- Respetá el CLAUDE.md: rama nueva `feat/reel-accion-<ticker>` desde `origin/main`
  (si `main` está tomado por un worktree: `git checkout -b feat/reel-accion-<t> origin/main`). El working dir lo
  comparten otras sesiones: mirá la rama actual antes de tocar nada.
- Copiá la plantilla: `cp -r .claude/skills/reel-accion/plantilla marketing/reel-accion-<ticker>`.
  Trae `comun/` (base.css + charts.js), `gancho/`, `seccion-1..3/` (con el contenido de NFLX como ejemplo a
  reemplazar), `cierre/` (genérico, NO se toca), `render.sh`, `snap.sh`, `capturar-paginas.py`,
  `preview-ejemplo.html`, `GUION-ejemplo.md` y `.gitignore`.
- Si `informes/<ticker>.html` no existe, ofrecé hacer el informe primero (skill del sector que corresponda).

### 1 · Datos
`python -I .claude/skills/reel-accion/datos.py <ticker> marketing/reel-accion-<ticker>` →
`datos/informe.txt` (el informe en texto) y `datos/precio.json` (1 año de cierres diarios + máximo, mínimo, último,
variación y los 8 días de mayor movimiento). **Leé el informe entero**, no solo el resumen. Anotá cada número con su
sección (01–14) para la tabla de fuentes del guion.

### 2 · El gancho (lo más importante)
El user rechazó el primer gancho de NFLX ("Le pagaron US$ 2.800 M por perder") por **pobre**: pide **conectar algo del
día a día de la gente común con algo de finanzas**. Fórmula que aprobó:

> **algo que la persona usa, paga o ve todos los días** ↔ **un dato de la acción que choca con eso**.
> NFLX: "¿Pagás Netflix? Este año te subió el precio otra vez… y aun así su acción vale la mitad que hace un año."
> Pantalla: "Vos pagás más. La acción vale la mitad." + tarjeta "Lo que pagás vos ↑" + tarjeta "Lo que vale su acción −48%" + precio diario.

Otro gancho que funcionó (NVDA): "una infidelidad le costó a NVIDIA ~US$ 430.000 M en dos días". Llamativo, pero
**funcional**: el dato es real y lleva directo al análisis.

Puntos de contacto con la vida diaria según el tipo de empresa (ideas, no plantillas cerradas):
- Consumo (KO, PEP, PG, WMT, COST): lo que pagás en el súper, el tamaño del paquete, la marca que está en tu casa.
- Plataformas y apps (NFLX, SPOT, UBER, META, GOOGL, AMZN, MELI): tu suscripción, el viaje, lo que comprás, las horas en el celular.
- Tecnología y semis (AAPL, NVDA, AMD, TSM, QCOM): tu celular, ChatGPT, la compu, la consola.
- Bancos y pagos (JPM, BAC, V, MA, AXP): tu tarjeta, cada vez que pagás con el celular, la comisión.
- Salud (LLY, JNJ, UNH): el remedio para adelgazar, la prepaga, el ibuprofeno del botiquín.
- Autos y energía (TSLA): el auto, la nafta.

Reglas:
- Todo dato del gancho tiene que estar en el informe o en `precio.json`. Si usás un salto de un día, buscá QUÉ pasó
  esa fecha (en el informe o en la prensa) antes de usarlo. Nada inventado ni exagerado.
- El dato "fuerte" que no entró en el gancho abre la Sección 1 como segundo gancho (en NFLX: "Primero: a Netflix le
  pagaron 2.800 millones… por perder").
- En el guion dejá el gancho elegido + 2 alternativas cortas, por si el user prefiere otro.
- Título en pantalla corto, en dos golpes: "Vos pagás más. *La acción vale la mitad.*"

### 3 · Las 3 secciones
Elegí las 3 cosas más llamativas **y de las que se esté hablando** (la noticia del trimestre, la paradoja de los
números, la pregunta "¿está barata?"). Cada sección:
- kicker `0N · TEMA` + título-frase que se entiende sin audio (ej. "Se salvó de una deuda *12 veces* más grande").
- **Gráfico obligatorio, dos fases**: A (0–4,9 s) el dato principal, B (5,2–10 s) la consecuencia o el contraste.
  Datos del informe; si el informe no tiene el gráfico, lo armás vos con sus números.
- Una línea de fuente abajo (`.src`): qué es y de dónde sale.
- Texto a cámara: ~15–20 s por sección, rioplatense, frases cortas, marcando con ▶ la frase donde entra el gráfico B.

Estructura que funcionó en NFLX: 1) el evento del año (Warner: deuda evitada + recompras récord) · 2) la paradoja
(margen récord vs. ventas que frenan) · 3) ¿está barata? (P/E propio 35x → 21x + comparables: "casi como Disney").

### 4 · Construir los clips (HyperFrames 0.7.109)
- Composición 1920×1080, 30 fps, `data-composition-id` = nombre de la carpeta, timeline GSAP pausado en
  `window.__timelines[id]`. Cada clip es su propio proyecto (`<clip>/index.html`); `render.sh` y `snap.sh` copian
  `comun/` adentro antes de correr.
- Gráficos: `MC.vbars`, `MC.hbars`, `MC.line` de `comun/charts.js` (ver los usos en las secciones de la plantilla:
  `notes`, `outline` para valores guiados/estimados, `valColors`, `labColors`, `subs`). Gancho: línea de precio SVG
  con `clipPath` que revela de izquierda a derecha y contador que sube hasta la variación.
- Logo: en NFLX el "N" es un SVG propio. Para otros tickers usá `assets/logos/<ticker>.png` (128 px, fondo blanco)
  dentro de un cuadrito blanco redondeado; no lo agrandes más de ~110 px porque se pixela.
- **Diseño de la casa (obligatorio):** paleta de `comun/base.css` (fondo `#060d19`, dorados `#e6cf96/#f0dcaa/#c9a24f`,
  negativo `#f2857b`, color de marca de la empresa solo como acento); títulos en DM Serif Display, números en IBM Plex
  Mono. **CERO texto gris, sin grilla ni líneas de fondo, sin letra blanca básica, y NUNCA el fair value / precio
  objetivo** (ni en pantalla ni en el guion: el guion dice "en el informe te muestro cuánto creemos que vale").
  Sobrio: nada de tarjetas de colores chillones.
- El clip se ve a ~56% de su tamaño arriba de la cabeza: texto mínimo ~22 px, números grandes.

### 5 · Revisar y renderizar
- `bash snap.sh <clip> 3.8,9.5` (gancho: `1.6,4.9`) y **mirá cada cuadro**: textos que se pisan con la línea, valores
  que se salen del cuadro, notas encimadas, fuente que choca con el logo de Manfredi. Corregí y volvé a mirar.
- `bash render.sh` (todos) o `bash render.sh gancho`. Verificá duración y tamaño con `ffprobe`.
- Recalculá con un script toda variación que aparezca (%, "12 veces", "la mitad"): no a ojo.

### 6 · Guion, vista previa y entrega
- `GUION.md` con la misma estructura que `GUION-ejemplo.md`: tabla de clips, gancho (+2 alternativas), las 3
  secciones con ▶, cierre, notas de TikTok/IG y la tabla "Datos y fuentes" con la sección del informe de cada número.
- Cierre hablado, siempre:
  > "Si comentás la palabra **INFORME**, te mando el informe completo de <Empresa> y de otras 40 acciones, con una
  > IA que te lo explica, y un código de descuento. Esto no es recomendación de inversión: es análisis para que decidas vos."
  Instagram: el bot de SendPulse responde INFORME → /guia-informes con MANFREDI30. TikTok no tiene bot: "link en mi
  perfil" + comentario fijado.
- `salida/index.html`: copiá `preview-ejemplo.html` y cambiá títulos y textos (los videos van en orden, con lo que se
  dice abajo de cada uno). Servilo con `python -m http.server 8765` (en segundo plano, desde `salida/`) y abrilo.
  Si los videos cambian, subí el `?v=` de los `src` para que el navegador no muestre los viejos.
- Copiá mp4 + png (último cuadro de cada fase con `ffmpeg -sseof -0.1` y `-ss 4.7`) + GUION.md al Escritorio.

### 7 · Commit
Commit en la rama (sin mp4: `salida/` y `snaps/` están en `.gitignore`), avisá que está lista para revisar y **no
mergees sin que el user lo pida**. Actualizá la memoria `project_video_camara_formato.md` con el ticker hecho.

## El cierre genérico
`cierre/` no se edita por ticker: "Comentá INFORME" + subtítulo "El informe completo de esta acción y de otras 40 · con
una IA que te lo explica", 48 logos de empresas con informe y un informe 3D que pasa 8 páginas reales.
- Si se suman informes nuevos: copiar el logo a `cierre/logos/` y agregar el ticker al array `T` del `index.html`
  (grilla de 7 columnas; el último cuadro dice "y más").
- Para cambiar las páginas: editar `PICKS` en `capturar-paginas.py` y correrlo (usa `?preview=full`). Mirá cada
  captura: ninguna puede mostrar fair value ni la portada del informe.
