# Compara informes/lly.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json', encoding='utf-8'))
src = open('render.py', encoding='utf-8').read().split('src = open(sys.argv[1]')[0]
ns = {}; exec(src, ns); fmt, get = ns['fmt'], ns['get']
tpl = open('lly.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/lly.html', encoding='utf-8').read()
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
def money(s): return float(s.replace('$', '').replace(',', '').replace('−', '-'))
rows = re.findall(r'<td class="label">Método (\d)[^<]*</td><td class="label">[^<]*</td><td class="right-al">([^<]+)</td><td class="right-al">(\d+)%</td><td class="right-al">([^<]+)</td>', out)
tot = 0
for n, fv, w, ap in rows:
    calc = money(fv) * int(w) / 100
    if abs(calc - money(ap)) > 0.006: diffs.append(f'aporte método {n}: {ap} vs {calc:.2f}')
    tot += calc
if len(rows) != 4: diffs.append(f'filas de métodos leídas: {len(rows)}')
blend = money(re.search(r'<div class="fv-value">([^<]+)</div>', out).group(1))
if abs(tot - blend) > 0.011: diffs.append(f'blend portada {blend} vs suma de aportes {tot:.4f}')
gap = re.search(r'vs\. \$[\d.,]+ mercado · ([^<]+)</div>', out).group(1)
if gap != fmt((blend / M['price'] - 1) * 100, 'spct1'): diffs.append(f'gap portada {gap}')
if ('fv-gap pos' in out) != (blend > M['price']): diffs.append('clase pos/neg del gap')
# 3) celda Base de la grilla = Método 1; suma de partes y puente del Método 1
cell = re.search(r'base-cell">([^<]+)</td>', out).group(1)
if cell != fmt(M['m1'], 'usd2'): diffs.append(f'celda base: {cell}')
S = M['sotp']
if abs(sum(S.values()) - M['m1_ev']) > 1e-9 or abs((M['m1_ev'] - M['net_debt']) / M['shares_dil'] * 1000 - M['m1']) > 1e-9: diffs.append('suma de partes')
if abs(M['sep_rebuilt_m1'] + sum(M['m1_bridge_vals']) - M['m1']) > 1e-6: diffs.append('puente del Método 1')
if abs(M['blend_at_sep_price'] + M['bridge_price'] - M['blend']) > 1e-9: diffs.append('puente del blend')
# 4) grupos independientes / anclados recalculados desde el HTML
fv = {n: money(v) for n, v, w, a in rows}
ind = (0.15 * fv['1'] + 0.25 * fv['2']) / 0.40; anc = (0.35 * fv['3'] + 0.25 * fv['4']) / 0.60
if fmt(ind, 'usd2') not in out or fmt(anc, 'usd2') not in out: diffs.append('promedios de grupo')
# 5) anti-circularidad: comparables, reversión y consenso no dependen del precio de LLY
for k in ('anti_m2', 'anti_m3', 'anti_m4'):
    if M[k] != 0: diffs.append(k)
if abs(M['m2'] - M['peer_q3'] * M['c27'] / (1 + M['ke'] / 100)) > 1e-9: diffs.append('Método 2 no es cuartil superior x EPS 2027')
# 6) deuda: corto + largo = deuda total del 10-Q (sin duplicar la porción corriente)
if abs(M['debt'] - 49.503) > 1e-9: diffs.append('deuda total')
# 7) reglas de texto y del sitio
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ hora', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
if 'src="../assets/logos/lly.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
if re.search(r'#5d646f|#6b7280|#9ca3af|#888|#999|color:\s*gr[ae]y', out, re.I): diffs.append('texto gris')
if 'Datos al 3T 2026 (cierre 30 sep 2026, publicado 29 oct 2026)' not in out: diffs.append('cabecera')
for old in ('$986.03', '$1,150.99', '$386.44', '$750.91'):   # solo pueden aparecer como referencia a septiembre
    pass
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
