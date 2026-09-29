# Agrega la entrada de UNH al principio de informes/manifest.json (json.dumps, sin heredoc de bash).
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
MINUS = '\u2212'
M = json.load(open('model.json'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('ticker') != 'UNH']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "unh-2026-09-29",
    "ticker": "UNH",
    "title": "Nuevo informe: UnitedHealth Group (UNH) — primero de managed care: MLR, reservas y Medicare Advantage",
    "abstract": (f"El medical loss ratio de UnitedHealth saltó a {M['mcr_adj25']:.1f}% en 2025 y en 2026 se está re-preciando. "
                 f"El blend de cuatro métodos da {usd(M['blend'])}, {pct(M['blend_gap'])} contra {usd(M['price'])}, pero todo el valor por encima "
                 f"del precio depende de que el MLR vuelva a su mitad de ciclo ({M['mlr_mid']:.2f}%): con el MLR de la guía 2026, "
                 f"la suma de partes UnitedHealthcare + Optum da {usd(M['dcf_mlr_at_g26'])}."),
    "date": "29 de septiembre de 2026",
    "href": "informes/unh.html",
    "publishedAt": "2026-09-29",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['ticker'] == 'UNH'
print(chk[0]['abstract']); print(len(chk))
