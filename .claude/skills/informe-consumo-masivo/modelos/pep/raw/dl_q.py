# Baja los documentos de EDGAR de una lista de accesiones (mismo User-Agent que dl.py).
import re, json, sys, time, urllib.request
UA = {'User-Agent': re.search(r"UA = \{'User-Agent': '([^']+)'\}", open('dl.py', encoding='utf-8').read()).group(1)}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
for acc in sys.argv[1:]:
    base = f"https://www.sec.gov/Archives/edgar/data/77476/{acc.replace('-', '')}/"
    for it in json.loads(get(base + 'index.json'))['directory']['item']:
        n = it['name']
        if n.endswith('.htm') and not n.endswith('-index.htm') and 'index-headers' not in n:
            open(f'{acc}_{n}', 'wb').write(get(base + n)); print(acc, n); time.sleep(0.3)
