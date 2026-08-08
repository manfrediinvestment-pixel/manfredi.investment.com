# Sistema de carruseles diarios — Instagram

Formato v3 aprobado por el fundador el 2026-08-08, tras dos rechazos anteriores. Referencia canónica: `carousel-v2-nvda/` (el nombre de la carpeta quedó de una versión anterior — el contenido adentro es siempre el v3 vigente). Cualquier carrusel nuevo debe reusar este sistema visual EXACTO — no reinventar el diseño cada vez, y no revertir a versiones anteriores.

**Historial de rechazos, para no repetir los mismos errores:**
- v1 (rechazada): placas con solo texto/títulos, sin gráficos de datos reales. El fundador: "no quiero simples títulos y listo, que aporten valor".
- v2 primer intento (rechazado): gráficos con barras grises azuladas y una textura de líneas horizontales de fondo en toda la placa. El fundador: "la calidad de las imágenes son una vergüenza... saca los cuadraditos del fondo, las líneas esas".
- v2 segundo intento (aceptable pero no aprobado del todo): sin grilla, barras píldora con degradé dorado. Mejor, pero el fundador pidió explícitamente que se usara un proceso de diseño real ("usá Claude design... en esa imagen no se ve eso") en vez de CSS genérico con paleta de fintech.
- **v3 (aprobada, es la vigente):** concepto "Research Desk" — tipografía editorial real (no system fonts), sistema de "ledger" financiero en vez de tarjetas de dashboard, folios de página en vez de dots de progreso, watermark tipográfico del ticker en la portada. El fundador: "esto sí es lo que quería, me parece grandioso". **No volver a ningún sistema anterior. No usar barras tipo píldora con degradé ni gridlines de fondo.**

## Qué es esto

Un carrusel de 5 placas (1080×1350 px, formato feed 4:5) que analiza UN activo financiero, usando **datos reales extraídos del informe institucional de ese ticker** en `informes/<ticker>.html`. Nunca se inventan cifras ni se usan gráficos decorativos sin datos detrás.

## El concepto v3: "Research Desk"

Cada placa se trata como una página de un informe institucional impreso, no como una pantalla de app:

- **Masthead** en la parte superior de cada placa (excepto la portada, que tiene su propio header): `Manfredi Investment — Research Desk` a la izquierda, `N.° XXX` (número de informe, arbitrario pero consistente dentro del mismo carrusel) a la derecha, en mono, separado por una línea fina.
- **Portada (placa 1):** el ticker en gigante como marca de agua tipográfica de fondo (`-webkit-text-stroke`, sin relleno, muy baja opacidad — NUNCA un logo real bajado de internet), headline editorial en serif con la palabra clave en cursiva dorada, y un índice tipo tabla de contenidos (no chips/pills) con los temas de las placas siguientes.
- **Gráficos como "ledger" financiero, no dashboard:** filas finas con el nombre del método arriba, el valor en cifra grande en serif *cursiva*, y una barra delgada (no píldora gruesa) debajo. Para gráficos verticales, barras rectangulares con esquina superior apenas redondeada (3-4px, no 14px+), valor en serif cursiva arriba de la barra.
- **Sin gridlines, sin textura de fondo.** Si hace falta una referencia (ej. precio de mercado), una única línea fina con una etiqueta chica — nunca una grilla.
- **Insight como cita editorial, no tarjeta:** una comilla grande en dorado (`"`) seguida del texto en serif, con la frase clave en cursiva — no una tarjeta con borde ni ícono circular de información.
- **Folio de página al pie** en vez de dots de progreso: número grande en serif cursiva ("02") + "／05" chico, más la wordmark "Manfredi Investment" del otro lado.
- **CTA (placa 5):** índice de secciones del informe con referencia tipo "§13" (no bullets con guión), y el link final subrayado en dorado en vez de un botón sólido.

## Tipografía — fuentes reales embebidas, no system fonts

