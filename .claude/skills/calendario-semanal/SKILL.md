---
name: calendario-semanal
description: "Use when the user asks to build the weekly economic calendar for manfredinvestment.com — 'hacé calendario', 'calendario de la semana', 'armá el calendario económico', 'calendario semana que viene'. Researches and VERIFIES every Argentina event (INDEC release calendar, BCRA reporting calendar, budget/Congress dates) and every US event (Investing.com economic calendar cross-checked against BEA, Census, U. Michigan, S&P Global, BLS/DOL, Fed), then delivers the week as the exact JSON the manfredi-calendario Cloudflare worker serves, with every event checked against the site's source-link table (CAL_SOURCES) and previewed on a local host. Since 28-sep-2026 it ALSO builds the week's EARNINGS and DIVIDENDS (ex-dividend and payment dates) for every ticker with a report in informes/, verified against each company's investor-relations releases, and loads the three JSONs (eventos_semana, earnings_semana, dividendos_semana) into the worker's KV through the Cloudflare dashboard in Chrome. Nothing in the worker is automatic anymore: no code deploy is needed."
metadata:
  version: 2.0.0
---

# Calendario semanal — Manfredi Investment

Cada semana el usuario dice **"hacé calendario"** (o algo equivalente) y vos hacés todo:
buscás los eventos, los **verificás contra la fuente primaria**, los redactás en el estilo
del sitio, comprobás que cada uno tenga link a su fuente y **cargás la semana en el
worker** vos mismo desde el panel de Cloudflare en Chrome. No hace falta que te
reexplique nada: este documento es el proceso completo, armado y probado en las semanas
del 21 al 25 y del 28/9 al 2/10 de 2026.

**Son tres calendarios, y los tres se hacen juntos** (el usuario lo pidió el 28-sep-2026:
"cuando te llamo a esa skill hacemos todo junto"):

| Pestaña del sitio | Clave del KV | Endpoint del worker | Pasos |
|---|---|---|---|
| Económico | `eventos_semana` | `/calendario` | 0 a 6 |
| Earnings | `earnings_semana` | `/earnings` | 8 |
| Dividendos | `dividendos_semana` | `/dividends` | 9 |

Los tres se validan juntos, se miran juntos en la vista previa (paso 7) y se cargan juntos
en el worker (paso 10).

Desde el 28-sep-2026 **el worker no genera nada solo**: sirve lo que haya en el KV y, si
no hay nada, responde 404 y el sitio muestra "Sin datos disponibles". Todo sale de esta
skill. Detalle del worker en `references/worker.md`.

## Regla de oro: verificar todo, todo el tiempo

El usuario lo pidió explícitamente: **"verificando en todo momento lo que hacés"**.

- Cada fecha sale de una **fuente primaria** (INDEC, BCRA, BEA, Census, U. Michigan, S&P
  Global, Fed, DOL/BLS) o queda afuera. Investing.com es el punto de partida para EE.UU.,
  no la verificación.
- Cada **dato previo** que cites se cruza contra el organismo que lo publicó.
- El **consenso** solo lo da Investing.com; no tiene segunda fuente. Decilo en la entrega.
- Nunca uses el resumen de `WebFetch` como verificación (lo hace un modelo chico que
  puede inventar). Leé el texto crudo con `get_page_text`, `curl` o un render en Chrome.
- Si dos fuentes discrepan, **no elijas en silencio**: buscá una tercera y contale al
  usuario la discrepancia y cómo se resolvió.
- Si algo no se puede verificar, **no entra** al calendario y se lista aparte con el motivo.
- Un evento que no podés fechar no se inventa: se omite y se avisa.

## Paso 0 — Fijar la semana

- La semana es **lunes a viernes**. Si hoy es sábado, domingo o lunes temprano, es la que
  empieza el próximo lunes (o la actual si el usuario lo aclara).
- Anotá las 5 fechas (`21/9`, `22/9`, …) y el año. Formato de la semana:
  `"21/9 al 25/9 de 2026"`, `fecha` de cada día `"21/9"` (sin ceros a la izquierda).
- Antes de redactar, leé lo que está **en vivo ahora** para copiar el estilo exacto y
  guardalo en el scratchpad: es también la **copia para volver atrás** antes de pisar el KV.
  `curl -s https://manfredi-calendario.nachito2502.workers.dev/{calendario,earnings,dividends}`.

## Paso 1 — Argentina · INDEC

