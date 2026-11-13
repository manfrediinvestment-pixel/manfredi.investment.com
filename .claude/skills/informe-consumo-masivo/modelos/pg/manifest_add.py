# Agrega la entrada de la edición 1T FY2027 de PG al principio de informes/manifest.json (deja la de septiembre abajo).
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()
M = json.load(open('model.json', encoding='utf-8'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('num') != 'pg-2026-11-13']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return ('−' if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "pg-2026-11-13",
    "ticker": "PG",
    "title": "Informe actualizado: Procter & Gamble (PG) — 1T FY2027",
    "abstract": (f"Actualización con el primer trimestre del año fiscal 2027 (reportado 22-oct-2026) y el 10-Q del mismo día: "
                 f"orgánico de +4.0% con 2.4 puntos de volumen, 1.1 de mezcla y apenas 0.4 de precio, crecimiento en los diez rubros "
                 f"y las seis regiones, y EPS core de $2.00 (+1%). La guía no cambió, pero el viento en contra de materias primas, "
                 f"intereses y monedas subió de $0.56 a $0.79 por acción, y Thorne cerró el 1 de octubre por $3,900 millones. "
                 f"El blend pasa de {usd(M['sep']['blend'])} a {usd(M['blend'])}, pero la acción subió {M['chg_price']:.1f}%: queda "
                 f"{pct(M['blend_gap'])} contra {usd(M['price'])}, y a diferencia de septiembre también su múltiplo histórico queda debajo "
                 f"del precio. Postura: neutral con sesgo bajista."),
    "date": "13 de noviembre de 2026",
    "href": "informes/pg.html",
    "publishedAt": "2026-11-13",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
assert json.load(open(p, encoding='utf-8'))[0]['num'] == 'pg-2026-11-13'
print(entry['abstract'])
