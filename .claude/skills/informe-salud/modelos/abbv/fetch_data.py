# Datos de ABBV. Precios, consenso, pares, WACC común, tasas BIO e IRA NO se bajan acá: salen del research común
# (.claude/skills/_compartido/defensivos_nov26.json y su carpeta yh/), que model.py lee directo.
# Este script baja de EDGAR (User-Agent genérico de raw/ua.py, sin datos personales) los documentos que usa el modelo
# y los pasa a texto (raw/*.txt). Los .htm y companyfacts.json quedan fuera del repo (.gitignore).
import subprocess, sys, urllib.request
from pathlib import Path
RAW = Path(__file__).resolve().parent / 'raw'
ACC = ['0001551152-26-000033', '0001551152-26-000037', '0001551152-26-000030',   # 8-K 3T26, 10-Q 3T26, 8-K 5-oct-2026
       '0001104659-26-121322', '0001104659-26-116227', '0001104659-26-104940', '0001104659-26-076067',   # directorio, Apogee
       '0001551152-26-000023', '0001551152-26-000026', '0001551152-26-000013', '0001551152-26-000017',   # 2T26 y 1T26
       '0001551152-26-000004', '0001551152-26-000008', '0001551152-26-000002',                           # 4T25, 10-K 2025
       '0001551152-25-000047', '0001551152-25-000036', '0001551152-25-000026', '0001551152-25-000011',   # 2025 y 4T24
       '0001551152-24-000036', '0001551152-24-000026', '0001551152-24-000016', '0001551152-24-000007',   # 2024 y 4T23
       '0001551152-23-000006', '0001551152-22-000003', '0001551152-21-000003']                           # FY2022, 2021, 2020
subprocess.run([sys.executable, 'dl_q.py'] + ACC, cwd=RAW, check=True)
sys.path.insert(0, str(RAW)); from ua import UA
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
# 10-K con la historia de Humira (2017-2025): solo el documento principal
for acc, doc in [('0001551152-23-000011', 'abbv-20221231.htm'), ('0001551152-20-000007', 'abbv-20191231x10k.htm'), ('0001551152-25-000020', 'abbv-20241231.htm')]:
    (RAW / f'{acc}_{doc}').write_bytes(get(f"https://www.sec.gov/Archives/edgar/data/1551152/{acc.replace('-', '')}/{doc}"))
(RAW / 'companyfacts.json').write_bytes(get('https://data.sec.gov/api/xbrl/companyfacts/CIK0001551152.json'))
subprocess.run([sys.executable, 'totext.py'], cwd=RAW, check=True)
# Orange Book (fechas de patentes y exclusividades): https://www.fda.gov/media/76860/download?attachment
# → patent.txt / exclusivity.txt / products.txt; se consultó el 22-nov-2026 (fechas citadas en la Sección 03).
