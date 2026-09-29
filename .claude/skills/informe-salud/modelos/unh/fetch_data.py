# Baja los datos de mercado que usa model.py: precios mensuales de UNH (reversión y sparkline) y el consenso de EPS
# de UNH y de las seis aseguradoras (Nasdaq / Zacks). Imprime los valores para copiarlos a model.py.
import json, urllib.request, os
os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(u, h=UA): return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=60).read()
open('yh/UNH.mo.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/UNH?interval=1mo&range=15y'))
for t in ['UNH', 'ELV', 'CI', 'CVS', 'HUM', 'CNC', 'MOH', '^TNX']:
    d = json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=5d'))['chart']['result'][0]
    print(t, 'precio', d['meta']['regularMarketPrice'])
NQ = dict(UA, **{'Accept': 'application/json', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'})
for t in ['UNH', 'ELV', 'CI', 'CVS', 'HUM', 'CNC', 'MOH']:
    rows = json.loads(get(f'https://api.nasdaq.com/api/analyst/{t}/earnings-forecast', NQ))['data']['yearlyForecast']['rows']
    print(t, [(r['fiscalEnd'], r['consensusEPSForecast'], r['noOfEstimates']) for r in rows])
