# Contexto compartido — petróleo y gas argentino (YPF, VIST; reutilizable para PAM upstream y TGS) — corte 24-nov-2026

Búsqueda hecha UNA vez el 24-nov-2026 para los informes de YPF y VIST. Cada dato con fecha y fuente.
Espejo de máquina: `contexto_energia_2026_11.py` (mismos números; los `valuacion.py` importan de ahí).
Macro y costo de capital: `contexto-2026-11.md` (apartado "Actualización 24-nov-2026" al final).

**Fecha de corte: martes 24-nov-2026** (cierre de NYSE y BYMA). El riesgo país es el del 23-nov (1.035 pb):
es el último EMBI publicado al cierre del 24-nov.

## 1. Crudo

| Dato | Valor | Fecha | Fuente |
|---|---|---|---|
| Brent spot (futuro 1er mes) | **USD 88,41/bbl** | 24-nov-2026 | Yahoo BZ=F |
| WTI spot | USD 81,64/bbl | 24-nov-2026 | Yahoo CL=F |
| Brent a cierre de mes | mar-26 118,35 · jun-26 72,92 · sep-26 103,53 · oct-26 117,64 · 24-nov 88,41 (−25% en noviembre) | — | Yahoo BZ=F |
| Brent promedio | 2024: 73,1 · 2025: 68,1 · **4T25: 63,1** · 3T26: 91,5 · 2026 al 24-nov: 91,4 | — | cálculo sobre Yahoo BZ=F |
| Curva Brent (NYMEX BZ, dic) | dic-27 **75,74** · dic-28 71,82 · dic-29 70,00 · dic-30 **68,87** | 24-nov-2026 | Yahoo BZZ27…BZZ30.NYM |
| Curva WTI (dic) | dic-27 71,80 · dic-28 67,70 · dic-29 65,43 · dic-30 63,25 · dic-31 60,65 | 24-nov-2026 | Yahoo CLZ27…CLZ31.NYM |
| EIA STEO | Brent 2027 ~USD 86 (85,78), 4T27 77; 2026 ~97 | publicado 10-nov-2026 | OGJ; Newsquawk |
| Precios realizados 3T26 | Vista 84,2 (exportación 86,0 / mercado interno 79,5); YPF 81,4 | 3T26 | 6-K de cada una (28-oct-2026) |
| **Descuento realizado vs. Brent (3T26, Brent 91,3)** | **Vista −7,1 · YPF −9,9** | 3T26 | cálculo sobre los 6-K |
| Medanito vs. Brent | Pasó de prima excepcional en el 2T26 (Brent en ~97) a descuento en el 3T26; Argus registró primas de hasta +8 y descuentos de hasta −8,5 USD en 12 meses; descuento de ~8 USD la semana del 11-nov | 2026 | 6-K YPF 3T26; Infobae 11-nov-2026; El Monterizo |
| Paridad de importación / naftas | Las petroleras fijan los surtidores con referencia a la paridad de importación en pesos; la nafta subió por debajo del IPC en 2026 y la baja del Brent de noviembre "modera aumentos", sin bajas | nov-2026 | Infobae 11-nov-2026; Revista Códigos 24-nov-2026 |

**Deck (regla de informe-energia — nunca el spot):**

| Escenario | Brent LP | Ancla | Probabilidad |
|---|---|---|---|
| Bear | **USD 63** | Promedio del 4T25: un precio que la industria ya vivió hace un año | 25% |
| Base (mitad de ciclo) | **USD 70** | (a) planificación: Vista 75 real desde 2028, Goldman 70 en 2028, BofA 70 desde 2027, Bradesco LP 65; (b) EIA: 4T27 77; (c) curva dic-29/dic-30: 70,0 / 68,9 → se elige 70 | 45% |
| Bull | **USD 85** | EIA STEO 2027 (85,78) | 30% |

El año 1 (2027) arranca en la curva dic-27 (75,74) y converge al deck en el año 3.

## 2. Vaca Muerta

