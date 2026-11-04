---
name: reel-noticia
description: Use when the user wants a vertical explainer reel (Instagram/TikTok, 1080x1920, ~60-70 s) about a market news event of one stock or company — a big drop or jump after earnings, a record day, a sector sell-off — told with Portiv-style motion (rolling numbers, vertical whip transitions, objects that fall and crack) in Manfredi's website colors, with the user's own voice, a "comentá PALABRA" CTA that sends a guide by DM, and the stock's full report updated. Trigger on: "reel de la caída de [empresa]", "video de [ticker] por los resultados", "hacé un video como el de Google", "video explicativo de [noticia]", "por qué cayó/subió [ticker], en video". Covers the whole pipeline: verify the data, find the hook, write the exact script the user records, build every scene in HyperFrames, render at 60 fps, review frame by frame, update the report and build the guide page. Not for the 5-block report reels (that is reel-informe).
---

# Reel de noticia — método completo (piloto: Google −12,64%, 02-nov-2026)

Formato copiado del reel de **@portivapp sobre Intel** (31-oct-2026, 88 s, 2,8k likes), analizado cuadro por cuadro a 60 fps,
y llevado a la identidad de Manfredi. Lo que el user pidió replicar **por encima de todo**: el movimiento (transiciones,
caídas, contadores), los colores y los logos. El análisis financiero tiene que ser nuestro y verificado.

Proyecto piloto completo (copiar de ahí cualquier escena): `marketing/reel-google-caida/` en la rama
`feat/reel-google-caida`. Plantillas en `plantillas/` de esta skill.

---

## 0. Reglas que no se negocian

- **Rama nueva + worktree** (`git worktree add ../manfredi-reel-<ticker> -b feat/reel-<ticker>-<evento> origin/main`). Nunca en main.
- **Cero datos sin verificar.** Cada número del guion tiene fuente primaria (8-K de la SEC, cierres diarios de Yahoo/Nasdaq) y se recalcula con script.
- **Cero texto gris** en todo (video, guía, informe). Palabras "apagadas" = dorado oscuro `#B8943F`, no gris.
- **La voz la graba el user** ("así no todo es 100% IA"). Nosotros entregamos el guion exacto; el video se construye con subtítulo karaoke y después se sincroniza a su audio.
- **No es recomendación de inversión**: el user no está matriculado como asesor. Cuando aparece nuestro valor justo, va el aviso en pantalla.
- Duración: **≤ ~70 s** ("no más de un minuto, o no mucho más").

---

## 1. Investigación: confirmar la noticia y encontrar el gancho

1. **Qué pasó** — `WebSearch` modo `extended`: "<empresa> stock falls after <trimestre> earnings". Fecha del reporte, magnitud, por qué.
2. **Cierres diarios de toda la historia** (sin API key):
   `curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/<TICKER>?period1=1092000000&period2=1794000000&interval=1d"`
   (`range=max` devuelve datos mensuales: no sirve). Con Python, calcular la variación diaria de toda la serie y ordenar:
   así salió "**peor día desde que salió a la bolsa en 2004**, peor que el COVID (−11,63%) y 2008 (−11,61%)". Ese ranking es el gancho más fuerte que existe; buscarlo siempre (peor/mejor día desde X).
   Confirmar el superlativo con prensa (NBC, Benzinga, Yahoo) antes de usarlo.
3. **Valor borrado**: tomarlo de prensa (Yahoo Finance da el cierre) y decir "casi medio billón" en la voz y la cifra exacta en pantalla.
4. **8-K oficial** (el comunicado trae todo: segmentos, balance, flujo de caja, impacto de partidas no recurrentes en EPS):
   `curl -s --compressed -A "Manfredi Investment research contact@manfredinvestment.com" "https://www.sec.gov/Archives/edgar/data/<CIK>/<accession>/<exhibit>.htm"`
   (sin `--compressed` y ese User-Agent la SEC devuelve vacío). Convertir a texto con `re.sub('<[^>]+>',' ',…)`.
