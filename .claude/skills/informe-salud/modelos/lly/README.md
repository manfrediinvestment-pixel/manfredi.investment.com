# Modelo LLY (Eli Lilly and Company) — informe-salud, Módulo A (pharma)

Todo número derivado de `informes/lly.html` sale de `model.py`. El HTML se arma con el sistema de tokens `{{clave|formato}}`
de KO/PG/UNH; `verify.py` compara el HTML contra el modelo y tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `sotp.py` | Motor del Método 1: suma de partes por producto hasta la LOE + rNPV, I+D como línea corporativa, plataforma post-2040 |
| `sep_params.py` | Supuestos de la edición de septiembre (2T 2026) + formas calibradas `CAL` (ver abajo) |
| `calib_sep.py` | Calibración de las formas no publicadas contra los componentes publicados en septiembre (se corre a mano) |
| `dcf_inv.py` | DCF de referencia ("renovación perpetua") y DCF inverso (crecimiento que exige el precio) |
| `model.py` | Datos del 3T26, los cuatro métodos, blend, septiembre recalculado (`model_sep.json`), puentes y anti-circularidad → `model.json` |
| `lly.head.html` / `lly.body.tpl.html` / `engine.js` / `charts_lly.js` | Cabecera+CSS, texto con tokens, motor de gráficos de septiembre, datos de los gráficos |
| `build.py` | Ensambla y renderiza `informes/lly.html`; parchea el motor para celular (margen de `drawHBars`/`drawRangeBars`, leyenda de `drawLines` en varias filas) y agrega `drawDiverging` |
| `render.py` / `verify.py` | Tokens → HTML; HTML ↔ modelo, aritmética del blend, celda Base, puentes, gate, logo, gris, lenguaje relativo |
| `manifest_add.py` | Entrada nueva arriba de `informes/manifest.json` (y repara el abstract de septiembre) |
| `fetch_data.py`, `raw/dl_q.py`, `raw/totext.py` | Yahoo (precios, ^TNX, pares) y EDGAR (8-K, 10-Q, 10-K; User-Agent con mail tomado de los scripts de KO) |

## Reconstrucción de septiembre (el script original no se guardó)
Lo publicado en la tabla de supuestos se cargó tal cual. Lo no publicado (nivel 2026 de tirzepatida y del resto, rampas de
Foundayo/retatrutida/fase 3, cola de erosión post-LOE, factor de legados) se calibró por mínimos cuadrados contra los
componentes del Base, ingresos 2030/2031, margen de FCF 2030 e incretinas 2030/2035. Resultado contra lo publicado:

| Método / escenario | Publicado | Reconstruido | Dif. |
|---|---|---|---|
| M1 Base | $386.44 | $386.76 | +0.08% |
| M1 Bear | $221.03 | $240.46 | +8.8% (supuestos Bear no publicados) |
| M1 Bull | $643.14 | $603.20 | −6.2% (ídem) |
| Patente 2039 | $430.97 | $432.54 | +0.4% |
| Renovación | $662.39 | $648.29 | −2.1% |
| DCF de referencia | $723.66 | $722.81 | −0.1% (valor terminal a mitad de año) |
| M2 / M3 / M4 / blend | 750.91 / 1,168.81 / 1,325.00 / 986.03 | idénticos (M3 −$0.02 por redondeo de insumos) | — |

Varias formas quedaron en el borde de la banda de calibración (resto 2026 = 14.0, Foundayo 2027 = 0.5, tirzepatida 2026 =
52): son artefactos de la reconstrucción; en el 3T26 esos niveles se reemplazan por datos (mezcla del 3T escalada al 4T
implícito en la guía).

## Edición 3T 2026 (13-nov-2026)
- Blend $1,089.85 vs $1,427.28 (cierre 12-nov), −23.6%; septiembre $986.03 (−14.3% vs $1,150.99). Modelo +$104.04, precio −$0.22.
- M1 $481.04 (tirzepatida 2027 = 2026e × crecimiento del consenso de ingresos 2027; margen 2030 +2.5 pp por la guía de
  performance margin; fase 3 de 5 a 7 activos; AtaiBeckley y Curevo a costo; WACC 7.91%). M2 $878.49 (sin NVO $884.36).
  M3 $1,197.89 (cuatro cierres trimestrales, sale sep-25 y entra sep-26). M4 $1,515.22 (Nasdaq; stockanalysis $1,460).
- Deuda: corto ($2,517M) + largo ($46,986M) = $49,503M del 10-Q. Sin duplicación (el tag de largo plazo es solo la porción no corriente).
- Corregido: `.verdict-note` gris (#5d646f) → var(--muted); `drawHBars` con padL fijo de 250 px rompía la suma de partes en celular.

## Actualizar el próximo trimestre
1. `python fetch_data.py`; `cd raw && python dl_q.py <accesiones 8-K y 10-Q> && python totext.py`.
2. En `model.py`: datos del trimestre (sección 1), guía, balance, flujo de caja (FY/9M), `PRICE`, `RF`, `BETA`, consenso
   (Nasdaq desde Chrome: `api.nasdaq.com/api/analyst/LLY/earnings-forecast` y `/targetprice`), pares (stockanalysis desde
   Chrome) y la fila nueva de la reversión.
3. Copiar el `model.json` vigente como `model_3t26.json` y armar el puente contra él (en esta edición el puente es contra la
   reconstrucción de septiembre, `sep_params.py`).
4. `python model.py && python build.py && python verify.py` → 0 diferencias. `model.py` se re-corre solo con `LLY_PRICE`
   (precio anterior para el puente; precio +25% para la anti-circularidad).
5. Navegador: `?preview=full` en escritorio y 390 px, y sin el parámetro para el gate.