| Dato | Valor | Fecha | Fuente |
|---|---|---|---|
| Producción de petróleo de Vaca Muerta | **698,5 kbbl/d** (récord; 71,7% del país) | sep-2026 (publicado 21/26-oct) | Secretaría de Energía vía El Economista e iProfesional |
| Producción de petróleo nacional | ~973,7 kbbl/d (a 26,3 kbbl/d del millón) | sep-2026 | ídem |
| Neuquén | >700 kbbl/d por primera vez | sep-2026 | El Economista |
| Gas nacional | 158,8 MMm3/d (Vaca Muerta 96,5) | jul-2026 | La Capital MdP (Secretaría de Energía); el dato de sep-2026 no se encontró |
| Costo por pozo | ~USD 9 M en Neuquén vs. ~USD 6 M en Texas; perforar y completar es ~30% más caro que en el Permian | 2026 | Wei Wang (Texas RRC) vía LM Neuquén; El Economista mar-2026 |
| Costo de desarrollo | YPF: USD 8,6/bbl vs. 6,8 del Permian (+25%) — dato anterior a 2026 | — | Pablo Iuliano (YPF) vía LM Neuquén |
| Productividad | Pozo de 3.000 m: EUR ~1 MMbbl vs. ~0,5 MMbbl en el Permian | 2026 | Ricardo Markous (Tecpetrol) |
| **Break-even** | **USD 36-45/bbl** en Vaca Muerta vs. ~USD 67 del Permian (según el funcionario de Texas) | 2026 | oilprice.com; Texas RRC |
| Lifting cost | YPF hub shale **4,2 USD/boe** (100% WI; total compañía 7,8); Vista **4,7 USD/boe** | 3T26 | 6-K de cada una |

## 3. Infraestructura de evacuación — el techo del crecimiento de las dos

| Obra | Capacidad | Puesta en marcha | Quién tiene capacidad | Fuente |
|---|---|---|---|---|
| **VMOS** (Vaca Muerta Oil Sur, Allen–Punta Colorada, ~440 km) | 180 kbbl/d en la 1ª etapa → **550 kbbl/d en el 2S27**; se estudia 700 kbbl/d y más | Construcción del caño terminada en oct-26; COD a fin de 2026; primer crudo exportado a principios de 2027 (~85% de avance a sep-26) | Firme inicial ~275 kbbl/d: **YPF 120 kbbl/d** (30% de la sociedad), **Vista 50 kbbl/d** (9,09% de la sociedad), Pluspetrol 80, PAE ~15%; opciones de Chevron y Shell por hasta 230 kbbl/d | 6-K YPF 3T26; El Economista (Gustavo Chaab, CEO); LM Neuquén; estados de Vista (nota de asociadas) |
| **Duplicar Norte** (Oldelval) | Junto con VMOS lleva la evacuación a ~1,3 Mbbl/d | Obras desde nov-25; algo de capacidad a fin de 2026; puesta en marcha definitiva en **mar-2027** | Contratos firmados con clientes (sin detalle público por empresa) | Ricardo Hösel (CEO de Oldelval) vía Ámbito |
| Duplicar Plus (Oldelval) | En operación desde 2025 | — | Vista paga ship-or-pay: el costo de venta por boe cayó 14% i.a. en el 3T26 por dilución de volumen | 6-K Vista 3T26; LM Neuquén |

## 4. Comparables en USD (precios 24-nov-2026)

