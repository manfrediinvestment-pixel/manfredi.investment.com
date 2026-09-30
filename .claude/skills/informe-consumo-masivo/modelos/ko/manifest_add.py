# Agrega la entrada de KO al principio de informes/manifest.json (json.dumps, sin heredoc de bash).
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
MINUS = '−'
M = json.load(open('model.json'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('ticker') != 'KO']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "ko-2026-09-30",
    "ticker": "KO",
    "title": "Nuevo informe: The Coca-Cola Company (KO) — primero de bebidas: volumen, precio/mix, embotelladoras y el juicio con el IRS",
    "abstract": (f"El volumen de Coca-Cola volvió (+3% y +5% en el primer semestre de 2026) y el precio/mix, inflado por Argentina en 2024, "
                 f"se normalizó en +2%. El blend de cuatro métodos da {usd(M['blend'])}, {pct(M['blend_gap'])} contra {usd(M['price'])}: "
                 f"el flujo de caja descontado (con {M['stk_now']:.1f} mil millones en participaciones a valor de mercado) y los comparables "
                 f"promedian {usd(M['indep'])}, y aun su propio múltiplo histórico y el consenso, {usd(M['anch'])}, quedan por debajo del precio."),
    "date": "30 de septiembre de 2026",
    "href": "informes/ko.html",
    "publishedAt": "2026-09-30",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['ticker'] == 'KO'
print(chk[0]['abstract']); print(len(chk))
