# Agrega la entrada de COST al principio de informes/manifest.json (json.dumps, sin heredoc de bash).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
MINUS = '−'
M = json.load(open(HERE/'model.json'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('ticker') != 'COST']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "cost-2026-11-23",
    "ticker": "COST",
    "title": "Nuevo informe: Costco (COST) — el modelo de membresía con números: cuotas contra mercadería, renovación y tráfico vs. ticket",
    "abstract": (f"Las cuotas de membresía explicaron {M['fee_share_26']:.1f}% del resultado operativo del FY2026 (eran {M['fee_share_16']:.0f}% diez años antes), "
                 f"la renovación de EE.UU. y Canadá es de {M['memq']['ren_us'][-1]:.1f}% y las comparables sin nafta crecen por más visitas. "
                 f"Pero a {M['pe_ntm_now']:.1f}x las ganancias de los próximos doce meses el precio ya lo paga: el blend de cinco métodos da "
                 f"{usd(M['blend'])}, {pct(M['blend_gap'])} contra {usd(M['price'])} (con el dividendo especial de $30 incluido). Un DCF que valúa por "
                 f"separado las cuotas y la mercadería, el DCF consolidado y los comparables promedian {usd(M['indep'])}; su múltiplo y el consenso, {usd(M['anch'])}."),
    "date": "23 de noviembre de 2026",
    "href": "informes/cost.html",
    "publishedAt": "2026-11-23",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['ticker'] == 'COST'
print(chk[0]['abstract']); print(len(chk))
