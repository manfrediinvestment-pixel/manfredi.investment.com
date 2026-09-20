---
name: calendario-semanal
description: "Use when the user asks to build the weekly economic calendar for manfredinvestment.com — 'hacé calendario', 'calendario de la semana', 'armá el calendario económico', 'calendario semana que viene'. Researches and VERIFIES every Argentina event (INDEC release calendar, BCRA reporting calendar, budget/Congress dates) and every US event (Investing.com economic calendar cross-checked against BEA, Census, U. Michigan, S&P Global, BLS/DOL, Fed), then delivers the week as the exact JSON the manfredi-calendario Cloudflare worker serves, with every event checked against the site's source-link table (CAL_SOURCES) and previewed on a local host. The user pastes the result into the worker by hand; this skill never deploys the worker."
metadata:
  version: 1.0.0
---

# Calendario semanal — Manfredi Investment

Cada semana el usuario dice **"hacé calendario"** (o algo equivalente) y vos hacés todo:
buscás los eventos, los **verificás contra la fuente primaria**, los redactás en el estilo
del sitio, comprobás que cada uno tenga link a su fuente y le entregás el JSON listo para
pegar en el worker. No hace falta que te reexplique nada: este documento es el proceso
completo, armado y probado en la semana del 21 al 25 de septiembre de 2026.

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
- Antes de redactar, leé lo que está **en vivo ahora** para copiar el estilo exacto:
  `curl -s https://manfredi-calendario.nachito2502.workers.dev/calendario`.

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

### 4a. Leer Investing.com en Chrome

1. `tabs_context_mcp` → `navigate` a `https://www.investing.com/economic-calendar/`.
   La cuenta del usuario está logueada; la hora se muestra en **GMT-3 (Buenos Aires)**.
2. Botones de rango: **"This Week"** vs **"Next Week"**. Un domingo, "This Week" ya muestra
   lun–dom de la semana siguiente y "Next Week" salta a la de después. **No asumas:
   leé las fechas de la lista y confirmá que son las de tu semana.**
3. **Anotá los filtros originales antes de tocar nada** (al 20-sep-2026 eran
   *Countries (3)* = EU, GB, US, e *Importance* = High). Cambiá a **solo US** e importancia
   **High + Medium** (la semana en vivo siempre incluyó eventos de 2 estrellas como Empire
   State o NAHB). Los cambios de importancia refrescan la lista; releé después.
4. Extraé la lista compacta con `javascript_tool` (una línea por evento: hora, nombre,
   consenso, previo). La salida se trunca: pedí Martes–Miércoles y Jueves–Viernes por
   separado.
5. **Restaurá los filtros originales al terminar** (país por país en el desplegable con el
   buscador; luego desmarcá Medium). Es la cuenta del usuario.

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

```
python .claude/skills/calendario-semanal/scripts/preview_server.py <raiz-del-repo> semana.json
```

Sirve el sitio real y, en `/preview.html`, reemplaza la respuesta del worker por el JSON de
la semana (no toca ningún archivo). Abrí `http://localhost:8899/preview.html#calendario` en
Chrome, bajá hasta la grilla (`scrollIntoView` + `scrollBy` negativo por el header fijo) y
comprobá con `javascript_tool`: cantidad de eventos, cuántos tienen `<a>` y el chip de
fuente de cada uno. Sacá una captura (`save_to_disk`). Al final **apagá el server** (o
dejalo corriendo si el usuario quiere mirarlo, y decíselo).

## Paso 8 — Entrega

1. El **JSON completo** en un bloque de código (el usuario lo copia de acá).
2. Copia en `C:\Users\Equipo\Documents\semana_<d>_<d>_calendario.json` (validá que el JSON
   parsea).
3. Una **tabla en texto** día × (Argentina | EE.UU.) con el organismo entre corchetes.
4. Qué **dejaste afuera y por qué** (revisiones, eventos sin fecha primaria, días vacíos).
5. Las **discrepancias** entre fuentes y cómo se resolvieron.
6. Qué está **verificado con fuente primaria** y qué **solo con Investing** (los consensos).
7. Recordar: el usuario pega el JSON en su **worker de Cloudflare** (`manfredi-calendario`).
   `workers/calendario/index.js` del repo **no es lo que corre en producción**; no lo
   modifiques ni lo despliegues. Si el usuario pega el código real del worker, integrá la
   semana ahí y devolvéselo listo.

## Checklist final (no entregues sin tildar todo)

- [ ] Las 5 fechas y el año son los de la semana pedida.
- [ ] INDEC: leído el PDF renderizado, anotado "Actualizado al …", cruzado con nota de prensa.
- [ ] BCRA: leído el calendario oficial con `get_page_text`.
- [ ] Presupuesto/Congreso: solo si hay fecha en la semana, verificado en varias fuentes; año correcto.
- [ ] EE.UU.: cada fecha cruzada con BEA/Census/UMich/S&P/Fed/DOL/BLS; previos verificados.
- [ ] Filtros de Investing.com **restaurados** a como estaban.
- [ ] `check_links.js`: 0 eventos sin link, y sin regresión en la semana en vivo.
- [ ] Vista previa comprobada en Chrome, con captura; server apagado.
- [ ] JSON válido, copia en Documents, tabla de texto, exclusiones y discrepancias explicadas.
- [ ] Ningún commit ni cambio directo en `main`; sin merge sin confirmación.

## Errores que ya pasaron (no repetir)

- Tomar el "200" del INDEC como prueba de que un link existe → el EMAE apuntaba al PIB.
- Que un PMI de S&P Global linkeara al ISM (son indicadores distintos): regla propia antes.
- Creer que Investing "se olvidó" del PCE o del PIB: caían el 30/9, otra semana.
- Confiar en `pdftotext -layout` del calendario del INDEC: desalinea las columnas.
- Dejar los filtros de Investing.com cambiados en la cuenta del usuario.
- Llamar "2026" al presupuesto que se discute en septiembre de 2026 (es el 2027).
