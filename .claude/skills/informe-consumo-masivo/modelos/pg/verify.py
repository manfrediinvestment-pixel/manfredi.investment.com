# Compara informes/pg.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open('model.json', encoding='utf-8'))
src = open('render.py', encoding='utf-8').read().split('src = open(sys.argv[1]')[0]
ns = {}; exec(src, ns); fmt, get = ns['fmt'], ns['get']
tpl = open('pg.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/pg.html', encoding='utf-8').read()
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
        if got != fmt(get(k), f): diffs.append(f'{k}: HTML={got!r} modelo={fmt(get(k), f)!r}')
print('tokens verificados:', len(tokens))
# 2) aritmética del blend leída del propio HTML
def money(s): return float(s.replace('$', '').replace(',', '').replace('−', '-'))
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
# 3) celdas Base de la grilla y de la sensibilidad al volumen = fair value del Método 1
for key in ('Grilla WACC', 'Sensibilidad al volumen'):
    cell = re.search(r'base-cell">([^<]+)</td>', out.split(key)[1]).group(1)
    if cell != fmt(M['dcf_base'], 'usd2'): diffs.append(f'celda base {key}: {cell}')
# 4) grupos independientes / anclados recalculados desde el HTML
fv = {n: money(v) for n, v, w, a in rows}
ind = (0.15*fv['1'] + 0.25*fv['2'])/0.40; anc = (0.35*fv['3'] + 0.25*fv['4'])/0.60
if abs(ind - M['indep']) > 0.011 or abs(anc - M['anch']) > 0.011 or fmt(M['indep'], 'usd2') not in out or fmt(M['anch'], 'usd2') not in out: diffs.append('promedios de grupo')
# 5) puente del DCF y del blend contra septiembre
if abs(M['dcf_base_ev'] - M['net_debt'] - M['nci'] - M['dcf_base_eq']) > 1e-9: diffs.append('puente del DCF')
if abs(M['sep']['blend'] + M['bridge_model'] + M['bridge_price'] - M['blend']) > 1e-9: diffs.append('puente contra septiembre')
# 6) anti-circularidad: el modelo con otro precio de PG da los mismos comparables, reversión y consenso
env = dict(os.environ, PG_PRICE='130', PYTHONIOENCODING='utf-8')
import shutil; shutil.copy('model.json', 'model.json.bak'); shutil.copy('model_sep.json', 'model_sep.json.bak')
try:
    subprocess.run([sys.executable, 'model.py'], env=env, check=True, capture_output=True)
    M2 = json.load(open('model.json', encoding='utf-8'))
    for k in ('comp', 'rev', 'cons'):
        if abs(M2[k] - M[k]) > 1e-9: diffs.append(f'anti-circularidad: {k} cambia con el precio')
    print('DCF Base con precio $130:', round(M2['dcf_base'], 2), '(solo por los pesos de mercado del WACC)')
finally:
    shutil.move('model.json.bak', 'model.json'); shutil.move('model_sep.json.bak', 'model_sep.json')
if M['reg_ok']: diffs.append('una regresión sostiene ajuste: revisar el Método 2')
# 7) reglas de texto y de estilo
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ (?:hora|día)', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
if 'src="../assets/logos/pg.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
for g in ('#5d646f', '#666', '#777', '#888', '#999', 'gray', 'grey'):
    if g in out.lower(): diffs.append(f'color gris en el HTML: {g}')
if 'Datos al 1T FY2027 (' not in out: diffs.append('encabezado de datos')
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