5. **Pares ese mismo día** (cinta de cotizaciones): bajar los cierres de 5-6 pares y calcular la variación del día.
6. **Nuestro diferencial**: ¿hay `informes/<ticker>.html`? Ver el valor justo y **desde cuándo está publicado** con
   `git log --format="%h %ad" --date=short -- informes/<ticker>.html` + `git show <hash>:informes/<ticker>.html | grep <valor>`.
   Si el precio "llegó" a nuestro valor, ese es el remate del video (Google: valor justo US$ 286,95 publicado el 5-ago,
   la acción cotizaba 356 y terminó en 283).

Datos que hay que tener en una tabla antes de escribir una línea: caída del día y precio antes/después, ranking histórico,
valor borrado, ventas vs año anterior, el dato que de verdad castigó el mercado (en Google: capex vs flujo operativo →
flujo libre negativo), la "ironía" (algo que se dio vuelta), el contrapeso positivo (Cloud +103%), y nuestro valor justo.

---

## 2. La historia (pensada como marketing, construida como analista)

Estructura del piloto, en el orden en que funciona. Cada bloque es una escena; entre escenas, latigazo vertical.

| # | Escena | Qué hace | Fondo |
|---|---|---|---|
| 1 | **Golpe** (0–3 s) | "X tuvo el peor día de su historia." Número rueda hasta −12,64% mientras se dibuja el gráfico real; el chip con el logo cae y **se parte**; flash rojo + temblor; regla de años que retrocede hasta el año de la salida a bolsa. | aurora |
| 2 | **Ranking** (3–7 s) | "Peor que en 2008. Peor que en el COVID." Barras de las peores caídas; la nueva **cae desde arriba** y empuja a las otras; contador "US$ 475.000 M" + "borrados" letra por letra; cinta de cotizaciones de pares. | panel |
| 3 | **La pregunta** (7–10 s) | "Y eso que vendió 25% más. ¿Entonces por qué cayó?" Barras de ventas, lupa sobre el chip roto, "?" rojo. **Bucle abierto** que retiene. | aurora |
| 4 | **La causa** (~10 s) | "Fue lo que gasta": billetes que salen disparados del chip, racks que caen, contador del gasto, comparación ×2,1. | panel |
| 5 | **La metáfora** (~10 s) | Algo cotidiano y NUEVO en cada video (ver regla de abajo). Piloto: panadería que compra hornos; la caja termina en **−9.065** con golpe. | aurora |
| 6 | **Lo irónico** (~9 s) | Algo que se dio vuelta (SpaceX: +99.000 M un trimestre, −8.664 M el siguiente): cohete que sube y cohete que cae. | panel |
| 7 | **El contrapeso** (~5 s) | Lo bueno que el mercado ignora (Cloud +103%) con callback a la metáfora del video (en el piloto, "los hornos ya venden"). | aurora |
| 8 | **Nuestro informe** (~8 s) | Tarjeta del informe con el valor justo + el precio cayendo hasta **tocar la línea dorada** ("a 1,1% de nuestro valor") + aviso de que no es recomendación. | panel |
| 9 | **Frase espejo + compartir** (~9 s) | "No lo castigó por vender poco. Lo castigó por gastar mucho." Tarjeta tachada vs tarjeta roja; cursor que toca Guardalo / Mandáselo / Ese amigo. | aurora |
| 10 | **Comentá PALABRA** (~5,6 s) | "Si querés el informe completo, comentá GOOGLE y te mando la guía." Tarjeta del informe, caja de comentario donde se tipea la palabra, se publica (corazón), llega el DM con "Ver la guía". | aurora |
| 11 | **Logo** (3,5 s) | Emblema + "Manfredi *Investment*" + "Tu mundo financiero, *en un solo lugar.*" + URL + aviso. Sin voz. | panel |

**Regla de la metáfora (pedido del user, 04-nov-2026: "que no hablemos de hornos, así no suena repetitivo"):** cada
reel usa una metáfora cotidiana DISTINTA a todas las anteriores. Antes de escribir el guion, leer
`marketing/METAFORAS.md` (registro de las ya usadas, con sus objetos en pantalla) y elegir una familia nueva; al
terminar, agregar la propia al registro en el mismo commit. Prohibido repetir el escenario o los objetos de otra
(panadería, hornos, harina, pan, libreta del fiado ya están usados). La escena de la metáfora del piloto
(`panaderia.html`) NO se copia: se escribe una escena nueva con sus propios objetos animados (mismo nivel de detalle:
algo que llega pesado, algo que se balancea, un contador que termina en el dato con golpe). La metáfora tiene que
explicar el dato real del video, no decorarlo: si el número no se puede trasladar a la metáfora, buscar otra.
Las sesiones en la nube se lanzan DE A UNA: cuatro en paralelo con el modelo grande agotaron el límite de 5 horas a
los 8 minutos (03-nov-2026) y no subieron nada.

