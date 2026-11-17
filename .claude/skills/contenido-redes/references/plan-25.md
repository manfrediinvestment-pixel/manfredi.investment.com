# Plan 25 — 25 videos por semana hasta fin de 2026

Arrancó el lunes 16-nov-2026. Termina el 31-dic-2026 (7 semanas: 16-nov, 23-nov,
30-nov, 7-dic, 14-dic, 21-dic, 28-dic; las 2 últimas son de fiestas, se mide
igual pero sin exigir 25).

## La regla del sistema

El user estudia en bloques de 1:30 + 30 min de descanso. **Los videos se graban
en los descansos** (1-2 por descanso). O sea: el costo de producción tiene que
ser casi cero. Nada de edición pesada: cámara, un gráfico o captura de fondo,
texto en pantalla, subir. Si una idea necesita más de 15 minutos entre grabar y
subir, NO va en las 5 del día (va al backlog de @manfredinvestment).

## Los 5 videos del día (lunes a viernes)

| Slot | Tipo | De dónde sale | Cómo se hace |
|------|------|---------------|--------------|
| 1 | **Informe** | Una acción de `informes/` (rotar; priorizar la que reporta esa semana o la que se movió fuerte) | Skill `reel-informe` o a cámara con la tapa del informe de fondo |
| 2 | **Dato del día** | Calendario económico (INDEC, BCRA, CPI, Fed, empleo) o evento clave | A cámara + gráfico del dato. Fuente oficial siempre |
| 3-5 | **Libres** | Noticia clave del día · gráfico visto en X/Twitter · responder un comentario | A cámara, green screen con la captura, o "respuesta a comentario" nativa de TikTok |

Prioridad dentro de los libres: (a) responder comentario (es el que más
retiene y es gratis de idear), (b) noticia que divide (Milei, dólar, inflación
— ver `aprendizajes.md`), (c) gráfico de X.

## Dónde se sube

| Cuenta | Qué va | Frecuencia |
|--------|--------|-----------|
| TikTok **@ignacio.manfredi** | Los 25 | 5/día |
| IG **@nacho.finanzas** — Reels de prueba (trial reels, solo a no-seguidores) | Los 25 | 5/día |
| IG **@nacho.finanzas** — feed normal | Los **3 mejores de la semana** (por vistas normalizadas en TikTok + prueba) | 3/semana, el finde o lunes |
| IG **@manfredinvestment** | 1 **historia cinematográfica** de lo que se construye (sale del Cerebro: lo construido esa semana) + 1 **Pro** (poder de Warren IA o de los informes, grabación de la web real: skill `video-pagina-real` / `hyperframes`) | 2/semana |

## KPIs (en este orden de importancia)

1. **Clientes**: socios pagos nuevos en la semana (Panel de creador → Membresía/Ingresos).
2. **Registros** nuevos en la web (Panel → Usuarios).
3. **Visitas** a la web (Panel → Tráfico, visitas reales sin bots).
4. **Seguidores**: TikTok @ignacio.manfredi, IG @nacho.finanzas, IG @manfredinvestment (Δ semanal).
5. **Vistas** totales de la semana (TikTok Studio + IG Insights) y **mediana por video**.
6. **Cumplimiento**: videos subidos / 25.

Vanidad vs. negocio: si suben vistas y seguidores pero no visitas ni registros,
el problema es el CTA / link en bio / disparador de SendPulse, no el contenido.
Decilo así en el recap.

## Base de datos del Cerebro (colecciones)

Artifact: https://claude.ai/artifact/9VzNXtN7aqAygfAkE6cuP1 — se escribe con
`ArtifactData` (cargarla con ToolSearch). La pestaña **Contenido** del Cerebro
lee todo esto en vivo.

### `contenido_meta/plan`
```json
{"inicio":"2026-11-16","fin":"2026-12-31","metaVideosSemana":25,
 "cuentas":{"tiktok":"@ignacio.manfredi","ig":"@nacho.finanzas","igMarca":"@manfredinvestment"},
 "base":{"fecha":"AAAA-MM-DD","tiktokSeg":0,"igSeg":0,"igMarcaSeg":0,"visitas30d":0,"socios":0},
 "metas":{"tiktokSeg":0,"igSeg":0,"igMarcaSeg":0,"visitasSemana":0,"sociosNuevos":0}}
```

### `contenido_semanas/<AAAA-MM-DD del lunes>`
```json
{"lunes":"2026-11-16","n":1,
 "videos":0, "vistas":0, "medianaVistas":0,
 "tiktokSeg":0, "igSeg":0, "igMarcaSeg":0,
 "visitas":0, "registros":0, "sociosNuevos":0,
 "top":[{"titulo":"","red":"tiktok","vistas":0,"url":""}],
 "funciono":["regla corta con evidencia"], "noFunciono":["..."], "ajustes":["qué cambiamos la semana que viene"],
 "fuente":"Chrome: TikTok Studio + IG Insights + Panel", "cerrada":false}
```
Números que no se pudieron leer: `null` (nunca inventar).

