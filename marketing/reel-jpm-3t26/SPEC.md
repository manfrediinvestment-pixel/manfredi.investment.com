# Reel JPM 3T26 — "Ganó 15.300 millones y la acción cerró en rojo"

Skill: reel-noticia, modo nube (sección 8b). Fuente principal: `informes/jpm.html` (datos al 3T26, commit a05f1f8).
Palabra para comentar: **JPMORGAN** → `guia-jpm.html`.

## Metáfora: campo y cosecha
Elegida sobre "edificio de alquiler" porque cubre los tres datos centrales del trimestre en una sola imagen:
- **Lluvia** = suba de tasas de la Fed → **cosecha** = ingreso neto por intereses +13% (US$ 27.036 M).
- **Comprarle la parte a los socios** = recomprar acciones, pero el campo "cotiza tres veces lo que dicen los papeles" (P/TBV 3,02x) → recompras −84%.
- **Sembrar más** = prestar más (préstamos +10%), lo que Dimon dijo preferir.
- **Llenar el silo** = aumento de reservas US$ 539 M "no porque venga sequía, porque sembró más" (castigos −15%).

## Escenas (build_index.py)
| # | id | entra (s) | fondo | qué pasa |
|---|---|---|---|---|
| 1 | golpe | 0 | aurora | US$ 15.310 M rueda en verde; gráfico previo→apertura→máximo→cierre pasa de +3,01% a −0,86%; la placa JPM cae y se hunde; flash rojo |
| 2 | esperado | 4,6 | panel | barra de lo esperado (5,92) y lo que dio (5,75) cae y golpea; −US$ 0,17; cinta de bancos del 13-oct |
| 3 | pregunta | 10,0 | aurora | estado de resultados, lupa sobre "Recompra de acciones", cae un "?" |
| 4 | recompras | 14,2 | panel | barras 8.300/8.300/6.700/1.060; la de 3T26 se desploma; −84% |
| 5 | campo | 21,2 | aurora | cartel "Campo JPM" se clava, nubes "TASAS ▲", lluvia, brotes, caja de cosecha US$ 27.036 M +13% |
| 6 | siembra | 30,1 | panel | valor libro US$ 112,64 vs precio US$ 340,58 → "3,02 veces"; sello CARO sobre recomprar; "sembrar más" con semillas; cita de Dimon |
| 7 | silo | 39,7 | aurora | silo que se llena de grano, +US$ 539 M; "sequía" tachada; "sembró más" brota; badges incobrables −15%, tarjetas 2,91% |
| 8 | informe | 47,2 | panel | tarjeta del informe con valor justo US$ 280,05; precio 1-sep→3-nov encima de la línea dorada; brecha −17,8% |
| 9 | final | 55,6 | aurora | −84%; tarjeta "gane poco" tachada; tarjeta roja "dejó de comprarse"; cursor Guardalo/Mandáselo/Ese amigo |
| 10 | comenta | 63,8 | aurora | se tipea JPMORGAN, se publica, llega el DM con "Ver la guía" |
| 11 | logo | 69,4 | panel | cierre Manfredi |

## Datos no verificables desde la nube / con salvedad
- **Recorrido intradiario del 13-oct**: solo hay apertura, máximo, mínimo y cierre diarios. El gráfico de la escena 1 une previo→apertura→máximo→cierre; el orden máximo-antes-del-cierre coincide con la prensa ("subió hasta 3% temprano y después dio vuelta") pero no se vio la serie intradiaria.
- **Consenso de EPS**: US$ 5,92 (Bloomberg, vía Yahoo Finance); otras fuentes dicen US$ 5,94. No se pudo abrir la fuente primaria de Bloomberg/LSEG.
- **8-K de la SEC (verificado con WebFetch, 4-nov)**: comunicado (Ex. 99.1) y suplemento (Ex. 99.2) confirman ganancia US$ 15,3 MM, EPS 5,57/5,75, ROTCE 20%/21%, ingresos managed US$ 50,9 MM, NII reportado US$ 27.036 M (+13%), préstamos US$ 1.584.641 M, castigos netos US$ 2,2 MM (−US$ 389 M ≈ −15%), aumento de reservas US$ 539 M, provisión US$ 2.743 M, TBVPS US$ 112,64, recompras **netas** US$ 664 M y tarjetas **2,91%** (el informe decía 2,90% y NII 27,04: el video usa las cifras del 8-K). **No se pudo verificar** la recompra **bruta** de US$ 1.060 M (3,1 M acciones a US$ 342,33) ni los US$ 6.700 M / 8.300 M de trimestres previos: la página del suplemento llega cortada; esas cifras salen del informe. TIKR (lectura del suplemento) confirma US$ 1,06 MM brutos y US$ 6,70 MM en 2T26 "en la misma base", aunque en otro párrafo cita US$ 6,79 MM. Se corrigió 2,90% → 2,91% en `informes/jpm.html`.
- **Cita de Dimon**: en castellano, tal como la traduce el informe; no se pudo verificar contra la transcripción original en inglés.
- **Fechas de resultado de los pares**: la cinta muestra cómo cerraron C, WFC, BAC y GS el 13-oct (Yahoo), sin afirmar que hayan reportado ese día.
- **Ranking histórico**: no se buscó "peor/mejor día desde X" porque el movimiento (−0,86%) no es extremo; el gancho es el contraste entre una ganancia de US$ 15.300 M y la acción en rojo.