| Empresa | Grupo | EV/EBITDA (TTM) | P/E fwd | EV/boe 1P | DN/EBITDA | Div. yield | Nota |
|---|---|---|---|---|---|---|---|
| Diamondback (FANG) | shale EE.UU. | 5,32x | 8,1x | 18,8 | 0,99x | 2,7% | 1P dic-25 3.618 MMboe |
| EOG | shale EE.UU. | 4,85x | 8,6x | 14,1 | 0,16x | 3,0% | 1P 5.514 MMboe |
| Permian Resources (PR) | shale EE.UU. | 4,71x | 7,5x | 18,6 | 0,71x | 3,1% | 1P 1.116 MMboe |
| Devon (DVN) | shale EE.UU. | 5,64x | 8,0x | n.c. | 1,06x | 3,1% | 1P ~2.400 MMboe pre-fusión con Coterra: EV/boe no comparable |
| Petrobras (PBR) | Latam estatal | 3,81x | 3,8x | 13,3 | 1,42x | 9,0% | 1P 12.100 MMboe; EV con deuda jun-26 |
| Ecopetrol (EC) | Latam estatal | 3,63x | 7,0x | 28,5 | 1,89x | 4,9% | 1P 1.944 MMboe; COP 3.604,7 |
| PEMEX | Latam estatal | — | — | — | — | — | sin acción: bono 6,625% 2035 con G-spread ~331 pb (Cbonds, fecha no publicada) |
| Pampa (PAM) | local | 5,23x | 5,1x | n.c. | 1,81x | 0% | holding energética |
| TGS | local | ~3,6x | 7,6x | — | caja neta | 0% | EBITDA en ARS ÷ CCL de sep-26 (aprox.) |
| **YPF / VIST** | — | ver cada `valuacion.py` | | | | | |

Fuente: Yahoo Finance quoteSummary + fundamentals-timeseries (24-nov-2026); reservas: comunicados de resultados
2025 de cada empresa (FANG 23-feb-26, PR, EOG 24-feb-26, DVN 10-K 18-feb-26, Petrobras Agência, Ecopetrol). En PBR,
EC y TGS el EV/EBITDA se recalculó en USD porque Yahoo mezcla monedas. Refinadoras (para el downstream de YPF):
Valero 4,63x, Marathon 5,26x, Phillips 66 6,92x (EV/EBITDA TTM, Yahoo 24-nov).

## 5. Consenso — precios objetivo del ADR (ventana 90 días: 26-ago → 24-nov-2026)

| Casa | YPF (USD/ADR) | VIST (USD/ADR) | Fecha | Fuente |
|---|---|---|---|---|
| Goldman Sachs | **48,70** (desde 56,60; neutral) | **69,70** (desde 81,50; compra) | 10-nov-2026 | iProfesional 469296 (17-nov) y 469373 (21-nov) |
| JPMorgan | 66 (dic-2027; SOTP) | 94 (overweight) | 31-ago / 11-sep-2026 | Ecosistema Startup (Bloomberg) 11-sep |
| Citi | 60 (compra) | 91 (compra) | 11-sep-2026 | ídem |
| BofA | 65 | 107 (Brent 82 en 2026 y 70 desde 2027; DCF 35 años al 11%) | 10/11-sep-2026 | El Cronista 10-sep; Ecosistema Startup |
| BTG Pactual | 58 (compra) | 92 (compra) | 11-sep-2026 | Ecosistema Startup |
| UBS | 55 (neutral) | 80 (compra) | 10-sep / 28-oct-2026 | El Cronista; Bloomberg Línea |
| Itaú BBA | — | 100 (outperform) | 11-sep-2026 | Ecosistema Startup |
| HSBC | — | 90 (compra) | 11-sep-2026 | ídem |
| Bradesco BBI | 55 (neutral; Brent 2027 70, LP 65) | — | 28-oct-2026 | Bloomberg Línea |
| Santander | 84 | — | 28-oct-2026 | Bloomberg Línea |
| TPH Research | 85 | — | 28-oct-2026 | Bloomberg Línea |
| Allaria (local) | 80 | — | 28-oct-2026 | Bloomberg Línea |
| Latin Securities (local) | 65 | — | 28-oct-2026 | Bloomberg Línea |
| Adcap (local) | 63 (compra) | 87 (compra) | 30-oct-2026 | El Economista |
| **Promedio** | **65,39 (12 casas)** | **90,08 (9 casas)** | | |
| Fuera de ventana | Morgan Stanley 60 (overweight, 11-ago); Bradesco 55 (11-ago) | Jefferies 105 (sin fecha ni fuente primaria: excluido) | | El Cronista 11-ago |

Casi todos los targets son **anteriores** a la caída de noviembre (Brent −25%, riesgo país de ~790 a 1.035 pb). Solo
Goldman recortó (10-nov), por mayor costo de capital: múltiplo EV/EBITDA 2028 de YPF de 3,4x a 2,8x y de Vista de
3,8x a 3,4x; con Brent 75, las dos cotizan 2,4-3,2x EBITDA 2027. No se cita research de Balanz.

