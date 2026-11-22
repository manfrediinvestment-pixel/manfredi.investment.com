# Arma el bloque de mercado del JSON común: cierres del 20-nov-2026 (Yahoo) + consenso y múltiplos (stockanalysis / S&P Global).
import json, re, datetime
CUT = '2026-11-20'
def closes(t):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    return {datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(): c for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c}, d['meta']
def num(s):
    if s in (None, 'n/a'): return None
    return float(s.replace(',', '').replace('%', ''))
SA = json.load(open('sa_parsed.json'))
out = {}
# Cierre del año fiscal "actual" (epsThis) y "siguiente" (epsNext) de stockanalysis, verificado contra la tabla anual de cada página.
FYC = {'COST': ('ago-2027 (FY2027)', 'ago-2028 (FY2028)'), 'WMT': ('ene-2027 (FY2027)', 'ene-2028 (FY2028)'),
       'TGT': ('ene-2027', 'ene-2028'), 'DG': ('ene-2027', 'ene-2028'), 'DLTR': ('ene-2027', 'ene-2028'), 'KR': ('ene-2027', 'ene-2028'), 'BJ': ('ene-2027', 'ene-2028')}
for t in SA:
    c, meta = closes(t)
    h = open(f'sa/{t}.forecast.html', encoding='utf-8').read()
    m = re.search(r'annual:\{epsNext:\{last:([-\d.e]+),this:([-\d.e]+).*?epsThis:\{last:([-\d.e]+),this:([-\d.e]+).*?revenueNext:\{last:([-\d.e]+),this:([-\d.e]+).*?revenueThis:\{last:([-\d.e]+),this:([-\d.e]+)', h)
    fy = re.search(r'table:\{annual:.*?fiscalYear:\[([^\]]*)\]', h, re.S)
    adj = re.search(r'table:\{annual:.*?adjustedEps:\[([^\]]*)\]', h, re.S)
    s = SA[t]; px = round(c[CUT], 2)
    rec = dict(cierre_20nov=px, max_52s=meta.get('fiftyTwoWeekHigh'), min_52s=meta.get('fiftyTwoWeekLow'), moneda=meta.get('currency'),
               consenso=dict(pt_prom=s['pt_prom'], pt_min=s['pt_min'], pt_max=s['pt_max'], n_analistas=s['n_analistas'], recomendacion=s['recomendacion'],
                             pt_vs_cierre_pct=round((s['pt_prom'] / px - 1) * 100, 2)),
               multiplos=dict(pe_fwd=num(s['pe_fwd']), pe_ttm=num(s['pe_ttm']), peg=num(s['peg']), ev_ebitda=num(s['ev_ebitda']), ev_ventas=num(s['ev_sales']),
                              beta_5y=num(s['beta5y']), div_yield_pct=num(s['div_yield']), ev_usd=num(s['ev']), roic_pct=num(s['roic']), payout_pct=num(s['payout']),
                              deuda_ebitda=num(s['deuda_ebitda'])))
    if m:
        v = [float(x) for x in m.groups()]
        rec['consenso'].update(eps_ajustado_fy_actual=round(v[3], 4), eps_ajustado_fy_anterior_real=round(v[2], 4), eps_ajustado_fy_siguiente=round(v[1], 4),
                               ventas_fy_actual=v[7], ventas_fy_siguiente=v[5])
        rec['consenso']['eps_fy_anterior_real'] = rec['consenso'].pop('eps_ajustado_fy_anterior_real')
        rec['consenso']['fy_actual_cierra'], rec['consenso']['fy_siguiente_cierra'] = FYC.get(t, ('dic-2026', 'dic-2027'))
    out[t] = rec
idx = {}
for t in ['^TNX', '^GSPC', 'XLP', 'XLV', 'SPY']:
    c, _ = closes(t); idx[t] = round(c[CUT], 3)
json.dump(dict(fecha_cierre=CUT, tickers=out, indices=idx), open('mercado.json', 'w'), indent=1, ensure_ascii=False)
for t, r in out.items(): print(t, r['cierre_20nov'], r['consenso'].get('fy_actual'), r['consenso'].get('eps_ajustado_fy_actual'), r['consenso'].get('eps_ajustado_fy_siguiente'), r['multiplos']['pe_fwd'])
print(idx)
