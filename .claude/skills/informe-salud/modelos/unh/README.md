# Modelo UNH (UnitedHealth Group) — informe-salud, Módulo C + conglomerado

Todo número derivado de `informes/unh.html` sale de `model.py`. El HTML se arma desde `unh.tpl.html`
con tokens `{{clave|formato}}` (mismo sistema que PG); `verify.py` compara el HTML contra el modelo y
tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | Modelo completo → `model.json` (datos de entrada arriba de cada bloque, con su fuente) |
| `unh.tpl.html` | Plantilla del informe (texto + tokens). `@@CSS@@` y `@@SCRIPT@@` los completa el build |
| `charts_unh.js` | `renderAll()` con los 11 gráficos (tokens para los datos del modelo) |
| `build.py` | Toma CSS y motor de gráficos de `informes/pg.html`, agrega `minV/maxV` a `drawLines`, renderiza `informes/unh.html` |
| `render.py` | Reemplaza tokens (formatos: usd0/usd2, f0-f3, x1/x2, pct/spct, a0/a1, js1/js2) |
| `verify.py` | Tokens vs. modelo, aritmética del blend, celdas Base de la grilla y del MLR, grupos, "hoy/ayer/mañana", gate, logo |
| `index_add.py` / `manifest_add.py` | Conexión al sitio (una sola vez; en una actualización solo hace falta volver a correr `manifest_add.py` si cambia el texto del cartel) |
| `fetch_data.py` | Baja precios (Yahoo) y consenso (Nasdaq/Zacks) |

## Actualizar el próximo trimestre
1. `python fetch_data.py` → copiar a `model.py`: `PRICE`, `RF`, consenso `C26/C27/C28` (y el año nuevo cuando
   cambie el calendario), precios y EPS de los pares en `PEERS`, `CONS` (stockanalysis `/forecast/`).
2. Del comunicado 8-K y el 10-Q nuevos: agregar el EPS ajustado del trimestre en `EPS`, el MLR en `MCRQ`, DCP en
   `DCP`, desarrollo de reservas (`pyd_*`), guía (`GUIDE_LO/HI`, `MCR_G26`, `OCF_G26`, resultado por segmento en
   `SEG`), balance (`DEBT`, `CASH_CE`, `CASH_FREE` — sale del MD&A "available for general corporate use" —, `NCI`),
   membresía (`MEMB`), acciones (`SH_DIL`, `SH_OUT`).
3. Revisar la ventana del MLR de mitad de ciclo (`MID_WIN`): cuando haya un 2026 real, reemplazar la guía por el dato.
4. Revisar la exclusión de la reversión (`reset`) y la regla de pares (`ratio < 75`).
5. `python model.py && python build.py && python verify.py` → 0 diferencias. Grep "hoy/ayer/mañana" ya lo hace verify.
6. Revisar el texto de la plantilla: fechas de corte, hechos del trimestre, riesgos y catalizadores (lo que no es número).
7. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