Reglas del gancho: el **cuadro 0 es la portada** (título y número ya visibles, nunca negro); prometer en los primeros 10 s algo
que se paga al final; una frase-espejo memorable para el cierre; siempre un dato propio (nuestro informe) que Portiv no tiene.

---

## 3. El guion (lo graba el user)

- Voseo rioplatense ("mirá", "guardalo", "mandáselo"), frases cortas, ~**2,7 palabras por segundo**, 170-190 palabras para ~65 s.
- Números como se dicen ("cincuenta y un mil millones"), y en pantalla la cifra exacta ("US$ 51.355 M").
- Entregar `GUION.md` con: tabla (# · segundo · texto exacto · tono), texto corrido, cómo grabar (sin eco, celular a 15-20 cm,
  de corrido, medio segundo entre frases, si se equivoca repite la frase entera), pronunciaciones raras, texto para la
  publicación de IG con todas las cifras y fuentes, y el disparador de SendPulse. Copia en el Escritorio.
- Ejemplo completo: `plantillas/GUION-ejemplo-google.md`.

---

## 4. Sistema visual (= la web, no inventar)

Fuente de verdad: `assets/aurora/aurora.css` y `bienvenida.html`. Ya volcado en `plantillas/brand.css`:

- Fondos que **se alternan** escena por medio (el borde duro de la transición necesita contraste):
  `.bg-aurora` (navy `#0a1730→#060d1a` con resplandor dorado arriba-izq. y azul a la derecha) y
  `.bg-panel` (navy más claro `#1f3d68→#0b1830`). Siempre `.grid` tenue + `.grain`.
- Texto `#f6f8fc`; dorado `#f2c94c`; champagne `#ead9a4` (rótulos chicos); rojo `#EF4444` = baja; verde `#10B981` = suba.
- Tipografías: IBM Plex Sans 700 (titulares), IBM Plex Mono (todo número), **DM Serif Display cursiva** para la palabra
  acento (como "*Una sola página.*" de la web). Fuentes en `assets/fonts/` (woff2 bajados de Google Fonts).
- Paneles de vidrio `.glass`, pastillas `.pill`, badges `.badge.red/green/gold`.
- Logos: el de la empresa dentro de un **chip** (`.chip` con patitas, placa blanca, SVG oficial del logo — el PNG de
  `assets/logos/` es de 128 px y se pixela). Logo Manfredi: `assets/img/favicon.svg`.
- Zona segura vertical: texto entre y=168 y y=1330; debajo solo decoración (chip, cinta).

---

## 5. Vocabulario de movimiento (medido en Portiv; implementado en `plantillas/brand.js` + escenas)

| Efecto | Cómo se hace |
|---|---|
| **Latigazo vertical** entre escenas | En `index.html`: la escena sale `y:0→-1920` y la nueva entra `y:1920→0`, **0,3 s `expo.inOut`**, ambas a la vez; root con `data-motion-blur="on" data-motion-blur-shutter="300"`. Escenas con 0,34 s de solape. Siempre al terminar una frase. |
| **Odómetro** | `MF.odo(el, ["−",10,1,",",0.1,0.01,"%"])` → `set(v)`; cada dígito rueda en su columna, medio dígito visible al girar; columnas de la izquierda se colapsan si el valor es chico; "." se oculta debajo de 1.000. Brillo con `filter: drop-shadow` en el contenedor (con `text-shadow` aparecen cajas). |
| **Gráfico que se dibuja** | Path SVG reconstruido en `render(t)` con progreso fraccional; punto + etiqueta de precio siguen la punta; la etiqueta pasa a roja en el último tramo; área roja aparece al final. Datos reales. |
| **Caída con impacto** | `fromTo(y:-1800, blur 14px → 0, power3.in, 0.42 s)`, aplaste `scaleY .9` 0,06 s + `elastic.out(1,.45)`. |
| **Se parte** | Dos copias con `clip-path` dentado (`.half-l/.half-r`), se separan ±34 px y rotan ±7°; 4 esquirlas con gravedad. |
| **Flash + temblor** | `MF.flash(tl,"#flash",t)` (bordes rojos o `.flash.gold`) y `MF.shake(tl,"#shake",t,amp)` (6 golpes de 32 ms). |
| **Lluvia escalonada** | Objetos que caen uno detrás de otro (0,22 s entre cada uno) con blur y rebote al apoyar. |
| **La escena se achica** | El grupo anterior `scale .8, y -40` para dar lugar al contador nuevo; o se va arriba con blur. |
| **Karaoke de arriba** | `MF.captions(tl,R,[[sel,tIn,tFin],…])`: cada línea entra con blur 10→0, cada palabra pasa de `#B8943F` a blanco o a su acento (`data-acc="red|green|gold"`, clase `em` = serif cursiva). |
| **Física simple** | Etiquetas que se balancean (`rotation` + `elastic.out(1,.25)`), cartel colgante, cohete que despega/cae. |
| **Cursor que toca** | Flecha SVG que viaja (`power3.inOut`), "tap" `scale .82` y el ícono se llena de dorado. |

