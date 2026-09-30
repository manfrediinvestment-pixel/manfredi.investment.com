# Baja los datos de mercado y XBRL que usa model.py: companyfacts de KO (SEC), precios mensuales de KO (15 años,
# reversión y sparkline), precio de cierre de KO, pares y ^TNX (Yahoo). Imprime los valores para copiarlos a model.py.
import json, urllib.request, os, sys
os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
SEC = {'User-Agent': 'Manfredi Research nachito2502@gmail.com'}
def get(u, h=UA): return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=90).read()
open('raw/companyfacts.json', 'wb').write(get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000021344.json', SEC))
open('yh/KO.mo.json', 'wb').write(get('https://query1.finance.yahoo.com/v8/finance/chart/KO?interval=1mo&range=15y'))
TICKERS = ['KO', 'PEP', 'KDP', 'MNST', 'PG', 'CL', 'PM', '^TNX', '^GSPC', 'KOF', 'CCEP', 'CCH.L', 'CCOLA.IS', '2579.T', 'AKO-B']
for t in TICKERS:
    try:
        d = json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=10d'))['chart']['result'][0]
        q = d['indicators']['quote'][0]['close']; ts = d['timestamp']
        import datetime
        rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c) for a, c in zip(ts, q) if c]
        print(t, d['meta'].get('currency'), rows[-4:])
    except Exception as e:
        print(t, 'ERROR', e, file=sys.stderr)
# Participaciones cotizantes (10-K 2025, nota de inversiones) y tipos de cambio: cierres diarios para leer el 31-dic-2025
# y el cierre de corte. Se guardan en yh/ para que model.py los lea.
for t in ['MNST', 'CCEP', 'KOF', 'CCH.L', 'CCOLA.IS', '2579.T', 'AKO-B', 'GBPUSD=X', 'TRY=X', 'JPY=X']:
    open(f'yh/{t}.d.json', 'wb').write(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=1y'))
