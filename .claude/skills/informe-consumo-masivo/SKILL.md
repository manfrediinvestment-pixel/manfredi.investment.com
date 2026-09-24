---
name: informe-consumo-masivo
description: "Use when writing or updating institutional-grade equity research for consumer staples / consumo masivo en la sección 'Inversiones' de manfredi.investment.com — alimentos y snacks (MDLZ, GIS, KHC, HSY), bebidas (KO, PEP, KDP, MNST), bebidas alcohólicas (DEO, STZ, BUD), cuidado personal y del hogar (PG, CL, KMB, CLX, EL, KVUE), tabaco (PM, MO, BTI) y retail de consumo masivo (WMT, COST, KR, DG, TGT). Reemplaza el foco 'crecimiento + márgenes de expansión' de informe-bigtech por el marco que usan los fondos para staples: crecimiento orgánico descompuesto en precio/mix vs. volumen, participación de mercado medida (Circana/Nielsen), margen bruto y productividad, reinversión en marca (A&P), conversión de FCF, ROIC, dividendo, y valuación por P/E relativo al S&P 500 + EV/EBITDA + DCF de bajo crecimiento. Mismo esqueleto de 15 secciones, mismo gate de vista previa. Trigger on: 'informe de [ticker de consumo masivo]', 'análisis de [KO/PEP/PG/PM/WMT/COST/etc.]', 'tesis de [empresa de consumo]', 'price target de [staple]', earnings/10-Q/10-K de un staple bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Consumo Masivo (Consumer Staples) — Manfredi Investment

Escribís research de renta variable al nivel de una mesa de research institucional cubriendo
**consumo masivo**. Mismo rigor y honestidad intelectual que `informe-bigtech`, pero la pregunta de
fondo es distinta: en una tech el mercado paga por **cuánto va a crecer**; en un staple paga por
**qué tan predecible y defendible es un crecimiento chico** (2-5% orgánico) y cuánta caja devuelve.
Un staple no se rompe por crecer 3% — se rompe cuando el crecimiento pasa a venir **solo de precio,
con volumen negativo varios trimestres seguidos**, porque eso es la marca perdiendo poder, no la
empresa ganándolo. Todo este marco gira alrededor de detectar eso.

**Relación con informe-bigtech:** para cualquier regla que no se mencione acá (regla de oro de no
forzar el modelo, cero lenguaje relativo a fechas, disclaimer no-negociable, precio único en portada,
motor de gráficos Canvas, bug de `drawHBars`, mecanismo de conexión al sitio, verificación de
cálculos con script), aplica exactamente lo mismo que en `informe-bigtech` — leelo si hace falta. Lo
que sigue son las diferencias.

## Regla de oro (idéntica, repetida porque es la más importante)

**El modelo dice lo que dice.** Nunca ajustés WACC, crecimiento o múltiplos para que el fair value
coincida con el precio de mercado. En staples el riesgo típico no es el DCF muy bajo sino al revés:
como el flujo es estable, es tentador justificar cualquier múltiplo. Si un staple cotiza a 25x con 1%
de volumen, el hallazgo es que el mercado paga calidad pasada — decilo.

## Paso 0 — clasificar la sub-industria (cambia métricas y peers)

| Sub-industria | Ejemplos | Métrica reina | Peers |
|---|---|---|---|
| Alimentos / snacks | MDLZ, GIS, KHC, HSY, K, CPB | Volumen/mix vs. precio; exposición GLP-1 | entre sí |
| Bebidas sin alcohol | KO, PEP, KDP, MNST | Unit case volume; precio/mix; concentrado vs. embotellado | entre sí |
| Bebidas alcohólicas | DEO, STZ, BUD, BF.B | Depletions vs. shipments; premiumización; inventario en distribución | entre sí |
| Cuidado personal / hogar (HPC) | PG, CL, KMB, CLX, CHD, KVUE, EL | Organic sales, participación medida, margen bruto | entre sí |
| Tabaco / nicotina | PM, MO, BTI | Volumen de cigarrillos (cae) vs. precio; % de ingresos smoke-free (IQOS, ZYN, vapor) | entre sí |
| Retail de consumo masivo | WMT, COST, KR, DG, DLTR, TGT, BJ | Ventas comparables (tráfico vs. ticket), membresías, margen bruto, rotación de inventario | entre sí, NO contra marcas |

