# Modelo WMT (Walmart) — informe-consumo-masivo, bloque de retail

Todo número derivado de `informes/wmt.html` sale de `model.py`. El HTML se arma desde `wmt.tpl.html` con tokens
`{{clave|formato}}` (mismo sistema que PG y UNH); `verify.py` compara el HTML contra el modelo y tiene que dar
**0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | Modelo completo → `model.json` (insumos arriba de cada bloque, con su fuente) |
| `wmt.tpl.html` | Plantilla del informe (texto + tokens). `@@CSS@@` y `@@SCRIPT@@` los completa el build |
| `charts_wmt.js` | `renderAll()` con los 13 gráficos; en pantallas de menos de 560 px usa etiquetas cortas y los últimos 8 trimestres |
| `build.py` | Toma CSS y motor de gráficos de `informes/pg.html`, agrega `minV/maxV` a `drawLines` y rótulos con decimal al rombo de `drawGroupedBars`, renderiza `informes/wmt.html` |
| `render.py` | Reemplaza tokens (formatos: usd0/usd2, f0-f3, i0, x1/x2, pct/spct, spp0/spp2, a0/a1, js1/js2) |
| `verify.py` | Tokens vs. modelo, aritmética del blend de cinco métodos (7.5/7.5/25/35/25), etiquetas y promedios de grupo, celdas Base de la grilla y de la sensibilidad a comparables, cierre de la suma de partes, "hoy/ayer/mañana", gate, logo |
| `index_add.py` / `manifest_add.py` | Conexión al sitio (una sola vez; en una actualización, solo `manifest_add.py` si cambia el texto) |
| `fetch_data.py` | Precios (Yahoo: WMT, pares, Walmex, MXN, INR, Treasury) y consenso trimestral y anual (Nasdaq/Zacks) |
| `data/fetch_sec.py`, `data/fetch_old.py`, `data/fetch_filings.py` | Comunicados 8-K 2.02 (desde 2015), 10-K, 10-Q y proxy como texto (ignorados en git; se regeneran) |
| `data/annual.py` → `data/annual.json` | Serie anual XBRL FY2016-FY2026 que usa el modelo |
| `data/balances.py` | Verifica contra XBRL los balances de FY2024-FY2026 que usa el ROIC |
| `data/extract_kpis.py` | Imprime comparables, tráfico, ticket y aporte del e-commerce de cada comunicado |

## Actualizar el próximo trimestre
1. `python fetch_data.py` → copiar a `model.py`: `PRICE`, `RF`, consenso (`C27/C28/C29`, `Q_CONS`: los cuatro trimestres
   siguientes), pares en `PEERS` (precio, consenso trimestral, comparables del último trimestre, EV/EBITDA y beta de
   stockanalysis), Walmex (`WALMEX_PX`, `MXN`), consenso de precio objetivo (`CONS`).
2. Del comunicado nuevo (`python data/fetch_sec.py` y `python data/extract_kpis.py`): agregar el trimestre a `QL`, `US`, `SAMS`,
   `ECOM_Q`; el EPS ajustado a `EPS_RAW`; `Q2` (o el trimestre que corresponda), balance (`DEBT_FIN`, `FIN_LEASE`, `OP_LEASE`,
   `CASH`), acciones (`SH_DIL`, `SH_OUT`), guía (`GUIDE_LO/HI`).
3. En el 4T: correr `data/annual.py` (nuevo año fiscal), actualizar `SEG`, `ADJ_OI`, `ECOM`, `ADS`, `MEMB`, `BAL`, `INT`, `SBC`, `DA`.
4. Revisar la regla de cambio de escalón del P/E (`RR_MIN_PRIOR`, `RR_MIN_AFTER`): si el múltiplo cae por debajo del máximo
   previo, la ventana se corta sola y la lectura 1 vuelve al promedio de diez años.
5. Revisar las marcas de Internacional: una salida a bolsa de Flipkart o PhonePe reemplaza `FLIP_VAL` / `PP_VAL`.
6. `python model.py && python build.py && python verify.py` → 0 diferencias.
7. Revisar el texto de la plantilla (fechas de corte, hechos del trimestre, riesgos y catalizadores).
8. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
