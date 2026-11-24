---
name: informe-argentina
description: "Use when writing or updating institutional-grade equity research for ARGENTINE stocks (acciones argentinas) en la sección 'Inversiones' de manfredi.investment.com — panel líder de BYMA y ADRs argentinos: bancos (GGAL, BMA, BBAR, SUPV, VALO), energía y oil & gas (YPF, PAMP/PAM, VIST, TGS/TGSU2, TGNO4, CEPU, EDN, TRAN, COME), materiales e industria (TXAR, ALUA, LOMA), telecom y medios (TECO2/TEO, CVH), real estate y agro (IRSA, CRES), infraestructura de mercado (BYMA) y holdings. Argentina no es un país normal: este marco reemplaza la valuación 'de manual' por la que usan los analistas que cubren Argentina — todo en DÓLARES, costo de capital con riesgo país explícito y escenarios macro (no solo de empresa), estados contables bajo NIC 29 (ajuste por inflación, RECPAM) leídos en términos reales y en USD, descalce de monedas, CCL implícito y ADR vs. local, restricciones cambiarias y de giro de dividendos, regulación (tarifas, precios, retenciones, RIGI), Estado/FGS como accionista, descuento de holding, y el 'riesgo país implícito' en el precio. Es la capa país que GOBIERNA el informe; toma prestados los métodos sectoriales de informe-bancos / informe-energia / informe-utilities cuando corresponde. Mismo esqueleto de 15 secciones y mismo gate de vista previa. Trigger on: 'informe de [ticker argentino]', 'análisis de [GGAL/YPF/PAMP/VIST/BMA/TGS/CEPU/TXAR/LOMA/TECO2/etc.]', 'acción argentina', 'Merval', 'tesis de [empresa argentina]', 'price target de [ADR argentino]', balances trimestrales de una empresa argentina bajo cobertura."
metadata:
  version: 1.0.0
---

# Equity Research Institucional — Acciones Argentinas — Manfredi Investment

Escribís research de renta variable argentina al nivel de una mesa que cubre Argentina para fondos
del exterior (los equipos de Argentina de JP Morgan, Morgan Stanley, BofA, BTG, Citi, Goldman) y de
los mejores research locales (PPI, Adcap, Latin Securities, Allaria, IEB). Mismo rigor y misma
honestidad que `informe-bigtech`, pero **el objeto valuado vive en otro planeta**: una empresa
argentina buena puede perder 60% en dólares en una semana porque cambió el país, no la empresa.
La pregunta central de cada informe no es solo "¿cuánto vale el negocio?", sino **"¿cuánto vale el
negocio en dólares, en qué Argentina, y qué Argentina está descontando el precio hoy?"**

**Relación con las otras skills:** esta skill **gobierna** el informe de cualquier empresa cuyo
negocio, activos o riesgo principal esté en Argentina. Las reglas de moneda, inflación, costo de
capital, escenarios, comparables y ponderación del blend de ACÁ pisan a las de la skill sectorial.
Del sector se toma prestado solo el método intrínseco específico (ver "Paso 0"). Para todo lo que no
se diga acá (motor Canvas, bug de `drawHBars`, gate de vista previa, conexión al sitio, grep de
fechas relativas, disclaimer), aplica `informe-bigtech` tal cual — leelo si hace falta.

**No usar esta skill** para empresas globales con sede o cotización principal afuera aunque tengan
origen o exposición argentina (MELI, GLOB, DESP, Tenaris TS, Ternium SA TX): esas van por su skill
sectorial, sumando la exposición argentina como un riesgo más, ponderada por % de ingresos.

## Regla de oro (la misma de siempre, más difícil de cumplir acá)

**El modelo dice lo que dice.** En Argentina es tentador ajustar el riesgo país hasta que el DCF
"cierre" con el precio. No. Si con un riesgo país razonable el DCF da muy por debajo (o muy por
encima) del mercado, ESO es el hallazgo — y la herramienta para explicarlo es el **riesgo país
implícito** (Método 6): decir en números qué Argentina está comprando el que paga el precio actual.

## Por qué Argentina es distinta — las 10 diferencias que cambian el análisis

Esto es lo que surge de leer a los analistas que cubren Argentina; cada punto tiene su regla abajo.

