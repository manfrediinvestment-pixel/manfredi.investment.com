# Fuentes y analistas de acciones argentinas

Relevamiento hecho el 23-nov-2026 para armar la skill. Los datos tienen fecha: **verificar siempre
el valor vigente a la fecha de corte del informe**; esto es contexto, no input.

## Quién cubre Argentina y qué mira cada uno

| Casa | Tipo | Qué priorizan (según sus informes y notas de prensa 2026) |
|---|---|---|
| PPI (Portfolio Personal Inversiones) | Research local | Valuación relativa vs. Latam: compañías argentinas a 4,7x EV/EBITDA vs. 5,7x pares Latam; bancos ~1x P/BV vs. 2,1x región. Cartera de largo plazo nov-2026: BMA 17,5%, YPF 17%, BBAR 15%, PAMP 13%, GGAL 12,5%, TGS 10% |
| Balanz | Research local | Probabilidad política implícita en precios (estimó ~55% de reelección descontada en el Merval); preferencia por energía (Pampa, Vista) e industriales (TXAR, ALUA); selectivo en bancos (prefiere Macro). Cobertura de ~5,5x EV/EBITDA 2026 en enero. **Conflicto: el autor del sitio es agente coproductor de Balanz** |
| Adcap Grupo Financiero | Research local | Sobrepondera utilities y oil & gas, subpondera bancos. Picks: YPF, Vista, Pampa, Central Puerto, TGS, TGN, Transener |
| Allaria | Research local | Valor intrínseco por suma de partes con **descuento de holding**: Cresud = IRSA + campos − 15%; IRSA con 10% |
| IEB | Research local | Prima de riesgo país en la valuación: "el mercado no valúa por el riesgo corporativo, le asigna riesgo electoral"; banda de riesgo país 700-900 pb como base |
| Latin Securities, Cohen, Facimex, Delphos, Rava | Research local | Estrategia, flujos, MSCI (Rava: recalificación no antes de 2027) |
| Citi | Banco de afuera | Bancos por ROE real sostenible: Galicia ~17,3% de ROE sostenible; Macro subió guía de ROE ajustado de ~8% a ~12% en 2026 |
| BofA | Banco de afuera | Merval el mercado más barato de Latam: 8,1x P/E fwd vs. 10,5x media histórica (descuento 23%). Targets ADR: GGAL USD 58, BMA USD 112 |
| Goldman Sachs | Banco de afuera | Targets ADR recortados por menor rentabilidad esperada y macro (BMA 110→95, GGAL 50→43); ROE trimestral proyectado GGAL 9,4%, BBAR 8,8% |
| Morgan Stanley | Banco de afuera | Bancos; ve la reclasificación MSCI a emergente recién hacia 2028 |
| UBS, Santander, JPM, BTG Pactual | Bancos de afuera | Bancos (UBS recortó GGAL 60→45), energía, real estate (BTG: IRSA USD 22,60, CRESY USD 14,72); JPM sobre Telecom |
| Un banco de afuera (no identificado en la nota) | — | Primas de riesgo país distintas por empresa en el mismo modelo: 900 pb Central Puerto (desde 800), 600 pb Pampa y TGS → λ distinto por empresa |

**Qué se repite en todos:** (1) todo en dólares, (2) riesgo país como variable maestra, (3) múltiplos
contra Latam con descuento, (4) ROE real en bancos, (5) suma de partes con descuento en holdings,
(6) escenarios políticos con probabilidad, (7) energía/Vaca Muerta como el sector con tesis propia
independiente del ciclo local.

## Datos de contexto relevados (con fecha)

- Riesgo país (EMBI, JP Morgan): ~851 pb a mediados de nov-2026; ~550 en may-2026. Escenarios
  citados por analistas: 300 pb (optimista extremo), 500-600 (normalización → Merval USD 60-70),
  700-900 (base IEB), 950-1.050 (negativo).
- Damodaran (tabla jul-2026, fuente secundaria — confirmar en `ctryprem`): ERP total Argentina
  ~14,87%, prima madura 4,17%.
- MSCI: jun-2026 mantuvo Argentina como **standalone** y no abrió consulta de reclasificación.
- Dividendos: Com. "A" 8226 BCRA (vigente desde 14-abr-2025) → giro de utilidades de ejercicios
  iniciados desde 1-ene-2025. Las empresas giraron ~USD 4.000 M ene-sep 2026 (récord en 10 años).
  Utilidades acumuladas en años de cepo: siguen restringidas.