**Retail no es una marca:** WMT/COST/KR se analizan con ventas comparables (comp sales ex-combustible,
separando tráfico de ticket promedio), crecimiento de e-commerce, margen bruto y SG&A como % de
ventas, rotación de inventario, ROIC, y en COST/BJ/Sam's además **ingresos por membresía y tasa de
renovación** (el grueso de la utilidad operativa de COST viene de las cuotas). Cuando el ticker sea
retail, la Sección 6 usa esas métricas en vez de precio/mix de marca, y los peers son otros
minoristas, nunca PG/KO.

## Antes de empezar — reunir datos reales

1. **Fundamentals (SEC EDGAR XBRL)** — mismo endpoint y `User-Agent` que informe-bigtech. Últimos 8
   trimestres standalone (restar YTD en 10-Q):
   - `RevenueFromContractWithCustomerExcludingAssessedTax` (o `Revenues`). En tabaco y alcohol
     verificá si el filer reporta ingresos **netos o brutos de impuestos especiales (excise)** — PM
     reporta ambos; usá siempre neto de excise para márgenes y comparaciones.
   - `CostOfGoodsAndServicesSold` / `CostOfRevenue` → margen bruto. `SellingGeneralAndAdministrativeExpense`.
   - `AdvertisingExpense` (suele venir solo anual en el 10-K) — es la base del ratio A&P/ventas.
   - `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment` → FCF.
   - `PaymentsOfDividendsCommonStock` (o `PaymentsOfDividends`), `PaymentsForRepurchaseOfCommonStock`.
   - Balance: `Goodwill`, `IndefiniteLivedIntangibleAssetsExcludingGoodwill` (marcas — las
     desvalorizaciones de marcas son la partida no recurrente típica del sector, ej. KHC),
     `InventoryNet`, `AccountsReceivableNetCurrent`, `AccountsPayableCurrent` (el ciclo de caja y el
     uso de factoring/supply-chain finance importan para leer bien el FCF), deuda y caja.

2. **Crecimiento orgánico y su descomposición — NO viene en XBRL.** Sale del comunicado de resultados
   (tabla de reconciliación non-GAAP): **ventas netas reportadas = orgánico + FX + M&A/desinversiones**,
   y **orgánico = volumen (o volumen/mix) + precio (o precio/mix)**. Traé los últimos 8 trimestres de
   esa descomposición — es el gráfico más importante del informe. Cada compañía define el split
   distinto (PG: volumen, precio, mix; KO: unit case volume, precio/mix, concentrate sales; PEP:
   efecto volumen orgánico + precio efectivo): citá la definición de la propia compañía.

3. **Participación de mercado medida** — datos de scanner Circana (ex-IRI/NPD) o NielsenIQ que la
   compañía cita en la earnings call o que publican medios/brokers vía WebSearch ("takeaway",
   "measured channels", "share gains/losses"). Si no hay un dato de share concreto y citado, decí
   explícitamente que no está disponible — nunca lo inventes.

4. **Guía de management** — orgánico del año, EPS ajustado, inflación de insumos esperada, ahorro de
   productividad, y cobertura de commodities (hedges: a cuántos meses tienen fijado el costo).

5. **Precio y peers** — mismos endpoints de Yahoo que informe-bigtech. También el **P/E forward del
   S&P 500** (y del sector, XLP) vigente a la fecha de corte, necesario para el P/E relativo.

## El entregable: mismas 15 secciones, contenido adaptado

`informes/<ticker>.html`, mismo CSS/motor de gráficos/gate que informe-bigtech (plantilla
`informes/aapl.html`), con logo en portada. Secciones marcadas con cambios:

1. Portada — igual (precio único, verdict-bar, disclaimer, logo).
2. Resumen Ejecutivo — igual, pero la primera frase de la tesis responde: ¿el crecimiento orgánico
   viene de volumen o solo de precio, y es sostenible?
3. Historia y Evolución — incluir la cartera de marcas y las grandes compras/escisiones (spin-offs
   como KVUE de JNJ, Kraft Heinz/Mondelez, etc.).
