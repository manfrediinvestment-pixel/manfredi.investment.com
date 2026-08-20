---
name: reel-informe
description: "Use when the user asks for a video/reel version of an existing equity research report from `informes/<ticker>.html` (skill informe-bigtech) — a vertical (1080x1920) Reels/TikTok/Instagram video with 5 analysis blocks, brand banner, and closing card. Trigger on minimal instructions: 'reel de [ticker]', 'video de [ticker]', 'hacé el video del informe de [ticker]', 'segui con el reel de [ticker]' — no further explanation from the user is needed, this skill carries the full format (script structure, visual system, motion, banner, closing) established in the NVDA pilot episode. Requires `informes/<ticker>.html` to already exist; if it doesn't, offer to run informe-bigtech first."
metadata:
  version: 1.0.0
---

# Reel de informe — serie semanal de video para Manfredi Investment

Producís el episodio de video de la serie semanal de análisis de acciones para
manfredinvestment.com, a partir de un informe institucional ya publicado en
`informes/<ticker>.html`. El formato completo — guion, sistema visual, animación,
banner de marca y cierre — ya está diseñado y aprobado por el usuario en el episodio
piloto (NVDA). Tu trabajo es **aplicarlo**, no reinventarlo.

**Referencia canónica — el episodio piloto completo vive en `marketing/reel-informe-nvda/`.**
Cuando tengas dudas de formato, layout, timing o motion que esta skill no cubra en
detalle, abrí ese proyecto y copiá el patrón de ahí (`frame.md`, `STORYBOARD.md`,
`index.html`, `compositions/*.html`) en vez de improvisar. `references/block-templates.md`
en esta skill señala exactamente qué archivo copiar para cada tipo de bloque.

## Invocación mínima

El usuario puede pedir esto con una sola palabra o frase corta: "reel de MU", "video de
INTC", "hacé el reel de AVGO". No hace falta que reexplique el formato — sabés todo lo
que sigue. Si falta `informes/<ticker>.html`, avisá y ofrecé correr `informe-bigtech`
primero (no lo inventes vos).

## El proceso, de punta a punta

1. **Leé el informe completo** (`informes/<ticker>.html`) — todas las secciones, no solo
   el resumen ejecutivo. Necesitás datos reales para el guion y los gráficos; nunca
   inventes una cifra.
2. **Elegí los 5 puntos** del episodio (ver criterio abajo).
3. **Escribí el guion**: para cada punto, un título corto de 2-4 palabras (para el
   bumper) + una línea de narración en español rioplatense, tono directo, sin jerga
   innecesaria — mirá el guion de NVDA en `marketing/reel-informe-nvda/STORYBOARD.md`
   como calibre de largo y registro. Mostrale el guion completo al usuario y esperá el
   OK antes de tocar código — así arrancó el episodio piloto y funcionó bien.
4. **Creá la rama** `feat/reel-informe-<ticker-minúscula>` desde `main` (nunca desde
   otra rama de trabajo en curso — puede tener commits ajenos sin relación).
5. **Scaffoldeá el proyecto**:
   ```
   npx hyperframes skills update general-video
   cd marketing
   npx hyperframes@latest init reel-informe-<ticker> --example=blank --resolution=portrait --skill=general-video --non-interactive
   ```
