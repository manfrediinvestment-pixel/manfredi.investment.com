# Compara informes/cost.html contra model.json. Sale con código 1 si hay diferencias.
# Chequea: tokens en su lugar, aritmética del blend de cinco métodos (7.5/7.5/25/35/25) y de los grupos, celdas Base de la grilla
# y de la sensibilidad, cierre del DCF por negocio, anti-circularidad (otro precio no mueve comparables ni el DCF por negocio
# salvo por el WACC), lenguaje relativo a fechas, colores grises, gate y logo.
import json, re, sys, os, subprocess, tempfile
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE/'model.json'))
sys.path.insert(0, str(HERE))
from render import fmt, get
tpl = open(HERE/'cost.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/cost.html', encoding='utf-8').read()
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
# 3) grupos independientes / anclados recalculados desde el HTML
ind = [n for n in fv if typ[n] == 'Independiente del precio']; anc = [n for n in fv if typ[n] == 'Anclado al mercado']
if sorted(ind) != ['1a', '1b', '2'] or sorted(anc) != ['3', '4']: diffs.append(f'etiquetas de grupo: {typ}')
else:
    gi = sum(fv[n][0]*fv[n][1] for n in ind)/sum(fv[n][1] for n in ind); ga = sum(fv[n][0]*fv[n][1] for n in anc)/sum(fv[n][1] for n in anc)
    for lab, g in (('independientes del precio', gi), ('anclados al mercado', ga)):
        shown = money(re.search(r'Promedio ponderado de los ' + lab + r'[^<]*</td><td class="label"></td><td class="right-al">([^<]+)</td>', out).group(1))
        if abs(shown - g) > 0.011: diffs.append(f'promedio de grupo {lab}: {shown} vs {g:.4f}')
    vb = re.search(r'class="verdict-stance">(.*?)</div>', out, re.S).group(1)
    for g, k in ((gi, 'indep'), (ga, 'anch')):
        if abs(g - M[k]) > 0.011: diffs.append(f'grupo {k}: HTML {g:.4f} vs modelo {M[k]:.4f}')
        if fmt(M[k], 'usd2') not in vb: diffs.append(f'verdict-bar sin el promedio de grupo {k}')
# 4) celdas Base de la grilla y de la sensibilidad a comparables = DCF Base
for key in ('Grilla WACC', 'Sensibilidad a las ventas comparables'):
    cell = re.search(r'base-cell">([^<]+)</td>', out.split(key)[1]).group(1)
    if cell != fmt(M['dcf_base'], 'usd2'): diffs.append(f'celda base {key}: {cell}')
# 5) el DCF por negocio cierra (cuotas + mercadería + caja neta) y la caja no se cuenta dos veces
if abs(M['biz_base_memb_ps'] + M['biz_base_merch_ps'] + M['biz_netcash_ps'] - M['biz_base']) > 1e-9: diffs.append('DCF por negocio no cierra')
if abs(M['biz_netcash_ps'] - M['net_cash_dcf']/M['sh_dil']*1000) > 1e-9: diffs.append('caja neta del DCF por negocio')
# 6) anti-circularidad: el modelo corrido con otro precio de COST da los mismos comparables y DCF por negocio a igual WACC
with tempfile.TemporaryDirectory() as td:
    alt_out = os.path.join(td, 'alt.json')
    env = dict(os.environ, COST_PRICE_OVERRIDE='700', COST_MODEL_OUT=alt_out)
    subprocess.run([sys.executable, str(HERE/'model.py')], env=env, check=True, capture_output=True)
    A = json.load(open(alt_out))
for k in ('comp_val', 'comp_pe', 'comp_ev', 'pe_sel', 'eve_sel', 'rev2', 'rev1', 'eps_ntm'):
    if abs(A[k] - M[k]) > 1e-9: diffs.append(f'anti-circularidad: {k} cambia con el precio ({M[k]} -> {A[k]})')
if abs(A['dcf_base'] - M['dcf_base']) > 0.02*M['dcf_base']: diffs.append('el DCF se mueve más que por los pesos de mercado del WACC')
print(f"anti-circularidad: precio 700 -> comparables {A['comp_val']:.2f} (igual), DCF {A['dcf_base']:.2f} vs {M['dcf_base']:.2f} (solo WACC)")
# 7) reglas de texto: lenguaje relativo a fechas, grises
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
vis_txt = re.sub(r'<[^>]+>', ' ', vis)
REL = r'\b(hoy|ayer|mañana|este año|el año pasado|este mes|el mes pasado|la semana pasada|esta semana|actualmente|recientemente|hace poco|el próximo mes|el año que viene)\b|hace \d+ (hora|día|semana|mes)'
for w in re.finditer(REL, vis_txt, re.I): diffs.append(f'lenguaje relativo: {w.group(0)}')
for w in re.findall(r'\b(hoy|ayer|mañana)\b', out, re.I): diffs.append(f'lenguaje relativo (código): {w}')
GRAYS = ['#5d646f', '#6b7280', '#9ca3af', '#888', '#999', '#777', '#666', '#aaa', 'gray', 'grey']
for g in GRAYS:
    for m in re.finditer(re.escape(g), out, re.I):
        ctx = out[max(0, m.start()-60): m.end()+10]
        if re.search(r'color\s*:', ctx) and 'border' not in ctx[-40:]: diffs.append(f'color gris en texto: {ctx!r}')
if '_preview-gate.js' not in out: diffs.append('falta el gate')
for sid in ('s01', 's03', 's04'):
    if f'id="{sid}"' not in out: diffs.append(f'falta la sección {sid} que usa el gate')
if 'class="disclosure"' not in out or 'class="wrap"' not in out: diffs.append('estructura del gate')
if 'src="../assets/logos/cost.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