4. **Modelo de Negocio, Marcas y Geografía** — segmentos reales de la compañía, marcas que superan
   ~$1B de ventas, % de ventas por región (desarrollados vs. emergentes — en emergentes el precio
   compensa FX y el crecimiento es mayor pero más volátil), canales (supermercado, club, discount,
   e-commerce, away-from-home) y concentración de clientes (ej. % de ventas a Walmart, que figura en
   el 10-K). Explicitar el modelo cuando aplique: concentrado/franquicia (KO) vs. integrado con
   embotellado y distribución directa (PEP).
5. Desarrollos Recientes y Perspectiva — anclado en la última earnings call: guía de orgánico, precio
   vs. volumen esperado, costo de insumos, reinversión.
6. **Estados Financieros** (2 trimestres + TTM) — reemplaza el foco en crecimiento por:
   **descomposición del orgánico** (volumen vs. precio/mix, 8 trimestres, gráfico de barras
   apiladas), **margen bruto** (y sus drivers: inflación de insumos, productividad, precio),
   **A&P / ventas** (reinversión en marca — un margen operativo que sube porque cortaron publicidad
   es de baja calidad), margen operativo ajustado, EPS ajustado vs. GAAP (explicitar qué excluye:
   reestructuraciones, desvalorización de marcas, mark-to-market de coberturas), impacto FX.
7. **Deuda y Balance** — deuda neta/EBITDA (el rango típico de un staple grado de inversión es
   ~2-3x; por arriba, preguntá si es por una compra reciente y cuál es el plan de desapalancamiento),
   calificación crediticia, vencimientos, intangibles/goodwill como % de activos y riesgo de
   desvalorización, ciclo de conversión de caja.
8. **Flujo de Caja, Dividendo y Capital Allocation** — **conversión de FCF** (FCF / utilidad neta
   ajustada; la vara del sector es ~90-100% — por debajo sostenidamente, averiguá por qué), capex/
   ventas, payout de dividendo sobre EPS y sobre FCF, **racha de aumentos de dividendo** (Dividend
   King/Aristocrat es un dato que los fondos de ingreso miran), recompras, M&A de portafolio
   (compras de marcas en crecimiento, desinversión de marcas lentas).
9. **Comparables** — P/E forward, EV/EBITDA forward, FCF yield y dividend yield de 3-4 peers de la
   misma sub-industria, **con el orgánico y el volumen de cada uno al lado del múltiplo** (el
   mercado paga más por volumen positivo, no por precio).
10. Gobierno Corporativo — igual; en staples revisá también activismo (Trian, Elliott, Starboard
    tienen historia en el sector: PG, PEP, KHC) y si el directorio empuja escisiones.
11. **Registro de Riesgos** — específicos del sector (ver lista abajo).
12. **Catalizadores** — lanzamientos/innovación, aumentos de precio anunciados, cambios en la cartera
    (spin-off, venta de marcas), guía anual (la mayoría la da en el reporte de Q4), CAGNY (conferencia
    anual de consumo en febrero donde las compañías actualizan algoritmos de largo plazo), resultados
    de un peer relevante.
13. Modelo Proyectado y Momentum de Estimados — consenso real de ventas, **orgánico** y EPS FY+1/FY+2.
14. **Valuación** — ver metodología abajo.
15. Limitaciones del Modelo.

## Riesgos específicos del sector (Sección 11 — citá datos, no genéricos)

- **Volumen negativo sostenido / elasticidad**: el riesgo #1 después de la ola de precios de
  2021-2023 — si el volumen lleva ≥3-4 trimestres negativo, el precio ya no está "sumando", está
  sacando consumidores.
- **Marcas propias (private label)** y consumidor que baja de categoría (trade-down), sobre todo en
  bajos ingresos (dato típico: participación de marca propia según Circana/PLMA).
- **Poder del retailer**: concentración de clientes (WMT/COST/Amazon) y pelea por espacio en góndola
  y promociones.
- **GLP-1 (Ozempic/Wegovy/Zepbound y orales)**: Morgan Stanley estima caída de ~3% en consumo de
  gaseosas, panificados y snacks salados hacia 2035 y 24 millones de usuarios en EE.UU.; hogares con
  un usuario gastan ~11% menos en snacks salados. Impacta más a snacks/golosinas/gaseosas/alcohol que
  a productos de despensa y cuidado del hogar — cuantificá el % de ventas de la compañía en las
  categorías más expuestas.
