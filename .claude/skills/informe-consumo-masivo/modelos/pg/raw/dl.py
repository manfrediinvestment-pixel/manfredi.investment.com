# Baja de EDGAR los comunicados de resultados (8-K ítem 2.02, ex-99) de P&G desde 2016 y los 10-K/10-Q desde 2024.
# User-Agent: el mismo que los scripts de KO/PEP (SEC exige un contacto); se lee de modelos/pep/raw/dl.py.
import urllib.request, json, time, os, re
from pathlib import Path
UA = {'User-Agent': re.search(r"UA = \{'User-Agent': '([^']+)'\}", (Path(__file__).resolve().parents[2] / 'pep/raw/dl.py').read_text(encoding='utf-8')).group(1)}
CIK = 80424
def get(u):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
        except Exception as e: print('retry', u, e); time.sleep(2)
    raise RuntimeError(u)
open('sub.json', 'wb').write(get(f'https://data.sec.gov/submissions/CIK{CIK:010d}.json'))
sub = json.load(open('sub.json'))
blocks = [sub['filings']['recent']] + [json.loads(get('https://data.sec.gov/submissions/' + f['name'])) for f in sub['filings'].get('files', [])]
want = []
for d in blocks:
    for i in range(len(d['form'])):
        f, dt, acc, it = d['form'][i], d['filingDate'][i], d['accessionNumber'][i], d['items'][i]
        if dt < '2016-07-01': continue
        if (f == '8-K' and '2.02' in it) or (f in ('10-K', '10-Q') and dt >= '2024-01-01') or (f == '8-K' and dt >= '2026-07-01'):
            want.append((f, dt, acc, d['primaryDocument'][i]))
for f, dt, acc, pd in sorted(want):
    base = f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}/"
    idx = json.loads(get(base + 'index.json'))
    for it in idx['directory']['item']:
        n = it['name']
        if n.endswith('.htm') and (n == pd or 'ex99' in n.lower().replace('-', '').replace('_', '') or 'exhibit99' in n.lower()):
            out = f"{dt}_{f}_{n}"
            if not os.path.exists(out):
                open(out, 'wb').write(get(base + n)); time.sleep(0.25)
            print(out)
open('companyfacts.json', 'wb').write(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK:010d}.json'))
