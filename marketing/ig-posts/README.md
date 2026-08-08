# Sistema de carruseles diarios — Instagram

Formato aprobado por el fundador el 2026-08-07 (v2, tras rechazar dos intentos anteriores por calidad de diseño). Referencia canónica: `carousel-v2-nvda/`. Cualquier carrusel nuevo debe reusar este mismo sistema visual EXACTO — no reinventar el diseño cada vez, y no revertir a versiones anteriores más simples.

**Historial de rechazos, para no repetir los mismos errores:**
- v1 (rechazada): placas con solo texto/títulos, sin gráficos de datos reales. El fundador: "no quiero simples títulos y listo, que aporten valor".
- v2 primer intento (rechazado): gráficos con barras grises azuladas (`--slate`) y una textura de líneas horizontales de fondo en toda la placa (`.ruled-bg`). El fundador: "la calidad de las imágenes son una vergüenza, el color de los gráficos otra vergüenza... saca los cuadraditos del fondo, las líneas esas". **Nunca reintroducir `.ruled-bg`, gridlines dentro de los charts, ni el color `--slate` gris azulado.**
- v2 final (aprobada): sin ninguna textura/gridline de fondo, barras en forma de píldora con degradé dorado (emphasis) o "vidrio esmerilado" blanco translúcido (secundarias) en vez de gris, colores semánticos desaturados tipo joya (terracota `--bear` / esmeralda `--bull`) para escenarios, insight en tarjeta con borde en vez de ícono circular, exportado a 2x y reescalado a 1080×1350 con interpolación bicúbica para máxima nitidez (ver sección de export).

## Qué es esto

Un carrusel de 5 placas (1080×1350 px, formato feed 4:5) que analiza UN activo financiero por día, usando **datos reales extraídos del informe institucional de ese ticker** en `informes/<ticker>.html`. Nunca se inventan cifras ni se usan gráficos decorativos sin datos detrás — esa fue la razón por la que se rechazó la primera versión de este sistema.

## Las 5 placas (siempre en este orden)

1. **Portada** — ticker en sello tipográfico grande (círculo con borde dorado, NO usar logos reales bajados de internet — riesgo de marca registrada y calidad inconsistente), headline con gancho editorial (una pregunta o afirmación fuerte sobre la tesis), subtítulo de una línea, chips con los métodos/temas que se van a ver.
2. **Gráfico de datos real #1** — el ángulo más fuerte del informe (ej. valuación por método, comparación de márgenes, crecimiento). Debe incluir un insight (caja con ícono "i") que explique QUÉ SIGNIFICA el dato, no solo mostrarlo.
3. **Gráfico de datos real #2** — un segundo ángulo (ej. escenarios DCF, evolución de un múltiplo, comparación de segmentos).
4. **Gráfico de datos real #3** — un tercer ángulo, preferentemente algo contraintuitivo o que muestre el rigor del análisis (ej. por qué un método se pondera menos, contexto histórico).
5. **CTA** — resume qué más tiene el informe completo, muestra el fair value blend si el informe lo tiene, botón "Leer el informe completo →", URL real del informe, y el disclaimer "Esto no es una recomendación de inversión." SIEMPRE presente.

**Cómo elegir qué graficar:** leer el informe completo del ticker (`informes/<ticker>.html`) y buscar la Sección 13 (Valuación) primero — casi siempre tiene una tabla "Fair value por método" y a veces un desglose de escenarios (Bear/Base/Bull). Buscar también cualquier comparación temporal o vs. la industria que sea genuinamente interesante (no forzar un gráfico si no hay un dato real que lo sostenga — mejor 4 placas sólidas que 5 con una floja).

## Sistema visual (no cambiar sin aprobación)

