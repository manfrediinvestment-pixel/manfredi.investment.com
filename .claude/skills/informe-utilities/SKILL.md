---
name: informe-utilities
description: "Use when writing or updating institutional-grade equity research for utilities / servicios públicos en la sección 'Inversiones' de manfredi.investment.com — eléctricas reguladas (NEE, DUK, SO, D, AEP, XEL, EXC, ETR, EVRG, DTE, PCG, EIX), distribuidoras de gas (ATO, NI), agua (AWK), y generadores no regulados / IPPs (CEG, VST, NRG, TLN) con reglas propias. Reemplaza el DCF de crecimiento de informe-bigtech por el marco que usan los fondos de utilities: base tarifaria (rate base) y su crecimiento, ROE autorizado vs. ROE ganado (regulatory lag), calidad de la jurisdicción regulatoria, calendario de rate cases, métricas de crédito (FFO/deuda) y necesidad de emitir acciones, crecimiento de EPS guiado, dividendo y payout; valuación por P/E relativo al grupo regulado ajustado por crecimiento, SOTP por jurisdicción/segmento, DDM, EV/rate base y P/E relativo al S&P 500. Mismo esqueleto de 15 secciones y mismo gate de vista previa. Trigger on: 'informe de [ticker de utility]', 'análisis de [NEE/DUK/SO/CEG/VST/etc.]', 'tesis de [eléctrica/utility]', 'price target de [utility]', earnings/10-Q/10-K de una utility bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Utilities — Manfredi Investment

Escribís research al nivel de una mesa institucional de utilities. Mismo rigor que `informe-bigtech`,
pero el motor del negocio es regulatorio, no competitivo: una utility regulada **gana un retorno
autorizado sobre el capital que invierte** (la base tarifaria o *rate base*). Entonces el crecimiento
de utilidades ≈ crecimiento de la base tarifaria × el ROE que el regulador le deja ganar, menos la
dilución de las acciones que tenga que emitir para financiar ese capex. Los fondos de utilities
analizan casi exclusivamente esa cadena: **capex → rate base → ROE autorizado/ganado → EPS → dividendo,
financiado sin romper el crédito**.

**Relación con informe-bigtech:** todo lo que no se menciona acá (regla de oro, cero lenguaje
relativo a fechas, disclaimer, precio único en portada, motor Canvas, bug de `drawHBars`, conexión al
sitio, verificación con script) aplica igual. **Relación con informe-bancos:** como en bancos, el
retorno está acotado por un regulador — el ROE autorizado cumple el rol que el CET1/CCAR cumple en un
banco: es una restricción dura, no un dato de contexto.

## Regla de oro (idéntica)

**El modelo dice lo que dice.** El sesgo típico en utilities es aceptar la guía de crecimiento de EPS
de management (5-7%, 6-8%) como si fuera un dato. Es un objetivo que depende de que los reguladores
aprueben rate cases y de que la compañía pueda emitir deuda/acciones a costo razonable — verificá la
cadena, no copies el número.

## Paso 0 — clasificar

| Tipo | Ejemplos | Qué valúan los fondos |
|---|---|---|
| Eléctrica regulada integrada / T&D | DUK, SO, AEP, XEL, ETR, EVRG, DTE, EXC (solo T&D) | Rate base, ROE autorizado, jurisdicción, capex |
| Regulada + renovables contratadas | NEE (FPL + NextEra Energy Resources) | SOTP: utility regulada + desarrollador de renovables |
| Riesgo de incendios / pasivos especiales | PCG, EIX (California), HE | Lo anterior + pasivo contingente y fondos de protección estatales |
| Gas / agua regulados | ATO, NI, AWK | Rate base, reemplazo de ductos, mecanismos de recupero |
| Generadores no regulados (IPPs) | CEG, VST, NRG, TLN | **No** son utilities reguladas: precio de la energía, contratos con data centers, capacidad — se valúan por EV/EBITDA y FCF yield (ver Módulo IPP) |

## Antes de empezar — datos reales

1. **XBRL (SEC EDGAR)** — endpoint de informe-bigtech. Tags útiles: `RegulatedOperatingRevenue`
   (o `RegulatedOperatingRevenueElectric`/`...Gas`), `PublicUtilitiesPropertyPlantAndEquipmentNet`,
   `RegulatoryAssetsNoncurrent` / `RegulatoryLiabilityNoncurrent` (costos diferidos a recuperar vía
   tarifa — un stock creciente de activos regulatorios es caja que todavía no volvió),
   `PaymentsToAcquirePropertyPlantAndEquipment` (capex), `ProceedsFromIssuanceOfCommonStock`
   (emisión de acciones), deuda, `NetCashProvidedByUsedInOperatingActivities`. Muchas utilities son
   holdings con varias subsidiarias que también presentan ante la SEC — usá la holding para el
   informe y las subsidiarias para el detalle por jurisdicción.
