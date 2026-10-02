# Compara informes/pep.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json'))
src = open('render.py', encoding='utf-8').read().split('src = open(sys.argv[1]')[0]
ns = {}; exec(src, ns); fmt, get = ns['fmt'], ns['get']
tpl = open('pep.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/pep.html', encoding='utf-8').read()
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
rows = re.findall(r'<td class="label">Método (\d)[^<]*</td><td class="label">[^<]*</td><td class="right-al">([^<]+)</td><td class="right-al">([\d.]+)%</td><td class="right-al">([^<]+)</td>', out)
tot = 0
for n, fv, w, ap in rows:
    calc = money(fv)*float(w)/100
    if abs(calc - money(ap)) > 0.006: diffs.append(f'aporte método {n}: {ap} vs {calc:.2f}')
    tot += calc
if len(rows) != 5: diffs.append(f'filas de métodos leídas: {len(rows)}')
if abs(sum(float(w) for _, _, w, _ in rows) - 100) > 1e-9: diffs.append('los pesos no suman 100%')
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
ind = (0.075*fv['1'] + 0.075*fv['2'] + 0.25*fv['3'])/0.40; anc = (0.35*fv['4'] + 0.25*fv['5'])/0.60
if fmt(ind, 'usd2') not in out or fmt(anc, 'usd2') not in out: diffs.append('promedios de grupo')
# 5) puentes: DCF (deuda neta SIN arrendamientos) y suma de partes (CON arrendamientos), Celsius y participadas una sola vez
eq = M['dcf_base_ev'] - M['net_debt'] - M['nci'] + M['celh_val'] + M['eqm']
if abs(eq - M['dcf_base_eq']) > 1e-9: diffs.append('puente del DCF')
eq2 = M['sotp_ev'] - M['net_debt_l'] - M['nci'] + M['nonop']
if abs(eq2 - M['sotp_eq']) > 1e-6: diffs.append('puente de la suma de partes')
if abs(M['nonop'] - M['celh_val'] - M['eqm']) > 1e-12: diffs.append('activos no operativos')
# 6) anti-circularidad: comparables y suma de partes no pueden depender del precio ni del múltiplo de PEP.
#    Se recalculan con un precio de PEP distinto: tienen que dar exactamente lo mismo.
if M['reg_ok']: diffs.append('una regresión sostiene ajuste: revisar el Método 3')
if abs(M['comp_pe'] - M['peer_pe_med']*M['eps_ntm']) > 1e-9: diffs.append('comparables P/E no es mediana x EPS')
if 'PEP' in M['peers']: diffs.append('PepsiCo está dentro de su propio grupo de pares')
# Prueba: se corre el modelo con otro precio de PEP (los asserts de redacción se neutralizan) y los tres métodos
# independientes del precio tienen que dar exactamente lo mismo.
src_m = open('model.py', encoding='utf-8').read()
src_m = src_m.replace("PRICE = put('price', yh_close('PEP'))", "PRICE = put('price', 99.0)")
src_m = src_m.replace("json.dump(M, open('model.json', 'w'), indent=1, default=float)", "TEST_OUT = {k: M[k] for k in ('comp', 'sotp', 'dcf_base')}")
src_m = re.sub(r'(?m)^(\s*)assert .*$', r'\1pass', src_m)
ns_t = {'__name__': 'anticirc', '__file__': 'model.py'}
try:
    exec(compile(src_m, 'model_test', 'exec'), ns_t)
    for k in ('comp', 'sotp'):   # el DCF usa pesos de mercado en el WACC (declarado en la Sección 15)
        if abs(ns_t['TEST_OUT'][k] - M[k]) > 1e-9: diffs.append(f"{k} cambia con el precio de PEP: {ns_t['TEST_OUT'][k]} vs {M[k]}")
    print('anti-circularidad: comparables y suma de partes no cambian con el precio de PEP')
except Exception as e:
    diffs.append(f'no corrió la prueba de anti-circularidad: {e!r}')
# 7) reglas de texto
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana)\b|hace \d+ hora', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
for w in re.findall(r'\b(hoy|ayer|mañana)\b', out, re.I): diffs.append(f'lenguaje relativo (código): {w}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
if 'src="../assets/logos/pep.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
