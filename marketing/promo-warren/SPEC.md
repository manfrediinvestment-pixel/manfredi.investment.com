# Promo Warren — "El problema no es la IA. Es el contexto."

Video vertical 1080x1920, 30 fps, 69,4 s. Proyecto HyperFrames (`build_index.py` → `index.html`).
Rama `claude/promo-warren`. Sistema visual, movimiento y sonido: skill `reel-noticia` (secciones 4, 5, 6, 6b, 8b).

## De dónde sale cada número

| Dato en pantalla | Valor | Fuente |
|---|---|---|
| Pregunta "¿Google está barata después de caer 12%?" | −12,64% el 29-oct-2026 | `informes/googl.html` (resumen: "la acción cayó −12.64% el 29-oct-2026, de $324.89 a $283.82") |
| Valor justo (blend ponderado) | US$ 330,28 | `informes/googl.html`, portada y tabla de síntesis de la sección 13 |
| Precio de referencia | US$ 279,84, cierre del 30-oct-2026 | `informes/googl.html` ("Precio de referencia: cierre del 30-oct-2026 ($279.84, Yahoo Finance / Nasdaq)") |
| Diferencia | +18,0% | `informes/googl.html` ("$330.28 vs. $279.84 mercado · +18.0%") |
| Postura | Neutral con sesgo constructivo | `informes/googl.html`, portada (Warren nunca dice comprar/vender: `workers/warren/prompt.js`) |
| Flujo operativo 3T26 / Capex 3T26 / Flujo libre | US$ 42,29 B / US$ 51,36 B / −US$ 9,07 B | `informes/googl.html`, tabla de flujo de caja (8-K, Exhibit 99.1) |
| Google Cloud | +103%, US$ 30,71 B | `informes/googl.html`, resumen ejecutivo |
| 5 métodos y pesos | DCF base 210,03 (7,5%) · Suma de partes 316,22 (7,5%) · Comparables 369,36 (25%) · Reversión histórica 280,43 (35%) · Consenso 401,29 (25%) | `informes/googl.html`, "Síntesis: los cinco métodos y el blend ponderado" |
| Football field (rangos) | DCF 67,21–486,12 · Comparables 265,11–504,42 · Suma de partes 316,22–346,01 · Reversión 272,65–288,20 · Consenso 300–490; líneas en 279,84 y 330,28 | `informes/googl.html`, datos de `footballChart` |
| Escenarios (DCF) | Bajista 67,21 (25%) · Base 210,03 (45%) · Alcista 486,12 (30%) · valor esperado ponderado 257,15 | `informes/googl.html`, sección 13 (DCF por escenarios) |
| Fecha del informe | 2-nov-2026 | `informes/catalogo.json` (`GOOGL.f = 2026-11-02`) y `git log` del archivo (commit 441054c, 2026-11-02) |
| Fuentes listadas | Nasdaq 30-oct · 8-K SEC 28-oct · informe Manfredi 2-nov · TipRanks post-reporte | las que cita el propio informe |
| "casi 50 informes" / odómetro 49 | 49 | `informes/catalogo.json` tiene 49 entradas (48 empresas + FOMC) al 4-nov-2026 |
| Lomos de la biblioteca | los 49 tickers del catálogo, en su orden | `informes/catalogo.json`; logos `assets/logos/mono/` |
| Contraste: "2 líneas · 16 palabras · 0 datos" | 16 | respuesta genérica del guion, contada a mano |
| Contraste: "148 palabras · 2 tablas · 2 gráficos" | 148 | texto de la respuesta de Warren (`assets/warren-doc.js`) contado con node (144 + los 2 valores del odómetro "US$ 330,28" y "US$ 279,84"). Tablas: métodos y escenarios. Gráficos: barras de caja y football field |

## Reglas aplicadas

- Chat genérico sin marca (sin nombres ni logos), blanco y plano, texto casi negro `#0b0f17` (nada de gris). En el contraste se rotula "UNA IA CUALQUIERA".
- La respuesta de Warren lleva el rótulo fijo "Recreación con datos del informe Manfredi de GOOGL (2-nov-2026)" en el encabezado del panel y termina con la línea de cierre real del prompt ("Análisis educativo de Manfredi Investment. No constituye asesoramiento financiero regulado.").
- Remate: "No te digo qué comprar. Te muestro cuánto vale y por qué."
- Descuento sin porcentaje; el código ("WARREN-K7Q2", de relleno) aparece siempre borroso.
- Aviso final: "Contenido informativo y educativo. No es recomendación de inversión."
- Todo local: GSAP en `assets/gsap.min.js`, fuentes en `assets/fonts/`, sonidos en `assets/sfx/` (los del piloto).

## Estilo tomado de la web

- Botón dorado flotante (`.warren-fab`, `.warren-badge` con "W", etiqueta "Preguntale a Warren") → escena 2→3.
- Panel de Warren (`.warren-header` #080c18, avatar `conic-gradient` de `.warren-avatar`, nombre en DM Serif dorado, punto verde, botón de enviar `linear-gradient(155deg,#F7CE4E,#F2784B)`).
- Respuesta en estilo Lector (`assets/lector/lector.css`: fondo #0b1629, líneas rgba(214,226,244,.10/.18), serif + mono, dorado).
- Biblioteca (`assets/informes/estanteria.css`): lomos `.spn` con filetes dorados, colores de serie `FONDO`, y la tapa `.est-cover` en el atril.

## Escenas (segundo de entrada)

gancho 0 · contexto 5,0 · revelacion 12,8 (sin latigazo: el botón crece y se vuelve el fondo) · respuesta 18,4 · contraste 44,0 · informes 50,0 · comenta 57,8 · logo 65,9 · fin 69,4.

## Pendiente / notas

- `marketing/reel-gota.html` no existe en el repo (ni en otra rama): la escena de comentario se armó desde `comenta.html` del piloto de Google.
- No hay sonido de "disco que se frena" en la biblioteca local: el "¿Eso es todo?" usa el golpe seco (`impact-bass-1`).
- Falta la voz del user; al grabarla, resincronizar con la sección 7 de la skill.
- El disparador de SendPulse para FINANZAS y el código real de descuento hay que crearlos desde la PC.