6. **Copiá los assets reusables** (no los reconstruyas — ver tabla de "Assets
   reusables" abajo) a `assets/fonts/`, `assets/img/`, `assets/video/` del proyecto
   nuevo.
7. **Escribí `frame.md`** — copiá el de `reel-informe-nvda/frame.md` casi literal
   (mismo sistema de color/tipografía/movimiento); el único ajuste real por ticker es
   si el relato pide una paleta de "alerta" en algún bloque (ver sección de color más
   abajo) — eso ya está resuelto, no hace falta rediseñar nada.
8. **Escribí `BRIEF.md`** (`workflow: general-video`, `flow: companion`,
   `storyboard: yes`) y **`STORYBOARD.md`** con un Frame por bloque — mismo formato que
   el de NVDA, con el guion de este ticker.
9. **Construí bloque por bloque, no todos de una** salvo que el usuario pida
   explícitamente "hacé todo de una". Para cada bloque:
   - Elegí la forma visual (ver "Menú de bloques" abajo) según qué tipo de dato es.
   - Copiá el composition file más parecido de `reel-informe-nvda/compositions/` como
     punto de partida, adaptá números/textos/colores.
   - Wireálo en `index.html` (nuevo slot, `data-start` = fin del bloque anterior).
   - Corré `npx hyperframes check` — 0 errores antes de seguir.
   - Sacá 4-6 `npx hyperframes snapshot --at ...` a lo largo del bloque y mirálos —
     el check NO detecta todo (ver "Bugs ya cazados" abajo, varios solo se ven a ojo).
   - Renderizá el video acumulado hasta ese bloque y abrilo (`start ""`) para que el
     usuario lo vea.
   - Commiteá ese bloque solo, con mensaje descriptivo.
   - Esperá confirmación del usuario antes del próximo bloque (salvo pedido explícito
     de seguir de una — en ese caso construí todos y renderizá al final de cada uno
     igual, pero sin pausar el chat entre medio).
10. **Agregá el banner de marca persistente** (logo + "Manfredi Investment" +
    "manfredinvestment.com", fijo abajo de todos los bloques de análisis) y el
    **cierre de marca** (reusa el mp4 ya renderizado, no lo reconstruyas) — ver
    `references/block-templates.md` § Banner y § Cierre para el snippet exacto.
11. El **hook inicial** (los primeros segundos) y la **cámara de cierre** los graba el
    usuario aparte — nunca son parte de lo que vos construís. Dejá un comentario en
    `STORYBOARD.md` marcando dónde van.

## Criterio para elegir los 5 puntos

No hay una lista fija de 5 temas — depende del informe — pero el arco que mejor
funcionó (NVDA) fue:

1. **El resultado / hook numérico** — el dato más grande y reciente del informe
   (ingresos, crecimiento, el titular del último trimestre).
2. **El modelo de negocio o la tesis central** — lo que hace a esta empresa distinta
   de sus comparables (de la sección "Modelo de Negocio y Segmentos" o el resumen
   ejecutivo del informe).
3. **Balance / capital allocation** — deuda, caja, recompras, dividendos: la salud
   financiera contada con un número contundente.
4. **Un riesgo real** — de la sección "Registro de Riesgos", elegí el que tenga más
   sustancia (no el genérico), idealmente con una cifra propia.
5. **La valuación** — el fair value del informe vs. el precio de mercado. Si el
   informe tiene matices entre métodos (como NVDA: DCF riguroso vs. blend optimista),
   ESE matiz es el mejor cierre posible — la nota da postura "razonable" en vez de venta
   fácil de "comprá ya", y eso construye más confianza que un titular ciego.

Si el sector no es big tech/semis (banco, energía, defensiva), el criterio se adapta
pero la estructura (hook → modelo → balance → riesgo → valuación) generalmente sigue
sirviendo — usar juicio.

## Sistema visual (no rediseñar — ya está resuelto)

Fondo navy con gradiente radial (nunca plano): `#0A0F1E`/`#07101E`/`#050810`, con un
tono navy más brillante `#1B3A6B` en el centro superior de cada escena. Acento dorado
`#F2C94C`/`#FFE28A` para crecimiento/positivo. Acento azul eléctrico `#4F8FE8`/`#7EB3FF`
para datos comparativos/neutrales. **Acento ámbar `#FFA53D`/`#FFC98A`** — paleta
alternativa reservada para el bloque de riesgo, para marcar el cambio de registro a
"cuidado" sin salirse de la marca. Tipografía: `DM Serif Display` (numerales/hero,
`@font-face` local, ver assets) + `IBM Plex Mono` (todo dato/label, bundled, no
necesita `@font-face`) — nunca uses `IBM Plex Sans` ni ninguna otra familia para texto
visible, dispara `font_family_without_font_face`.

**Mandato de brillo (aplica siempre, pedido explícito del usuario del piloto):**
"muchísima calidad de imagen, con brillo y que resalte todo, no quiero nada oscuro, ni
azules apagados" — glow fuerte (`ambient-glow-bloom` a 0.30-0.45 de opacidad, nunca
0.15), nunca un fondo sólido de un solo tono, texto blanco puro sobre navy profundo.

## Menú de bloques (qué forma visual usar según el dato)

| El dato es...                                      | Copiá de (`reel-informe-nvda/compositions/`) | Forma                                              |
| --------------------------------------------------- | --------------------------------------------- | --------------------------------------------------- |
| Una serie temporal (ingresos/trimestres)             | `frame2-block1-trimestre.html`                | Barras verticales, la más reciente dorada con glow  |
| Una comparación de 2 magnitudes (A vs. B, % o $)     | `frame3-block2-modelo.html`                   | Barras horizontales (una corta+dorada, otra banda)  |
| 2-3 cifras paralelas sin relación entre sí           | `frame4-block3-capital.html`                  | Stat cards con contador propio cada una             |
| Una lista de 2-4 ítems cualitativos (riesgos, hitos)  | `frame5-block4-riesgo.html`                   | Lista vertical con marcador + descripción           |
| Un número que se matiza/contradice a sí mismo         | `frame6-block5-valuacion.html`                | Dos actos: hero grande → "— PERO —" → comparación   |

Todos comparten el mismo esqueleto de bumper (numeral gigante + título + shrink a
header fijo) y el mismo patrón de cámara (`push-in` sutil todo el bloque) — copiá eso
literal, cambiá solo el contenido central. El detalle completo de cada patrón está en
`references/block-templates.md`.

## Bugs ya cazados — no los repitas

- **`&nbsp;` entre `<span>` no cuenta para `:nth-child`** — si separás palabras de un
  título con `&nbsp;`, el segundo `<span>` es `:nth-child(2)`, no `:nth-child(3)`. Ya
  pasó una vez (el segundo word nunca aparecía).