- **Costo de insumos** (commodities agrícolas, cacao, café, envases, flete) y el desfase de coberturas
  (la inflación de insumos llega al margen con 6-12 meses de retraso según el hedge).
- **FX y emergentes** (ingresos en monedas débiles, hiperinflación — Argentina, Turquía, Nigeria —
  que infla el "precio" orgánico sin ser poder de marca real: si el orgánico de una región es de dos
  dígitos por hiperinflación, decilo y separalo).
- **Aranceles** sobre insumos o productos importados.
- **Regulación**: impuestos a bebidas azucaradas, etiquetado frontal, regulación de nicotina/vapeo
  (FDA), restricciones a ingredientes (colorantes, etc.).
- **Desvalorización de marcas** (goodwill/intangibles) si la marca pierde relevancia.

## Metodología de valuación

**WACC:** CAPM normal (Rf ≈ Treasury 10Y + beta × ERP ~5%) + costo de deuda después de impuestos,
ponderado por estructura real. **Cuidado con la beta:** los staples tienen betas bajas (~0.4-0.7);
usá una beta ajustada (Blume: 0.67 × beta cruda + 0.33) o la mediana de peers, y nunca un costo de
equity por debajo de ~Rf + 2.5% — una beta cruda de 0.3 da un costo de capital irrealmente bajo y
un DCF inflado. Documentá la beta usada y de dónde sale.

Blend final ponderado (mismos pesos y misma lógica que informe-bigtech; consenso y reversión
**siempre** entran):

1. **DCF (3 escenarios) — 15%.** Horizonte 5 años. Crecimiento de ventas anclado en el orgánico real
   de los últimos 4-8 trimestres **separando precio de volumen**: el caso Base no puede asumir que el
   precio sigue creciendo al ritmo de 2022-2023 si la inflación de insumos ya bajó y el volumen es
   negativo — proyectá precio ~ inflación de largo plazo (2-3%) + volumen según la tendencia real.
   Margen de OCF anclado en el OCF real (regla de informe-bigtech). Terminal growth 2-3% (un staple
   maduro rara vez justifica 4%; si usás más de 3%, justificalo con exposición a emergentes).
   Reportá % del EV desde terminal (en staples suele ser 70-80%, decilo).
2. **Comparables — 25%.** P/E forward (el múltiplo principal que usa el sector) y EV/EBITDA forward de
   3-4 peers de la **misma sub-industria**, promedio de ambos resultados. **Ajuste por calidad del
   crecimiento:** si el ticker tiene volumen claramente mejor/peor que los peers, podés aplicar
   premio/descuento, pero explícito y cuantificado (ej. "+1x por 2 puntos más de volumen orgánico"),
   nunca de ojo.
3. **Reversión histórica — 35%.** Dos lecturas, promediadas:
   - P/E forward propio: promedio de 5-10 años limpio (excluir años con desvalorizaciones grandes de
     marcas o cargos puntuales, regla de "ventana limpia" de informe-bigtech).
   - **P/E relativo al S&P 500** (P/E forward del ticker ÷ P/E forward del S&P): es cómo los fondos
     miran staples, porque el múltiplo absoluto del sector sube y baja con las tasas y con el
     mercado. El sector históricamente cotizó con premio al índice (~15% según Guinness; 22x+ en
     2021-2022, ~18x en 2024), y en 2024-2026 con descuento, porque el S&P se re-rateó por las mega
     tech. Calculá el relativo promedio del propio ticker en 10 años y aplicalo al P/E actual del
     S&P × EPS forward. **Si el P/E relativo actual está en mínimos de 10 años, no concluyas
     "barato" sin más**: explicá si es porque el S&P está caro (efecto denominador) o porque el
     volumen del ticker empeoró de verdad.
4. **Consenso Wall Street — 25%.**

Adicionales (se reportan, no entran al blend salvo que se indique):
- **FCF yield y dividend yield vs. Treasury 10Y** — el spread dice cuánto paga el mercado por el
  carácter "bono con crecimiento" del staple. Reportalo como contexto en la Sección 14.
- **DDM** — solo como chequeo cruzado en tabaco (MO/PM/BTI), donde el dividendo es el grueso del
  retorno; si se incluye en el blend, reparte el 15% del DCF (7.5% / 7.5%), igual que el SOTP en
  informe-bigtech.
