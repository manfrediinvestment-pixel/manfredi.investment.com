# Agrega la entrada de la actualización 3T26 de UNH al principio de informes/manifest.json (json.dumps, sin heredoc de
# bash). Conserva la entrada de septiembre ("unh-2026-09-29") y reemplaza solo una corrida anterior de esta misma edición.
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
MINUS = '−'
M = json.load(open('model.json'))
NUM = 'unh-2026-11-13'
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('num') != NUM]
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": NUM,
    "ticker": "UNH",
    "title": "Informe actualizado: UnitedHealth Group (UNH) — 3T 2026",
    "abstract": (f"Actualización con el tercer trimestre (reportado el 13-oct-2026) y el 10-Q del 3-nov: medical loss ratio de "
                 f"{M['mcrq']['3T26']:.1f}% contra {M['mcrq']['3T25']:.1f}% un año antes (con $610 millones de reservas del mismo año liberadas), "
                 f"EPS ajustado de $4.69 contra $2.92 y guía 2026 subida por tercera vez, a \"al menos $20.50\". Para 2027 la gerencia "
                 f"apunta al piso de su meta de 13%-16% de crecimiento. Lo que empeoró: las estrellas 2027 dejan \"al menos 69%\" de los "
                 f"afiliados de Medicare Advantage en planes de 4+ estrellas, contra ~78% un año antes (pagan en 2028), y Medicare "
                 f"Advantage ya perdió {abs(M['ma_chg']):,.0f} mil afiliados desde diciembre. El blend pasa de {usd(M['blend_sep'])} a {usd(M['blend'])} "
                 f"(todo del modelo: WACC más bajo, base 2026 más alta y Centene dentro de los comparables; sin Centene, "
                 f"{usd(M['blend_comp_core'])}), pero la acción subió {M['price_chg_pct']:.1f}%, a {usd(M['price'])}: la brecha pasa de "
                 f"{pct(M['blend_gap_sep'])} a {pct(M['blend_gap'])}. Postura: neutral (antes, neutral con sesgo constructivo)."),
    "date": "13 de noviembre de 2026",
    "href": "informes/unh.html",
    "publishedAt": "2026-11-13",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['num'] == NUM and any(e.get('num') == 'unh-2026-09-29' for e in chk)
print(chk[0]['abstract']); print(len(chk))
