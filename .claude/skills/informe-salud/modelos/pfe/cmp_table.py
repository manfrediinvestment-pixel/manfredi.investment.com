# Cuadro corto "PFE vs. ABBV vs. LLY vs. JNJ" (el mismo en el informe de ABBV). Lo arma el modelo, no se tipea:
# PFE y las referencias LLY/JNJ salen de model.json["cmp"] / ["cmp_refs"]; ABBV, de modelos/abbv/model.json["cmp"]
# (en este worktree o, mientras no exista, en el worktree hermano manfredi-abbv). Si ABBV no está, la columna se omite.
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
HERE = Path(__file__).resolve().parent
MINUS = '−'
KEYS = ['ticker', 'precio', 'fair_value', 'gap_pct', 'm1_sotp', 'm2_comp', 'm3_rev', 'm4_cons', 'indep', 'anclados', 'pe_fy27',
        'div_yield_pct', 'payout_fcf_pct', 'nd_ebitda', 'rd_ventas_pct', 'margen_bruto_pct', 'ventas_riesgo_loe_2030_pct',
        'crec_eps_fy27_pct', 'wacc_pct', 'postura']
def abbv_cmp():
    cands = [HERE.parent / 'abbv/model.json',
             HERE.parents[5] / 'manfredi-abbv/.claude/skills/informe-salud/modelos/abbv/model.json']
    for c in cands:
        if c.exists():
            d = json.load(open(c, encoding='utf-8')).get('cmp')
            if d and list(d) == KEYS: return d, c
    return None, None
def usd(v): return '—' if v is None else '$' + f'{v:,.2f}'
def pct(v, s=False):
    if v is None: return 'n.d.'
    t = f'{abs(v):.1f}%'
    return (MINUS + t) if v < 0 and t != '0.0%' else (('+' + t) if s and t != '0.0%' else t)
def x(v): return 'n.d.' if v is None else f'{v:.1f}x'
ROWS = [('Precio (cierre 20-nov-2026)', 'precio', usd), ('Fair value (blend)', 'fair_value', usd), ('Distancia al precio', 'gap_pct', lambda v: pct(v, True)),
        ('M1 · suma de partes + rNPV', 'm1_sotp', usd), ('M2 · comparables', 'm2_comp', usd), ('M3 · reversión histórica', 'm3_rev', usd),
        ('M4 · consenso', 'm4_cons', usd), ('Promedio independientes (M1, M2)', 'indep', usd), ('Promedio anclados (M3, M4)', 'anclados', usd),
        ('P/E sobre EPS 2027E', 'pe_fy27', x), ('Rendimiento del dividendo', 'div_yield_pct', pct), ('Dividendos / FCF', 'payout_fcf_pct', pct),
        ('Deuda neta / EBITDA', 'nd_ebitda', x), ('I+D / ventas (TTM)', 'rd_ventas_pct', pct), ('Margen bruto (3T26)', 'margen_bruto_pct', pct),
        ('Ventas en riesgo de LOE', 'ventas_riesgo_loe_2030_pct', pct), ('Crecimiento EPS 2027E', 'crec_eps_fy27_pct', lambda v: pct(v, True)),
        ('Tasa de descuento del M1', 'wacc_pct', pct), ('Postura', 'postura', lambda v: v)]
def table_html(M):
    ab, src = abbv_cmp()
    cols = [M['cmp']] + ([ab] if ab else []) + [M['cmp_refs']['LLY'], M['cmp_refs']['JNJ']]
    h = ['<div class="table-scroll"><table>', '    <tr><th>Métrica</th>' + ''.join(f'<th class="right-al">{c["ticker"]}</th>' for c in cols) + '</tr>']
    for lab, k, f in ROWS:
        cls = 'total' if k == 'fair_value' else ''
        h.append(f'    <tr{" class=\"total\"" if cls else ""}><td class="label">{lab}</td>' + ''.join(f'<td class="right-al">{f(c[k])}</td>' for c in cols) + '</tr>')
    h.append('  </table></div>')
    return '\n'.join(h), ab is not None
if __name__ == '__main__':
    M = json.load(open(HERE / 'model.json', encoding='utf-8'))
    t, has = table_html(M); print(t); print('ABBV presente:', has)