- **SOTP** cuando haya segmentos de perfil muy distinto (ej. PEP bebidas vs. Frito-Lay; PM
  cigarrillos vs. smoke-free; BUD por región) — mismo tratamiento que informe-bigtech (reparte el
  15% del DCF).

**Grilla de sensibilidad**: WACC × crecimiento terminal (5×5) recalculada con la fórmula, celda Base
= fair value publicado. **Sensibilidad extra obligatoria**: fair value del DCF con volumen orgánico
−2 / 0 / +2 puntos anual respecto del Base (tabla 1×3) — muestra cuánto del valor depende del
volumen, la variable que el mercado más castiga.

**Football field**: igual que informe-bigtech.

**Chequeo de sesgo antes de cerrar la Sección 14:** si el DCF Base queda a más de ~30-40% del precio
(en staples la dispersión esperable es menor que en tech), revisá: (1) beta/costo de equity
irrealmente bajo o alto, (2) margen de OCF año 1 vs. real, (3) si proyectaste precio de la era
inflacionaria o volumen de un trimestre atípico (ej. compras anticipadas antes de un aumento).

## Reglas de lectura de métricas

- **Orgánico ≠ ventas reportadas**: siempre separá FX y M&A. Una compañía puede reportar ventas −2%
  con orgánico +4% (FX fuerte en contra) o al revés.
- **Precio vs. volumen**: el mismo +4% orgánico vale muy distinto si es +4 precio / 0 volumen que
  +1 precio / +3 volumen. Graficalo siempre separado, nunca solo el total.
- **Hiperinflación contamina el precio**: excluí o marcá las regiones hiperinflacionarias (algunas
  compañías ya reportan "orgánico ex-Argentina").
- **Shipments vs. consumo (takeaway/depletions)**: si la compañía vende más de lo que el consumidor
  compra, está llenando inventario de retailers/distribuidores y se revierte en los trimestres
  siguientes. En alcohol mirá depletions; en el resto, takeaway medido vs. ventas reportadas.
- **Margen operativo que sube con A&P que baja** es de baja calidad — reportalo.
- **EPS ajustado**: listá qué excluye. Si la compañía tiene "cargos de reestructuración" todos los
  años, no son no-recurrentes; mencionalo.

## Cadencia de rollout sugerida

Empezar por los más seguidos y con más dato público: **KO → PEP → PG → WMT → COST → PM** (cubren
bebidas, HPC, retail y tabaco — los cuatro modelos de esta skill) → MO, MDLZ, CL, KMB, MNST, DEO,
KR, etc. si se piden. Mismo ritmo: 2-3 tickers por día.

## Al terminar un ticker

1. `informes/<ticker>.html` completo (15 secciones), con `<script src="_preview-gate.js" defer></script>`.
2. Grep de lenguaje relativo a fechas (regla de informe-bigtech).
3. Card en el picks-list de `#inversiones` + entrada al principio de `informes/manifest.json`
   (mismo formato que informe-bigtech). La lista fija de la home no se toca.
4. Navegador: gráficos Canvas renderizan, ningún `drawHBars` corta labels (nombres de marcas y
   regiones suelen ser largos).
5. Recalculá con script cada número derivado (descomposición del orgánico, conversión de FCF,
   P/E relativo, blend) y corré el chequeo de sesgo.

## Fuentes de la investigación que respalda este marco (sep-2026)

- Guinness Global Investors, *Consumer Staples: Sector & Stocks* (drivers precio/volumen/mix, margen
  bruto, premio histórico de P/E): https://www.guinnessgi.com/insights/consumer-staples-sector-stocks
- Morgan Stanley IM, *GLP-1 Medications and Shifting Consumer Behavior*:
  https://www.morganstanley.com/im/en-us/individual-investor/insights/articles/medications-and-shifting-consumer-behavior.html
- Morgan Stanley Research, *Consumer Staples*: https://www.morganstanley.com/im/publication/insights/investment-insights/ii_consumerstaples_us.pdf
- Circana (datos de scanner / participación medida): https://www.circana.com/solution-areas/market
- Investing.com Academy, *How to Evaluate Consumer Staples Stocks*:
  https://www.investing.com/academy/analysis/how-to-evaluate-consumer-staples-stocks/
