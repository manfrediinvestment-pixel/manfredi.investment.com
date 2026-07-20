# Plan de rediseño — Manfredi Investment

Documento de investigación y estrategia. **No incluye cambios de código.** Preparado para revisión antes de tocar nada en `index.html`.

---

## 0. Nota importante: brief vs. código real

El brief describía la identidad actual como *Lora/Playfair Display + Poppins*, navy `#060f1e`/`#0A1628`, dorado `#C9A84C`, azul `#4A9EFF`. Audité el repo (`index.html`, `index-v2.html`, y las ramas abiertas `fix/remove-stats-strip-hero`, `feature/diversificar-fuentes-noticias`, `fix/crypto-proxy-and-resilience`) y **ninguno de esos valores exactos aparece en el código**. Tampoco pude resolver `manfredi.investment.com` desde este entorno para chequear el sitio en vivo (DNS no resuelve), así que la fuente de verdad que uso abajo es el repo.

Lo que sí encontré, en `index.html` (el archivo servido desde la raíz):

- **Tipografía real**: `DM Serif Display` (headlines/números hero) + `IBM Plex Sans` (todo lo demás), con `Playfair Display` cargado y usado en algunos bloques puntuales — mezcla de dos serif de display, no una. **Poppins y Lora no están en ningún archivo del repo.**
- **Paleta real**: navy primario `#0A0F1E` (no `#060f1e`/`#0A1628`), dorado `#F2C94C` (no `#C9A84C`), azules `#1a56db` / `#3b82f6` (no `#4A9EFF`). La *dirección* de marca que describís — navy + dorado + azul de apoyo — es correcta; los valores hex concretos no coinciden.

No es un detalle menor: si `manfredi.investment.com` en vivo usa esos otros valores, hay una divergencia entre lo deployado y lo que está en `main` de este repo que vale la pena resolver antes de rediseñar sobre una base equivocada. Te lo marco como primer punto a confirmar con vos, no lo asumo.

Todo lo que sigue está basado en el código real de `main`.

---

## 1. Resumen ejecutivo

El sitio ya tiene una ambición correcta ("Bloomberg meets luxury finance magazine") y varias piezas que ya están a buen nivel: terminal-style chrome (dots rojo/amarillo/verde) en los feeds de informes, sparklines en picks de inversión, indicador "live" con pulse, tesis de acciones con bull/bear/catalysts/peers muy completas, un asistente IA (Warren) con UI de chat propia. **El problema no es que falte ambición de producto — es que la ejecución es inconsistente**, y esa inconsistencia es lo que te separa de Bloomberg/Stripe/Linear más que cualquier elección de fuente.

El hallazgo estructural más importante: **el sitio alterna entre modo claro y modo oscuro sección por sección sin una lógica de producto clara** (hero oscuro → mercados sobre fondo `#F9FAFB` claro → informes oscuro `#07101E` → picks de inversión (tu contenido premium, pago) otra vez sobre fondo claro → widget Warren flotante oscuro). Ningún referente premium hace esto: Bloomberg Terminal, Linear y Coinbase son consistentemente oscuros en su superficie de producto; FT/Economist son consistentemente claros. Manfredi hoy no eligió ninguno de los dos caminos — eso es lo que más "no premium" se siente, no la tipografía.

---

## 2. Auditoría del sitio actual (grounded en el código)

### 2.1 Estructura y funcionalidad existente

