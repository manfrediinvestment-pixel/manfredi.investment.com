# Baja los comunicados de resultados (8-K ítem 2.02, Exhibit 99) de Pfizer de las fechas pedidas y los guarda en rel/.
# Uso: python fetch_rel.py 2012-01-31 2013-01-29 ...   (fecha de presentación del 8-K)
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sec import get, txt, CIK
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subs = json.load(open('subs.json'))
rows = []
def add(r):
    for i in range(len(r['form'])):
        if r['form'][i] == '8-K' and '2.02' in r['items'][i]: rows.append((r['filingDate'][i], r['accessionNumber'][i]))
add(subs['filings']['recent'])
for f in subs['filings'].get('files', []): add(json.loads(get('https://data.sec.gov/submissions/' + f['name'])))
want = set(sys.argv[1:])
for fd, acc in sorted(set(rows)):
    if want and fd not in want and fd[:4] not in want: continue
    path = f'rel/rel_{fd}.txt'
    if os.path.exists(path): continue
    idx = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}/index.json"))
    ex = [it['name'] for it in idx['directory']['item'] if re.search(r'ex.?99', it['name'], re.I) and it['name'].endswith('.htm')]
    if not ex: print(fd, 'sin anexo 99'); continue
    open(path, 'w', encoding='utf-8').write(txt(get(f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}/{ex[0]}")))
    print(fd, acc, ex[0])