1. Bajá el calendario oficial del semestre:
   `https://www.indec.gob.ar/ftp/cuadros/publicaciones/calendario_2sem2026.pdf`
   (1er semestre: `calendario_1sem2026.pdf`; cambiá el año). El PDF dice al pie
   **"Actualizado al d/m/aaaa"**: anotalo.
2. **No confíes en `pdftotext`**: mezcla las dos columnas y desalinea fechas e ítems. Abrí
   el PDF en Chrome (`navigate`), apretá `End` para llegar a la parte baja, y usá `zoom`
   sobre la región del mes para leer qué ítem cae en qué día.
3. Cruzá con una segunda fuente (nota de prensa "calendario del INDEC de <mes>" vía
   `WebSearch`). Si el PDF es viejo respecto de la nota, avisá.
4. Tomá **todos** los ítems de la semana, incluso los menos conocidos (turismo, encuestas
   de supermercados, tendencia de negocios). Agrupá los de un mismo día y misma familia en
   un solo evento si quedan demasiados (ej. encuestas de supermercados + mayoristas +
   centros de compras).

## Paso 2 — Argentina · BCRA

- Leé `https://www.bcra.gob.ar/en/reporting-calendar/` con `get_page_text` (lista todas las
  publicaciones 2026 por fecha). Tomá solo las de la semana.
- Todas se publican **"al cierre de la jornada"** (lo dice la propia página).
- Nombres en castellano: Boletín Estadístico, Informe sobre Bancos, Informe de Pagos
  Minoristas, Evolución del Mercado de Cambios y Balance Cambiario, Informe Monetario
  Mensual, REM, IPOM, IEF, etc.

## Paso 3 — Argentina · presupuesto y Congreso

- El proyecto de Ley de Presupuesto **entra al Congreso el 15 de septiembre y es el del año
  siguiente**. En septiembre de 2026 el usuario dijo "presupuesto 2026", pero el que se
  discute es el **2027**: aclaráselo.
- Solo entra como evento si hay una **fecha agendada dentro de la semana** (audiencia de
  comisión, exposición de funcionarios, votación). Verificala en más de una fuente
  periodística y, si existe, en el sitio del Congreso. Sin fecha en la semana, no se
  inventa: se menciona en la entrega.
- Fuente oficial: `https://www.mecon.gob.ar/onp/presupuestos/<año>` (mensaje, articulado y
  anexos) y el PDF `https://www.argentina.gob.ar/sites/default/files/proyecto_de_ley_de_presupuesto_<año>.pdf`.
  Si citás cifras (PIB, inflación, dólar), sacalas **del PDF**, no de la prensa.
  En 2027: PIB +4,0%, IPC dic/dic 18,0%, dólar $1.847,6 a dic-2027; debate en la comisión
  de Presupuesto desde el 7/10/2026.
- En `CAL_SOURCES` ya hay una regla `presupuesto` → ONP. Un evento cuyo título contenga
  "Presupuesto" linkea solo.

## Paso 4 — EE.UU. · Investing.com + cruce con fuentes primarias

### 4a. Leer Investing.com en Chrome (sin tocar los filtros de la cuenta)

Método preferido desde el 28-sep-2026: pedirle la semana al servicio interno del
calendario, que **no cambia los filtros guardados** de la cuenta del usuario.

1. `tabs_context_mcp` → `navigate` a `https://www.investing.com/economic-calendar/`.
2. Con `javascript_tool` en esa pestaña, hacé un `POST` a
   `/economic-calendar/Service/getCalendarFilteredData` con
   `country[]=5` (EE.UU.), `importance[]=2`, `importance[]=3`, `dateFrom`/`dateTo` en
   `AAAA-MM-DD` (lunes y viernes de tu semana), `timeZone=55`, `timeFilter=timeRemain`,
   `currentTab=custom`, `limit_from=0` y el header `X-Requested-With: XMLHttpRequest`.
   Parseá `j.data` (HTML de filas `<tr>`): las filas `.theDay` son los días; en las demás,
   celdas 0 = hora, 3 = evento, 4 = actual, 5 = consenso, 6 = previo, y las estrellas se
   cuentan con `.grayFullBullishIcon`. Guardá el resultado en `window.__rows`.
