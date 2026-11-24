# Contexto compartido — bancos argentinos (GGAL, BMA, BBAR, SUPV) — corte 20-nov-2026

Búsqueda hecha UNA vez el 23-nov-2026 para los informes de GGAL y BMA. Cada dato con fecha y fuente.
Espejo de máquina: `contexto_2026_11.py` (mismos números; los `valuacion.py` importan de ahí).
Serie histórica: `serie-trimestral.json`, generada por `construir_serie.py` (fuentes en su docstring).

**Fecha de corte: viernes 20-nov-2026** (último día con mercado local abierto; el lunes 23-nov fue
feriado en Argentina y solo operaron los ADR: GGAL USD 26,62, BMA USD 51,70, riesgo país ~1.035 pb).

## 1. Macro a la fecha de corte

| Dato | Valor | Fecha | Fuente |
|---|---|---|---|
| Riesgo país EMBI (spot) | **1.070 pb** (+236 pb en el día; máximo desde 24-oct-2024) | 20-nov-2026 | api.argentinadatos.com (serie EMBI JP Morgan); Ámbito "Crece la tensión financiera: el riesgo país saltó 15% y llegó a 1.070 puntos" |
| Riesgo país, promedio 90 días (24-ago → 20-nov) | **653 pb** (mín. 485, máx. 1.070; 65 ruedas) | 20-nov-2026 | cálculo sobre la serie de argentinadatos |
| Riesgo país, rebote | 1.035 pb | 23-nov-2026 | Infobae "Sin operaciones en el mercado local, el riesgo país cayó 30 puntos…" |
| Riesgo país, mínimo del año | ~400 pb | 10-jul-2026 | argentinahoy.com (rango 12 meses 402-925 hasta 5-nov) |
| CCL (venta) | **ARS 1.806,2** | 20/21-nov-2026 | argentinadatos /cotizaciones/dolares/contadoconliqui |
| CCL implícito GGAL / BMA | 1.802,1 / 1.803,0 | 20-nov-2026 | cálculo: local × 10 / ADR (Yahoo: GGAL.BA 4.557,5 / GGAL 25,29; BMA.BA 8.990 / BMA 49,86) |
| MEP (venta) | ARS 1.743,1 | 20/21-nov-2026 | argentinadatos /dolares/bolsa |
| Oficial mayorista (A3500 aprox.) | ARS 1.564,8 | 20-nov-2026 | Yahoo ARS=X; minorista BNA 1.600 (argentinadatos) |
| Brecha CCL / mayorista | **15,2%** | 20-nov-2026 | cálculo |
| IPC octubre-2026 | 2,2% m/m; 33,2% interanual | publicado 12-nov-2026 | INDEC vía argentinadatos /indices/inflacion |
| REM (oct-2026, publicado 5-nov) | IPC oct esperado 1,8%; 2026 dic/dic 30,4%; próximos 12 meses 21,8%; PBI 2026 +0,7%; tasa ~24% a dic | 5-nov-2026 | BCRA REM oct-2026; Bloomberg Línea; Ámbito |
| Tasa de referencia | Sin tasa de política formal (esquema de agregados monetarios, fase de remonetización 2026). Badlar bancos privados promedio 2T26: 21,48% | 2T26 | BCRA; 6-K Galicia 25-ago-2026 (tabla "Inflation, exchange rate and interest rates") |
| FMI | Acuerdo técnico por la 3ª revisión; aprobación del Directorio a principios de dic-2026 → desembolso ~USD 900 M. Pagos al FMI 2026: USD 4.483 M; 2027: USD 7.840 M. Reservas < USD 50.000 M tras un pago | nov-2026 | Forbes Argentina (n101221); iProfesional 467665; C5N |
| Financiamiento 2027 | El FT estima que faltan "casi USD 10.000 M" para cubrir la deuda de 2027 | nov-2026 | Financial Times citado por Forbes Argentina |
| Elecciones | Presidenciales y legislativas: oct-2027 (primarias ago-2027, régimen a confirmar). Legislativas de medio término: 26-oct-2025 (RP 1.222 a sep-25 → 571 a dic-25) | — | calendario electoral; serie argentinadatos |
| Qué pasó en noviembre | Riesgo país +29% en el mes; bonos y acciones en caída por dudas sobre el financiamiento 2027, actividad débil ("recesión estadística"), contagio político tras la elección de Brasil y salida de Wall Street de acciones de IA. Bancos en NY en la semana al 20-nov: SUPV −22,6%, BBAR −16,9%, GGAL −14,5%, BMA −11,5% | 20/21-nov-2026 | Ámbito; iProfesional 469257 y 469569; KCH FM; El Destape 23-nov |
| Merval | 2.848.945 pts ≈ USD 1.577 al CCL | 23-nov-2026 (Yahoo ^MERV) | Yahoo; la serie histórica del Merval en USD NO se pudo bajar (BYMA open data sin respuesta; Yahoo solo desde jul-2026): se usa el panel de ADR bancarios en USD como serie de ciclo |

