---
name: equity-research
description: "Use when writing or updating institutional-grade equity research for the 'Inversiones' section of manfredi.investment.com — individual stock/ADR deep-dive analysis with full investment thesis, financial statement analysis, industry positioning, and valuation (DCF + comparable companies) culminating in an explicit fair value. Each ticker ships as a standalone HTML report in `informes/<ticker>.html`, linked from the picks-list and the hero widget. Trigger on: 'informe de [ticker]', 'análisis de [empresa]', 'tesis de inversión', 'price target', 'valuación de [activo]', 'reporte institucional', 'nuevo pick', earnings/10-Q/10-K release for a tracked ticker."
metadata:
  version: 2.0.0
---

# Equity Research Institucional — Manfredi Investment

Escribís research de renta variable al nivel de una mesa de research institucional (Morgan Stanley,
JP Morgan). El lector es un inversor sofisticado que va a tomar decisiones con esto. Rigor y
honestidad intelectual priman sobre "vender" la acción — un informe que siempre dice "comprar" no
sirve para nada.

## Regla de oro

**El modelo dice lo que dice.** Nunca ajustés los supuestos de un DCF para que el precio objetivo
coincida con el precio de mercado o con lo que "gustaría" que diera. Si el DCF da un valor muy por
debajo del precio de mercado con supuestos razonables, ESO es el hallazgo — repórtalo así, y
reconciliá la diferencia con juicio cualitativo (momentum, multiple expansion, moat) en vez de
maquillar los inputs. Un analista que fuerza el número no es un analista.

## Regla no-negociable: cero lenguaje relativo a fechas

El informe no se actualiza hasta el próximo reporte trimestral (~3 meses), así que **nunca uses
"hoy", "ayer", "mañana", "hace X horas" ni ningún marcador de tiempo relativo al momento de
redacción** — un lector que abra el informe en septiembre no puede encontrarse con "Microsoft
reportó hoy" sobre un resultado de julio. Escribí siempre en términos de fechas y períodos fijos:
"el 29-jul-2026", "el trimestre cerrado 30-jun-2026", "el reporte de Q4/FY2026". Antes de dar un
informe por terminado, corré `grep -in "hoy\|ayer\|mañana\|hace [0-9]* hora"` sobre el archivo final
y no dejes ninguna coincidencia real (fuera de nombres propios como "Cash and cash equivalents").
Este bug ya se coló una vez en el informe piloto de MSFT (37 apariciones de "hoy") — no repetirlo.

## Antes de empezar — reunir datos reales

No inventes cifras. Para cada ticker nuevo:

