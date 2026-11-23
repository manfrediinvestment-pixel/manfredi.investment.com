# Utilidades para bajar de SEC EDGAR los documentos de Pfizer (CIK 78003) y pasarlos a texto plano.
# User-Agent genérico (sin datos personales).
# Uso: python sec.py                -> companyfacts.json + subs.json y lista 10-K/10-Q/8-K desde 2025
#      python sec.py idx <acc>      -> índice de una presentación
#      python sec.py <acc> <doc>    -> baja el documento y lo guarda como texto en <acc>_<doc>.txt
import json, urllib.request, re, html, time, os, sys
UA = {'User-Agent': 'Mozilla/5.0 equity-research-script admin@example.org'}
CIK = 78003
def get(u):
    time.sleep(0.15); return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
def txt(b):
    s = b.decode('utf-8', 'ignore')
    s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
    s = re.sub(r'(?is)<ix:header>.*?</ix:header>', '', s)
    s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'(?i)</(p|div|tr|li|h\d)>|<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s); s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s); s = re.sub(r'( \| ){2,}', ' | ', s); s = re.sub(r'\n\s*\n+', '\n', s)
    return s
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == 'idx':
        idx = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/{CIK}/{a[1].replace('-', '')}/index.json"))
        for it in idx['directory']['item']: print(it['name'], it.get('size'))
    elif len(a) == 2:
        out = f"{a[0]}_{a[1]}.txt"
        open(out, 'w', encoding='utf-8').write(txt(get(f"https://www.sec.gov/Archives/edgar/data/{CIK}/{a[0].replace('-', '')}/{a[1]}")))
        print(out, os.path.getsize(out))
    else:
        open('companyfacts.json', 'wb').write(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK:010d}.json'))
        open('subs.json', 'wb').write(get(f'https://data.sec.gov/submissions/CIK{CIK:010d}.json'))
        r = json.load(open('subs.json'))['filings']['recent']
        for i in range(len(r['form'])):
            if r['filingDate'][i] >= '2025-01-01' and r['form'][i] in ('10-K', '10-Q', '8-K'):
                print(r['form'][i], r['filingDate'][i], r['accessionNumber'][i], r['primaryDocument'][i], r['items'][i])