### IPC INDEC — inflación trimestral (12 trimestres + oct-2026)

| Trim. | % | Trim. | % | Trim. | % |
|---|---|---|---|---|---|
| 4T23 | 53,3 | 4T24 | 8,0 | 4T25 | 7,8 |
| 1T24 | 51,5 | 1T25 | 8,5 | 1T26 | 9,5 |
| 2T24 | 18,6 | 2T25 | 6,0 | 2T26 | 6,7 |
| 3T24 | 12,2 | 3T25 | 6,0 | 3T26 | 5,8 |

Oct-2026: 2,2%. Reexpresión jun-26 → oct-26 (jul 2,1 · ago 1,7 · sep 1,9 · oct 2,2): **× 1,0814**.
Fuente: INDEC vía argentinadatos (coincide con la tabla del 6-K de Galicia: 1T26 9,44%, 2T26 6,76%).

## 2. Costo de capital

| Dato | Valor | Fecha | Fuente |
|---|---|---|---|
| Treasury 10Y | **4,91%** (4,92% el 23-nov) | 20-nov-2026 | Yahoo ^TNX |
| Prima de mercado maduro (ERP) | **4,23%** | tabla 5-ene-2026 | Damodaran `ctryprem.xlsx` (fuente original, NYU Stern) |
| Argentina en `ctryprem` | Moody's **Caa1**; default spread 6,37%; **CRP 9,71%**; ERP total 13,94%; alícuota 35% | tabla 5-ene-2026 (calificaciones actualizadas 16-feb-2026) | Damodaran `ctryprem.xlsx`, hoja "ERPs by country", fila 12 — **confirmado en la fuente original** |
| Tabla jul-2026 | ERP total ~14,87%, madura 4,17% — **NO confirmada**: el archivo publicado en la web de Damodaran sigue siendo el de ene-2026; solo aparece en una nota secundaria (elitecurrensea) | jul-2026 | se reporta como referencia, no se usa |
| CRP de los pares (misma tabla) | Brasil 3,24% (Ba1) · México 2,46% (Baa2) · Colombia 2,85% (Baa3) · Perú 2,07% (Baa1) · Chile 1,10% (A2) · EE.UU. 0 | ene-2026 | Damodaran `ctryprem.xlsx` |
| Beta del sector | Bank (Money Center) EE.UU. **0,76** (15 empresas); global 0,70; emergentes 0,59 | ene-2026 | Damodaran `betas.xls`, `betaGlobal.xls`, `betaemerg.xls` |
| Inflación EE.UU. largo plazo (Regla 7) | 2,5% | supuesto | — |

## 3. Sistema bancario

