# Modelo KO (The Coca-Cola Company) — informe-consumo-masivo, bebidas sin alcohol

Todo número derivado de `informes/ko.html` sale de `model.py`. El HTML se arma desde `ko.tpl.html` con tokens
`{{clave|formato}}` (mismo sistema que PG y UNH); `verify.py` compara el HTML contra el modelo y tiene que dar
**0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | Modelo completo → `model.json` (datos de entrada arriba de cada bloque, con su fuente) |
| `ko.tpl.html` | Plantilla del informe (texto + tokens). `@@CSS@@` y `@@SCRIPT@@` los completa el build |
| `charts_ko.js` | `renderAll()` con los 11 gráficos (tokens para los datos del modelo) |
| `build.py` | Toma CSS y motor de gráficos de `informes/pg.html`, aplica tres parches para celular (leyenda de `drawLines` en varias filas, grilla de `drawGroupedBars` cada 2 o 5 puntos, rótulos de los rombos más chicos) y renderiza `informes/ko.html` |
| `render.py` | Reemplaza tokens (formatos: usd0/usd2, f0-f3, x1/x2, pct/spct, spp0, a0/a1, js1/js2) |
| `verify.py` | Tokens vs. modelo, aritmética del blend, celdas Base (grilla y volumen), grupos, puente del DCF, anti-circularidad, "hoy/ayer/mañana", gate, logo |
| `index_add.py` / `manifest_add.py` | Conexión al sitio (una sola vez; `index.html` se escribe con CRLF como está en el working tree) |
| `fetch_data.py` | Baja companyfacts (SEC), precios de KO, pares, participaciones y tipos de cambio (Yahoo) |
| `xbrl.py` | Series anuales y semestrales de XBRL para revisar (`raw/xbrl_series.json`) |
| `raw/dl.py`, `raw/dl_old.py`, `raw/totext.py` | Bajan 10-K, 10-Q y comunicados 8-K (2015-2026) de EDGAR y los pasan a texto. Los `.htm/.txt/.json` de `raw/` no se versionan (111 MB) |

## Actualizar el próximo trimestre
1. `python fetch_data.py`, `cd raw && python dl.py && python totext.py`.
2. En `model.py`: `PRICE`, `RF`, consenso `C26/C27/C28` (Nasdaq), `REV_C26`, EPS trimestral nuevo en `EPS`, fila nueva en
   `ORG` (tabla "Revenues and Volume" del comunicado; si la compañía vuelve a cuantificar la inflación intensa, cargarla en
   `INFL`), balance (`DEBT`, `CASH`, `NCI`, `BS`), `OCF_G26/CAPEX_G26` (guía), precios de los pares en `PEERS` y consenso de
   stockanalysis en `CONS`.
3. Cuando cierre la venta de CCBA: sacar el ajuste `CCBA_REV/CCBA_FCF` de la base, reemplazar `CCBA_VAL` por la caja cobrada
   (41.52%) + el 25% retenido, y revisar `NCI`.
4. Cuando falle el Undécimo Circuito: si gana, sumar el reintegro a los activos no operativos; si pierde, restar la
   contingencia y subir la tasa efectiva 3.8 puntos en el margen de caja.
5. `python model.py && python build.py && python verify.py` → 0 diferencias.
6. Revisar el texto de la plantilla (fechas de corte, hechos del trimestre, riesgos y catalizadores).
7. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
