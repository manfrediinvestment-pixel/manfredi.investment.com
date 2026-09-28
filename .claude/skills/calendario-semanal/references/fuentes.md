# Fuentes verificadas del calendario semanal

Estado al **20-sep-2026**. La tabla que usa el sitio vive en `index.html` (`CAL_SOURCES`,
justo antes de `HTX_CAL_MESES`); esto documenta de dónde salió cada URL y cómo se verificó.
Si una URL deja de servir, corregila en `CAL_SOURCES` **verificándola de nuevo** (ver
"Cómo verificar" abajo) y actualizá esta tabla.

## Argentina

### INDEC — `https://www.indec.gob.ar/indec/web/…`

| Rutas | Página (miga de pan verificada) |
|---|---|
| `Calendario-Fecha-0` | Calendario de difusión (mes en grilla) |
| `Nivel4-Tema-3-5-31` | Economía › Precios › Precios al consumidor (IPC) |
| `Nivel4-Tema-3-9-48` | Economía › Cuentas nacionales › **EMAE** |
| `Nivel4-Tema-3-9-47` | Cuentas nacionales › Agregados macroeconómicos (**PIB**) — *no es el EMAE* |
| `Nivel4-Tema-3-35-45` | Economía › Cuentas internacionales › Balanza de pagos, PII y deuda externa (28-sep-2026) |
| `Nivel4-Tema-3-35-46` | Economía › Cuentas internacionales › Posición de inversión internacional |
| `Nivel4-Tema-3-6-18` | Economía › Industria manufacturera › Productos Industriales (EPI) (28-sep-2026) |
| `Nivel4-Tema-3-6-19` / `-20` / `-21` | Industria farmacéutica / Maquinaria agrícola / Autogeneración de energía eléctrica |
| `Nivel4-Tema-4-31-59` | Sociedad › Trabajo e ingresos › Caracterización de la PEA |
| `Nivel4-Tema-4-31-60` | Sociedad › Trabajo e ingresos › **Distribución del ingreso** (28-sep-2026) — no usar la de Mercado de trabajo |
| `Nivel4-Tema-4-31-62` / `-63` | Seguridad social / Actividades de niños, niñas y adolescentes |
| `Nivel3-Tema-3-36` | Economía › Energía (muestra el informe "Indicadores del sector energético") |
| `Nivel3-Tema-3-10` | Economía › Sector público (muestra el informe de Dotación de personal de la APN) |
| `Nivel3-Tema-3-9` | Economía › Cuentas nacionales (informe de avance del nivel de actividad) |
| `Nivel4-Tema-3-2-40` | Economía › Comercio exterior › Intercambio comercial argentino |
| `Nivel4-Tema-4-31-58` | Sociedad › Trabajo e ingresos › Mercado de trabajo |
| `Nivel4-Tema-4-31-61` | Sociedad › Trabajo e ingresos › Salarios (Índice de salarios) |
| `Nivel4-Tema-4-46-152` | Sociedad › Pobreza › Línea de pobreza |
| `Nivel3-Tema-3-1` | Economía › Comercio (supermercados, autoservicios mayoristas, centros de compras) |
| `Nivel3-Tema-3-3` | Economía › Construcción (ICC) |
| `Nivel3-Tema-3-5` | Economía › Precios (SIPM, mayoristas) |
| `Nivel3-Tema-3-6` | Economía › Industria manufacturera (UCII) |
| `Nivel3-Tema-3-13` | Economía › Turismo (turismo internacional) |
| `Nivel3-Tema-3-52` | Economía › Tendencia de negocios |

Otras categorías Nivel3 verificadas: `3-2` Comercio exterior, `3-4` Empresas, `3-7` Minería,
`3-8` Sector agropecuario, `3-10` Sector público, `3-11` Servicios, `3-12` Sistema financiero,
`3-35` Cuentas internacionales, `3-36` Energía, `3-49` Censo económico, `3-50` Pesca.

**Sin página propia todavía** (caen a `Calendario-Fecha-0`): canasta de crianza, industria
farmacéutica. Si el usuario o el sitio dan una URL mejor, agregá la regla.

### Calendario de difusión (PDF por semestre)

`https://www.indec.gob.ar/ftp/cuadros/publicaciones/calendario_2sem2026.pdf`
(1er semestre: `calendario_1sem2026.pdf`). Pie: "Actualizado al …".

### BCRA

- Calendario oficial: `https://www.bcra.gob.ar/en/reporting-calendar/` (español: `/calendario-de-informes/`).
- Informe de Pagos Minoristas: `https://www.bcra.gob.ar/informe-de-pagos-minoristas/`
- Evolución del Mercado de Cambios y Balance Cambiario:
  `https://www.bcra.gob.ar/informe-de-la-evolucion-del-mercado-de-cambios-y-balance-cambiario/`
- Boletín Estadístico, Informe sobre Bancos, otros: caen a
  `https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp` (página general).

### Presupuesto (Oficina Nacional de Presupuesto)

- Portal del año: `https://www.mecon.gob.ar/onp/presupuestos/2027`
- PDF completo: `https://www.argentina.gob.ar/sites/default/files/proyecto_de_ley_de_presupuesto_2027.pdf`
  (Mensaje MEN-2026-43-APN-JGM del 15/9/2026; tiene las tablas de supuestos macro).

## Estados Unidos

