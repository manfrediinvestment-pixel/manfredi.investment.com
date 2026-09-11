---
name: informe-bancos
description: "Use when writing or updating institutional-grade equity research for banks / financieras en la sección 'Inversiones' de manfredi.investment.com — money-center/GSIB (JPM, BAC, WFC, C, GS, MS), bancos regionales, y en general cualquier emisor donde el balance (depósitos + préstamos) ES el negocio, no apalancamiento externo a valuar. Reemplaza DCF-FCF-to-firm y comparables EV/EBITDA de informe-bigtech por Dividend Discount Model, Residual Income Model, P/TBV justificado por ROTCE, comparables P/E-P/TBV y capital regulatorio (CET1/CCAR). Cada ticker ships as a standalone HTML report en `informes/<ticker>.html`, mismo esqueleto de 14-15 secciones y mismo gate de vista previa que informe-bigtech, pero con el contenido de las secciones 4, 6, 7, 8, 11, 12 y 14 adaptado al sector. Trigger on: 'informe de [ticker bancario]', 'análisis de [banco]', 'tesis de inversión de [JPM/BAC/WFC/C/GS/MS/etc.]', 'price target de [banco]', earnings/10-Q/10-K de un banco bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Bancos y Financieras — Manfredi Investment

Escribís research de renta variable al nivel de una mesa de research institucional de un banco de
inversión (Morgan Stanley, JP Morgan, BofA) cubriendo **otros bancos**. Mismo rigor y honestidad
intelectual que `informe-bigtech`, pero el marco de análisis es distinto porque el objeto valuado es
distinto: en una tech, la deuda es apalancamiento externo sobre un negocio operativo separable; en un
banco, **los depósitos y la deuda son la materia prima del negocio** — no hay flujo de caja libre "a
la firma" que tenga sentido separar de cómo se financia. Por eso ningún research shop serio usa
DCF-FCF ni EV/EBITDA para bancos, y este documento no es informe-bigtech "con ajustes menores": es un
marco distinto que comparte el mismo esqueleto de 15 secciones, el mismo motor de gráficos y el mismo
gate de vista previa.

**Relación con informe-bigtech:** para cualquier regla que no se mencione acá explícitamente (regla
de oro de no forzar el modelo, cero lenguaje relativo a fechas, disclaimer no-negociable, motor de
gráficos Canvas, mecanismo de conexión al sitio, bug de `drawHBars`), aplica exactamente lo mismo que
en `informe-bigtech` — no lo repito completo acá, léelo si hace falta. Lo que sigue son las
diferencias.

## Regla de oro (idéntica a informe-bigtech, repetida porque es la más importante)

**El modelo dice lo que dice.** Nunca ajustés los supuestos de un DDM/Residual Income para que el
precio objetivo coincida con el precio de mercado. Si el modelo da un fair value muy por debajo (o
por arriba) del precio con supuestos razonables, ESO es el hallazgo.

## Antes de empezar — reunir datos reales (distinto de informe-bigtech)

Los tags XBRL genéricos de informe-bigtech (`Revenues`, `OperatingIncomeLoss`, `GrossProfit`) no
existen o no significan lo mismo en un banco. Para cada ticker nuevo:

1. **Fundamentals bancarios (SEC EDGAR XBRL)** —
   `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` (mismo header `User-Agent` que
   informe-bigtech). Tags específicos de banco, últimos 8 trimestres, standalone (mismo cuidado con
   YTD acumulado en 10-Q que en informe-bigtech):
   - `InterestAndDividendIncomeOperating` (ingreso bruto por intereses) y `InterestExpense` →
     `InterestIncomeExpenseNet` (NII, ingreso neto de intereses) — si el filer no reporta el neto
     directo, restalo a mano.
   - `NoninterestIncome` (fees, trading, banca de inversión, servicing) y `NoninterestExpense`
     (compensación, ocupación, tecnología, litigios).
   - `ProvisionForLoanLeaseAndOtherLosses` (o `ProvisionForLoanLossesExpensed` en filers más viejos) —
     es P&L, forward-looking (CECL). Distinto de net charge-offs (ver regla abajo).
   - Balance: `LoansAndLeasesReceivableNetReportedAmount` (o el tag específico del filer para
     préstamos netos), `Deposits`, `AllowanceForLoanAndLeaseLosses` (o `FinancingReceivableAllowanceForCreditLosses`).
   - `EarningsPerShareDiluted`, `EntityCommonStockSharesOutstanding` (namespace `dei`) — igual que
     informe-bigtech.
   - `StockholdersEquity` y, si está tagueado, `Goodwill` + `FiniteLivedIntangibleAssetsNet` — hacen
     falta para TBV (book value − goodwill − intangibles).

