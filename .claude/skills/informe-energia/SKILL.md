---
name: informe-energia
description: "Use when writing or updating institutional-grade equity research for energy / petróleo y gas en la sección 'Inversiones' de manfredi.investment.com — integradas / supermajors (XOM, CVX, SHEL, TTE, BP, EQNR), exploración y producción / E&P (COP, EOG, OXY, DVN, FANG, EQT, VIST, YPF), midstream / oleoductos (ENB, EPD, ET, KMI, WMB, OKE, TRGP) y refinación (MPC, VLO, PSX). Reemplaza el DCF a perpetuidad y el P/E histórico de informe-bigtech por el marco que usan los fondos de energía: todo valuado a un precio de commodity de mitad de ciclo (no spot), NAV de reservas, EV/DACF y EV/EBITDA a mitad de ciclo, breakeven de caja, ROACE a lo largo del ciclo, reemplazo de reservas, disciplina de capex y retorno total al accionista; en midstream, EV/EBITDA, cobertura de distribución, apalancamiento y % de ingresos por tarifa. Mismo esqueleto de 15 secciones y mismo gate de vista previa. Trigger on: 'informe de [ticker de energía]', 'análisis de [XOM/CVX/COP/OXY/EPD/VIST/YPF/etc.]', 'tesis de [petrolera]', 'price target de [petrolera/oleoducto]', earnings/10-Q/10-K de un nombre de energía bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Energía (Petróleo y Gas) — Manfredi Investment

Escribís research al nivel de una mesa institucional de energía. Mismo rigor que `informe-bigtech`,
pero con una diferencia de fondo que cambia todo: **la variable más importante del valor no la
controla la empresa** — es el precio del crudo y del gas. Por eso los fondos de energía no preguntan
"¿cuánto gana?" sino **"¿cuánto gana a un precio normal de mitad de ciclo, a qué precio deja de
cubrir el dividendo, y cuántos años de reservas le quedan?"**. Un informe de energía que valúa con el
precio spot del día del informe está valuando el precio del petróleo, no la compañía.

**Relación con informe-bigtech:** todo lo que no se menciona acá (regla de oro, cero lenguaje
relativo a fechas, disclaimer, precio único en portada, motor Canvas, bug de `drawHBars`, conexión al
sitio, verificación con script) aplica igual. Lo que sigue son las diferencias.

## Regla de oro (idéntica)

**El modelo dice lo que dice** — y en energía hay una trampa adicional: el mismo modelo da números
opuestos según el precio del commodity que le pongas. Nunca elijas el precio del commodity para
acercar el fair value al precio de mercado. El deck de precios se fija **antes** de valuar, con
fuente, y se reporta la sensibilidad completa.

## Regla no-negociable: el deck de precios de commodity

Todo método intrínseco y todo múltiplo sobre EBITDA/flujo proyectado se calcula con **tres decks
fijos y sourceados**, nunca con el spot:

- **Base = mitad de ciclo**: precio de largo plazo del crudo (Brent y WTI) y del gas (Henry Hub; TTF
  si la compañía vende en Europa/GNL) — anclalo en (a) el precio de planificación que la propia
  compañía divulga para su plan de capital, (b) la proyección de largo plazo de la EIA (STEO para los
  próximos 2 años, AEO para largo plazo) y (c) la curva de futuros a 3-5 años (backend del strip).
  Citá los tres y elegí uno explícito. Como referencia de orden de magnitud, muchos decks de
  planificación de la industria rondan WTI ~$60-70/bbl y Henry Hub ~$3-4/MMBtu — **verificalo a la
  fecha, no lo copies**.
- **Bear**: un precio que la industria ya vivió en un bajón reciente (ej. el promedio de un año
  malo real), no un número arbitrario.
- **Bull**: strip de futuros si está por encima del Base, o el promedio de un año alto reciente.

Precios de referencia de 2026 para contexto (verificá a la fecha de corte): el Brent tocó ~$138 y se
acomodó cerca de ~$89 en 2026, tras un 4Q2025 en la zona de $60-70. Esa volatilidad es exactamente la
razón por la que la valuación no puede anclarse en el spot de un día.

## Paso 0 — clasificar la sub-industria

