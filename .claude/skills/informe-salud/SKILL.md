---
name: informe-salud
description: "Use when writing or updating institutional-grade equity research for health care / salud en la sección 'Inversiones' de manfredi.investment.com — pharma grande y biotech con ventas (LLY, JNJ, MRK, PFE, ABBV, BMY, AMGN, GILD, NVO, AZN, VRTX, REGN), dispositivos médicos / medtech (ABT, MDT, SYK, BSX, ISRG, EW, BDX, DXCM), seguros médicos / managed care (UNH, ELV, CI, CVS, HUM, CNC, MOH) y herramientas/servicios de ciencias de la vida (TMO, DHR, A, IQV). Reemplaza el DCF consolidado de informe-bigtech por el marco que usan los fondos de salud: en pharma, suma de partes producto por producto hasta la pérdida de exclusividad (LOE) + rNPV del pipeline ponderado por probabilidad de éxito clínico; en medtech, crecimiento orgánico a moneda constante, volumen de procedimientos y base instalada; en managed care, medical loss ratio, tendencia de costo médico, reservas y reglas de Medicare Advantage. Mismo esqueleto de 15 secciones y mismo gate de vista previa. Trigger on: 'informe de [ticker de salud]', 'análisis de [LLY/JNJ/UNH/ABT/ISRG/etc.]', 'tesis de [farmacéutica/medtech/aseguradora de salud]', 'price target de [empresa de salud]', earnings/10-Q/10-K de un nombre de salud bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Salud (Health Care) — Manfredi Investment

Escribís research al nivel de una mesa institucional especializada en salud. Mismo rigor que
`informe-bigtech`, pero "salud" no es un sector con un solo marco: una farmacéutica, un fabricante de
stents y una aseguradora de salud tienen economías opuestas (la aseguradora **paga** lo que las otras
dos **cobran**). Por eso esta skill tiene un tronco común y **cuatro módulos por sub-industria** — el
Paso 0 es elegir el módulo, y el módulo manda sobre las Secciones 4, 6, 7, 11, 12 y 14.

**Relación con informe-bigtech:** todo lo que no se menciona acá (regla de oro, cero lenguaje
relativo a fechas, disclaimer, precio único en portada, motor Canvas, bug de `drawHBars`, conexión al
sitio, verificación con script) aplica igual. **Relación con informe-bancos:** managed care comparte
con bancos la idea de que el capital regulatorio limita cuánto se puede devolver (capital estatutario
de las subsidiarias aseguradoras) — ver Módulo C.

## Regla de oro (idéntica)

**El modelo dice lo que dice.** En salud el sesgo típico es doble: sobrestimar el pico de ventas de un
fármaco "de moda" (GLP-1, obesidad) o ignorar un precipicio de patentes ya fechado. Ninguno de los
dos se corrige tocando el resultado; se corrige anclando supuestos en datos (fechas de LOE reales,
probabilidades de éxito publicadas, consenso de ventas por producto).

## Paso 0 — elegir el módulo

| Módulo | Sub-industria | Ejemplos | Método intrínseco principal |
|---|---|---|---|
| A | Pharma grande / biotech comercial | LLY, JNJ (pharma), MRK, PFE, ABBV, BMY, AMGN, GILD, NVO, AZN, VRTX, REGN | SOTP por producto hasta LOE + rNPV del pipeline |
| B | Medtech / dispositivos | ABT, MDT, SYK, BSX, ISRG, EW, BDX, DXCM, ZBH | DCF consolidado (flujo estable) |
| C | Managed care / seguros médicos | UNH, ELV, CI, CVS, HUM, CNC, MOH | DCF + P/E sobre EPS normalizado, restricción de capital estatutario |
| D | Herramientas y servicios de ciencias de la vida | TMO, DHR, A, WAT, IQV, ICLR | DCF consolidado, ciclo de bioproceso |

**Conglomerados** (JNJ = Innovative Medicine + MedTech; ABT = diagnósticos + dispositivos +
nutrición + genéricos de marca; CVS = aseguradora + PBM + farmacias; CI = Evernorth PBM + seguros;
UNH = UnitedHealthcare + Optum): usá SOTP por segmento, cada segmento con el módulo que le
corresponde, y aclaralo en la Sección 4.

## Antes de empezar — datos reales (común a todos los módulos)

