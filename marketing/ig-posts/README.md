# Sistema de carruseles diarios — Instagram

Formato aprobado por el fundador el 2026-08-07. Referencia canónica: `carousel-v2-nvda/`. Cualquier carrusel nuevo debe reusar este mismo sistema visual — no reinventar el diseño cada vez.

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

- Paleta: navy `#0A0F1E` / `#060A14` de fondo, dorado `#F2C94C` como acento único, verde `#34D399` para escenarios alcistas, rojo apagado `#C97A6B` para escenarios bajistas, gris azulado `#5B6785`→`#7889AC` para datos neutros/secundarios.
- Tipografía: serif institucional (`Iowan Old Style`/`Palatino`/`Georgia` — system fonts, nunca links a CDN) para titulares, sans-serif de sistema para cuerpo, monospace para tickers/cifras/labels de eyebrow.
- Todas las cifras en `font-variant-numeric: tabular-nums` vía la fuente monospace de los charts.
- Cada gráfico debe tener: gridlines sutiles, ejes con valores reales, línea de referencia si aplica (ej. precio actual), y las cifras mostradas directamente sobre/al lado de cada barra — nunca una leyenda separada que obligue a ir y volver.
- Reusar `_shared.css` de `carousel-v2-nvda/` como base — copiarlo a la carpeta del nuevo carrusel y ajustar solo lo necesario (nombres, valores, escalas de los ejes).

## Cómo exportar (headless Chrome)

Cada placa es un HTML standalone (`<link rel="stylesheet" href="_shared.css">`) de tamaño fijo 1080×1350, sin gallery ni wrapper — así el screenshot no necesita recorte.

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"   # ajustar según el entorno (linux: chromium/google-chrome-stable)
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1080,1350 --user-data-dir="/tmp/chrome-profile-$$" \
  --screenshot="slide-N.png" "file:///ruta/absoluta/slide-N.html"
```

Notas:
- Usar un `--user-data-dir` nuevo/único por corrida — reusar uno bloqueado por otro proceso hace que el comando falle en silencio (exit code sin escribir el archivo).
- Verificar SIEMPRE que el PNG se haya escrito (`test -f`) y que el ancho/alto sea 1080×1350 antes de dar la tarea por terminada.
- Si no hay Chrome/Chromium disponible en el entorno, instalar chromium vía el gestor de paquetes disponible (ej. `apt-get install -y chromium` en Debian/Ubuntu) antes de intentar exportar. No dejar el carrusel sin exportar a PNG — el HTML solo no sirve para subir a Instagram.

## Rotación de tickers

Estado de rotación en `marketing/ig-posts/rotation-state.json`. Cada corrida:
1. Leer el archivo, tomar `next_ticker`.
2. Generar el carrusel para ese ticker en `marketing/ig-posts/YYYY-MM-DD-<ticker>/`.
3. Actualizar `rotation-state.json`: mover el ticker usado al final de la lista (o marcarlo como usado) y calcular el próximo `next_ticker`, actualizar `last_run_date`.
4. Commitear todo (carrusel + estado actualizado) en la rama de trabajo indicada en el prompt del agente — nunca directo a `main`.

Si `informes/<ticker>.html` no existe todavía para el ticker que tocaría (por ejemplo, se agregó un ticker nuevo a la rotación antes de que el informe estuviera listo), saltar ese ticker y pasar al siguiente, dejando una nota en el mensaje de cierre del agente.

## Caption

Cada carrusel lleva un `caption.md` en su carpeta: gancho de 1 línea, 3-4 bullets con los datos más fuertes (con cifras reales), mención de qué hay en el informe completo, disclaimer, y bloque de hashtags (mezclar hashtags de ticker/empresa específicos con generales de finanzas/Argentina — ver `caption.md` de `carousel-v2-nvda/` como referencia de tono y longitud).