| Dato | Valor | Fecha | Fuente |
|---|---|---|---|
| Irregularidad crédito al sector privado | **7,50%** (−0,25 pp en el mes); familias **12,20%** (−0,61 pp; ~+5 pp interanual); empresas **3,82%** | sep-2026 (publicado 20-nov) | BCRA Informe sobre Bancos sep-2026 vía Cronista/El Intransigente |
| Cobertura con previsiones | 88,2% de la cartera irregular | sep-2026 | ídem |
| Refinanciaciones a familias | 3,9% del crédito a hogares (máximo en 15 años); parte de la baja de mora es pase a cuentas de orden | sep-2026 | ídem |
| ROE del sistema (12 meses) | **6,9%** (ROA 1,6%); jul-2026: 5,7% | ago-2026 (publicado 16-oct) | BCRA Informe sobre Bancos ago-2026 |
| Mora jul-2026 (ADEBA) | 7,7% | jul-2026 | ADEBA, "Informe de bancos septiembre 2026" |
| Depósitos privados | −0,3% real m/m, +1,1% real i.a. | ago-2026 | BCRA |
| Crédito | Empresas creciendo (industria); familias −1,1% real en jul-2026, más en tarjetas | jul/ago-2026 | BCRA |
| Préstamos/depósitos, exposición al sector público, capital, dolarización del sistema | no encontrados en esta búsqueda para sep-2026: se usan los de cada banco (6-K 2T26) | — | — |
| Bancos Latam vs. locales | Locales ~1x P/BV vs. ~2x región (PPI, 2026) | 2026 | skill `references/fuentes-y-analistas.md` |

## 4. Comparables Latam en USD (precios 23-nov-2026; balances 30-sep-2026)

| Banco | Ticker | P/BV | P/E fwd | ROE (TTM) | Nota de cálculo |
|---|---|---|---|---|---|
| Itaú Unibanco | ITUB / ITUB4 | **1,91x** | 7,95x | 21,0% | cap. BRL 437,9 mil M / PN 229,3 mil M |
| Bradesco | BBD / BBDC4 | **0,78x** | 5,08x | 14,2% | 153,1 / 195,0 mil M BRL |
| Banorte | GFNORTEO | **2,12x** | 8,28x | 24,9% | priceToBook de Yahoo (moneda local) |
| Bancolombia | CIB | **1,80x** | 7,29x | 19,1% | cap. USD 19,88 mil M / PN COP 38,78 bn ÷ 3.505,5 |
| Credicorp | BAP | **2,45x** | 10,36x | 19,9% | cap. USD 27,99 mil M / PN PEN 39,63 mil M ÷ 3,463 |
| Banco de Chile | BCH / CHILE | **3,27x** | 13,87x | 21,1% | 19.027 / 5.824 mil M CLP |
| Santander Chile | BSAC / BSANTANDER | **3,01x** | 11,73x | 23,3% | 14.859 / 4.943 mil M CLP |
| **Mediana Latam (7)** | | **2,12x** | **8,28x** | **21,0%** | |
| BBVA Argentina | BBAR | 0,71x | 5,9x* | 12,1%** | PN jun-26 × 1,0814 |
| Supervielle | SUPV | 0,55x | 12,8x* | ~4% | ídem |

Fuente: Yahoo Finance quoteSummary + fundamentals-timeseries (23-nov-2026); FX Yahoo (COP 3.505,5; PEN 3,463).
\* P/E sobre la ganancia del 2T26 anualizada y reexpresada. \*\* ROE 2T26 de BBVA Argentina citado por
Citi (iProfesional 13-nov-2026). GGAL y BMA se calculan en sus `valuacion.py`.

## 5. Consenso — precios objetivo del ADR (ventana 90 días: 22-ago → 20-nov-2026)