2. **Capital regulatorio y resultado de stress test — NO viene limpio en XBRL.** Sacar del comunicado
   de resultados / earnings presentation (la tabla de "Capital Ratios", casi siempre las últimas
   páginas del deck de la earnings call, vía WebSearch) o del texto del 10-Q/10-K:
   - **CET1 ratio** (standardized approach, o advanced si el banco lo divulga por separado),
     **Tier 1 capital ratio**, **RWA** (risk-weighted assets), **GSIB surcharge** (solo aplica a los
     ~8 bancos G-SIB de EE.UU.: JPM, BAC, C, WFC, GS, MS, BNY, State Street).
   - **Resultado del último CCAR/DFAST** (junio de cada año, Fed) — el **Stress Capital Buffer (SCB)**
     resultante determina el mínimo de CET1 requerido y, por lo tanto, cuánto puede devolver en
     dividendo/buyback. Buscalo en el comunicado del banco tras la publicación de resultados del Fed,
     no lo inventes ni lo asumas constante de un año a otro.
   - Sensibilidad de NII a movimientos de tasas (management suele divulgar un escenario de ±100bps en
     el 10-K, sección de riesgo de mercado/ALM) y el **deposit beta** reciente (cuánto de un cambio en
     la tasa de referencia se traslada al costo de los depósitos) — sacalo de la earnings call o la
     presentación, citando la fuente.

3. **Precio y peers** — mismos endpoints de Yahoo Finance que informe-bigtech. Peer set separado por
   perfil (ver "Regla de comparables" abajo): money-center/GSIB entre sí, regionales entre sí, y para
   bancos con mezcla fee-heavy (MS, y en menor medida JPM/BAC vía sus brazos de wealth/asset
   management) agregar también gestores de activos/brokers puros como referencia cruzada.

4. Anotá la fecha/quarter de la última publicación de resultados y del último CCAR usado — todo
   informe debe indicar su fecha de corte de datos regulatorios además de la de resultados.

## El entregable: mismo formato HTML, mismas 15 secciones, contenido adaptado