### `contenido_dias/<AAAA-MM-DD>`
La pauta del día: 5 slots (+ opcionales de marca).
```json
{"fecha":"2026-11-17","slots":[
  {"tipo":"informe|dato|noticia|grafico|comentario|marca-historia|marca-pro",
   "titulo":"", "gancho":"pregunta corta para los primeros 2 s",
   "puntos":["3 frases para decir"], "cta":"comentá INFORME…", "pantalla":"qué se ve de fondo",
   "fuente":"url", "grabado":false, "subido":false, "url":""}],
 "generado":"claude-code|cerebro"}
```
El user tilda "grabado" y "subido" desde el Cerebro: eso alimenta el contador
de la semana. En el recap, `videos` = cantidad de slots con `subido:true` en
los días de esa semana (y se contrasta con TikTok Studio).

### `contenido_ideas/<id>` — banco de ideas
Lo que el Cerebro muestra de a 5 ("Ver 5 más"). Tocar una idea la pone en el
primer video de la pauta que no esté grabado; "↻ Cambiar" en un video la
cambia por la próxima del banco (mismo tipo si hay). La idea que sale vuelve
al banco. **Cada idea tiene que traer `fuente` con el link real** (el user saca
de ahí el gráfico o la captura). Id: `AAAA-MM-DD-<slug>`.
```json
{"fecha":"2026-11-16","tipo":"noticia|dato|grafico|comentario|informe",
 "titulo":"tema en 5 palabras","gancho":"pregunta para los 2 primeros segundos",
 "puntos":["3 frases para decir"],"pantalla":"qué se ve de fondo","cta":"cierre",
 "fuente":"https://…","usada":false}
```
Las ideas que ya están en la pauta llevan `usada:true`. Las de más de 4 días
sin usar se borran en el modo Hoy (dejar como máximo ~25 en el banco).

### `contenido_diario/<AAAA-MM-DD>` — foto diaria para los gráficos
Al tocar un KPI del Cerebro se abre un gráfico Diario / Semanal de esto.
```json
{"tiktokSeg":4379,"tiktokLikes":222400,"igSeg":null,"igMarcaSeg":140,
 "visitas":null,"registros":null,"sociosNuevos":null,"fuente":"Chrome: perfiles públicos"}
```
Seguidores = foto del día (stock). Visitas, registros y socios = lo del día
(flujo; el gráfico semanal los suma). Nunca inventar: lo que no se leyó, `null`
o no se escribe.

## Modo HOY — "contenido hoy", "ideas de hoy", "qué grabo hoy"

Objetivo: en < 5 minutos de lectura, el user tiene las 5 piezas del día listas para grabar.

0. **Foto diaria**: leer seguidores de TikTok (perfil público, screenshot + zoom), IG personal y @manfredinvestment (`get_page_text` del perfil) y escribir `contenido_diario/<hoy>`.
1. **Banco** (cargar cada noticia/dato/comentario como idea completa en `contenido_ideas`, con link; borrar las de > 4 días sin usar):
   - Noticias y datos de HOY: WebSearch (mode standard) en paralelo: "mercados hoy argentina", "dólar hoy", "Wall Street hoy", "INDEC hoy" / "BCRA", y lo que diga el calendario de la semana (`marketing/calendario` o el KV `eventos_semana`, ver memoria de la semana). Solo fuentes con fecha de hoy o ayer.
   - Earnings de la semana de tickers con informe (sale del calendario).
   - Noticias: la fuente más rápida y fresca es el worker propio `curl -s https://manfredi-noticias.nachito2502.workers.dev/noticias` (claves `argentina` y `wallstreet`, con fecha y link). WebSearch casi no trae notas fechadas en 2026. El calendario de la semana está en `~/Documents/semana_<dd>_<dd>_{calendario,earnings}.json` (lo deja la skill calendario-semanal; ojo, a veces está en cp1252).
   - **Comentarios y DMs**: Chrome → TikTok Studio → Comentarios, y notificaciones de IG @nacho.finanzas. Elegir 3-5 comentarios con pregunta respondible (no insultos, no pedidos de "qué compro"). Solo lectura: nunca responder, likear ni mandar DMs desde Chrome.
   - **Lo que se construyó**: `git log origin/main --since="7 days ago" --merges --oneline` + array `S` del Cerebro → material para la historia cinematográfica de @manfredinvestment.
