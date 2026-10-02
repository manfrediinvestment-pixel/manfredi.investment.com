# Lee las páginas de estadísticas de stockanalysis.com (bajadas el 2-oct-2026) y guarda los campos que usa model.py.
import re, html, json
def num(x):
    if x is None: return None
    x = x.replace(',', ''); mult = 1
    if x[-1] in 'BMK': mult = {'B': 1e9, 'M': 1e6, 'K': 1e3}[x[-1]]; x = x[:-1]
    if x.endswith('%'): x = x[:-1]
    return float(x)*mult
out = {}
for t in ['pep', 'ko', 'kdp', 'mnst', 'mdlz', 'pg', 'cl', 'pm', 'hsy', 'gis', 'celh']:
    s = open(f'sa/{t}.stats.html', encoding='utf-8').read()
    txt = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)))
    def g(lbl, nth=0):
        ms = re.findall(re.escape(lbl) + r' (-?[\d.,]+[BMK%]?)', txt)
        return ms[nth] if len(ms) > nth else None
    d = dict(evx=num(g('EV / EBITDA')), ev=num(g('Enterprise Value')), mcap=num(g('Market Cap')), sh=num(g('Shares Outstanding')),
             ebitda=num(g('EBITDA', 2)), capex=num(g('Capital Expenditures')), ocf=num(g('Operating Cash Flow')),
             fcf=num(g('Free Cash Flow')), rev=num(g('Revenue')), beta=num(g('Beta (5Y)')), dy=num(g('Dividend Yield')),
             fcfy=num(g('FCF Yield')), roic=num(g('Return on Invested Capital (ROIC)')))
    d['px_sa'] = d['mcap']/d['sh'] if d['mcap'] and d['sh'] else None
    out[t.upper()] = d
    print(t, {k: (round(v/1e9, 3) if v and abs(v) > 1e6 else v) for k, v in d.items()})
json.dump(out, open('../data/sa_stats.json', 'w'), indent=1)