- **Glow del numeral vs. título multi-palabra**: `.bumper-title { margin-top: 96px;
  max-width: 920px; font-size: 42px; }` aguanta hasta 4 palabras sin overlap ni
  overflow — usalo siempre, no empieces en 64px y vayas subiendo.
- **Cualquier elemento decorativo que viva por encima del bumper en el DOM** (una
  pista de gráfico vacía, por ejemplo) necesita `opacity: 0` inicial explícito, si no
  se ve flotando arriba de pantalla durante la fase de bumper.
- **Labels/subtextos secundarios necesitan mínimo `rgba(255,255,255,.7-.75)`** de
  color sobre el fondo navy para pasar contraste WCAG AA — `.5` falla, ya pasó dos
  veces (`4.08:1`, se necesita `4.5:1`).
- **Nunca muestres el año fiscal de la empresa en pantalla** (ej. "Q1 FY27" de
  NVIDIA) — un año fiscal adelantado al calendario se lee como año futuro y confunde.
  Convertí siempre a fecha calendario real: mes abreviado + año de cierre real del
  trimestre (ej. "ABR '26"), sacado del propio informe (dice el cierre real en cada
  tabla, ej. "trimestre cerrado 26-abr-2026").
- **Nombrá el bloque por el dato que muestra, no por un genérico.** "El trimestre" se
  corrigió a "Ingresos" porque el contenido era específicamente sobre crecimiento de
  ingresos — el título del bumper tiene que decir qué es el número, no cuándo.
- **`google_fonts_import` warning**: nunca uses `<link href="fonts.googleapis.com...">`
  — declará `@font-face` local apuntando a un `.woff2` en `assets/fonts/` (ver
  siguiente sección), y repetí el mismo `@font-face` DENTRO de cada sub-composición
  que use esa fuente, no solo en `index.html` (el lint lo pide por archivo).
- **Rutas de assets nunca con `../`** fuera del proyecto (`invalid_parent_traversal_in_asset_path`)
  — copiá el asset adentro del proyecto nuevo, nunca referencies `marketing/otro-proyecto/...`
  directo.
- **Working directory compartido**: este repo puede tener otra sesión de Claude Code
  trabajando en paralelo en la misma carpeta — si un `Read`/`Edit` falla con "File
  does not exist" sobre un archivo que vos mismo escribiste segundos antes, no entres
  en pánico ni asumas pérdida de datos: corré `git branch --show-current` y
  `git reflog -10`, probablemente cambió de rama otra sesión y ya volvió. Commiteá
  seguido (por bloque) para minimizar la ventana de riesgo.

## Assets reusables (copiar, nunca reconstruir)

| Asset                                    | Fuente canónica                                                                                          | Destino en el proyecto nuevo         |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Fuente DM Serif Display                   | `marketing/reel-informe-nvda/assets/fonts/dm-serif-display.woff2`                                            | `assets/fonts/dm-serif-display.woff2`    |
| Logo real de la marca                     | `assets/img/logo-source.png` (raíz del repo — el sitio real)                                                 | `assets/img/logo-source.png`             |
| Cierre de marca ya aprobado (con audio)   | `marketing/reel-informe-nvda/assets/video/outro-manfredi-brand.mp4` (5s, 1080x1920, sting de audio incluido) | `assets/video/outro-manfredi-brand.mp4`  |

Si el usuario aprueba una versión nueva del cierre de marca en el futuro, actualizar
esta tabla y el archivo canónico — hasta entonces, este es el cierre de toda la serie.

## Estructura final de `index.html` (orden de montaje)

1. Frame de preview (headline "N CLAVES DE [TICKER]" + lista de los N títulos que
   siguen) — copiá `frame1-preview.html`, cambiá los N títulos.
2. Un frame por cada uno de los 5 bloques (10s cada uno es el default que funcionó;
   ajustable si el guion de un bloque necesita más aire).
3. Banner de marca persistente — elemento root-level (`data-track-index="20"`, por
   encima de todas las escenas), `data-start="0"`, `data-duration` = hasta el final de
   los bloques de análisis (antes del cierre). Snippet exacto en
   `references/block-templates.md` § Banner.
4. (Hueco para el Frame de cámara del usuario — no lo construís vos, solo dejalo
   anotado en `STORYBOARD.md` con el `data-start` correcto una vez que sepas cuánto
   dura la toma real.)
5. Cierre de marca — `<video muted>` + `<audio>` separados apuntando al mismo mp4
   copiado, `data-start` = fin de todo lo anterior, `data-duration="5"`.

## Al terminar cada bloque

Correr `npx hyperframes check` (0 errores obligatorio, warnings de
`composition_self_attribute_selector` son aceptables y esperables), sacar snapshots,
renderizar el acumulado, abrirlo con `start ""`, commitear ese bloque solo. No declares
un bloque terminado sin haber mirado el snapshot con tus propios ojos — el check
automático no cachea overlaps de glow ni bugs de selector como el de `:nth-child`.