1. **XBRL (SEC EDGAR)** — mismo endpoint que informe-bigtech; tags estándar de ingresos, costo,
   operativo, neto, OCF, capex, deuda, caja, acciones. Además:
   - `ResearchAndDevelopmentExpense` (y `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost`
     / `ResearchAndDevelopmentInProcess` si el filer separa la I+D adquirida en compras — el IPR&D
     adquirido es la partida que más ensucia el EPS GAAP de pharma).
   - `AmortizationOfIntangibleAssets` y `FiniteLivedIntangibleAssetsNet` — el EPS "core/ajustado" de
     pharma y medtech excluye la amortización de intangibles de adquisiciones; reportá los dos.
2. **Ventas por producto / franquicia** — tabla de desagregación de ingresos del 10-Q/10-K y del
   comunicado de resultados (no confiar solo en XBRL, los ejes por producto varían por filer).
3. **Consenso** de EPS y de ventas por producto clave (WebSearch: stockanalysis, comunicados de
   brokers citados en prensa, Evaluate/visible alpha solo si hay cita pública).
4. **Precio y peers** — Yahoo, igual que informe-bigtech.
5. Fecha de corte de resultados **y** fecha de corte del estado del pipeline/regulatorio.

---

## Módulo A — Pharma grande y biotech comercial

**Cómo lo piensan los fondos:** el valor de una farmacéutica es una **suma de productos con fecha de
vencimiento** más una cartera de opciones (el pipeline). El DCF consolidado a perpetuidad falla porque
asume que las ventas de hoy siguen para siempre, cuando cada producto pierde 70-90% de sus ventas en
2-3 años después de que entra el genérico. Por eso el método dominante en research y M&A de pharma es
el **SOTP producto por producto hasta la LOE + rNPV del pipeline**.

**Datos específicos a reunir:**
- **Calendario de LOE** de cada producto que pese >3-5% de las ventas: fecha de expiración de la
  patente de compuesto y de exclusividad regulatoria en EE.UU. y UE (10-K, sección "Patents and
  Intellectual Property", y el Orange Book / Purple Book de la FDA). Distinguir fecha de patente de
  fecha probable de entrada de genérico (acuerdos de litigio suelen fijar la fecha real).
- **Exposición al "revenue gap"**: % de las ventas actuales que pierde exclusividad en los próximos
  ~5-7 años. Es el número que más mueven los fondos al mirar pharma grande.
- **Pipeline**: activos en Fase 2, Fase 3 y en revisión regulatoria, con indicación, fecha esperada
  de lectura de datos (readout) o de decisión (PDUFA), y el pico de ventas estimado por consenso si
  es público. Fuente: presentación de pipeline de la compañía + clinicaltrials.gov.
- **IRA (negociación de precios de Medicare)**: qué productos ya fueron seleccionados y su "Maximum
  Fair Price" (lista de CMS; la segunda ronda, vigente desde 1-ene-2027, trae descuentos de 38% a
  85%). Moléculas pequeñas son elegibles a los 7 años de aprobación (precio negociado efectivo a los
  9), biológicos a los 11 (efectivo a los 13) — verificá si hubo cambios de ley vigentes a la fecha.
- **Política de precios y comercio vigente**: acuerdos de precio de "nación más favorecida" (MFN),
  aranceles a medicamentos importados y compromisos de inversión en plantas en EE.UU. — verificar el
  estado a la fecha de corte vía WebSearch, no asumir.

**Adaptación de secciones:**
- **4. Modelo de negocio**: tabla de productos principales (ventas TTM, crecimiento, % del total,
  fecha de LOE EE.UU./UE, tipo molécula pequeña vs. biológico) + áreas terapéuticas + pipeline.
- **6. Estados Financieros**: ventas por producto, margen bruto, **I+D / ventas** (15-25% es el rango
  de pharma grande), SG&A / ventas, margen operativo core vs. GAAP, y reconciliación EPS core ↔ GAAP
  (IPR&D adquirido, amortización, litigios).
- **7. Deuda y Balance**: apalancamiento post-M&A (deuda neta/EBITDA) y **capacidad de compra
  ("firepower")**: cuánto M&A podría hacer sin perder la calificación — en pharma el M&A es la forma
  principal de tapar el revenue gap.
- **8. Capital allocation**: dividendo (pharma grande paga), recompras, y M&A/licencias (business
  development) de los últimos 3 años con lo que se pagó.
- **11. Riesgos**: LOE y erosión, fracaso clínico de un activo clave, IRA/MFN/aranceles, reforma de
  PBMs, litigios de producto, competencia de clase (ej. entre GLP-1), biosimilares.
