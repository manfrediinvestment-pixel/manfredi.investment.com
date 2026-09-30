# Compara informes/wmt.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE/'model.json'))
sys.path.insert(0, str(HERE))
from render import fmt, get
tpl = open(HERE/'wmt.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/wmt.html', encoding='utf-8').read()
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
# 2) aritmética del blend leída del propio HTML (cinco métodos, pesos con decimales)
def money(s): return float(s.replace('$', '').replace(',', '').replace('−', '-'))
rows = re.findall(r'<td class="label">Método (\d[ab]?) [^<]*</td><td class="label">([^<]*)</td><td class="right-al">([^<]+)</td><td class="right-al">([\d.]+)%</td><td class="right-al">([^<]+)</td>', out)
tot = 0; wsum = 0; fv = {}; typ = {}
for n, t, v, w, ap in rows:
    calc = money(v)*float(w)/100
    if abs(calc - money(ap)) > 0.006: diffs.append(f'aporte método {n}: {ap} vs {calc:.2f}')
    tot += calc; wsum += float(w); fv[n] = (money(v), float(w)); typ[n] = t
if len(rows) != 5: diffs.append(f'filas de métodos leídas: {len(rows)}')
if abs(wsum - 100) > 1e-9: diffs.append(f'pesos suman {wsum}')
if not (fv.get('1a', (0, 0))[1] == 7.5 and fv.get('1b', (0, 0))[1] == 7.5): diffs.append('el 15% intrínseco no está repartido 7.5/7.5')
blend = money(re.search(r'<div class="fv-value">([^<]+)</div>', out).group(1))
if abs(tot - blend) > 0.011: diffs.append(f'blend portada {blend} vs suma de aportes {tot:.4f}')
gap = re.search(r'vs\. \$[\d.,]+ mercado · ([^<]+)</div>', out).group(1)
if gap != fmt((blend/M['price']-1)*100, 'spct1'): diffs.append(f'gap portada {gap}')
if ('fv-gap pos' in out) != (blend > M['price']): diffs.append('clase pos/neg del gap')
# 3) grupos independientes / anclados recalculados desde el HTML, con las etiquetas de la tabla
ind = [n for n in fv if typ[n] == 'Independiente del precio']; anc = [n for n in fv if typ[n] == 'Anclado al mercado']
if sorted(ind) != ['1a', '1b', '2'] or sorted(anc) != ['3', '4']: diffs.append(f'etiquetas de grupo: {typ}')
gi = sum(fv[n][0]*fv[n][1] for n in ind)/sum(fv[n][1] for n in ind); ga = sum(fv[n][0]*fv[n][1] for n in anc)/sum(fv[n][1] for n in anc)
for lab, g in (('independientes del precio', gi), ('anclados al mercado', ga)):
    shown = money(re.search(r'Promedio ponderado de los ' + lab + r'[^<]*</td><td class="label"></td><td class="right-al">([^<]+)</td>', out).group(1))
    if abs(shown - g) > 0.011: diffs.append(f'promedio de grupo {lab}: {shown} vs {g:.4f}')
# 4) celda Base de la grilla y de la sensibilidad a comparables = DCF Base
for key in ('Grilla WACC', 'Sensibilidad a las ventas comparables'):
    cell = re.search(r'base-cell">([^<]+)</td>', out.split(key)[1]).group(1)
    if cell != fmt(M['dcf_base'], 'usd2'): diffs.append(f'celda base {key}: {cell}')
# 5) la suma de partes cierra y Walmex/India no se cuentan dos veces
if abs(sum(v['ev'] for v in M['sotp'].values())/M['sh_dil']*1000 - M['sotp_base']) > 1e-6: diffs.append('suma de partes no cierra')
if abs(M['intl_rest_oi26'] - (M['seg']['intl']['oi'] - M['walmex_oi_usd'] + M['india_loss'])) > 1e-9: diffs.append('resto de Internacional')
# 6) comparables: el método no usa el precio de WMT (recalcula con otro precio y el valor no cambia)
if M['reg_ok'] and abs(M['comp_pe'] - M['reg_comp_pe_wmt']*M['eps_ntm']) > 1e-9: diffs.append('P/E de comparables no es el de la regresión')
# 7) reglas de texto
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ (hora|día)', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
for w in re.findall(r'\b(hoy|ayer|mañana)\b', out, re.I): diffs.append(f'lenguaje relativo (código): {w}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
if 'src="../assets/logos/wmt.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
