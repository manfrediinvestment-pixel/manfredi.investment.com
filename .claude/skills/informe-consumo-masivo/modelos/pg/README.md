# Modelo PG (The Procter & Gamble Company) — informe-consumo-masivo, cuidado personal y del hogar

Todo número derivado de `informes/pg.html` sale de `model.py`. El HTML se arma desde `pg.tpl.html` con tokens
`{{clave|formato}}`; `verify.py` compara el HTML contra el modelo y tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `model.py` | `run(D)` arma el modelo completo para una edición. `run(SEP)` reproduce la edición de septiembre (assert contra 48 cifras publicadas, la grilla 5×5, los 40 P/E de la reversión y la regresión de volumen) → `model_sep.json`; `run(NOV)` arma la edición 1T FY2027 → `model.json`, con el puente contra septiembre y la prueba de anti-circularidad |
| `pg.tpl.html` | Plantilla del informe. `@@CSS@@` y `@@ENGINE@@` los completa el build |
| `build.py` | CSS y motor de gráficos de `../_motor/pg_motor_sep2026.html` (copia congelada del pg.html de septiembre, que también usan KO, PEP, WMT y UNH), parches de KO, `.verdict-note` a `var(--muted)` (cero gris), `pointLabels` en `drawLines` |
| `render.py` | Reemplaza tokens (mismos formatos que KO) |
| `verify.py` | Tokens vs. modelo, aritmética del blend, celdas Base, grupos, puentes, anti-circularidad (corre el modelo con `PG_PRICE=130`), "hoy/ayer/mañana", gate, logo, grises |
| `manifest_add.py` | Entrada de la edición al principio de `informes/manifest.json` (después: `node scripts/catalogo-informes.mjs`) |
| `fetch_data.py` | Precios de Yahoo (PG mensual 15 años; diarios de PG, pares, ^TNX, ^GSPC) → `yh/` |
| `raw/dl.py`, `raw/totext.py` | Bajan de EDGAR los comunicados 8-K 2.02 (desde 2016), 10-K/10-Q (desde 2024) y companyfacts; el User-Agent con el contacto se lee de `../pep/raw/dl.py` |
| `raw/sa_parse.py` | Estadísticas de stockanalysis (bajar con curl a `raw/sa/<t>.stats.html`) → `data/sa_stats.json` |
| `data/nasdaq_eps.json` | Consenso de EPS (Nasdaq devuelve 403 a scripts: se lee con `fetch` desde una pestaña de nasdaq.com) |

## Reconstrucción de septiembre (el modelo original no se guardó)
- Reproduce al centavo DCF Bear/Base/Bull, EV, % en perpetuidad, grilla, sensibilidades, DCF inverso, reversión (40 P/E),
  consenso, blend y grupos. Despejado: la capitalización de la fuente ($339.27 mil millones; las 25 celdas de la grilla la
  acotan a 339.255-339.29), la mezcla del Base (0.4, la de la tabla; el texto decía 0.38), Bear con precio 1.0/1.0/1.5 y Bull
  con margen lineal 22.5 → 23.5 y capex 4.75 → 4.5 desde el FY2028, y la compensación en acciones como % de las ventas.
- Residuos (`model_sep.json`, `sep_residuals`): Bull $158.575 (publicado $158.58), DCF con margen FY2026 $116.015 ($116.02),
  Método 2 $122.829 ($122.82; EV/EBITDA $120.69 vs $120.67, piso $117.70 vs $117.68, techo $166.77 = ok). La deuda neta con
  arrendamientos que usó septiembre en el EV/EBITDA no se pudo identificar (~$25.3 mil millones contra $25.22 de la tabla).
- No reproducibles: las regresiones de P/E contra crecimiento del EPS (R² 0.12/0.24): el crecimiento de cada par no se publicó.
- Deuda: P&G no usa `LongTermDebt` en XBRL; `LongTermDebtNoncurrent` excluye la porción corriente (que está en `DebtCurrent`).
  Septiembre sumó bien, sin duplicar.

## Edición 1T FY2027 (13-nov-2026, precio al 12-nov)
- Blend $148.32 vs. $168.03 (−11.7%); septiembre $143.76 (−1.7% vs. $146.23). Modelo +$4.72, precio −$0.16 (contra las cifras publicadas de septiembre, no las reconstruidas).
- Cambios de método (reglas de la skill posteriores a PG): comparables con mediana, P/E de 12 meses y EV/EBITDA de 12 meses
  (antes promedio y FY2028 descontado), grupo de 7 (KO, PEP, CL, KMB, CHD, CLX, UL; sale KVUE); margen del DCF = año real +
  guía del año en curso (antes dos años reales: −$2.63 en el DCF); se restan minoritarios; ventana de reversión móvil (40
  cierres hasta el último trimestre) con regla de escalón simétrica.
- KMB fuera de la mediana de EV/EBITDA: cerró Kenvue el 2-nov (EV con Kenvue, EBITDA sin Kenvue).

## Actualizar el próximo trimestre
1. `python fetch_data.py`; `cd raw && python dl.py && python totext.py`; stockanalysis con curl + `python raw/sa_parse.py`;
   consenso de Nasdaq desde el navegador a `data/nasdaq_eps.json`.
2. Copiar `model.json` como `model_1t27.json`; en `model.py`: crear `NOV`→ edición nueva (`CUT`, `rf`, balance, EBITDA de
   12 meses, `sh_dil`, consenso, `spx_pe`), fila nueva en `ORGQ` y `Q8`, EPS del trimestre en `EPS_Q`/`eps_fill`, `Q1`/`SEGQ`,
   y apuntar el puente a la edición anterior.
3. `python model.py && python build.py && python verify.py` → 0 diferencias. `chk()` ata frases del texto a números.
4. Navegador: `?preview=full` en escritorio y 375 px (la extensión de Chrome a veces no llega a 127.0.0.1: Playwright + Chrome local).
