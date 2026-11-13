# Baja precios de Yahoo que usa model.py: mensuales de PG (15 años: reversión y sparkline) y diarios (1 año) de PG,
# pares, ^TNX y ^GSPC. Imprime los últimos cierres. El consenso (Nasdaq) y las estadísticas de stockanalysis van aparte
# (data/nasdaq_eps.json, data/sa_stats.json): Nasdaq devuelve 403 a scripts y se lee desde el navegador.
import json, urllib.request, os, sys, datetime
os.chdir(os.path.dirname(os.path.abspath(__file__))); os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
open('yh/PG.mo.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/PG?interval=1mo&range=15y'))
for t in ['PG', 'KO', 'PEP', 'CL', 'KMB', 'CHD', 'CLX', 'UL', 'KVUE', '^TNX', '^GSPC']:
    try:
        raw = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=1y')
        open(f'yh/{t}.d.json', 'wb').write(raw)
        d = json.loads(raw)['chart']['result'][0]
        rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), round(c, 3))
                for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
        print(t, d['meta'].get('currency'), rows[-5:])
    except Exception as e:
        print(t, 'ERROR', e, file=sys.stderr)
