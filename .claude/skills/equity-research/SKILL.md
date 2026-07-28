---
name: equity-research
description: "Use when writing or updating institutional-grade equity research for the 'Inversiones' section of manfredi.investment.com (the MI_ASSETS object in index.html) — individual stock/ADR deep-dive analysis with full investment thesis, financial statement analysis, industry positioning, and valuation (DCF + comparable companies) culminating in an explicit price target and rating. Trigger on: 'informe de [ticker]', 'análisis de [empresa]', 'tesis de inversión', 'price target', 'valuación de [activo]', 'actualizar MI_ASSETS', 'reporte institucional', 'nuevo pick', earnings/10-Q/10-K release for a tracked ticker."
metadata:
  version: 1.0.0
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

## Antes de empezar — reunir datos reales

No inventes cifras. Para cada ticker nuevo:

1. **Fundamentals (SEC EDGAR XBRL)** — `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
   (headers: `User-Agent: manfrediinvestment-pixel contact@manfredi.com`). Buscá el CIK del ticker
   si no está ya en `TICKERS_CIK` de `update_reports.py`. Extraé, para los últimos 8 trimestres
   (10-Q/10-K, separando el valor standalone del trimestre cuando el concepto viene YTD):
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
   como `"fuente": "aproximado, no verificado en tiempo real"` en el output — nunca lo presentes
   como dato de mercado en vivo si no lo es. Si en el futuro se contrata una API paga (Financial
   Modeling Prep, Polygon, etc.) reemplazá esto por datos reales.

4. Anotá la fecha/quarter de la última publicación de resultados usada — todo informe debe indicar
   su fecha de corte de datos.

## Estructura obligatoria del informe

Cada ticker se escribe como un objeto en `MI_ASSETS` (`index.html`, buscar `const MI_ASSETS={`).
Mantené el schema existente y agregá el objeto `valuation` (nuevo, ver más abajo) que hoy no existe
para ningún ticker.

### 1. Resumen / métricas clave
`fullname`, `tags[]`, `rec` (`alcista`/`bajista`/`neutral` — ver regla de asignación abajo),
`recLabel`, `updatedAt` (mes/año real de esta actualización), `pe`, `evEbitda`, `revGrowth` (YoY del
último trimestre real), `opMargin`, `fcf` (TTM), `debtEbitda`, `targetPrice`, `upside` (calculado
del target vs precio spot real, no inventado).

### 2. Tesis (`thesis`, string de 1 párrafo)
3-4 oraciones. Qué es la empresa, por qué importa ahora, cuál es el driver central de la tesis y
cuál es la tensión principal (crecimiento vs valuación, moat vs competencia, etc.). Nada de relleno.

### 3. Bull / Bear (`bull[]`, `bear[]` — 4 puntos cada uno)
Cada punto con un dato concreto (%, $, fecha), no una afirmación vaga. "Azure crece 33% YoY" no
"Azure crece mucho".

### 4. Catalizadores (`catalysts[]`)
`{date, text, done, risk}`. Próximos earnings, lanzamientos, decisiones regulatorias — con fecha
real o ventana estimada. `risk:true` para catalizadores negativos/regulatorios.

### 5. Condiciones de salida (`exitUp[]`, `exitDn[]` — 3 puntos cada uno)
Umbrales concretos y verificables, no genéricos.

### 6. Valuación — `valuation` (objeto nuevo, obligatorio)

```js
valuation: {
  asOf: 'YYYY-MM-DD',              // fecha de corte de los datos usados
  dataSource: 'SEC EDGAR 10-Q Q1 FY2027 (2026-04-26) + Yahoo Finance spot',
  ttm: { revenue, ebitda, netIncome, eps, sharesOutB, netDebtB },  // USD B salvo eps/shares
  dcf: {
    wacc, terminalGrowth,
    scenarios: {
      base: { growthPath:[y1..y5], opMarginPath:[y1..y5], priceTarget, upsidePct, evB, pctEVFromTerminal },
      bull: { ... },
      bear: { ... }
    }
  },
  comps: {
    peers: [{ticker, price, source:'aproximado'|'en vivo'}],
    peerAvgEvEbitda, peerAvgPE,
    impliedPriceEvEbitda, impliedPricePE, blended
  },
  priceTarget: { value, methodology: 'ej. 60% DCF base + 40% comps', ratingRationale: '...' },
  limitations: ['string explicando qué asume el modelo y dónde puede fallar']
}
```

**Reglas del DCF:**
- Horizonte explícito de 5 años, supuestos de crecimiento y márgenes por año (no un solo número
  constante) — el crecimiento debe desacelerar hacia el terminal de forma creíble, nunca sostener
  tasas de hipercrecimiento a perpetuidad.
- WACC razonado: Rf (~yield del Treasury 10Y actual) + beta × ERP (~5%). Si la empresa tiene caja
  neta, WACC ≈ costo de equity.
- Terminal growth entre 2.5%-4%, nunca mayor al crecimiento nominal de largo plazo de la economía
  salvo justificación explícita.
- Corré siempre 3 escenarios (bear/base/bull), no solo el base — reportá el rango completo.
- Si el valor terminal es más del ~65-70% del EV, decilo explícitamente: el modelo es sensible y hay
  que leerlo con cautela (es normal en growth stocks, pero hay que ser honesto sobre ello).
- Comps: aplicá el múltiplo promedio de peers al EBITDA/EPS proyectado a 1 año (forward), no al TTM.
- Precio objetivo final = blend explícito y declarado (ej. 60/40 DCF/comps) — nunca un número "de
  ojo".

**Regla de asignación de `rec`:** si el precio objetivo blended está por debajo del precio spot,
`rec` NO puede ser `'alcista'` solo porque el negocio sea bueno — usá `'neutral'` (o `'bajista'` si
la brecha es grande) y explicá en la tesis la tensión entre calidad del negocio y valuación exigente.
"Buen negocio" y "buena inversión al precio actual" son preguntas distintas.

## Disclaimer

El informe se muestra bajo el disclaimer ya existente del sitio ("Posiciones con fines
ilustrativos. No constituyen recomendación...") — no dupliques ese texto dentro del objeto, ya está
en el `mi-footer` del modal.

## Al terminar un ticker

1. Actualizá la entrada correspondiente en `MI_ASSETS` (`index.html`) — no crees un archivo nuevo,
   este objeto es la única fuente de verdad que lee el frontend.
2. Si el ticker no tiene datos reales en `reports/fundamentals.json` (revenue/márgenes/FCF/deuda
   para los tabs de charts del modal), sumalo a `TICKERS_CIK` en `update_reports.py` y corré el
   script para generar esos datos — sin eso los tabs de gráficos van a mostrar "Cargando…" para
   siempre.
3. Probá el resultado en el navegador (abrí `#inversiones`, click en "Ver análisis" del ticker,
   revisá los 7 tabs incluyendo el nuevo "Valuación") antes de dar el trabajo por terminado.
