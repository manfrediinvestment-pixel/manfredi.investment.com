"""Renderiza informes/ant.html desde ant.src.html reemplazando {{TOKENS}} con resultados.json.
Uso: python valuacion.py <precio_cierre> && python render.py <fecha_precio>"""
import json, re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(here, 'resultados.json'), encoding='utf-8'))
fecha = sys.argv[1] if len(sys.argv) > 1 else '19-nov-2026'
P = r['price']
usd = lambda v: f"${v:,.2f}"
sg = lambda v: (f"+{v:.1f}%" if v >= 0 else f"&minus;{abs(v):.1f}%")
pc = lambda v: (v / P - 1) * 100
cls = lambda v: 'pos' if v >= P else 'neg'
d = r['dcf']
T = {
  'PRICE': usd(P), 'PRICE0': f"${P:.0f}", 'FECHA': fecha,
  'DAY1': sg((P / 83 - 1) * 100),
  'BLEND': usd(r['blend']), 'BLEND0': f"${r['blend']:.0f}", 'BLEND_PCT': sg(r['blend_pct']), 'BLEND_CLS': cls(r['blend']),
  'SIMPLE': usd(r['simple']), 'BLEND_EXCONS': usd(r['blend_ex_cons']), 'BLEND_BEAR': usd(r['blend_bear']), 'BLEND_EXPLTR': usd(r['blend_ex_pltr']),
  'MCAP_B': f"${r['mcap_basic_B']/1000:.2f} billones", 'MCAP_D': f"${r['mcap_diluted_B']/1000:.2f} billones",
  'EV_D': f"${r['ev_diluted_B']/1000:.2f} billones", 'DIL_SH': f"{r['diluted_shares_B']:,.2f}", 'BAS_SH': f"{r['basic_shares_B']:,.2f}",
  'REV26': f"${r['rev_2026E']:.1f}", 'Q426': f"${r['q4_26E']:.1f}",
  'EVREV27': f"{r['ant_ev_rev27']:.1f}x", 'EVRR': f"{r['ev_diluted_B']/81:.1f}x",
  'MKT_MULT': f"{r['mkt_mult']:.1f}x", 'IPO_MULT': f"{r['ipo_mult']:.1f}x",
  'DCF_SIMPLE': usd(r['dcf_simple']), 'DCF_PW': usd(r['dcf_pw']),
  'INV_K': f"{r['inv_growth_factor']:.2f}", 'INV_REV36': f"${r['inv_rev_2036']:,.0f}", 'INV_MARGIN': f"{r['inv_margin']:.1f}%",
  'INV_G': ', '.join(f"{x:.0f}%" for x in r['inv_growth'][1:6]),
  'PEER_AVG': f"{r['peer_avg']:.1f}x", 'COMPS': usd(r['comps']), 'COMPS_LO': usd(r['comps_lo']), 'COMPS_HI': usd(r['comps_hi']),
  'COMPS_EXPLTR': usd(r['comps_ex_pltr']),
  'OWN': usd(r['own']), 'OWN_LO': usd(r['own_lo']), 'OWN_HI': usd(r['own_hi']), 'WIN_MULT': f"{r['win_mult']:.1f}x",
  'CONS': usd(r['cons']), 'CONS_EXM': usd(r['cons_ex_melius']),
}
for k in ('bear', 'base', 'bull'):
    K = k.upper()
    T[f'DCF_{K}'] = usd(d[k]['fv']); T[f'DCF_{K}_PCT'] = sg(d[k]['pct']); T[f'DCF_{K}_CLS'] = cls(d[k]['fv'])
    T[f'TV_{K}'] = f"{d[k]['tv']:.1f}%"
    T[f'REV27_{K}'] = f"${d[k]['rev'][0]:.0f}B"; T[f'REV31_{K}'] = f"${d[k]['rev'][4]:.0f}B"; T[f'REV36_{K}'] = f"${d[k]['rev'][9]:,.0f}B"
    T[f'FCF27_{K}'] = f"${d[k]['fcf'][0]:.1f}B"
for i, row in enumerate(r['grid']):
    for j, v in enumerate(row):
        T[f'G{i}{j}'] = usd(v)
for n in ('comps', 'own', 'cons'):
    T[f'{n.upper()}_PCT'] = sg(r['pcts'][n]); T[f'{n.upper()}_CLS'] = cls(r[n])
for p, v in r['peers'].items():
    T[f'M_{p}'] = f"{v['mult']:.1f}x"; T[f'MV_{p}'] = f"{v['mult']:.2f}"
T['M_ANTV'] = f"{r['ant_ev_rev27']:.2f}"; T['PEER_AVGV'] = f"{r['peer_avg']:.2f}"
# datos crudos para JS
T['JS_RANGES'] = json.dumps([[d['bear']['fv'], d['bull']['fv']], [r['comps_lo'], r['comps_hi']], [r['own_lo'], r['own_hi']], [92.0, 155.0]])
T['JS_PRICE'] = f"{P:.2f}"; T['JS_BLEND'] = f"{r['blend']:.2f}"
T['JS_REV_BASE'] = json.dumps([round(x, 1) for x in d['base']['rev'][:5]])
T['JS_REV_BEAR'] = json.dumps([round(x, 1) for x in d['bear']['rev'][:5]])
T['JS_REV_BULL'] = json.dumps([round(x, 1) for x in d['bull']['rev'][:5]])
T['JS_ROUNDS'] = json.dumps([x[3] for x in r['rounds']] + [r['ipo_mult'], r['mkt_mult']])
T['JS_COMPS'] = json.dumps([r['peers']['MSFT']['mult'], r['peers']['NVDA']['mult'], r['peers']['PLTR']['mult'], r['peer_avg'], r['ant_ev_rev27']])
pos = r['blend'] >= P
T['POSTURA'] = ('CONSTRUCTIVA — TRES DE LOS CUATRO MÉTODOS QUEDAN POR ENCIMA DEL PRECIO; ES, A LA VEZ, LA ACCIÓN CON MÁS DISPERSIÓN DE TODA LA COBERTURA'
                if r['blend_pct'] >= 10 else
                'NEUTRAL CON SESGO CONSTRUCTIVO — EL BLEND QUEDA POR ENCIMA DEL PRECIO, PERO CON LA DISPERSIÓN MÁS AMPLIA DE TODA LA COBERTURA') if pos else \
               'NEUTRAL — EL PRECIO YA DESCUENTA EL CASO BASE; EL NEGOCIO ES EXCEPCIONAL, LA VALUACIÓN NO DEJA MARGEN'
src = open(os.path.join(here, 'ant.src.html'), encoding='utf-8').read()
missing = set(re.findall(r'\{\{([A-Z0-9_]+)\}\}', src)) - set(T)
if missing: raise SystemExit(f'Tokens sin valor: {sorted(missing)}')
html = re.sub(r'\{\{([A-Z0-9_]+)\}\}', lambda m: T[m.group(1)], src)
dst = os.path.normpath(os.path.join(here, '..', '..', '..', '..', '..', 'informes', 'ant.html'))
open(dst, 'w', encoding='utf-8').write(html)
print('OK ->', dst, len(html))