3. **Con `timeZone=55` las horas vienen en UTC** (ADP 12:15 = 8:15 ET). ART = UTC−3.
4. La salida se trunca: leé `window.__rows` por tramos (`slice(0,15)`, `slice(15,30)`, …).
5. Plan B, si el servicio deja de responder: botones "This Week"/"Next Week" y filtros de
   la pantalla. En ese caso **anotá los filtros originales antes de tocar nada** (al
   20-sep-2026: *Countries (3)* = EU, GB, US; *Importance* = High) y **restauralos al
   terminar**: es la cuenta del usuario.

### 4b. Cruzar cada evento contra el organismo

| Dato | Fuente primaria | Cómo leerla |
|---|---|---|
| PIB, PCE, comercio exterior, cuenta corriente | BEA `https://www.bea.gov/news/schedule` | `curl` + limpiar HTML. Hora 8:30 ET |
| Ventas minoristas, viviendas nuevas, bienes duraderos, permisos/starts, inventarios | Census `https://www.census.gov/economic-indicators/calendar-listview.html` | `curl`. **El título viene ANTES de su fecha/hora/período** |
| Valores previos de Census | `census.gov/construction/nrs/current/index.html`, `census.gov/manufacturing/m3/adv/current/index.html` | `curl` + texto |
| Sentimiento del consumidor | U. Michigan `https://www.sca.isr.umich.edu/` | Dice "Next data release: …" y el preliminar |
| PMI flash | S&P Global `https://www.pmi.spglobal.com/Public/Release/ReleaseDates` | Horas en **UTC** (13:45 UTC = 10:45 ART) |
| CPI, empleo, PPI, JOLTS | BLS | `curl` da **403**: abrir en Chrome |
| Reclamos por desempleo | DOL | `curl` da 403: buscar la nota del jueves / Chrome |
| FOMC, discursos | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` | `curl` |

- **Conversión horaria:** ART = UTC−3. ET = UTC−4 en verano (hasta el primer domingo de
  noviembre) y UTC−5 en invierno. 8:30 ET (verano) = 9:30 ART.
- **Trampa flash vs. final:** en un dato *final*, el "previo" de Investing puede ser el
  *preliminar*, no el del mes anterior (Michigan) o el flash del mes (PMI de servicios de
  agosto: flash 56,8, final 56,5). Verificá cuál es el que citás.
- **Revisiones:** Investing a veces lista una revisión aparte (ej. "Building Permits" una
  semana después de Housing Starts). Si la fuente primaria no agenda una publicación nueva
  ese día, **no entra**; mencionalo.
- **Qué NO entra por defecto:** discursos de la Fed, subastas del Tesoro, API/EIA de
  petróleo, Baker Hughes, CFTC. Solo si el usuario lo pide. Sí entran las reuniones del
  FOMC, la decisión de tasas, el comunicado con proyecciones y la conferencia de prensa.
- **Fechas fuera de la semana:** si un dato "clásico" no aparece (PIB final, PCE), confirmá
  en BEA/Census que cae otra semana, y decilo (evita que el usuario piense que falta algo).

## Paso 5 — Redactar los eventos

Formato exacto que sirve el worker (`fuente: "Manual"`, sin horarios de evento salvo que
sean centrales, y **solo dos tipos: `ar` y `us`**):

```json
{
  "semana": "21/9 al 25/9 de 2026",
  "generado": "2026-09-20T00:00:00.000Z",
  "fuente": "Manual",
  "dias": [
    { "nombre": "Lunes", "fecha": "21/9", "eventos": [
      { "tipo": "ar", "titulo": "INDEC – …", "descripcion": "…" }
    ]}
  ]
}
```

- `nombre`: Lunes, Martes, Miércoles, Jueves, Viernes. Los días sin eventos van con
  `"eventos": []`.
- **Argentina:** título `"INDEC – <Nombre> (<Mes> 2026)"` o `"BCRA – <Nombre>"`; usar el
  guion largo `–`. Descripción de una oración que explique qué mide.
- **EE.UU.:** título `"<Nombre en castellano> - <Nombre en inglés> (<Mes>)"`, p. ej.
  `Ventas Minoristas - Retail Sales M/M (Agosto)`. La descripción incluye el **dato previo**
  y, si corresponde, el consenso.
- **Los títulos deben contener las palabras que matchean `CAL_SOURCES`** (INDEC, BCRA,
  "Fed", "Michigan", "S&P Global", "Ventas Minoristas", …). El paso 6 lo comprueba.
- Máximo razonable: ~5 eventos por día. Priorizá lo que mueve mercados.
- Usá el **mismo estilo de decimales que la semana en vivo** (leída en el paso 0). Sé
  consistente dentro del JSON: no mezcles coma y punto.
- No pongas nada que no verificaste. No agregues eventos "de relleno".

## Paso 6 — Comprobar que cada evento tenga link a su fuente

El sitio resuelve el link por el título con `CAL_SOURCES` + `calSourceFor()` en
`index.html` (antes de `HTX_CAL_MESES`). Desde el 20-sep-2026 está en `main` y en vivo.
Un evento sin regla queda como texto plano (no se rompe, pero pierde el link).

```
node .claude/skills/calendario-semanal/scripts/check_links.js index.html semana.json
```

Imprime, por evento, el organismo y la URL, y sale con error si alguno no tiene link.

**Si un evento queda sin link (o cae al calendario genérico):**
1. Trabajá en una **rama nueva** (nunca en `main`, ver CLAUDE.md del repo).
2. Agregá una regla en `CAL_SOURCES` **antes** de las genéricas (gana la primera que
   matchea) con la URL más específica que puedas verificar.
3. **Verificá la URL de verdad:**
   - **INDEC: un `200` no prueba nada.** El sitio devuelve el mismo cascarón HTML con 200
     para cualquier URL. Abrí una pestaña en `indec.gob.ar`, cargá la URL en un iframe
     same-origin y leé la miga de pan (`Inicio > …`). Así se detectó que
     `Nivel4-Tema-3-9-47` es "Agregados macroeconómicos (PIB)" y el EMAE es `3-9-48`.
   - **BCRA:** devuelve 404 reales, ahí el 200 sí vale. Confirmá también el `<title>`.
   - **Otros organismos:** `curl` con User-Agent de navegador + revisar el `<title>`. Los
     `403` de `bls.gov` con `curl` no significan que el link esté roto: abrilo en Chrome.
4. Repetí `check_links.js` **con la semana en vivo y la nueva** para no romper nada previo.
5. Commiteá en la rama y avisá; **el merge a `main` solo con confirmación explícita**.

La tabla completa de URLs ya verificadas está en `references/fuentes.md`.

## Paso 7 — Vista previa en un host local

Se hace **una sola vez al final, con los tres JSON** (después de los pasos 8 y 9):

```
python .claude/skills/calendario-semanal/scripts/preview_server.py <raiz-del-repo> semana.json --earnings earnings.json --dividends dividendos.json
```

Sirve el sitio real y, en `/preview.html`, reemplaza las respuestas del worker
(`/calendario`, `/earnings`, `/dividends`) por los JSON de la semana, sin tocar ningún
archivo. Abrí `http://localhost:8899/preview.html#calendario` en Chrome y comprobá con
`javascript_tool`, pestaña por pestaña (`await calSetView('economico'|'earnings'|'dividendos')`):
la semana en `#calSemanaLabel`, la cantidad de eventos y de `<a>` en `#calWeekGrid`, el chip
de fuente en el económico y que earnings/dividendos linkeen a `informes/<ticker>.html`.
Sacá una captura (`save_to_disk`) y **apagá el server** al terminar.