2. **Presentación a inversores (la fuente más importante — no viene en XBRL):** plan de capex a 5
   años, **rate base por jurisdicción y su CAGR**, ROE autorizado y equity ratio autorizado por
   jurisdicción, guía de EPS y de crecimiento, necesidad de equity (emisión anual planificada, ATM,
   forwards), métricas de crédito objetivo (FFO/deuda o CFO pre-capital de trabajo/deuda) y
   calificación, crecimiento de demanda (load growth) y contratos de data centers.
3. **Rate cases**: decisiones recientes y casos pendientes por jurisdicción (expedientes de la
   comisión estatal vía WebSearch; prensa especializada citando a RRA/S&P Global). Referencia de
   industria: el **ROE autorizado promedio de eléctricas fue 9.72% (mediana 9.70%) en los 12 meses a
   junio 2025**, con tendencia levemente a la baja desde 2024 — actualizá el dato vigente.
4. **Calidad de la jurisdicción**: ranking de ambiente regulatorio (RRA clasifica los estados en
   Above/Average/Below Average con subniveles 1-3) — citalo si está disponible públicamente; si no,
   usá evidencia (ROE autorizado vs. promedio, lag entre pedido y decisión, mecanismos de recupero
   automático — formula rates, riders, test year futuro).
5. **Precio y peers** — Yahoo. **P/E forward del grupo regulado** (índice de utilities / XLU / peers)
   y del **S&P 500**, y el **Treasury 10Y** a la fecha de corte.

## El entregable: mismas 15 secciones, contenido adaptado

1. Portada — igual (precio único).
2. Resumen Ejecutivo — la tesis responde: ¿a qué ritmo crece la base tarifaria, cuánto de eso llega
   al EPS después de la dilución, y el regulador acompaña?
3. Historia — fusiones, quiebras (PCG), escisiones (EXC/CEG), cambios de modelo.
4. **Jurisdicciones, Segmentos y Rate Base** — tabla por subsidiaria/estado: rate base, % del total,
   ROE autorizado, equity ratio autorizado, próxima rate case, mecanismos (formula rate, riders).
   Mix regulado vs. no regulado. Mix de generación (gas, carbón, nuclear, renovables).
5. Desarrollos Recientes — rate cases decididas, actualización del plan de capex, contratos de
   grandes cargas (data centers — ej. DUK con 7.8 GW de acuerdos firmados; EVRG con rate base CAGR
   ~12% y load growth 7-8% hasta 2030), eventos climáticos.
6. **Estados Financieros** — EPS operativo/ajustado vs. GAAP, **ROE ganado vs. autorizado** por
   jurisdicción (la brecha = regulatory lag: S&P Global documenta que el "underearning spread" se
   amplió en eléctricas y gas), crecimiento de rate base, O&M/cliente, ventas de energía por tipo de
   cliente (residencial/comercial/industrial) normalizadas por clima.
7. **Deuda, Crédito y Financiamiento** — deuda total, deuda de la holding vs. de las subsidiarias
   operativas, **FFO/deuda vs. el umbral de baja de calificación** de cada agencia (típicamente los
   objetivos rondan 14-15%; ej. EVRG 14-15% para 2026-2028), calificación y outlook, **necesidad de
   equity** (emisiones anuales planificadas: ej. EVRG $700-900M/año 2026-2029, DTE $500-600M/año
   2026-2028) y la dilución resultante en EPS.
8. **Flujo de Caja, Capex y Dividendo** — capex vs. OCF (las utilities son estructuralmente FCF
   negativas en etapa de inversión — no es alarma por sí solo, es el modelo; la alarma es si las
   métricas de crédito no aguantan), dividendo, payout (~60-70% típico), crecimiento del dividendo
   vs. crecimiento de EPS.
9. **Comparables** — P/E forward de 3-4 peers de perfil similar (crecimiento de EPS, calidad
   regulatoria, mix), dividend yield, EV/EBITDA; al lado de cada múltiplo, **el CAGR de rate base y
   de EPS guiado** — el mercado paga el premio por crecimiento y por jurisdicción.
