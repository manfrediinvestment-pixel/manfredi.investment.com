# Baja los datos que no están en el research común (.claude/skills/_compartido/defensivos_nov26.json):
#  - Yahoo: serie mensual de 25 años de PFE (para la reversión histórica y el gráfico de precio) -> yh/PFE.mo25.json
#  - EDGAR: companyfacts + submissions (raw/sec.py), comunicados (raw/fetch_rel.py), Orange Book (raw/orange_book.py)
# User-Agent genérico, sin datos personales.
import urllib.request, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs('yh', exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
u = 'https://query1.finance.yahoo.com/v8/finance/chart/PFE?interval=1mo&range=25y&events=div%7Csplit%7CcapitalGain'
open('yh/PFE.mo25.json', 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
print('yh/PFE.mo25.json')