- Paleta: navy `#0A0F1E`→`#050810` de fondo (con un leve glow radial dorado en la esquina superior derecha, nada más — **sin textura de líneas ni grilla de fondo**), dorado `#F2C94C` como único acento real, esmeralda `#1F8F6B` para escenarios alcistas, terracota `#B8654F` para escenarios bajistas, "vidrio esmerilado" (`rgba(246,247,250,.15→.05)` con borde `rgba(246,247,250,.24)`) para barras/datos neutros o secundarios — **nunca gris azulado plano**.
- Barras: siempre en forma de píldora (horizontales, `border-radius:999px`) o con esquinas superiores muy redondeadas (verticales, `border-radius:14px 14px 3px 3px`), con degradé sutil de 2-3 paradas y una sombra/glow del mismo color por debajo para dar profundidad — nunca un color plano sin sombra.
- Tipografía: serif institucional (`Iowan Old Style`/`Palatino`/`Georgia` — system fonts, nunca links a CDN) para titulares, sans-serif de sistema para cuerpo, monospace para tickers/cifras/labels de eyebrow. Todas las cifras en la fuente monospace de los charts.
- **Sin gridlines ni ejes con marcas cada N unidades** — las cifras van directamente sobre/al lado de cada barra. Si hace falta un punto de referencia (ej. precio actual), usar una única línea fina con una etiqueta tipo "flag" (fondo `--navy-panel`, texto dorado), no una grilla completa.
- El insight de cada gráfico va en una tarjeta con borde sutil y borde izquierdo dorado de 3px, con un eyebrow tipo "POR QUÉ IMPORTA" en mono — no un ícono circular de información.
- Reusar `_shared.css` de `carousel-v2-nvda/` tal cual — copiarlo sin modificar a la carpeta del nuevo carrusel. Solo se ajustan valores/porcentajes en el HTML de cada placa, nunca el sistema de diseño en sí.

## Cómo exportar (headless Chrome) — a máxima nitidez

Cada placa es un HTML standalone (`<link rel="stylesheet" href="_shared.css">`) de tamaño fijo 1080×1350, sin gallery ni wrapper — así el screenshot no necesita recorte. Se exporta al doble de resolución y se reescala hacia abajo para que el texto y los degradés queden nítidos (el render 1:1 directo se ve notablemente peor, con bordes más ásperos) — **no saltear el paso de reescalado**.

```bash
# 1) Render a 2x
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"   # ajustar según el entorno (linux: chromium/google-chrome-stable)
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1080,1350 --user-data-dir="/tmp/chrome-profile-$$" \
  --screenshot="slide-N-raw2x.png" "file:///ruta/absoluta/slide-N.html"

# 2) Reescalar a 1080x1350 con interpolación de alta calidad (bicúbica), no un resize simple/nearest-neighbor.
#    En Windows/PowerShell: System.Drawing con InterpolationMode.HighQualityBicubic + SmoothingMode.HighQuality.
#    En Linux/otros entornos: usar el equivalente disponible (ej. ImageMagick `convert -resize 1080x1350 -filter Lanczos`,
#    o Pillow en Python con Image.resize(..., Image.LANCZOS)) — el punto es un filtro de calidad, no un downscale barato.
```

Notas:
- Usar un `--user-data-dir` nuevo/único por corrida (y por placa si se paraleliza) — reusar uno bloqueado por otro proceso hace que el comando falle en silencio (exit code sin escribir el archivo).
- Verificar SIEMPRE que el PNG final (ya reescalado) se haya escrito (`test -f`) y que el ancho/alto sea exactamente 1080×1350 antes de dar la tarea por terminada.
- Borrar los `*-raw2x.png` intermedios y los directorios `chrome-profile-*` antes de commitear — no deben quedar en el repo.
- Si no hay Chrome/Chromium disponible en el entorno, instalar chromium vía el gestor de paquetes disponible (ej. `apt-get install -y chromium` en Debian/Ubuntu) antes de intentar exportar. Si tampoco hay una librería de imagen disponible para el paso 2 (Pillow/ImageMagick/System.Drawing), exportar directo a 1080×1350 a 1x en vez de saltear el PNG — es preferible una imagen algo menos nítida que ninguna imagen.

## Rotación de tickers

Estado de rotación en `marketing/ig-posts/rotation-state.json`. Cada corrida:
1. Leer el archivo, tomar `next_ticker`.
2. Generar el carrusel para ese ticker en `marketing/ig-posts/YYYY-MM-DD-<ticker>/`.
3. Actualizar `rotation-state.json`: mover el ticker usado al final de la lista (o marcarlo como usado) y calcular el próximo `next_ticker`, actualizar `last_run_date`.
4. Commitear todo (carrusel + estado actualizado) en la rama de trabajo indicada en el prompt del agente — nunca directo a `main`.

Si `informes/<ticker>.html` no existe todavía para el ticker que tocaría (por ejemplo, se agregó un ticker nuevo a la rotación antes de que el informe estuviera listo), saltar ese ticker y pasar al siguiente, dejando una nota en el mensaje de cierre del agente.

## Caption

Cada carrusel lleva un `caption.md` en su carpeta: gancho de 1 línea, 3-4 bullets con los datos más fuertes (con cifras reales), mención de qué hay en el informe completo, disclaimer, y bloque de hashtags (mezclar hashtags de ticker/empresa específicos con generales de finanzas/Argentina — ver `caption.md` de `carousel-v2-nvda/` como referencia de tono y longitud).
