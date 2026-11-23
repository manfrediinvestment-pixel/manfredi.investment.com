# Baja los insumos propios del informe de COST que no están en el bloque compartido:
#   1) SEC EDGAR (subs.json, facts.json y filings como texto en data/ex/) y la serie anual data/annual.json;
#   2) comunicados de ventas mensuales (PDF del sitio de inversores de Costco) a data/monthly/ y su texto (.txt, versionado).
# Precios, Treasury, consenso y pares salen de .claude/skills/_compartido/defensivos_nov26.json y de modelos/wmt/model.json.
import subprocess, sys, os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data')
subprocess.run([sys.executable, 'fetch_sec.py', '2016-09-01'], cwd=D, check=True)
subprocess.run([sys.executable, 'annual.py'], cwd=D, check=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36'}
BASE = 'https://s201.q4cdn.com/287523651/files/doc_news/Costco-Wholesale-Corporation-Reports-{}-Sales-Results-2026.pdf'
os.makedirs(os.path.join(D, 'monthly'), exist_ok=True)
for tag, mes in (('sep26', 'September'), ('oct26', 'October')):
    pdf = os.path.join(D, 'monthly', tag + '.pdf')
    open(pdf, 'wb').write(urllib.request.urlopen(urllib.request.Request(BASE.format(mes), headers=UA), timeout=60).read())
    import pymupdf
    open(os.path.join(D, 'monthly', tag + '.txt'), 'w', encoding='utf-8').write(''.join(p.get_text() for p in pymupdf.open(pdf)))
    print(tag, 'ok')
