# Baja los datos de mercado que usa model.py: precios diarios y mensuales de LLY, pares y ^TNX (Yahoo).
# El companyfacts y los documentos de EDGAR los baja raw/dl_q.py (con el User-Agent con mail que exige SEC).
import json, urllib.request, os, sys, datetime
os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
open('yh/LLY.mo.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/LLY?interval=1mo&range=12y'))
T = ['LLY', '^TNX', 'JNJ', 'ABBV', 'AMGN', 'MRK', 'GILD', 'NVS', 'AZN', 'REGN', 'NVO', 'PFE', 'GSK', 'BMY', 'SNY', 'VRTX']
for t in T:
    try:
        b = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=1y')
        open(f'yh/{t}.d.json', 'wb').write(b)
        d = json.loads(b)['chart']['result'][0]
        rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c)
                for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
        print(t, rows[-3:])
    except Exception as e:
        print(t, 'ERROR', e, file=sys.stderr)