| Organismo | URL usada en `CAL_SOURCES` |
|---|---|
| BLS (CPI) | `https://www.bls.gov/news.release/cpi.nr0.htm` |
| BLS (PPI) | `https://www.bls.gov/news.release/ppi.nr0.htm` |
| BLS (empleo) | `https://www.bls.gov/news.release/empsit.nr0.htm` |
| BLS (JOLTS) | `https://www.bls.gov/jlt/` |
| BLS (precios de import./export.) | `https://www.bls.gov/mxp/` |
| DOL (reclamos) | `https://oui.doleta.gov/unemploy/claims.asp` |
| Fed (FOMC) | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` |
| Fed (Beige Book) | `https://www.federalreserve.gov/monetarypolicy/beige-book-default.htm` |
| Fed (producción industrial) | `https://www.federalreserve.gov/releases/g17/current/default.htm` |
| Fed NY (Empire State) | `https://www.newyorkfed.org/survey/empire/empiresurvey_overview` |
| Fed Filadelfia | `https://www.philadelphiafed.org/surveys-and-data/regional-economic-analysis/manufacturing-business-outlook-survey` |
| BEA (PIB) | `https://www.bea.gov/data/gdp/gross-domestic-product` |
| BEA (PCE) | `https://www.bea.gov/data/personal-consumption-expenditures-price-index` |
| BEA (cuenta corriente) | `https://www.bea.gov/data/intl-trade-investment/international-transactions` |
| Census (ventas minoristas) | `https://www.census.gov/retail/index.html` |
| Census (comercio exterior) | `https://www.census.gov/foreign-trade/index.html` |
| Census (viviendas nuevas) | `https://www.census.gov/construction/nrs/index.html` |
| Census (housing starts/permisos) | `https://www.census.gov/construction/nrc/index.html` |
| Census (bienes duraderos y pedidos de fábrica) | `https://www.census.gov/manufacturing/m3/index.html` |
| Census (gasto en construcción) | `https://www.census.gov/construction/c30/c30index.html` — **no** `c30/index.html` ni `c30/` (dan "Page not found") |
| Census (inventarios) | `https://www.census.gov/mtis/index.html` |
| ISM | `https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/` |
| S&P Global PMI | `https://www.pmi.spglobal.com/` |
| U. Michigan | `https://www.sca.isr.umich.edu/` |
| Conference Board | `https://www.conference-board.org/topics/consumer-confidence` (LEI: `/topics/us-leading-indicators`) |
| ADP | `https://adpemploymentreport.com/` |
| NAHB | `https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index` |
| NAR | `https://www.nar.realtor/research-and-statistics/housing-statistics/existing-home-sales` |
| EIA | `https://www.eia.gov/naturalgas/weekly/`, `https://www.eia.gov/petroleum/supply/weekly/` |

## Cómo verificar una URL

- **INDEC:** el `200` no significa nada (cascarón HTML para cualquier URL). Abrí una pestaña
  en `indec.gob.ar`, cargá la URL en un `<iframe>` del mismo origen, esperá ~3 s y leé
  `contentDocument.body.innerText` desde `"Inicio >"` (miga de pan + título). Se pueden
  probar varias en un solo `javascript_tool`.
- **BCRA:** los `404` son reales; comprobá `200` y el `<title>` (`grep -o "<title>…"`).
  El `<link rel="alternate" hreflang="es">` de la página en inglés da el equivalente en español.
- **Resto:** `curl -s -L -A "Mozilla/5.0 … Chrome/140" -o /dev/null -w "%{http_code}"`.
  `bls.gov` y `dol.gov` devuelven `403` a `curl` aunque el link sea válido → abrir en Chrome.

## Calendarios de fechas (dónde se ve cuándo sale cada cosa)

| Qué | Dónde |
|---|---|
| INDEC | PDF del semestre (arriba) |
| BCRA | `https://www.bcra.gob.ar/en/reporting-calendar/` |
| BEA | `https://www.bea.gov/news/schedule` |
| Census | `https://www.census.gov/economic-indicators/calendar-listview.html` (el título va **antes** de su fecha) |
| U. Michigan | `https://www.sca.isr.umich.edu/` ("Next data release") |
| S&P Global (PMI flash) | `https://www.pmi.spglobal.com/Public/Release/ReleaseDates` (UTC) |
| Fed | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` |
| Investing.com | `https://www.investing.com/economic-calendar/` (GMT-3) |

## Earnings y dividendos (desde el 28-sep-2026)

| Qué | Dónde | Notas |
|---|---|---|
| Rastreo de earnings por día | `https://api.nasdaq.com/api/calendar/earnings?date=AAAA-MM-DD` | JSON; UA de navegador + `Accept: application/json`. Cubre NYSE y Nasdaq. Puede traer fechas estimadas |
| Historial de dividendos (Nasdaq-listed) | `https://api.nasdaq.com/api/quote/<T>/dividends?assetclass=stocks` | Para NYSE devuelve "N/A": no sirve |
| Fechas ex por día | `https://api.nasdaq.com/api/calendar/dividends?date=AAAA-MM-DD` | Casi solo Nasdaq: no alcanza para NYSE |
| Anuncios (fuente primaria) | Sitio de inversores de cada empresa; GlobeNewswire / PR Newswire / Business Wire | Leer crudo con `curl -m 25` |
| 8-K en la SEC | `https://data.sec.gov/submissions/CIK<10 dígitos>.json` → `https://www.sec.gov/Archives/edgar/data/<cik>/<acc sin guiones>/<acc>.txt` | UA con mail. El `.txt` trae los anexos (ahí está "payable on …") |

Verificado el 28-sep-2026: MU (earnings 30/9, 14:30 MT, sitio de inversores de Micron);
dividendos META 28/9 (PR Newswire), GS 29/9 (8-K del 2T26), AVGO 30/9 (8-K del 3T FY26),
NVDA 1/10 (8-K del 2T FY27); BAC pagó el 25/9 (8-K). AXP todavía sin anuncio del dividendo
de noviembre.