Este es el cambio más importante de la v3: **nunca usar `Georgia`/`Palatino`/system fonts**. Se usan fuentes reales de Google Fonts, descargadas y embebidas como `data:` URI en `_fonts.css` (subset `latin`, que cubre los caracteres acentuados del español: á é í ó ú ñ ü ¿ ¡):

- **Newsreader** (serif editorial, normal + italic, pesos 400) — titulares, valores de datos, folios de página, comillas de insight. La cursiva se usa como recurso real de énfasis (no solo el color dorado).
- **IBM Plex Sans** (pesos 400/500/600, variable) — cuerpo de texto, nombres de categorías/labels.
- **IBM Plex Mono** (pesos 400/500/600) — masthead, tickers, eyebrows, referencias de sección.

`_fonts.css` y `_shared.css` de `carousel-v2-nvda/` son la fuente de verdad — copiarlos tal cual a cada carpeta nueva, sin modificar. Si `_fonts.css` no existe todavía en el checkout (por ejemplo si se está regenerando desde cero), se puede reconstruir así:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
curl -s -A "$UA" "https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" -o fonts.css
# parsear los bloques marcados "/* latin */", descargar cada .woff2, base64, y armar @font-face con
# src: url(data:font/woff2;base64,...) format('woff2') — ver historial de esta sesión (2026-08-08) para el script Python exacto.
```

Si no hay acceso a internet en el entorno de ejecución, **no** caer de nuevo en system fonts silenciosamente — usar el `_fonts.css` ya versionado en el repo (`carousel-v2-nvda/_fonts.css`), que ya tiene todo embebido y no necesita red.

## Las 5 placas (siempre en este orden)

1. **Portada** — ver sección "Research Desk" arriba.
2. **Gráfico de datos real #1** — el ángulo más fuerte del informe (ej. valuación por método). Ledger horizontal + cita editorial de insight.
3. **Gráfico de datos real #2** — un segundo ángulo (ej. escenarios DCF). Ledger vertical.
4. **Gráfico de datos real #3** — un tercer ángulo, preferentemente contraintuitivo o que muestre el rigor del análisis (ej. por qué un método se descarta, contexto histórico).
5. **CTA** — índice de secciones del informe completo, fair value blend si existe, link subrayado, disclaimer "Esto no es una recomendación de inversión." SIEMPRE presente.

**Cómo elegir qué graficar:** leer el informe completo del ticker y buscar la Sección de Valuación primero (suele tener una tabla "Fair value por método" y a veces escenarios Bear/Base/Bull). Si algún método es un outlier no confiable (ver el caso de NFLX y la reversión histórica excluida en `2026-08-08-nflx/slide-4-reversion-excluida.html`), está bien dedicarle una placa a explicar por qué se excluye en vez de forzarlo en el gráfico principal — eso es exactamente el tipo de rigor analítico que distingue a este desk.

## Cómo exportar (headless Chrome) — a máxima nitidez

Cada placa es un HTML standalone (`<link rel="stylesheet" href="_fonts.css"><link rel="stylesheet" href="_shared.css">`) de tamaño fijo 1080×1350, sin gallery ni wrapper. Se exporta al doble de resolución y se reescala hacia abajo para que el texto y los degradés queden nítidos — **no saltear el paso de reescalado**.

```bash
# 1) Render a 2x
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"   # ajustar según el entorno (linux: chromium/google-chrome-stable)
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1080,1350 --user-data-dir="/tmp/chrome-profile-$$" \
  --screenshot="slide-N-raw2x.png" "file:///ruta/absoluta/slide-N.html"

