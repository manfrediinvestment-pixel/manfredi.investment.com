# Baja los datos de mercado y XBRL que usa model.py: companyfacts de PEP (SEC), precios mensuales de PEP y KO (15 años,
# reversión, sparkline y comparación), cierres diarios de PEP, KO, pares, Celsius y ^TNX (Yahoo), y consenso de EPS
# (Nasdaq / Zacks). Imprime los valores para copiarlos a model.py.
import json, urllib.request, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.makedirs('yh', exist_ok=True); os.makedirs('raw', exist_ok=True); os.makedirs('data', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
SEC = {'User-Agent': 'Manfredi Research nachito2502@gmail.com'}
def get(u, h=UA): return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=90).read()
if '--no-sec' not in sys.argv:
    open('raw/companyfacts.json', 'wb').write(get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000077476.json', SEC))
for t in ['PEP', 'KO']:
    open(f'yh/{t}.mo.json', 'wb').write(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1mo&range=15y'))
TICKERS = ['PEP', 'KO', 'KDP', 'MNST', 'MDLZ', 'PG', 'CL', 'PM', 'HSY', 'GIS', 'CELH', '^TNX', '^GSPC']
for t in TICKERS:
    try:
        raw = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=1y')
        open(f'yh/{t}.d.json', 'wb').write(raw)
        d = json.loads(raw)['chart']['result'][0]
        rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), round(c, 3))
                for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
        print(t, d['meta'].get('currency'), rows[-4:])
    except Exception as e:
        print(t, 'ERROR', e, file=sys.stderr)
NQ = dict(UA, **{'Accept': 'application/json', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'})
out = {}
for t in ['PEP', 'KO', 'KDP', 'MNST', 'MDLZ', 'PG', 'CL', 'PM', 'HSY', 'GIS']:
    try:
        j = json.loads(get(f'https://api.nasdaq.com/api/analyst/{t}/earnings-forecast', NQ))['data']
        out[t] = j
        print(t, [(r['fiscalEnd'], r['consensusEPSForecast'], r['noOfEstimates']) for r in j['yearlyForecast']['rows']])
    except Exception as e:
        print(t, 'nasdaq error', e, file=sys.stderr)
json.dump(out, open('data/nasdaq_eps.json', 'w'), indent=1)