- ON corporativas: YPF 2029 ~7,4%, YPF 2031 ~7,6%, TGS 2031/2035 ~7,3%, Telecom 2033 ~8,6% (ley
  extranjera, 2025-26). "Riesgo país corporativo" ~420 pb vs. soberano ~700 en el mismo momento.
  YPF, Pampa, Vista y Pluspetrol con calificación Moody's por encima del soberano.
- Bancos (sistema): ROE 6,5% en jul-2026 (ADEBA); mora 7,75% en ago-2026 (BCRA); Macro ROE 14,3%
  en 2T26.
- Tipo de cambio real multilateral ~40% por debajo del promedio de 25 años (IERAL, 2026).
- Loma Negra apagó su horno principal en may-2026; despachos de cemento −13,2% interanual en abril
  (AFCP). Granel (obra pública/industria) mejor que bolsa (autoconstrucción).
- YPF/Burford: el 27-mar-2026 la Cámara del Segundo Circuito revocó la condena de USD 16.100 M;
  rechazó la reconsideración en abril. Pendiente: eventual certiorari y la vía CIADI.
- RIGI: ~23 proyectos aprobados por ~USD 49.800 M (jul-2026), 98% minería e hidrocarburos;
  desembolsos efectivos todavía chicos; prorrogado un año en feb-2026.
- PASO 2019 (referencia de Bear electoral): Merval −37,9% en pesos en un día, riesgo país 872 →
  1.472 pb, oficial 45,40 → 55,75.

## Fuentes primarias (dónde buscar cada cosa)

| Dato | Fuente |
|---|---|
| Estados contables completos | CNV — Autopista de Información Financiera (AIF) |
| 20-F / 6-K de ADRs | SEC EDGAR |
| Precios BYMA, ON, cauciones, históricos | skill `byma` (open.bymadata.com.ar) |
| Precios live, CCL/MEP, ADRs, históricos | skill `data912` (data912.com) |
| Merval USD, riesgo país histórico | Rava (rava.com, perfil MERVAL USD), Ámbito |
| IPC (deflactar) | INDEC |
| Expectativas macro | REM del BCRA (mensual) |
| Bancos | BCRA "Informe sobre Bancos", central de deudores, ADEBA (informe mensual) |
| Tarifas reguladas | ENRE, ENARGAS (resoluciones RTI y cuadros tarifarios) |
| Energía | Secretaría de Energía (datos por yacimiento), CAMMESA |
| Cemento / acero | AFCP (despachos mensuales), Cámara Argentina del Acero |
| Prima de riesgo país | Damodaran `ctryprem.html` (enero y julio) |
| RIGI | Boletín Oficial, Ministerio de Economía |
| MSCI | Market Classification Review (junio) |

## Fuentes de las notas relevadas

- Cronista — "La City elige sus acciones favoritas tras la recalificación de Moody's" / "Riesgo
  país: a qué nivel debe caer para que mejoren las acciones" / "El S&P Merval en dólares en
  máximos históricos" / notas sobre ON corporativas.
- Bloomberg Línea — "¿La caída del riesgo país generará una ola de salidas a la bolsa?"; "MSCI
  mantiene a Argentina como mercado Standalone"; "En qué invertir en Argentina…".
- Ámbito — "Acciones argentinas: qué hay detrás de la reciente caída del Merval…"; "Golpe para las
  expectativas del mercado: MSCI mantuvo a Argentina en Standalone".
- iProfesional — "Las 10 acciones del Merval que recomienda comprar…" (PPI); "Morgan Stanley, UBS y
  Santander eligieron…"; "IRSA y Cresud presentaron balances…" (Allaria); "Bank of America ve muy
  baratas a las acciones argentinas…".
- InvertirOnline — "Balances de bancos argentinos Q2 2026".
- ADEBA — Informe de bancos sep-2026. BCRA — Informe sobre Bancos.
- Infobae / La Nación / Diario Río Negro — giro de dividendos 2026.
- La Nación / Bloomberg Línea — fallo YPF 27-mar-2026.
- Chequeado / Cronista / Perfil — estado del RIGI.
- El Economista / Forbes / Perfil — tipo de cambio real 2026.
- FACPCE — Guía de ajuste por inflación (RECPAM). KPMG / CPCE — moneda funcional NIC 21 vs. NIC 29.
- Damodaran (NYU Stern) — Country risk 2026; nota secundaria de elitecurrensea sobre la tabla de
  jul-2026.