| Sub-industria | Ejemplos | Qué valúan los fondos | Método intrínseco |
|---|---|---|---|
| Integradas / supermajors | XOM, CVX, SHEL, TTE, BP, EQNR | Upstream + refinación + química + GNL + transición; ROACE del ciclo; retorno total | SOTP (NAV upstream + EV/EBITDA mid-cycle downstream/química) |
| E&P | COP, EOG, OXY, DVN, FANG, EQT, CTRA, VIST, YPF (upstream) | Reservas, inventario de pozos, costo, breakeven | NAV de reservas (PV-10) |
| Midstream | ENB, EPD, ET, KMI, WMB, OKE, TRGP, MPLX | Flujo por tarifa, contratos, cobertura, apalancamiento | DCF de flujo distribuible / DDM |
| Refinación | MPC, VLO, PSX | Márgenes de refinación (crack spread) a mitad de ciclo, captura, utilización | DCF / EV/EBITDA mid-cycle |

**Argentina (YPF, VIST, PAM, TGS):** mismo marco, más riesgo país explícito (sumá el spread de
riesgo soberano al costo de equity, citando el valor vigente), régimen de precios local vs. paridad
de exportación, RIGI y controles de cambio/exportación vigentes, e inventario de Vaca Muerta. YPF es
integrada (usar SOTP), VIST es E&P pura (NAV).

## Antes de empezar — datos reales

1. **XBRL (SEC EDGAR)** — endpoint y `User-Agent` de informe-bigtech. Tags estándar + específicos
   de petróleo y gas (divulgación suplementaria del 10-K, anual):
   - `ProvedDevelopedAndUndevelopedReservesNet` (reservas probadas, por producto — eje de crudo, gas,
     NGL; convertí a barriles equivalentes a 6 mcf = 1 boe).
   - `StandardizedMeasureOfDiscountedFutureNetCashFlowsRelatingToProvedOilAndGasReserves`
     (**"SMOG"**: valor presente al 10% de las reservas probadas a precios SEC — es un piso
     contable, no el fair value; ver regla abajo).
   - `CostsIncurredDevelopmentCosts`, `CostsIncurredExplorationCosts`,
     `CostsIncurredAcquisitionOfProvedOilAndGasProperty`,
     `CostsIncurredAcquisitionOfUnprovedOilAndGasProperties` → costo de hallazgo y desarrollo (F&D).
   - `ResultsOfOperationsExpenseExploration`, `AssetRetirementObligation` (costo de abandono,
     se resta en el NAV), `DepreciationDepletionAndAmortization`.
   - Filers extranjeros (SHEL, TTE, BP, EQNR, YPF, VIST) reportan en 20-F/IFRS: tags `ifrs-full`
     o directamente el 20-F/informe anual.
2. **Producción y precios realizados — NO vienen limpios en XBRL**: del comunicado trimestral y el
   suplemento financiero/operativo: producción (kboe/d por producto y región), precio realizado vs.
   benchmark, costo de producción (lifting cost $/boe), y en integradas las utilidades por segmento
   (upstream, energy products/refinación, chemical, specialty) con los factores de explicación
   (precio, volumen, márgenes, timing effects).
3. **Sensibilidades divulgadas por management**: casi todas las majors y E&P publican el impacto en
   utilidades/flujo por cada ±$1 o ±$10/bbl de crudo y ±$0.10-1/MMBtu de gas, y por cada ±$1/bbl
   de margen de refinación. Usalas — no las inventes.
4. **Plan de capital y breakeven**: capex guiado, crecimiento de producción guiado, breakeven de
   caja (precio que cubre capex de mantenimiento + dividendo) que divulga la compañía (ej. CVX
   indica breakeven upstream por debajo de $50/bbl), marco de retorno al accionista (ej. XOM
   recompras planificadas de $20B en 2026 y 43 años de aumentos de dividendo; SHEL bajó la recompra
   trimestral de $3.5B a $3.0B en 1Q2026 mientras subía el dividendo 5%).
5. **Precio y peers** — Yahoo, igual que informe-bigtech. **Deck de commodities** (ver regla arriba):
   EIA STEO, curva de futuros (CME vía WebSearch), deck propio de la compañía.

## El entregable: mismas 15 secciones, contenido adaptado

1. Portada — igual, más **el deck de precios usado**, en una línea debajo del fair value (ej.
   "Valuado a Brent $70 / Henry Hub $3.50 de mitad de ciclo").