1. **Fundamentals (SEC EDGAR XBRL)** — `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
   (headers: `User-Agent: manfrediinvestment-pixel contact@manfredi.com`). Buscá el CIK del ticker
   en `TICKERS_CIK` de `update_reports.py` si ya está, o buscalo en EDGAR si es nuevo. Extraé, para
   los últimos 8 trimestres (10-Q/10-K, separando el valor standalone del trimestre cuando el
   concepto viene YTD):
   - `Revenues` o `RevenueFromContractWithCustomerExcludingAssessedTax`
   - `OperatingIncomeLoss`, `GrossProfit`, `NetIncomeLoss`
   - `DepreciationDepletionAndAmortization` (viene YTD acumulado en 10-Q — restar el trimestre
     anterior para obtener el standalone)
   - `EarningsPerShareDiluted`
   - Balance (instant, no flow): `CashAndCashEquivalentsAtCarryingValue`,
     `LongTermDebt`/`LongTermDebtNoncurrent`
   - `EntityCommonStockSharesOutstanding` (namespace `dei`, no `us-gaap`)
   - Calculá el TTM (últimos 4 trimestres standalone) para revenue, operating income, net income,
     D&A — es la base del DCF, no uses el último fiscal year si el TTM es más reciente.

2. **Precio y rango 52 semanas (Yahoo Finance chart API)** —
   `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?interval=1d&range=5d` (funciona sin
   auth; los endpoints `v7/finance/quote` y `v10/finance/quoteSummary` devuelven 401 sin cookie/crumb,
   no los uses). El campo `meta.regularMarketPrice` es el precio spot.

3. **Peers / comparables** — elegí 3-4 comparables directos del mismo sector/industria. Traé su
   precio con el mismo endpoint. Si no conseguís sus múltiplos (P/E, EV/EBITDA) de una fuente en
   vivo confiable, usá tu conocimiento de mercado como aproximación PERO etiquetalo explícitamente
   como "aproximado, no verificado en tiempo real" en el output — nunca lo presentes como dato de
   mercado en vivo si no lo es.

4. Anotá la fecha/quarter de la última publicación de resultados usada — todo informe debe indicar
   su fecha de corte de datos.

## El entregable: un HTML autocontenido en `informes/<ticker>.html`

Cada ticker cubierto se entrega como **un único documento HTML autocontenido** guardado directo en
el repo en `informes/<ticker-en-minúscula>.html` (ej. `informes/googl.html`) — no hay paso
intermedio de modal-resumen ni de objeto `MI_ASSETS`: este archivo ES el entregable completo, con
el mismo rigor de una nota de mesa de research bulge-bracket. Usá como plantilla de referencia
`informes/aapl.html` o `informes/msft.html` (mismo CSS embebido, misma estructura, mismo motor de
gráficos). Estructura obligatoria (14 secciones):

1. **Portada** — ticker, Fair Value blend propio vs. precio de mercado (`fv-block`), y un banner de
   veredicto (`verdict-bar`) con la postura del análisis en lenguaje descriptivo (nunca "Buy/Sell" —
   ver regla de disclaimer abajo) + nota de que no es recomendación de inversión, visible en la
   portada, no solo al pie.
2. Resumen Ejecutivo
3. Historia y Evolución
4. Modelo de Negocio y Segmentos
5. Desarrollos Recientes y Perspectiva
6. Estados Financieros (últimos 2 trimestres + TTM)
7. Deuda y Balance
8. Flujo de Caja y Capital Allocation
9. Comparables de Industria (3-4 peers reales, con contexto cualitativo de cada uno, no solo la
   tabla de múltiplos)
10. **Gobierno Corporativo y Estructura Accionaria** — ownership institucional/insider (GuruFocus,
    WallStreetZen), directorio, compensación del CEO/ejecutivos (SEC DEF 14A), y cualquier
    transición de liderazgo relevante. Buscar datos reales vía WebSearch, nunca inventar.
11. Registro de Riesgos
12. Catalizadores
13. **Modelo Financiero Proyectado y Momentum de Estimados** — consenso Street real (EPS/revenue
    FY+1, FY+2 vía WebSearch a stockanalysis.com/ChartMill/Zacks), estimado del próximo trimestre, y
    gráfico de revisiones de EPS de los últimos 90 días (al alza vs. a la baja). Nunca fabricar una
    proyección línea por línea a 5 años que no esté sourceada — para años sin consenso público,
    remitir explícitamente a los supuestos del DCF (sección siguiente) en vez de inventar precisión.
14. **Valuación: Cuatro (o más) Métodos y el Fair Value** — DCF (3 escenarios) + comparables +
    reversión histórica + consenso Wall Street como piso mínimo, más los métodos adicionales de la
    regla "Compañías con apuesta de plataforma" de abajo cuando corresponda, más:
    - **Grilla de sensibilidad WACC × crecimiento terminal** (5×5): recalculá el DCF con la fórmula
      real para cada combinación — nunca tipees números a mano. Calibrá el resultado para que la
      celda del caso Base reproduzca exactamente el fair value y el %EV-desde-terminal ya
      publicados.
    - **Football field** (rango bajo/alto por metodología, con líneas de referencia de precio de
      mercado y del fair value/blend propio o de la referencia externa más relevante).
15. Limitaciones del Modelo.

**Reglas del DCF:**
- Horizonte explícito de 5 años, supuestos de crecimiento y márgenes por año (no un solo número
  constante) — el crecimiento debe desacelerar hacia el terminal de forma creíble, nunca sostener
  tasas de hipercrecimiento a perpetuidad.
- WACC razonado: Rf (~yield del Treasury 10Y vigente) + beta × ERP (~5%). Si la empresa tiene caja
  neta, WACC ≈ costo de equity.
- Terminal growth entre 2.5%-4%, nunca mayor al crecimiento nominal de largo plazo de la economía
  salvo justificación explícita.
- Corré siempre 3 escenarios (bear/base/bull), no solo el base — reportá el rango completo. Además
  del promedio simple, calculá también un valor esperado ponderado por probabilidad explícita (ej.
  25/45/30) — es más riguroso que promediar sin más, y hay que reportar ambos.
- Si el valor terminal es más del ~65-70% del EV, decilo explícitamente: el modelo es sensible y hay
  que leerlo con cautela (es normal en growth stocks, pero hay que ser honesto sobre ello).
- Comps: aplicá el múltiplo promedio de peers al EBITDA/EPS proyectado a 1 año (forward), no al TTM.
- Fair value final = blend explícito y declarado (ej. promedio simple DCF Base + comparables +
  reversión histórica) — nunca un número "de ojo".

**Compañías con negocio maduro + apuesta de plataforma/opcionalidad (autonomía, IA, robótica,
plataformas todavía sin ingresos materiales):** el DCF/comparables/reversión estándar valúan
*solo* el negocio que ya factura — son retrospectivos y estáticos por diseño, y en compañías de este
tipo terminan dando un fair value que parece poco creíble frente al precio de mercado, porque no le
ponen ningún precio a la apuesta de plataforma. Cuando el negocio bajo cobertura tenga una línea de
crecimiento futuro grande y todavía no monetizada (ej. robotaxi, robótica humanoide, licenciamiento
de IA), sumá además:
- **Sum-of-the-parts (SOTP) propio**, deliberadamente conservador: valuá el negocio actual por DCF
  (como siempre) y sumale el valor de cada apuesta nueva usando la valuación de transacciones reales
  y recientes de sus comparables directos en el mercado privado (rondas de financiamiento, series de
  venture capital, adquisiciones) — nunca un TAM inventado sin anclar a una transacción real. Hacé
  también una sensibilidad simple (ej. 50%-150% del valor del comparable) en vez de un único punto.
- **SOTP externo de referencia**: si un banco o casa de research reconocida publicó su propio SOTP
  para la misma compañía, citalo aparte (no lo promedies con tus propios métodos) y comparalo
  críticamente contra transacciones de mercado privado reales — cuantificar la brecha (ej. "el
  componente X implica una valuación N veces mayor que la última ronda del comparable directo más
  cercano") es más útil que aceptar o rechazar el número sin más.
- **DCF inverso**: en vez de solo proyectar hacia adelante, partí del precio de mercado y resolvé qué
  trayectoria de crecimiento o de margen sería necesaria para justificarlo, dentro del mismo WACC y
  crecimiento terminal ya usados. Traducir el precio en supuestos concretos y verificables (ej. "el
  mercado exige un margen operativo de caja de X% para el año 5") es más honesto y más útil para el
  lector que una etiqueta de "cara" o "barata".
- El **fair value final**, en estos casos, se reporta como **rango** (mínimo del DCF del negocio
  actual a máximo del SOTP más agresivo disponible, propio o externo) en vez de forzar un único punto
  — el objetivo es que el precio de mercado quede visiblemente ubicado dentro de ese rango, no que el
  informe declare un solo número "correcto" que nadie encuentra creíble. Ver `informes/tsla.html`
  como plantilla completa de esta estructura de seis métodos (Sección 13).

**Regla de asignación de la postura (bajista/neutral/alcista):** si el fair value (o el rango) queda
por debajo del precio spot, la postura NO puede ser alcista solo porque el negocio sea bueno — usá
neutral (o bajista si la brecha es grande) y explicá en la tesis la tensión entre calidad del
negocio y valuación exigente. Cuando el fair value se reporta como rango y el precio de mercado cae
dentro de él, la postura puede ser "neutral, con sesgo cauteloso/optimista" según en qué extremo del
rango caiga el precio — pero seguí explicitando qué tiene que ser cierto para que el precio actual
tenga sentido. "Buen negocio" y "buena inversión al precio actual" son preguntas distintas.

**Disclaimer no-negociable (portada + pie):** el autor no es un asesor financiero registrado. Nunca
un rating tipo "Buy/Hold/Sell" — siempre un Fair Value descriptivo derivado del propio modelo,
etiquetado como análisis, no como recomendación personalizada. Reforzar esto en el `verdict-bar` de
portada y en el bloque `.disclosure` del pie del documento.

**Motor de gráficos:** los charts son Canvas 2D propio (sin dependencias externas, ver `<script>` al
final de `informes/aapl.html`) — reusá `drawVBars`, `drawHBars`, `drawLines`, `drawRangeBars` (para
el football field) en vez de introducir una librería nueva.

## Cómo conectar el ticker al sitio

Una vez que `informes/<ticker>.html` está listo, hay que enlazarlo desde **dos** lugares de
`index.html` — ya no existe `MI_ASSETS` ni el modal viejo, así que no hay tercer lugar que tocar:

1. **Picks-list de la sección Inversiones** (buscar `class="picks-list"`, dentro de
   `id="inversiones"`): agregar una `pick-card` nueva (copiar el bloque de AAPL o MSFT como
   plantilla) con ticker, tag, nombre, sentimiento y sparkline. El botón va con
   `href="informes/<ticker>.html" class="pick-btn" target="_blank" rel="noopener"` — **sin**
   `data-ticker` (ese atributo dispara el modal viejo vía JS, que ya no queremos para tickers
   nuevos).
2. **Widget del hero** (buscar `id="heroInvCard"`, dentro de `class="hero-bottom-row"`): agregar un
   `hero-inv-item` (copiar el bloque de AAPL o MSFT) con ticker/nombre/postura + el mismo link
   `informes/<ticker>.html`. El widget muestra 3 activos visibles: si ya hay 3 informes reales,
   sacá el placeholder `hero-inv-item--soon` ("Próximo análisis en camino"); si vas a cubrir más de
   3 en simultáneo, priorizá mostrar los más recientes y dejá el resto solo en el picks-list de
   `#inversiones` (el hero es una vidriera, no tiene que listar toda la cobertura).

