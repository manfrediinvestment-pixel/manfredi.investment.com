# Modelo PEP (PepsiCo) — informe-consumo-masivo, snacks y bebidas (modelo integrado)

Todo número derivado de `informes/pep.html` sale de `model.py`. El HTML se arma desde `pep.tpl.html` con tokens
`{{clave|formato}}` (mismo sistema que KO, PG y WMT); `verify.py` compara el HTML contra el modelo y tiene que dar
**0 diferencias** antes de publicar. La comparación con Coca-Cola (Sección 09) lee `../ko/model.json`: de KO solo se
recalcula lo que depende del precio (cierre de KO a la misma fecha de corte que PEP, de Yahoo).

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | Modelo completo → `model.json`: DCF por negocio (snacks / bebidas), suma de partes con EV/(EBITDA − capex), comparables con regresiones, reversión con ventana limpia y regla de cambio de escalón, consenso, blend 7.5/7.5/25/35/25 y bloque PEP vs. KO (`cmp`) |
| `pep.tpl.html` | Plantilla del informe (texto + tokens). `@@CSS@@` y `@@SCRIPT@@` los completa el build |
| `charts_pep.js` | `renderAll()` con los 16 gráficos (tokens para los datos del modelo) |
| `build.py` | Toma CSS y motor de gráficos de `informes/pg.html`, aplica los parches de KO y tres nuevos: escala fija en `drawGroupedBars` (`minV`/`maxV`, para los gráficos PEP y KO lado a lado), y huecos (`null`) en `drawLines` |
| `render.py` | Reemplaza tokens; agrega el formato `sg` (puntos con signo y medio punto: PepsiCo reporta +4.5, −2.5) |
| `verify.py` | Tokens vs. modelo, aritmética del blend de cinco métodos, celdas Base, grupos, puentes del DCF y de la suma de partes, **prueba de anti-circularidad** (corre el modelo con otro precio de PEP: comparables y suma de partes no pueden cambiar), "hoy/ayer/mañana", gate, logo |
| `index_add.py` / `manifest_add.py` | Conexión al sitio (una sola vez; el contador del panel se lee y se le suma 1) |
| `fetch_data.py` | Baja companyfacts (SEC), precios mensuales de PEP y KO, diarios de pares, Celsius y ^TNX (Yahoo) y consenso de EPS (Nasdaq, con headers de navegador) → `data/nasdaq_eps.json` |
| `xbrl.py` | Series anuales y semestrales de XBRL para revisar |
| `raw/dl.py`, `raw/dl_old.py`, `raw/totext.py` | Bajan 10-K, 10-Q y comunicados 8-K (2015-2026) de EDGAR y los pasan a texto (no se versionan) |
| `raw/eps_extract.py` | Extrae el EPS core y GAAP trimestral del encabezado de cada comunicado |
| `raw/sa_parse.py` | Lee las páginas de estadísticas de stockanalysis.com (bajadas a `raw/sa/`) → `data/sa_stats.json` |
| `data/` | Insumos versionados del modelo (consenso Nasdaq y estadísticas de pares) |

## Actualizar el próximo trimestre
1. `python fetch_data.py`; `cd raw && python dl.py && python totext.py && python eps_extract.py`; bajar
   `stockanalysis.com/stocks/<t>/statistics/` y `/forecast/` a `raw/sa/` y correr `python sa_parse.py`.
2. En `model.py`: `CUT` (fecha de corte), EPS trimestral nuevo en `EPS`, fila nueva en `ORG` (tabla "Organic Revenue
   Performance" y columnas de volumen unitario del comunicado) y en `NA` (PFNA y PBNA), balance (`DEBT`, `CASH`, `NCI`,
   `BS`, `EQM`), segmentos (`SEG`, `SEG_1H`), consenso de S&P Global (`REV_C26`, `OI_C26`, `FCF_C26`), precio objetivo
   (`CONS`), y revisar `SHOCK` si hay deterioros nuevos.
3. Si PepsiCo anuncia la refranquiciación del embotellado de Norteamérica: modelar PBNA sin la parte vendida y sumarla al
   precio de la operación (regla de unidades en venta de la skill); revisar el reparto snacks/bebidas.
4. `python model.py && python build.py && python verify.py` → 0 diferencias. Los `assert` del modelo atan frases del
   texto a los números (por ejemplo, "menos de la mitad", "el P/E más bajo de la década"): si uno falla, reescribir la frase.
5. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