Tiempos: llegadas `expo.out`/`back.out(1.6-2.6)`, salidas `power3.in` y más cortas; nada queda quieto más de ~1 s sin un
elemento terminando de acomodarse.

**El bug que más apareció (6 veces):** `fromTo` renderiza su estado inicial desde el segundo 0 de la escena. Todo lo que
"entra" tiene que **arrancar completamente fuera de cuadro** (y ≥ 1200-1800 px, x ≥ 1200) o con `opacity:0`; si el
estado inicial es visible, usar `immediateRender:false`. Revisar siempre el primer segundo de cada escena.

---

## 6. Construcción (HyperFrames)

1. `npx hyperframes init <carpeta> --example blank --resolution portrait --non-interactive --skip-skills --skill hyperframes` dentro de `marketing/`.
2. Copiar `plantillas/brand.css`, `brand.js` a `assets/`, fuentes a `assets/fonts/`, logo a `assets/`, `build_index.py` a la raíz.
3. Cada escena = un archivo en `compositions/` (todo dentro de `<template>`, root `#root`, ids con prefijo propio,
   `window.__timelines["<id>"]`). Partir de la escena del piloto más parecida y cambiar datos y textos.
4. En `build_index.py` poner `SCENES = [(id, segundo_de_entrada), …]` y `END`; `python -I build_index.py` genera `index.html`.
5. `npx hyperframes check --json` (0 errores). Dígitos del odómetro → `data-layout-ignore`; cintas → `data-layout-allow-overflow`.
6. `npx hyperframes snapshot --at <t,…> --no-end -o snapsN` y mirar la hoja de contacto **antes** de renderizar.
7. Render: con FFmpeg de winget en el PATH,
   `npx hyperframes render -o output/<nombre>-vN.mp4 --fps 60 --quality high` (~4 min para 70 s). En segundo plano.
8. **Revisión cuadro a cuadro** (como se analizó Portiv): tiras de cada transición
   `ffmpeg -ss <t-0.1> -i video.mp4 -t 0.42 -vf "fps=36,scale=180:-1,tile=15x1" -frames:v 1 seam.jpg`
   y una vista general a 1 fps. Buscar: objetos que asoman antes de entrar, números cortados, texto encimado.
9. Copiar el mp4 al Escritorio y abrirlo (`start ""`).
10. **El mp4 NUNCA va al repo** (`output/*.mp4` en `.gitignore`): Cloudflare Pages rechaza archivos de más de 25 MiB y
    un reel de 70 s a 60 fps pesa ~28 MB. Pasó con el merge `2f46b99c` (deploy fallido, arreglado en `2177253f`).
    Después de cada merge, verificar el deploy: `curl -s https://api.github.com/repos/manfrediinvestment-pixel/manfredi.investment.com/commits/<sha>/check-runs`
    → "Cloudflare Pages" tiene que estar en `success`, y la página nueva tiene que responder con su propio `<title>`.

---

## 6b. Sonido (lo hacemos nosotros; el user solo pone la voz)