## 6. Regulación sectorial

| Tema | Estado | Fuente |
|---|---|---|
| **RIGI** | Decreto 105/2026 (19-feb-2026): extiende un año la adhesión (desde el 8-jul-2026) y suma el upstream onshore de petróleo y gas como actividad promovida; piso de inversión USD 600 M; exención de derechos de exportación después de 3 años | Boletín Oficial vía nota de los estados de Vista 3T26; Diario Uno |
| RIGI — YPF | Pendientes: **LLL Oil** (~USD 25.000 M, 15 años, presentado el 15-may-26), **Argentina LNG** (USD 51.000 M; ~29.000 M a 2031), **Bajo del Toro** (USD 8.700 M); en total 5 proyectos shale por ~USD 44.000 M, ~2.200 pozos y un pico de 270 kbbl/d | 6-K YPF 3T26; LM Neuquén; Industrial Info |
| RIGI — Vista | Pidió el ingreso de un proyecto upstream (Bandurria Norte, 100%), "en revisión" | Estados de Vista 3T26 (nota de marco regulatorio); Industrial Info |
| RIGI aprobados en upstream | Pluspetrol Bajo del Choique–La Invernada; Rincón de Aranda; Los Toldos II Este; VMOS (midstream) | Industrial Info |
| Derechos de exportación | Vista pagó USD 50,2 M en el 3T26 (4,1% de los ingresos; 5,9% de las exportaciones); en 2026 hubo idas y vueltas para el crudo convencional (8% con Brent alto) | 6-K Vista; iProfesional |
| Libertad de precios y exportación | Vista vende el 100% del crudo a paridad de exportación; YPF fija los surtidores con referencia a la paridad de importación (sin decreto de congelamiento vigente) | 6-K de cada una; Infobae |
| **ON en USD ("riesgo país corporativo")** | **YPF 2035**: USD 1.200 M al **7,85%** (cupón 7,55%; ley NY), ~300 pb sobre el UST (sep-2026, con el EMBI en 491-506) → spread/EMBI ≈ 0,56. YM34 (2034) TIR 7,43% (Rava, ~5-nov). **Vista**: ON XXXI USD 500 M al 7,88% (2038, abr-2026, EMBI 527, UST 4,28 → 0,68); ON XXIX USD 900 M al 8,50% (2033, jun-2025, EMBI 655 → 0,62); ley NY ~7,15% (jul-2026). **No se encontró la TIR de ninguna ON al 24-nov**: después del salto del EMBI de noviembre las TIR seguramente subieron | 6-K YPF 3T26; estados de Vista 3T26 (tabla de ON); Rava; iProfesional |

## 7. Matriz de 9 combinaciones — macro × crudo (DCF en USD por ADR)

Probabilidades independientes: macro 30/45/25 (Bear/Base/Bull de la skill, año preelectoral) × crudo 25/45/30
(informe-energia). Salida de `ypf/valuacion.py` y `vist/valuacion.py` (`matriz_dcf` en cada `salida.json`).

| Macro ↓ / Crudo → | Bear (Brent 63) | Base (70) | Bull (85) |
|---|---|---|---|
| **Bear** (RP 1.500 → 1.000; controles) | YPF 12,51 · VIST 21,38 | YPF 20,35 · VIST 36,72 | YPF 37,14 · VIST 69,59 |
| **Base** (RP 1.035 → 793) | YPF 41,90 · VIST 55,71 | **YPF 53,63 · VIST 77,71** | YPF 78,76 · VIST 124,85 |
| **Bull** (RP 1.035 → 500) | YPF 76,55 · VIST 91,76 | YPF 92,91 · VIST 121,28 | YPF 127,97 · VIST 184,52 |
| **Esperado** | | YPF **58,07** · VIST **84,90** | |

Precio al 24-nov: YPF 31,71 · VIST 49,61. Lectura: con el crudo en el Bear, la macro decide casi todo el valor de
YPF (de 12,5 a 76,6); en VIST la macro pesa algo menos y el crudo algo más, como corresponde a una exportadora pura.
