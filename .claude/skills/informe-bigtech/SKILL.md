---
name: informe-bigtech
description: "Use when writing or updating institutional-grade equity research for big tech / semiconductor names in the 'Inversiones' section of manfredi.investment.com — individual stock/ADR deep-dive analysis with full investment thesis, financial statement analysis, industry positioning, and valuation (DCF + comparable companies) culminating in an explicit fair value. Scoped to big tech / semis (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, NFLX, etc.) — sectors like banks, energy, or defensive/dividend names need a different analysis plan and should get their own skill instead of reusing this one. Each ticker ships as a standalone HTML report in `informes/<ticker>.html`, linked from the picks-list and the hero widget. Trigger on: 'informe de [ticker]', 'análisis de [empresa]', 'tesis de inversión', 'price target', 'valuación de [activo]', 'reporte institucional', 'nuevo pick', earnings/10-Q/10-K release for a tracked big-tech ticker."
metadata:
  version: 2.1.0
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
    reversión histórica + consenso Wall Street, los cinco promediados en el blend final (ver regla de
    "Reversión histórica y consenso siempre entran al blend" más abajo — ninguno de los dos se
    excluye ni se deja como "referencia externa" por default), más los métodos adicionales de la
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
- Fair value final = blend explícito y declarado, promedio simple de DCF Base + comparables +
  reversión histórica + consenso Wall Street (+ SOTP cuando aplique) — nunca un número "de ojo", y
  nunca dejando reversión o consenso afuera del promedio sin pasar primero por la regla de "ventana
  limpia" de más abajo.

**Regla no-negociable: el margen de OCF del DCF tiene que estar anclado en el OCF real reportado, no
en una analogía al margen operativo (regla agregada 05-ago-2026, tras un caso real en INTC donde el
DCF Bear daba $0 y el Base $13 porque el margen de OCF Año 1 se había estimado "a ojo" por parecido
al margen operativo GAAP/no-GAAP, sin cruzarlo contra el estado de flujo de efectivo real — al
recalcularlo contra el OCF TTM real, el Bear subió a $1.46 y el Base a $23.91, un cambio de +75% en
el Base):**
- Antes de fijar el margen de OCF (año 1 → año 5) de cada escenario, calculá el margen de OCF real de
  los últimos 4-8 trimestres reportados (`NetCashProvidedByUsedInOperatingActivities` en XBRL —
  ojo, en los 10-Q suele venir acumulado YTD, no trimestral: hay que restar el trimestre anterior
  para aislar el standalone, igual que con revenue/net income) y usalo como ancla del caso Base del
  año 1, no una cifra derivada del margen operativo por analogía. El margen de OCF y el margen
  operativo son cosas distintas — el OCF suma de vuelta partidas no-caja (D&A, compensación en
  acciones, y en casos atípicos ganancias/pérdidas de revaluación no-caja) que pueden hacer que el
  OCF real esté muy por encima (o, en compañías con mucho capital de trabajo negativo, por debajo) de
  lo que el margen operativo sugeriría a simple vista.
- Si el OCF real de los últimos trimestres es volátil (común en compañías con partidas no-caja
  grandes, ganancias/pérdidas puntuales, o negocios cíclicos), no promedies sin más: identificá si
  algún trimestre está inflado o deprimido por una partida específica no recurrente y decilo
  explícitamente en el texto, en vez de dejar que ese ruido se cuele sin comentario en el supuesto
  del año 1.