10. Gobierno Corporativo — igual, más relación con reguladores y gobiernos estatales.
11. **Registro de Riesgos** — ver lista abajo.
12. **Catalizadores** — decisiones de rate cases, actualizaciones del plan de capex (suelen ser en Q3
    o Q4/EEI Financial Conference en noviembre), contratos de data centers, legislación estatal,
    subastas de capacidad (PJM), eventos climáticos.
13. Modelo Proyectado y Momentum — consenso EPS FY+1/FY+2 vs. guía; crecimiento de largo plazo.
14. **Valuación** — ver metodología abajo.
15. Limitaciones.

## Riesgos específicos del sector (Sección 11)

- **Regulatorio**: rate case adversa, ROE autorizado a la baja, desautorización de costos, cambios
  de comisionados/políticos; regulación por desempeño (al menos 9 estados la persiguen activamente a
  inicios de 2026 según EQ Research).
- **Tasas de interés**: las utilities se comportan como proxy de bonos — un Treasury 10Y más alto
  sube el costo de capital, encarece la deuda y hace menos atractivo el dividendo (cuantificá la
  sensibilidad del EPS a +100pb en la deuda a refinanciar).
- **Financiamiento / dilución**: emisiones de acciones por encima de lo planificado; baja de
  calificación.
- **Asequibilidad**: facturas que suben mucho generan resistencia política a nuevas subas.
- **Clima y pasivos**: incendios (California, oeste), huracanes y tormentas (recupero de costos vía
  titulización), responsabilidad civil.
- **Data centers**: riesgo de que la demanda proyectada no se materialice o que la compañía construya
  para cargas que después no llegan (mitigado si hay contratos con pago mínimo / tarifas de grandes
  cargas).
- **Transición**: cierre de carbón, costo de renovables, nuclear (en IPPs: precio de energía).

## Metodología de valuación

**Costo de equity:** CAPM (beta de utilities ~0.4-0.8 — misma cautela que en consumo masivo: beta
ajustada, piso de Rf + 2.5-3%), y WACC ponderado por la estructura real (las utilities tienen ~50-60%
de deuda). Reportá también el **ROE autorizado promedio vs. tu costo de equity**: si el regulador
autoriza más de lo que el mercado exige, la utility crea valor al invertir (y debería cotizar arriba
de 1x su rate base).

**Pesos del blend** (consenso y reversión siempre entran):

1. **Intrínseco — 15%**, repartido según corresponda:
   - **DDM** con dividendo creciendo al ritmo de EPS guiado *verificado* por 5 años, luego terminal
     2.5-3.5%. Es el método intrínseco natural de una utility pura.
   - **SOTP** cuando hay segmentos distintos (NEE: FPL a múltiplo de utility premium + NEER a
     EV/EBITDA de desarrollador de renovables; utilities multi-estado con jurisdicciones de calidad
     muy distinta: P/E de peers de cada perfil × EPS de cada subsidiaria). Si hay SOTP, reparte el 15%
     (7.5 DDM / 7.5 SOTP), igual que informe-bigtech.
   - **EV/rate base** como chequeo: las reguladas bien manejadas cotizan ~1.2-1.8x rate base; el
     premio sobre 1x refleja ROE autorizado > costo de equity y/o crecimiento. Reportalo, no lo
     promedies.
2. **Comparables — 25%**: P/E forward de peers **ajustado por crecimiento y jurisdicción**: aplicar
   el P/E promedio del grupo sin ajustar castiga a la utility que crece más y premia a la que crece
   menos. Regla: partí del P/E promedio de peers, y si el CAGR de EPS guiado *verificado* del ticker
   difiere del promedio de peers, ajustá con un criterio explícito (ej. la pendiente P/E vs.
   crecimiento de EPS observada en el propio grupo de peers — calculala con los datos, no la
   supongas) y declarala.
3. **Reversión histórica — 35%**: dos lecturas promediadas: (a) P/E forward propio promedio de 5-10
   años en ventana limpia, y (b) **P/E relativo al S&P 500** y **spread de dividend yield vs.
   Treasury 10Y** promedio de 10 años, aplicados a los niveles actuales. Referencia: las eléctricas
   cotizaban ~17.5x forward, apenas por encima de su mediana histórica de 16.8x. Si el perfil de
   crecimiento cambió de escalón de forma real (ej. rate base CAGR que pasó de 5% a 10%+ por data
   centers, con capex aprobado), aplicá la regla de ventana de informe-bancos/informe-bigtech (2-3
   años que ya muestran el nuevo régimen, no un anuncio) y documentalo.
4. **Consenso Wall Street — 25%**.

