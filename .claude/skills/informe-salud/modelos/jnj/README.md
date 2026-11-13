# Modelo JNJ (Johnson & Johnson) — informe-salud, conglomerado (Módulo A + Módulo B)

Todo número derivado de `informes/jnj.html` sale de `model.py`. El HTML se arma con el sistema de tokens `{{clave|formato}}`
de LLY/KO/PG; `verify.py` compara el HTML contra el modelo y tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `sotp.py` | Motor del Método 1: Innovative Medicine producto por producto hasta la LOE + rNPV de fase 3, I+D como línea corporativa, plataforma post-2040; MedTech por DCF con perpetuidad |
| `sep_params.py` | Supuestos de la edición de septiembre (2T 2026) + formas calibradas `CAL` |
| `calib_sep.py` / `check_sep.py` | Calibración de lo no publicado contra los componentes publicados (se corre a mano) / comparación de escenarios publicados vs reconstruidos |
| `model.py` | Datos del 3T26, los cuatro métodos, blend, septiembre recalculado (`model_sep.json`), puentes y anti-circularidad → `model.json` |
| `jnj.head.html` / `jnj.body.tpl.html` / `engine.js` / `charts_jnj.js` | Cabecera+CSS (`.verdict-note` en var(--muted)), texto con tokens, motor de gráficos de septiembre, datos de los gráficos |
| `build.py` | Ensambla y renderiza `informes/jnj.html` con los mismos parches de celular que LLY (`drawHBars`/`drawRangeBars` con margen limitado, leyenda de `drawLines` en varias filas) |
| `render.py` / `verify.py` | Tokens → HTML; HTML ↔ modelo, aritmética del blend, reparto IM/MedTech, puentes, deuda, gate, logo, gris, lenguaje relativo |
| `manifest_add.py` | Entrada nueva arriba de `informes/manifest.json` |
| `fetch_data.py`, `raw/dl_q.py`, `raw/totext.py`, `raw/parse_prod.py` | Yahoo (JNJ, ^TNX, pares) y EDGAR (8-K, 10-Q; User-Agent con mail tomado de `informe-consumo-masivo/modelos/pep/raw/dl.py`); ventas por producto del Exhibit 99.2 → `raw/prod.json` |

## Reconstrucción de septiembre (el script original no se guardó)
Lo publicado en la tabla de supuestos y en el texto de la Sección 13 se cargó tal cual. Lo no publicado (nivel 2026 de cada
producto, años de pico de las rampas, cola de erosión después del año 2, crecimiento de Darzalex resto del mundo 2030,
crecimiento y meseta del grupo "otros", rampa de fase 3, inicio de la desaceleración de MedTech) se calibró por mínimos
cuadrados contra los componentes del Base, el valor de MedTech y su peso en la perpetuidad, ingresos de IM 2030/2035,
ingresos totales 2027, el fair value Base y el escenario de fechas tardías.

| Método / escenario | Publicado | Reconstruido | Dif. |
|---|---|---|---|
| M1 Base | $97.56 | $97.64 | +0.1% |
| M1 Bear | $68.30 | $75.13 | +10.0% (supuestos Bear no publicados completos) |
| M1 Bull | $163.58 | $154.23 | −5.7% (ídem) |
| Fechas más tardías | $113.18 | $114.45 | +1.1% |
| Erosión lenta | $100.47 | $100.57 | +0.1% |
| Sin fase 3 | $92.18 | $91.79 | −0.4% |
| Renovación | $146.36 | $129.29 | −11.7% (no se publicó si el valor terminal reemplaza o se suma a la plataforma; se usa la definición de LLY: VT sobre el flujo total de 2045, sin plataforma) |
| Beta propia | $108.61 | $108.66 | +0.0% |
| Grilla WACC × probabilidad | — | dentro de ±0.3% en la fila Base | — |
| DCF de referencia | $215.43 | $215.47 | (WACC ponderado por valor de empresa, mitad de año, margen 22.7% → 25% en 2031) |
| M2 / M3 / M4 / blend | 193.08 / 192.16 / 277.91 / 199.64 | idénticos al centavo (blend +$0.01 por M1) | — |

Formas en el borde de la banda: `sm_tail` (cola de moléculas pequeñas tras el año 2) quedó en ~0 y `dara_g_late` alto;
son artefactos de la reconstrucción. Inconsistencia de septiembre: el football field usaba $286.71 como techo del M2 y la
tabla $285.59 (la tabla es la correcta: 27.63x Lilly / 17.84x Abbott sobre $12.14).

## Edición 3T 2026 (13-nov-2026)
- Trimestre cerrado el 27-sep-2026 (8-K del 13-oct, 10-Q del 21-oct). Precio: cierre del 12-nov-2026, $283.52; ^TNX 5.103%.
- Blend $205.56 (−27.5%); septiembre $199.64 (−25.8% vs $269.17). Cambio +$5.92: modelo +$5.94, precio −$0.02 (solo peso
  de la deuda en el WACC). La brecha se amplía 1.7 pp: la suba de la acción la amplía 3.9 pp y el modelo la achica 2.2 pp.
- M1 $85.94 (−$11.62): margen de caja TTM (OCF 26.3% vs 28.2%) −$9.70; reserva total de talco $9.0B en vez de $5.5B
  −$1.43 (cambio metodológico: la reserva de junio ~$3.7B no se restaba); MedTech 4.0% vs 4.5% −$0.89; niveles 2026
  −$0.80; WACC +$0.34; deuda neta y acciones +$0.78.
- I+D del ancla de margen sin el cargo de Firefly ($964M, no-caja, sumado de vuelta en OCF y pagado en inversión).
- M2 $200.91 (EPS 2027 Nasdaq $11.56; cuartiles 18.78x pharma / 18.66x medtech; reparto 76.4% IM con el resultado ajustado
  de 9M26). Sin Lilly (el par que más se aleja de la mediana): $192.91, blend $203.57.
- M3 $201.36 (sale jun-24, entra sep-26 a 24.86x; EPS TTM $10.65 con Firefly/Sail adentro, regla del marco).
- M4 $287.88 (Nasdaq, 17 analistas). En septiembre se usó stockanalysis ($277.91); hoy daría $279.41 → blend $203.45.
- Deuda: corto ($8,852M) + largo no corriente ($35,799M) = $44,651M (10-Q: $44.6B). `LongTermDebt` del XBRL incluye la
  porción corriente: no usar.
- DePuy Synthes: fuera del Base (sin Form 10 ni fecha firme); escenario venta a $20B → M1 $82.92.
- Corregido: `.verdict-note` gris (#5d646f) → var(--muted).

## Actualizar el próximo trimestre
1. `python fetch_data.py`; `cd raw && python dl_q.py <accesiones 8-K y 10-Q> && python totext.py && python parse_prod.py`
   (primero aplanar los Exhibit 99.2 a `*_flat.txt`, ver el bloque en el historial de esta edición o repetir el regex de `parse_prod.py`).
2. En `model.py`: accesiones en `P[...]`, datos del trimestre, guía, balance, flujo (FY/9M), `CUT`, consenso (Nasdaq desde
   Chrome: `api.nasdaq.com/api/analyst/JNJ/earnings-forecast` y `/targetprice`), pares (stockanalysis `/statistics/` desde
   Chrome) y la fila nueva de la reversión.
3. El puente se arma contra `model_3t26.json` (copia del `model.json` de esta edición).
4. `python model.py && python build.py && python verify.py` → 0 diferencias.
5. Navegador: `?preview=full` en escritorio y 375 px (Playwright + Chrome local si la extensión no llega a 127.0.0.1), y sin el parámetro para el gate.