1. **La moneda de análisis es el dólar.** Nadie serio evalúa una acción argentina en pesos: el
   inversor (local o extranjero) mide su resultado en USD, y el Merval en pesos sube siempre por
   inflación. Se mide en dólares CCL (ver `references/fuentes-y-analistas.md`).
2. **Los balances están en "moneda de cierre" (NIC 29).** Argentina es economía hiperinflacionaria
   a efectos contables: las empresas con moneda funcional peso reexpresan todo por IPC y reportan
   un **RECPAM** (resultado por exposición a la inflación) que puede ser enorme y no es operativo.
   Otras (YPF, Vista, Pampa, TGS en gran parte) tienen **moneda funcional dólar** y convierten. Hay
   que saber cuál es cada caso (nota 2 de los estados contables) antes de tocar un número.
3. **El riesgo país es la variable que más mueve el precio.** Es el principal componente del costo
   de capital y el principal driver del múltiplo. Los analistas trabajan con escenarios de riesgo
   país (ej. bandas de 500-600 pb "normalización" / 700-900 "statu quo" / 950-1.050+ "estrés"), no
   con un solo número.
4. **El ciclo es político.** Las elecciones mueven más que los balances (PASO 2019: −38% el Merval
   en pesos en un día, riesgo país de 872 a 1.472 pb). El calendario electoral es un catalizador
   obligatorio.
5. **Tipo de cambio real y descalce de monedas.** Quién cobra en dólares y quién en pesos, quién
   debe en dólares y quién no, define ganadores y perdedores de cada etapa (apreciación real 2024-26
   = golpe a industria y exportadores no-commodity; devaluación = golpe a reguladas y endeudados).
6. **Regulación que cambia el negocio de un decreto a otro.** Tarifas (RTI de ENRE/ENARGAS),
   precios de combustibles, retenciones, cupos, RIGI, cepo. El riesgo regulatorio es de primer
   orden, no un renglón del registro de riesgos.
7. **Restricciones cambiarias y de dividendos.** Ganar plata no alcanza: hay que poder pagarla en
   dólares. Desde la Com. "A" 8226 (BCRA, 14-abr-2025) se giran dividendos de ejercicios iniciados
   desde 1-ene-2025; utilidades retenidas de años de cepo siguen con límites (verificar vigencia).
8. **Estructura de mercado propia.** ADR vs. acción local, CCL implícito, ratios de conversión,
   tickers sin ADR (TXAR, ALUA, COME…), liquidez baja, free float chico, MSCI "standalone" (no
   emergente) que deja afuera a los fondos indexados grandes.
9. **El accionista controlante y el Estado.** Estado nacional controlante (YPF 51%), FGS/ANSES con
   participaciones en muchas cotizantes, grupos familiares, holdings en cascada (Pampa → TGS,
   Transener, Edenor; Cresud → IRSA). El minoritario necesita un análisis explícito de cómo fue
   tratado históricamente. Las holdings cotizan con descuento (los research locales usan 10-15%).
10. **Riesgo de cola legal/institucional.** Expropiaciones (YPF 2012 → juicio Burford), pesificación
    (2002), default (2001, 2014, 2020), cepos (2011-15, 2019-25). Un bear case argentino tiene que
    poder ser genuinamente malo, pero anclado en episodios reales, no inventado.

## Paso 0 — clasificar la empresa (define el método sectorial y la exposición al riesgo país)

| Grupo | Tickers | Método sectorial (Método 2 del blend) | Exposición λ al riesgo país |
|---|---|---|---|
| Bancos | GGAL, BMA, BBAR, SUPV, VALO | P/BV justificado por **ROE real sostenible** + RIM (de `informe-bancos`, adaptado abajo) | 1.0 |
| Oil & gas upstream / integradas | YPF, VIST, (PAMP upstream) | NAV de reservas a precio mid-cycle (de `informe-energia`) + SOTP en YPF | 0.6-0.8 (exportan, se financian afuera) |
| Generación eléctrica | CEPU, PAMP (generación) | DCF por contrato (PPA en USD vs. energía base regulada) | 0.8-1.0 |
| Transporte y distribución regulada | TGS (transporte), TGNO4, TRAN, EDN | Base de capital regulatoria (RAB) × WACC regulatorio de la RTI (de `informe-utilities`) | 1.0 |
| Midstream / líquidos de exportación | TGS (líquidos + midstream VM) | DCF en USD por segmento (SOTP con el regulado) | 0.7-0.9 |
| Materiales / industria | TXAR, ALUA, LOMA | DCF en USD con EBITDA mid-cycle + EV/capacidad (USD/ton) | 0.8-1.0 |
| Telecom / medios | TECO2, CVH | DCF en USD + EV/suscriptor | 1.0 |
| Real estate / agro | IRSA, CRES | NAV (shoppings, oficinas, campos USD/ha) con descuento | 0.8-1.0 |
| Holdings | GGAL (grupo), PAMP, CRES, CVH, COME | SOTP a mercado de las cotizadas + intrínseco de las no cotizadas − **descuento de holding** | según subsidiarias |
| Infraestructura de mercado | BYMA | DCF en USD + P/E vs. bolsas Latam (B3, BMV) | 1.0 |