Igual que informe-bigtech: `informes/<ticker>.html`, mismo CSS/motor de gráficos/gate de vista previa
(`<script src="_preview-gate.js" defer></script>` antes de `</body>`, misma excepción de "una muestra
completa gratis" si en algún momento se decide para un ticker bancario). Usar como plantilla de
estructura HTML/CSS `informes/aapl.html`, pero el contenido de las secciones marcadas abajo es
distinto:

1. Portada — Fair Value blend vs. precio de mercado, verdict-bar, disclaimer. Igual que
   informe-bigtech.
2. Resumen Ejecutivo — igual.
3. Historia y Evolución — igual.
4. **Modelo de Negocio y Segmentos** — la segmentación real del banco universal, no segmentos de
   producto: JPM = Consumer & Community Banking / Commercial & Investment Bank / Asset & Wealth
   Management; BAC = Consumer Banking / GWIM (Global Wealth & Investment Management) / Global Banking
   / Global Markets; WFC/C tienen su propia estructura análoga. Explicitar si el ticker es
   **money-center/GSIB** (balance grande, mesa de trading, negocio internacional) o **banco
   regional** (sin mesa de trading, geografía concentrada, funding más dependiente de depósitos
   locales) — esta distinción cambia el peer set de la Sección 9 y los riesgos de la Sección 11.
5. Desarrollos Recientes y Perspectiva — igual, pero anclado en la última earnings call (guía de NII,
   guía de gastos, comentario de calidad de crédito).
6. **Estados Financieros** (últimos 2 trimestres + TTM) — reemplaza revenue/gross margin/operating
   margin por: **NII**, **NIM** (NII / activos que generan interés promedio), **eficiencia ratio**
   (gastos no financieros / ingresos totales — ojo, más BAJO es mejor, al revés que un margen),
   mix de ingreso por intereses vs. no financiero (fees + trading + banca de inversión), y
   **ROA, ROE y ROTCE los tres juntos** (ver regla de ROE-vs-ROTCE abajo).
7. **Balance, Calidad de Activos y Capital Regulatorio** (reemplaza "Deuda y Balance"): composición y
   costo de depósitos (core/transaccionales vs. time deposits, deposit beta reciente), mix y
   concentración de la cartera de préstamos (por tipo: comercial, hipotecario, consumo/tarjetas, y por
   geografía si es relevante), calidad de activos (NPL ratio, tasa de net charge-offs, cobertura
   ACL/NPL — ver regla provisión-vs-NCO abajo), y capital regulatorio (CET1, Tier 1, RWA, GSIB
   surcharge, SCB del último CCAR y el colchón real sobre el mínimo requerido).
8. **Retorno de Capital** (reemplaza "Flujo de Caja y Capital Allocation"): payout ratio histórico
   (dividendo + buyback / utilidad neta), y explicitar que la capacidad de buyback está limitada por
   el resultado del stress test, no por caja disponible — un banco con CET1 apretado contra su SCB no
   puede sostener el mismo payout aunque genere la utilidad.
9. **Comparables de Industria** — P/E forward y **P/TBV** de 3-4 peers reales del mismo perfil
   (money-center vs. money-center, regional vs. regional), nunca EV/EBITDA (ver regla abajo).
10. Gobierno Corporativo y Estructura Accionaria — igual que informe-bigtech (ownership, directorio,
    comp del CEO vía DEF 14A), más el resultado del último CCAR como parte de la relación regulatoria
    con la Fed.
11. **Registro de Riesgos** — específicos del sector: Basel III Endgame (suba de requerimiento de
    capital pendiente de reglamentación), resultado/tendencia de CCAR, riesgo de tasa (sensibilidad de
    NII a un escenario de ±100bps guiado por management), riesgo de crédito cíclico (build/release de
    reserva CECL), riesgo de liquidez/corrida de depósitos (post-SVB marzo 2023, relevante sobre todo
    en regionales), litigios y multas regulatorias.
12. **Catalizadores** — resultado de CCAR (junio), anuncio de dividendo/buyback post-stress-test, forma
    de la curva de tasas (steepening/flattening y su efecto en NIM), guía de NII de management,
    M&A sectorial.
13. Modelo Financiero Proyectado y Momentum de Estimados — consenso Street real de EPS y NII (no solo
    EPS) vía WebSearch, mismo tratamiento que informe-bigtech.
14. **Valuación: Métodos y Fair Value** — ver metodología completa abajo (reemplaza DCF+comps).
15. Limitaciones del Modelo.

## Metodología de valuación (el corazón de la diferencia con informe-bigtech)

**No hay WACC.** Solo **costo de equity** (CAPM: Rf ≈ yield del Treasury 10Y vigente + beta × ERP
~5%) — la deuda/depósitos es insumo operativo, no se pondera como fuente de financiamiento externa.

Blend final = promedio de estos métodos (misma regla que informe-bigtech de que reversión y consenso
**siempre** entran, nunca se dejan afuera ad hoc):

1. **Dividend Discount Model (DDM)** — horizonte explícito de 5 años, 3 escenarios (bear/base/bull),
   payout ratio evolucionando de forma creíble (no constante si el banco viene de reconstruir capital
   post-stress-test), terminal growth 2.5%-4% (misma cota que informe-bigtech). Reportá también el
   valor esperado ponderado por probabilidad, igual que el DCF de informe-bigtech.

2. **Residual Income Model / Excess Return Model** — el método que Wall Street de hecho prefiere para
   bancos, porque ancla la mayor parte del valor en un número real del balance (book value) en vez de
   uno proyectado: `Fair Value = BV₀ + Σ PV[(ROE_t − Costo de Equity) × BV_{t-1}]` + valor terminal del
   excess return. **Regla de anclaje (equivalente a la regla de margen de OCF de informe-bigtech):**
   el ROE proyectado año 1 tiene que anclarse en el ROTCE real de los últimos 4-8 trimestres,
   ajustado explícitamente por el escenario de tasas y de ciclo de crédito del caso — nunca un ROE
   "de tabla" copiado de un peer o de memoria.

3. **P/TBV justificado por ROTCE** — el ancla central de la industria para bancos:
   `P/TBV justificado = (ROTCE − g) / (Costo de Equity − g)`, donde `g` ≈ ROTCE × (1 − payout ratio).
   Aplicalo al TBV per share actual y compará el resultado contra el P/TBV real de mercado —
   cuantificar la brecha (¿el mercado paga de más o de menos por el ROTCE que el banco efectivamente
   genera?) es más útil que aceptar o rechazar el múltiplo de mercado sin más.

4. **Comparables** — P/E forward y P/TBV de 3-4 peers reales, **nunca EV/EBITDA** (un banco no tiene
   "enterprise value" en el sentido convencional: la deuda/depósitos no es algo que se sume para
   llegar del equity al valor de la firma, es el negocio). Peer set separado por perfil: money-center
   contra money-center, regional contra regional. **Excepción MS/GS:** cuando el ticker bajo
   cobertura tenga una mezcla de ingresos mayoritariamente fee-based/trading (wealth management,
   banca de inversión, mercados) en vez de spread bancario puro, agregá como referencia cruzada
   comparables de gestión de activos/brokers (ej. SCHW) — forzarlo solo contra bancos comerciales
   puros subestima la parte del negocio que no depende del spread de tasas.

5. **Reversión histórica** — sobre P/TBV o P/E propio (no EV/EBITDA), misma regla de "ventana limpia"
   que informe-bigtech para descontaminar trimestres con distorsión — en bancos, los eventos de
   contaminación típicos son el day-1 CECL (adopción 2020), builds/releases grandes y puntuales de
   reserva (COVID 2020, crisis de bancos regionales de marzo 2023), o cargos de litigio/regulatorios
   puntuales.

6. **Consenso Wall Street** — igual que informe-bigtech, siempre entra al blend.

**Grilla de sensibilidad** (reemplaza la de WACC×crecimiento terminal): Costo de Equity × crecimiento
terminal (5×5), recalculando el DDM/RIM real para cada combinación, calibrada para que la celda del
caso Base reproduzca el fair value ya publicado — misma exigencia que informe-bigtech.

**Football field**: mismo formato que informe-bigtech (rango bajo/alto por método + líneas de
referencia de precio de mercado y fair value propio).

**Chequeo de sesgo obligatorio antes de dar la Sección 14 por terminada** (equivalente a la regla de
informe-bigtech): si el Bear del DDM/RIM da un fair value de $0 o negativo, o el Base queda a más de
~60-70% del precio de mercado, revisá en este orden: (1) el ROE/ROTCE proyectado año 1 vs. el real
reciente, (2) el supuesto de provisión vs. la tendencia real de net charge-offs y la guía de reserva
de management, (3) el payout ratio proyectado vs. lo que el resultado real del último CCAR permite —
un payout que el banco no tendría autorización regulatoria para sostener es un supuesto sin anclaje,
no un escenario legítimamente pesimista.

## Reglas de lectura de métricas (para no confundir conceptos que se parecen pero no son lo mismo)

- **ROE vs. ROTCE — reportar siempre los dos, nunca solo ROE:** las fusiones bancarias generan mucho
  goodwill/intangibles, que infla el equity contable y deprime el ROE sin reflejar peor rentabilidad
  real del capital que el negocio efectivamente necesita. ROTCE (utilidad / equity tangible, sin
  goodwill ni intangibles) es la métrica que de hecho usa la industria para comparar bancos entre sí
  y para el múltiplo justificado de P/TBV — si hay una brecha grande entre ROE y ROTCE, explicitala en
  el texto, no la dejes solo en la tabla.

- **Provisión vs. net charge-off — no son lo mismo:** la provisión (P&L, CECL) es forward-looking —
  el banco reservando contra pérdidas que espera, no que ya ocurrieron. El net charge-off es la
  pérdida ya realizada y castigada contra la reserva. Un aumento de provisión con NCO estable es un
  banco **construyendo colchón por precaución**, no necesariamente un banco cuyo libro se está
  deteriorando ya — y viceversa, una reserva liberándose (provisión negativa) con NCO estable es
  releasing de exceso de cautela pasada, no necesariamente mejora del negocio. Distinguilo
  explícitamente en la Sección 7, nunca lo trates como sinónimos.

- **Eficiencia ratio — más bajo es mejor:** al revés que un margen operativo. Un banco con eficiencia
  ratio de 52% gasta 52 centavos por cada dólar de ingreso en operar — eso es *bueno* comparado con un
  regional con 65%+. No lo escribas ni lo grafiques como si "más alto = mejor negocio".

- **Capital regulatorio como restricción dura, no como dato de contexto:** el CET1 ratio vigente vs.
  el mínimo requerido (regulatorio base + buffers + GSIB surcharge + SCB) determina cuánto colchón real
  tiene el banco para seguir devolviendo capital — tratalo en el DDM/Retorno de Capital con el mismo
  peso que informe-bigtech le da al capex guiado por management: un caso Bull que asume un payout que
  excede la capacidad regulatoria real no es agresivo, es un supuesto sin anclaje.

## Regla de asignación de la postura, disclaimer, motor de gráficos, mecanismo de conexión al sitio

Idéntico a informe-bigtech — no lo repito acá. Misma regla de no dar rangos en portada (salvo que en
el futuro aparezca un caso análogo a la "apuesta de plataforma" de TSLA, poco probable en bancos
maduros), mismo disclaimer no-negociable, mismos `drawVBars`/`drawHBars`/`drawLines`/`drawRangeBars`,
mismo proceso de picks-list + `informes/manifest.json`, misma lista fija de 7 informes en la home (no
se toca).

## Cadencia de rollout sugerida

Empezar por los money-center/GSIB, que son los más seguidos y los que tienen más dato público
limpio: **JPM → BAC → WFC → C** (los cuatro bancos comerciales más grandes de EE.UU., comparables
directos entre sí) → **GS → MS** (más fee/trading-heavy, aplicá la excepción de peer set de
comparables de arriba) → de ahí en más, bancos regionales (ej. USB, PNC, TFC) si se pide
explícitamente. Mismo ritmo que informe-bigtech: 2-3 tickers por día, no todos de una.

## Al terminar un ticker

1. Generá `informes/<ticker>.html` completo (15 secciones) siguiendo la estructura de arriba, con el
   gate de vista previa incluido.
2. Corré el grep de lenguaje relativo a fechas (regla de informe-bigtech, sin cambios).
3. Agregá la card en el picks-list de `#inversiones` y la entrada al principio de
   `informes/manifest.json`, mismo formato que informe-bigtech. La lista fija de la home no se toca.
4. Probá en el navegador que los gráficos Canvas renderizan y que ningún `drawHBars` corta un label
   (los nombres de segmentos bancarios — "Consumer & Community Banking", "Global Wealth & Investment
   Management" — son largos, chequealo con más cuidado que en tech).
5. Antes de dar la Sección 14 por terminada, corré el chequeo de sesgo de arriba y recalculá con un
   script (no a mano) cada promedio/footnote/blend, igual que exige informe-bigtech.
