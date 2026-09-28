# Worker `manfredi-calendario` (Cloudflare)

Estado al **28-sep-2026**, versión activa `0874bda9` (desplegada desde el panel). La
anterior, `60a8abc3`, queda en el historial de versiones por si hubiera que volver atrás.
`workers/calendario/index.js` del repo **no** es lo que corre en producción.

## Todo es manual

Desde `0874bda9` el worker **no genera nada solo**. Sirve lo que haya en el KV y nada más.

| Ruta | Qué devuelve |
|---|---|
| `/calendario` | KV `eventos_semana`. Si está vacío, lo genera (INDEC + ForexFactory) — no dejarlo vacío |
| `/earnings` | KV `earnings_semana`; si está vacío → `404 {"error":"sin datos cargados"}` |
| `/dividends` | KV `dividendos_semana`; si está vacío → `404 {"error":"sin datos cargados"}` |
| `/macro-us` | KV `macro_us` (FRED, caché 24 h) — automático, no tocar |
| `/commodities` | KV `commodities` (caché 6 h) — automático, no tocar |
| `/debug-ff`, `/debug-indec`, `/debug-tickers` | diagnóstico, solo lectura |

El sitio (`calFetchView` en `index.html`) muestra "Sin datos disponibles" cuando la
respuesta no trae `dias`, así que un 404 se ve prolijo.

**Se eliminaron** (28-sep-2026): `/calendario/refresh`, `/earnings/refresh`,
`/dividends/refresh` (regeneraban automático y pisaban la carga manual) y `/debug-av`
(devolvía la respuesta cruda de Alpha Vantage, **que incluía la API key**). No volver a
agregarlos.

## Cron

`0 9 * * MON` (lunes 06:00 ART) → `generarYGuardar` (no toca `eventos_semana` si tiene
`"fuente": "Manual"`) + `fetchYGuardarCommodities`. Historial de corridas (solo última
semana): panel → Workers → manfredi-calendario → Settings → Cron triggers → link de la
próxima fecha (`/workers/services/cron-events/manfredi-calendario/production`).

Hasta el 28-sep-2026 el cron llamaba además a `fetchYGuardarFRED`, **función que no
existía**: tiraba ReferenceError al instante (Error, 0.6 ms de CPU) y nunca llegaba a
earnings ni dividendos. Por eso esas pestañas quedaron congeladas.

## KV

Namespace `manfredi-calendario-kv` (id `6d2171ac1fe748f5b30847dd21ffd455`), binding
`CALENDARIO_KV`. Claves: `eventos_semana`, `earnings_semana`, `dividendos_semana`,
`macro_us`, `commodities`, `tickers_trackeados`.

## Cómo cargar una clave desde el panel (Chrome)

1. `https://dash.cloudflare.com/aa3c7a3bcab4ea4d9262c585793de9ac/workers/kv/namespaces/6d2171ac1fe748f5b30847dd21ffd455`
   (la cuenta del usuario ya está logueada en su Chrome; nunca escribas credenciales).
2. **Antes de pisar, guardá lo que hay**: `curl -s <worker>/<endpoint>` a un archivo del
   scratchpad. Es la copia para volver atrás.
3. El lápiz de la fila aparece gris hasta que el valor termina de cargar: abrí el menú `⋯`
   de la fila (eso fuerza la carga), `Escape`, y recién ahí clic en el lápiz.
4. En el diálogo **Edit**, reemplazá el `<textarea>` que contiene `"semana"` con
   `javascript_tool`: setter nativo (`Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set`)
   + eventos `input` y `change`. Verificá en el mismo script que `ta.value === texto` y que
   `JSON.parse(ta.value)` da la semana y la cantidad de eventos esperadas.
5. Captura para mirar que diga la clave y la semana correctas → **Save**.
6. Comprobá con `curl` que el endpoint devuelva **exactamente** el JSON validado
   (`JSON.stringify(vivo) === JSON.stringify(local)`); KV puede tardar hasta ~60 s.
7. Una clave cargada desde el panel **no vence** (no lleva `expirationTtl`).

## Si hay que tocar el código

El editor web del panel (VS Code dentro de un iframe de otro dominio) **no es confiable
con el teclado**: varias veces un clic o `Ctrl+F` terminó seleccionando toda la página en
vez del editor. Método que funcionó el 28-sep-2026, sin tipear código:

1. Clic dentro del código y confirmar el foco en la barra de estado (`Ln X, Col Y`).
2. `Ctrl+A`, `Ctrl+C` → leer con PowerShell `Get-Clipboard -Raw` y guardarlo (copia para
   volver atrás).
3. Editar el archivo localmente con reemplazos exactos (cada uno debe encajar una sola
   vez), `node --check`, y probarlo con un KV simulado (importarlo como `.mjs`).
4. `Set-Clipboard` con el archivo nuevo → clic en el código → `Ctrl+A`, `Ctrl+V`.
5. Poner un centinela en el portapapeles, volver a copiar desde el editor y comparar con el
   archivo local: tienen que ser idénticos antes de desplegar.
6. `Deploy` (si la ventana quedó angosta, ubicarlo con `find` "Deploy button").
7. Verificar en vivo cada ruta y, en Deployments, la versión activa al 100%.

Para leer el código sin editarlo: panel de búsqueda lateral (lupa) y clic en los
resultados; no tipear dentro del editor.
