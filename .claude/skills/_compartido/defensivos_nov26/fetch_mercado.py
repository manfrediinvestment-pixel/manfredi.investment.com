# Fase 1 (research común defensivos, 22-nov-2026): precios de Yahoo y consenso de Nasdaq. Guarda crudos en yh/ y nq/.
import json, urllib.request, os, datetime, time
os.makedirs('yh', exist_ok=True); os.makedirs('nq', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(u, h=UA): return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=60).read()
MAIN = ['COST', 'PFE', 'ABBV']
PHARMA = ['LLY', 'JNJ', 'MRK', 'BMY', 'AMGN', 'GILD', 'NVO', 'AZN', 'NVS', 'GSK', 'SNY', 'REGN', 'VRTX']
RETAIL = ['WMT', 'BJ', 'TGT', 'DG', 'DLTR', 'KR', 'AMZN']
IDX = ['^TNX', '^GSPC', 'XLP', 'XLV', 'SPY']
for t in MAIN:
    open(f'yh/{t}.mo.json', 'wb').write(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1mo&range=15y'))
for t in MAIN + PHARMA + RETAIL + IDX:
    open(f'yh/{t}.d.json', 'wb').write(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&range=2y'))
    time.sleep(0.3)
NQ = dict(UA, **{'Accept': 'application/json', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'})
for t in MAIN + PHARMA + RETAIL:
    for kind in ['earnings-forecast', 'targetprice', 'ratings']:
        try: open(f'nq/{t}.{kind}.json', 'wb').write(get(f'https://api.nasdaq.com/api/analyst/{t}/{kind}', NQ))
        except Exception as e: print(t, kind, 'error', e)
        time.sleep(0.3)
print('ok')
