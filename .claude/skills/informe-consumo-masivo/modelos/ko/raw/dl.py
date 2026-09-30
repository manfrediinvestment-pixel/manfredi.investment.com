import urllib.request, json, time, os
UA = {'User-Agent': 'Manfredi Research nachito2502@gmail.com'}
def get(u):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
        except Exception as e: print('retry', u, e); time.sleep(2)
    raise RuntimeError(u)
d = json.load(open('sub.json'))['filings']['recent']
want = []
for i in range(len(d['form'])):
    f, dt, acc = d['form'][i], d['filingDate'][i], d['accessionNumber'][i]
    if dt < '2023-10-01': continue
    it = d['items'][i]
    if (f == '8-K' and ('2.02' in it or '8.01' in it or '7.01' in it)) or f in ('10-K', '10-Q'):
        want.append((f, dt, acc, d['primaryDocument'][i]))
for f, dt, acc, pd in want:
    base = f"https://www.sec.gov/Archives/edgar/data/21344/{acc.replace('-', '')}/"
    idx = json.loads(get(base + 'index.json'))
    for it in idx['directory']['item']:
        n = it['name']
        if n.endswith('.htm') and (n == pd or 'ex-9' in n.lower() or 'ex99' in n.lower() or 'exhibit99' in n.lower()):
            out = f"{dt}_{f}_{n}"
            if not os.path.exists(out):
                open(out, 'wb').write(get(base + n)); time.sleep(0.3)
            print(out)