- **Ticker bar** superior con scroll infinito (`@keyframes scroll-left`, pausa en hover).
- **Navbar** con dropdowns, login por Google o email/password, área de usuario dinámica (`navUserArea`).
- **Hero** oscuro con mini-cotizaciones (Merval, S&P, BTC, MEP).
- **Mercados**: grid de 6 cards destacadas (Merval, S&P, Nasdaq, BTC, MEP, Oro) + tablas con tabs (ADRs, acciones USA, bonos AR, FX, cripto, commodities, ETFs, índices). Refresco por `setInterval` cada 60–120s por tabla.
- **Calendario económico**: KPIs clickeables (AR: PBI, inflación, desempleo, riesgo país; US: PBI, inflación, desempleo, Treasury 10Y) con panel de detalle, más un calendario semanal traído de un Worker (`manfredi-calendario.nachito2502.workers.dev`).
- **Informes** (`member-protected locked`): dos feeds estilo terminal (Argentina / Wall Street) con chrome tipo macOS, señal de texto, grid de papers PDF.
- **Manfredi University**: quiz de perfil de inversor + 4 cursos gratuitos + 2 "próximamente". Todo gratis, sin gate.
- **Inversiones** (`member-protected locked`): picks de acciones con sparkline SVG inline, sentiment (alcista/neutral), y al hacer click abren un modal con tesis completa — bull/bear cases, catalysts con fecha, comparables (peers) con chart, proyecciones reales vs. estimadas (Chart.js). Esto es contenido genuinamente rico, a nivel de un research note real.
- **Asesoría** (`member-protected locked`): sección de servicios de asesoría.
- **Warren**: FAB flotante (bottom-right), panel de chat centrado en pantalla al abrir, recomendaciones buy/hold/sell con badges de color, tablas markdown-rendered, Chart.js propio.
- **Paywall**: sistema por clase (`member-protected.locked` + overlay `.mi-paywall-overlay`) que se remueve vía JS al autenticar.
- **Calculadoras financieras**: DCA vs. lump-sum (Chart.js), ahorro para el retiro, precio teórico de CEDEAR.

### 2.2 Lo que ya está bien (preservar y llevar al resto del sitio)

- Chrome de terminal macOS-style en los feeds de informes — es un detalle genuinamente premium, subutilizado (solo vive ahí).
- `font-variant-numeric: tabular-nums` ya se usa en las tablas de mercado — bien, pero solo en 15 lugares del archivo; no es sistemático.
- Indicador "live" con pulse animation y badge stale — el patrón correcto, pero no está en todos los bloques de datos en vivo.
- Modal de tesis de acciones (bull/bear/catalysts/peers/proyecciones) — es más rico que lo que la mayoría de fintech retail muestra gratis. Es un activo, no hay que rediseñarlo desde cero, hay que vestirlo mejor.
- Hover states y transiciones ya definidas en tokens (`--transition: .2s cubic-bezier(.4,0,.2,1)`) — el sistema existe, falta aplicarlo consistentemente.

### 2.3 Problemas técnicos concretos (no cosméticos)

- **Encoding roto**: los íconos de `CAL_DETAILS` (detalle del calendario económico) están en mojibake (`ð`, `ð¥`, `ð·`...) — emojis UTF-8 mal guardados. Se ve roto en producción ahora mismo.
- **Cero animación de "flash" al actualizar un precio.** Ningún `classList.add` de flash/highlight en todo el archivo. Los precios que refrescan cada 60–120s simplemente cambian el texto sin transición — la app nunca se *siente* viva, aunque los datos sí lo estén.
- **Cero soporte de `prefers-reduced-motion`** en ningún lado del CSS.
- **Cero personalización**: no hay watchlist, no hay "mi cartera", no hay memoria de qué tabs/filtros usó el usuario la última vez.
- **Cero command palette / búsqueda global** — con calendario + 8 tablas de mercado + informes + picks + cursos, un usuario recurrente no tiene forma rápida de ir a lo que busca.
- **Contenido duplicado**: el bloque de pasos "Calculá tu presupuesto en dólares CCL..." y las cards de ahorro para el retiro aparecen literalmente dos veces en el archivo (líneas ~4527/6838 y ~4616/6927) — probablemente contenido de curso repetido entre dos vistas que se copiaron en vez de compartir un template.
- **`index.html` vs `index-v2.html`**: hay dos archivos de casi 11k/9k líneas con contenido y estilos parcialmente distintos y sin que quede claro cuál es la fuente de verdad servida. Esto es deuda técnica que conviene resolver antes de invertir en un rediseño — sin eso, cualquier cambio corre el riesgo de aplicarse al archivo que no se sirve.
- **10.300 líneas en un solo `index.html`** con CSS y JS inline: no es un problema de diseño, pero sí un techo real para la velocidad con la que se puede iterar el rediseño con calidad.

---

## 3. Qué aprendimos de los referentes