**λ (lambda) = qué parte del riesgo país "le toca" a esta empresa** (enfoque de Damodaran). 1.0 =
todo el negocio y el financiamiento son locales. Bajalo de 1.0 solo con un dato que lo justifique
(% de ingresos en USD de exportación, deuda emitida afuera a tasas por debajo del soberano, activos
afuera) y citalo. Nunca por debajo de 0.5: ninguna empresa con activos en Argentina escapa al cepo,
la ley local o una expropiación.

## Antes de empezar — reunir datos reales

1. **Estados contables** — fuente primaria, en este orden:
   - **CNV — Autopista de Información Financiera (AIF)**: estados contables trimestrales y anuales
     completos, con notas, en pesos (NIC 29 o NIC 21). Es la fuente obligatoria para empresas sin
     ADR.
   - **SEC EDGAR** para los que tienen ADR: 20-F anual y **6-K** trimestrales (no hay 10-Q; los 6-K
     traen el comunicado de resultados, casi siempre con **cifras ya convertidas a USD** — usalas
     como primera opción si la empresa las publica, y citá el tipo de cambio que usó).
   - **Comunicado de resultados / presentación a inversores** (web de IR): ahí están las métricas
     operativas (producción, despachos, suscriptores, mora, ROE ajustado) y casi siempre el EBITDA
     ajustado en USD.
   - Leé la **nota 2 (bases de preparación)**: moneda funcional (peso → NIC 29; dólar → NIC 21) y
     cómo convierten. Anotalo en el informe: cambia cómo se lee todo lo demás.
2. **Precio** — ADR: Yahoo chart API (igual que `informe-bigtech`). Local: skill `byma` o `data912`
   (`/live/arg_stocks`). **CCL implícito** del día con la fórmula de abajo, o `data912 /live/ccl`.
   Anotá: precio ADR, precio local en pesos, ratio, CCL usado, oficial (A3500) y brecha.
3. **Macro (fecha de corte del informe)** — riesgo país (EMBI de JP Morgan, vía Rava/Ámbito),
   CCL/MEP/oficial, IPC INDEC (serie para deflactar), tasa de política, reservas, último dato de
   actividad (EMAE), estado del acuerdo con el FMI, calendario electoral. Para el costo de capital:
   yield del Treasury 10Y, prima de mercado maduro y la tabla de Damodaran (`ctryprem`, se actualiza
   en enero y julio) — siempre con fecha.
4. **Deuda corporativa en USD** — TIR de las ON de la propia empresa (ley NY y ley local) desde
   BYMA/MAE o informes de ON: es el mejor dato del mercado sobre el riesgo crédito *de esa empresa*
   y se usa para cruzar el costo de capital (ver reglas).
5. **Sector y regulador** — según el grupo: BCRA (Informe sobre Bancos, central de deudores,
   ADEBA), ENRE/ENARGAS (cuadros tarifarios, RTI), Secretaría de Energía (producción por
   yacimiento), CAMMESA, AFCP (despachos de cemento), Cámara Argentina del Acero, ENACOM.
6. **Consenso** — targets de ADR de bancos de afuera (Citi, JPM, MS, GS, BofA, BTG, UBS, Santander,
   Itaú) y de research locales (PPI, Adcap, Latin Securities, Allaria, IEB, Cohen, Facimex, Delphos),
   vía WebSearch, cada uno con fecha. Ver `references/fuentes-y-analistas.md`.
7. Anotá fecha de corte de: resultados, precio, riesgo país, CCL e IPC. Todo en fechas fijas
   (regla de cero lenguaje relativo de `informe-bigtech`).

