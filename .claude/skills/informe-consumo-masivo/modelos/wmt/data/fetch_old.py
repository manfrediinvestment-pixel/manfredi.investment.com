# Comunicados de resultados (8-K ítem 2.02) de feb-2015 a abr-2023, para la serie de EPS ajustado de la reversión.
import json, os
from fetch_sec import get, txt
UA_FILE = 'subs_old.json'
if not os.path.exists(UA_FILE):
    open(UA_FILE, 'wb').write(get('https://data.sec.gov/submissions/CIK0000104169-submissions-001.json'))
r = json.load(open(UA_FILE))
os.makedirs('ex_old', exist_ok=True)
for i in range(len(r['form'])):
    f, fd, acc, items = r['form'][i], r['filingDate'][i], r['accessionNumber'][i], r['items'][i]
    if f != '8-K' or '2.02' not in items or fd < '2015-02-01': continue
    base = f"https://www.sec.gov/Archives/edgar/data/104169/{acc.replace('-', '')}/"
    idx = json.loads(get(base + 'index.json'))
    for it in idx['directory']['item']:
        n = it['name']
        if n.endswith('.htm') and not n.startswith('R') and n != r['primaryDocument'][i] and 'index' not in n:
            out = f"ex_old/{fd}_{n}.txt"
            if not os.path.exists(out): open(out, 'w', encoding='utf-8').write(txt(get(base + n)))
            print(out, os.path.getsize(out))