2. **Pauta**: escribir `contenido_dias/<hoy>` con los 5 slots elegidos del banco (cada slot con `ideaId` y la idea marcada `usada:true`) (1 informe, 1 dato, 3 libres). Cada slot: gancho como PREGUNTA (regla de `aprendizajes.md`), 3 puntos para decir, CTA, qué poner de fondo y la fuente. Los martes y viernes sumar 1 slot `marca-*` para @manfredinvestment.
3. En el chat: solo la tabla de los 5 (tipo · gancho · fondo) y el link al Cerebro. Los detalles quedan en el Cerebro.

Reglas: todo número con fuente y fecha; **nunca decir el fair value ni el precio objetivo en un video** (regla de marketing del user: el cierre manda a comentar INFORME); nunca "comprá X"; cierre "no es recomendación de inversión". Respetar [[feedback_no_mostrar_composicion_cartera]]: rendimientos de la cartera sí, pesos no.

## Modo SUBÍ — "subí el de X", "ya subí 3", pegar links

Marcar `subido:true` (+ `url`) en `contenido_dias`. Si el user sube algo fuera de pauta, agregarlo como slot nuevo. Una línea de confirmación con el contador de la semana (`N/25`).

## Modo RECAP — "recap", "recap semanal", "cómo vamos"

Correr el viernes a la noche o el lunes temprano. Chrome con la sesión del user (cargar skill `claude-in-chrome`):

1. **TikTok Studio** → Analytics → últimos 7 días: vistas, seguidores, Δ seguidores; Contenido → vistas por video.
2. **IG @nacho.finanzas** → Panel profesional → Insights 7 días: cuentas alcanzadas, seguidores, reels (incluye reels de prueba) con reproducciones.
3. **IG @manfredinvestment** → igual (cambiar de cuenta solo si el user ya la tiene agregada; si no, pedir captura).
4. **manfredinvestment.com/#panel** (Panel de creador) → visitas 7 días, usuarios nuevos, socios/ingresos.

Después:
- Guardar snapshot en `marketing/contenido-redes/metricas/AAAA-MM-DD-semana-N.md` y el doc `contenido_semanas/<lunes>` (con `cerrada:true`).
- Top 3 por vistas normalizadas (vistas / mediana de la semana) → son los que van al feed de @nacho.finanzas. Decirlo explícito.
- 2-3 `funciono`, 2-3 `noFunciono`, 2-3 `ajustes` (cambios concretos para la semana que viene: qué tipo de slot reforzar, qué gancho repetir, qué slot sacar). Pasar las reglas firmes a `aprendizajes.md`.
- Embudo: vistas → seguidores → visitas → registros → socios. Señalar el escalón que se rompe.
- Si Chrome no está conectado: pedir 4 capturas (TikTok Analytics, IG Insights x2, Panel) y leerlas con Read.

## Modo PLAN — "cómo vamos con el plan", fin de mes / fin de año

Tabla de las semanas cerradas + proyección lineal al 31-dic contra las metas de `contenido_meta/plan`. Si el cumplimiento es < 60% dos semanas seguidas, proponer bajar a 4 por día antes que abandonar.

## Estado de las fuentes (16-nov-2026)

- TikTok perfil público: Chrome lo lee (screenshot + zoom). 16-nov: 4.379 seguidores, 222,4K likes.
- TikTok Studio: FUNCIONA desde el 17-nov (el user dio el permiso desde el panel de la extensión). `get_page_text` en tiktok.com/tiktokstudio/comment trae todos los comentarios con el video al que responden; Home trae vistas, visitas al perfil, likes, comentarios y compartidos de 7 días.
- Instagram: FUNCIONA desde el 17-nov. Perfiles con `get_page_text`; panel profesional `instagram.com/accounts/insights/?timeframe=7` solo con screenshot + zoom (vistas, % no seguidores, espectadores, top 5). IG personal = @nacho.finanzas. @manfredinvestment 16-nov: 140 seguidores, 17 posts.
- Panel de creador: en Chrome está logueada otra cuenta, no la creadora → no se ve. Si sigue así, pedir captura del Panel o que inicie sesión con la cuenta creadora en ese Chrome.

## Metas al 31-dic-2026 (las puso el user el 17-nov)

- TikTok @ignacio.manfredi: **10.000 seguidores** (arranque 4.379 → +5.621, ~128/día).
- IG @nacho.finanzas: **10.000 seguidores** (arranque 3.137 → +6.863, ~156/día).
- **1 socio pago de Manfredi Pro.**

En cada recap, comparar el ritmo real contra el necesario y decirlo sin suavizar. Para crecer así hacen falta videos que se escapen (100K+ vistas), no solo constancia: priorizar los formatos que ya demostraron eso (pregunta que divide + Milei/dólar/inflación). Para el socio: cada video con CTA a un recurso gratis de la web (comentá INFORME → DM de SendPulse), nunca venta directa en el video.
