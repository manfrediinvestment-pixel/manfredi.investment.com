# Fuentes de contenido dentro del sitio

Todo lo que el sitio ya produce es materia prima. Priorizá lo que no exige
investigación nueva.

| Fuente | Dónde | Qué sale | Skill que lo produce |
|--------|-------|----------|----------------------|
| Informes de tickers | `informes/<ticker>.html` (listá con `ls informes`) | Estructura A (ticker) y D (comparativo) | `reel-informe`, `informe-bigtech` / `informe-bancos` si falta el informe |
| Informes semanales / Fed | `informes/informe-semanal-*.html`, `informes/fed-*.html` | Estructura C, resumen semanal | `hyperframes` |
| Calendario | Pestaña Calendario del sitio; worker `manfredi-calendario` (tickers del sitio + macro AR del INDEC) | Estructura C: balances de tickers cubiertos, IPC/EMAE/INDEC, FOMC | `motion-graphics` |
| Cursos (University) | `index.html`: Introducción a la Bolsa, Finanzas Personales Básicas, El Mercado Argentino, Análisis Fundamental | Estructura B (explicadores), carruseles | `motion-graphics`, `marketing-images` |
| Portafolio de Manfredi | Sección Portfolio (operaciones con fecha, p. ej. GGAL, IBIT) | "Qué compré y por qué", seguimiento | cámara + `hyperframes` |
| Tu Portafolio / Finanzas Personales | Features del sitio (importar PDF del broker, mapa de calor, rendimiento vs. S&P 500) | Estructura E (producto) | `product-launch-video`, `marketing-images` |
| Warren IA | Chat del sitio | Estructura E | ver `marketing/reel-warren-ia/` |
| Pedir informe | "Vos elegís la acción. Nosotros hacemos el informe." | Estructura E + CTA de comentarios | cámara |
| Mercados | Logos + market cap, pulso del mercado | Datos para ganchos de número | — |

## Oferta (para las CTA)

- Membresía: **USD 15/mes**. Incluye todos los informes, Warren IA y el análisis de portafolio.
- El informe de **Microsoft (`informes/msft.html`) es gratis y completo**: es la prueba gratuita.
- Los no-socios ven una vista previa de cada informe.
- Verificá precios y ofertas en `index.html` antes de usarlos: pueden cambiar.

## Producción ya hecha (no repetir, reutilizar)

- Reels de informes: NVDA, AAPL, DIS, MA vs V (ver `marketing/` y las memorias del proyecto).
- `marketing/`: reel del portfolio (versiones a-d y final), reel de Warren IA, noticiero inversor IA, stories de informes y de portfolio, portada, miniatura, overlays de gancho y cierre, outro de marca.
- `videos/`: tour del sitio, promo de informes + membresía, overlay de Apple.
- Los overlays `overlay-hook` y `overlay-closing` y el `outro-manfredi-brand` se reutilizan en cualquier reel nuevo.
