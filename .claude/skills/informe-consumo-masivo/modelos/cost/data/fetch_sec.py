# Baja de SEC EDGAR (CIK 0000909832) los 8-K (con anexos 99), 10-K, 10-Q y DEF 14A de Costco desde 2022 y los guarda
# como texto en ex/. Requiere subs.json (https://data.sec.gov/submissions/CIK0000909832.json) y facts.json
# (https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json), que se bajan con el mismo User-Agent.
import json, urllib.request, re, os, html, time, sys
UA = {'User-Agent': 'Manfredi Investment research research@manfredinvestment.com'}   # genérico, sin datos personales
def get(u):
    time.sleep(0.15); return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def txt(b):
    s = b.decode('utf-8', 'ignore'); s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
    s = re.sub(r'(?is)<ix:header>.*?</ix:header>', '', s)
    s = re.sub(r'(?i)</(p|div|tr|h\d|li)>', '\n', s); s = re.sub(r'(?i)<br\s*/?>', '\n', s); s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s); s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s); return s
if __name__ == '__main__':
    if not os.path.exists('subs.json'):
        open('subs.json', 'wb').write(get('https://data.sec.gov/submissions/CIK0000909832.json'))
    if not os.path.exists('facts.json'):
        open('facts.json', 'wb').write(get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json'))
    since = sys.argv[1] if len(sys.argv) > 1 else '2022-01-01'
    d = json.load(open('subs.json')); r = d['filings']['recent']
    os.makedirs('ex', exist_ok=True)
    for i in range(len(r['form'])):
        f, fd, acc = r['form'][i], r['filingDate'][i], r['accessionNumber'][i]
        if fd < since or f not in ('8-K', '10-K', '10-Q', 'DEF 14A'): continue
        base = f"https://www.sec.gov/Archives/edgar/data/909832/{acc.replace('-', '')}/"
        idx = json.loads(get(base + 'index.json'))
        for it in idx['directory']['item']:
            n = it['name']
            if n.endswith('.htm') and not n.startswith('R') and 'index' not in n:
                out = f"ex/{fd}_{f.replace(' ', '')}_{n}.txt"
                if not os.path.exists(out): open(out, 'w', encoding='utf-8').write(txt(get(base + n)))
                print(out, os.path.getsize(out))
