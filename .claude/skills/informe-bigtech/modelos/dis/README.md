# Modelo DIS (The Walt Disney Company) — informe-bigtech

No había modelo en el repo: la edición de sep-2026 (3T FY26, precio $104.16 del 8-sep) se armó a mano en el HTML.

## Archivos
| Archivo | Qué hace |
|---|---|
| `valuacion.py` | (1) Reconstruye el DCF de sep-2026; (2) edición nov-2026 (4T FY26 + año de 53 semanas) → `resultados.json` |
| `actualizar_html.py` | Pasó `informes/dis.html` de la edición de sep a la de nov (se corrió una vez; falla si no encuentra los bloques de sep) |
| `verify.py` | Aritmética del blend leída del HTML, cifras clave vs. `resultados.json`, celda base de la grilla, gate, logo, gris, "hoy/ayer/mañana" → 0 diferencias |
| `comun_2026-11-20.json` | Bloque compartido con WMT: precios del 20-nov, Treasury, S&P, consenso de precio objetivo (misma fuente y día), consumidor de EE.UU. |

## Reconstrucción de septiembre
El HTML declaraba OCF y capex del año 1 y del año 5, WACC, g, deuda neta (40.856), minoritarias (6.810 libro) y 1,727 M de
acciones. Con **interpolación lineal** entre año 1 y año 5, flujos a fin de año, y el interés después de impuestos despejado
(0.7174 mil millones; el texto decía "~0.8") el Base da $102.32 exacto; la grilla 5x5 publicada se reproduce con ±$0.22, el
Bear con −$0.32 y el Bull con −$0.99. Los otros métodos se toman tal como se publicaron (comps $95.36, SOTP $98.01 —se
reproduce en $97.99 con las cifras redondeadas del texto—, reversión ~17x → $108.12, consenso $127.61). Sep promediaba los
cinco en partes iguales ($106.28); con la regla vigente 7.5/7.5/25/35/25 habría dado $108.61.

Errores de la edición de sep corregidos en nov: EPS ajustado del 2T FY26 ($1.86 "por diferencia" → $1.57 del comunicado);
cierre del FY2025 (~$99.50 → $113.47 real); sentido del sesgo por restar minoritarias a valor libro (es al alza, no a la baja);
P/E de FOXA "aproximado" → calculado.

## Próxima actualización (1T FY2027, ~feb-2027)
- Desde el 1T FY27 Disney NO publica la utilidad del streaming y pasa Consumer Products (licencias y editorial) de
  Experiences a Entertainment, sin participación en ganancias en Entertainment. El 8-K 7.01 del 17-nov-2026 trae FY24-FY26
  recalculados: decidir si la suma de partes pasa a la apertura nueva (con los mismos múltiplos baja ~$4/acción: `sotp_recast`).
- DCF: año 1 = FY2028 cuando el FY2027 esté casi cerrado; mismo crecimiento implícito del OCF por escenario salvo que haya razón.
- Reversión: agregar el cierre del 1T FY27 y sacar el más viejo (4 cierres), EPS ajustado de 12 meses; el 4T FY27 compara
  contra la semana 53.
- Consenso: stockanalysis.com (S&P Global), páginas `/forecast/` y `/statistics/` (JSON embebido). Nasdaq/Zacks bloquea.

## Ajustes de revisión (21-nov-2026, a mano sobre el HTML, después de actualizar_html.py)
Orden de la síntesis 1-2-3, "~" fuera de cifras exactas, sin dobles signos, 46% en el pie del gráfico de segmentos, matiz del 1T de Fox, drawLines con pointLabels (valores con halo blanco) en el gráfico de margen, football field angosto.