- **12. Catalizadores**: readouts de Fase 3, fechas PDUFA, comités asesores de la FDA, congresos
  médicos (ASCO, ESMO, ADA, AHA, ASH), listas de CMS para negociación IRA, fallos de patentes.

**Valuación del Módulo A** (pesos del blend):

1. **SOTP por producto + rNPV del pipeline — 15%** (reemplaza al DCF):
   - **I+D como línea corporativa, no dentro de cada producto** (regla agregada 24-sep-2026, caso LLY):
     cada producto y cada activo del pipeline aportan su **margen de contribución** (OCF + I+D después
     de impuestos, menos capex, sobre ingresos — anclado en el semestre o TTM real, y si un trimestre
     es atípico por capital de trabajo, explicá qué ventana usás) y la I+D total de la compañía se
     resta una sola vez como línea negativa del SOTP. Cargar el margen después de I+D a cada producto
     y además valuar el pipeline cuenta el costo de investigar dos veces.
   - **Fechas de patente desde el Orange Book, no solo del 10-K**: bajá el archivo de datos de la FDA
     (`https://www.fda.gov/media/76860/download?attachment` → `patent.txt`, `exclusivity.txt`,
     `products.txt`; buscá por número de NDA). El 10-K da la patente de compuesto; el Orange Book
     muestra además patentes de sustancia/producto y de uso más tardías (en LLY: compuesto 2036, pero
     sustancia/producto 2039 y uso 2041) y la exclusividad regulatoria (NCE). Usá la del 10-K en el
     Base y la más tardía en el Bull. Si un activo del pipeline no tiene patentes listadas, decilo y
     declaralo como supuesto.
   - **Escenario de "renovación" obligatorio como referencia** (no entra al blend): el mismo Base con la
     franquicia principal sin erosión después de su LOE, creciendo ~2% con valor terminal. Muestra
     cuánto de la brecha contra el precio viene de las fechas de patente y cuánto de expectativas de
     crecimiento.
   - **Productos comercializados**: flujo de cada producto relevante (ventas × margen de contribución
     estimado — usá el margen de la compañía como proxy si no hay dato por producto, declarándolo, y
     si asignás una prima al producto principal, justificala con lo que diga la compañía sobre mezcla)
     hasta la LOE, y **curva de erosión post-LOE**: molécula pequeña en EE.UU. ~−80-90%
     en 12-24 meses; biológico ante biosimilares, erosión más lenta y gradual (IQVIA documenta que
     los biológicos son "mucho más durables" y que la erosión hoy depende cada vez más de decisiones
     de formulario de pagadores). Si hay un análogo real reciente (ej. Humira en EE.UU. 2023-2024 para
     biológicos, Eliquis/Januvia para moléculas pequeñas), buscá sus números reales y usalos como
     ancla, citándolos. Ajustar por IRA si el producto fue o será seleccionado.
   - **Productos "resto/base"**: agrupados, con un declive o un múltiplo explícito.
   - **Pipeline (rNPV)**: para cada activo de Fase 2 en adelante, flujo proyectado × **probabilidad de
     éxito acumulada** hasta aprobación. Benchmarks de BIO/Informa/QLS (2011-2020, 9,704 programas):
     transición Fase 1→2 **52.0%**, Fase 2→3 **28.9%**, Fase 3→presentación **57.8%**,
     presentación→aprobación **90.6%**; probabilidad de aprobación desde Fase 1 **7.9%** (5.7% en
     moléculas pequeñas nuevas, 9.1% en biológicos; hematología la más alta, oncología la más baja).
     Usá estas probabilidades por fase y ajustalas solo con razón explícita (biomarcador de
     selección, mecanismo ya validado en la misma clase, datos de Fase 2 fuertes).
   - Tasa de descuento: WACC de la compañía (el riesgo técnico ya está en la probabilidad — no lo
     cuentes dos veces subiendo la tasa).
   - Sumá, restá deuda neta, dividí por acciones diluidas. **Valor terminal: no hay perpetuidad
     sobre los productos actuales**; el valor de "plataforma" (capacidad de I+D de seguir
     descubriendo) se incluye, si se incluye, como línea separada, chica y explícita (ej. I+D
     recurrente × productividad histórica), nunca escondida en un terminal genérico.