## Paso 8 — Earnings de la semana

Solo empresas **con informe en el sitio**: la lista sale de `informes/*.html` en `main`,
sacando `_preview-gate`, `manifest`, `informe-semanal-*` y `fed-*` (al 28-sep-2026: 43
tickers, incluido `brk.b`).

1. **Rastreo** con el calendario de Nasdaq, un pedido por día (cubre NYSE y Nasdaq):
   `curl -s -A "<UA de navegador>" -H "Accept: application/json" "https://api.nasdaq.com/api/calendar/earnings?date=AAAA-MM-DD"`
   → `data.rows[]` con `symbol`, `time` (`time-pre-market` / `time-after-hours` /
   `time-not-supplied`) y `fiscalQuarterEnding`. Cruzá los `symbol` con la lista
   (en Nasdaq `BRK.B` aparece como `BRK/B`).
2. **Verificación obligatoria** de cada coincidencia en la **fuente primaria**: el
   comunicado de la empresa que anuncia la fecha ("to report … results on …"), en su sitio
   de inversores o en GlobeNewswire/PR Newswire/Business Wire, leído **crudo** (`curl -m 25`
   + limpiar HTML, o `get_page_text`). Nasdaq a veces tiene fechas **estimadas**; si la
   empresa no confirmó, el evento no entra y se avisa. Poné siempre `-m` a los `curl`:
   GlobeNewswire a veces no responde y traba todo.
