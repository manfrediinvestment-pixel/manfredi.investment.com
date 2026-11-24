# Modelo BRK.B (Berkshire Hathaway) — SOTP propio

Primer holding del sitio. Marco: suma de las partes (50%) + reversión del P/B propio (30%) + consenso (20%). Sin DDM ni WACC único.

- `valuacion.py` — reconstruye la edición de sep-2026 (2T26) y corre la de nov-2026 (3T26). Tiene asserts que exigen reproducir sep al centavo (SOTP $494.13, reversión $492.67, blend $504.40). Bear/Bull de sep difieren < $0.50 (usa los múltiplos redondeados publicados).
- `verificar_html.py` — chequea que ~84 cifras del modelo aparezcan en `informes/brk.b.html` y que no queden restos de la edición anterior.
- `resultados.json` — salida (UTF-8).
- `data/` — precios Yahoo (30-jun, 22-sep, 30-sep y 20-nov-2026), comparables Yahoo al 20-nov (forwardPE, beta, P/B, ROE) y los 13F del 2T26 y 3T26 agregados por emisor/clase.

## Para la próxima actualización (4T26 / 10-K 2026)
1. Agregar en `SEG` el trimestre nuevo y en `edition_*()` los datos del balance (Nota 4: acciones cotizadas y ganancia no realizada; Nota 5: valor libro de OXY/KHC; caja y letras netas de compras sin liquidar; deuda de seguros y otros; float del MD&A; acciones A-equivalentes de la Nota 18).
2. Bajar precios y comparables (Yahoo: chart API + v7 quote con crumb). stockanalysis bloquea curl desde nov-2026; el consenso de BRK.B se leyó con el agente web-fetch (`/stocks/brk.b/forecast/`, EPS ya publicado por acción B).
3. Cartera: valor de balance + variación de las 9 posiciones principales del 13F (AAPL, AXP, KO, GOOGL, GOOG, BAC, CVX, MCO, CB) desde el cierre del trimestre hasta la fecha de precio.
4. Recompras: tabla mensual del 10-Q (Parte II, Ítem 2); el P/B ponderado se acumula sobre $82.723M (2018-1S26) + lo nuevo.
5. Si un cierre de año nuevo entra a `PB_HIST`, la mediana pasa a ser 2017-2026.