# 2) Reescalar a 1080x1350 con interpolación de alta calidad (bicúbica), no un resize simple/nearest-neighbor.
#    Windows/PowerShell: System.Drawing con InterpolationMode.HighQualityBicubic + SmoothingMode.HighQuality.
#    Linux/otros: ImageMagick `convert -resize 1080x1350 -filter Lanczos`, o Pillow (Image.LANCZOS).
```

**IMPORTANTE — usar una URL `file:///` bien formada.** En bash/Git Bash sobre Windows, las rutas suelen estar en formato POSIX (`/c/Users/...`) — pasarle esa ruta directamente a Chrome como `file:////c/Users/...` NO funciona (da `ERR_FILE_NOT_FOUND`, cuatro barras + ruta POSIX). Convertir siempre a formato Windows antes de armar la URL: `file:///C:/Users/...` (tres barras, luego la letra de unidad con dos puntos). Verificar esto ANTES de asumir que un fallo de render es un problema del HTML/CSS.

Notas:
- Usar un `--user-data-dir` nuevo/único por corrida (y por placa si se paraleliza) — reusar uno bloqueado por otro proceso hace que el comando falle en silencio.
- Verificar SIEMPRE que el PNG final (ya reescalado) se haya escrito y que el ancho/alto sea exactamente 1080×1350.
- Borrar los `*-raw2x.png` intermedios y los directorios `chrome-profile-*` antes de commitear.
- Si no hay Chrome/Chromium disponible, instalarlo vía el gestor de paquetes disponible (ej. `apt-get install -y chromium`) antes de exportar. No dejar el carrusel sin exportar a PNG.

## Cuándo se genera un carrusel

Dos disparadores posibles (ver el prompt del agente/rutina programada para cuál aplica en cada caso):

1. **Activo nuevo agregado a la página** (prioridad alta): si aparece un `informes/<ticker>.html` nuevo que todavía no tiene una carpeta `marketing/ig-posts/*-<ticker>/` correspondiente, generar su carrusel antes que cualquier otro — esto es lo que el fundador pidió como objetivo principal ("crear uno de estos por cada activo que se agrega a la página"). Comparar la lista de `informes/*.html` contra las carpetas ya generadas para detectar cuáles faltan.
2. **Rotación diaria de respaldo:** si no hay ningún activo nuevo sin cubrir, seguir la rotación de `marketing/ig-posts/rotation-state.json` (releer tickers ya cubiertos, en orden, para mantener presencia constante aunque no salga un informe nuevo ese día).

En ambos casos: generar el carrusel en `marketing/ig-posts/YYYY-MM-DD-<ticker>/`, actualizar `rotation-state.json` (`last_used`, `last_run_date`, `next_ticker`), commitear todo en la rama de trabajo indicada — nunca directo a `main`.

## Caption

Cada carrusel lleva un `caption.md`: gancho de 1 línea, 3-4 bullets con los datos más fuertes (cifras reales), mención de qué hay en el informe completo, disclaimer, y bloque de hashtags — ver `caption.md` de `carousel-v2-nvda/` como referencia de tono y longitud.

## Publicación automática a Instagram / TikTok — todavía NO implementada

El fundador pidió (2026-08-08) que cada carrusel se dispare automáticamente a Instagram y TikTok con su descripción apenas se genera. **Esto no está armado todavía** — no inventar una integración falsa ni simular que se publicó. Requiere, como mínimo:
- Cuenta de Instagram convertida a Business/Creator y vinculada a una Página de Facebook, más una app registrada en Meta for Developers con el permiso `instagram_content_publish` (requiere revisión de Meta) — la Content Publishing API de Meta exige que la imagen esté en una URL pública (no acepta upload directo), así que además hay que decidir dónde se hostean los PNG (ej. subcarpeta pública de manfredinvestment.com).
- Para TikTok, la Content Posting API con publicación directa (no solo "borrador") requiere aprobación de auditoría de TikTok — más restrictivo que Meta, no asumir que se consigue rápido.
- Ninguna de las dos cosas se resuelve solo con código — el fundador tiene que crear las apps de desarrollador y autorizar el acceso desde su propia cuenta (pantalla de consentimiento oficial de Meta/TikTok, nunca contraseñas tipeadas a un tercero).

Hasta que esto esté armado, el flujo real es: el carrusel y el caption quedan listos en su carpeta, el fundador los revisa y los sube a mano.
