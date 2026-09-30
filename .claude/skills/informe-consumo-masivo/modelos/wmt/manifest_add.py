# Agrega la entrada de WMT al principio de informes/manifest.json (json.dumps, sin heredoc de bash).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
MINUS = '−'
M = json.load(open(HERE/'model.json'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('ticker') != 'WMT']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "wmt-2026-09-30",
    "ticker": "WMT",
    "title": "Nuevo informe: Walmart (WMT) — primero de retail: tráfico vs. ticket, e-commerce, publicidad y membresías",
    "abstract": (f"Las ventas comparables de Walmart crecen por más clientes y no solo por precio, el e-commerce ya es "
                 f"{M['ecom_pct_26']:.1f}% de las ventas y es rentable, y publicidad y membresías explicaron casi un tercio de la utilidad del 4T FY2026. "
                 f"Pero a {M['pe_ntm_now']:.1f}x el EPS de los próximos cuatro trimestres el precio ya lo paga: el blend de cinco métodos da "
                 f"{usd(M['blend'])}, {pct(M['blend_gap'])} contra {usd(M['price'])}. El DCF, la suma de partes con Walmex, Flipkart y PhonePe y los "
                 f"comparables contra minoristas promedian {usd(M['indep'])}; su múltiplo reciente y el consenso, {usd(M['anch'])}."),
    "date": "30 de septiembre de 2026",
    "href": "informes/wmt.html",
    "publishedAt": "2026-09-30",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['ticker'] == 'WMT'
print(chk[0]['abstract']); print(len(chk))
