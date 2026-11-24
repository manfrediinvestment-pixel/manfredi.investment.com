# Modelo PFE (Pfizer Inc.) — informe-salud, Módulo A (pharma), informe inicial con datos al 3T 2026

Todo número derivado de `informes/pfe.html` sale de `model.py`. El HTML se arma con el sistema de tokens `{{clave|formato}}`
de LLY/JNJ; `verify.py` compara el HTML contra el modelo y tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `sotp.py` | Motor del Método 1: suma de partes por producto (tramos EE.UU. / fuera de EE.UU.) hasta la LOE, erosión integrada por trimestre, rNPV del pipeline con regalías, I+D como línea corporativa, plataforma post-2040, CVR de Metsera |
| `model.py` | Datos del 3T26, revenue gap, los cuatro métodos, blend, transparencia (independientes / anclados), referencias, anti-circularidad, dict `cmp` → `model.json` |
| `cmp_table.py` | Cuadro "PFE vs. ABBV vs. LLY vs. JNJ" (mismo cuadro que el informe de ABBV). ABBV se lee de `../abbv/model.json` o, si no existe, del worktree hermano `manfredi-abbv`; si no está en ninguno, la columna se omite |
| `pfe.head.html` / `pfe.body.tpl.html` / `engine.js` / `charts_pfe.js` | Cabecera+CSS (la de LLY, `.verdict-note` en var(--muted)), texto con tokens, motor de gráficos de LLY/JNJ, datos de los gráficos |
| `build.py` | Inserta el cuadro comparativo en `@@CMP_TABLE@@`, aplica los parches de celular de LLY (`drawHBars`/`drawRangeBars` con margen limitado y etiquetas en dos líneas, leyenda de `drawLines` en varias filas) y renderiza `informes/pfe.html` |
| `render.py` / `verify.py` | Tokens → HTML; HTML ↔ modelo, aritmética del blend, celda Base, suma de partes, M2 = mediana, anti-circularidad, deuda, cuadro comparativo, gate, logo, gris, lenguaje relativo, 14 secciones, cada `<canvas>` con datos y `node --check` del JS |
| `index_add.py` | Reemplaza la tarjeta "Próximamente" de PFE del panel Defensivos de `index.html` por la tarjeta activa (acento `card_accent` del modelo, sparkline de 7 cierres mensuales, botón con `miGateAnalysis`). **No toca el contador "N de 10"**. Conserva CRLF |
| `manifest_add.py` | Entrada `pfe-2026-11-23` arriba de `informes/manifest.json` (conserva CRLF) |
| `fetch_data.py`, `raw/sec.py`, `raw/fetch_rel.py`, `raw/parse_prod.py`, `raw/orange_book.py` | Yahoo (serie mensual de 25 años), EDGAR (User-Agent genérico), comunicados históricos, tablas de ventas por producto → `raw/prod.json`, Orange Book → `raw/ob_pfe.json` |

Datos de mercado, consenso, tasa común, pares, tasas BIO, IRA y LLY/JNJ: `.claude/skills/_compartido/defensivos_nov26.json` (no se vuelven a buscar).

## Decisiones de esta edición
- **M1**: WACC común de pharma (7.114%, ±75 pb). Fechas de LOE: acuerdos de litigio (Eliquis 1-abr-2028, Vyndamax 1-jun-2031), Orange Book (Ibrance mar-2027, Xtandi ago-2027, Xeljanz jun-2026) y 10-K. Curvas: Lipitor/Lyrica (EE.UU.), Lipitor internacional, Humira (biológicos). Margen de contribución anclado en el TTM (OCF + I+D después de impuestos). Activo #1 de la grilla = el de mayor rNPV que no sea un grupo (tilrekimig).
- **M2** (decisión del coordinador, igual en ABBV): la regresión P/E vs. crecimiento no se sostiene (R² 0.41 con 11 pares, 0.19 sin LLY) → **mediana** de los 13 pares (15.766x) × EPS 2027 de consenso, descontado un año al Ke común. Referencias fuera del blend: cuartil superior ($54.84) y pares en precipicio BMY/SNY/GSK/NVO (10.07x → $27.69).
- **M3**: ocho cierres trimestrales 4T24–3T26 sobre EPS ajustado TTM tal como lo reporta Pfizer (IPR&D adentro). Se muestran sin el ajuste (2015-2025 con COVID, 2015-2019) y la ventana del precipicio de Lipitor (2011-2013). Precios previos a nov-2020 × 1.054 (escisión de Upjohn tratada por Yahoo como split).
- **M4**: `pt_prom` del JSON ($30.22).
- **Postura**: sale del número (|brecha| < 5% → neutral; 5-15% → neutral con sesgo; > 15% → fuera de neutral). `card_accent` en el modelo.

## Pendiente / no verificado
- La presentación de pipeline del 3-nov-2026 no se pudo bajar (pfizer.com 403): se usó la del 4-ago-2026 + comunicado y 10-Q.
- Picos de venta del pipeline: supuestos propios salvo Metsera (Leerink, >$5B combinado, pre-compra).
- Arancel 232 en cero por el acuerdo MFN: no verificado contra el anexo oficial.
- Erosión de Humira: prensa (AbbVie), no EDGAR.

## Integración (rama de defensivos) y rebuild
Desde la raíz del repo, con el `model.json` de ABBV presente en `.claude/skills/informe-salud/modelos/abbv/`:
```
cd .claude/skills/informe-salud/modelos/pfe && python model.py && python build.py && python verify.py && python index_add.py && python manifest_add.py
cd ../../../../.. && node scripts/catalogo-informes.mjs
```
`verify.py` tiene que terminar con `diferencias: 0` y `cuadro comparativo con ABBV: True`. Si ABBV cambia su `model.json`, basta
con `python build.py && python verify.py` (el cuadro se regenera). El contador "7 de 10" del panel Defensivos lo ajusta la integración.
`informes/catalogo.json` lo regenera `scripts/catalogo-informes.mjs`.

## Actualizar el próximo trimestre
1. `python fetch_data.py`; `cd raw && python sec.py && python sec.py <acc> <doc>` para el 8-K y el 10-Q nuevos; `python parse_prod.py`;
   Orange Book nuevo → `python orange_book.py <carpeta>`.
2. En `model.py`: nombres de archivo del comunicado nuevo, cifras del trimestre, guía, balance, flujo (FY/9M), EPS trimestral, fila nueva de
   la reversión, research común nuevo.
3. `python model.py && python build.py && python verify.py` → 0 diferencias.
