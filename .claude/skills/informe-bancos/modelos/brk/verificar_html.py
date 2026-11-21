"""Chequea que las cifras del modelo aparezcan en informes/brk.b.html (edición 3T26)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
html = open(os.path.join(ROOT, 'informes', 'brk.b.html'), encoding='utf-8').read()
r = json.load(open(os.path.join(HERE, 'resultados.json'), encoding='utf-8'))
n, s, d = r['nov'], r['sep'], r['derivados']
b = n['base']

def m(x):  # $M con punto de miles
    return '$' + f'{round(x):,}'.replace(',', '.') + 'M'

exp = {
    'blend': f"${n['blend']:.2f}", 'sotp': f"${b['ps']['total']:.2f}", 'rev': f"${n['rev']:.2f}",
    'cons': f"${n['consensus']:.2f}", 'bear': f"${n['bear']:.2f}", 'bull': f"${n['bull']:.2f}",
    'expected': f"${n['expected']:.2f}", 'float_eq': f"${n['float_eq']:.2f}", 'simple': f"${n['simple']:.2f}",
    'port_ps': f"${b['ps']['port']:.2f}", 'ins_ps': f"${b['ps']['ins']:.2f}", 'bnsf_ps': f"${b['ps']['bnsf']:.2f}",
    'bhe_ps': f"${b['ps']['bhe']:.2f}", 'msr_ps': f"${b['ps']['msr']:.2f}",
    'eq_mkt': m(b['eq_mkt']), 'unreal': m(b['unreal']), 'dtl': m(b['dtl']), 'eqm': m(b['eqm']),
    'cash_fixed': m(b['cash_fixed']), 'port': m(b['port']), 'ins': m(b['ins']), 'bnsf': m(b['bnsf']),
    'bhe': m(b['bhe']), 'msr': m(b['msr']), 'total': m(b['total']), 'uw': m(b['uw']), 'float_y': m(b['float_y']),
    'ins_base': m(b['ins_base']), 'bvps': f"${n['bvps']:.2f}", 'pb_now': f"{n['pb_now']:.2f}x",
    'updown': f"{abs(n['updown'])*100:.1f}%", 'mult_to_price': f"{n['mult_to_price']*100:.1f}%",
    'rev3': f"${n['rev_3y']:.2f}", 'revbb': f"${n['rev_buyback']:.2f}",
    'ttm_op': m(d['ttm_op']), 'ttm_ni': m(d['ttm_ni']), 'ttm_rev': m(d['ttm_rev']), 'op_ps': f"${d['op_ps']:.2f}",
    'ni_ps': f"${d['ni_ps']:.2f}", 'roe_op': f"{d['roe_op']*100:.1f}%", 'roe_gaap': f"{d['roe_gaap']*100:.1f}%",
    'rate100': m(d['rate100']).replace('M', ' millones').replace('$', '$'), 'cash': m(d['cash']),
    'buy3': m(r['buy3']['usd']), 'buy3px': f"${r['buy3']['px']:.2f}", 'pb_all': f"{r['buy3']['pb_all']:.2f}x",
    'cross_ps': f"${abs(d['cross']['ps']):.2f}", 'sep_blend': '$504.40', 'sep_sotp': '$494.13',
}
exp['rate100'] = '$' + f"{round(d['rate100']):,}".replace(',', '.') + ' millones'
for i, row in enumerate(n['grid']):
    for j, v in enumerate(row):
        exp[f'grid{i}{j}'] = f"${v:.2f}"
for y, bv, p, pb, imp in n['rev_rows']:
    exp[f'rev{y}'] = f"${imp:.2f}"
bad = {k: v for k, v in exp.items() if v not in html}
print(f'{len(exp) - len(bad)}/{len(exp)} cifras encontradas')
for k, v in bad.items():
    print('  FALTA', k, v)
# restos de la edición anterior
for old in ['$503.49 mercado', '22-sep', '2T 2026 (cierre 30 jun', '$359.230', '$48.014M</td><td class="right-al">100%', '#5d646f']:
    if old in html:
        print('  RESTO', old, html.count(old))