3. Hora: pasala a ART (MT = UTC−6 en verano, ET = UTC−4 en verano; ART = UTC−3).
   Ej.: Micron "2:30 p.m. Mountain time" = 17:30 ART, después del cierre.
4. Formato de cada evento (el `ticker` en minúscula es el link a `informes/<ticker>.html`):

```json
{ "tipo": "earnings", "titulo": "MU presenta resultados",
  "descripcion": "Micron Technology · 4° trimestre fiscal 2026 (cerrado en agosto). Conferencia a las 17:30 ART, después del cierre del mercado.",
  "ticker": "mu" }
```

## Paso 9 — Dividendos de la semana

Dos tipos de evento, para los mismos tickers: **fecha ex-dividendo** (desde ese día la
acción cotiza sin derecho al pago) y **pago**. Con la liquidación T+1 de EE.UU., la fecha
ex es **el mismo día** que la fecha de registro.

1. **Nasdaq-listed** (AAPL, AVGO, GOOGL, META, MSFT, NVDA, QCOM, TXN, INTU, ASML, MU…):
   `https://api.nasdaq.com/api/quote/<TICKER>/dividends?assetclass=stocks` →
   `data.dividends.rows[]` con `exOrEffDate`, `paymentDate`, `amount`, `declarationDate`.
   Mirá las primeras 3 filas. Espaciá los pedidos (~1,5 s).
2. **NYSE-listed** (JPM, BAC, C, GS, MS, WFC, AXP, V, MA, JNJ, LLY, DIS, ORCL, CRM, SAP,
   TSM…): **ese endpoint devuelve vacío ("N/A") para NYSE**, y el calendario diario
   `api/calendar/dividends?date=` es casi solo de Nasdaq. No sirven: buscá el **último
   anuncio de dividendo** de cada una (comunicado de la empresa o 8-K en EDGAR:
   `https://data.sec.gov/submissions/CIK<10 dígitos>.json`, con un User-Agent que tenga un
   mail, y el `.txt` completo de la presentación para leer los anexos) y leé
   "payable on … to shareholders of record on …".
   Calendarios habituales (orientativos, **confirmar siempre**): GS paga a fin de
   trimestre (29/9/2026); BAC la última semana del mes (25/9/2026); JPM fin de
   ene/abr/jul/oct; ORCL ~día 23 del mes siguiente al anuncio; CRM y TSM ~día 8;
   MA registro ~día 9 de ene/abr/jul/oct; V y WFC pagan el 1 de mar/jun/sep/dic; JNJ ~día
   9 y LLY ~día 10 de mar/jun/sep/dic; AXP registro ~día 10 de ene/abr/jul/oct (anuncia a
   fines del mes anterior); C, MS y DIS se confirman cada vez. Si una empresa **todavía no
   declaró** el próximo dividendo, no puede tener fecha ex esa semana.
3. Cada dato de Nasdaq también se **confirma en la fuente primaria** (8-K o comunicado,
   texto crudo). Las búsquedas web sirven para encontrar el comunicado, nunca como prueba.
4. Formato (mismo estilo que usaba el worker cuando era automático):

```json
{ "tipo": "dividend", "titulo": "GS — pago de dividendo",
  "descripcion": "Goldman Sachs paga su dividendo trimestral de US$5.00 por acción, el primero tras la suba desde US$4.50 (registro: 1/9).",
  "ticker": "gs" }
{ "tipo": "dividend", "titulo": "JPM — fecha ex-dividendo",
  "descripcion": "JPMorgan Chase cotiza sin derecho a su dividendo de US$1.65 (pago: 31/10) a partir de hoy.",
  "ticker": "jpm" }
```

### Armado de earnings.json y dividendos.json

Mismo esqueleto que el económico: `semana` **idéntica** a la del económico,
`fuente: "Manual"`, los mismos 5 días con las mismas fechas y `"eventos": []` en los días
sin nada. Validá los tres juntos:

```
node .claude/skills/calendario-semanal/scripts/validar_semana.js semana.json earnings.json dividendos.json <repo>/informes
```

Sale con error si no parsean, si la semana o las fechas no coinciden, si un tipo es
incorrecto, si falta `fuente: "Manual"`, o si un ticker no tiene `informes/<ticker>.html`.

## Paso 10 — Cargar las tres semanas en el worker (Chrome)