Pedido del user (02-nov-2026): "yo hago la voz, pero no le pongo los sonidos, hacelos vos". Piloto: 73 efectos.

- **Fuentes gratis y sin cuenta** (no invocar la skill `media-use` por el tema HeyGen: usar sus archivos y la API pública):
  biblioteca local `~/.claude/skills/media-use/audio/assets/sfx/` (Pixabay, sin atribución) y Freesound **CC0** vía
  `https://api.openverse.org/v1/audio/?q=<efecto>&license=cc0` (el preview mp3 está en `results[].url`). Openverse limita
  la frecuencia: `curl -m 30`, pocas búsquedas, y si se traba seguir con lo que hay. Ojo: en la biblioteca `whoosh` =
  `whoosh-short` y `click` = `click-soft` (son el mismo archivo).
- Ya armados en el piloto (copiar `marketing/reel-google-caida/assets/sfx/` + `CREDITS.md`): 3 latigazos que rotan
  (`swoosh-a/b/c`), vidrio (`crack-a/b`), golpes graves (`impact-bass-1`, `impact-bass-2` con crecida), `pop`, `click`,
  `key-press`, `ping`, `sparkle`, `notification`, `typing`, `whoosh-cinematic`. Todos normalizados a pico −3 dBTP con ffmpeg.
- **Qué suena** (solo acciones visibles): latigazo en cada transición; golpe grave + vidrio cuando algo se parte o choca;
  pop cuando aterriza un badge o un número; golpes graves bajitos (0,13-0,2) en cada objeto que cae en serie; tecla por
  letra tipeada; clic en cada toque del cursor; notificación cuando llega el DM; golpe con crecida en el remate (nuestro
  valor justo) y en el logo. Nada de música salvo que la pida.
- **Sincronía**: en `build_index.py`, `SFX = [(archivo, escena, segundo_local_del_cuadro, volumen, extra)]`, `PEAK` (pico
  medido con `npx hyperframes audio <archivo> --only moments --json`) y `DUR`. El script calcula
  `inicio = escena + segundo − pico + 1 cuadro`, pone `data-duration` (sin eso el audio "ocupa" hasta el final y el lint
  tira cientos de avisos) y reparte en pistas 30+ sin superposición. Al cambiar los tiempos de escena por la voz, los
  sonidos se mueven solos.
- **Verificar midiendo** (no se puede escuchar): `npx hyperframes audio output/<video>.mp4 --only loudness,onsets --json`
  → mezcla −16 a −14 LUFS, pico ≤ −1 dBTP, y cada onset fuerte a ±1-2 cuadros de su imagen. Cuando entre la voz, bajar
  los efectos ~6 dB para que queden debajo.

## 7. Sincronizar con la voz del user

Cuando pase el audio:
1. `faster_whisper` (modelo `small`, `language="es"`, `word_timestamps=True`) → tiempo de cada palabra.
2. Para cada escena, el segundo de entrada = inicio de su primera frase (la transición cae justo al terminar la frase anterior).
   Actualizar `SCENES`/`END` en `build_index.py`.
3. Dentro de cada escena, los tiempos de `MF.captions(...)` son **locales** (segundo de la escena): reemplazarlos por los de
   las palabras; si una escena se estira o encoge, escalar sus tweens con `tl.timeScale` o mover los marcadores clave.
4. Agregar el audio como `<audio id="voz" src="assets/voz.m4a" data-start="0" data-volume="1">` en el root, y normalizar a
   −14 LUFS (`ffmpeg -af loudnorm=I=-14`). Portiv: voz continua, sin silencios, −17 LUFS.

---

## 8. Comentá PALABRA → guía → informe

1. **Informe**: si el informe del ticker es de un trimestre anterior, actualizarlo con la skill del sector
   (`informe-bigtech`, `informe-bancos`, …) — el que comente la palabra tiene que recibir datos al día. Regenerar
   `node scripts/catalogo-informes.mjs`, entrada nueva al principio de `informes/manifest.json`, tarjeta del picks-list.