- **Chequeo de sesgo obligatorio antes de dar el DCF por terminado:** si el escenario Bear da un fair
  value de $0 o negativo, o si el Base queda a más de ~60-70% del precio de mercado, pará y
  preguntate explícitamente: ¿este resultado viene de datos reales (deuda, dilución, capex guiado por
  la propia compañía) o de un supuesto que estimé por parecido/intuición y nunca crucé contra un dato
  duro? Revisá en este orden: (1) margen de OCF del año 1 vs. OCF real reciente (la causa más común
  del sesgo, ver arriba), (2) capex del año 1 vs. guía real de la compañía — un capex "congelado" en
  el nivel más alto guiado incluso en el escenario Bear, cuando en la realidad la propia compañía
  ajustaría el capex si la demanda decepcionara, es otra fuente común de sesgo a la baja, (3) el
  ingreso base (año 0) — ¿es un dato real o consenso, o una extrapolación propia sin anclar? Un DCF
  que da un resultado extremo después de este chequeo (y sigue dando extremo) es un hallazgo legítimo
  que hay que reportar con confianza, no suavizar — pero solo después de haber descartado que el
  extremo viene de un supuesto no verificado, no una característica real del negocio. No se trata de
  ajustar el número para que "se vea mejor": se trata de no dejar pasar un error de calibración
  disfrazado de rigor.
- **Cada supuesto del escenario Bear que se desvíe del nivel ya alcanzado necesita una razón
  documentada en el Registro de Riesgos, no solo "es el caso pesimista" (regla agregada 05-ago-2026,
  tras un segundo ajuste en el mismo informe de INTC):** un Bear que hace *retroceder* un margen por
  debajo del nivel que la compañía ya demostró, sin una causa específica citada (competencia
  concreta, pérdida de un cliente concreto, etc.), es un supuesto sin anclaje — el Bear defendible
  por defecto es que la mejora *se estanca* en el nivel ya alcanzado, no que retrocede sin motivo. Si
  el negocio tiene mucha deuda neta relativa al FCF proyectado (equity apalancada), avisá
  explícitamente en el texto —no solo en una tabla— que la dispersión entre Bear y Bull va a ser
  mucho más amplia que en una cobertura con balance sano, y por qué (el equity es un residuo chico
  después de pagar la deuda, así que cualquier diferencia operativa razonable entre escenarios se
  amplifica en términos porcentuales) — un lector que ve un rango de 15x entre Bear y Bull sin esa
  explicación asume que el modelo está roto, no que está siendo honesto sobre el apalancamiento.

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

**Compañías con segmentos de rentabilidad muy distinta (cloud/ads de alto margen diluido por un
negocio core de menor margen):** un DCF consolidado que mezcla, en un solo flujo de caja, un
segmento de ~35-40%+ de margen operativo (AWS, Azure, Google Cloud, la parte de publicidad de un
marketplace) con un negocio core de márgenes finos (retail, hardware, dispositivos) diluye
sistemáticamente la parte más valiosa del negocio — es la razón documentada por la que la cobertura
de research de Wall Street sobre estas compañías usa rutinariamente **sum-of-the-parts (SOTP)**
además de un DCF único, y por la que un DCF consolidado sin SOTP tiende a dar fair values muy por
debajo de precio de mercado y de los price targets de los bancos, no porque el mercado esté "pagando
de más" sino porque el propio método tiene un sesgo estructural a la baja. Cuando el negocio bajo
cobertura tenga esta estructura de segmentos, sumá como método adicional del blend (no solo como
referencia externa):
- **SOTP propio por múltiplo de ingresos**: aplicá un múltiplo EV/Ingresos moderado y explícito al
  segmento de alto margen (ej. 8-13x a un cloud de 35-40% de margen operativo y crecimiento de
  doble dígito alto — nunca copiés sin más un múltiplo agresivo publicado por analogía con
  compañías puras de IA; si citás uno así, etiquetalo como referencia externa, no como caso propio)
  y un múltiplo más conservador al resto del negocio (1.5-3x ingresos para retail/hardware maduro,
  ajustado por margen y crecimiento). Declará la base de ingresos usada (TTM o tasa anualizada del
  trimestre) y de dónde sale cada múltiplo.
- Si existe una nota pública reciente de un banco o research shop con su propia SOTP, citala aparte
  como referencia (no la promedies con la tuya) — mismo tratamiento que el SOTP externo de la regla
  de "apuesta de plataforma" de abajo.