2. **Comparables — 25%**: P/E forward (múltiplo principal del sector) de un grupo amplio de pharmas
   grandes (10-15 nombres, no 3-4, para que el percentil sea estable). **Regla anti-circularidad
   (agregada 24-sep-2026, caso LLY):** el método no puede usar el precio ni el múltiplo del propio
   ticker en ningún paso. En LLY, la primera versión aplicaba el PEG de AbbVie (1.30), casi idéntico al
   de Lilly (1.28): la cuenta era "precio × 1.30/1.28" y el método devolvía el precio de mercado. **No
   ajustes por PEG salvo que los datos del grupo lo sostengan:** antes de usarlo, corré la regresión
   P/E forward vs. crecimiento esperado del grupo; en LLY dio R² de 0.05-0.16 (en pharma el mercado
   paga duración de patentes, no crecimiento de corto plazo), y además las PEG de stockanalysis
   mezclan definiciones (algunas usan P/E trailing). Si el R² es bajo, usá el **P/E del cuartil
   superior del grupo aplicado al EPS de consenso del año siguiente, descontado un año al costo de
   equity**, con la mediana (sobre EPS de los próximos 12 meses) como piso del rango y el par más caro
   como techo. Declará el criterio.
3. **Reversión histórica — 35%**: P/E propio en ventana limpia sobre el **EPS ajustado tal como lo
   reporta la compañía**. **No sumes de vuelta la IPR&D adquirida si la compañía compra pipeline todos
   los años** (regla agregada 24-sep-2026, caso LLY): Lilly gasta ~$3-5 mil millones por año en eso y lo
   deja dentro de su EPS no-GAAP; sumarlo de vuelta inflaba la reversión ($1,204 vs. $1,169) y además
   contaba dos veces, porque el SOTP ya valúa esas compras. Solo excluí un cargo de IPR&D si es
   genuinamente extraordinario para esa compañía (una compra única fuera de su patrón). **Chequeo de LOE**: si el ticker está entrando a un precipicio de
   patentes, el P/E histórico describe una compañía con más años de exclusividad por delante —
   decilo explícitamente y, si el revenue gap es >25-30% de las ventas, usá la ventana de años en que
   la compañía tenía un perfil de LOE comparable, o documentá por qué no hay una.
4. **Consenso Wall Street — 25%**.

**Transparencia del blend (obligatoria, agregada 24-sep-2026):** en la síntesis de la Sección 13
etiquetá cada método como "independiente del precio" (SOTP, comparables) o "anclado al mercado"
(reversión, consenso: 60% del peso) y reportá el promedio ponderado de cada grupo por separado. Con los
pesos fijos de la casa el blend tiende a quedar cerca del precio; el lector tiene que poder ver qué dice
cada grupo. En LLY: independientes $614.23, anclados $1,233.89, blend $986.03.

**Sensibilidad**: WACC × probabilidad de éxito del activo #1 del pipeline (5×5) en vez de WACC ×
terminal. **Chequeo de sesgo**: si el SOTP da muy por debajo del precio, revisá (1) si tomaste la LOE
de la patente de compuesto cuando hay patentes de formulación/litigio que la extienden, (2) si
aplicaste erosión de molécula pequeña a un biológico, (3) si el pipeline tiene activos en Fase 3 que
dejaste afuera. Si da muy por encima, revisá picos de venta vs. consenso.

---

## Módulo B — Medtech / dispositivos médicos

**Cómo lo piensan los fondos:** el crecimiento orgánico es el predictor más fuerte del múltiplo —
por cada punto de crecimiento orgánico por encima del promedio de la industria (~5-6%), una medtech
suele cotizar 1-2 vueltas más de EV/EBITDA. Rango típico del sector: 10-20x EV/EBITDA y 3-6x
EV/ventas, con compañías puras de alto crecimiento (EW, ISRG) por encima. La calidad del ingreso
importa tanto como el nivel: **consumibles recurrentes (modelo "navaja y hojita") > equipos de
capital**, que son cíclicos y dependen del presupuesto hospitalario.

**Datos específicos**: crecimiento orgánico a moneda constante por segmento (comunicado),
volumen de procedimientos (ej. procedimientos de da Vinci en ISRG, base instalada de sistemas),
% de ingresos recurrentes, lanzamientos recientes y su aporte ("new product vitality"), estado
regulatorio (PMA vs. 510(k) — la PMA es una barrera de entrada más alta), reembolso (códigos CPT,
NTAP de CMS), exposición a China (licitaciones de compra centralizada VBP que bajan precios) y a
aranceles.

**Adaptación de secciones**: Sección 6 con orgánico constant-currency por segmento y
recurrente vs. capital; Sección 11 con reembolso, VBP China, retiros de producto (recalls, FDA
warning letters — buscá cartas de advertencia de la FDA vigentes), aranceles, presión de GPOs y
hospitales, disrupción de GLP-1 en procedimientos bariátricos/de apnea/ortopédicos si aplica;
Sección 12 con aprobaciones FDA, datos clínicos en congresos (TCT, ACC, AAOS), lanzamientos.

