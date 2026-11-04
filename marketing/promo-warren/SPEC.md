# Promo Warren v2 — "El problema no es la IA. Es todo lo que le decís."

Video vertical 1080x1920, 30 fps, 66,0 s. Proyecto HyperFrames (`build_index.py` → `index.html`).
Rama `claude/promo-warren`. Sistema visual, movimiento y sonido: skill `reel-noticia` (secciones 4, 5, 6, 6b, 8b).

## Escenas (segundo de entrada)

| # | Escena | Entra | Qué pasa |
|---|---|---|---|
| 1 | `gancho` | 0,0 | Punch-in + flash en el cuadro 0; logos de IA (Claude, Anthropic, Google Gemini, Perplexity, Meta, Mistral AI) orbitando entre velas, línea que sube, cinta de tickers y dos odómetros; todo choca en el centro (destello, temblor, esquirlas) y cae el cartel "Si no usás IA para invertir, estás perdido." |
| 2 | `pregunta` | 6,0 | Chat blanco genérico sin marca: se tipea la pregunta, la respuesta de 2 líneas aparece de golpe, queda congelado y cae el cartel "El problema no es la IA. Es todo lo que le decís." |
| 3 | `contexto` | 12,0 | Caen CONTEXTO, FUENTES, PROMPT y PRECIO; cada uno se agrieta con su ✗ y al final se parten en dos; cartel "No los podés juntar en una sola IA."; entra el botón dorado de Warren y crece hasta llenar la pantalla. |
| 4 | `revelacion` | 22,0 | Sin latigazo: el dorado se recoge en el avatar de Warren; las mitades vuelven y se rearman; un cable dorado por casillero, ✗ → ✓ verde y la frase nueva. |
| 5 | `respuesta` | 27,0 | Misma pregunta a Warren: tecleo rápido, ráfaga de lo que leyó, y el informe (`assets/warren-doc.js`) baja de corrido con punch-ins de 0,5 s; cierra con "No te digo qué comprar. Te muestro cuánto vale y por qué." |
| 6 | `real` | 42,0 | La tapa de GOOGL se abre en una ventana con la página REAL de `informes/googl.html`, que baja de punta a punta mientras corre el contador; cartel "Esto es UN informe. Tenemos casi 50." |
| 7 | `comenta` | 54,0 | Comentá FINANZAS → mensaje con el código de descuento borroso, sin porcentaje. |
| 8 | `logo` | 63,0 | Logo + "Contenido informativo y educativo. No es recomendación de inversión." Fin 66,0. |

Se eliminaron las escenas `contraste` (pantalla partida) e `informes` (biblioteca).

## De dónde sale cada número

| Dato en pantalla | Valor | Fuente |
|---|---|---|
| Pregunta "…después de caer 12%?" y odómetro GOOGL del gancho | −12,64% | `informes/googl.html` (caída del 29-oct-2026, de $324.89 a $283.82) |
| Odómetro CLOUD del gancho | +103% | `informes/googl.html` (Google Cloud +103%, a $30.71 mil millones) |
| Velas y línea del gancho | sin cifras | forma decorativa determinista: no representa ningún precio |
| Cinta de tickers | sin cifras | tickers de `informes/catalogo.json`; las flechas son decorativas |
| "USD 20 por mes" | 20 | guion del user (precio típico de una suscripción de IA; no sale del repo) |
| "Incluido en la membresía" | sin número | por pedido del user no se muestra el precio de la membresía |
| Valor justo / precio / diferencia | US$ 330,28 / US$ 279,84 (cierre 30-oct-2026) / +18,0% | `informes/googl.html`, portada y sección 13 |
| Caja 3T26 | flujo operativo US$ 42,29 B · capex US$ 51,36 B · flujo libre −US$ 9,07 B | `informes/googl.html`, tabla de flujo de caja (8-K, Exhibit 99.1) |
| 5 métodos y pesos | DCF base 210,03 (7,5%) · Suma de partes 316,22 (7,5%) · Comparables 369,36 (25%) · Reversión histórica 280,43 (35%) · Consenso 401,29 (25%) | `informes/googl.html`, síntesis de la sección 13 |
| Football field | rangos de los datos de `footballChart`; líneas en 279,84 y 330,28 | `informes/googl.html` |
| Escenarios | Bajista 67,21 (25%) · Base 210,03 (45%) · Alcista 486,12 (30%) · esperado 257,15 | `informes/googl.html`, DCF por escenarios |
| Fecha del informe | 2-nov-2026 | `informes/catalogo.json` (`GOOGL.f`) |
| Contador del informe real | 14 secciones · 18 tablas · 8 gráficos · 7.845 palabras | `informes/catalogo.json` (`GOOGL`: secs 14, tb 18, ch 8, w 7845). Verificado sobre el HTML renderizado: 14 `h2`, 18 `table`, 8 `canvas`/`.chartbox` (innerText: 7.832 palabras) |
| "24.658 px de alto" | 24.658 | alto de la página completa capturada a 1080 px de ancho |
| "casi 50" | 49 | `informes/catalogo.json` tiene 49 entradas (48 empresas + FOMC) |

## Cómo se capturó el informe real

1. `python3 -m http.server 8765` en la raíz del repo.
2. `puppeteer-core` (npm, en el scratchpad) con `/usr/bin/google-chrome` headless, viewport 1080x1920, `fullPage: true` sobre `http://127.0.0.1:8765/informes/googl.html`.
3. Durante la captura se bloqueó la carga de `informes/_preview-gate.js` (intercepción de requests) para que no difumine la página; el archivo NO se tocó. También se bloqueó cualquier request externo (fuentes de Google): la página usa las fuentes de respaldo.
4. Resultado 1080x24.658 px, cortado en 13 tiras de 2.000 px (`assets/googl/t00.jpg`…`t12.jpg`, JPG calidad 72, 3,1 MB).

## Logos de IA

`npm i simple-icons` (CC0) en el scratchpad; los paths SVG se copiaron a `assets/ai-logos.js`. Pedidos: claude, anthropic, googlegemini, perplexity, meta, mistralai — están los seis. Monocromo blanco/dorado. Solo aparecen en el gancho; el chat que contesta poco sigue sin marca.

## Reglas aplicadas

- Cero texto gris (chat genérico con texto `#0b0f17`; rótulos chicos en champagne `#ead9a4`).
- Warren nunca dice comprar ni vender; rótulo "Recreación con datos del informe Manfredi de GOOGL (2-nov-2026)".
- Código de descuento de relleno, siempre borroso, sin porcentaje.
- Todo local (GSAP, fuentes, sonidos, logos, captura).

## Pendiente

- Grabar la voz y resincronizar (skill, sección 7).
- Disparador de SendPulse para FINANZAS y código real (no se puede desde la nube).