- Este SOTP entra al blend final junto con el DCF Base y comparables (sumándose a la reversión
  histórica y al consenso, no reemplazándolos por default — ver regla de "ventana limpia" más abajo
  para cuándo sí corresponde reemplazar reversión por SOTP).

**Usar datos reales de eficiencia de costos ya divulgados por management, no supuestos genéricos
conservadores, para el margen y el capex del DCF:** si la compañía ya cuantificó públicamente (en el
comunicado de resultados o la earnings call) una ventaja de costo concreta — chips propios que
reducen el capex o mejoran el margen en X puntos básicos, automatización que reduce costo por unidad,
eficiencia de batería/manufactura — ese dato concreto y ya público tiene que informar la velocidad de
expansión de margen y de normalización de capex de los casos Base y Bull del DCF. Un DCF que ignora
esa evidencia y usa una curva de normalización genérica y lenta "porque así es como se hacen los DCF
conservadores" no es más riguroso — es menos preciso, porque descarta información real y disponible.
Citá la fuente concreta (earnings call, comunicado) de esa ventaja de costo en el texto del Método 1.

**Reversión histórica y consenso de Wall Street siempre entran al blend — no se excluyen ad hoc
(regla agregada 05-ago-2026, tras auditar 9 informes y encontrar que la inclusión/exclusión de estos
dos métodos, no el WACC ni el crecimiento, era la causa real de que el fair value quedara
sistemáticamente por debajo del mercado en 7 de 9 casos):**

- **Consenso de Wall Street**: siempre se promedia dentro del blend final, nunca se muestra solo como
  "referencia externa, no promediada" ni como "piso mínimo" aislado. Es información de mercado tan
  legítima como un múltiplo de comparables — si comparables entra al promedio, consenso también.

- **Reversión histórica**: si el P/E histórico propio de la compañía tiene una dispersión extrema
  (rango de 5-10 años que varía más de 20-30 puntos según la fuente, o que incluye P/E negativos o de
  cientos de x), **antes de excluirla del blend, distinguí la causa**:
  - **Dato contaminado** (ganancia neta casi nula/negativa en algunos trimestres por cargos puntuales
    de M&A, impuestos, litigios — un problema del denominador, no del negocio): reconstruí una
    **ventana limpia** en vez de descartar el método entero — el P/E promedio de los últimos 4
    cierres de trimestre fiscal, cada uno calculado con el precio real de esa fecha sobre el EPS TTM
    vigente en ese momento, excluyendo específicamente los trimestres contaminados. Aplicá ese
    múltiplo limpio al EPS TTM actual y usá ese resultado en el blend. Mostrá igual el rango
    contaminado completo, por transparencia, pero como referencia aparte — no como el número del
    método.
  - **El múltiplo actual es alto porque el crecimiento cambió de escalón de forma real** (la empresa
    entró en un régimen de crecimiento estructuralmente más alto, no una burbuja): esto NO es motivo
    para excluir la reversión ni para forzarla a la baja hacia un promedio viejo que describe "otra
    empresa" — se resuelve igual con la ventana limpia/reciente, no con una exclusión total.
  - Solo excluí el método del todo, como referencia aislada no incluida en el blend, si ni siquiera la
    ventana limpia da un número utilizable (ej. sigue incluyendo trimestres de ganancia negativa).
  - Reemplazar reversión por SOTP en el blend (en vez de reconstruir la ventana limpia) sigue siendo
    válido en compañías donde el SOTP aplica por la regla de "segmentos de rentabilidad muy
    distinta" de abajo — pero no es un sustituto automático, es una decisión aparte.

Ver `informes/avgo.html` (Sección 13, Método 4) como plantilla completa de la ventana limpia de
reversión, y `informes/amzn.html` (Sección 13, Método 3) como plantilla completa de SOTP por segmento
de margen — distinto del SOTP de apuesta de plataforma/opcionalidad de `informes/tsla.html`, que es
para negocios futuros todavía no monetizados, no para segmentos ya facturando con distinto perfil de
margen.

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

