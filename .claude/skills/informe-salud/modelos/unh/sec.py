# Descargas de SEC EDGAR. El User-Agent (SEC exige un mail) se toma del script de KO, el mismo que usa el resto del repo.
import re, urllib.request, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
_src = (ROOT/'.claude/skills/informe-consumo-masivo/modelos/ko/fetch_data.py').read_text(encoding='utf-8')
UA = {'User-Agent': re.search(r"SEC = \{'User-Agent': '([^']+)'\}", _src).group(1)}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
if __name__ == '__main__':
    url, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'wb').write(get(url)); print(out, os.path.getsize(out))
