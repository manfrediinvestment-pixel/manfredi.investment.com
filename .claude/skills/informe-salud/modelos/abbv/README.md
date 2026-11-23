# Modelo ABBV (AbbVie Inc.) — informe-salud, Módulo A (pharma) — informe inicial (22-nov-2026)

Todo número derivado de `informes/abbv.html` sale de `model.py`. El HTML se arma con el sistema de tokens `{{clave|formato}}`
de LLY/JNJ; `verify.py` compara el HTML contra el modelo y tiene que dar **0 diferencias** antes de publicar.

## Archivos
| Archivo | Qué hace |
|---|---|
| `sotp.py` | Motor del Método 1: producto por producto hasta la LOE (curvas de erosión), rNPV del pipeline, I+D como línea corporativa, valor terminal propio de Botox y estética (sin LOE clásica), plataforma post-2040 |
| `model.py` | Datos del 3T26, puente GAAP → ajustado, los cuatro métodos, blend, anti-circularidad (se re-corre con `ABBV_PRICE` = precio × 1.25), dict `cmp` y cuadro PFE/ABBV/LLY/JNJ → `model.json` |
| `abbv.head.html` / `abbv.body.tpl.html` / `engine.js` / `charts_abbv.js` | Cabecera+CSS (copia de LLY), texto con tokens, motor de gráficos de LLY, datos de los gráficos |
| `build.py` | Genera las tablas de largo variable (pares, pipeline, reversión, cuadro comparativo) con tokens, parchea el motor para celular (igual que LLY) y renderiza `informes/abbv.html` |
| `render.py` / `verify.py` | Tokens → HTML; HTML ↔ modelo (914 tokens), aritmética del blend, celda Base, suma de partes, anti-circularidad, deuda, puente, claves de `cmp`, gate, logo, gris, lenguaje relativo |
| `index_add.py` | (integración) reemplaza la tarjeta "Próximamente" de ABBV del panel Defensivos por la tarjeta activa; no toca el contador |
| `manifest_add.py` | (integración) entrada nueva arriba de `informes/manifest.json` |
| `fetch_data.py`, `raw/dl_q.py`, `raw/totext.py`, `raw/ua.py` | EDGAR (User-Agent genérico, sin datos personales): 8-K, 10-Q, 10-K, companyfacts → `raw/*.txt` |

Datos de mercado, consenso, pares, WACC común (7.114%), tasas BIO e IRA: `.claude/skills/_compartido/defensivos_nov26.json`
(y `defensivos_nov26/yh/ABBV.mo.json` para la reversión). No se volvieron a buscar.

## Resultado (cierre 20-nov-2026, $286.20)
| Método | Valor | Peso | vs. precio | Tipo |
|---|---|---|---|---|
| M1 suma de partes + rNPV | $106.53 | 15% | −62.8% | independiente |
| M2 comparables (mediana 15.766x, NVS, × EPS 2027 $16.22, descontado al ke común) | $237.89 | 25% | −16.9% | independiente |
| M3 reversión (12 cierres post-Humira, 19.39x × EPS ajustado TTM $12.83) | $248.78 | 35% | −13.1% | anclado |
| M4 consenso (29 analistas) | $315.88 | 25% | +10.4% | anclado |
| **Blend** | **$241.49** | | **−15.6%** | neutral, con sesgo bajista |

M2: la regresión P/E vs. crecimiento no se sostiene (R² 0.27 / 0.41 con todos; 0.01 / 0.19 sin LLY) → regla de la casa
(desde KO, decisión del coordinador, igual en PFE): mediana. El cuartil superior (19.95x, GILD → $301.05; blend $257.28) se
muestra como referencia fuera del blend. Postura: regla de `model.py` (≤1 método arriba del precio y blend < −10% → sesgo bajista).

## Integración (rama feat/defensivos-10-de-10)
Desde la raíz del repo, con `informes/abbv.html` y esta carpeta ya traídos de `feat/informe-abbv`, y la carpeta
`modelos/pfe/` de `feat/informe-pfe` (para que el cuadro comparativo tenga las cuatro columnas):

```
cd .claude/skills/informe-salud/modelos/abbv && python model.py && python build.py && python verify.py
python index_add.py && python manifest_add.py
cd ../../../../.. && node scripts/catalogo-informes.mjs
```

`model.py` busca el `cmp` de Pfizer primero en `../pfe/model.json` y después en el worktree hermano
`C:\Users\Equipo\Documents\manfredi-pfe\...\pfe\model.json`; si no existe, el cuadro muestra ABBV/LLY/JNJ y una nota.
Si se cambia el informe de PFE, re-correr `model.py && build.py && verify.py` acá (y lo simétrico en `modelos/pfe/`).
El contador "N de 10 con informe completo" lo ajusta la integración, no `index_add.py`.

## Decisiones declaradas
- Curva de biológicos = Humira real (10-K 2019/2022/2025): EE.UU. −34.7% / −61.6% / −83.6% / −91.8% (2026E) acumulado; resto del
  mundo desde 2018; ponderada 86/14 con la mezcla de Skyrizi. Moléculas pequeñas: −80% / −90% (skill).
- LOE: Skyrizi 2033 (10-K, compuesto), Rinvoq abr-2037 (10-K, acuerdos); resto Orange Book (sustancia) o 12 años BPCIA; Imbruvica
  2032 y Linzess 2029 por acuerdos citados en prensa (no verificados en EDGAR).
- Pagos contingentes (regalías de Skyrizi a Boehringer): se suman al margen de contribución y el pasivo ($27.3B) se resta como deuda.
- Reversión: ventana posterior a la LOE de Humira (dic-23 a sep-26); la previa (2020-2022, 10.85x → $139.18) se muestra y no entra.
- IPR&D adquirida queda dentro del EPS ajustado (regla de la casa).