## Reglas de números — la contabilidad argentina sin trampas

**Regla 1 — Nunca crecimiento nominal en pesos.** "Las ventas crecieron 180%" no dice nada si la
inflación fue 200%. Toda variación se reporta **en términos reales** (lo que ya hace NIC 29 si las
dos cifras están en moneda de cierre) **y en USD**. Si una cifra viene en pesos de distintas fechas,
primero llevala a la misma moneda.

**Regla 2 — Trimestre aislado bajo NIC 29.** Los estados vienen acumulados (YTD) y cada informe
reexpresa los anteriores. Para aislar un trimestre en moneda de cierre:
`Q_t = YTD_t − YTD_{t−1} × (IPC_t / IPC_{t−1})` (función `trimestre_standalone` en
`modelos/_ar.py`). Restar dos YTD de informes distintos sin reexpresar es el error más común.

**Regla 3 — Serie en USD: desreexpresar y convertir al tipo de cambio del período.** Para la serie
histórica en dólares de una empresa NIC 29: cada trimestre en moneda de cierre se lleva a pesos
nominales de ese trimestre (`× IPC_q / IPC_cierre`) y se divide por el tipo de cambio **promedio**
de ese trimestre (flujos) o el de **cierre** (saldos de balance). Si la empresa publica sus cifras
en USD (casi todas las que tienen ADR), usá las suyas y citá su metodología.

**Regla 4 — Qué tipo de cambio.** Flujos operativos → **oficial** (A3500), porque es al que la
empresa factura y paga. Precio de la acción y capitalización → **CCL implícito** (o el ADR
directamente). Si la brecha oficial-CCL supera ~10%, el EBITDA en USD oficiales sobreestima lo que
vale para un inversor que sale por CCL: mostrá ambos y explicitá cuál usa cada método. En años de
cepo duro (2019-2025), cualquier serie histórica en USD se arma con CCL, nunca con oficial.

**Regla 5 — Separar lo que no es operativo.** Del resultado neto se aíslan y se explican por
separado: RECPAM, diferencias de cambio, resultado por tenencia de títulos públicos o inventarios,
y el efecto del ajuste impositivo por inflación en el impuesto diferido. El EPS que entra a los
múltiplos es el **ajustado** (sin esas partidas), con la conciliación a la vista.

**Regla 6 — Descalce de monedas.** Tabla obligatoria en la Sección 7: % de ingresos en USD (o
atados al USD), % de costos en USD, deuda por moneda y ley, caja por moneda, vencimientos de ON de
los próximos 24 meses en USD. Una empresa que cobra en pesos y debe en dólares es otra empresa en
una devaluación.

**Regla 7 — ROE real.** En bancos y cualquier empresa NIC 29, el ROE reportado ya es real (en
moneda de cierre). Nunca compares un ROE nominal con un costo de capital en USD. Para compararlos:
`Ke real = (1 + Ke_USD) / (1 + inflación EE.UU. de largo plazo) − 1` (supuesto implícito: paridad
del poder adquisitivo de largo plazo; decilo en Limitaciones).

## El costo de capital — en dólares y con riesgo país explícito

```
Ke_USD = Rf (Treasury 10Y) + β × ERP maduro + λ × CRP
```

- **β**: beta de la industria global/EE.UU. (desapalancada y reapalancada con la estructura de la
  empresa), **no** la beta contra el Merval ni contra el S&P de un ADR ilíquido. Usar una beta local
  y además sumar el CRP es contar el riesgo país dos veces.
- **CRP (prima de riesgo país)** — tres anclas, siempre las tres reportadas:
  1. Riesgo país EMBI spot (pb) y su promedio de 90 días.
  2. CRP de equity de Damodaran para Argentina (spread × volatilidad relativa equity/bonos), última
     tabla publicada, con fecha.
  3. **Spread de la ON en USD de la propia empresa** sobre el Treasury: chequeo de cordura — el
     costo de equity tiene que quedar **al menos 300-500 pb por encima** de la TIR de su propia
     deuda en dólares. Las ON de las mejores corporativas (YPF, Pampa, TGS, Vista) suelen rendir
     menos que el soberano: el riesgo país funciona como techo, pero no es el riesgo de la empresa.
