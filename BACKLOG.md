# Backlog — Manfredi Investment

Lista viva de pendientes: bugs, mejoras de diseño, decisiones de producto sin resolver y features a futuro. Se actualiza cada vez que aparece algo nuevo mientras se trabaja en otra tarea, no solo se menciona en el chat.

Formato por item: descripción corta · prioridad (alta/media/baja) · estado (pendiente/en progreso/hecho).

---

## Decisiones de producto

| # | Descripción | Prioridad | Estado |
|---|---|---|---|
| 1 | **Login gate**: se sacó el modal de login a pantalla completa. Ahora el login solo se pide de forma contextual al entrar a contenido premium (Inversiones, Warren), vía el gate suave existente (preview parcial + tarjeta de suscripción). Informes y Asesoría pasaron a ser 100% libres (decisión explícita, ya no son premium). Queda un botón discreto "Ingresar" en el navbar. | Alta | Hecho |
| 2 | Manfredi University: decidir si mantiene fondo claro/editorial como excepción intencional al resto del sitio (terminal oscuro) o si se unifica también. No es automático, requiere decisión explícita. | Media | Pendiente |

## Bugs

| # | Descripción | Prioridad | Estado |
|---|---|---|---|
| 3 | Modal de login (`#loginOverlay`) aparecía automáticamente a pantalla completa al hacer scroll como guest. Se eliminó el trigger por scroll y el intercept de clicks en nav — el login ahora es siempre voluntario o contextual a contenido premium. | Media | Hecho |
| 4 | Contenido de curso duplicado: bloques de "Calculá tu presupuesto en dólares CCL..." y cards de ahorro para el retiro aparecen dos veces en `index.html` (líneas ~4527/6838 y ~4616/6927). | Baja | Pendiente |
| 5 | Encoding roto en íconos de `CAL_DETAILS` (calendario económico) | Alta | Hecho |

## Diseño

| # | Descripción | Prioridad | Estado |
|---|---|---|---|
| 6 | Migrar `#mercados` a fondo oscuro, consistente con Informes/Warren/Inversiones. Incluyó reajustar los colores de acento de las dash-cards (MERV, SPX, NDX, BTC, MEP, XAU) que eran ilegibles sobre navy oscuro. | Alta | Hecho |
| 19 | Navegación por pestañas: una sola sección visible a la vez (Inicio/Mercados/Calendario/Informes/University/Inversiones/Asesoría), con hash propio por sección (`#mercados`, etc.), botón atrás y deep-links funcionando. Se encontró y corrigió un bug de integración con AOS (animaciones fade-up) que dejaba el contenido de una pestaña recién activada invisible. | Alta | Hecho |
| 7 | Consolidar tipografía serif: eliminar el único uso de `Playfair Display` (`.mi-ticker`) y reemplazar por `DM Serif Display`; borrar `@import` de `Inter` (no se usa en ningún selector). | Media | Pendiente |
| 8 | Extender `IBM Plex Mono` a todo número en tabla/card del resto del sitio (precios de mercado, KPIs de calendario, precios de picks) — hoy solo vive en el modal de tesis de acciones. | Media | Pendiente |
| 9 | Auditar y reemplazar hex literales sueltos por tokens (`--gold`, `--primary`, etc.), adoptando la escalera de navys del modal `.mi-*` (`#07101E → #0A0F1E → #0a1525 → #0C1828 → #1a2f4a`) como sistema único de elevación. | Media | Pendiente |
| 10 | Sistema de "flash on update" para datos en vivo (precios, KPIs): flash breve de color direccional al cambiar un valor, decae en ~600–900ms, sobre tabular-nums para que no salte el ancho. Gap de mayor impacto/esfuerzo del plan. | Alta | Pendiente |
| 11 | Soporte de `prefers-reduced-motion` — ausente en todo el CSS. | Baja | Pendiente |
| 12 | Letter-spacing progresivo por tamaño de tipografía (hoy ad-hoc, sin regla consistente). | Baja | Pendiente |

## Features futuros

| # | Descripción | Prioridad | Estado |
|---|---|---|---|
| 13 | Dashboard personalizado / watchlist: usuario logueado fija 5-8 activos de las tablas de Mercados, persistidos por usuario, mostrados primero. | Media | Pendiente |
| 14 | Command palette (⌘K) para búsqueda global sobre calendario, tablas, informes, picks y cursos. | Media | Pendiente |
| 15 | Sparklines reales con Chart.js en picks de Inversiones (hoy son `<polyline>` con puntos hardcodeados, no representan datos reales). | Media | Pendiente |
| 16 | Rediseño de jerarquía tipográfica del modal de tesis de acciones (mismo contenido, un número hero por vista). | Media | Pendiente |
| 17 | Sistema de alertas/notificaciones (ej. "avisame si el riesgo país cambia más de X" o antes de un evento del calendario). | Media | Pendiente |
| 18 | Paywall más honesto con preview real: Inversiones ya mostraba el primer pick sin blur + tarjeta de suscripción; ese mismo gate ahora también se aplica a Warren (antes no se activaba para usuarios anónimos que nunca habían intentado loguearse). Informes/Asesoría dejaron de necesitarlo al pasar a ser libres (ver item 1). | Media | Hecho |

---

Detalle y justificación de cada item en `REDESIGN_PLAN.md`. Este archivo es el índice accionable; el plan es el research/racional detrás.