**Bug conocido de `drawHBars` con labels largos (reaparecido en INTC, 05-ago-2026, después de ya
haberse arreglado en AVGO el 04-ago-2026):** `padL` está hardcodeado en 128px en la definición de la
función (`var padL = opts.padL || 128, ...` — confirmá que la función tenga ese `|| 128`, no solo
`var padL = 128`, porque si a alguien se le escapa el `opts.padL ||` al copiar la función de un
informe viejo, pasar `padL:190` en la llamada no hace nada). Cualquier `drawHBars` con labels de más
de ~20 caracteres (nombres de segmentos, "EPS no-GAAP consenso pre-reporte", etc.) corta el texto
contra el borde del canvas si no se pasa `padL` explícito más grande en esa llamada puntual. Antes de
dar un informe por terminado, abrí cada chart con `drawHBars` en el navegador (no alcanza con mirar
el código) y confirmá visualmente que ningún label quedó cortado — es un bug que no tira error en
consola, solo se ve mal.

## Cómo conectar el ticker al sitio

Una vez que `informes/<ticker>.html` está listo, hay que enlazarlo desde **tres** lugares:

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
3. **Cartel de "nuevo informe"** (`informes/manifest.json`, en la raíz de `informes/`): agregar una
   entrada nueva **al principio** de la lista (el manifest va ordenado del más nuevo al más viejo,
   `list[0]` es siempre el último publicado) con este formato:
   ```json
   {
     "num": "<ticker-en-minúscula>-YYYY-MM-DD",
     "ticker": "<TICKER>",
     "title": "Nuevo informe: <Nombre de la compañía> (<TICKER>)",
     "abstract": "1-2 frases con el dato más fuerte del informe (fair value vs. mercado, la tensión
       central de la tesis) — mismo tono que el resumen ejecutivo, no un teaser genérico.",
     "date": "<fecha en español, ej. 18 de agosto de 2026>",
     "href": "informes/<ticker>.html",
     "publishedAt": "<fecha ISO, YYYY-MM-DD, la fecha real de publicación>"
   }
   ```
   No hay que tocar `index.html` para esto — `loadInformesManifest()` ya lee este archivo solo al
   cargar la página y dispara el cartel (abajo a la izquierda, primera visita del día, vence al día
   siguiente) para quien esté en la ventana de `publishedAt`. Reusa el mismo gate de membresía que
   el picks-list: si el lector no es socio, el botón "Ver informe" muestra el paywall en vez de abrir
   el HTML directo. No hace falta borrar entradas viejas del manifest — solo la más reciente
   (`list[0]`) dispara el cartel.

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
3. Agregá la card en el picks-list de `#inversiones`, el row en `heroInvCard`, y la entrada al
   principio de `informes/manifest.json` para el cartel de anuncio (ver "Cómo conectar el ticker al
   sitio"), todos linkeando a `informes/<ticker>.html`.
4. Probá en el navegador: abrí `#inversiones`, click en "Ver análisis" del ticker nuevo — debe abrir
   el informe completo en pestaña nueva con los gráficos Canvas renderizando — y repetí el chequeo
   desde el botón del widget del hero. Recorré **cada** `drawHBars` del informe (no solo el football
   field) y confirmá visualmente que ningún label quedó cortado contra el borde del canvas (ver "Bug
   conocido de drawHBars" más arriba) — este bug no tira error de consola, solo se detecta mirando.
5. Antes de dar la Sección 13 por terminada, corré el chequeo de sesgo del DCF (ver "Regla
   no-negociable: el margen de OCF..." más arriba) — recalculá cada número derivado (promedios de
   footnotes, variaciones % interanuales TTM-vs-TTM, el blend final) con un script en vez de a mano,
   y si el Bear da $0/negativo o el Base queda a más de ~60-70% del mercado, revisá primero si el
   margen de OCF y el capex del año 1 están anclados en datos reales antes de aceptar el resultado
   como hallazgo genuino.
