# Compara informes/unh.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json'))
src = open('render.py', encoding='utf-8').read().split('src = open(sys.argv[1]')[0]
ns = {}; exec(src, ns); fmt, get = ns['fmt'], ns['get']
tpl = open('unh.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/unh.html', encoding='utf-8').read()
diffs = []
# 1) cada token de la plantilla aparece en el HTML con el valor del modelo, en su lugar
parts = re.split(r'(\{\{[^}]+\}\})', tpl); pattern = ''; tokens = []
for p in parts:
    m = re.fullmatch(r'\{\{([^|}]+)\|?([^}]*)\}\}', p)
    if m: pattern += '(.*?)'; tokens.append((m.group(1).strip(), m.group(2)))
    else: pattern += re.escape(p)
mm = re.fullmatch(pattern, out, re.S)
if not mm: diffs.append('el HTML no respeta la estructura de la plantilla (texto editado a mano)')
else:
    for (k, f), got in zip(tokens, mm.groups()):
        exp = fmt(get(k), f)
        if got != exp: diffs.append(f'{k}: HTML={got!r} modelo={exp!r}')
print('tokens verificados:', len(tokens))
# 2) aritmética del blend leída del propio HTML
def money(s): return float(s.replace('$','').replace(',','').replace('\u2212','-'))
rows = re.findall(r'<td class="label">Método (\d)[^<]*</td><td class="label">[^<]*</td><td class="right-al">([^<]+)</td><td class="right-al">(\d+)%</td><td class="right-al">([^<]+)</td>', out)
tot = 0
for n, fv, w, ap in rows:
    calc = money(fv)*int(w)/100
    if abs(calc - money(ap)) > 0.006: diffs.append(f'aporte método {n}: {ap} vs {calc:.2f}')
    tot += calc
if len(rows) != 4: diffs.append(f'filas de métodos leídas: {len(rows)}')
blend = money(re.search(r'<div class="fv-value">([^<]+)</div>', out).group(1))
if abs(tot - blend) > 0.011: diffs.append(f'blend portada {blend} vs suma de aportes {tot:.4f}')
gap = re.search(r'vs\. \$[\d.,]+ mercado · ([^<]+)</div>', out).group(1)
if gap != fmt((blend/M['price']-1)*100, 'spct1'): diffs.append(f'gap portada {gap}')
if ('fv-gap pos' in out) != (blend > M['price']): diffs.append('clase pos/neg del gap')
# 3) celda Base de la grilla y de la tabla de MLR = fair value de la suma de partes
for key in ('Grilla WACC', 'Sensibilidad al MLR'):
    cell = re.search(r'base-cell">([^<]+)</td>', out.split(key)[1]).group(1)
    if cell != fmt(M['dcf_base'], 'usd2'): diffs.append(f'celda base {key}: {cell}')
# 4) grupos independientes / anclados recalculados desde el HTML
fv = {n: money(v) for n, v, w, a in rows}
ind = (0.15*fv['1'] + 0.25*fv['2'])/0.40; anc = (0.35*fv['3'] + 0.25*fv['4'])/0.60
# el modelo los calcula con los valores sin redondear: se exige que el HTML muestre el del modelo y que el recálculo
# desde las cifras redondeadas del HTML no se aparte más de un centavo
if fmt(M['indep'],'usd2') not in out or fmt(M['anch'],'usd2') not in out: diffs.append('promedios de grupo (texto)')
if abs(ind - M['indep']) > 0.011 or abs(anc - M['anch']) > 0.011: diffs.append(f'promedios de grupo: {ind:.4f} / {anc:.4f}')
# 5) pesos por segmento suman 15% y los valores por segmento suman el EV
if abs(sum(M[f'w_{k}'] for k in ('uhc','health','insight','rx')) - 15) > 1e-9: diffs.append('pesos SOTP')
if abs(sum(M['sotp'][k]['ev'] for k in M['sotp']) - M['dcf_base_ev']) > 1e-6: diffs.append('suma de EV por segmento')
# 6) reglas de texto
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ hora', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
for w in re.findall(r'\b(hoy|ayer|mañana)\b', out, re.I): diffs.append(f'lenguaje relativo (código): {w}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
if 'src="../assets/logos/unh.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
# 7) edición 3T26: cabecera, sin gris, y con y sin el comparable en el límite
if 'Datos al 3T 2026 (cierre 30 sep 2026, publicado 13 oct 2026)' not in out: diffs.append('cabecera 3T26')
if '#5d646f' in out: diffs.append('verdict-note gris')
if abs(M['blend_comp_core'] - (M['blend'] - 0.25*M['comp'] + 0.25*M['comp_core'])) > 1e-9: diffs.append('blend sin el par en el límite')
if abs(M['blend'] - M['blend_sep'] - sum(M[f'd_contrib_{k}'] for k in ('dcf','comp','rev','cons'))) > 1e-9: diffs.append('puente contra septiembre')
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