**Valuación del Módulo B**: DCF 15% (la regla de OCF anclado de informe-bigtech aplica igual) /
Comparables 25% (EV/EBITDA y P/E forward, con ajuste explícito por diferencial de orgánico usando la
regla de 1-2 vueltas por punto, declarada) / Reversión 35% / Consenso 25%. Mismo chequeo de sesgo
que informe-bigtech.

---

## Módulo C — Managed care / seguros médicos

**Cómo lo piensan los fondos:** una aseguradora de salud cobra una prima fija por miembro y paga los
costos médicos reales. El negocio es el **spread entre precio y costo médico**, y se rompe cuando la
tendencia de costo (utilización + precio unitario) sube más rápido de lo que la prima se re-precia
(el comercial se re-precia una vez al año; Medicare Advantage depende de las tarifas de CMS; Medicaid
de los estados). Es un negocio de márgenes finos (2-6% operativo) sobre ingresos enormes: 1 punto de
MLR mueve el EPS de forma desproporcionada.

**Datos específicos**:
- **MLR / medical care ratio / medical benefit ratio** (costos médicos ÷ primas) por trimestre y
  por segmento (comercial, Medicare Advantage, Medicaid, ACA). Ej.: UNH cerró 4Q2025 en 88.9% (vs.
  89.9% en 3Q2025). La estacionalidad es fuerte (el MLR sube en el año por deducibles que se agotan):
  compará siempre contra el mismo trimestre del año anterior, nunca trimestre contra trimestre.
- **Tendencia de costo médico** guiada por management y la real, **desarrollo de reservas de años
  anteriores** (favorable = reservaron de más, desfavorable = alerta), y **days claims payable (DCP)**:
  días de costo médico en reservas (`LiabilityForClaimsAndClaimsAdjustmentExpense` o el tag propio del
  filer ÷ costo médico diario) — una caída de DCP puede inflar la utilidad por reservar menos.
- **Membresía** por segmento (risk vs. ASO — administración sin riesgo), churn en el período de
  inscripción anual (AEP).
- **Medicare Advantage**: aviso de tarifas de CMS (preliminar enero/febrero, final principios de
  abril), **star ratings** (≥4 estrellas cobra bonos; el promedio ponderado 2026 fue 3.98),
  modelo de ajuste de riesgo **V28** (100% implementado en 2026 — baja el pago por codificación de
  diagnósticos), auditorías RADV. **Medicaid**: redeterminaciones y suficiencia de tarifas estatales
  (el MLR de Medicaid gestionado llegó a 92.1% en 2Q2025). **ACA**: estado de los subsidios
  ampliados — verificar a la fecha.
- **Segmentos no aseguradores** (Optum, Evernorth, CVS Health Services): PBM, provisión de atención,
  farmacia — cada uno con su propio margen; en SOTP, valorarlos aparte.
- **Capital estatutario**: las subsidiarias aseguradoras necesitan capital mínimo por regulación
  estatal (RBC) y solo pueden girar dividendos a la holding dentro de límites — el "parent cash" y los
  dividendos de subsidiarias, no la utilidad consolidada, limitan recompras y dividendos (misma
  lógica que el CET1 en informe-bancos).

**Adaptación de secciones**: Sección 6 con primas, MLR por segmento, ratio de gastos
administrativos (SG&A ÷ ingresos), margen operativo por segmento; Sección 7 con deuda/capital total
(la industria apunta a ~40% o menos), capital estatutario, DCP y reservas; Sección 8 con parent cash
y dividendos de subsidiarias; Sección 11 con tendencia de costo, V28/RADV, star ratings, tarifas
CMS, redeterminaciones de Medicaid, reforma de PBMs, investigaciones del DOJ, riesgo político;
Sección 12 con el aviso de tarifas de CMS, publicación de star ratings (octubre), el AEP y el
investor day (donde suele darse la guía del año siguiente).

**Valuación del Módulo C**: DCF 15% / Comparables 25% (**P/E forward** es el múltiplo del sector,
nunca EV/ventas por márgenes finos) / Reversión 35% (P/E propio en ventana limpia — **cuidado**: si la
compañía está en un año de "reseteo" de márgenes por tendencia de costo, usá EPS normalizado a un MLR
de mitad de ciclo, explicitando el MLR asumido y de dónde sale, en vez de aplicar el P/E histórico a
un EPS deprimido o inflado) / Consenso 25%. SOTP para conglomerados (repartiendo el 15% como en
informe-bigtech). Sensibilidad obligatoria: fair value con MLR ±100pb vs. Base.