Investigación completa con fuentes en `design-research.md` (research agent — WebSearch/WebFetch sobre Bloomberg Terminal/Bloomberg.com, Robinhood, Stripe, FT/The Economist, Linear.app, Coinbase). Los 8 patrones que se repiten en 3+ de las 6 referencias, de mayor a menor transferibilidad a Manfredi:

1. **Numerales tabulares, tratados como dato serio.** Bloomberg encargó glifos de fracciones custom a Matthew Carter; Coinbase shipea una familia Mono dedicada; Stripe afina su escala tipográfica específicamente para cifras densas. Cualquier número que actualiza en vivo o vive en una columna necesita tabular figures reales — es piso, no diferenciador.
2. **El color como señal escasa y semántica, nunca decoración.** El rojo del Economist toca texto/bordes, nunca un fill; el acento de Linear es "una linterna, no una lámpara"; Stripe reserva el color saturado para un solo momento hero. Un dorado usado en todos lados deja de leerse lujoso y empieza a leerse recargado — esto aplica directo a Manfredi, que hoy usa `#F2C94C` en botones, bordes, texto, badges y el propio Warren simultáneamente.
3. **Serif para autoridad + sans para datos** — exactamente la dirección que Manfredi ya eligió (FT con Financier, Robinhood con Martina Plantijn + Robinhood Phonic). No hay que cambiar de estrategia tipográfica, hay que ejecutarla con más disciplina (ver §4).
4. **Arquitectura de color por tokens semánticos**, no hex sueltos. Linear deriva un tema entero de 3 inputs en espacio LCH; Coinbase (CDS) usa tokens semánticos (`bgPrimary`, `fgMuted`) que se adaptan solos entre claro/oscuro. Manfredi tiene *algunos* tokens (`--primary`, `--gold`) pero el archivo también tiene decenas de hex literales sueltos (`#F2C94C`, `#0A0F1E`, `#10B981`... repetidos a mano en vez de referenciar la variable).
5. **Elevación por aclarado de superficie, no por sombra**, en fondos oscuros — las sombras casi no se ven sobre navy casi negro. Linear usa bordes de 0.5px en vez de `box-shadow`. Directamente aplicable a las secciones oscuras de Manfredi (informes, Warren).
6. **La "vida" de los datos en vivo es una capa de producto diseñada, no un efecto secundario.** El gradient WebGL de Stripe, el UI optimista de Linear, el flash-on-update de Robinhood son sistemas construidos a propósito. Manfredi tiene datos reales actualizando cada minuto y ningún feedback visual de que eso está pasando — es la brecha de mayor costo/beneficio de todo este documento.
7. **Personalización y hábito superan al pulido visual puro para retención.** El paywall personalizado con IA de FT (+280% conversión reportado), el ritual diario de Espresso (The Economist), las alertas de precio de Robinhood — todos mueven la aguja más que cualquier refinamiento visual. Manfredi ya tiene la materia prima (calendario, mercados, picks) para esto y hoy no la usa.
8. **Restricción y consistencia aplicadas sin excepción es lo que de verdad significa "caro."** Ya sea el minimalismo editorial del Economist o el micro-ajuste acumulativo de Linear, el patrón común es un vocabulario chico (tamaños, espaciados, colores, duraciones) aplicado sin excepciones — no más elementos, más color o más animación. Es la lección más transferible de las seis.

---

## 4. Gaps concretos: estructurales vs. cosméticos

### 4.1 Estructurales (afectan jerarquía, arquitectura de producto o funcionalidad — resolver primero)