2. **Guía**: copiar `plantillas/guia-ticker.html` a `guia-<ticker>.html` (raíz → `manfredinvestment.com/guia-<ticker>`).
   Portada con 4 datos verificados + valor justo **borroso** (en el informe está detrás de la membresía), 3 datos del
   video, 3 pasos (cuenta gratis `/?registro=1` → abrir `/informes/<ticker>` → Pro `/?membresia=1`, USD 15/mes salvo
   promo vigente en `MI_PROMO`), índice de las 14 secciones (la 03 es gratis), frase espejo, aviso legal.
   Probar en Chrome headless a 500 px de ancho (por debajo de ~500 la captura sin ventana sale cortada aunque la página esté bien).
3. **SendPulse** (ver memoria `reference_sendpulse_instagram_bot`): disparador "Comentario en tu publicación → PALABRA"
   (contiene, cualquier publicación), mensaje + botón "Quiero la guía" → filtro "sigue tu página" → botón URL "Ver la guía".
   **Prenderlo recién cuando la guía esté en vivo** (después del merge + push).

---

## 8b. Modo nube (Claude Code en la web / rutinas)

Probado el 03-nov-2026 en el entorno `env_01DMYtiRM7Vk37xoE5mPdX5L` (Linux, 4 núcleos): ya vienen Node 22, Python 3.11,
**ffmpeg** y **Chrome** (`/usr/bin/google-chrome`), hay `sudo`, y `npx -y hyperframes@0.9.4` se instala desde npm.
La red está **restringida**: pasan npm, PyPI y Anthropic; están BLOQUEADOS jsDelivr, Yahoo Finance, la SEC, Openverse
y manfredinvestment.com. Si el user pasa el entorno a acceso "Completo", ignorar las restricciones de abajo.

- **GSAP**: nunca desde CDN. Copiar `plantillas/vendor/gsap.min.js` a `assets/gsap.min.js` (el `build_index.py` de
  plantillas ya lo carga de ahí). Las fuentes ya son locales (`assets/fonts/`). Ningún `<script>` o `<link>` externo.
- **Sonido**: copiar `plantillas/sfx/` a `assets/sfx/` (no buscar en Openverse).
- **Datos**: la fuente principal es **nuestro informe** `informes/<ticker>.html` (cifras del 8-K, valor justo, precio de
  referencia). Para la reacción de la acción, cierres diarios y ranking histórico, usar **WebSearch / WebFetch** (corren
  fuera del sandbox): p. ej. WebFetch a `https://query1.finance.yahoo.com/v8/finance/chart/<TICKER>?period1=...&interval=1d`
  o a stockanalysis.com / la web de relaciones con inversores. Nada de `curl` a Yahoo/SEC desde Bash.
- **Render**: `npx -y hyperframes@0.9.4 render -o output/<nombre>.mp4 --fps 30 --quality high` (en la nube, 30 fps para
  que no tarde). Si el render no encuentra navegador, revisar `npx hyperframes render --help` para indicar
  `/usr/bin/google-chrome`.
- **Revisión sin ver**: `npx hyperframes snapshot --at <tiempos> -o snaps` y leer las imágenes con Read; tiras de
  ffmpeg como en la sección 6.
- **Entrega**: no hay Escritorio. Comprimir a menos de 20 MB
  (`ffmpeg -i output/x.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k entrega/<ticker>-reel.mp4`), guardar en
  `marketing/<proyecto>/entrega/` y commitearlo **solo en la rama del video** (nunca mergear ese mp4 a main: al traer la
  rama a la PC se copia al Escritorio y se borra del repo antes de mergear). Commitear también `GUION.md` y el proyecto.
- **Guía y palabra**: crear `guia-<ticker>.html` desde `plantillas/guia-ticker.html` en la misma rama. El disparador de
  SendPulse NO se puede crear desde la nube (necesita el Chrome del user): dejarlo anotado en `GUION.md`.
- **Mensaje final de la sesión**: rama, commit, ruta del mp4, palabra para comentar, y cualquier dato que no se pudo
  verificar.

## 9. Entregables y cierre

- `marketing/reel-<ticker>-<evento>/` con `SPEC.md` (datos y fuentes), `GUION.md`, `build_index.py`, escenas, `output/*.mp4`.
- Informe actualizado + guía + manifest + catálogo, todo en la misma rama.
- Video y guion en el Escritorio. Avisar que la rama está lista para revisar; **no mergear sin OK**.
- Pendiente para el user: grabar la voz, prender el disparador cuando esté en vivo.