- **Senda de riesgo país, no un número fijo**: el CRP del año 1 es el del escenario; del año 1 al 5
  converge linealmente al **CRP de largo plazo** del escenario, y el terminal usa ese nivel
  (`crp_path` en `modelos/_ar.py`). Piso del CRP terminal en el caso Base: el nivel de
  "normalización" que el propio mercado discute (hoy ~500-600 pb), nunca el de un país con grado
  de inversión mientras Argentina no lo tenga.
- **Crecimiento terminal en USD**: 2%-3% (por debajo del rango de `informe-bigtech`: no hay
  justificación para crecer a perpetuidad más rápido que la economía mundial en dólares).
- **WACC**: Kd = TIR de sus ON en USD (antes de impuestos), alícuota de ganancias 35% (verificar).

## Escenarios macro — la empresa dentro del país

Los tres escenarios del DCF (y del método sectorial) son **escenarios de país + empresa**, con
probabilidad explícita, y cada uno fija juntos: riesgo país, tipo de cambio real, actividad y
régimen (tarifas/precios/cepo).

| | Bear — "ruptura" | Base — "statu quo" | Bull — "normalización" |
|---|---|---|---|
| Riesgo país año 1 → largo plazo | 1.300-1.500+ → 900 | spot (prom. 90 d) → punto medio entre spot y 550 | spot → 450-550 |
| Tipo de cambio real | salto devaluatorio (ancla: 2018, 2019, dic-2023) | estable | apreciación moderada |
| Actividad / volumen | recesión (ancla en una real: 2018-19, 2020) | consenso REM del BCRA | crecimiento de consenso + inversión (RIGI) |
| Régimen | vuelta de controles/congelamiento tarifario | reglas vigentes | MSCI emergente, libre giro, tarifas plenas |
| Probabilidad por defecto | 25% | 50% | 25% |

