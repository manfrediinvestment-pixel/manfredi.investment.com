# Verifica informes/dis.html contra resultados.json: aritmética del blend leída del HTML, cifras clave, gate, logo y
# lenguaje relativo a fechas. Sale con código 1 si algo no cierra.
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
R = json.load(open(HERE/'resultados.json', encoding='utf-8'))
s = open(ROOT/'informes'/'dis.html', encoding='utf-8').read()
def num(t): return float(t.replace('$', '').replace('.', '').replace(',', '.').replace('−', '-'))
def es(v, d=2): return f'{abs(v):,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
bad = []
rows = re.findall(r'<td class="label">Método (\d) — [^<]*</td><td class="label">([^<]*)</td><td class="right-al">([^<]+)</td><td class="right-al">([\d,]+)%</td><td class="right-al">([^<]+)</td>', s)
if len(rows) != 5: bad.append(f'filas del blend: {len(rows)}')
tot = 0
for n, t, v, w, a in rows:
    if abs(num(v)*num(w)/100 - num(a)) > 0.006: bad.append(f'aporte método {n}')
    tot += num(v)*num(w)/100
fv = num(re.search(r'<div class="fv-value">([^<]+)</div>', s).group(1))
if abs(fv - tot) > 0.011 or abs(fv - R['blend']) > 0.006: bad.append(f'blend {fv} vs {tot} / {R["blend"]}')
for k in ('dcf_base', 'sotp_base', 'comp', 'rev', 'cons', 'indep', 'anch', 'sep_blend_w', 'dcf_bear', 'dcf_bull'):
    if '$' + es(R[k]) not in s: bad.append(f'no aparece {k} = ${es(R[k])}')
base_cell = re.search(r'base-cell">([^<]+)</td>', s).group(1)
if abs(num(base_cell) - R['dcf_base']) > 0.006: bad.append('celda base de la grilla')
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ (hora|día)', vis, re.I): bad.append(f'lenguaje relativo: {w}')
if '_preview-gate.js' not in s: bad.append('falta el gate')
if 'src="../assets/logos/dis.png"' not in s: bad.append('falta el logo')
if '#5d646f' in s: bad.append('texto gris')
print('diferencias:', len(bad)); [print(' -', b) for b in bad]; sys.exit(1 if bad else 0)