No hace falta tocar `MI_ASSETS`, `reports/fundamentals.json` ni `TICKERS_CIK` — ese pipeline
alimentaba el modal resumen viejo, que quedó retirado para los tickers que usan este formato nuevo.

## Cadencia de rollout (uno por vez)

Cada informe de este nivel implica varias búsquedas web + un DCF recalculado + ~4000-6000 palabras
— es intensivo en tokens. Ritmo sugerido: **2-3 tickers por día**, no todos de una. AAPL y MSFT ya
están completos en el formato nuevo (`informes/aapl.html`, `informes/msft.html`). Orden sugerido
para seguir sumando cobertura: GOOGL → AMZN → META (mega-caps que se retroalimentan con AAPL/MSFT
en la sección de comparables) → JPM → BAC (financieras, requieren ajustar el DCF a un modelo de
descuento de dividendos o residual income en vez de FCF-to-firm estándar) → MELI → UBER → ADBE →
TSLA → NVDA, y de ahí en más cualquier activo que se pida explícitamente. Para pedir uno, alcanza
con: *"hacé el informe institucional de [TICKER], nivel AAPL"*.

## Al terminar un ticker

1. Generá `informes/<ticker>.html` completo (14 secciones) siguiendo la estructura de arriba.
2. Corré el grep de lenguaje relativo a fechas (ver regla no-negociable) y limpiá cualquier
   coincidencia antes de seguir.
3. Agregá la card en el picks-list de `#inversiones` y el row en `heroInvCard` (ver "Cómo conectar
   el ticker al sitio"), ambos linkeando a `informes/<ticker>.html`.
4. Probá en el navegador: abrí `#inversiones`, click en "Ver análisis" del ticker nuevo — debe abrir
   el informe completo en pestaña nueva con los gráficos Canvas renderizando — y repetí el chequeo
   desde el botón del widget del hero.