**Sensibilidad** (reemplaza WACC × terminal): **ROE autorizado (±50pb/±100pb) × crecimiento de rate
base (5 niveles)**, recalculando EPS y fair value con el modelo real; celda Base = fair value
publicado. Tabla aparte: fair value con Treasury 10Y ±100pb.

**Chequeo de sesgo antes de cerrar la Sección 14:** (1) ¿el crecimiento de EPS del Base es la guía de
management sin descontar la dilución de las emisiones planificadas? (2) ¿el ROE proyectado es el
autorizado o el que la compañía realmente gana (menor, por lag)? Usá el ganado. (3) ¿el capex incluye
proyectos de data centers sin contrato firmado? Ponelos en Bull, no en Base.

## Módulo IPP — generadores no regulados (CEG, VST, NRG, TLN)

No hay rate base ni ROE autorizado: venden energía y capacidad a precios de mercado o contratados.
Se analizan como un cíclico con contratos: **EBITDA ajustado y FCF antes de crecimiento**, % de la
generación cubierta con coberturas/contratos para los próximos 2-3 años, **contratos de largo plazo
con hyperscalers** (precio, plazo, contraparte — ej. acuerdos de nucleares con data centers),
precios de capacidad (subastas PJM), curvas forward de energía, y política (créditos fiscales a
nuclear existente). Valuación: DCF 15 / Comparables 25 (EV/EBITDA y FCF yield entre IPPs, nunca contra
reguladas) / Reversión 35 (ventana corta y documentada: el re-rating de 2024-2026 por IA es un cambio
de régimen, pero reciente — explicitá el riesgo) / Consenso 25. Deck de precios de energía con la
misma disciplina que el deck de commodities de `informe-energia` (mitad de ciclo, sourceado, 3
escenarios).

## Cadencia de rollout sugerida

**NEE → DUK → SO → CEG → AEP → VST** (la más grande con SOTP, dos reguladas de referencia del
sudeste, el IPP nuclear de data centers, la mayor en transmisión, y un IPP con gas) → XEL, D, EXC,
ETR, PCG, AWK, etc. si se piden. 2-3 tickers por día.

## Al terminar un ticker

1. `informes/<ticker>.html` (15 secciones), gate de vista previa.
2. Grep de lenguaje relativo a fechas.
3. Picks-list + `informes/manifest.json` (formato de informe-bigtech). Home no se toca.
4. Navegador: gráficos renderizan, ningún `drawHBars` corta labels (nombres de subsidiarias largos).
5. Script que recalcule rate base CAGR, ROE ganado, dilución, DDM/SOTP, grillas y blend. Chequeo de
   sesgo.

## Fuentes de la investigación que respalda este marco (sep-2026)

- Guías de valuación de utilities (P/E 15-20x, EV/rate base 1.2-1.8x, crecimiento = ROE × retención):
  https://ibinterviewquestions.com/guides/energy-investment-banking/utility-valuation-pe-rate-base-dividend-models
  y https://ibinterviewquestions.com/guides/energy-investment-banking/regulated-utilities-rate-base-rate-cases-allowed-roe
- RRA Regulatory Focus, ROE autorizado 9.72% promedio (12m a jun-2025), vía expediente público:
  https://psc.ky.gov/pscecf/2025-00114/kyle.j.smith124.civ%40army.mil/09232025013307/MPG_Copyright_Protected_WP_27.pdf
- S&P Global, *Underearning spread widens for gas, electric utilities in ROE analysis*:
  https://www.spglobal.com/market-intelligence/en/news-insights/research/underearning-spread-widens-for-gas-electric-utilities-in-roe-analysis
- Gabelli, *Utilities – U.S.* (P/E 17.5x vs. mediana 16.8x): https://gabelli.com/research/utilities-u-s-3/
- Evergy Q1/Q2 2026 (rate base CAGR 12%, FFO/deuda 14-15%, emisión de equity):
  https://www.fool.com/earnings/call-transcripts/2026/05/07/evergy-evrg-q1-2026-earnings-transcript/
  y https://finance.biggo.com/news/US_EVRG_2026-08-06
- DTE Energy 8-K (outlook 2026, capex $36.5B, equity $500-600M/año):
  https://www.stocktitan.net/sec-filings/DTB/8-k-dte-energy-co-reports-material-event-630896707c96.html
- Distributed Grid, regulación por desempeño (EQ Research, 9 estados):
  https://distributedgrid.substack.com/p/the-utility-business-model-is-built
- Enerdynamics, cómo fijan los reguladores el ROE:
  https://www.enerdynamics.com/Energy-Currents_Blog/How-Regulators-Determine-a-Utilitys-Return-on-Equity-ROE.aspx