| Gap | Evidencia en el código | Por qué importa |
|---|---|---|
| Inconsistencia claro/oscuro sección por sección | `.section-alt { background: var(--bg-alt) }` (`#F9FAFB`) aplicado tanto a Mercados como a **Inversiones** (tu contenido pago), mientras Informes usa `#07101E` y Warren es oscuro | Ningún referente premium mezcla así; rompe la sensación de "un solo producto" |
| Cero feedback visual de "dato recién actualizado" | 0 ocurrencias de flash/highlight en todo el CSS/JS pese a 6 `setInterval` activos | Es la brecha de mayor impacto/esfuerzo de todo el plan — ver §6 |
| Cero personalización (watchlist, cartera, preferencias) | 0 resultados para "watchlist", "favorito", "mi cartera" | Es lo que más mueve retención según los 6 referentes, más que la estética |
| Sin command palette / búsqueda | 0 resultados para búsqueda global, ⌘K | Con 8+ tablas, calendario, cursos e informes, un usuario recurrente no tiene atajo |
| Tokens de color inconsistentes | `--gold: #F2C94C` definido, pero decenas de hex literales repetidos sueltos en el mismo archivo | Bloquea theming consistente y hace el rediseño más caro de lo necesario |
| Dos archivos HTML de ~10k/9k líneas sin fuente de verdad clara | `index.html` vs `index-v2.html` | Riesgo de que el rediseño se aplique al archivo que no se sirve |
| Contenido de curso duplicado | bloques idénticos en dos ubicaciones del archivo | Mantenimiento: un fix hay que aplicarlo dos veces o se desincroniza |

### 4.2 Cosméticos (refinar, no rehacer — segunda prioridad)

- Mezcla de dos fuentes serif de display (`DM Serif Display` + `Playfair Display`) sin lógica aparente de cuándo usar cada una.
- Tracking/letter-spacing no sigue una regla consistente por tamaño (Stripe: tracking se ajusta progresivamente con el tamaño; acá es más ad-hoc).
- Encoding roto en íconos del calendario (bug puntual, no rediseño, pero rompe la percepción de calidad).
- Elevación de cards vía `border` genérico en vez de un sistema de 2-3 niveles.
- `prefers-reduced-motion` ausente.

---

## 5. Propuestas de componentes

Cada propuesta está atada a un gap del §4, no es agregar por agregar.

### 5.1 Sistema de "dato en vivo" (resuelve el gap #1 de mayor impacto)
Un único componente reutilizable para todo valor que actualiza (precios, KPIs de calendario, cards de picks): al cambiar el valor, el número hace un flash breve del color de dirección (`+`/verde o `-`/rojo) durante ~150ms y decae a su color base en ~600–900ms; el dígito nunca "salta" de ancho porque todo corre sobre tabular-nums. Se engancha directo en las funciones `fetch*` existentes (`fetchAllAssets`, `fetchCryptoTable`, etc.) — no requiere rehacer el fetching, solo envolver el `textContent =` actual.

### 5.2 Dashboard personalizado / watchlist
Un tab "Mi Watchlist" dentro de Mercados: el usuario logueado puede fijar 5-8 activos de las tablas existentes (ícono de estrella en cada fila, ya hay filas con hover) que se guardan por usuario y se muestran primero, con el mismo `dash-card` que ya existe para Merval/SPX/BTC. Reutiliza componentes existentes, no inventa un patrón nuevo — el trabajo es de persistencia (asociar al login existente) y de un filtro de orden, no de UI desde cero.

### 5.3 Gráficos interactivos reales en vez de sparklines estáticos
Los picks de inversión (`.pick-card`) usan un SVG `<polyline>` con puntos hardcodeados. Con Chart.js ya cargado en la página para otros usos, un sparkline real conectado a datos históricos (mismo endpoint que ya alimenta las tablas) permite hover-to-see-value y es trivialmente más creíble que una polyline fija — hoy el gráfico no representa datos reales, es decorativo.

### 5.4 Modal de tesis de acciones: mismo contenido, mejor jerarquía
El modal ya tiene todo el contenido correcto (bull/bear, catalysts, peers, proyecciones). Rediseñar solo la jerarquía tipográfica dentro del modal: un número hero (precio objetivo / upside), el resto en la jerarquía secundaria/terciaria que define §2 de la skill de diseño — sin agregar ni quitar información, solo aplicando el principio de "un número hero por vista."

### 5.5 Command palette (⌘K)
Dado el volumen de contenido (calendario, 8 tablas, informes, picks, 6 cursos), un buscador global tipo Linear que salte directo a "AAPL", "inflación", "curso de análisis fundamental", etc. Alto impacto para usuarios recurrentes/pagos, esfuerzo moderado porque no requiere backend nuevo — indexa lo que ya está en el DOM/en los objetos JS de datos (`CAL_DETAILS`, los objetos de picks, etc.).