Autorizado por el usuario el 28-sep-2026 ("hacelo por chrome"; "hacemos todo junto").
Procedimiento completo, con las trampas del panel, en `references/worker.md` →
"Cómo cargar una clave desde el panel". En resumen, para `eventos_semana`,
`earnings_semana` y `dividendos_semana`:

1. Copia de lo que hay (paso 0).
2. Panel → Workers KV → `manfredi-calendario-kv` → lápiz de la clave.
3. Reemplazar el textarea por script, verificar clave y semana en una captura, **Save**
   (si la ventana de Chrome se achica sola, ubicá el botón con `find` "Save button").
4. `curl` del endpoint hasta que devuelva la semana nueva y comparar con el JSON local
   (`JSON.stringify` idéntico).
5. Al final, `validar_semana.js` sobre **lo que devuelven los tres endpoints en vivo**, y
   una pasada por manfredinvestment.com (`#calendario`, las tres pestañas).

**Nunca** uses rutas `/…/refresh` (ya no existen) ni despliegues código para cargar una
semana: el código no se toca.

## Paso 11 — Entrega

1. Los **tres JSON** guardados en `C:\Users\Equipo\Documents\semana_<d>_<d>_{calendario,earnings,dividendos}.json`.
2. Una **tabla en texto** día × (Argentina | EE.UU. | Earnings | Dividendos), con el
   organismo o el ticker entre corchetes.
3. Qué **dejaste afuera y por qué** (revisiones, eventos sin fecha primaria, fechas de
   earnings no confirmadas por la empresa, días vacíos).
4. Las **discrepancias** entre fuentes y cómo se resolvieron.
5. Qué está **verificado con fuente primaria** y qué **solo con Investing** (los consensos).
6. Confirmación de que las tres pestañas están **en vivo** e idénticas a lo validado, con
   captura.

## Checklist final (no entregues sin tildar todo)

- [ ] Las 5 fechas y el año son los de la semana pedida.
- [ ] INDEC: leído el PDF renderizado, anotado "Actualizado al …", cruzado con nota de prensa.
- [ ] BCRA: leído el calendario oficial con `get_page_text`.
- [ ] Presupuesto/Congreso: solo si hay fecha en la semana, verificado en varias fuentes; año correcto.
- [ ] EE.UU.: cada fecha cruzada con BEA/Census/UMich/S&P/Fed/DOL/BLS; previos verificados.
- [ ] Investing.com leído por el servicio interno (o filtros **restaurados** si se tocaron).
- [ ] `check_links.js`: 0 eventos sin link, y sin regresión en la semana en vivo.
- [ ] Earnings: los 5 días rastreados en Nasdaq; cada fecha confirmada por la empresa.
- [ ] Dividendos: Nasdaq-listed por historial; **NYSE-listed uno por uno** en su anuncio/8-K.
- [ ] `validar_semana.js` OK con los tres JSON locales.
- [ ] Vista previa de las tres pestañas en Chrome, con captura; server apagado.
- [ ] Copia de lo que había en el KV antes de pisarlo.
- [ ] Las tres claves cargadas; endpoints en vivo idénticos a lo validado; `validar_semana.js` OK sobre lo vivo.
- [ ] Ningún commit ni cambio directo en `main`; sin merge sin confirmación.

## Errores que ya pasaron (no repetir)

- Tomar el "200" del INDEC como prueba de que un link existe → el EMAE apuntaba al PIB.
- Que un PMI de S&P Global linkeara al ISM (son indicadores distintos): regla propia antes.
- Creer que Investing "se olvidó" del PCE o del PIB: caían el 30/9, otra semana.
- Confiar en `pdftotext -layout` del calendario del INDEC: desalinea las columnas.
- Dejar los filtros de Investing.com cambiados en la cuenta del usuario.
- Llamar "2026" al presupuesto que se discute en septiembre de 2026 (es el 2027).
- Dar por buena una URL de Census sin mirar el `<title>`: `construction/c30/index.html`
  era "Page not found"; la buena es `construction/c30/c30index.html`.
- Creer que el endpoint de dividendos de Nasdaq cubre todo: para JPM, V, JNJ… (NYSE)
  devuelve "N/A" aunque paguen dividendo.
- Confiar en que el cron del worker actualizaba earnings/dividendos: estuvo roto semanas
  (llamaba a una función inexistente) y nadie lo notó. Ahora todo es manual y lo carga esta skill.
- Tipear dentro del editor de código del panel de Cloudflare: los clics y atajos terminan
  en la página entera. Ver `references/worker.md`.
