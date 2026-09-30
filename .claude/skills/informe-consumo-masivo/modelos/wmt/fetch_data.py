# Baja los datos de mercado que usa model.py: precios mensuales de WMT (reversión y sparkline), precio de los pares,
# de Walmex (WALMEX.MX), peso mexicano, Treasury a 10 años, y consenso de EPS (Nasdaq / Zacks). Imprime para copiar a model.py.
import json, urllib.request, os
os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(u, h=UA): return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=60).read()
open('yh/WMT.mo.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/WMT?interval=1mo&range=15y'))
open('yh/WMT.d.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/WMT?interval=1d&range=1y'))
TICK = ['WMT', 'COST', 'TGT', 'KR', 'BJ', 'DG', 'DLTR', 'AMZN', 'WALMEX.MX', 'MXN=X', 'INR=X', '^TNX', '^GSPC']
for t in TICK:
    d = json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=5d'))['chart']['result'][0]
    ts = d['timestamp']; cl = d['indicators']['quote'][0]['close']
    import datetime
    print(t, 'precio', d['meta']['regularMarketPrice'], [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), round(c, 2)) for a, c in zip(ts, cl) if c],
          '52s', d['meta'].get('fiftyTwoWeekHigh'), d['meta'].get('fiftyTwoWeekLow'))
NQ = dict(UA, **{'Accept': 'application/json', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'})
for t in ['WMT', 'COST', 'TGT', 'KR', 'BJ', 'DG', 'DLTR', 'AMZN']:
    try:
        j = json.loads(get(f'https://api.nasdaq.com/api/analyst/{t}/earnings-forecast', NQ))['data']
        print(t, [(r['fiscalEnd'], r['consensusEPSForecast'], r['noOfEstimates']) for r in j['yearlyForecast']['rows']])
        print('   trim', [(r['fiscalEnd'], r['consensusEPSForecast']) for r in j['quarterlyForecast']['rows']])
    except Exception as e: print(t, 'error', e)
