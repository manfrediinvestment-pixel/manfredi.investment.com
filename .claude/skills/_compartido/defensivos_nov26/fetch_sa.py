# Consenso y múltiplos de stockanalysis.com (consenso de S&P Global), bajado el 22-nov-2026 (refleja el cierre del 20-nov).
import urllib.request, re, json, os, time, html as H
os.makedirs('sa', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
T = ['COST','PFE','ABBV','LLY','JNJ','MRK','BMY','AMGN','GILD','NVO','AZN','NVS','GSK','SNY','REGN','VRTX','WMT','BJ','TGT','DG','DLTR','KR','AMZN']
for t in T:
    for pg in ['forecast', 'statistics']:
        f = f'sa/{t}.{pg}.html'
        if not os.path.exists(f):
            open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(f'https://stockanalysis.com/stocks/{t.lower()}/{pg}/', headers=UA), timeout=60).read()); time.sleep(0.5)
def cell(h, label):
    m = re.search(r'<span><!---->' + re.escape(label) + r'<!---->.*?title="([^"]*)"', h, re.S)
    return m.group(1) if m else None
out = {}
for t in T:
    fc = open(f'sa/{t}.forecast.html', encoding='utf-8').read(); st = open(f'sa/{t}.statistics.html', encoding='utf-8').read()
    m = re.search(r'According to (\d+) analysts polled by S&amp;P Global, .*? consensus rating of &quot;([^&]+)&quot;.*?average price target of \$([\d.,]+).*?lowest is \$([\d.,]+).*?highest is \$([\d.,]+)', fc, re.S)
    m2 = re.search(r'According to (\d+) analysts.*?consensus rating of "([^"]+)".*?average price target of \$([\d.,]+).*?lowest is \$([\d.,]+).*?highest is \$([\d.,]+)', fc, re.S)
    mm = m or m2
    d = dict(n_analistas=int(mm.group(1)), recomendacion=mm.group(2), pt_prom=float(mm.group(3).replace(',', '').rstrip('.')), pt_min=float(mm.group(4).replace(',', '').rstrip('.')), pt_max=float(mm.group(5).replace(',', '').rstrip('.'))) if mm else {}
    for lab, k in [('Forward PE', 'pe_fwd'), ('PE Ratio', 'pe_ttm'), ('PEG Ratio', 'peg'), ('EV / EBITDA', 'ev_ebitda'), ('Beta (5Y)', 'beta5y'),
                   ('Dividend Yield', 'div_yield'), ('Market Cap', 'mcap'), ('Enterprise Value', 'ev'), ('EV / Sales', 'ev_sales'), ('Return on Invested Capital (ROIC)', 'roic'),
                   ('Payout Ratio', 'payout'), ('Debt / EBITDA', 'deuda_ebitda'), ('Revenue Growth Forecast (5Y)', 'g_rev_5y'), ('EPS Growth Forecast (5Y)', 'g_eps_5y')]:
        d[k] = cell(st, lab)
    # tabla anual de estimaciones (EPS y revenue) del forecast
    for kind in ['EPS', 'Revenue']:
        m = re.search(r'\{id:"' + ('eps' if kind == 'EPS' else 'revenue') + r'".*?\}', fc)
    out[t] = d
    print(t, d)
json.dump(out, open('sa_parsed.json', 'w'), indent=1)
