# Reel MSFT — 1T del año fiscal 2027 (reportado el 28-oct-2026)

Skill `reel-noticia`, modo nube (sección 8b). Palabra para comentar: **MICROSOFT**. Guía: `/guia-msft`.
Metáfora: **obra en construcción** (constructora con los departamentos vendidos antes de levantarlos que pide un crédito
para hacer más pisos). Registrada en `marketing/METAFORAS.md`.

## Datos y fuentes

| Dato en pantalla / voz | Valor | Fuente | Estado |
|---|---|---|---|
| Cierre previo al reporte (28-oct) | US$ 531,01 | Yahoo Finance, chart diario | Verificado |
| 29-oct / 30-oct / 2-nov / 3-nov | 530,14 / 521,91 / 507,12 / 520,99 | Yahoo Finance | Verificado |
| Caída en 3 ruedas (28-oct → 2-nov) | −4,50% (507,12 / 531,01 − 1 = −4,499%) | cálculo propio | Verificado |
| Valor borrado | ≈ US$ 177.900 M (23,89 × 7.446 M acciones diluidas) | cálculo propio con acciones diluidas del informe | **Estimación** (la capitalización real usa acciones en circulación, no diluidas; la prensa no publicó una cifra) |
| Ventas 1T FY27 vs 1T FY26 | US$ 92.282 M vs 77.672 M (+18,8%) | 8-K (vía informes/msft.html, sección 03) | Verificado en el informe |
| "Vendió más que nunca" | 92.282 > 90.010 (4T FY26), máximo trimestral | informe, sección 05 + TTM | Verificado |
| Azure | US$ 33.170 M (+48,2%) | 8-K, ingresos por línea de producto | Verificado en el informe |
| Superó al consenso | EPS 4,89 vs 4,73; ventas 92,28 vs 90,69 (LSEG) | informe, sección 01 | Verificado en el informe |
| Capex del trimestre | US$ 45.200 M con arrendamientos financieros; 39.370 M en efectivo vs 19.390 M (×2,0) | 8-K / 10-Q; llamada (Amy Hood) | Verificado |
| Bono | ~US$ 25.000 M, 10 tramos de 2 a 40 años; primero desde 2017 | Bloomberg/Reuters, TradingView; 424B2 citados en el informe | Monto **de prensa** (la compañía no publicó un comunicado con la cifra final) |
| Contratos firmados (RPO comercial) | US$ 677.000 M (+73%) | 8-K / llamada | Verificado en el informe |
| Capex esperado por el mercado | > US$ 50.000 M | StreetAccount (vía informe, sección 04) | De fuente secundaria |
| Demora de materiales | "algunas entregas de capacidad de terceros … se demoraron" | Amy Hood, llamada del 28-oct | Verificado (transcripción) |
| Guía de capex 2T FY27 | > US$ 50.000 M, acelerando en la 2ª mitad | llamada del 28-oct (transcripción no oficial) | Verificado en el informe |
| Flujo de caja libre | US$ 18.630 M (OCF 58.000 − capex efectivo 39.370) | 8-K, flujo de caja | Verificado en el informe |
| Flujo operativo | US$ 58.000 M (+29%) | 8-K | Verificado en el informe |
| Margen operativo | 49,8%, el más alto de los últimos 8 trimestres | informe, sección 05 | Verificado en el informe |
| Valor justo Manfredi | US$ 540,66 (blend 15/25/35/25) | informes/msft.html, commit 6b68028 del 3-nov-2026 | Verificado |
| Distancia al precio | 540,66 / 520,99 − 1 = +3,8% | cálculo propio | Verificado |

**No usado en el video (no verificado):** que las órdenes del bono superaron los US$ 100.000 M (solo prensa, no
confirmado por la compañía).

## Escenas (segundo de entrada)
golpe 0 · ventas 4,0 · causa 12,7 · obra 24,2 · ironia 35,9 · caja 44,5 · informe 49,9 · final 58,0 · comenta 66,9 · logo 72,5 · fin 76,0

## Render
`npx -y hyperframes@0.9.4 render -o output/msft-1t-fy27-v1.mp4 --fps 30 --quality high`; comprimido con
`ffmpeg -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k` a `entrega/msft-reel.mp4` (solo en la rama del video).