### 5.6 Alertas / notificaciones (retención)
Sobre el calendario económico y las tablas de mercado ya existentes: permitir que un usuario logueado marque "avisame si el riesgo país cambia más de X" o "avisame antes de un evento del calendario semanal." No es un feature visual — es el tipo de mecánica que, según la investigación (§3, punto 7), mueve retención más que cualquier rediseño visual.

### 5.7 Superficie de paywall más honesta
Hoy `member-protected.locked` aplica un overlay genérico sobre Informes/Inversiones/Asesoría. Un patrón tipo FT/Robinhood Gold: mostrar contenido real parcialmente (ej. el pick de AAPL completo, gratis, como "muestra"; el resto con blur + overlay explicando qué desbloquea el pago) en vez de bloquear todo por igual — vende el producto en vez de solo anunciar que existe.

### 5.8 Unificación de superficie oscura
Llevar Mercados, Calendario e Inversiones al mismo sistema de fondo oscuro que ya usan Informes y Warren (con la disciplina de elevación por aclarado, no sombra, del §3.5), dejando el modo claro solo para las páginas 100% editoriales (University, sobre nosotros) si es que se decide mantener algo de contraste editorial estilo FT. Esta es la decisión de mayor impacto visual de todo el documento y es la que más se beneficia de tu confirmación antes de ejecutar (ver Pregunta abierta en §7).

---

## 6. Priorización

### Impacto alto / esfuerzo bajo-medio (hacer primero)
1. Fix del encoding roto en `CAL_DETAILS` (bug, no diseño — 15 minutos, visible ahora mismo en producción)
2. Sistema de "flash on update" (§5.1) — el gap de mayor impacto/esfuerzo de todo el plan
3. Auditoría y reemplazo de hex literales por tokens (`--gold`, `--primary`, etc.) — desbloquea todo lo demás y reduce el costo de los próximos cambios
4. Resolver `index.html` vs `index-v2.html` (decidir fuente de verdad) — bloquea que cualquier trabajo posterior se pierda

### Impacto alto / esfuerzo medio-alto (siguiente tramo)
5. Unificación light/dark por sección (§5.8) — la decisión estructural más grande, requiere tu confirmación primero
6. Watchlist/personalización (§5.2)
7. Command palette (§5.5)
8. Paywall más honesto con preview real (§5.7)

### Impacto medio (después)
9. Sparklines reales con Chart.js en picks (§5.3)
10. Rediseño de jerarquía del modal de tesis (§5.4)
11. Sistema de alertas/notificaciones (§5.6)

### Impacto bajo / cosmético (último, y solo si hay margen)
12. Consolidar a una sola fuente serif de display
13. Afinar letter-spacing progresivo por tamaño (regla Stripe)
14. `prefers-reduced-motion`
15. Deduplicar contenido de cursos repetido

---

## 7. Identidad de marca: qué mantener

Mantener sin discusión: navy oscuro (no negro puro — ya es la elección correcta según §3), dorado como acento, serif de display + sans de cuerpo, el "carácter" editorial-financiero del copy. Nada de esto se toca.

Lo que sí conviene decidir con vos antes de ejecutar el §5.8:

**Pregunta abierta**: ¿el objetivo es que Manfredi se sienta como una *terminal* (oscuro consistente en toda la superficie de producto, como Bloomberg Terminal/Linear/Coinbase) o como una *revista financiera* (claro consistente con acentos oscuros, como FT/Economist)? Hoy el sitio no eligió ninguno de los dos — tiene ambos mezclados. Es la decisión de mayor impacto visual de todo este plan y la única que cambia sustancialmente cómo se ve el sitio, así que prefiero que la definas antes de que arme el plan de implementación.

---

## 8. Próximos pasos

Este documento vive en la rama `research/premium-redesign-plan` (no en `main`), junto con la skill `web-design-expert` (`.claude/skills/web-design-expert/`) que usé para armarlo y que va a guiar la ejecución. No se tocó ningún archivo de producto.

Cuando lo revisemos: confirmamos (a) si hay que reconciliar esto contra el sitio deployado en vivo dado que no pude verificarlo desde acá, (b) la pregunta abierta del §7, y (c) el orden de §6 — y recién ahí paso a plan de implementación y código, en una rama nueva por feature, como marca `CLAUDE.md`.
