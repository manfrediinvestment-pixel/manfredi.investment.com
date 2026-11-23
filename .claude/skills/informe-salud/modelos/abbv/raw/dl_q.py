# Baja los documentos .htm (principal + exhibits) de EDGAR de una lista de accesiones de AbbVie (CIK 1551152).
# Uso: python dl_q.py 0001551152-26-000033 0001551152-26-000037 ...   (User-Agent genérico de ua.py)
import json, sys, time, urllib.request, os
from ua import UA
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
for acc in sys.argv[1:]:
    base = f"https://www.sec.gov/Archives/edgar/data/1551152/{acc.replace('-', '')}/"
    for it in json.loads(get(base + 'index.json'))['directory']['item']:
        n = it['name']
        if n.endswith('.htm') and not n.endswith('-index.htm') and 'index-headers' not in n and not n.startswith('R'):
            out = f'{acc}_{n}'
            if os.path.exists(out): continue
            open(out, 'wb').write(get(base + n)); print(acc, n); time.sleep(0.3)
