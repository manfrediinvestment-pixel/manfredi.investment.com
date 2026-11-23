# Modelo COST (Costco Wholesale) — informe-consumo-masivo, bloque de retail con modelo de membresía

Todo número derivado de `informes/cost.html` sale de `model.py`. El HTML se arma desde `cost.tpl.html` con tokens
`{{clave|formato}}` (mismo sistema que WMT, KO y PEP); `verify.py` compara el HTML contra el modelo y tiene que dar
**0 diferencias** antes de publicar.

## Ediciones
- 23-nov-2026: informe inicial. Datos al 4T FY2026 (10-K del 7-oct-2026) + ventas de septiembre y octubre de 2026; precio del
  20-nov-2026 ($1,102.15, con el dividendo especial de $30 incluido). Blend $758.59 (−31.2%), neutral con sesgo bajista.

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | Modelo completo → `model.json`. Lee el bloque compartido `_compartido/defensivos_nov26.json` (precio, Treasury, ERP, consenso, S&P) y los pares de `modelos/wmt/model.json`. Acepta `COST_PRICE_OVERRIDE` / `COST_MODEL_OUT` (anti-circularidad) |
| `cost.tpl.html` | Plantilla del informe (texto + tokens). `@@CSS@@` y `@@SCRIPT@@` los completa el build |
| `charts_cost.js` | `renderAll()` con 19 gráficos; en menos de 560 px: rótulos cortos ('16, "3T 24"), últimos 8 trimestres en las barras agrupadas y valores sin unidad para que no se encimen |
| `build.py` | CSS y motor de `_motor/pg_motor_sep2026.html` + parches de KO/PEP (gris → `--muted`, `minV/maxV`, leyendas en varias filas, grilla de las barras agrupadas, nulls en `drawLines`) + rombo con un decimal (WMT) → `informes/cost.html` |
| `render.py` | Reemplaza tokens (copia del de WMT) |
| `verify.py` | Tokens vs. modelo, blend 7.5/7.5/25/35/25, grupos independientes/anclados (tabla y verdict-bar), celdas Base, cierre del DCF por negocio, anti-circularidad (corre el modelo a $700), lenguaje relativo, grises, gate, logo |
| `index_add.py` | Reemplaza la tarjeta "Próximamente" de COST del panel Defensivos por la activa (acento `down`, sparkline). **No toca el contador "N de 10"**: lo actualiza la integración. Conserva los CRLF de `index.html` |
| `manifest_add.py` | Agrega la entrada de COST al principio de `informes/manifest.json` |
| `fetch_data.py` | Corre `data/fetch_sec.py` + `data/annual.py` y baja las ventas mensuales (PDF → `data/monthly/*.txt`) |
| `data/fetch_sec.py`, `data/annual.py`, `data/extract_q.py` | EDGAR (CIK 0000909832, User-Agent genérico), serie anual XBRL, extracción de los estados trimestrales de los comunicados |

## Integración (rama de integración, no en esta)
```
python .claude/skills/informe-consumo-masivo/modelos/cost/index_add.py
python .claude/skills/informe-consumo-masivo/modelos/cost/manifest_add.py
node scripts/catalogo-informes.mjs      # regenera informes/catalogo.json (lo corre también el workflow diario)
```
y subir a mano el contador del panel Defensivos. Catálogo: no hace falta script propio; `catalogo-informes.mjs` lee el HTML.

## Actualizar (1T FY2027, ~10-dic-2026)
1. `python fetch_data.py` (o solo `data/fetch_sec.py`) y `python data/extract_q.py` para el comunicado nuevo.
2. En `model.py`: trimestre nuevo en `COMP`, `TRX`, `TKT_PUB`, `DIG`, `COMP_REP`, `MQ`/`MEMQ` (renovación, socios, Executive, cuotas);
   `EPS[2027][0]`; `FEEQ`/`OIQ`/`NSQ`; balance (`CASH`, `DEBT`, después del dividendo especial); precio y consenso (bloque compartido
   nuevo o stockanalysis); `PHI` (días transcurridos del año fiscal). Revisar la regla de cambio de escalón: al 20-nov-2026 se cumple por 1.5%.
3. `python model.py && python build.py && python verify.py` → 0 diferencias. Releer los asserts de texto si alguno falla.
4. Navegador: `?preview=full` en escritorio y 390 px, y sin `?preview=full` para el gate.
