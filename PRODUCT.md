# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Principal:** inversor minorista argentino de 22 a 45 años que ya invierte (CEDEARs, acciones, bonos) en uno o dos brokers (IOL, Balanz, Cocos, PPI, Bull Market) y mira el mercado casi todos los días.
- **Secundario (el público actual de las redes del fundador):** gente interesada en la economía argentina (inflación, dólar, plazo fijo) que todavía no invierte o invierte poco. 84% tiene entre 18 y 34 años, 90% es de Argentina y entra casi siempre desde el celular.

## Product Purpose
Juntar en un solo lugar lo que el inversor argentino hoy busca en diez páginas distintas: noticias y reportes, cotizaciones de Argentina y el mundo, calendario económico, informes de empresas y su propia cartera. El éxito es que Manfredi sea la página que se abre todas las mañanas.

## Positioning
La cartera del usuario, cargada desde cualquier broker argentino (a mano o importando el PDF), puesta al lado del mercado y medida de verdad: rendimiento real (Dietz modificado) contra el S&P 500. Todo en español y con contexto argentino (CEDEARs, dólar CCL/MEP, INDEC). Los sitios argentinos tienen cotizaciones y noticias pero no tu cartera; los trackers extranjeros no entienden CEDEARs ni brokers locales.

## Operating Context
- Rutina de la mañana: reporte → cotizaciones → calendario del día → cómo abrió la cartera.
- Tráfico principal desde Instagram y TikTok del fundador, en el celular.
- Sitio estático en Cloudflare Pages + workers (mercados, noticias, calendario, memberships, warren, log-user, admin).

## Capabilities and Constraints
- **Gratis:** Mercados (cotizaciones), Noticias / reportes diarios, Calendario económico (eventos, earnings, dividendos), University (cursos), Finanzas personales, Portfolio (cargar cartera a mano o por PDF, rendimiento vs. mercado, mapa, rendimientos, perfil, Cartera Manfredi).
- **Membresía USD 15/mes:** ratios de riesgo del portafolio, informes institucionales completos con fair value (más de 40), Warren IA (asistente que conoce tu cartera).
- No hay fondos comunes de inversión (FCI) en las cotizaciones todavía.
- No es asesoramiento: la herramienta es de autogestión. Evitar "qué comprar" y promesas de rendimiento.

## Brand Commitments
- Nombre: Manfredi Investment. Emblema: M sobre card dorada.
- Voz: directa, cercana, argentina (voseo), con fundamento serio. Mostrar antes que explicar, números concretos, frases cortas.

## Evidence on Hand
- Más de 40 informes publicados en `informes/`.
- Datos reales en vivo desde los workers de mercados, noticias y calendario.
- Cartera Manfredi con rendimiento real desde el 22-may-2026.
- No hay testimonios ni métricas de usuarios publicables: no inventarlos.

## Product Principles
1. Todo en un lugar: cada pieza nueva tiene que reforzar que esta es la única pestaña que hace falta.
2. Lo principal es gratis; la membresía profundiza.
3. Datos reales antes que maquetas.
4. Celular primero: el público llega desde redes.
5. Honestidad: nunca prometer rendimientos ni recomendar activos.