| Casa | Fecha | GGAL (USD/ADR) | BMA (USD/ADR) | Fuente |
|---|---|---|---|---|
| Morgan Stanley | 12/13-oct-2026 | **70** | **108** | iProfesional 466835 (18-oct) |
| UBS | 12/13-oct-2026 | **45** (desde 60; neutral) | **90** (desde 130; compra, preferido) | Forbes Argentina n100664 (19-oct); iProfesional 466835 |
| Santander | 12/13-oct-2026 | **103** | **150** | iProfesional 466835 |
| Allaria (local) | 27-oct-2026 | ARS 15.500 → **86,0** | ARS 22.600 → **125,4** | iProfesional 467421; convertido × 10 / CCL implícito 1.802 |
| Citi (local) | 13-nov-2026 | compra, sin número publicado | ARS 15.500 → **86,0** | iProfesional 468851 |
| Goldman Sachs | 10-ago-2026 (**fuera de ventana**) | 46 (neutral) | 105 (compra) | Forbes Argentina n95169; el 13-nov recortó targets sin publicar números |
| JPMorgan | jun-2026 (**fuera de ventana**) | 85 (2027) | 132 | iProfesional 458765 |
| Promedio Yahoo (referencia) | 23-nov-2026 | 61,89 (9 analistas) | 102,09 (8 analistas) | Yahoo financialData |

Casi todos los targets son **anteriores** al salto del riesgo país de noviembre (de ~600 a 1.070 pb).
No se encontraron targets de BofA, BTG ni JPM dentro de la ventana. No se cita research de Balanz.

Estimaciones del 3T26 (resultados pendientes: **Macro 25-nov-2026** después del cierre, call 30-nov;
Galicia ~24/26-nov, fecha no confirmada): Citi (13-nov) Galicia ARS 272.527 M (+5% vs. consenso),
Macro ARS 188.511 M (consenso 219.521 M). Goldman: ganancia recurrente real −15% t/t Galicia, −19% Macro;
NIM Macro 17,6% → 16,3%, Galicia 14,3% → 13,2%; ROE 3T26 Macro 11,2%, Galicia 9,4%; mora 9,6% Galicia,
6,1% Macro.

## 6. Serie histórica trimestral (dic-2016 → sep-2026)

En `serie-trimestral.json`: riesgo país, CCL, índice IPC, ADR GGAL y BMA, P/BV en pesos de GGAL y BMA
(desde dic-2018). Riesgo país a cada cierre, CCL y ADRs: argentinadatos + Yahoo. P/BV: precio local ×
acciones / patrimonio nominal (SEC XBRL 20-F 2018-2024 + 6-K/Yahoo 2025-2026; interpolación geométrica;
sep-2026 estimado con IPC). **Antes de 2020 el patrimonio no está reexpresado (NIC 29 en bancos rige
desde ene-2020)**: para la reversión se usa 1T20 → 3T26 (27 trimestres).

## 7. Regulación común

- **Dividendos de bancos**: Com. "A" 8410 (BCRA, 19-mar-2026) — hasta el 31-dic-2026, con autorización
  previa, distribuir hasta el **60%** de las utilidades de 2025 en **3 cuotas mensuales** desde mayo
  (mismo porcentaje que 2025; 40% en 2023). Fuente: BCRA A8410.pdf; Cronista; Bloomberg Línea.
- **Giro al exterior**: Com. "A" 8226 (14-abr-2025) — los no residentes pueden girar dividendos de
  ejercicios iniciados desde 1-ene-2025; utilidades retenidas de años anteriores siguen con límites
  (vigente a nov-2026 según skill; los dividendos de bancos 2026 corresponden a ejercicio 2025 → girables).
- **Encajes**: Com. "A" 8397 (exigencia de efectivo desde 6-feb-2026); "A" 8423 (integración diaria
  mínima en pesos ≥ 65%). Préstamos con depósitos en dólares: "A" 8446 amplía a financiaciones con
  garantía en moneda extranjera. Cuentas sueldo en USD: "A" 8460.
- **MSCI**: jun-2026 mantuvo a Argentina como **standalone**, sin consulta de reclasificación; Morgan
  Stanley ve la reclasificación a emergente recién hacia 2028; Rava, no antes de 2027. Próxima revisión
  anual: jun-2027.
- **Impuesto a los dividendos**: retención 7% (art. 97 Ley de Ganancias), según el 6-K de Macro.