2. Resumen Ejecutivo — la tesis responde: ¿cuánto vale a precio normal, cuál es su breakeven, y
   qué te da (dividendo + recompra) mientras esperás?
3. Historia y Evolución — fusiones grandes (XOM-Pioneer, CVX-Hess, COP-Marathon, etc.) y ciclos.
4. **Activos, Segmentos y Reservas** — segmentos reales; producción por región/cuenca; reservas
   probadas (1P) y vida de reservas (R/P = reservas ÷ producción anual, en años); **inventario de
   pozos** en E&P de shale (años de locaciones de primer nivel al ritmo actual de perforación — en
   shale importa más que las reservas probadas); en integradas, capacidad de refinación, química y
   GNL; en midstream, km de ductos, capacidad, cuencas y % de ingresos por tarifa/take-or-pay.
5. Desarrollos Recientes — guía de producción y capex, M&A, arranques de proyectos grandes.
6. **Estados Financieros** — utilidad por segmento, **precio realizado vs. benchmark**, costo de
   producción $/boe, margen de caja por boe (netback), ROACE (retorno sobre capital empleado promedio
   — la métrica de rentabilidad que usan las majors entre sí) **mostrado a lo largo de un ciclo
   completo (≥8-10 años)**, no solo el último año.
7. **Deuda y Balance** — deuda neta/EBITDA y gearing (deuda neta ÷ (deuda neta + equity)), a precio
   de mitad de ciclo y a precio Bear (¿el balance aguanta un año malo sin cortar dividendo?);
   obligaciones de abandono (ARO).
8. **Flujo de Caja y Retorno al Accionista** — flujo operativo, capex de mantenimiento vs. de
   crecimiento, FCF, **breakeven de caja** (propio calculado + el divulgado), dividendo + recompra
   = **retorno total al accionista (shareholder yield)**, marco de retorno (fijo + variable, % del
   FCF comprometido), y qué hizo la compañía con la recompra en el último bajón.
9. **Comparables** — EV/EBITDA (EV/EBITDAX en E&P) y EV/DACF a **precios de mitad de ciclo**, P/CF,
   FCF yield y dividend yield, de 3-4 peers de la misma sub-industria.
10. Gobierno Corporativo — igual, más política de transición energética (metas de emisiones que
    condicionan capex en las europeas) y activismo (Elliott en BP, etc.).
11. **Registro de Riesgos** — ver lista abajo.
12. **Catalizadores** — reuniones de OPEP+, arranque de proyectos (ej. Guyana, GNL), M&A, datos de
    inventarios (EIA semanal), guía anual de capex (diciembre-febrero), resultados de refinación
    estacionales (driving season).
13. Modelo Proyectado y Momentum de Estimados — consenso de EPS/flujo **indicando qué precio de
    commodity implica el consenso** (los analistas lo actualizan con el strip; decilo).
14. **Valuación** — ver metodología abajo.
15. Limitaciones del Modelo — incluir siempre: sensibilidad al commodity, riesgo de estimación de
    reservas, riesgo de transición de largo plazo.

## Riesgos específicos del sector (Sección 11)