---

## Módulo D — Herramientas y servicios de ciencias de la vida

TMO, DHR, A, WAT, IQV. Mismo marco que el Módulo B (DCF 15 / Comparables 25 / Reversión 35 /
Consenso 25), con métricas propias: crecimiento orgánico por mercado final (pharma/biotech,
académico/gobierno, industrial, diagnóstico), **bioprocesamiento** (consumibles para producir
biológicos, con ciclos de acumulación y desacumulación de inventario de los clientes), % de ingresos
recurrentes, financiamiento biotech (rondas de venture, IPOs) y presupuesto de NIH/académico como
indicadores adelantados, exposición a China, y para CROs (IQV, ICLR) book-to-bill y backlog.

---

## Pesos del blend (resumen)

Todos los módulos: **método intrínseco 15%** (SOTP+rNPV en A; DCF en B, C, D) / **Comparables 25%** /
**Reversión histórica 35%** / **Consenso 25%**. Misma lógica que informe-bigtech: los métodos que
dependen de supuestos de largo plazo pesan menos; consenso y reversión siempre entran.

## Cadencia de rollout sugerida

**LLY → JNJ → UNH → ABBV → ISRG → MRK** (cubren los cuatro módulos: obesidad/crecimiento,
conglomerado pharma+medtech, managed care, precipicio de patentes, medtech de alto crecimiento) →
PFE, AMGN, ABT, TMO, NVO, etc. si se piden. 2-3 tickers por día.

## Al terminar un ticker

1. `informes/<ticker>.html` (15 secciones) con el gate de vista previa.
2. Grep de lenguaje relativo a fechas.
3. Picks-list + `informes/manifest.json` (formato de informe-bigtech). Home no se toca.
4. Navegador: gráficos renderizan; en pharma los nombres de productos y áreas terapéuticas son
   largos — revisá cada `drawHBars`.
5. Script que recalcule SOTP/rNPV (producto por producto), MLR, blend. Chequeo de sesgo del módulo.

## Fuentes de la investigación que respalda este marco (sep-2026)

- BIO / Informa / QLS, *Clinical Development Success Rates and Contributing Factors 2011-2020*:
  https://www.bio.org/clinical-development-success-rates-and-contributing-factors-2011-2020
- IQVIA, *The Rules of Loss of Exclusivity are Being Rewritten* (2025) y *Generic and Biosimilar
  Economics in a Payer-Engineered Market* (2026):
  https://www.iqvia.com/locations/united-states/blogs/2025/07/the-rules-of-loss-of-exclusivity-are-being-rewritten
- Guía de valuación pharma (SOTP hasta LOE + rNPV): https://ibinterviewquestions.com/guides/healthcare-investment-banking/valuing-pharma-company-sotp
- DrugPatentWatch, uso de datos de vencimiento de patentes por analistas:
  https://www.drugpatentwatch.com/blog/how-financial-analysts-use-drug-patent-expiry-data-to-predict-pharma-stock-movements/
- CMS, fármacos seleccionados y precios negociados (IRA):
  https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices
- Guía de múltiplos medtech (1-2 vueltas de EV/EBITDA por punto de orgánico):
  https://ibinterviewquestions.com/guides/healthcare-investment-banking/medtech-valuation-multiples-comps
- AllianceBernstein, *Medical Technology Stocks: Innovation Endures as Valuations Reset*:
  https://www.alliancebernstein.com/corporate/en/insights/investment-insights/medical-technology-stocks-innovation-endures-as-valuations-reset.html
- GuruFocus, MLR de UNH: https://www.gurufocus.com/term/medical-loss_ratio_pct/UNH
- Healthcare Dive, star ratings 2026: https://www.healthcaredive.com/news/2026-medicare-advantage-star-ratings-winners-losers/802572/
- MedPAC, reporte de Medicare Advantage (marzo 2026, V28):
  https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch12_MedPAC_Report_To_Congress_SEC.pdf
- Mark Farrah Associates, rentabilidad de aseguradoras 2Q25 (MLR Medicaid 92.1%):
  https://secure.businesswire.com/news/home/20251021401045/en/2Q25-Profitability-Trends-for-Health-Insurance-Business-Assessed-by-Mark-Farrah-Associates
