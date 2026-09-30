# Baja de SEC EDGAR los comunicados (8-K, anexo 99) de Walmart desde mayo de 2023 y los guarda como texto en ex/.
import json, urllib.request, re, os, html, time
UA = {'User-Agent': 'Manfredi Investment research nachito2502@gmail.com'}
def get(u):
    time.sleep(0.2); return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def txt(b):
    s = b.decode('utf-8', 'ignore'); s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
    s = re.sub(r'(?i)</(p|div|tr|h\d|li)>', '\n', s); s = re.sub(r'(?i)<br\s*/?>', '\n', s); s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s); s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s); return s
if __name__ == '__main__':
    d = json.load(open('subs.json')); r = d['filings']['recent']
    os.makedirs('ex', exist_ok=True)
    for i in range(len(r['form'])):
        f, fd, acc, items = r['form'][i], r['filingDate'][i], r['accessionNumber'][i], r['items'][i]
        if fd < '2023-05-01' or f != '8-K': continue
        base = f"https://www.sec.gov/Archives/edgar/data/104169/{acc.replace('-', '')}/"
        idx = json.loads(get(base + 'index.json'))
        for it in idx['directory']['item']:
            n = it['name']
            if n.endswith('.htm') and not n.startswith('R') and 'index' not in n:
                out = f"ex/{fd}_{n}.txt"
                if not os.path.exists(out): open(out, 'w', encoding='utf-8').write(txt(get(base + n)))
                print(out, os.path.getsize(out))
