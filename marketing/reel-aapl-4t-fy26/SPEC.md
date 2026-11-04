# SPEC — Reel AAPL, resultados 4T del año fiscal 2026

Hecho en la nube (skill `reel-noticia`, sección 8b) el 4-nov-2026. Fuente principal: `informes/aapl.html`
(actualizado el 3-nov-2026 con el 8-K del 2-nov-2026 y el 10-K del año fiscal 2026). Reacción de la acción:
cierres diarios de Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart/AAPL` y `v7/finance/spark`, vía WebFetch).
Todos los cálculos se rehicieron con Python.

## El dato central
Apple vendió más que nunca, pero avisó que de cada venta le va a quedar menos: margen bruto guiado de 45%–46% para
oct–dic contra 48,8% en el año, por el costo de la memoria. Metáfora: **heladería** con cola a la vuelta de la manzana
(demanda récord) y la crema y los cucuruchos (memoria) cada vez más caros.

## Datos y fuentes

| Dato | Valor | Fuente / cálculo |
|---|---|---|
| Cierre 2-nov-2026 (día del reporte, publicado después del cierre) | US$ 338,32 | Yahoo Finance |
| Cierre 3-nov-2026 | US$ 331,90 | Yahoo Finance |
| Variación 3-nov | −1,90% (331,90 / 338,32 − 1 = −1,898%) | cálculo |
| Apertura / mínimo 3-nov | 325,58 (−3,77%) / 325,33 (−3,84%) | Yahoo Finance (no se usa en la voz) |
| Pares el 3-nov | MSFT +2,74% · META +2,36% · NVDA +2,29% · AMZN +2,06% · GOOGL +0,37% | Yahoo Finance spark, cierres 2-nov → 3-nov |
| Valor en bolsa perdido | US$ 93.295 M (6,42 × 14.532 M de acciones) | acciones: informe Manfredi (capitalización al 2-nov) |
| Ventas 4T FY26 (jul–sep) | US$ 114.480 M, +11,7% | 8-K 2-nov-2026 / informe sección 05 |
| Ventas 4T FY25 | US$ 102.466 M | 8-K del 4T FY25 (114.480 / 102.466 − 1 = 11,72%) |
| Consenso de ventas 4T | US$ 113.390 M | LSEG, citado en el informe sección 01 |
| Ventas año fiscal 2026 | US$ 478.830 M (+15,1%), récord | 10-K FY2026 |
| Margen bruto FY26 / 4T FY26 | 48,8% / 47,9% | 8-K / 10-K |
| Guía de margen bruto 1T FY27 (oct–dic) | 45%–46% (punto medio 45,5%) | 8-K y llamada del 2-nov; baja de 2,8 a 3,8 pts vs 48,8% |
| Guía de ventas oct–dic | +7% a +10% (US$ 153.800–158.100 M), trimestre récord | llamada del 2-nov / informe sección 01 |
| Causa | costo de la memoria (escasez en toda la industria) + nube de Siri AI | CFO en la llamada; 10-K |
| Inventario | US$ 5.720 M → US$ 14.540 M (×2,5) | 10-K FY2026 / informe sección 04 |
| Metáfora "de cada $100" | $48,80 → $45,50 (−$3,30) | margen bruto 48,8% vs punto medio de la guía |
| EPS de consenso FY2027 | US$ 9,66 (informe del 3-ago-2026) → US$ 9,44 (informe del 3-nov) | stockanalysis.com, citado en el informe |
| Precio en el informe de agosto | US$ 306,07 | `git show 378e53e:informes/aapl.html` |
| P/E sobre EPS FY27 | 31,7x (306,07/9,66) → 35,2x (331,90/9,44) | cálculo |
| iPhone 4T FY26 / 4T FY25 | US$ 57.580 M / US$ 49.026 M (+17,5%) | 8-K / informe sección 03 |
| Mac 4T FY26 | US$ 10.790 M (+23,7%) | 8-K / informe sección 03 |
| Valor justo Manfredi (blend) | US$ 263,56, publicado el 3-nov-2026 (commit 121d371) | informe sección 13 |
| Distancia precio vs valor justo | 331,90 / 263,56 − 1 = +25,9% | cálculo |

## Datos que NO se pudieron verificar contra fuente primaria desde la nube
- La SEC está bloqueada en este entorno: las cifras del 8-K/10-K salen de nuestro informe (que sí las tomó de EDGAR el
  3-nov), no de una lectura directa del 8-K en esta sesión.
- Ventas del 4T FY25 (US$ 102.466 M) e iPhone 4T FY25 (US$ 49.026 M): no figuran como cifra en el informe; se tomaron
  del 8-K del 4T FY25 y se confirmaron con prensa (Retail Insider, PhoneArena: US$ 102.470 M e iPhone US$ 49.030 M);
  cuadran con las variaciones del informe (+11,7% y +17,5%).
- Acciones en circulación (14.532 M) para el valor borrado: del informe; el número de "93 mil millones" es aproximado
  (no se cruzó con un dato de prensa de capitalización perdida).
- "Única de las seis gigantes en rojo": verificado solo contra MSFT, META, NVDA, AMZN y GOOGL (no contra TSLA, AVGO u otras).
- No hay ranking histórico (no es un récord de caída); el gancho es el contraste año récord / acción en baja.

## Escenas (build_index.py)
golpe 0 · reaccion 3,3 · pregunta 7,9 · causa 12,5 · heladeria 23,1 · ironia 35,0 · cola 41,8 · informe 46,2 ·
final 53,8 · comenta 62,0 · logo 67,6 · fin 71,1
