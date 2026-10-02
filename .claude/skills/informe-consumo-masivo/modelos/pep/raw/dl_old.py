# Baja los comunicados de resultados (8-K ítem 2.02, exhibit 99.1) de 2015 a 2023 para el EPS comparable trimestral.
import urllib.request, json, time, os
UA = {'User-Agent': 'Manfredi Research nachito2502@gmail.com'}
def get(u):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
        except Exception as e: print('retry', u, e); time.sleep(2)
    raise RuntimeError(u)
if not os.path.exists('sub1.json'):
    open('sub1.json', 'wb').write(get('https://data.sec.gov/submissions/CIK0000077476-submissions-001.json'))
rows = []
for src in ('sub.json', 'sub1.json'):
    d = json.load(open(src)); r = d['filings']['recent'] if 'filings' in d else d
    for i in range(len(r['form'])):
        if r['form'][i] == '8-K' and '2.02' in r['items'][i] and '2015-01-01' <= r['filingDate'][i] < '2023-07-01':
            rows.append((r['filingDate'][i], r['accessionNumber'][i]))
for dt, acc in sorted(set(rows)):
    base = f"https://www.sec.gov/Archives/edgar/data/77476/{acc.replace('-', '')}/"
    idx = json.loads(get(base + 'index.json'))
    names = [it['name'] for it in idx['directory']['item'] if it['name'].endswith('.htm')]
    ex = [n for n in names if 'ex-9' in n.lower() or 'ex99' in n.lower() or 'exhibit99' in n.lower() or 'earningsrelease' in n.lower()]
    if not ex: print('SIN EXHIBIT', dt, names); continue
    out = f"old_{dt}_{ex[0]}"
    if not os.path.exists(out): open(out, 'wb').write(get(base + ex[0])); time.sleep(0.3)
    print(out)