- **Precio del commodity** (cuantificado con la sensibilidad divulgada: "cada −$10/bbl resta ~$X de
  flujo anual"), OPEP+ y su capacidad ociosa, demanda china, recesión.
- **Declino de producción** (shale declina rápido: sin perforar, un pozo nuevo pierde gran parte de
  su producción el primer año) y agotamiento de inventario de primer nivel.
- **Costos/inflación de servicios**, aranceles al acero (casing/tubing).
- **Márgenes de refinación** (crack spreads) y paradas de planta.
- **Transición energética y regulación** (impuestos a ganancias extraordinarias en Europa, metas de
  emisiones, metano), litigios climáticos.
- **Geopolítica** (sanciones, estrechos, expropiación — relevante en Argentina y mercados
  emergentes), riesgo cambiario y de controles en Argentina.
- **Ejecución de megaproyectos** y de integraciones de M&A.

## Metodología de valuación

**Costo de capital:** WACC con CAPM (beta de peers — energía tiene betas ~0.8-1.2) + costo de deuda.
En NAV la convención de la industria es descontar al **10%** (PV-10), con 8% para activos de bajo
riesgo y 12%+ para jurisdicciones riesgosas — documentá la tasa elegida.

**Pesos del blend** (consenso y reversión siempre entran, misma lógica que informe-bigtech):

1. **Método intrínseco a precio de mitad de ciclo — 15%**:
   - **E&P → NAV de reservas**: flujo de caja de la vida completa de las reservas probadas +
     probables (con curva de declino) + valor del inventario no desarrollado (a un riesgo explícito),
     menos G&A corporativo en valor presente, deuda neta y ARO, ÷ acciones diluidas. Descuento 10%.
   - **Integradas → SOTP**: NAV del upstream + EV/EBITDA de mitad de ciclo para refinación, química,
     GNL y comercialización (múltiplos de peers puros de cada negocio: refinadoras para downstream,
     químicas para chemical) − deuda neta. Explicitá el múltiplo de cada pieza y de dónde sale.
   - **Midstream → DCF del flujo distribuible** (o DDM de la distribución si la cobertura es sana) con
     crecimiento anclado en proyectos ya sancionados y contratados, no en "crecimiento de la cuenca".
   - **Refinación → DCF** con márgenes de refinación de mitad de ciclo (promedio de crack spreads de
     un ciclo completo, no el del trimestre).
   Tres escenarios = los tres decks de precios (Bear/Base/Bull). Reportá también el valor esperado
   ponderado 25/45/30.
2. **Comparables — 25%**: EV/DACF (E&P grandes cotizan típicamente ~3-6x, operadores premium 6-8x;
   "la vida de reservas pone el techo": una E&P con 9 años de reservas no justifica el múltiplo de
   una con 18 a igual margen), EV/EBITDA (EBITDAX en E&P: ~3-6x productores maduros, 4-8x de
   crecimiento), midstream EV/EBITDA; **siempre sobre EBITDA/flujo proyectado al precio Base**, no
   sobre el TTM de un año de precio extremo.
3. **Reversión histórica — 35%**: **acá la regla es la opuesta a la de bancos/tech.** En energía el
   ciclo ES el régimen: la ventana tiene que cubrir **un ciclo completo (≥10 años, incluyendo un
   bajón como 2015-2016 o 2020)**, no los últimos 2-3 años. Y **nunca uses P/E**: en un cíclico el
   P/E es contracíclico (se ve barato en el pico de utilidades y caro en el piso — la trampa clásica
   del sector). Usá EV/EBITDA o P/CF promedio del ciclo aplicado al EBITDA/flujo **a precio de mitad de
   ciclo**. Si hubo un cambio real de modelo (ej. las E&P de shale pasaron de "crecer a cualquier
   costo" pre-2020 a "disciplina de capital y retorno de caja" post-2021), podés mostrar las dos
   ventanas, pero justificá con datos (reinversión de flujo en capex antes vs. después) y
   explicalo en Limitaciones.
4. **Consenso Wall Street — 25%** — aclarando el precio de commodity que implícitamente usa.

**Adicionales que se reportan (no entran al blend):**
- **Breakeven**: precio del crudo que cubre capex de mantenimiento + dividendo (y + recompra
  planificada). Es el número que más miran los fondos de ingreso en energía.
- **FCF yield al precio Base y al strip**, y **shareholder yield** (dividendo + recompra ÷ market cap).
- **Precio implícito en la acción** (análogo al DCF inverso de informe-bigtech): ¿qué precio de
  crudo de largo plazo justifica el precio actual de la acción? Traducirlo a un número verificable
  ("el mercado descuenta Brent de $X a largo plazo") es más honesto que "cara/barata".
- **SMOG / PV-10 SEC** como referencia contable: usa precios promedio de 12 meses y costos actuales,
  solo reservas probadas, sin impuestos futuros en PV-10 — no es el fair value, es un piso de
  referencia; no lo promedies.

**Sensibilidad** (reemplaza WACC × terminal): **precio del crudo (5 niveles) × tasa de descuento
(5 niveles)**, recalculada con el modelo real, celda Base = fair value publicado. En gaseras
(EQT, CTRA) usá Henry Hub en vez de crudo; en midstream, WACC × crecimiento terminal como en
informe-bigtech.

**Chequeo de sesgo antes de cerrar la Sección 14:** (1) ¿algún método usa el spot o el TTM de un año
de precio extremo en vez del deck Base? (2) ¿la reversión usa P/E o una ventana que no cubre un
ciclo completo? (3) ¿el Bear asume un precio que la compañía nunca vivió? (4) en E&P, ¿el NAV incluye
inventario no desarrollado sin descuento de riesgo? Si después de esto el fair value sigue lejos del
precio, calculá el precio de crudo implícito — probablemente ESE es el hallazgo.

## Reglas de lectura de métricas

- **Reservas probadas (1P) ≠ recursos**: 1P tiene ~90% de probabilidad de extraerse a precios SEC;
  2P/3P y "recursos" son menos seguros. No mezcles.
- **Reemplazo de reservas** (reservas agregadas ÷ producción del año): >100% sostenido = la compañía
  repone lo que extrae. Separá el reemplazo orgánico del comprado (M&A) y el de revisiones por precio
  (a precio alto las reservas suben "solas").
- **Recycle ratio** (netback por boe ÷ costo F&D por boe): >2x es sano; mide si cada dólar invertido
  en encontrar/desarrollar vuelve multiplicado.
- **Cobertura de distribución en midstream**: flujo distribuible ÷ distribuciones; ~1.5-1.9x es
  cómodo para operadores grandes con tarifa; <1.2x es alerta. Apalancamiento (deuda neta/EBITDA):
  la industria bajó de ~5x hace una década a ~3-4x (promedio ~3.8x a fin de 2025); >5x es zona de
  baja de calificación y posible recorte.
- **EBITDA de un año de precios altos no es "el" EBITDA**: normalizá siempre.
- **Utilidades de refinación con efectos de inventario** (LIFO/FIFO, timing effects) — usá la
  utilidad ajustada que la compañía reporta y explicá el ajuste.

## Cadencia de rollout sugerida

**XOM → CVX → COP → EPD → VIST → YPF** (dos majors comparables, la E&P más grande, el midstream de
referencia, y dos argentinas que la audiencia sigue) → OXY, EOG, SHEL, TTE, KMI, MPC, etc. si se
piden. 2-3 tickers por día.

## Al terminar un ticker

1. `informes/<ticker>.html` (15 secciones), gate de vista previa, deck de precios en portada.
2. Grep de lenguaje relativo a fechas.
3. Picks-list + `informes/manifest.json` (formato de informe-bigtech). Home no se toca.
4. Navegador: gráficos renderizan, ningún `drawHBars` corta labels.
5. Script que recalcule NAV/SOTP, breakeven, múltiplos a mitad de ciclo, grilla crudo × tasa y blend.
   Chequeo de sesgo.

## Fuentes de la investigación que respalda este marco (sep-2026)

- Selborne Research, *NAV vs EV/DACF: When to Use Each for E&P Valuation* (PV-10, 8-12%, deck de
  planificación, rangos de EV/DACF): https://selborneresearch.com/guides/oil-gas/nav-vs-ev-dacf/
- Guías de valuación de E&P (NAV, PV-10, EBITDAX, EV/producción, EV/reservas):
  https://ibinterviewquestions.com/guides/valuation-investment-banking/oil-gas-valuation-reserve-based-nav-pv10-ebitdax
  y https://ibinterviewquestions.com/guides/energy-investment-banking/nav-model-energy-signature-valuation
- CNBC, retorno al accionista de las majors europeas (feb-2026):
  https://www.cnbc.com/2026/02/03/oil-earnings-shell-bp-equinor-totalenergies-dividends-buybacks.html
- Yahoo Finance / 24/7 Wall St., recompras de XOM, breakeven de CVX, precio del Brent 2026:
  https://finance.yahoo.com/news/exxon-vs-chevron-oil-giant-132800148.html y
  https://247wallst.com/investing/2026/09/03/exxon-dividend-scorecard-how-an-oil-major-holds-up-when-crude-falls/
- Cobertura y apalancamiento de midstream: https://www.etftrends.com/energy-infrastructure-content-hub/2025-midstream-mlp-leverage-ratios-signal-flexibility/
  y https://infrastructurecapital.substack.com/p/the-coverage-ratio-number-every-mlp
- EIA Short-Term Energy Outlook (deck de precios): https://www.eia.gov/outlooks/steo/