Ajustá las probabilidades por calendario político (año electoral → más peso a las colas) y decilo.
**Cada supuesto del Bear tiene que anclarse en un episodio argentino real y citado** (no "es el caso
pesimista"): el Bear argentino puede ser muy malo, pero tiene que haber pasado antes.

## El entregable: mismo HTML, 15 secciones, contenido adaptado

`informes/<ticker>.html` (ticker en minúscula; para tickers con ADR usá el del ADR — `ggal`, `ypf`,
`pam`, `vist`, `bma`, `bbar`, `cepu`, `teo`, `tgs`, `loma`, `irs`, `cresy`, `edn`, `supv`; sin ADR,
el local — `txar`, `alua`, `tgno4`, `tran`, `come`, `byma`). Plantilla de HTML/CSS: `informes/jpm.html`
para bancos, `informes/aapl.html` para el resto. Gate de vista previa igual que `informe-bigtech`.

1. **Portada** — Fair Value en **USD por ADR** (o por acción local en USD CCL si no tiene ADR),
   precio de mercado en USD, y debajo, en chico: precio local en pesos, ratio, CCL implícito usado y
   fecha. El `verdict-bar` incluye el **riesgo país implícito** en una línea ("el precio descuenta
   ~X pb de riesgo país vs. Y pb de mercado"). Un solo número de fair value (regla de no dar rangos).
2. **Resumen Ejecutivo** — la tesis en una frase que combine empresa + país ("buen negocio, pero el
   precio ya descuenta normalización" / "el precio descuenta una Argentina peor que la actual").
3. **Historia y Evolución — cómo sobrevivió a Argentina**: qué le pasó en cada crisis (2001-02,
   2008-09, 2018-19, 2020, cepo), caída de su capitalización en USD en cada una, si reestructuró
   deuda, si cortó dividendos, cambios de control, estatizaciones o privatizaciones.
4. **Modelo de Negocio y Segmentos** (sección gratis del gate, lleva gráfico) — segmentos reales +
   **mapa de exposición**: % de ingresos dolarizados / en pesos libres / regulados; gráfico de barras
   con ese mix.
5. **Desarrollos Recientes y Contexto Macro** — último trimestre + tablero macro a la fecha de corte
   (riesgo país, CCL y brecha, inflación, tasa, actividad, FMI) y los cambios regulatorios que tocan
   a la empresa.
6. **Estados Financieros en USD y en términos reales** — últimos 2 trimestres + TTM, en USD y
   variación real; conciliación resultado reportado → ajustado (RECPAM, diferencia de cambio,
   tenencias); márgenes. Gráfico: ventas y EBITDA en USD de 8-12 trimestres.
7. **Deuda, Balance y Descalce de Monedas** — tabla de la Regla 6, perfil de vencimientos de ON,
   TIR de sus ON vs. riesgo país, deuda neta/EBITDA en USD. **Bancos**: ver bloque de bancos abajo.
8. **Flujo de Caja, Dividendos y Acceso a Divisas** — FCF en USD; política de dividendos y su
   historia (incluidos los años que no pudo pagar), dividend yield en USD, si puede girar al
   exterior y bajo qué norma, utilidades retenidas pre-2025, recompras, impuesto sobre dividendos.
9. **Comparables: locales, Latam y EE.UU.** — tres niveles: peers locales (mismo sector en BYMA),
   peers Latam en USD (Brasil, México, Chile, Colombia, Perú) y el peer global de referencia. Tabla
   con EV/EBITDA, P/E y, en bancos, P/BV y ROE. Siempre con el contexto de por qué el descuento.
10. **Gobierno Corporativo y Estructura Accionaria** — controlante y su historia con minoritarios,
    Estado nacional/provincial y **FGS-ANSES** (% y si tiene directores), free float, ADR (ratio,
    % del capital en ADR), operaciones con partes relacionadas, recompras, OPAs pasadas. Directorio
    y management (memoria anual + 20-F).
11. **Registro de Riesgos** — en capas: (a) país/macro (riesgo país, devaluación, cepo, default
    soberano), (b) político-electoral, (c) regulatorio específico, (d) legal (ej. Burford/YPF),
    (e) operativo de la empresa, (f) mercado (liquidez, MSCI, flujo de fondos). Cada riesgo con el
    episodio histórico que lo ancla.
12. **Catalizadores** — calendario con fechas: elecciones, revisiones del FMI, revisión anual de
    MSCI (junio), RTI/aumentos tarifarios, licitaciones, RIGI, vencimientos de deuda soberana,
    emisiones de ON, resultados, pago de dividendos.
13. **Modelo Proyectado y Consenso** — consenso de EPS/EBITDA en USD (bancos de afuera + locales),
    estimados del REM del BCRA para la macro, y la tabla de precios objetivo de cada casa con fecha.
14. **Valuación** — los 6 métodos de abajo, blend, riesgo país implícito, grilla, football field.
15. **Limitaciones del Modelo** — incluí siempre: supuesto de PPA de largo plazo, sensibilidad al
    riesgo país, calidad de la data histórica en USD durante el cepo, y el tipo de cambio elegido.

### Bloque específico de bancos argentinos (Secciones 6, 7, 8 y Método 2)

Un banco argentino no es un banco de EE.UU. con más inflación. Tomá de `informe-bancos` el marco
(no hay WACC, RIM, P/BV justificado, ROE vs. ROTCE), con estas diferencias:
- **Exposición al sector público**: títulos públicos + instrumentos del BCRA como % del activo. Es
  la métrica de riesgo soberano del banco; en un default el patrimonio se va con el bono.
- **Préstamos / depósitos** (históricamente bajo en Argentina: el crédito al privado es la palanca
  de crecimiento de la tesis), crédito al sector privado / PBI como contexto.
- **Calidad de cartera**: irregularidad (mora) del banco vs. sistema (BCRA: 7,75% ago-2026,
  verificar el último dato), costo de riesgo, cobertura con previsiones. En 2026 la mora de consumo
  fue el tema central; distinguí consumo vs. empresas.
- **Dolarización de depósitos y préstamos**, encajes, y margen financiero real (NIM).
- **ROE real** (reportado bajo NIC 29) vs. **ROE ajustado** que publica el banco — no son lo mismo:
  explicá la diferencia. El "ROE real sostenible" de largo plazo que usan los bancos de afuera
  (ej. Citi ~17% para Galicia en 2026) es el ancla del P/BV justificado.
- **Capital**: los bancos argentinos tienen exceso de capital enorme (RPC/APR muy por encima del
  mínimo): es colchón y a la vez ROE deprimido. Cuantificá cuánto capital "sobra".
- **P/BV justificado** = `(ROE_real − g_real) / (Ke_real − g_real)` con la Regla 7. Comparar contra
  el P/BV de mercado y contra bancos Latam (PPI 2026: bancos locales ~1x P/BV vs. ~2x región).

## Metodología de valuación — los 6 métodos

1. **DCF en USD con senda de riesgo país** (3 escenarios macro de arriba, probabilidad explícita).
   FCF en USD, Ke/WACC en USD con `crp_path`, terminal 2-3%. Reportá % del valor desde terminal.
   Bancos: el DCF se reemplaza por el **DDM de payout total** de `informe-bancos` en USD.
2. **Método sectorial** (de la tabla del Paso 0): P/BV justificado + RIM (bancos), NAV mid-cycle
   (energía), RAB × WACC regulatorio (reguladas), NAV con descuento (real estate), SOTP − descuento
   de holding (holdings). Mismos tres escenarios macro.
3. **Comparables Latam con descuento país justificado** — no "le aplico un 20% de descuento porque
   es Argentina". El descuento sale del diferencial de costo de capital:
   `múltiplo AR = múltiplo peer × (Ke_peer − g) / (Ke_AR − g)` (`multiplo_ajustado_por_pais`). Si
   el peer es de EE.UU., Ke_peer sin CRP. Mostrá la mediana de peers locales como referencia.
4. **Reversión histórica condicionada al riesgo país** — el múltiplo histórico de una acción
   argentina sin contexto no sirve: el promedio de 10 años mezcla default, cepo y euforia. Armá la
   serie del múltiplo propio (EV/EBITDA en USD, o P/BV en bancos) a cierre de cada trimestre de los
   últimos 8-10 años **junto con el riesgo país de esa fecha**, agrupala en regímenes (<800 pb,
   800-1.500, >1.500) y usá el múltiplo del régimen que corresponde al escenario Base (o una
   regresión múltiplo ~ riesgo país evaluada en el Base). Mostrá el gráfico de dispersión.
5. **Consenso** — promedio de precios objetivo de ADR de los últimos 90 días (bancos de afuera +
   research locales, cada uno con fecha y casa). Siempre entra al blend. **Conflicto de interés:**
   si se cita research de Balanz, agregá en el pie del informe que el autor es agente coproductor de
   Balanz — y no le des peso distinto al de las demás casas.
6. **Riesgo país implícito (no entra al blend — se reporta siempre)** — DCF inverso: el nivel de
   riesgo país (manteniendo el resto del caso Base) que hace que el DCF iguale el precio de mercado
   (`riesgo_pais_implicito`). Es la conclusión más útil para el lector: "el precio descuenta 1.100
   pb con el país hoy en 850 → cotiza como si Argentina empeorara" o "descuenta 450 pb → ya pagás la
   normalización". Mostralo en portada (verdict-bar), Sección 2 y Sección 14.

**Ponderación del blend:**

- **DCF en USD (o DDM en bancos): 15%**
- **Método sectorial: 15%**
- **Comparables Latam ajustados por país: 20%**
- **Reversión condicionada al riesgo país: 30%**
- **Consenso: 20%**

Misma lógica que `informe-bigtech`: los intrínsecos de largo plazo pesan menos; la reversión propia
pesa más. Si el método sectorial no aplica (ej. BYMA), su 15% pasa al DCF (30%).

**Grilla de sensibilidad (5×5): riesgo país de largo plazo × tipo de cambio real** (o × crecimiento
terminal en empresas sin exposición cambiaria relevante), recalculada con la fórmula, con la celda
Base igual al fair value publicado. **Football field**: los 5 métodos + línea de precio + línea de
fair value + marca del riesgo país implícito.

**Gráficos propios de esta skill** (Canvas, mismo motor): (a) precio en USD de la acción vs.
riesgo país invertido, 10 años, con crisis marcadas; (b) ventas y EBITDA en USD trimestrales;
(c) mapa de exposición de monedas; (d) dispersión múltiplo vs. riesgo país del Método 4.

## Chequeo de sesgo obligatorio (antes de dar la Sección 14 por terminada)

Si el DCF Base queda a más de ~50% del precio, o el Bear da cero, revisá en este orden:
1. **¿Mezclaste monedas?** Flujos en pesos nominales descontados a tasa en USD (o al revés) — es el
   error número uno en Argentina.
2. **¿Contaste el riesgo país dos veces?** CRP + beta local + escenario Bear con actividad
   destruida + CRP terminal de crisis.
3. **¿El tipo de cambio de conversión es coherente?** Oficial con brecha alta infla el EBITDA USD;
   CCL de un pico de corrida lo deprime.
4. **¿El año base es representativo?** Un año de tarifas congeladas, de cepo o de sequía (2023) no
   es mid-cycle; tampoco uno de euforia.
5. **¿El EPS/EBITDA está limpio de RECPAM y diferencias de cambio?**
Si después de esto el resultado sigue extremo, es un hallazgo: reportalo junto al riesgo país
implícito, que lo explica.

## Errores clásicos que esta skill prohíbe

- Presentar crecimiento en pesos nominales como crecimiento.
- Comparar el P/E de una argentina con el de una de EE.UU. sin ajustar por costo de capital.
- Calcular un dividend yield en USD con un dividendo en pesos de pago lejano sin convertir al CCL
  de la fecha de pago esperada.
- Tratar el ADR y la acción local como intercambiables sin mirar el CCL implícito (puede haber
  primas por liquidez o por restricciones).
- Usar el promedio histórico de 10 años del múltiplo sin condicionarlo al riesgo país.
- Ignorar al Estado/FGS como accionista o al controlante en la tesis del minoritario.
- Escribir "barata" solo porque cotiza a 4-5x EBITDA: en Argentina el múltiplo bajo es el precio
  del riesgo; la pregunta es si el riesgo bajó más de lo que el precio refleja.

## Fórmulas de mercado

- **CCL implícito** = `precio local (ARS) × ratio / precio ADR (USD)` (`ccl_implicito`). Ratios a
  verificar con el banco depositario (referencia: GGAL 10, BMA 10, BBAR 3, PAM 25, YPF 1, CEPU 10,
  TEO 5, SUPV 5, TGS 5, LOMA 5, EDN 20, CRESY 10, IRS 10 — **verificar cada vez**).
- **Precio en USD de un ticker sin ADR** = `precio local / CCL` del mismo día.
- **Merval en USD** = `Merval / CCL` — contexto de ciclo obligatorio en Sección 5.

## Disclaimer, postura, conexión al sitio

Idéntico a `informe-bigtech` (sin Buy/Hold/Sell, fair value descriptivo, disclaimer en portada y
pie, postura neutral/cautelosa si el fair value queda por debajo del precio). Agregá al pie:
"Las acciones argentinas tienen riesgo país, cambiario, regulatorio y de liquidez adicionales a los
de una acción de EE.UU.; los valores en USD dependen del tipo de cambio utilizado." Y la línea de
conflicto de interés si se citó research de Balanz.

Conexión al sitio (picks-list + `informes/manifest.json`, lista de la home fija sin tocar) igual que
`informe-bigtech`. Logo en `assets/logos/<ticker>.png` (ojo homónimos: Loma Negra empresa ≠ club).

## Modelo reproducible

Todo cálculo va en `.claude/skills/informe-argentina/modelos/<ticker>/valuacion.py`, importando
`modelos/_ar.py` (ke en USD, senda de CRP, DCF con tasa variable, trimestre NIC 29, desreexpresión,
CCL implícito, P/BV justificado real, múltiplo ajustado por país, riesgo país implícito, blend). El
script tiene que reproducir al centavo el fair value publicado. Nada a mano.

## Cadencia de rollout sugerida

Empezar por lo más líquido y seguido por la audiencia: **GGAL → YPF → PAM → VIST → BMA** (un banco,
la integrada, la holding energética, la E&P pura, el segundo banco: con esos cinco quedan probados
todos los métodos), después **TGS → CEPU → BBAR → TEO → LOMA → TXAR → IRS/CRESY**. Mismo ritmo de
siempre: 1-2 por día.

## Al terminar un ticker

1. `informes/<ticker>.html` (15 secciones), gate incluido, portada en USD con riesgo país implícito.
2. `modelos/<ticker>/valuacion.py` corre y reproduce el blend.
3. Grep de fechas relativas (`grep -in "hoy\|ayer\|mañana\|hace [0-9]* hora"`) y de pesos nominales
   sospechosos ("creció X%" sin "real" ni "en USD" al lado).
4. Picks-list + manifest.
5. Navegador: gráficos, ningún `drawHBars` cortado, la dispersión del Método 4 legible.
6. Chequeo de sesgo de arriba.
