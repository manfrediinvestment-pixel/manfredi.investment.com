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

## Edición 3T 2026 (12-nov-2026)
- Blend $79.03 vs. $97.57 (cierre 11-nov), −19.0%; septiembre $75.99 (−12.5% vs. $86.84). Modelo +$3.10, precio −$0.06.
- Bull: volumen = promedio de los últimos cuatro trimestres (antes 2.5% fijo; con el Base en 2.25% ya no se distinguía).
- Corregido: la deuda de CCBA en pasivos en venta al 3-jul-2026 era $1,452 millones (septiembre citaba $584, solo la
  porción corriente). La nota de portada (`.verdict-note`) heredaba gris `#5d646f` de pg.html: `build.py` la pasa a
  `var(--muted)`.
- stockanalysis se leyó durante la rueda: `PEERS` guarda EV, capitalización y precio de la fuente (`ev_sa`, `mc_sa`,
  `px_sa`) y el modelo lleva EV/EBITDA y rendimientos al cierre de corte.
- El 3T26 sumó Singapur, Malasia y Myanmar a "mantenidas para la venta" (cierre ~mediados de 2027): cuando se conozca el
  precio, tratarlas como CCBA.

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
   `model.py` se vuelve a correr solo (variable `KO_PRICE`) dos veces: con el precio de la edición anterior, para el puente
   "modelo vs. precio" contra `model_2t26.json` (copia del `model.json` publicado en septiembre; en la próxima edición,
   copiar el `model.json` vigente como `model_3t26.json` y apuntar `OLD` ahí), y con el precio +25%, para verificar que
   comparables, reversión y consenso no dependen del precio de KO. Los `assert` que atan frases del texto a los números
   solo corren con el precio de corte (`TXT`).
6. Revisar el texto de la plantilla (fechas de corte, hechos del trimestre, riesgos y catalizadores).
7. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
